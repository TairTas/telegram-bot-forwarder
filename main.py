import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# --- КОНСТАНТЫ (ВАШИ ДАННЫЕ) ------------------------------
TOKEN = '7648623138:AAFyF0GENQmf4N9h9AInhh1c-hIwuOLkdi4' 
OWNER_ID = 1949782369 
CHANNEL_ID = -1003165019626 
# --------------------------------------------------------------------------

# --- ОБРАБОТЧИК ДЛЯ КОМАНДЫ /start ---

async def cmd_start_handler(message: types.Message):
    """
    Обработчик команды /start.
    """
    await message.answer("Привет! Отправь мне сообщение, и я перешлю его пользователю.")


# --- ОСНОВНОЙ ОБРАБОТЧИК ДЛЯ СООБЩЕНИЙ ---

async def handle_student_message(message: types.Message, bot: Bot):
    """
    Обрабатывает входящее сообщение, отправляет лог владельцу и контент в канал.
    """
    user = message.from_user
    
    # 1. Сбор и форматирование информации о пользователе (ЛОГ)
    log_info = (
        "<b>\u26a0\ufe0f НОВОЕ СООБЩЕНИЕ ОТ ПОЛЬЗОВАТЕЛЯ \u26a0\ufe0f</b>\n"
        f"<b>ID:</b> <code>{user.id}</code>\n"
        f"<b>Имя:</b> {user.first_name}\n"
        f"<b>Юзернейм:</b> @{user.username}" if user.username else "Нет юзернейма"
    )

    message_content = ""
    # Определяем тип контента для лога
    if message.text:
        message_content = f"\n\n<b>СОДЕРЖАНИЕ ТЕКСТА:</b>\n{message.html_text}"
    elif message.caption:
        message_content = f"\n\n<b>ПОДПИСЬ:</b>\n{message.caption}"
    else:
        # Если это медиа без подписи или другой тип
        message_content = f"\n\n<b>СОДЕРЖАНИЕ:</b> (Тип: {message.content_type.name})"
        
    full_log = log_info + message_content
    
    # 2. Отправка полного лога владельцу
    try:
        await bot.send_message(OWNER_ID, full_log, parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Не удалось отправить лог владельцу {OWNER_ID}: {e}")
        
    # 3. ОТПРАВКА КОНТЕНТА В КАНАЛ
    try:
        await message.copy_to(
            chat_id=CHANNEL_ID, 
            caption_entities=message.caption_entities
        )
        
        # 4. Уведомление пользователя (Исправлено: "передано пользователю")
        # Если сообщение пришло от владельца (для тестирования), не отвечаем ему же.
        if message.from_user.id != OWNER_ID:
            await message.answer("Ваше сообщение получено и передано пользователю.")
        
    except Exception as e:
        logging.error(f"Ошибка отправки сообщения в канал {CHANNEL_ID}. Проверьте права бота. Ошибка: {e}")
        if message.from_user.id != OWNER_ID:
             await message.answer("Произошла ошибка при отправке сообщения. Пожалуйста, сообщите об этом пользователю.")


# --- ОСНОВНАЯ ФУНКЦИЯ ЗАПУСКА ---

async def main():
    
    # Создаем объекты Bot и Dispatcher
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # 1. Регистрируем команду /start
    dp.message.register(cmd_start_handler, Command("start"))

    # 2. Регистрируем основной обработчик для всех входящих сообщений
    dp.message.register(handle_student_message) 
    
    print("Бот запущен на aiogram (v3.x)...")
    
    # Запускаем опрос, игнорируя старые обновления.
    await dp.start_polling(bot, skip_updates=True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен вручную.")
    except Exception as e:
        logging.error(f"Критическая ошибка запуска: {e}")
