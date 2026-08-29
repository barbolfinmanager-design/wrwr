import aiosqlite

DB_PATH = "pepe.db"
NANO = 1_000_000_000

SCHEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;

CREATE TABLE IF NOT EXISTS users (
  user_id INTEGER PRIMARY KEY,
  username TEXT,
  first_name TEXT,
  ton_nano INTEGER NOT NULL DEFAULT 10000000000,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gifts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  owner_id INTEGER NOT NULL,
  purchase_serial INTEGER NOT NULL UNIQUE,
  collectible_no INTEGER UNIQUE,
  model TEXT,
  model_rarity REAL,
  model_style TEXT,
  backdrop TEXT,
  backdrop_rarity REAL,
  backdrop_c1 TEXT,
  backdrop_c2 TEXT,
  pattern TEXT,
  pattern_rarity REAL,
  pattern_icon TEXT,
  upgrade_used INTEGER NOT NULL DEFAULT 0,
  paid_with TEXT NOT NULL DEFAULT 'TON',
  stars_paid INTEGER NOT NULL DEFAULT 0,
  ton_paid_nano INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  upgraded_at TEXT,
  FOREIGN KEY(owner_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS payments (
  charge_id TEXT PRIMARY KEY,
  user_id INTEGER NOT NULL,
  amount_stars INTEGER NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS listings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  gift_id INTEGER NOT NULL,
  seller_id INTEGER NOT NULL,
  price_ton_nano INTEGER NOT NULL,
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(gift_id) REFERENCES gifts(id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_active_listing_gift
ON listings(gift_id) WHERE active=1;
CREATE UNIQUE INDEX IF NOT EXISTS idx_collectible_no
ON gifts(collectible_no) WHERE collectible_no IS NOT NULL;
"""

async def _columns(db, table):
    cur = await db.execute(f"PRAGMA table_info({table})")
    return {r[1] for r in await cur.fetchall()}

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)

        ucols = await _columns(db, "users")
        if "ton_nano" not in ucols:
            await db.execute("ALTER TABLE users ADD COLUMN ton_nano INTEGER")
            await db.execute("UPDATE users SET ton_nano=10000000000 WHERE ton_nano IS NULL")

        gcols = await _columns(db, "gifts")
        additions = {
            "purchase_serial":"INTEGER","collectible_no":"INTEGER",
            "model":"TEXT","model_rarity":"REAL","model_style":"TEXT",
            "backdrop":"TEXT","backdrop_rarity":"REAL","backdrop_c1":"TEXT","backdrop_c2":"TEXT",
            "pattern":"TEXT","pattern_rarity":"REAL","pattern_icon":"TEXT",
            "upgrade_used":"INTEGER NOT NULL DEFAULT 0","paid_with":"TEXT NOT NULL DEFAULT 'TON'",
            "stars_paid":"INTEGER NOT NULL DEFAULT 0","ton_paid_nano":"INTEGER NOT NULL DEFAULT 0",
            "upgraded_at":"TEXT"
        }
        for col, typ in additions.items():
            if col not in gcols:
                await db.execute(f"ALTER TABLE gifts ADD COLUMN {col} {typ}")
        if "serial" in gcols:
            await db.execute("UPDATE gifts SET purchase_serial=serial WHERE purchase_serial IS NULL")

        lcols = await _columns(db, "listings")
        if "price_ton_nano" not in lcols:
            await db.execute("ALTER TABLE listings ADD COLUMN price_ton_nano INTEGER")
            if "price_coins" in lcols:
                # Old dev listings are converted 1 coin -> 0.001 TON only to keep local test DB usable.
                await db.execute("""
                    UPDATE listings
                    SET price_ton_nano=price_coins*1000000
                    WHERE price_ton_nano IS NULL
                """)

        # For this test build every existing account gets 10 TON.
        await db.execute("UPDATE users SET ton_nano=10000000000")
        await db.commit()

async def ensure_user(user_id: int, username: str | None, first_name: str | None, start_ton_nano: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
        if await cur.fetchone() is None:
            await db.execute(
                "INSERT INTO users(user_id,username,first_name,ton_nano) VALUES(?,?,?,?)",
                (user_id, username, first_name, start_ton_nano)
            )
        else:
            await db.execute(
                "UPDATE users SET username=?,first_name=? WHERE user_id=?",
                (username,first_name,user_id)
            )
        await db.commit()

async def stats(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT COUNT(*) FROM gifts")
        minted = (await cur.fetchone())[0]
        cur = await db.execute("SELECT COUNT(*) FROM gifts WHERE collectible_no IS NOT NULL")
        upgraded = (await cur.fetchone())[0]
        cur = await db.execute("SELECT COUNT(*) FROM gifts WHERE owner_id=?", (user_id,))
        owned = (await cur.fetchone())[0]
        cur = await db.execute("SELECT ton_nano,username,first_name FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        return {
            "minted":minted,"upgraded":upgraded,"owned":owned,
            "ton_nano":row[0] if row else 0,
            "ton":round((row[0] if row else 0)/NANO, 9),
            "username":row[1] if row else None,"first_name":row[2] if row else None
        }

async def _next_purchase_serial(db):
    cur = await db.execute("SELECT COALESCE(MAX(purchase_serial),0)+1 FROM gifts")
    return (await cur.fetchone())[0]

async def mint_with_stars(user_id: int, charge_id: str, amount_stars: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("BEGIN IMMEDIATE")
        cur = await db.execute("SELECT 1 FROM payments WHERE charge_id=?", (charge_id,))
        if await cur.fetchone():
            await db.rollback()
            return None
        serial = await _next_purchase_serial(db)
        cur = await db.execute("""
            INSERT INTO gifts(owner_id,purchase_serial,paid_with,stars_paid)
            VALUES(?,?, 'STARS', ?)
        """,(user_id,serial,amount_stars))
        gift_id=cur.lastrowid
        await db.execute(
            "INSERT INTO payments(charge_id,user_id,amount_stars) VALUES(?,?,?)",
            (charge_id,user_id,amount_stars)
        )
        await db.commit()
        return {"id":gift_id,"purchase_serial":serial}

async def buy_gift_with_ton(user_id: int, price_ton_nano: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("BEGIN IMMEDIATE")
        cur = await db.execute("SELECT ton_nano FROM users WHERE user_id=?", (user_id,))
        row = await cur.fetchone()
        if not row or row[0] < price_ton_nano:
            await db.rollback()
            return None, "Недостаточно TON."
        serial = await _next_purchase_serial(db)
        await db.execute("UPDATE users SET ton_nano=ton_nano-? WHERE user_id=?", (price_ton_nano,user_id))
        cur = await db.execute("""
            INSERT INTO gifts(owner_id,purchase_serial,paid_with,ton_paid_nano)
            VALUES(?,?, 'TON', ?)
        """,(user_id,serial,price_ton_nano))
        gift_id=cur.lastrowid
        await db.commit()
        return {"id":gift_id,"purchase_serial":serial}, "Подарок куплен за TON."

def _gift_dict(r):
    return dict(
        id=r[0],purchase_serial=r[1],collectible_no=r[2],
        model=r[3],model_rarity=r[4],model_style=r[5],
        backdrop=r[6],backdrop_rarity=r[7],backdrop_c1=r[8],backdrop_c2=r[9],
        pattern=r[10],pattern_rarity=r[11],pattern_icon=r[12],
        upgrade_used=bool(r[13]),listed=bool(r[14]),listing_price_ton_nano=r[15],
        listing_price_ton=round((r[15] or 0)/NANO,9),paid_with=r[16]
    )

async def inventory(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur=await db.execute("""
          SELECT g.id,g.purchase_serial,g.collectible_no,
                 g.model,g.model_rarity,g.model_style,
                 g.backdrop,g.backdrop_rarity,g.backdrop_c1,g.backdrop_c2,
                 g.pattern,g.pattern_rarity,g.pattern_icon,g.upgrade_used,
                 CASE WHEN l.id IS NULL THEN 0 ELSE 1 END,
                 COALESCE(l.price_ton_nano,0),g.paid_with
          FROM gifts g
          LEFT JOIN listings l ON l.gift_id=g.id AND l.active=1
          WHERE g.owner_id=? ORDER BY g.id DESC
        """,(user_id,))
        return [_gift_dict(r) for r in await cur.fetchall()]

async def get_gift(gift_id:int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur=await db.execute("""
          SELECT id,owner_id,purchase_serial,collectible_no,upgrade_used
          FROM gifts WHERE id=?
        """,(gift_id,))
        r=await cur.fetchone()
        return None if not r else dict(id=r[0],owner_id=r[1],purchase_serial=r[2],collectible_no=r[3],upgrade_used=bool(r[4]))

async def upgrade(gift_id:int,owner_id:int,model:dict,backdrop:dict,pattern:dict):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("BEGIN IMMEDIATE")
        cur=await db.execute("""
          SELECT owner_id,upgrade_used FROM gifts
          WHERE id=? AND NOT EXISTS(
            SELECT 1 FROM listings WHERE gift_id=? AND active=1
          )
        """,(gift_id,gift_id))
        row=await cur.fetchone()
        if not row or row[0]!=owner_id or row[1]:
            await db.rollback();return None
        cur=await db.execute("SELECT COALESCE(MAX(collectible_no),0)+1 FROM gifts")
        no=(await cur.fetchone())[0]
        cur=await db.execute("""
          UPDATE gifts SET collectible_no=?,
          model=?,model_rarity=?,model_style=?,
          backdrop=?,backdrop_rarity=?,backdrop_c1=?,backdrop_c2=?,
          pattern=?,pattern_rarity=?,pattern_icon=?,
          upgrade_used=1,upgraded_at=CURRENT_TIMESTAMP
          WHERE id=? AND owner_id=? AND upgrade_used=0
        """,(no,model["name"],model["weight"],model["style"],
             backdrop["name"],backdrop["weight"],backdrop["colors"][0],backdrop["colors"][1],
             pattern["name"],pattern["weight"],pattern["icon"],gift_id,owner_id))
        if cur.rowcount!=1:
            await db.rollback();return None
        await db.commit();return no

async def list_item(gift_id:int,seller_id:int,price_ton_nano:int):
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            cur=await db.execute("""
              INSERT INTO listings(gift_id,seller_id,price_ton_nano,active)
              SELECT id,owner_id,?,1 FROM gifts
              WHERE id=? AND owner_id=?
              AND NOT EXISTS(SELECT 1 FROM listings WHERE gift_id=? AND active=1)
            """,(price_ton_nano,gift_id,seller_id,gift_id))
            await db.commit();return cur.rowcount==1
        except aiosqlite.IntegrityError:
            return False

async def cancel_listing(gift_id:int,seller_id:int):
    async with aiosqlite.connect(DB_PATH) as db:
        cur=await db.execute("UPDATE listings SET active=0 WHERE gift_id=? AND seller_id=? AND active=1",(gift_id,seller_id))
        await db.commit();return cur.rowcount==1

async def market(limit=100):
    async with aiosqlite.connect(DB_PATH) as db:
        cur=await db.execute("""
          SELECT l.id,g.id,g.purchase_serial,g.collectible_no,
                 g.model,g.model_rarity,g.model_style,
                 g.backdrop,g.backdrop_rarity,g.backdrop_c1,g.backdrop_c2,
                 g.pattern,g.pattern_rarity,g.pattern_icon,
                 l.price_ton_nano,l.seller_id
          FROM listings l JOIN gifts g ON g.id=l.gift_id
          WHERE l.active=1 ORDER BY l.id DESC LIMIT ?
        """,(limit,))
        rows=await cur.fetchall()
        return [dict(
          listing_id=r[0],gift_id=r[1],purchase_serial=r[2],collectible_no=r[3],
          model=r[4],model_rarity=r[5],model_style=r[6],
          backdrop=r[7],backdrop_rarity=r[8],backdrop_c1=r[9],backdrop_c2=r[10],
          pattern=r[11],pattern_rarity=r[12],pattern_icon=r[13],
          price_ton_nano=r[14],price_ton=round(r[14]/NANO,9),seller_id=r[15]
        ) for r in rows]

async def buy_listing(listing_id:int,buyer_id:int,fee_percent:int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("BEGIN IMMEDIATE")
        cur=await db.execute("""
          SELECT l.gift_id,l.seller_id,l.price_ton_nano,g.owner_id
          FROM listings l JOIN gifts g ON g.id=l.gift_id
          WHERE l.id=? AND l.active=1
        """,(listing_id,))
        row=await cur.fetchone()
        if not row:
            await db.rollback();return False,"Лот уже недоступен."
        gift_id,seller_id,price,owner_id=row
        if seller_id==buyer_id:
            await db.rollback();return False,"Нельзя купить свой подарок."
        if owner_id!=seller_id:
            await db.execute("UPDATE listings SET active=0 WHERE id=?",(listing_id,))
            await db.commit();return False,"Лот устарел."
        cur=await db.execute("SELECT ton_nano FROM users WHERE user_id=?",(buyer_id,))
        buyer=await cur.fetchone()
        if not buyer or buyer[0]<price:
            await db.rollback();return False,"Недостаточно TON."
        fee=price*fee_percent//100
        seller_gets=price-fee
        await db.execute("UPDATE users SET ton_nano=ton_nano-? WHERE user_id=?",(price,buyer_id))
        await db.execute("UPDATE users SET ton_nano=ton_nano+? WHERE user_id=?",(seller_gets,seller_id))
        await db.execute("UPDATE gifts SET owner_id=? WHERE id=?",(buyer_id,gift_id))
        await db.execute("UPDATE listings SET active=0 WHERE id=?",(listing_id,))
        await db.commit()
        return True,f"Куплено за {price/NANO:.3f} TON · комиссия {fee/NANO:.3f} TON"
