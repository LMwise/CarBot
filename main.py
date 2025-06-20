# main.py

import os
import logging
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def continuous_scrape(urls, interval=60):
    """Цикл парсинга с обработкой ошибок"""
    logger.info("Запуск цикла парсинга...")
    while True:
        try:
            logger.info("Инициализация драйвера...")
            driver = get_driver(headless=True)

            for url in urls:
                logger.info(f"Открываем страницу: {url}")
                try:
                    driver.get(url)
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-cy='ad-card-title']"))
                    )
                    logger.info("Страница успешно загружена.")
                except Exception as e:
                    logger.error(f"Ошибка при загрузке страницы: {e}")
                    continue

                try:
                    logger.info("Парсинг страницы...")
                    page_source = driver.page_source
                    listings = parse_listings(page_source, base_url="https://www.olx.pl")
                    logger.info(f"Найдено объявлений: {len(listings)}")
                except Exception as e:
                    logger.error(f"Ошибка парсинга: {e}")
                    continue

                for listing in listings:
                    try:
                        logger.info(f"Сохранение объявления: {listing['title']}")
                        loop = asyncio.get_running_loop()
                        inserted = await loop.run_in_executor(None, insert_listing, listing)
                        if inserted:
                            logger.debug(f"Новое объявление: {listing['title']}")
                    except Exception as e:
                        logger.error(f"Ошибка сохранения: {e}")

            logger.info("Завершение работы драйвера...")
            driver.quit()
            logger.info(f"Ожидание {interval} секунд перед следующим циклом...")
            await asyncio.sleep(interval)

        except WebDriverException as e:
            logger.error(f"Критическая ошибка браузера: {e}")
            await asyncio.sleep(10)

"""Facebook"""



if __name__ == "__main__":
    logger.info("Инициализация базы данных...")
    db_setup()
    logger.info("Запуск основного цикла...")
    asyncio.run(continuous_scrape(URLS))
