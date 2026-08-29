# Sharp Tongue — Telegram Mini App + Bot

Готовый MVP:
- нижнее меню: **Магазин / Маркет / Инвентарь / Профиль**
- покупка **неулучшенного Sharp Tongue за 100 ⭐**
- ограниченный supply
- один бесплатный Upgrade
- анимация Sharp Tongue, блики, floating, частицы и reveal-анимация
- внутренняя торговля за Pepe Coins
- server-side проверка Telegram Mini App `initData`
- Telegram Stars invoice через `XTR`
- бот + FastAPI backend + frontend

## 1. Установка

```bash
python -m venv .venv
source .venv/bin/activate
# Windows:
# .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
```

Заполни:

```env
BOT_TOKEN=123456:...
WEBAPP_URL=https://your-domain.example
```

## 2. Запуск

Один процесс поднимает и backend, и polling-бота:

```bash
python main.py
```

Backend по умолчанию слушает порт `8000`.

## 3. HTTPS

Telegram Mini App должен быть доступен по публичному HTTPS URL.
Можно задеплоить на Railway / Render / Fly.io / VPS + Caddy/Nginx.

После деплоя укажи адрес:

```env
WEBAPP_URL=https://pepe.example.com
```

Перезапусти приложение.

## 4. BotFather

В @BotFather:
- `/mybots`
- выбрать бота
- Bot Settings
- Configure Mini App / Main Mini App
- указать тот же HTTPS URL

Бот также отправляет кнопку Web App в `/start`.

## 5. Локальный просмотр интерфейса

Для UI-разработки можно временно включить:

```env
DEV_MODE=1
```

После этого открыть `http://localhost:8000`.

**На production обязательно `DEV_MODE=0`.**

## 6. Экономика

`.env`:
- `TOTAL_SUPPLY=1000`
- `PEPE_PRICE_STARS=100`
- `START_COINS=500`
- `MARKET_FEE_PERCENT=5`

Upgrade:
- Uncommon — 45%
- Rare — 30%
- Epic — 18%
- Legendary — 6%
- Mythic — 1%

Pepe Coins — внутриигровые очки без вывода и обмена на Stars/фиат.

## 7. Перед реальным запуском

MVP использует SQLite. Для большого онлайна:
- PostgreSQL
- Redis/очередь
- atomic supply reservation до/на этапе checkout
- админка и moderation
- rate limits
- payment/refund panel
- audit log
- backup
- антибот/антифрод

`telegram_payment_charge_id` сохраняется в БД.


## Быстрый запуск после распаковки

Токен бота уже добавлен в `.env`.

### Посмотреть интерфейс локально

```bash
pip install -r requirements.txt
python main.py
```

Открой:

```text
http://localhost:8000
```

Сейчас `DEV_MODE=1`, поэтому интерфейс можно смотреть в браузере без Telegram.

### Подключить настоящий Mini App к Telegram

1. Задеплой проект на сервер с HTTPS.
2. В `.env` укажи:

```env
WEBAPP_URL=https://твой-домен
DEV_MODE=0
```

3. Перезапусти приложение.
4. В BotFather установи тот же URL как Main Mini App.
5. Напиши своему боту `/start`.

### Посмотреть код

Открой папку проекта в VS Code:

```bash
code .
```

Главные файлы:
- `static/index.html` — интерфейс
- `static/styles.css` — дизайн и анимации
- `static/app.js` — логика Mini App
- `app.py` — API
- `bot.py` — Telegram-бот
- `db.py` — база данных


## Sharp Tongue upgrade mechanic

После покупки предмет хранится как обычный `Sharp Tongue` без коллекционного номера.

При первом бесплатном Upgrade сервер:
1. блокирует транзакцию БД;
2. берёт следующий `collectible_no = MAX + 1`;
3. независимо выбирает случайные Model / Backdrop / Pattern по весам;
4. сохраняет атрибуты навсегда;
5. после этого предмет можно выставить на внутренний маркет.

Поэтому номер зависит именно от **порядка улучшений**, а не от порядка покупок.

В Mini App нет декоративных неработающих кнопок: поиск, сортировка, фильтры инвентаря,
просмотр пула атрибутов, Upgrade, выставление, снятие и покупка лота подключены к логике.


## Visual renderer v2

Карточки Sharp Tongue теперь не используют screenshots. Каждая модель рендерится процедурно в SVG, а фон/узор/анимации строятся из сохранённых traits. Визуал в магазине, коллекции, маркете и upgrade reveal использует один и тот же renderer.


## TON test economy build

- каждому новому аккаунту: **10 TON** внутреннего тестового баланса;
- при старте этой сборки существующим локальным аккаунтам тоже устанавливается 10 TON;
- Sharp Tongue можно покупать бесконечно:
  - **15 Telegram Stars**
  - **0.15 TON** из внутреннего тестового баланса;
- каждый купленный экземпляр можно один раз бесплатно улучшить;
- каждый улучшенный экземпляр получает следующий коллекционный номер;
- маркет полностью переведён на TON;
- цена лота задаётся в TON;
- при покупке TON переводятся с внутреннего баланса покупателя продавцу за вычетом комиссии.

Важно: тестовый TON-баланс в этой сборке не является настоящим blockchain TON и не выводится on-chain.
