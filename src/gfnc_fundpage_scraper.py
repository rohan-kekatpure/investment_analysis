import os
import re
from bs4 import BeautifulSoup
from tidylib import tidy_document
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
        Delegator function for google finance scraper
        @param outputfile: name of output CSV file where info is to be written
        @type outputfile: str
        """

        # @TODO: Delegation after creating the soup
        # Soup creation is an expensive step and it may make more sense to
        # delegate after generating the soup of the downloaded page.
        self.get_performance2(outputfile=outputfile)

    def get_risk(self, outputfile=None):
        """
        Scraper function to get risk data
        """
        pass

    def get_performance(self, outputfile=None):
        """
        Scraper function to get performance data
        """
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

    def get_performance2(self, outputfile=None):
        """
        Alternate scraper function to get performance data. Laborious, slower, but direct
        """

        # Strings for intervals for which return information is vailable in Google Finance
        header = ["ticker", "1 day", "1 week", "4 week", "3 month", "YTD",
                  "1 year", "3 years", "5 years"]

        # Pattern for detecting performance strings
        pattern = pattern=re.compile("[ ]+([\+\-]\d*\.*\d*)%*")
        ticker_count = len(self.tickers)
        fund_performances = []
        for ticker_no, ticker in enumerate(self.tickers):
            page = os.path.join(self.fundpages_location, "%s.html" % ticker)
            tidy_html, errors = tidy_document(open(page).read())
            soup = BeautifulSoup(tidy_html)
            try:
                performance_tags\
                    = soup.body.div(id="gf-viewc")[0] \
                    .find('div', class_='fjfe-content')\
                    .find('div', class_='mutualfund')\
                    .find('div', class_='g-section g-tpl-right-1')\
                    .find('div', class_='g-unit g-first')\
                    .find('div', class_='g-c')\
                    .find('div', class_='sector performance')\
                    .findAll('div', class_='subsector')[1]\
                    .find('table')\
                    .findAll('tr')[::2]

                performance_data_strings = \
                    filter(lambda x: x != u'', [u.text.encode('ascii', errors='ignore').replace("\n", "").strip()
                                                for u in performance_tags])
                performance_data = [re.search(pattern, s).group(1) for s in performance_data_strings[:-1]]
            except AttributeError:
                performance_data = []

            fund_performances.append(zip(header, [ticker] + performance_data))

            # Print progress
            if ticker_no % 100 == 0:
                print "%d of %d" % (ticker_no, ticker_count)

        # write performance data to a CSV file
        super(GfncFundpageScraper, self).writecsv(header, fund_performances, outputfile)