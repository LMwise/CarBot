from bs4 import BeautifulSoup
import hashlib
from nlp_utils import analyze_listing, calculate_delivery_cost


def parse_listings(page_source, base_url="https://www.olx.pl"):
    """Парсинг объявлений с OLX с исправленным поиском города"""
    try:
        soup = BeautifulSoup(page_source, 'html.parser')
        listing_blocks = soup.find_all('div', attrs={'data-cy': 'ad-card-title'})
        print(f"[INFO] Найдено блоков объявлений: {len(listing_blocks)}")

        listings = []

        for i, block in enumerate(listing_blocks, start=1):
            try:
                # --- URL ---
                link_tag = block.find('a', href=True)
                url = f"{base_url}{link_tag['href']}" if link_tag else "No URL"

                # --- Заголовок ---
                title_tag = link_tag.find('h4') if link_tag else None
                title = title_tag.get_text(strip=True) if title_tag else "No Title"

                # --- Цена ---
                price_tag = block.find('p', attrs={'data-testid': 'ad-price'})
                price = price_tag.get_text(strip=True) if price_tag else "No Price"

                # --- Локация и дата (Исправлено) ---
                location_date_tag = block.find_next('p', attrs={'data-testid': 'location-date'})

                if location_date_tag:
                    location_date = location_date_tag.get_text(strip=True)
                    location_date = location_date.split("–")[0].strip()  # Убираем "Odświeżono..."
                else:
                    location_date = "No Location/Date"
                    print(f"[WARNING] Город не найден! Полный HTML объявления #{i}:\n{block.find_parent().prettify()[:1000]}")

                delivery_info, delivery_cost = calculate_delivery_cost(location_date)

                # --- Пробег ---
                mileage_tag = block.find('p', attrs={'data-testid': 'mileage'})
                mileage = mileage_tag.get_text(strip=True) if mileage_tag else "No Mileage"

                # --- Генерация ID ---
                listing_id = hashlib.md5(url.encode()).hexdigest()

                # --- Создание объявления ---
                listing = {
                    'id': listing_id,
                    'title': title,
                    'price': price,
                    'location_date': location_date,
                    'mileage': mileage,
                    'url': url,
                    'delivery_cost': delivery_cost  # Сохранение доставки
                }

                # --- Анализ AI ---
                listing = analyze_listing(listing)

                listings.append(listing)


            except Exception as e:
                print(f"[ERROR] Ошибка парсинга блока #{i}: {e}")
                continue

        return listings

    except Exception as e:
        print(f"[FATAL ERROR] Ошибка парсинга страницы: {e}")
        return []
