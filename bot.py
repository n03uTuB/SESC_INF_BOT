import os
import io
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, BufferedInputFile, BotCommand
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
    await message.answer(
        "👋 <b>Добро пожаловать в QR Code Generator Bot!</b>\n\n"
        "Я умею генерировать QR коды из любого текста или ссылки.\n\n"
        "📝 <b>Как использовать:</b>\n"
        "Просто отправьте мне любой текст или ссылку, и я создам для вас QR код!\n\n"
        "💡 Попробуйте отправить:\n"
        "• Текст: <code>Привет, мир!</code>\n"
        "• Ссылку: <code>https://example.com</code>\n"
        "• Контакты, Wi-Fi пароли и многое другое\n\n"
        "Для списка команд используйте /help"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    await message.answer(
        "📚 <b>Справка по командам:</b>\n\n"
        "🔹 <code>/start</code> - Начать работу с ботом и получить приветственное сообщение\n"
        "🔹 <code>/help</code> - Показать эту справку\n"
        "🔹 <code>/about</code> - Информация о боте\n\n"
        "📱 <b>Основной функционал:</b>\n"
        "Отправьте мне <b>любой текст</b> или <b>ссылку</b>, и я мгновенно создам QR код с этим содержимым!\n\n"
        "💡 <b>Примеры использования:</b>\n"
        "• Текстовые сообщения\n"
        "• URL адреса\n"
        "• Wi-Fi пароли в формате: <code>WIFI:T:WPA;S:Название;P:пароль;;</code>\n"
        "• Контактная информация (vCard)\n"
        "• И многое другое!\n\n"
        "⚡ <b>Быстрый старт:</b>\n"
        "Просто напишите что-нибудь, и получите QR код!"
    )


@dp.message(Command("about"))
async def cmd_about(message: Message):
    """Обработчик команды /about"""
    await message.answer(
        "ℹ️ <b>О боте:</b>\n\n"
        "🤖 <b>QR Code Generator Bot</b>\n\n"
        "Этот бот позволяет легко создавать QR коды из любого текста или ссылки.\n\n"
        "🔧 <b>Технологии:</b>\n"
        "• Python 3.12+\n"
        "• aiogram 3.x\n"
        "• qrcode library\n\n"
        "📦 <b>Возможности:</b>\n"
        "✓ Генерация QR кодов из текста\n"
        "✓ Поддержка URL адресов\n"
        "✓ Быстрая обработка запросов\n"
        "✓ Отправка QR кодов как изображений\n\n"
        "Для начала работы отправьте /start"
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


async def set_bot_commands():
    """Устанавливает меню команд бота"""
    commands = [
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="help", description="Показать справку по командам"),
        BotCommand(command="about", description="Информация о боте"),
    ]
    await bot.set_my_commands(commands)


async def set_bot_description():
    """Устанавливает описание бота (показывается до /start)"""
    description = (
        "🤖 Генератор QR кодов\n\n"
        "Отправьте мне любой текст или ссылку, и я создам QR код!\n"
        "Поддерживает URL, Wi-Fi пароли, контакты и многое другое."
    )
    await bot.set_my_description(description=description)
    
    # Также устанавливаем короткое описание для меню команд
    short_description = "Генератор QR кодов из текста и ссылок"
    await bot.set_my_short_description(short_description=short_description)


async def main():
    """Основная функция для запуска бота"""
    print("Бот запускается...")
    
    # Устанавливаем описание и команды
    await set_bot_description()
    await set_bot_commands()
    
    print("Описание и меню команд установлены!")
    print("Бот запущен и готов к работе...")
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

