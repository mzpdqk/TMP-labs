from mistralai import Mistral
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import asyncpg
import aiohttp

# Конфигурация
mistral_api_key = os.getenv("MISTRAL_API_KEY")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
model = "mistral-large-latest"

# PostgreSQL connection settings
POSTGRES_USER = os.getenv("PGUSER")
POSTGRES_PASSWORD = os.getenv("PGPASSWORD")
POSTGRES_DB = os.getenv("PGDATABASE")
POSTGRES_HOST = os.getenv("PGHOST")
POSTGRES_PORT = os.getenv("PGPORT")

# Webhook настройки
WEBHOOK_PATH = "/webhook"
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "your-secret-key")
PORT = int(os.getenv("PORT", 8000))
WAKEUP_INTERVAL = 300

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(TOKEN)
dp = Dispatcher()
client = Mistral(api_key=mistral_api_key)

class Database:
    def __init__(self):
        self.pool = None
        self.logger = logging.getLogger(__name__ + ".Database")

    async def connect(self):
        self.logger.info(f"Connecting to PostgreSQL at {POSTGRES_HOST}:{POSTGRES_PORT}")
        try:
            self.pool = await asyncpg.create_pool(
                user=POSTGRES_USER,
                password="***",  # Маскируем пароль в логах
                database=POSTGRES_DB,
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                ssl="require"
            )
            await self.create_tables()
            self.logger.info("Successfully connected to PostgreSQL database")
        except Exception as e:
            self.logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    async def create_tables(self):
        self.logger.debug("Creating database tables if not exist")
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    role VARCHAR(20) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    is_system BOOLEAN DEFAULT FALSE
                );
                CREATE INDEX IF NOT EXISTS idx_chat_id ON chat_history(chat_id);
            ''')

    async def init_chat(self, chat_id: int):
        self.logger.debug(f"Initializing chat {chat_id}")
        async with self.pool.acquire() as conn:
            exists = await conn.fetchval(
                "SELECT 1 FROM chat_history WHERE chat_id = $1 AND is_system = TRUE",
                chat_id
            )
            if not exists:
                self.logger.info(f"Creating new chat session for {chat_id}")
                await conn.execute(
                    "INSERT INTO chat_history (chat_id, role, content, is_system) VALUES ($1, $2, $3, $4)",
                    chat_id, "system", "Ты полезный ассистент, отвечай кратко и по делу.", True
                )

    async def get_history(self, chat_id: int):
        self.logger.debug(f"Getting history for chat {chat_id}")
        async with self.pool.acquire() as conn:
            records = await conn.fetch(
                "SELECT role, content FROM chat_history WHERE chat_id = $1 ORDER BY created_at",
                chat_id
            )
            self.logger.debug(f"Retrieved {len(records)} messages for chat {chat_id}")
            return [dict(r) for r in records]

    async def add_message(self, chat_id: int, role: str, content: str):
        self.logger.debug(f"Adding {role} message to chat {chat_id}")
        async with self.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO chat_history (chat_id, role, content) VALUES ($1, $2, $3)",
                chat_id, role, content
            )

    async def clean_history(self, chat_id: int, max_messages: int = 10):
        self.logger.debug(f"Cleaning history for chat {chat_id}, keeping max {max_messages} messages")
        async with self.pool.acquire() as conn:
            deleted = await conn.execute('''
                DELETE FROM chat_history 
                WHERE id IN (
                    SELECT id FROM (
                        SELECT id, ROW_NUMBER() OVER (
                            PARTITION BY is_system ORDER BY created_at DESC
                        ) as rn 
                        FROM chat_history 
                        WHERE chat_id = $1 AND is_system = FALSE
                    ) sub
                    WHERE rn > $2
                )
            ''', chat_id, max_messages - 1)
            self.logger.debug(f"History cleaned for chat {chat_id}: {deleted}")

db = Database()

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer('Привет! Я - бот с нейросетью, отправь запрос')

@dp.message(Command("wakeup"))
async def cmd_wakeup(message: Message):
    await message.answer("Я бодрствую! ⚡")

@dp.message(F.text)
async def handle_message(message: Message):
    chat_id = message.chat.id
    await db.init_chat(chat_id)
    await db.add_message(chat_id, "user", message.text)
    history = await db.get_history(chat_id)
    
    try:
        response = client.chat.complete(
            model=model,
            messages=history
        )
        answer = response.choices[0].message.content
        await db.add_message(chat_id, "assistant", answer)
        await db.clean_history(chat_id)
        await message.answer(answer, parse_mode="Markdown")
    except Exception:
        await message.answer("Произошла ошибка при обработке запроса")

async def get_webhook_url(app: web.Application) -> str:
    """Получает базовый URL сервиса на Render"""
    if "RENDER" not in os.environ:
        return f"http://localhost:{PORT}{WEBHOOK_PATH}"
    
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_url:
        return f"{render_url}{WEBHOOK_PATH}"
    
    service_name = os.getenv("RENDER_SERVICE_NAME")
    return f"https://{service_name}.onrender.com{WEBHOOK_PATH}"

async def get_self_url() -> str:
    """Определяет URL сервера для self-ping"""
    if "RENDER" not in os.environ:
        return f"http://localhost:{PORT}"
    
    render_url = os.getenv("RENDER_EXTERNAL_URL")
    if render_url:
        return render_url.rstrip('/')
    
    service_name = os.getenv("RENDER_SERVICE_NAME")
    return f"https://{service_name}.onrender.com"

async def self_ping():
    """Отправляет запрос к своему же серверу для предотвращения сна"""
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                url = await get_self_url()
                async with session.get(f"{url}/wakeup") as resp:
                    pass
        except Exception:
            pass
        await asyncio.sleep(WAKEUP_INTERVAL)

async def on_startup(app: web.Application):
    await db.connect()
    async with db.pool.acquire() as conn:
        version = await conn.fetchval("SELECT version();")
    
    webhook_url = await get_webhook_url(app)
    await bot.set_webhook(url=webhook_url, secret_token=WEBHOOK_SECRET)

async def on_shutdown(app: web.Application):
    await bot.delete_webhook()
    await db.pool.close()

async def create_app():
    app = web.Application()
    app["bot"] = bot
    
    # Регистрация обработчиков
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=WEBHOOK_SECRET
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    
    # Добавляем эндпоинт для wakeup
    async def wakeup_handler(request):
        return web.Response(text="OK")
    
    app.router.add_get('/wakeup', wakeup_handler)
    
    # События запуска/остановки
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    # Запускаем self-ping в фоне
    app.on_startup.append(lambda _: asyncio.create_task(self_ping()))
    
    setup_application(app, dp, bot=bot)
    return app

if __name__ == "__main__":
    logger.info(f"Starting bot on port {PORT}")
    app = asyncio.run(create_app())
    web.run_app(
        app,
        host="0.0.0.0",
        port=PORT
    )
