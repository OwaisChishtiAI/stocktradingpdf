from crawler import Crawler
from config import Config
from time import sleep

def main():
    i = 1
    while(1):
        try:
            print("Initiating Round ", i)
            crawl = Crawler()
            has_crawled = crawl.run()
            if has_crawled:
                print("[INFO] Data Extracted.")
                downloaded = crawl.download_pdf()
                if downloaded:
                    print("[INFO] PDFs Downloaded.")
                    extracted = crawl.extract_pdf()
                    if extracted:
                        print("[INFO] PDFs Readed.")
                        crawl.save_results()
                        print("[INFO] Data Saved.")
                        crawl.log("Round {} Successful.".format(str(i)))
                    else:
                        crawl.log("Round {} Not Successful.".format(str(i)))
                else:
                    crawl.log("Found No Downloads.")
            print("Waiting...")
            sleep(Config.INTERVAL_TIME)
        except Exception as e:
            print("[ERROR] Round {} Failed.".format(str(i)))
            crawl.log("Round {} Failed.".format(str(i)) + str(e))
        i+=1

if __name__ == "__main__":
    main()