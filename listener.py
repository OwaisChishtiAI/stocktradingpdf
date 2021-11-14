from crawler import Crawler
from config import Config
from time import sleep

def main():
    while(1):
        print("Initiating...")
        crawl = Crawler()
        has_crawled = crawl.run()
        if has_crawled:
            downloaded = crawl.download_pdf()
            if downloaded:
                extracted = crawl.extract_pdf()
                if extracted:
                    crawl.log("Round Successful.")
                else:
                    crawl.log("Round Not Successful.")
            else:
                crawl.log("Found No Downloads.")
        print("Waiting...")
        sleep(Config.INTERVAL_TIME)

if __name__ == "__main__":
    main()