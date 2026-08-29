from pathlib import Path
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from aiogram import Bot
from aiogram.types import LabeledPrice
import logging

from config import config
from security import validate_init_data, AuthError
from traits import MODELS, BACKDROPS, PATTERNS, roll_traits
import db

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Sharp Tongue Mini App")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Папка с статикой
STATIC = Path(__file__).parent / "static"
logger.info(f"📁 Static folder: {STATIC}")
logger.info(f"📁 Static exists: {STATIC.exists()}")

if STATIC.exists():
    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    logger.info("✅ Static mounted successfully")
else:
    logger.error(f"❌ Static folder not found at {STATIC}")

class GiftAction(BaseModel):
    gift_id: int

class ListingCreate(BaseModel):
    gift_id: int
    price_ton_nano: int = Field(ge=1_000_000, le=1_000_000_000_000)

class ListingBuy(BaseModel):
    listing_id: int

def auth(init_data: str):
    try:
        return validate_init_data(init_data)
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))

async def current_user(init_data: str):
    user = auth(init_data)
    await db.ensure_user(user["id"],user.get("username"),user.get("first_name"),config.start_ton_nano)
    return user

@app.on_event("startup")
async def startup():
    logger.info("🚀 FastAPI startup...")
    try:
        await db.init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database error: {e}")

@app.get("/", response_class=HTMLResponse)
async def index():
    """Главная страница"""
    logger.info("📄 Serving index.html")
    try:
        index_path = STATIC / "index.html"
        if not index_path.exists():
            logger.error(f"❌ index.html not found at {index_path}")
            return HTMLResponse(
                content="<h1>❌ index.html not found</h1><p>Expected path: " + str(index_path) + "</p>",
                status_code=404
            )
        return FileResponse(index_path)
    except Exception as e:
        logger.error(f"❌ Error serving index: {e}")
        return HTMLResponse(
            content=f"<h1>❌ Error: {str(e)}</h1>",
            status_code=500
        )

@app.get("/health")
async def health():
    """Проверка состояния"""
    logger.info("✅ Health check")
    return {"status": "ok", "static_path": str(STATIC), "static_exists": STATIC.exists()}

@app.get("/api/state")
async def state(x_telegram_init_data: str = Header(default="")):
    logger.info("📄 GET /api/state")
    try:
        user = await current_user(x_telegram_init_data)
        s = await db.stats(user["id"])
        return {
            "user":{"id":user["id"],"first_name":user.get("first_name") or "Player","username":user.get("username")},
            "stats":s,
            "inventory":await db.inventory(user["id"]),
            "market":await db.market(),
            "config":{"price_stars":config.pepe_price_stars,"price_ton_nano":config.gift_price_ton_nano,"price_ton":config.gift_price_ton_nano/1_000_000_000,"market_fee_percent":config.market_fee_percent}
        }
    except Exception as e:
        logger.error(f"❌ Error in /api/state: {e}")
        raise

@app.get("/api/traits")
async def traits(x_telegram_init_data: str = Header(default="")):
    logger.info("📄 GET /api/traits")
    try:
        await current_user(x_telegram_init_data)
        return {"models":MODELS,"backdrops":BACKDROPS,"patterns":PATTERNS}
    except Exception as e:
        logger.error(f"❌ Error in /api/traits: {e}")
        raise

@app.post("/api/create-invoice")
async def invoice(x_telegram_init_data: str = Header(default="")):
    logger.info("📄 POST /api/create-invoice")
    try:
        user = await current_user(x_telegram_init_data)
        bot = Bot(config.bot_token)
        try:
            link = await bot.create_invoice_link(
                title="Sharp Tongue",
                description="Sharp Tongue с одним бесплатным Upgrade.",
                payload="sharp_tongue_v2",
                currency="XTR",
                prices=[LabeledPrice(label="Sharp Tongue",amount=config.pepe_price_stars)],
                provider_token=""
            )
            logger.info(f"✅ Invoice created for user {user['id']}")
            return {"invoice_link":link}
        finally:
            await bot.session.close()
    except Exception as e:
        logger.error(f"❌ Error in /api/create-invoice: {e}")
        raise

@app.post("/api/buy-gift-ton")
async def buy_gift_ton(x_telegram_init_data: str = Header(default="")):
    logger.info("📄 POST /api/buy-gift-ton")
    try:
        user = await current_user(x_telegram_init_data)
        item,msg = await db.buy_gift_with_ton(user["id"], config.gift_price_ton_nano)
        if not item:
            raise HTTPException(409,msg)
        logger.info(f"✅ User {user['id']} bought gift with TON")
        return {"ok":True,"message":msg,"gift":item}
    except Exception as e:
        logger.error(f"❌ Error in /api/buy-gift-ton: {e}")
        raise

@app.post("/api/upgrade")
async def upgrade(body: GiftAction,x_telegram_init_data: str = Header(default="")):
    logger.info(f"📄 POST /api/upgrade (gift_id={body.gift_id})")
    try:
        user = await current_user(x_telegram_init_data)
        gift = await db.get_gift(body.gift_id)
        if not gift or gift["owner_id"] != user["id"]:
            raise HTTPException(404,"Подарок не найден")
        if gift["upgrade_used"]:
            raise HTTPException(409,"Этот подарок уже улучшен")

        model,backdrop,pattern = roll_traits()
        no = await db.upgrade(body.gift_id,user["id"],model,backdrop,pattern)
        if no is None:
            raise HTTPException(409,"Upgrade сейчас недоступен")
        logger.info(f"✅ User {user['id']} upgraded gift {body.gift_id}")
        return {
            "ok":True,"collectible_no":no,
            "model":model,"backdrop":backdrop,"pattern":pattern
        }
    except Exception as e:
        logger.error(f"❌ Error in /api/upgrade: {e}")
        raise

@app.post("/api/list")
async def list_item(body: ListingCreate,x_telegram_init_data: str = Header(default="")):
    logger.info(f"📄 POST /api/list (gift_id={body.gift_id}, price={body.price_ton_nano})")
    try:
        user = await current_user(x_telegram_init_data)
        if not await db.list_item(body.gift_id,user["id"],body.price_ton_nano):
            raise HTTPException(409,"Не удалось выставить подарок")
        logger.info(f"✅ User {user['id']} listed gift {body.gift_id}")
        return {"ok":True}
    except Exception as e:
        logger.error(f"❌ Error in /api/list: {e}")
        raise

@app.post("/api/cancel")
async def cancel(body: GiftAction,x_telegram_init_data: str = Header(default="")):
    logger.info(f"📄 POST /api/cancel (gift_id={body.gift_id})")
    try:
        user = await current_user(x_telegram_init_data)
        if not await db.cancel_listing(body.gift_id,user["id"]):
            raise HTTPException(404,"Лот не найден")
        logger.info(f"✅ User {user['id']} cancelled listing for gift {body.gift_id}")
        return {"ok":True}
    except Exception as e:
        logger.error(f"❌ Error in /api/cancel: {e}")
        raise

@app.post("/api/buy")
async def buy(body: ListingBuy,x_telegram_init_data: str = Header(default="")):
    logger.info(f"📄 POST /api/buy (listing_id={body.listing_id})")
    try:
        user = await current_user(x_telegram_init_data)
        ok,msg = await db.buy_listing(body.listing_id,user["id"],config.market_fee_percent)
        if not ok:
            raise HTTPException(409,msg)
        logger.info(f"✅ User {user['id']} bought listing {body.listing_id}")
        return {"ok":True,"message":msg}
    except Exception as e:
        logger.error(f"❌ Error in /api/buy: {e}")
        raise
