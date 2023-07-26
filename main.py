from openpyxl import load_workbook
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from googletrans import Translator
from re import search
from datetime import datetime

from config.colors import *
from config.columns import *
from config.config import *
from config.rich import *
from config.sizes import *
from config.table_of_sizes import *
from config.materials import *

from random import random
import shutil
import requests
import os
import logging
import time
import sys
import traceback
import argparse


class Parser:
    def __init__(self):
        self.result = []
        parser = argparse.ArgumentParser(description='Process some integers.')
        parser.add_argument('--headless', action='store_true', help='headless')
        args = parser.parse_args()
        if args.headless:
            self.driver = self.get_driver(True)
        else:
            self.driver = self.get_driver(False)

    def get_driver(self, headless):
        try:
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')

            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            options.add_argument(
                "user-agent=Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0")

            # options.add_argument('--disable-dev-shm-usage')
            # options.add_argument('--no-sandbox')

            driver = webdriver.Chrome(
                service=Service('chromedriver.exe'),
                options=options
            )
            driver.set_window_size(1920, 1080)
            driver.implicitly_wait(30)

            self.wait = WebDriverWait(driver, 30)

            return driver
        except Exception as e:
            print('Неудачная настройка браузера!')
            print(traceback.format_exc())
            print(input('Нажмите ENTER, чтобы закрыть эту программу'))
            sys.exit()

    def get_all_products(self):
        products = []
        blocks = self.driver.find_elements(By.CLASS_NAME, 'item-link')
        for block in blocks:
            product_url = block.get_attribute('href')
            if product_url != 'https://www2.hm.com/pl_pl/index.html':
                products.append(product_url)
        products = self.delete_duplicate(products)
        return products

    def parse(self):
        c = 0
        self.driver.get(CATEGORIE)

        products = self.get_all_products()
        for product_url in products[:PARSE_LIMIT]:
            print(f'{products.index(product_url) + 1} of {len(products[:PARSE_LIMIT])}')
            try:
                self.driver.get(product_url)
            except:
                continue

            self.driver.execute_script("window.scrollTo(0, 1000)")

            description_btn = self.driver.find_element(By.ID, 'toggle-descriptionAccordion')
            description_btn.click()
            description = self.translate(self.driver.find_element(By.CLASS_NAME, 'd1cd7b.b475fe.e2b79d').text).strip()

            try:
                material_btn = self.driver.find_element(By.ID, 'toggle-materialsAndSuppliersAccordion')
                material_btn.click()
                self.wait.until(EC.visibility_of_element_located((By.CLASS_NAME, 'd1cd7b.a09145.efef57')))
                material = self.driver.find_element(By.CLASS_NAME, 'd1cd7b.a09145.efef57').text
            except Exception:
                material = 'Bad material'

            try:
                creator_btn = self.driver.find_element(By.XPATH, '//button[@class="f05bd4 cf896c c63d19 aaa2a2 d28f9c"]')
                creator_btn.click()
                time.sleep(TIMEOUT)

                self.wait.until(EC.visibility_of_element_located((By.XPATH, '//h2[@class="fa226d ca21a4"]')))
                creator = self.translate(self.driver.find_element(By.XPATH, '//h2[@class="fa226d ca21a4"]').text)
                if creator == 'Инди': creator = 'Индия'
                close = self.driver.find_element(By.XPATH, '//div[@class="f10030"]/button')
                close.click()
                time.sleep(TIMEOUT)
            except:
                creator = 'Bad creator'

            name = self.translate(self.driver.find_element(By.ID, 'js-product-name').text).strip()

            price = self.driver.find_element(By.ID, 'product-price').text.replace(' PLN', '').replace(',', '.')

            if len(price.split('\n')) > 1: price = price.split('\n')[1]

            colors = [j.get_attribute('href') for j in self.driver.find_elements(By.XPATH, '//li[@class="list-item"]/a')]
            # if len(colors) >= 8: colors = colors[:7]
            if PARSE_TYPE == 'bags':
                if material != 'Bad material' and material != 'N/A 100%' and material.split(' ')[0].lower() != '':
                    material = MATERIALS[material.split(' ')[0]]
                else:
                    material = ''
                for j in colors:
                    try:
                        self.driver.get(j)
                    except Exception:
                        continue
                    time.sleep(TIMEOUT)

                    article_num = search('[0-9]{5,}', self.driver.current_url)[0]

                    self.wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="product-detail-main-image-container"]/img')))
                    main_photo_url = self.driver.find_element(By.XPATH, '//div[@class="product-detail-main-image-container"]/img').get_attribute('src')
                    main_photo = self.get_photo(main_photo_url, str(article_num) + '_0.jpeg')

                    other_photo_urls = self.driver.find_elements(By.XPATH, '//figure[@class="pdp-secondary-image pdp-image"]/img')
                    other_photo = ','.join([self.get_photo('https:' + other_photo_urls[i].get_attribute('src'), article_num + '_' + str(i + 1) + '.webp') for i in range(len(other_photo_urls))])

                    c += 1

                    color = self.driver.find_element(By.CLASS_NAME, 'product-input-label').text

                    article = 'H&M_' + article_num

                    rich = RICH.format(name, description, article_num)

                    COLUMNS['№'] = c
                    COLUMNS['Артикул*'] = article
                    COLUMNS['Название товара'] = name
                    COLUMNS['Цена, руб.*'] = self.get_price(price)
                    COLUMNS['Ссылка на главное фото*'] = main_photo
                    COLUMNS['Ссылки на дополнительные фото'] = other_photo
                    COLUMNS['Название модели (для объединения в одну карточку)*'] = article_num[:-3]
                    COLUMNS['Цвет товара'] = COLORS[color] if color in COLORS else 'разноцветный'
                    COLUMNS['Название цвета'] = self.translate(color)
                    COLUMNS['Страна-изготовитель'] = creator
                    COLUMNS['Материал'] = material
                    COLUMNS['Таблица размеров JSON'] = TABLE_OF_SIZES
                    COLUMNS['Rich-контент JSON'] = rich

                    self.result.append(COLUMNS.copy())
            elif PARSE_TYPE == 'clothes':
                for j in colors:
                    try:
                        self.driver.get(j)
                    except Exception:
                        continue
                    time.sleep(TIMEOUT)

                    article_num = search('[0-9]{5,}', self.driver.current_url)[0]

                    self.wait.until(EC.visibility_of_element_located(
                        (By.XPATH, '//div[@class="product-detail-main-image-container"]/img')))
                    main_photo_url = self.driver.find_element(By.XPATH,
                                                              '//div[@class="product-detail-main-image-container"]/img').get_attribute(
                        'src')
                    main_photo = self.get_photo(main_photo_url, str(article_num) + '_0.jpeg')

                    other_photo_urls = self.driver.find_elements(By.XPATH,
                                                                 '//figure[@class="pdp-secondary-image pdp-image"]/img')
                    other_photo = ','.join([self.get_photo('https:' + other_photo_urls[i].get_attribute('src'),
                                                           article_num + '_' + str(i + 1) + '.webp') for i in
                                            range(len(other_photo_urls))])

                    sizes = self.driver.find_elements(By.XPATH, '//hm-size-selector/ul/li')
                    for i in sizes:
                        c += 1

                        color = self.driver.find_element(By.CLASS_NAME, 'product-input-label').text

                        size = i.text.split('\n')[0]

                        article = 'H&M_' + article_num + '_' + size

                        rich = RICH.format(name, description, article_num)

                        COLUMNS['№'] = c
                        COLUMNS['Артикул*'] = article
                        COLUMNS['Название товара'] = name
                        COLUMNS['Цена, руб.*'] = self.get_price(price)
                        COLUMNS['Ссылка на главное фото*'] = main_photo
                        COLUMNS['Ссылки на дополнительные фото'] = other_photo
                        COLUMNS['Объединить на одной карточке*'] = article_num[:-3]
                        COLUMNS['Цвет товара*'] = COLORS[color] if color in COLORS else 'разноцветный'
                        if size.isdigit():
                            COLUMNS['Российский размер*'] = str(int(size) + 6)
                        else:
                            try:
                                COLUMNS['Российский размер*'] = SIZES[size.upper()]
                            except:
                                COLUMNS['Российский размер*'] = 'Bad size'  # Если размера нету в таблице размеров
                        COLUMNS['Размер производителя'] = size
                        COLUMNS['Название цвета'] = self.translate(color)
                        COLUMNS['Страна-изготовитель'] = creator
                        COLUMNS['Состав материала'] = self.translate(material)
                        COLUMNS['Таблица размеров JSON'] = TABLE_OF_SIZES
                        COLUMNS['Rich-контент JSON'] = rich

                        self.result.append(COLUMNS.copy())
            elif PARSE_TYPE == 'shoes':
                material = self.driver.find_element(By.XPATH, '//ul[@class="f94b22"]').text
                main_material, internal_material, sole_material = '', '', ''
                for i in material.split('\n'):
                    key, value = i.split(':')
                    if key == 'Strona wierzchnia':
                        main_material = MATERIALS[value.split(' ')[0]]
                    elif key == 'Podszewka':
                        internal_material = MATERIALS[value.split(' ')[0]]
                    elif key == 'Podeszwa zewnętrzna':
                        sole_material = MATERIALS[value.split(' ')[0]]
                for j in colors:
                    try:
                        self.driver.get(j)
                    except Exception:
                        continue
                    time.sleep(TIMEOUT)

                    article_num = search('[0-9]{5,}', self.driver.current_url)[0]

                    self.wait.until(EC.visibility_of_element_located(
                        (By.XPATH, '//div[@class="product-detail-main-image-container"]/img')))
                    main_photo_url = self.driver.find_element(By.XPATH,
                                                              '//div[@class="product-detail-main-image-container"]/img').get_attribute(
                        'src')
                    main_photo = self.get_photo(main_photo_url, str(article_num) + '_0.jpeg')

                    other_photo_urls = self.driver.find_elements(By.XPATH,
                                                                 '//figure[@class="pdp-secondary-image pdp-image"]/img')
                    other_photo = ','.join([self.get_photo('https:' + other_photo_urls[i].get_attribute('src'),
                                                           article_num + '_' + str(i + 1) + '.webp') for i in
                                            range(len(other_photo_urls))])

                    sizes = self.driver.find_elements(By.XPATH, '//hm-size-selector/ul/li')
                    for i in sizes:
                        c += 1

                        color = self.driver.find_element(By.CLASS_NAME, 'product-input-label').text

                        size = i.text.split('\n')[0]

                        article = 'H&M_' + article_num + '_' + size

                        rich = RICH.format(name, description, article_num)

                        COLUMNS['№'] = c
                        COLUMNS['Артикул*'] = article
                        COLUMNS['Название товара'] = name
                        COLUMNS['Цена, руб.*'] = self.get_price(price)
                        COLUMNS['Ссылка на главное фото*'] = main_photo
                        COLUMNS['Ссылки на дополнительные фото'] = other_photo
                        COLUMNS['Объединить на одной карточке*'] = article_num[:-3]
                        COLUMNS['Цвет товара*'] = COLORS[color] if color in COLORS else 'разноцветный'
                        try:
                            COLUMNS['Российский размер (обуви)*'] = SIZES[size.upper()]
                        except:
                            COLUMNS['Российский размер (обуви)*'] = 'Bad size'  # Если размера нету в таблице размеров
                        COLUMNS['Размер производителя'] = size
                        COLUMNS['Название цвета'] = self.translate(color)
                        COLUMNS['Страна-изготовитель'] = creator
                        COLUMNS['Материал'] = main_material
                        COLUMNS['Внутренний материал'] = internal_material
                        COLUMNS['Материал подошвы'] = sole_material
                        COLUMNS['Таблица размеров JSON'] = TABLE_OF_SIZES
                        COLUMNS['Rich-контент JSON'] = rich

                        self.result.append(COLUMNS.copy())


    def check_exists_by_xpath(self, xpath):
        try:
            self.driver.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return False
        return True

    def get_photo(self, url, name):
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(SAVE_PHOTO_PATH + name, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            return 'http://' + HOST + '/H-M_parser/' + SAVE_PHOTO_PATH + name
        else:
            return 'Bad photo'

    def delete_duplicate(self, urls):
        result = []
        set_of_articles = set()
        for url in urls:
            article = search(r'[0-9]{5,}', url)[0][:-3]
            if article not in set_of_articles:
                set_of_articles.add(article)
                result.append(url)
        return result

    def translate(self, text):
        translator = Translator()
        while True:
            try:
                result = translator.translate(text, dest='ru')
                return result.text
            except:
                pass

    def gPriceDict(self, key):
        return float(PRICE_TABLE[key])

    def get_price(self, pln_price):
        cost_price = ((float(pln_price) / self.gPriceDict("КУРС_USD_ЗЛОТЫ")) * self.gPriceDict("КОЭФ_КОНВЕРТАЦИИ") * self.gPriceDict(
            'КУРС_USD_RUB')) + (self.gPriceDict('ЦЕНА_ДОСТАВКИ_В_КАТЕГОРИИ') * self.gPriceDict('КУРС_БЕЛ.РУБ_РУБ') * self.gPriceDict(
            'КУРС_EUR_БЕЛ.РУБ'))
        final_price = ((cost_price + self.gPriceDict('СРЕД_ЦЕН_ДОСТАВКИ')) * self.gPriceDict('НАЦЕНКА')) / (
                    1 - self.gPriceDict('ПРОЦЕНТЫ_ОЗОН') - self.gPriceDict('ПРОЦЕНТЫ_НАЛОГ') - self.gPriceDict('ПРОЦЕНТЫ_ЭКВАЙРИНГ'))

        if final_price > 20000:
            final_price = (final_price // 1000 + 1) * 1000 - 1
        elif final_price > 10000:
            if final_price % 1000 >= 500:
                final_price = (final_price // 1000) * 1000 + 999
            else:
                final_price = (final_price // 1000) * 1000 + 499
        else:
            final_price = (final_price // 100 + 1) * 100 - 1
        return final_price

    def save(self, result):
        wb = load_workbook(filename=f'templates/{TEMPLATE_NAME}')
        ws = wb['Шаблон для поставщика']
        alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        cols = []
        for col in alphabet:
            value = ws[col + '2'].value
            if value:
                cols.append(value)
        for col1 in alphabet:
            for col2 in alphabet:
                value = ws[col1 + col2 + '2'].value
                if value:
                    cols.append(value)

        for row in range(len(result)):
            for col in range(len(cols)):
                if cols[col] not in result[row]:
                    ws.cell(row=4 + row, column=1 + col).value = ''
                else:
                    ws.cell(row=4 + row, column=1 + col).value = result[row][cols[col]]

        wb.save(SAVE_XLSX_PATH + f"{datetime.now()}.xlsx".replace(':', '.'))

    def start(self):
        try:
            print('--- START PARSING ---')
            self.parse()
            self.save(self.result)
            print('--- END PARSING ---')
        except Exception as e:
            self.save(self.result)
            error = self.driver.current_url + '\n' + traceback.format_exc() + '\n'
            print(error)
            with open('log.log', 'a') as f:
                f.write(error)
        finally:
            self.driver.close()
            self.driver.quit()


def main():
    parser = Parser()
    parser.start()


if __name__ == '__main__':
    if 'photo' not in os.listdir():
        os.mkdir('photo')
    if 'xlsx' not in os.listdir():
        os.mkdir('xlsx')
    if 'log.log' not in os.listdir():
        file = open('log.log', 'w')
        file.close()
    main()

