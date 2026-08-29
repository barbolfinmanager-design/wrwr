import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Config:
    # Telegram
    bot_token: str = os.getenv("BOT_TOKEN", "").strip()
    webapp_url: str = os.getenv("WEBAPP_URL", "").strip().rstrip("/")
    
    # Server
    host: str = os.getenv("HOST", "0.0.0.0").strip()
    port: int = int(os.getenv("PORT", "8000"))
    
    # Game settings
    total_supply: int = int(os.getenv("TOTAL_SUPPLY", "1000"))
    pepe_price_stars: int = int(os.getenv("PEPE_PRICE_STARS", "15"))
    start_coins: int = int(os.getenv("START_COINS", "500"))
    market_fee_percent: int = int(os.getenv("MARKET_FEE_PERCENT", "5"))
    gift_price_ton_nano: int = int(os.getenv("GIFT_PRICE_TON_NANO", "150000000"))
    start_ton_nano: int = int(os.getenv("START_TON_NANO", "10000000000"))
    
    # Dev mode
    dev_mode: bool = os.getenv("DEV_MODE", "0") == "1"
    dev_user_id: int = int(os.getenv("DEV_USER_ID", "777000"))

config = Config()

# Проверка конфигурации
if not config.bot_token:
    print("⚠️  Переменная BOT_TOKEN не установлена")
if not config.webapp_url:
    print("⚠️  Переменная WEBAPP_URL не установлена")
