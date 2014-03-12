import csv
import glob
import os
from pprint import pprint
import re
from bs4 import BeautifulSoup
from yfnc_fundpage_scraper import YfncFundpageScraper
from fundpage_downloader import FundpageDownloader
from ticker_generator import TickerGenerator

# tkgen = TickerGenerator(downloads_folder="../tickerpages")
# tkgen.download_marketwatch_ticker_pages("http://www.marketwatch.com/tools/mutual-fund/list/")
# tkgen.extract_marketwatch_tickers("../csv/marketwatch_ticker_list.csv")


#Download fundpages recursively
downloads_folder = "../html/gfnc_fund_pages"
failed_downloads_file = "../csv/failed_downloads.csv"

fundpage_downloader = FundpageDownloader(tickerlist_file=failed_downloads_file,
                                         delimiter="|",
                                         downloads_folder=downloads_folder,
                                         failed_downloads_file=failed_downloads_file,
                                         source="gfnc",
                                         fresh=False)
while len(open(failed_downloads_file).readlines()) > 0:
    fundpage_downloader.download_fundpages()




# test scraper
# yscraper = YfncFundpageScraper("../test_fund_pages",
#                                "../csv/marketwatch_ticker_list.csv",
#                                delimiter="|")
# yscraper.get_profiles("../csv/test_profiles.csv")
# yscraper.get_risk("../csv/test_risk.csv")
# yscraper.get_performance("../csv/test_performance.csv")

# fundpages = glob.glob("../google_finance_fund_pages/*.html")
# pattern = re.compile("([\+\-]\w+\.\w+)%")
# no_performance_info = 0
# with open("test.csv", "wb") as f:
#     writer = csv.writer(f, delimiter="|")
#     for page in fundpages:
#         # print page,
#         soup = BeautifulSoup(open(page))
#         try:
#             perf = soup.body.div(class_="subsector")[1].text.replace("\n", " ").encode('ascii', errors='ignore')
#         except IndexError:
#             perf = ""
#             no_performance_info += 1
#             print "Instance = %d; page = %s" % (no_performance_info, page)
#         fund_returns = re.findall(pattern, perf)
#         # print "%s" % fund_returns
#         writer.writerow(fund_returns)

