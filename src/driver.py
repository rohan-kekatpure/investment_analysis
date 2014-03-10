import csv
import os
from bs4 import BeautifulSoup
from yfnc_fundpage_scraper import YfncFundpageScraper
from fundpage_downloader import FundpageDownloader
from ticker_generator import TickerGenerator

# tkgen = TickerGenerator(downloads_folder="../tickerpages")
# tkgen.download_marketwatch_ticker_pages("http://www.marketwatch.com/tools/mutual-fund/list/")
# tkgen.extract_marketwatch_tickers("../csv/marketwatch_ticker_list.csv")


failed_download_tickers = "../csv/failed_downloads.csv"
while len(open(failed_download_tickers).readlines()) > 0:
    fundpage_downloader = FundpageDownloader(tickerlist_file=failed_download_tickers,
                                             delimiter="|",
                                             downloads_folder="../google_finance_fund_pages",
                                             source="gfnc",
                                             fresh=False)
    fundpage_downloader.download_fundpages()



# test scraper
# yscraper = YfncFundpageScraper("../test_fund_pages",
#                                "../csv/marketwatch_ticker_list.csv",
#                                delimiter="|")
# yscraper.get_profiles("../csv/test_profiles.csv")
# yscraper.get_risk("../csv/test_risk.csv")
# yscraper.get_performance("../csv/test_performance.csv")
