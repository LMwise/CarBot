import logging
import requests
from geopy.distance import geodesic
from transformers import pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

classifier = None  # Глобальная переменная для NLP-модели

# Настройки доставки
FUEL_CONSUMPTION_PER_100KM = 10  # литров на 100 км
FUEL_PRICE_PER_LITER = 6.50  # PLN за литр
WROCLAW_COORDS = (51.1079, 17.0385)  # Координаты Вроцлава

# Функция загрузки NLP-модели
def load_model():
    """Загружаем NLP-модель"""
    global classifier
    try:
        logger.info("[INFO] Загружаем NLP-модель...")
        classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=-1  # Используем CPU
        )
        logger.info("[INFO] NLP-модель успешно загружена.")
    except Exception as e:
        logger.error(f"[ERROR] Ошибка загрузки NLP-модели: {e}")
        classifier = None

# Функция определения координат города
def get_city_coordinates(city_name):
    """
    Определяет координаты города по названию через OpenStreetMap API.
    """
    try:
        url = f"https://nominatim.openstreetmap.org/search?city={city_name}&format=json"
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            logger.info(f"[INFO] Город найден: {city_name} -> Координаты: {lat}, {lon}")
            return lat, lon
        else:

            return None
    except Exception as e:
        logger.error(f"[ERROR] Ошибка определения координат города {city_name}: {e}")
        return None

# Функция расчета стоимости доставки
def calculate_delivery_cost(location):
    """Рассчитывает стоимость доставки автомобиля в Вроцлав."""

    coords = get_city_coordinates(location)
    if not coords:
        logger.warning(f"[WARNING] Не удалось определить координаты города {location}")
        return "N/A", 0.0

    distance = geodesic(WROCLAW_COORDS, coords).km

    # Топливо на путь туда-обратно:
    fuel_needed = (distance / 100) * FUEL_CONSUMPTION_PER_100KM
    total_fuel = fuel_needed + (fuel_needed / 2)  # В обратную сторону едут 2 машины

    # Общая стоимость топлива
    delivery_cost = total_fuel * FUEL_PRICE_PER_LITER
    delivery_info = f"{int(distance)} км - {int(delivery_cost)} PLN"

    logger.info(f"[INFO] Доставка из {location}: {delivery_info}")  # Лог доставки
    return delivery_info, delivery_cost

# Функция анализа состояния авто
def analyze_listing(listing):
    """Анализ состояния авто с использованием NLP"""
    if not classifier:
        return listing  # Если модель не загружена, просто возвращаем оригинал

    try:
        categories = ["новый", "б/у", "аварийный", "с пробегом", "без пробега"]
        result = classifier(listing['title'], candidate_labels=categories)
        listing['category'] = result['labels'][0]
        listing['category_score'] = result['scores'][0]
    except Exception as e:
        logger.error(f"[ERROR] Ошибка анализа объявления: {e}")
        listing['category'] = 'unknown'
        listing['category_score'] = 0.0

    return listing

# Автозагрузка модели при импорте
load_model()
