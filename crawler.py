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
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from lxml import etree
from datetime import datetime
import PyPDF2
from config import Config
#import tika
#tika.initVM()
#time.sleep(1)
from tika import parser

class Crawler:
    def __init__(self):
        self.data = {"axs_code" : [], "headline" : [], "date_published" : [], "link_to_pdf" : [], "total_word_count" : [], "positive_count" : [], "negative_count" : [], "positive_words" : [], "negative_words" : []}
        self.temp_links = []
        self.pdf_link = "https://www.asx.com.au"

    def log(self, info):
        with open("logs.txt", "a", encoding='utf8', errors='ignore')as f:
            f.write(str(datetime.now()) + ": " + info)
            f.write("\n")

    def cleaner(self):
        for key in self.data.keys():
            self.data[key] = []
        self.temp_links = []

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
            for item in range(15):#len(items)
                i = 0
                if items[item]:
                    for each in items[item].findAll('td'):
                        if i == 0:
                            self.data['axs_code'].append(each.text.replace("\n", "").replace("\t", ""))
                        elif i == 1:
                            timestamp = each.text.replace("\n", "").replace("\t", "")
                            timestamp = timestamp.split('2021')
                            timestamp[0] = timestamp[0]+'2021'
                            timestamp = " ".join(timestamp)
                            self.data['date_published'].append(timestamp)
                        elif i == 3:
                            self.data['headline'].append(each.find('a').text.replace("\n", "").replace("\t", ""))
                            if each.find('a').get('href') in self.temp_links:
                                self.data['axs_code'].pop()
                                self.data['date_published'].pop()
                                self.data['headline'].pop()
                            else:
                                self.temp_links.append(each.find('a').get('href'))
                        i+=1
            driver.close()
            return True
        else:
            self.log("No Items Found.")
            return False

    def download_pdf(self):
        if self.temp_links:
            print("@@@@", self.temp_links)
            for each in self.temp_links:
                options = webdriver.ChromeOptions()
                options.add_argument(Config.HEADLESS)
                driver = webdriver.Chrome(Config.CHROME_EXTENSION_PATH, options=options)
                driver.get(self.pdf_link + each.replace("amp;", "")) #1
                link = driver.find_element_by_xpath("//input[@name='pdfURL']")
                link = link.get_attribute('value') #2
                driver.close()
                existing_links = pd.read_csv("test.csv")
                existing_links = existing_links['link_to_pdf'].to_list()
                if self.pdf_link + link in existing_links:
                    self.data['axs_code'].pop()
                    self.data['date_published'].pop()
                    self.data['headline'].pop()
                    print("Omiiting Link as Already Exist", link)
                    self.log("Omiiting Link as Already Exist {}".format(link))
                    continue

                options = webdriver.ChromeOptions()
                options.add_argument(Config.HEADLESS)
                options.add_experimental_option('prefs', Config.EXPERIMENTAL_OPTIONS)
                driver = webdriver.Chrome(Config.CHROME_EXTENSION_PATH, options=options)
                self.log("Chrome Started for pdfs.")
                print("LINK: ", link)
                self.data['link_to_pdf'].append(self.pdf_link + link)
                driver.get(self.pdf_link + link)
                time.sleep(5)
                f = os.listdir(Config.EXPERIMENTAL_OPTIONS['download.default_directory'])
                f = " ".join(f)
                print("#####", f)
                while(1):
                    if 'crdownload' in f:
                        print("[INFO] Waiting for incomplete download..")
                        time.sleep(2)
                        f = os.listdir(Config.EXPERIMENTAL_OPTIONS['download.default_directory'])
                        f = " ".join(f)
                    else:
                        print("[INFO] No Incomplete Download Found")
                        break
                driver.close()
            return True
        else:
            return False

    def extract_pdf(self):
        files = os.listdir(Config.EXPERIMENTAL_OPTIONS['download.default_directory'])
        if files:
            pdf_over_all = {}
            for file in files:
                if file.endswith(".pdf"):
                    try:
                        #filer = open(os.path.join(Config.EXPERIMENTAL_OPTIONS['download.default_directory'], file), 'rb')
                        #fileReader = PyPDF2.PdfFileReader(filer)
                        #text = ""
                        #for i in range(fileReader.numPages):
                            #pageObj = fileReader.getPage(i)
                            #text += pageObj.extractText()
                        text = None
                        raw = parser.from_file(os.path.join(Config.EXPERIMENTAL_OPTIONS['download.default_directory'], file))['content']
                        time.sleep(0.2)
                        text = raw.replace("\n", "").replace("\t", "").strip().lower().split()
                        positive_words_count = 0
                        positive_words = []
                        negative_words_count = 0
                        negative_words = []                    
                        pdf_data = {}
                        pdf_data['total_word_count'] = 0
                        pdf_data['positive_words'] = 0
                        pdf_data['negative_words'] = 0
                        pdf_data['positive_count'] = 0
                        pdf_data['negative_count'] = 0
                        pdf_data['total_word_count'] = len(text)
                        #self.data['total_word_count'].append(len(text))
                        for positive_word in Config.POSITIVE_WORDS_LIST:
                            if positive_word in text:                                
                                positive_words_count += 1
                                positive_words.append(positive_word)
                                if positive_word == 'contract':
                                    #f = open("check.txt", "w")
                                    #f.write("||".join(text.lower().split()));f.close()
                                    print(text.index(positive_word))

                        #self.data["positive_words"].append(positive_words)
                        #self.data['positive_count'].append(positive_words_count)
                        pdf_data['positive_words'] = positive_words
                        pdf_data['positive_count'] = positive_words_count

                        for negative_word in Config.NEGATIVE_WORDS_LIST:
                            if negative_word in text:
                                negative_words_count += 1
                                negative_words.append(negative_word)
                        #self.data["negative_words"].append(negative_words)
                        #self.data['negative_count'].append(negative_words_count)
                        pdf_data['negative_words'] = negative_words
                        pdf_data['negative_count'] = negative_words_count
                        pdf_over_all[file] = pdf_data
                        #filer.close()
                        os.remove(os.path.join(Config.EXPERIMENTAL_OPTIONS['download.default_directory'], file))
                    except Exception as e:
                        self.log("[Exception] PDF is corrupted" + str(e))
                        #try:
                            #filer.close()
                        #except:
                            #pass
                        self.data['total_word_count'].append("Nan")
                        self.data["positive_words"].append(["Nan"])
                        self.data['positive_count'].append("Nan")
                        self.data["negative_words"].append(["Nan"])
                        self.data['negative_count'].append("Nan")
                        os.remove(os.path.join(Config.EXPERIMENTAL_OPTIONS['download.default_directory'], file))
                else:
                    print("[INFO] Invalid PDF", file)
            print("PDF OEVRALL ", pdf_over_all)
            for i in range(len(self.data['link_to_pdf'])):
                file_se = self.data['link_to_pdf'][i].split('/pdf/')[1]
                req_dict = pdf_over_all[file_se]
                self.data['total_word_count'].append(req_dict['total_word_count'])
                self.data["positive_words"].append(req_dict['positive_words'])
                self.data['positive_count'].append(req_dict['positive_count'])
                self.data["negative_words"].append(req_dict['negative_words'])
                self.data['negative_count'].append(req_dict['negative_count'])
            return True
        else:
            return False

    def save_results(self):
        print(self.data)
        new_df = pd.DataFrame(self.data)
        new_df.to_csv('test.csv')
        # is_file = os.path.isfile(Config.STORAGE_FILE)
        # if is_file:
        #     print("[INFO] Storage File Found.")
        #     df = pd.read_excel(Config.STORAGE_FILE, engine='openpyxl')
        #     df = df.append(new_df)
        #     df.to_excel(Config.STORAGE_FILE, index=False)
        # else:
        #     print("[INFO] Storage File Not Found.")
        #     print("[INFO] Creating Storage File")
        #     new_df.to_excel(Config.STORAGE_FILE, index=False)
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

        # add credentials to the account
        creds = ServiceAccountCredentials.from_json_keyfile_name('utility-terrain-330100-03694d82617f.json', scope)

        # authorize the clientsheet 
        client = gspread.authorize(creds)
        sheet = client.open('Stocks Data Sheet')
        sheet_instance = sheet.get_worksheet(0)
        df = pd.read_csv("test.csv")
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        sheet_instance.insert_rows(df.values.tolist())

        self.cleaner()
