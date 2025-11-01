import os
import io
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import Command
import qrcode


# Загружаем переменные окружения
load_dotenv()

# Получаем токен бота из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения. Проверьте файл .env")

# Инициализируем бота и диспетчер
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer("Привет! Бот запущен и готов к работе.")


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать справку\n\n"
        "📱 <b>Использование:</b>\n"
        "Просто отправьте боту любой текст или ссылку, и я создам для вас QR код!"
    )


@dp.message()
async def generate_qr(message: Message):
    """Обработчик текстовых сообщений для генерации QR кода"""
    # Получаем текст из сообщения
    text = message.text or message.caption or ""
    
    if not text:
        await message.answer("Пожалуйста, отправьте текст или ссылку для генерации QR кода.")
        return
    
    try:
        # Создаем QR код
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        # Создаем изображение
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Сохраняем в байты
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        # Отправляем QR код как фото
        await message.answer_photo(
            photo=BufferedInputFile(img_bytes.read(), filename="qrcode.png"),
            caption=f"QR код для:\n<code>{text[:100]}{'...' if len(text) > 100 else ''}</code>"
        )
    except Exception as e:
        await message.answer(f"Ошибка при генерации QR кода: {str(e)}")


async def main():
    """Основная функция для запуска бота"""
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

