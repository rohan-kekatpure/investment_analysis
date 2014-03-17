import os
import re
from bs4 import BeautifulSoup
from tidylib import tidy_document
from abstract_scraper import AbstractScraper
from gfnc_key_mappings import GfncKeymappings


class GfncScraper(AbstractScraper):
    """
    Class for scraping google finance fundpages.
    This class is a sibling of the YfncFundpageScraper
    """
    def __init__(self, fundpages_location, tickerlist_file, delimiter="|"):
        """
        Constructs Google finance page scraper object by calling __init__ of AbstractScraper
        @param fundpages_location: Location of downloaded html fund pages (string)
        @type fundpages_location: str
        @param tickerlist_file: Location of csv file containing ticker symbol list
        @type tickerlist_file: str
        @param delimiter: delimiter in tickerlist_file
        @type delimiter: str
        """
        super(GfncScraper, self).__init__(fundpages_location, tickerlist_file, delimiter="|")

    def scrape(self, outputfile=None):
        """
        Delegator function for google finance scraper
        @param outputfile: name of output CSV file where info is to be written
        @type outputfile: str
        """

        # @TODO: Delegation after creating the soup
        # Soup creation is an expensive step and it may make more sense to
        # delegate after generating the soup of the downloaded page.

        # ------------------------------------
        # Get performance
        # ------------------------------------
        outputfile_performance = super(GfncScraper, self).insert_suffix(outputfile, "_performance")
        print "writing to file %s" % outputfile_performance
        self.get_performance(outputfile=outputfile)

        # ------------------------------------
        # Get risk
        # ------------------------------------
        outputfile_risk = super(GfncScraper, self).insert_suffix(outputfile, "_risk")
        print "writing to file %s" % outputfile_risk
        self.get_risk(outputfile=outputfile_risk)

        # ------------------------------------
        # Get profile
        # ------------------------------------
        outputfile_profile = super(GfncScraper, self).insert_suffix(outputfile, "_profile")
        print "writing profile data to file %s" % outputfile_profile
        self.get_profile(outputfile=outputfile_profile)

    def get_profile(self, outputfile=None):

        """
        Scraper to get profile (net assets, exp ratio) data
        """
        management_fields = ["total_assets", "front_load", "deferred_load", "expense_ratio", "management_fees", "fund_family"]
        allocation_fields = ["pct_cash", "pct_stock", "pct_bonds", "pct_preferred", "pct_convertible", "pct_other"]

        ticker_count = len(self.tickers)
        profile_list = []
        for ticker_no, ticker in enumerate(self.tickers):
            page = os.path.join(self.fundpages_location, "%s.html" % ticker)
            newpage, errors = tidy_document(open(page).read())
            soup = BeautifulSoup(newpage)

            # Initialize a dict to hold risk data of this ticker. The data will be added
            # at the ned of the try block
            profile_dict = {"ticker": ticker}

            try:
                profile_data_tables = \
                    soup\
                    .body\
                    .findAll('div', id='gf-viewc')[0]\
                    .findAll('div', class_='fjfe-content')[0]\
                    .findAll('div', class_='mutualfund')[0]\
                    .findAll('div', class_='g-section g-tpl-right-1')[0]\
                    .findAll('div', class_='g-unit g-first')[0]\
                    .findAll('div', class_='g-c')[0]\
                    .findAll('div', class_='sector')

                # Extract and clean profile fields
                management_table = profile_data_tables[2]\
                    .findAll('div', class_='subsector')[0]\
                    .table

                management_data_raw = [[col.text.strip() for col in row.findAll('td')]
                                       for row in management_table.findAll('tr')]

                management_data_clean = map(lambda x: '' if x == '-' else x,
                                            [P[1] for P in management_data_raw])

                # Clean up 'total_assets' fields by removing millions and billions suffix
                total_assets = management_data_clean[0]
                if total_assets.endswith("M"):
                    total_assets = float(total_assets.replace("M", ""))
                elif total_assets.endswith("B"):
                    total_assets = 1000.0 * float(total_assets.replace("B", ""))
                elif total_assets == "":
                    total_assets = -1.0  # Sentinel value to indicate missing total_asset information
                else:
                    total_assets = float(total_assets.replace(",", "")) / 1000000.0  # Total assets in dollars, convert to Millions
                management_data_clean[0] = total_assets

                # Clean up 'front_load', 'deferred_load' and 'expense_ratio' fields
                # by removing the percent '%' symbol at the end and converting to float
                management_data_clean[1:4] = map(lambda x: x.replace("%", "") if x != "" else x,
                                                 management_data_clean[1:4])

                # Add management data to current fund profile
                profile_dict.update(dict(zip(management_fields, management_data_clean)))

                # Extract and clean asset allocation data
                # allocation_table = soup.body.findAll('div', class_='sector')[3].table
                allocation_table = profile_data_tables[3].table
                allocation_data_raw = [[col.text.strip() for col in row.findAll('td')]
                                       for row in allocation_table.findAll('tr')]

                # Allocations only list the asset categories in the fund. A fund with 'cash'
                # and 'stocks' will not have 'bond' = '-', 'convertibles'='-' etc.
                # We therefore need to make sure that the output dictionary contains all the
                # fields even if they are empty. We initialize an empty dictionary and fill it
                # with values of existing asset categories for the current fund.
                allocations_dict = dict.fromkeys(allocation_fields, "")
                for asset_class, allocation_pct, _ in allocation_data_raw:
                    allocations_dict[GfncKeymappings.allocations_keymap[asset_class]] = allocation_pct.replace("%", "")

                # Add asset allocation data to profile data
                profile_dict.update(allocations_dict)
            except IndexError, E:
                print "[IndexError: %s] could not parse %s" % (E.message, page)
            except KeyError, K:
                # print "[KeyError: %s] could not parse %s" % (K.message, page)
                pass
            # Append current fund profile to profiles_list
            profile_list.append(profile_dict)

            # publish progress
            if ticker_no % 100 == 0:
                print "%d of %d" % (ticker_no, ticker_count)

        # Aggregate profile fields
        profile_fields_all = ["ticker"] + management_fields + allocation_fields
        super(GfncScraper, self).writecsv(profile_fields_all, profile_list, outputfile)

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
                    .div(id="gf-viewc")[0]\
                    .findAll("div", class_="fjfe-content")[0]\
                    .findAll("div", class_="mutualfund")[0]\
                    .findAll("div", class_="g-section g-tpl-right-1")[0]\
                    .findAll("div", class_="g-unit")[1]\
                    .findAll("div", class_="g-c sfe-break-right")[0]\
                    .findAll("div", class_="sector")[1]\
                    .findAll("div", class_="subsector")[0].table

                riskdata_raw = [
                    [col.text.strip() for col in row.findAll("td")]
                    for row in risktable.findAll("tr")
                ]

                # Convert available fields to float. Unavailable fields are presented as '-'
                # in the html, convert them to empty strings.
                riskdata_float = [map(lambda x: float(x) if x != "-" else "", R[1:])
                                  for R in riskdata_raw[1:-1]]

                # Add the risk data for this ticker to riskdata_dict
                for field_type, field_data in zip(risk_fields, riskdata_float):
                    riskdata_dict.update(dict(zip(field_type, field_data)))
            except (IndexError, AttributeError):
                pass
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
        super(GfncScraper, self).writecsv(risk_fields_flattened, risk_list, outputfile)

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
        super(GfncScraper, self).writecsv(["ticker"] + performance_fields, performance_list, outputfile)

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
        super(GfncScraper, self).writecsv(performance_fields, fund_performances, outputfile)