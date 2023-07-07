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
from config import *
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
    def __init__(self, choice):
        self.result = []
        self.choice = choice
        self.categorie = CATEGORIES[choice]
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
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            driver.set_window_size(1920, 1080)
            driver.implicitly_wait(60)

            self.wait = WebDriverWait(driver, 60)

            return driver
        except Exception as e:
            print('Неудачная настройка браузера!')
            print(traceback.format_exc())
            print(input('Нажмите ENTER, чтобы закрыть эту программу'))
            sys.exit()

    def parse_dresses(self):
        products = []
        c = 0
        self.driver.get(self.categorie)

        """# scroll page
        while self.check_exists_by_xpath('//button[@class="button js-load-more "]'):
            while True:
                scroll_height = 2000
                document_height_before = self.driver.execute_script("return document.documentElement.scrollHeight")
                self.driver.execute_script(f"window.scrollTo(0, {document_height_before + scroll_height});")
                time.sleep(1.5)
                document_height_after = self.driver.execute_script("return document.documentElement.scrollHeight")
                if document_height_after == document_height_before:
                    self.driver.execute_script(f"window.scrollTo(0, {document_height_before - scroll_height});")
                    break
            self.driver.find_element(By.XPATH, '//button[@class="button js-load-more "]').click()
            time.sleep(TIMEOUT)"""

        blocks = self.driver.find_elements(By.CLASS_NAME, 'item-link')
        for block in blocks:
            product_url = block.get_attribute('href')
            if product_url != 'https://www2.hm.com/pl_pl/index.html':
                products.append(product_url)
        products = self.delete_duplicate(products)
        for product_url in products[:200]:
            print(f'{products.index(product_url) + 1} of {len(products)}')
            self.driver.get(product_url)

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

            if self.check_exists_by_xpath('//button[@class="f05bd4 cf896c c63d19 aaa2a2 d28f9c"]'):
                creator_btn = self.driver.find_element(By.XPATH, '//button[@class="f05bd4 cf896c c63d19 aaa2a2 d28f9c"]')
                creator_btn.click()
                time.sleep(TIMEOUT)

                self.wait.until(EC.visibility_of_element_located((By.XPATH, '//h2[@class="fa226d ca21a4"]')))
                creator = self.translate(self.driver.find_element(By.XPATH, '//h2[@class="fa226d ca21a4"]').text)
                if creator == 'Инди':
                    creator = 'Индия'
                close = self.driver.find_element(By.XPATH, '//div[@class="f10030"]/button')
                close.click()
                time.sleep(TIMEOUT)
            else:
                creator = 'Bad creator'

            name = self.translate(self.driver.find_element(By.ID, 'js-product-name').text).strip()

            price = self.driver.find_element(By.ID, 'product-price').text.replace(' PLN', '')

            colors = [j.get_attribute('href') for j in self.driver.find_elements(By.XPATH, '//li[@class="list-item"]/a')]
            if len(colors) >= 8: colors = colors[:7]
            for j in colors:
                self.driver.get(j)
                time.sleep(TIMEOUT)

                article_num = search('[0-9]{5,}', self.driver.current_url)[0]

                sizes = self.driver.find_elements(By.CLASS_NAME, 'ListGrid-module--item__lHoHF')

                self.wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="product-detail-main-image-container"]/img')))
                main_photo_url = self.driver.find_element(By.XPATH, '//div[@class="product-detail-main-image-container"]/img').get_attribute('src')
                main_photo = self.get_photo(main_photo_url, str(article_num) + '_0.jpeg')

                other_photo_urls = self.driver.find_elements(By.XPATH, '//figure[@class="pdp-secondary-image pdp-image"]/img')
                other_photo = ','.join([self.get_photo('https:' + other_photo_urls[i].get_attribute('src'), article_num + '_' + str(i + 1) + '.webp') for i in range(len(other_photo_urls))])

                for i in sizes:
                    c += 1

                    color = self.driver.find_element(By.CLASS_NAME, 'product-input-label').text

                    size = i.text.split('\n')[0]

                    article = 'H&M_' + article_num + '_' + size

                    rich = RICH.format(name, description, article_num)

                    DRESS_COLUMNS['№'] = c
                    DRESS_COLUMNS['Артикул*'] = article
                    DRESS_COLUMNS['Название товара'] = name
                    DRESS_COLUMNS['Цена, руб.*'] = price
                    DRESS_COLUMNS['Ссылка на главное фото*'] = main_photo
                    DRESS_COLUMNS['Ссылки на дополнительные фото'] = other_photo
                    DRESS_COLUMNS['Объединить на одной карточке*'] = article_num[:-3]
                    DRESS_COLUMNS['Цвет товара*'] = COLORS[color] if color in COLORS else 'разноцветный'
                    if size.isdigit():
                        DRESS_COLUMNS['Российский размер*'] = str(int(size) + 6)
                    else:
                        try:
                            DRESS_COLUMNS['Российский размер*'] = DRESS_SIZES[size.upper()]
                        except:
                            DRESS_COLUMNS['Российский размер*'] = 'Bad size'
                    DRESS_COLUMNS['Размер производителя'] = size
                    DRESS_COLUMNS['Название цвета'] = self.translate(color)
                    DRESS_COLUMNS['Страна-изготовитель'] = creator
                    DRESS_COLUMNS['Состав материала'] = self.translate(material)
                    DRESS_COLUMNS['Таблица размеров JSON'] = TABLE_OF_SIZES
                    DRESS_COLUMNS['Rich-контент JSON'] = rich

                    self.result.append(DRESS_COLUMNS)

    def parse_jeans(self):
        products = []
        c = 0
        self.driver.get(self.categorie)

        """# scroll page
        while self.check_exists_by_xpath('//button[@class="button js-load-more "]'):
            while True:
                scroll_height = 2000
                document_height_before = self.driver.execute_script("return document.documentElement.scrollHeight")
                self.driver.execute_script(f"window.scrollTo(0, {document_height_before + scroll_height});")
                time.sleep(1.5)
                document_height_after = self.driver.execute_script("return document.documentElement.scrollHeight")
                if document_height_after == document_height_before:
                    self.driver.execute_script(f"window.scrollTo(0, {document_height_before - scroll_height});")
                    break
            self.driver.find_element(By.XPATH, '//button[@class="button js-load-more "]').click()
            time.sleep(TIMEOUT)"""

        blocks = self.driver.find_elements(By.CLASS_NAME, 'item-link')
        for block in blocks:
            product_url = block.get_attribute('href')
            if product_url != 'https://www2.hm.com/pl_pl/index.html':
                products.append(product_url)
        products = self.delete_duplicate(products)
        for product_url in products[:200]:
            print(f'{products.index(product_url) + 1} of {len(products)}')
            self.driver.get(product_url)

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

            if self.check_exists_by_xpath('//button[@class="f05bd4 cf896c c63d19 aaa2a2 d28f9c"]'):
                creator_btn = self.driver.find_element(By.XPATH,
                                                       '//button[@class="f05bd4 cf896c c63d19 aaa2a2 d28f9c"]')
                creator_btn.click()
                time.sleep(TIMEOUT)

                self.wait.until(EC.visibility_of_element_located((By.XPATH, '//h2[@class="fa226d ca21a4"]')))
                creator = self.translate(self.driver.find_element(By.XPATH, '//h2[@class="fa226d ca21a4"]').text)
                if creator == 'Инди':
                    creator = 'Индия'
                close = self.driver.find_element(By.XPATH, '//div[@class="f10030"]/button')
                close.click()
                time.sleep(TIMEOUT)
            else:
                creator = 'Bad creator'

            name = self.translate(self.driver.find_element(By.ID, 'js-product-name').text).strip()

            price = self.driver.find_element(By.ID, 'product-price').text.replace(' PLN', '')

            colors = [j.get_attribute('href') for j in
                      self.driver.find_elements(By.XPATH, '//li[@class="list-item"]/a')]
            if len(colors) >= 8: colors = colors[:7]
            for j in colors:
                self.driver.get(j)
                time.sleep(TIMEOUT)

                article_num = search('[0-9]{5,}', self.driver.current_url)[0]

                sizes = self.driver.find_elements(By.CLASS_NAME, 'ListGrid-module--item__lHoHF')

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

                for i in sizes:
                    c += 1

                    color = self.driver.find_element(By.CLASS_NAME, 'product-input-label').text

                    size = i.text.split('\n')[0]

                    article = 'H&M_' + article_num + '_' + size

                    rich = RICH.format(name, description, article_num)

                    DRESS_COLUMNS['№'] = c
                    DRESS_COLUMNS['Артикул*'] = article
                    DRESS_COLUMNS['Название товара'] = name
                    DRESS_COLUMNS['Цена, руб.*'] = price
                    DRESS_COLUMNS['Ссылка на главное фото*'] = main_photo
                    DRESS_COLUMNS['Ссылки на дополнительные фото'] = other_photo
                    DRESS_COLUMNS['Объединить на одной карточке*'] = article_num[:-3]
                    DRESS_COLUMNS['Цвет товара*'] = COLORS[color] if color in COLORS else 'разноцветный'
                    if size.isdigit():
                        DRESS_COLUMNS['Российский размер*'] = str(int(size) + 6)
                    else:
                        try:
                            DRESS_COLUMNS['Российский размер*'] = DRESS_SIZES[size.upper()]
                        except:
                            DRESS_COLUMNS['Российский размер*'] = 'Bad size'
                    DRESS_COLUMNS['Размер производителя'] = size
                    DRESS_COLUMNS['Название цвета'] = self.translate(color)
                    DRESS_COLUMNS['Страна-изготовитель'] = creator
                    DRESS_COLUMNS['Состав материала'] = self.translate(material)
                    DRESS_COLUMNS['Таблица размеров JSON'] = TABLE_OF_SIZES
                    DRESS_COLUMNS['Rich-контент JSON'] = rich

                    self.result.append(DRESS_COLUMNS)

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

    def save(self, result, name):
        wb = load_workbook(filename=f'examples/{name}_example.xlsx')
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

        wb.save(SAVE_XLSX_PATH + f"{name}_{datetime.now()}.xlsx")

    def start(self):
        try:
            print('--- START PARSING ---')
            if self.choice == 0:
                self.parse_dresses()
                self.save(self.result, 'dresses')
            elif self.choice == 1:
                self.parse_dresses()
                self.save(self.result, 'baby_dresses')
            elif self.choice == 2:
                self.parse_dresses()
                self.save(self.result, "men's_jeans")
            print('--- END PARSING ---')
        except Exception as e:
            print(self.driver.current_url)
            print(traceback.format_exc())
            logging.error("ERROR")
            html = self.driver.page_source
            with open('last_page.html', 'w') as f:
                data = f.write(html)
            self.save(self.result, 'dresses_' + str(len(self.result)))
        finally:
            self.driver.close()
            self.driver.quit()


def main(choice):
    parser = Parser(choice)
    parser.start()


if __name__ == '__main__':
    if 'photo' not in os.listdir():
        os.mkdir('photo')
    if 'xlsx' not in os.listdir():
        os.mkdir('xlsx')
    print('Выберите категорию для парсинга:\n0 - платья\n1 - детские платья\n2 - мужские джинсы')
    choice = int(input())
    main(choice)
