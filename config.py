import os
class Config:
    POSITIVE_WORDS_LIST = [x.lower() for x in open("positive_words_list.txt", "r", encoding="utf8", errors="ignore").read().split("\n") if x]
    NEGATIVE_WORDS_LIST = [x.lower() for x in open("negative_words_list.txt", "r", encoding="utf8", errors="ignore").read().split("\n") if x]
    STORAGE_FILE = "Stocks Data.xlsx"
    CHROME_EXTENSION_PATH = r"C:\Users\owais\Documents\chrome95\chromedriver_win32\chromedriver.exe"
    EXPERIMENTAL_OPTIONS = {"download.default_directory": os.path.join(os.path.abspath('.') , "cached_pdfs"),\
    "download.prompt_for_download": False,\
    "download.directory_upgrade": True,\
    "plugins.always_open_pdf_externally": True}
    HEADLESS = "--headless"
    TODAY_ANNOUNCEMENTS = "https://www.asx.com.au/asx/v2/statistics/todayAnns.do"
    INTERVAL_TIME = 60 * 1 # Change 5 to any other number, 5 refers five minutes.s