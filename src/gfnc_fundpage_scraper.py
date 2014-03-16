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

        # outputfile_performance = super(GfncFundpageScraper, self).insert_suffix(outputfile, "_performance")
        # self.get_performance(outputfile=outputfile)

        outputfile_risk = super(GfncFundpageScraper, self).insert_suffix(outputfile, "_risk")
        print "writing to file %s" % outputfile_risk
        self.get_risk(outputfile=outputfile_risk)

    def get_risk(self, outputfile=None):
        """
        Scraper function to get risk data
        """
        risk_fields = [["alpha1", "alpha3", "alpha5", "alpha10"],
                       ["beta1", "beta3", "beta5", "beta10"],
                       ["MAR1", "MAR3", "MAR5", "MAR10"],
                       ["R2_1", "R2_3", "R2_5", "R2_10"],
                       ["SD1", "SD3", "SD5", "SD10"],
                       ["sharpe1", "sharpe3", "sharpe5", "sharpe10"]]

        ticker_count = len(self.tickers)
        risk_list = []
        for ticker_no, ticker in enumerate(self.tickers):
            page = os.path.join(self.fundpages_location, "%s.html" % ticker)
            # print "scraping page %s" % page
            newpage, errors = tidy_document(open(page).read())
            soup = BeautifulSoup(newpage)
            # Initialize a dict to hold risk data of this ticker. The data will be added
            # at the ned of the try block
            riskdata_dict = {"ticker": ticker}

            try:
                # Retrieve the risk table by descending into the DOM
                risktable = \
                    soup\
                    .body\
                    .div(id='gf-viewc')[0]\
                    .findAll('div', class_='fjfe-content')[0]\
                    .findAll('div', class_='mutualfund')[0]\
                    .findAll('div', class_='g-section g-tpl-right-1')[0]\
                    .findAll('div', class_='g-unit')[1]\
                    .findAll('div', class_='g-c sfe-break-right')[0]\
                    .findAll('div', class_='sector')[1]\
                    .findAll('div', class_='subsector')[0].table

                riskdata_raw = [
                    [row.text.strip() for row in rows.findAll('td')]
                    for rows in risktable.findAll('tr')
                ]

                # Convert available fields to float. Unavailable fields are presented as '-'
                # in the html, convert them to empty strings.
                riskdata_float = [map(lambda x: float(x) if x != '-' else '', R[1:])
                                  for R in riskdata_raw[1:-1]]

                # Add the risk data for this ticker to riskdata_dict
                for field_type, field_data in zip(risk_fields, riskdata_float):
                    riskdata_dict.update(dict(zip(field_type, field_data)))
            except (IndexError, AttributeError):
                # print "page could not be scraped for ticker %s" % ticker

            # Append risk data for the current ticker to the list
            risk_list.append(riskdata_dict)

            # Print progress
            if ticker_no % 100 == 0:
                print "%d of %d" % (ticker_no, ticker_count)

        # Flatten the risk_fields to feed to the CSV writer and add field
        # "ticker" at the front
        risk_fields_flattened = ["ticker"] + reduce(lambda x, y: x + y, risk_fields)

        # Write the CSV file
        super(GfncFundpageScraper, self).writecsv(risk_fields_flattened, risk_list, outputfile)

    def get_performance(self, outputfile=None):
        """
        Scraper function to get performance data
        """
        # Strings for intervals for which return information is vailable in Google Finance
        performance_fields = ["1 day", "1 week", "4 week", "3 month", "YTD",
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
        intvl_patterns = [re.compile("%s%s" % (durn, base_pattern_string)) for durn in performance_fields]

        # Create tuples of duration strings and their corresponding regexes
        dur_patterns = zip(performance_fields, intvl_patterns)

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
        super(GfncFundpageScraper, self).writecsv(["ticker"] + performance_fields, performance_list, outputfile)

    def get_performance2(self, outputfile=None):
        """
        Alternate scraper function to get performance data. Laborious, slower, but direct
        """

        # Strings for intervals for which return information is vailable in Google Finance
        performance_fields = ["ticker", "1 day", "1 week", "4 week", "3 month", "YTD",
                              "1 year", "3 years", "5 years"]

        # Pattern for detecting performance strings
        pattern = pattern = re.compile("[ ]+([\+\-]\d*\.*\d*)%*")
        ticker_count = len(self.tickers)
        fund_performances = []
        for ticker_no, ticker in enumerate(self.tickers[:10]):
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

            fund_performances.append(dict(zip(performance_fields, [ticker] + performance_data)))

            # Print progress
            if ticker_no % 100 == 0:
                print "%d of %d" % (ticker_no, ticker_count)

        # write performance data to a CSV file
        super(GfncFundpageScraper, self).writecsv(performance_fields, fund_performances, outputfile)