import csv
import os
import re
from bs4 import BeautifulSoup
import sys
from abstract_scraper import AbstractScraper


class GfncFundpageScraper(AbstractScraper):
    """
    Class for scraping google finance fundpages.
    This class is a sibling of the YfncFundpageScraper
    """
    def __init__(self, fundpages_location, tickerlist_file, delimiter="|"):
        """
        Constructs yahoo finance page scraper object by calling __init__ of AbstractScraper
        @param fundpages_location: Location of downloaded html fund pages (string)
        @type fundpages_location: str
        @param tickerlist_file: Location of csv file containing ticker symbol list
        @type tickerlist_file: str
        @param delimiter: delimiter in tickerlist_file
        @type delimiter: str
        """
        super(GfncFundpageScraper, self).__init__(fundpages_location, tickerlist_file, delimiter="|")

    def scrape(self, outputfile=None):
        """
        Actual scraping is done here
        @param outputfile: name of output CSV file where info is to be written
        @type outputfile: str
        """
        self.get_performance(outputfile=outputfile)

    def get_performance(self, outputfile=None):
        # Strings for intervals for which return information is vailable in Google Finance
        durations = ["1 day", "1 week", "4 week", "3 month", "YTD",
                     "1 year", "3 years", "5 years"]

        # Common pattern
        # The common pattern (base_pattern) is constructed by inspecting the performance_info
        # An example raw performance_info string looks like the following:
        #
        # '   1 day       -0.45%    1 week       -0.57%    4 week   +2.82%\
        #         3 month   +6.31%          YTD   +2.34%        1 year   +19.87%\
        #         3 years*   +10.82%        5 years*   +21.35%       *annualized  '
        #
        # The three and five year return labels have an * after them so we catch it as a
        # first character. The rest of the pattern is self explanatory.
        base_pattern_string = "[\*]{0,1}[ ]+([\+\-]{1}[\d]+\.[\d]+)%"

        # Regex patterns for extracting returns for these intervals
        intvl_patterns = [re.compile("%s%s" % (durn, base_pattern_string)) for durn in durations]

        # Create tuples of duration strings and their corresponding regexes
        dur_patterns = zip(durations, intvl_patterns)

        ticker_count = len(self.tickers)
        performance_list = []
        for ticker_no, ticker in enumerate(self.tickers):
            page = os.path.join(self.fundpages_location, "%s.html" % ticker)
            with open(page) as fpage:
                soup = BeautifulSoup(fpage)
                try:
                    performance_info = soup.body.div(class_="subsector")[1].text.replace("\n", " ").encode('ascii', errors='ignore')
                    fund_data = {dur: re.search(pat, performance_info).group(1)
                                 for dur, pat in dur_patterns
                                 if re.search(pat, performance_info) is not None}
                except IndexError:
                    fund_data = {}
            fund_data.update({"ticker": ticker})
            performance_list.append(fund_data)

            # Print progress
            if ticker_no % 100 == 0:
                print "%d of %d" % (ticker_no, ticker_count)

        # write performance data to a CSV file
        super(GfncFundpageScraper, self).writecsv(["ticker"] + durations, performance_list, outputfile)