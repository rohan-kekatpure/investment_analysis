import glob
import os
import re
import shutil
import string
from bs4 import BeautifulSoup
import requests


class TickerGenerator:
    """
    We want to decouple downloading of fund ticker web pages from their scraping. Too
    many programmatic hits to marketwatch or morningstar websites is likely to get us
    banned for an interval of time; so we download the HTMLs containing ticker symbols
    and _then_ scrape the HTMLs to extract <ticker>:<name> key-value pairs.

    The class has different methods for various download sites such as Morningstar,
    marketwatch. Custom methods for other sites can be added as needed.
    """

    def __init__(self, downloads_folder="."):
        """
        stores
        @param downloads_folder: folder for storing downloaded pages
        @type downloads_folder: str
        """
        self.downloads_folder = downloads_folder
        if os.path.exists(self.downloads_folder):
            shutil.rmtree(self.downloads_folder)
            os.makedirs(self.downloads_folder)
        else:
            os.makedirs(self.downloads_folder)

    def download_marketwatch_ticker_pages(self, base_url=None):
        # base_url = "http://www.marketwatch.com/tools/mutual-fund/list/"
        for startletter in string.ascii_uppercase:
            fund_url = base_url + startletter
            print "downloading %s..." % fund_url
            response = requests.get(fund_url)
            with open(self.downloads_folder + "/" + startletter + ".html", "w") as f:
                f.write(response.content)

    def extract_marketwatch_tickers(self, tickerlist_file):
        """
        This function, scrapes ticker HTMLs in "./marketwatch_mutf_tickers" and generates
        <ticker>:<name> key-value pairs and writes it as a DSV file.
        """
        # Generate a regex pattern to match mutual funds. Ticker ymbols are anywhere between
        # UPPERCASE 2-5 characters

        assert os.path.exists(self.downloads_folder), \
            "Folder %s does not exist" % self.downloads_folder

        fundpages = glob.glob("%s/*.html" % self.downloads_folder)
        tickerpattern = re.compile("/[A-Z]{2,5}")
        with open(tickerlist_file, "w") as f:
            for fundpage in fundpages:
                soup = BeautifulSoup(open(fundpage).read())
                fundname_tags = soup.findAll("td", class_="quotelist-name")
                fundnames = [tag.text for tag in fundname_tags]
                fundtickers = [re.findall(tickerpattern, tag.find("a").attrs["href"])[0][1:]
                               for tag in fundname_tags]
                for ticker, name in zip(fundtickers, fundnames):
                    print "%s: %s" % (ticker, name)
                    f.write("%s|%s\n" % (ticker, name))

