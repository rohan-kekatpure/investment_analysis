import csv
import glob
import os
from pprint import pprint
import re
from bs4 import BeautifulSoup
from gfnc_fundpage_scraper import GfncFundpageScraper
from yfnc_fundpage_scraper import YfncFundpageScraper
from fundpage_downloader import FundpageDownloader
from ticker_generator import TickerGenerator

# tkgen = TickerGenerator(downloads_folder="../tickerpages")
# tkgen.download_marketwatch_ticker_pages("http://www.marketwatch.com/tools/mutual-fund/list/")
# tkgen.extract_marketwatch_tickers("../csv/marketwatch_ticker_list.csv")


#Download fundpages recursively
# downloads_folder = "../html/gfnc_fund_pages"
# failed_downloads_file = "../csv/failed_downloads.csv"
#
# fundpage_downloader = FundpageDownloader(tickerlist_file=failed_downloads_file,
#                                          delimiter="|",
#                                          downloads_folder=downloads_folder,
#                                          failed_downloads_file=failed_downloads_file,
#                                          source="gfnc",
#                                          fresh=False)
# while len(open(failed_downloads_file).readlines()) > 0:
#     fundpage_downloader.download_fundpages()

# fundpage_downloader.list_failed_downloads()


# test scraper
# yscraper = YfncFundpageScraper("../test_fund_pages",
#                                "../csv/marketwatch_ticker_list.csv",
#                                delimiter="|")
# yscraper.get_profiles("../csv/test_profiles.csv")
# yscraper.get_risk("../csv/test_risk.csv")
# yscraper.get_performance("../csv/test_performance.csv")

fundpages_location = "/Users/rkekatpure/work/code/investing/html/gfnc_fund_pages"
tickerlist_file = "/Users/rkekatpure/work/code/investing/csv/marketwatch_ticker_list.csv"
outputfile = "/Users/rkekatpure/work/code/investing/csv/gfnc.csv"
gfnc_scraper = GfncFundpageScraper(fundpages_location=fundpages_location,
                                   tickerlist_file=tickerlist_file,
                                   delimiter="|")
gfnc_scraper.scrape(outputfile)

