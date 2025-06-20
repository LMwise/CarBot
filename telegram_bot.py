import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from database import (
    add_subscriber,
    get_subscribers,
    get_new_listings,
    db_setup,
    get_connection,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not API_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")

# Инициализируем бота и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Обработчик команды /subscribe
@dp.message(Command("subscribe"))
async def subscribe_handler(message: types.Message):
    chat_id = message.chat.id
    add_subscriber(chat_id)
    await message.answer("✅ Вы подписались на уведомления о новых объявлениях.")

# Обработчик команды /gazwpol
@dp.message(Command("gazwpol"))
async def gazwpol_handler(message: types.Message):
    listings = get_new_listings()
    if listings:
        for listing_id, title, url in listings:
            # Получаем данные из БД
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT price, location_date, category, delivery_cost FROM listings WHERE id = ?', (listing_id,))
                data = cursor.fetchone()

            if data:
                price, location_date, category, delivery_cost = data
                delivery_text = f"📦 Доставка в Вроцлав: {int(delivery_cost)} PLN" if delivery_cost else "🚚 Доставка не рассчитана"
            else:
                price, location_date, category, delivery_text = "Не указана", "Не указано", "Неизвестно", "🚚 Доставка не рассчитана"

            # Формируем сообщение
            message_text = (
                f"📢 *Новое объявление!*\n"
                f"🚗 *{title}*\n"
                f"💰 *Цена:* {price}\n"
                f"📍 *Город:* {location_date}\n"
                f"🏷️ *Состояние:* {category}\n"
                f"{delivery_text}\n"
                f"🔗 [Подробнее]({url})"
            )

            await message.answer(message_text, parse_mode="Markdown")
    else:
        await message.answer("🚀 Пока новых объявлений нет.")


# Фоновая задача для уведомления подписчиков
async def notify_subscribers():
    while True:
        await asyncio.sleep(30)  # Проверка каждые 30 секунд
        subscribers = get_subscribers()
        listings = get_new_listings()
        for chat_id in subscribers:
            for listing_id, title, url in listings:
                # Получаем остальные данные из базы
                with get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('SELECT price, location_date, category, delivery_cost FROM listings WHERE id = ?', (listing_id,))
                    data = cursor.fetchone()

                if data:
                    price, location_date, category, delivery_cost = data
                    delivery_text = f"📦 Доставка в Вроцлав: {delivery_cost} PLN" if delivery_cost else "🚚 Доставка не рассчитана"
                else:
                    price, location_date, category, delivery_text = "Не указана", "Не указано", "Неизвестно", "🚚 Доставка не рассчитана"

                # Формируем сообщение
                message_text = (
                    f"📢 *Новое объявление!*\n"
                    f"🚗 *{title}*\n"
                    f"💰 *Цена:* {price}\n"
                    f"📍 *Город:* {location_date}\n"
                    f"🏷️ *Состояние:* {category}\n"
                    f"{delivery_text}\n"
                    f"🔗 [Подробнее]({url})"
                )

                await bot.send_message(chat_id, message_text, parse_mode="Markdown")

# Главная функция для запуска бота
async def main():
    db_setup()  # Инициализация базы данных
    asyncio.create_task(notify_subscribers())  # Фоновая задача уведомлений
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
