import os
import logging
import requests
import json

# --- КОНСТАНТЫ (ВАШИ ЗНАЧЕНИЯ) ---
# Токен вашего бота.
BOT_TOKEN = '7648623138:AAFyF0GENQmf4N9h9AInhh1c-hIwuOLkdi4' 

# ID целевого канала или чата (используйте числовое значение с минусом).
TARGET_CHAT_ID = -1003165019626

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# --- ГЛАВНАЯ ФУНКЦИЯ ДЛЯ CLOUD FUNCTION ---
def run_forwarder(request):
    """
    Эта функция вызывается по HTTP-запросу из Google Cloud Functions.
    Она однократно проверяет пропущенные сообщения (через getUpdates)
    и пересылает их в целевой канал, после чего завершается.
    """
    logging.info("--- STARTING FORWARDER FUNCTION ---")
    
    # 1. Получаем пропущенные обновления (сообщения)
    try:
        response = requests.get(f"{TELEGRAM_API_URL}/getUpdates")
        response.raise_for_status()
        updates = response.json().get('result', [])
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка при запросе getUpdates: {e}")
        return f"Ошибка API Telegram: {e}", 500

    if not updates:
        logging.info("Нет пропущенных сообщений для пересылки. Завершение.")
        return "Нет пропущенных сообщений для пересылки."

    processed_count = 0
    
    # 2. Обрабатываем и пересылаем каждое сообщение
    for update in updates:
        message = update.get('message')
        if not message:
            continue
        
        # Получаем текст сообщения
        text_to_forward = message.get('text')
        
        # Проверяем, есть ли текст для пересылки
        if text_to_forward:
            try:
                # Отправляем сообщение в целевой канал
                send_response = requests.post(
                    f"{TELEGRAM_API_URL}/sendMessage",
                    json={
                        'chat_id': TARGET_CHAT_ID,
                        'text': text_to_forward
                    }
                )
                send_response.raise_for_status()
                processed_count += 1
                logging.info(f"Переслано сообщение: '{text_to_forward[:30]}...'")

            except requests.exceptions.RequestException as e:
                logging.error(f"Ошибка при пересылке сообщения: {e}")
                # Продолжаем обработку, даже если одно сообщение не отправилось

    # 3. Очищаем очередь, чтобы эти сообщения больше не попадали в getUpdates
    if updates:
        last_update_id = updates[-1]['update_id']
        # Отправляем getUpdates с offset, чтобы подтвердить, что мы обработали все до этого ID
        requests.get(f"{TELEGRAM_API_URL}/getUpdates?offset={last_update_id + 1}")
        logging.info(f"Очередь сообщений очищена до update_id: {last_update_id}")

    logging.info(f"--- ENDING FORWARDER FUNCTION: Успешно обработано {processed_count} сообщений ---")
    return f"Успешно обработано и переслано {processed_count} сообщений."
