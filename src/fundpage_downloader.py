import csv
import os
import shutil
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

    def __init__(self, downloads_folder=default_download_folder):
        # Start a fresh downloads folder. If exists, delete and create. If doesn't exist,
        # just create.
        self.downloads_folder = downloads_folder
        if os.path.exists(downloads_folder):
            shutil.rmtree(downloads_folder)
            os.makedirs(downloads_folder)
        else:
            os.makedirs(downloads_folder)

    def download_fundpages(self, tickerlist_csv_file, delimiter="|", source="gfnc"):
            """
            Reads records from the supplied delimited file, extracts ticker symbol and passes
            on to yfnc_fund_page_downloader(ticker) for the actual download task

             @param tickerlist_csv_file: Filename (with location) of the csv file containing
             a delimited rows of form "fund_ticker" <delimiter> "fund name"
             @type tickerlist_csv_file: str

             @param delimiter: delimiter in the csv file containing ticker names
             @type delimiter: str

             @param source: One of the predefined download sources. Currently supported
             options are "gfnc" for google finance and "yfnc" for yahoo finance.
            """

            # Read the csvfile, and download page(s) for each ticker symbol.
            ticker_reader = csv.reader(open(tickerlist_csv_file, "rb"), delimiter=delimiter)
            for ticker, name in ticker_reader:
                print "downloading %s: %s..." % (ticker, name)
                if source == "gfnc":
                    self.download_gfnc_fundpages(ticker)
                elif source == "yfnc":
                    self.download_yfnc_fundpages(ticker)

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