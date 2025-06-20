# selenium_driver_setup.py

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import time
import pickle
import os

def get_driver(headless=True):
    """
    Возвращает объект WebDriver для Chrome.
    По умолчанию headless=True, чтобы при запуске
    браузер не был виден.
    """
    chrome_options = Options()
    if headless:
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')

    # Доп. аргументы для стабильности
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    # Если вы не хотите, чтобы окно появлялось даже на долю секунды,
    # не используйте driver.maximize_window() или driver.set_window_size().
    return driver

FB_EMAIL = "scandinavians502@gmail.com"
FB_PASSWORD = "Vbnm921009"
COOKIES_PATH = "fb_cookies.pkl"

def get_facebook_driver(headless=True):
    """
    Запускает браузер Chrome с обходом антибот-защиты для Facebook.
    """
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")  # Новый headless-режим

    driver = uc.Chrome(options=options)
    driver.get("https://www.facebook.com/")

    # Загружаем cookies, если они есть
    if os.path.exists(COOKIES_PATH):
        with open(COOKIES_PATH, "rb") as f:
            cookies = pickle.load(f)
            for cookie in cookies:
                driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(5)
    else:
        # Авторизуемся вручную
        driver.find_element("name", "email").send_keys(FB_EMAIL)
        driver.find_element("name", "pass").send_keys(FB_PASSWORD)
        driver.find_element("name", "login").click()
        time.sleep(10)

        # Сохраняем cookies после авторизации
        with open(COOKIES_PATH, "wb") as f:
            pickle.dump(driver.get_cookies(), f)

    return driver