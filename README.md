# Sharp Tongue - Telegram Mini App

## 🚀 Быстрый старт

### Локально

1. Клонируй репо:
```bash
git clone <repo-url>
cd wrwr
```

2. Создай `.env` файл:
```bash
cp env.example .env
```

3. Заполни переменные в `.env`:
```
BOT_TOKEN=your_token_from_botfather
WEBAPP_URL=http://localhost:8000
```

4. Установи зависимости:
```bash
pip install -r requirements.txt
```

5. Запусти приложение:
```bash
python main.py
```

Приложение будет доступно на http://localhost:8000

### На Railway

1. Подключи этот репо к Railway
2. Добавь переменные в Railway Dashboard (Project → Variables):
   - `BOT_TOKEN` - токен от @BotFather
   - `WEBAPP_URL` - URL твоего Railway приложения (например: https://my-app.railway.app)
3. Railway автоматически соберет и запустит приложение

## 📋 Переменные окружения

| Переменная | Описание | Пример |
|---|---|---|
| BOT_TOKEN | Токен Telegram бота | `123:ABC...` |
| WEBAPP_URL | URL веб-приложения | `https://app.railway.app` |
| HOST | Адрес сервера | `0.0.0.0` |
| PORT | Порт сервера | `8000` |
| PEPE_PRICE_STARS | Цена в звездах Telegram | `15` |
| GIFT_PRICE_TON_NANO | Цена в TON (нано) | `150000000` |

## 🏗️ Структура проекта

```
wrwr/
├── bot.py              # Telegram бот
├── app.py              # FastAPI веб-приложение
├── db.py               # Работа с БД
├── config.py           # Конфигурация
├── main.py             # Точка входа
├── static/
│   ├── index.html      # Фронтенд
│   ├── styles.css      # Стили
│   └── app.js          # JavaScript
├── requirements.txt    # Зависимости
└── Dockerfile          # Docker образ
```

## 🐳 Docker

```bash
# Собрать образ
docker build -t sharp-tongue .

# Запустить контейнер
docker run -e BOT_TOKEN=your_token -e WEBAPP_URL=http://localhost:8000 -p 8000:8000 sharp-tongue
```

## 🔧 Технологический стек

- **Backend**: Python, FastAPI, aiogram
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (aiosqlite)
- **Deployment**: Docker, Railway

## 📝 Лицензия

MIT
