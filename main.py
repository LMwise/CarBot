# main.py

import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"  # Игнорируем предупреждения о симлинках

import asyncio
from selenium_driver_setup import get_driver
from parse_listings import parse_listings
from settings import URLS
from database import insert_listing, db_setup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
"""from parse_facebook import parse_facebook_listings"""

async def continuous_scrape(urls, interval=60):
    """Цикл парсинга с обработкой ошибок"""
    print("[INFO] Запуск цикла парсинга...")
    while True:
        try:
            print("[INFO] Инициализация драйвера...")
            driver = get_driver(headless=True)

            for url in urls:
                print(f"\n[INFO] Открываем страницу: {url}")
                try:
                    driver.get(url)
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-cy='ad-card-title']"))
                    )
                    print("[INFO] Страница успешно загружена.")
                except Exception as e:
                    print(f"[ERROR] Ошибка при загрузке страницы: {e}")
                    continue

                try:
                    print("[INFO] Парсинг страницы...")
                    page_source = driver.page_source
                    listings = parse_listings(page_source, base_url="https://www.olx.pl")
                    print(f"[INFO] Найдено объявлений: {len(listings)}")
                except Exception as e:
                    print(f"[ERROR] Ошибка парсинга: {e}")
                    continue

                for listing in listings:
                    try:
                        print(f"[INFO] Сохранение объявления: {listing['title']}")
                        loop = asyncio.get_running_loop()
                        inserted = await loop.run_in_executor(None, insert_listing, listing)
                        if inserted:
                            print(f"[DEBUG] Новое объявление: {listing['title']}")
                    except Exception as e:
                        print(f"[ERROR] Ошибка сохранения: {e}")

            print("[INFO] Завершение работы драйвера...")
            driver.quit()
            print(f"[INFO] Ожидание {interval} секунд перед следующим циклом...")
            await asyncio.sleep(interval)

        except WebDriverException as e:
            print(f"[FATAL ERROR] Критическая ошибка браузера: {e}")
            await asyncio.sleep(10)

"""Facebook"""
"""async def continuous_facebook_scrape(interval=600):
    while True:
        print("[INFO] Парсим Facebook Marketplace...")
        listings = parse_facebook_listings()

        for listing in listings:
            inserted = insert_listing(listing)
            if inserted:
                print(f"[DEBUG] Добавлено объявление с Facebook: {listing['title']}")

        print(f"[INFO] Ожидание {interval} секунд перед следующим парсингом...")
        await asyncio.sleep(interval)"""


if __name__ == "__main__":
    print("[INFO] Инициализация базы данных...")
    db_setup()
    print("[INFO] Запуск основного цикла...")
    asyncio.run(continuous_scrape(URLS))
    """asyncio.create_task(continuous_facebook_scrape())
    print("Парсинг facebook")"""