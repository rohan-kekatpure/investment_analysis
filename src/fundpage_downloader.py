import csv
import os
import shutil
from bs4 import BeautifulSoup
import requests
import time


class FundpageDownloader:
    """
    Class for organizing downloads of fund pages from the ticker symbol list
    """

    # Static variables: Base urls for download links
    default_download_folder = "./_fund_pages_html"
    gfnc_baseurl = "http://www.google.com/finance?q="
    yfnc_baseurl_profile = "http://finance.yahoo.com/q/pr?s="
    yfnc_baseurl_performance = "http://finance.yahoo.com/q/pm?s="
    yfnc_baseurl_risk = "http://finance.yahoo.com/q/rk?s="

    def __init__(self, tickerlist_file=None,
                 delimiter="|",
                 downloads_folder=default_download_folder,
                 source="gfnc",
                 fresh=False):
        """
        @param tickerlist_file: Pipe delimited file of <ticker>|<fundname>
        @type tickerlist_file: str
        @param delimiter: Delimiter used in tickerlist_file
        @type delimiter: str
        @param downloads_folder: Folder to put downloaded HTML
        @type downloads_folder: str
        @param source: One of the predefined download sources. Currently supported
        options are "gfnc" for google finance and "yfnc" for yahoo finance.
        @type source: str
        @param fresh: Delete and recreate downloads folder
        @type fresh: bool

        """
        # Start a fresh downloads folder. If exists, delete and create. If doesn't exist,
        # just create.
        self.downloads_folder = downloads_folder

        # If 'fresh' is True,
        if fresh:
            if os.path.exists(self.downloads_folder):
                shutil.rmtree(self.downloads_folder)
                os.makedirs(self.downloads_folder)
            else:
                os.makedirs(self.downloads_folder)
        else:
            assert os.path.exists(self.downloads_folder), \
                '''[FundpageDownloader] Downloads folder %s does not exist.
                Either create externally or create new downloader instance with fresh=True'''\
                % tickerlist_file

        self.source = source

        assert os.path.exists(tickerlist_file), \
            "[FundpageDownloader] Tickerlist file %s does not exist" % tickerlist_file

        # Generate list of tickers from tickerlist_file and store in self.tickers
        with open(tickerlist_file, "rb") as f:
            tickerlist = list(csv.reader(f, delimiter="|"))
            symbs = [record[0] for record in tickerlist]
            fundnames = [record[1] for record in tickerlist]
            self.funds = dict(zip(symbs, fundnames))
            del tickerlist, symbs, fundnames

    def download_fundpages(self):
            """
            Reads records from the supplied delimited file, extracts ticker symbol and passes
            on to yfnc_fund_page_downloader(ticker) for the actual download task
            """
            for ticker in self.funds:
                print "downloading fundpage for %s..." % ticker
                if self.source == "gfnc":
                    self.download_gfnc_fundpage(ticker)
                elif self.source == "yfnc":
                    self.download_yfnc_fundpage(ticker)

            # Validate that all downloaded pages contain valid data. Fast programmatic
            # hits to Google finance pages results in come pages getting CAPTCHA response.
            # The validator function writes un-downloaded symbols to a separate file.

            if self.source == "gfnc":
                self.list_failed_downloads()

    def download_gfnc_fundpage(self, ticker):
        """
        Downloades one page per mutual fund from Google finance
        @type ticker: str
        @param ticker: Ticker symbol
        @return: None
        """
        pageurl = FundpageDownloader.gfnc_baseurl + ticker
        response = requests.get(pageurl)
        filename = "%s/%s.html" % (self.downloads_folder, ticker)

        with open(filename, "w") as f:
            f.write(response.content)

    def download_yfnc_fundpage(self, ticker):
        """
        Downloads profile, performance and risk pages for a mutual fund with symbol 'ticker'
        from Yahoo Finance.
        @type ticker: str
        @param ticker: Ticker symbol
        @return: None
        """
        url_profile = FundpageDownloader.yfnc_baseurl_profile + ticker
        url_performance = FundpageDownloader.yfnc_baseurl_performance + ticker
        url_risk = FundpageDownloader.yfnc_baseurl_risk + ticker

        urls = {"profile": url_profile,
                "performance": url_performance,
                "risk": url_risk}
        for kind in urls:
            response = requests.get(urls[kind])
            filename = "%s/%s_%s.html" % (self.downloads_folder, ticker, kind)
            with open(filename, "w") as f:
                f.write(response.content)

    def list_failed_downloads(self):
        """
        Separates downloaded webpages into those with data and those without.
        The ones without data have captchas. We locate presencee of captchas
        to detect un-downloaded pages
        """
        print "Generating failed downloads..."

        failed_downloads = "../csv/failed_downloads.csv"

        # If a 'failed_downloads' file exists already, rename it by appending a current
        # timestamp to its name.
        if os.path.exists(failed_downloads):
            old_failed_downloads = "../csv/failed_downloads_%s.csv" % str(int(time.time()))
            os.rename(failed_downloads, old_failed_downloads)

        with open(failed_downloads, "wb") as f:
            writer = csv.writer(f, delimiter="|")
            for ticker in self.funds:
                page = os.path.join("../google_finance_fund_pages", "%s.html" % ticker)
                soup = BeautifulSoup(open(page))
                body = soup.find("body")
                try:
                    if "captcha" in body.attrs["onload"]:
                        print "Not downloaded %s" % ticker
                        writer.writerow([ticker, self.funds[ticker]])
                except KeyError:
                    pass