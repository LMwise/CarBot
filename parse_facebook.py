from bs4 import BeautifulSoup
import time
import hashlib
import logging
from selenium_driver_setup import get_facebook_driver

logger = logging.getLogger(__name__)

FB_MARKETPLACE_URL = "https://www.facebook.com/marketplace/category/vehicles"

def parse_facebook_listings():
    """Парсинг Facebook Marketplace с логами"""
    logger.info("Запуск парсинга Facebook Marketplace...")

    try:
        driver = get_facebook_driver(headless=True)
        logger.debug("Драйвер успешно запущен, открываем Facebook Marketplace...")

        driver.get(FB_MARKETPLACE_URL)
        time.sleep(5)

        logger.info("Загружаем страницу Facebook Marketplace...")
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Найдём объявления
        listing_blocks = soup.find_all("div", class_="x1i10hfl x6umtig x1j85h84")
        logger.info(f"Найдено объявлений: {len(listing_blocks)}")

        listings = []

        for i, item in enumerate(listing_blocks):
            try:
                title_tag = item.find("span")
                price_tag = item.find("span", class_="x193iq5w xeuugli")
                url_tag = item.find("a")

                if not title_tag or not url_tag:
                    logger.warning(
                        f"Пропущено объявление #{i+1} (нет заголовка или ссылки)"
                    )
                    continue

                title = title_tag.text.strip()
                price = price_tag.text.strip() if price_tag else "Не указана"
                url = "https://www.facebook.com" + url_tag["href"]

                # Генерируем ID на основе ссылки
                listing_id = hashlib.md5(url.encode()).hexdigest()

                listing = {
                    "id": listing_id,
                    "title": title,
                    "price": price,
                    "url": url,
                }

                listings.append(listing)
                logger.debug(f"Объявление #{i+1}: {title} | {price} | {url}")

            except Exception as e:
                logger.error(f"Ошибка при парсинге объявления #{i+1}: {e}")
                continue

        driver.quit()
        logger.info(f"Парсинг Facebook завершён, найдено {len(listings)} объявлений.")
        return listings

    except Exception as e:
        logger.error(f"Ошибка при парсинге Facebook Marketplace: {e}")
        return []
