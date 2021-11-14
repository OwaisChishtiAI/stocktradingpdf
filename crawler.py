from selenium import webdriver
from bs4 import BeautifulSoup
import time
import os
import pandas as pd
import pickle
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from lxml import etree
from datetime import datetime
import PyPDF2
from config import Config

class Crawler:
    def __init__(self):
        self.data = {"axs_code" : [], "headline" : [], "date_published" : [], "link_to_pdf" : [], "positive_count" : [], "negative_count" : [], "positive_words" : [], "negative_words" : []}
        self.temp_links = []
        self.pdf_link = "https://www.asx.com.au"

    def log(self, info):
        with open("logs.txt", "a", encoding='utf8', errors='ignore')as f:
            f.write(str(datetime.now()) + ": " + info)
            f.write("\n")

    def cleaner(self):
        for key in self.data.keys():
            self.data[key] = []

    def run(self):
        options = webdriver.ChromeOptions()
        options.add_argument(Config.HEADLESS)
        driver = webdriver.Chrome(Config.CHROME_EXTENSION_PATH, options=options)
        driver.get(Config.TODAY_ANNOUNCEMENTS)
        self.log("Chrome Started for main page.")
        soup = BeautifulSoup(driver.page_source,'html.parser')
        items = soup.findAll('tr')
        if self.data['axs_code']:
            self.log("Data cleaned ForceFully: " + str(len(self.data['axs_code'])))
            self.cleaner()
        if items:
            for item in range(len(items)):
                i = 0
                if items[item]:
                    for each in items[item].findAll('td'):
                        if i == 0:
                            self.data['axs_code'].append(each.text.replace("\n", "").replace("\t", ""))
                        elif i == 1:
                            self.data['date_published'].append(each.text.replace("\n", "").replace("\t", ""))
                        elif i == 3:
                            self.data['headline'].append(each.find('a').text.replace("\n", "").replace("\t", ""))
                            self.temp_links.append(each.find('a').get('href'))
                        i+=1
            driver.close()
            return True
        else:
            self.log("No Items Found.")
            return False

    def download_pdf(self):
        if self.temp_links:
            for each in self.temp_links:
                options = webdriver.ChromeOptions()
                options.add_argument(Config.HEADLESS)
                driver = webdriver.Chrome(Config.CHROME_EXTENSION_PATH, options=options)
                driver.get(self.pdf_link + each.replace("amp;")) #1
                link = driver.find_element_by_xpath("//input[@name='pdfURL']")
                link = link.get_attribute('value') #2
                driver.close()

                options = webdriver.ChromeOptions()
                options.add_argument(Config.HEADLESS)
                options.add_experimental_option('prefs', Config.EXPERIMENTAL_OPTIONS)
                driver = webdriver.Chrome(Config.CHROME_EXTENSION_PATH, options=options)
                self.log("Chrome Started for pdfs.")
                driver.get(link)
            return True
        else:
            return False

    def extract_pdf(self):
        files = os.listdir(Config.EXPERIMENTAL_OPTIONS['download.default_directory'])
        if files:
            for file in files:
                if file.endswith(".pdf"):
                    file = open(os.path.join(Config.EXPERIMENTAL_OPTIONS['download.default_directory'], file), 'rb')
                    fileReader = PyPDF2.PdfFileReader(file)
                    text = ""
                    for i in range(fileReader.numPages):
                        pageObj = fileReader.getPage(i)
                        text += pageObj.extractText()
                    positive_words_count = 0
                    positive_words = []
                    for positive_word in Config.POSITIVE_WORDS_LIST:
                        if positive_word in text:
                            positive_words_count += 1
                            positive_words.append(positive_word)
                    self.data["positive_words"].append(positive_words)
                    self.data['positive_count'].append(positive_words_count)
                    os.remove(os.path.join(Config.EXPERIMENTAL_OPTIONS['download.default_directory'], file))
            return True
        else:
            return False

    def save_results(self):
        df = pd.DataFrame(self.data)
        df.to_csv("results.csv")
        self.cleaner()