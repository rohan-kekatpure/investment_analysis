import csv
import os
import shutil
from bs4 import BeautifulSoup
import requests


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
                 delimiter = "|",
                 downloads_folder=default_download_folder):
        # Start a fresh downloads folder. If exists, delete and create. If doesn't exist,
        # just create.
        self.downloads_folder = downloads_folder
        if os.path.exists(downloads_folder):
            shutil.rmtree(downloads_folder)
            os.makedirs(downloads_folder)
        else:
            os.makedirs(downloads_folder)

        assert os.path.exists(tickerlist_file), \
            "[FundpageDownloader] Tickerlist file %s does not exist" % tickerlist_file

        # Generate list of tickers from tickerlist_file and store in self.tickers
        with open(tickerlist_file, "rb") as f:
            reader = csv.reader(f, delimiter=delimiter)
            self.tickers = [record[0] for record in reader]

    def download_fundpages(self, source="gfnc"):
            """
            Reads records from the supplied delimited file, extracts ticker symbol and passes
            on to yfnc_fund_page_downloader(ticker) for the actual download task

             @param source: One of the predefined download sources. Currently supported
             options are "gfnc" for google finance and "yfnc" for yahoo finance.
            """
            for ticker in self.tickers:
                print "downloading fundpage for %s..." % ticker
                if source == "gfnc":
                    self.download_gfnc_fundpages(ticker)
                elif source == "yfnc":
                    self.download_yfnc_fundpages(ticker)

            # Validate that all downloaded pages contain valid data. Fast programmatic
            # hits to Google finance pages results in come pages getting CAPTCHA response.
            # The validator function writes un-downloaded symbols to a separate file.

            if source == "gfnc":
                self.validate_gfnc_fundpages()

    def download_gfnc_fundpages(self, ticker):
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

    def download_yfnc_fundpages(self, ticker):
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

    def validate_gfnc_fundpages(self):
        """
        Separates downloaded webpages into those with data and those without.
        The ones without data have captchas. We locate presencee of captchas
        to detect un-downloaded pages
        """
        not_downloaded_file = "../csv/not_downloaded.csv"
        with open(not_downloaded_file, "wb") as f:
            writer = csv.writer(f)
            for ticker in self.tickers:
                page = os.path.join(self.downloads_folder, "%s.html" % ticker)
                soup = BeautifulSoup(open(page))
                if soup.find("body").attrs["onload"].find("captcha") > -1:
                    writer.writerow(ticker)