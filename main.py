from openpyxl import load_workbook
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from googletrans import Translator
from re import search
from datetime import datetime
from config import *
from random import random
import time
import sys
import traceback


class Parser():
    def __init__(self):
        self.driver = self.get_driver()

    def get_driver(self, headless=False):
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

            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            driver.set_window_size(1920, 1080)
            driver.implicitly_wait(10)
            return driver
        except Exception as e:
            print('Неудачная настройка браузера!')
            print(traceback.format_exc())
            print(input('Нажмите ENTER, чтобы закрыть эту программу'))
            sys.exit()

    def parse(self, categories):
        result = []
        products = []
        c = 0
        for categorie in categories:
            self.driver.get(categorie)
            blocks = self.driver.find_elements(By.CLASS_NAME, 'item-link')
            for block in blocks[:3]:
                product_url = block.get_attribute('href')
                products.append(product_url)
        for product_url in products:
            print(f'{products.index(product_url) + 1} of {len(products)}')
            self.driver.get(product_url)

            self.driver.execute_script("window.scrollTo(0, 1100)")

            material_btn = self.driver.find_element(By.ID, 'toggle-materialsAndSuppliersAccordion')
            material_btn.click()
            time.sleep(TIMEOUT)
            material = self.driver.find_element(By.CLASS_NAME, 'd1cd7b.a09145.efef57').text

            creator_btn = self.driver.find_element(By.CLASS_NAME, 'f05bd4.cf896c.c63d19.aaa2a2.d28f9c')
            creator_btn.click()
            time.sleep(TIMEOUT)
            creator = self.driver.find_element(By.XPATH, '//h2[@class="fa226d ca21a4"]').text
            close = self.driver.find_element(By.CLASS_NAME, 'b395d2.fe373a.dfc6c7.ee87dd')
            close.click()
            time.sleep(TIMEOUT)

            description_btn = self.driver.find_element(By.ID, 'toggle-descriptionAccordion')
            description_btn.click()
            description = self.translate(self.driver.find_element(By.CLASS_NAME, 'd1cd7b.b475fe.e2b79d').text).strip()

            name = self.translate(self.driver.find_element(By.ID, 'js-product-name').text).strip()
            price = self.driver.find_element(By.ID, 'product-price').text.replace(' PLN', '')

            colors = self.driver.find_elements(By.XPATH, '//li[@class="list-item"]/a')
            for j in colors:
                j.click()
                time.sleep(TIMEOUT)
                sizes = self.driver.find_elements(By.CLASS_NAME, 'ListGrid-module--item__lHoHF')
                for i in sizes:
                    c += 1

                    color = self.driver.find_element(By.CLASS_NAME, 'product-input-label').text
                    size = i.text.split('\n')[0]

                    article_num = self.driver.find_element(By.CLASS_NAME, 'd1cd7b.b7f566.a0f363').text
                    article = 'H&M_' + article_num + '_' + size

                    rich = RICH.format(name, description, article_num)

                    result.append([c, article, name, price, '', 'Не облагается', '', 'Платье, сарафан женские',
                                   '', '500', '200', '50', '200', 'main_photo_url', 'other_photos', '', '', 'H&M',
                                   article_num[:-3], COLORS[color] if color in COLORS else 'разноцветный',
                                   str(int(size) + 6) if size.isdigit() else SIZES[size.upper()], size, self.translate(color), 'Платье', 'Женский',
                                   'платье;платье женское летнее;платье женское;сарафан женский;платье женское праздничное;платье вечернее;платье zara;zara;короткое платье;длинное платье;джинсовое платье;вязаное платье',
                                   'Взрослая', 'На любой сезон', '175 см', '', '44', 'Базовая коллекция', self.translate(creator),
                                   '', '', 'Машинная стирка при температуре до 30ºC с коротким циклом отжима.Отбеливание запрещено.Гладить при температуре до 110ºC .Химчистка с тетрахлорэтиленом.Не использовать машинную сушку',
                                   '', '', self.translate(material), '', '', '', '', '', 'Повседневный;праздничный;вечерний', '',
                                   '', '', '', '', '', '', '', '', '', 'Пакет', '1', '', '', '', '', '', TABLE_OF_SIZES,
                                   rich, '', '', '', '', '', '', '', '', '', '', '', '', '', 'Нет'])
        return result

    def translate(self, text):
        translator = Translator()
        result = translator.translate(text, dest='ru')
        return result.text

    def save(self, result):
        wb = load_workbook(filename='example.xlsx')
        ws = wb['Шаблон для поставщика']
        for row in range(len(result)):
            for col in range(len(result[row])):
                ws.cell(row=4 + row, column=1 + col).value = result[row][col]

        wb.save("h&m_test.xlsx")

    def start(self):
        try:
            print('--- START PARSING ---')
            result = self.parse(CATEGORIES)
            self.save(result)
            print('--- END PARSING ---')
        except Exception:
            print(self.driver.current_url)
            print(traceback.format_exc())
        finally:
            self.driver.close()
            self.driver.quit()


def main():
    parser = Parser()
    parser.start()


if __name__ == '__main__':
    main()
