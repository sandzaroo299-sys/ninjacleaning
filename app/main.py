"""
Точка входа FastAPI + запуск бота.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.routes import router as api_router
from app.config import settings
from app.db import init_db
from app.bot.main import start_bot, stop_bot

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

bot_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global bot_task
    logger.info("Инициализация базы данных...")
    init_db()
    logger.info("База данных готова.")

    logger.info("Запуск Telegram-бота...")
    bot_task = asyncio.create_task(start_bot())
    logger.info("Бот запущен.")

    yield

    logger.info("Остановка Telegram-бота...")
    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
    await stop_bot()
    logger.info("Бот остановлен.")


app = FastAPI(title="Промышленный альпинизм - Мойка окон", version="1.0.0", lifespan=lifespan)
app.include_router(api_router)

static_dir = Path(__file__).resolve().parent.parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
else:
    logger.warning("Папка static не найдена!")

@app.get("/")
async def serve_index():
    index_path = static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Mini App не найден. Разместите файлы в папке static/"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "bot_token_set": bool(settings.BOT_TOKEN)}
