import csv
import os
from pprint import pprint
import re
import string
from bs4 import BeautifulSoup
from yfnc_key_mappings import YfncKeymappings


class YfncFundpageScraper:
    """
    Methods for scraping downloaded yahoo finance webpages
    """

    # Utility method for writing CSV files
    @staticmethod
    def writecsv(csvfields, funddata, output_file):
            with open(output_file, "wb") as f:
                writer = csv.DictWriter(f, fieldnames=csvfields,
                                        delimiter='|',
                                        quoting=csv.QUOTE_MINIMAL)
                writer.writeheader()
                for item in funddata:
                    writer.writerow(item)

    # Utility method for generating names for intermediate files
    @staticmethod
    def insert_suffix(input_path, suffix):
        dirname = os.path.dirname(input_path)
        input_file_name, input_file_extn = os.path.basename(input_path).split(".")

        # Prepend a dot  ( "." ) to the input file extension
        if input_file_extn != "":
            input_file_extn = "." + input_file_extn

        suffixed_input_path = os.path.join(dirname, input_file_name + suffix + input_file_extn)
        return suffixed_input_path

    def __init__(self, fundpages_location, tickerlist_file, delimiter="|"):
        """
        Constructs yahoo finance page scraper object.
        @param fundpages_location: Location of downloaded html fund pages (string)
        @type fundpages_location: str
        @param tickerlist_file: Location of csv file containing ticker symbol list
        @type tickerlist_file: str
        @param delimiter: delimiter in tickerlist_file
        @type delimiter: str
        """

        self.fundpages_location = fundpages_location
        assert os.path.exists(tickerlist_file), \
            "[YfncFundpageScraper] Folder %s does not exist" % tickerlist_file

        assert os.path.exists(self.fundpages_location), \
            "[YfncFundpageScraper] Folder %s does not exist" % self.fundpages_location

        # Generate list of tickers from tickerlist_file and store in self.tickers
        with open(tickerlist_file, "rb") as f:
            reader = csv.reader(f, delimiter=delimiter)
            self.tickers = [record[0] for record in reader]

    def get_profiles(self, output_file="./_profiles.csv"):
        """
        Generates fund profile data from downloaded html pages and produces a CSV file
        containing profile data for each ticker.
        """
        profile_list = []
        for ticker in self.tickers:
            profile_page = "%s/%s_profile.html" % (self.fundpages_location, ticker)
            try:
                with open(profile_page) as fprofile:
                    profile_soup = BeautifulSoup(fprofile)
                    title_tables = profile_soup.findAll("table", class_="yfnc_mod_table_title1")
                    translations = string.maketrans("", "")
                    deletions = ":\n"
                    raw_profile = {}

                    # Scrape values of all fields form the HTML tables and store them in
                    # raw_profile dictionary. This dictionary is "raw" in the sense that
                    # the labelkeys are unstandardized names (with parens, colons etc)
                    # The label keys will be standardized in the next step with the help
                    # of YfncKeymappings.profile_keymap
                    for table in title_tables:
                        data_table = table.findNextSibling()
                        labels = data_table.findAll("td", class_="yfnc_datamodlabel1")
                        labelkeys = [re.sub("[ ]+", "", l.text
                                            .encode("ascii")
                                            .translate(translations, deletions))
                                     for l in labels]
                        values = data_table.findAll("td", class_="yfnc_datamoddata1")
                        labelvals = [v.text for v in values]
                        raw_profile.update(dict(zip(labelkeys, labelvals)))

                    # Standardize interesting fields using YfncKeymappings.profile_keymap
                    # and create a nice dictionary for output
                    selected_profile_data = {"ticker": ticker}
                    for key in YfncKeymappings.profile_keymap:
                        for field in raw_profile:
                            if field.startswith(YfncKeymappings.profile_keymap[key]):
                                norm_field = raw_profile[field].replace("%", "").replace("N/A", "")
                                selected_profile_data.update({key: norm_field})

                # Standardized profile with selected fields is now available. Append it to
                # to the list of profiles
                pprint(selected_profile_data)
                profile_list.append(selected_profile_data)
            except IOError:
                print "Profile page for ticker %s does not exist...skipping" % ticker

        # Now list of profiles is available, write it to an intermediate CSV file
        unstd_output_filename = YfncFundpageScraper.insert_suffix(output_file, "__UNSTD__")
        YfncFundpageScraper.writecsv(YfncKeymappings.profile_fields, profile_list, unstd_output_filename)

        # This CSV written in the above step file is unstandardized:
        # It has field values like net_assets = "120M". We need to standardize this and
        # other fields so they are proper numeric format for database ingestion. We use
        # standardize_profiles to do this final cleanup.
        YfncFundpageScraper.standardize_profiles(unstd_output_filename, output_file)

    def get_risk(self, output_file="./_risks.csv"):
        """
        Gets the risk statistics for a mutual fund ticker symbol.
        The function assumes the knowledge of the schema for Yahoo
        finance pages for the give security.
        """
        risk_list = []
        for ticker in self.tickers:
            risk_page = "%s/%s_risk.html" % (self.fundpages_location, ticker)
            try:
                with open(risk_page) as frisk:
                    risk_soup = BeautifulSoup(frisk)
                    risk_tables = risk_soup.findAll("table", class_="yfnc_tableout1")
                    raw_risk = {}

                    # Scrape values of risk fields form the HTML tables and store them in
                    # raw_risk dictionary. This dictionary is "raw" in the sense that
                    # the labelkeys are unstandardized names (with parens, colons etc)
                    # The label keys will be standardized in the next step with the help
                    # of YfncKeymappings.risk_keymaps

                    for table in risk_tables:
                        interval = table.find("td", class_="yfnc_tablehead1").text
                        intervaldata = table.findAll("td", class_="yfnc_tabledata1")
                        assert len(intervaldata) % 3 == 0, \
                            "ticker = %s, len(intervaldata) = %d (should be multiple if 3) " \
                            % (ticker, len(intervaldata))

                        labels = intervaldata[0::3]
                        securitydata_tags = intervaldata[1::3]
                        categorydata_tags = intervaldata[2::3]

                        securitydata = dict(
                            zip(
                                [l.text + "(" + interval + ")__SEC" for l in labels],
                                [s.text for s in securitydata_tags]
                            )
                        )

                        categorydata = dict(
                            zip(
                                [l.text + "(" + interval + ")__CAT" for l in labels],
                                [c.text for c in categorydata_tags]
                            )
                        )

                        raw_risk.update(securitydata)
                        raw_risk.update(categorydata)
                        pprint(raw_risk)

                    # Standardize interesting fields using YfncKeymappings.risk_keymap
                    # and create a nice dictionary for output
                    selected_risk_data = {"ticker": ticker}
                    for key in YfncKeymappings.risk_keymap:
                        for field in raw_risk:
                            if field.startswith(YfncKeymappings.risk_keymap[key]):
                                norm_field = raw_risk[field].replace("N/A", "")
                                selected_risk_data.update({key: norm_field})

                pprint(selected_risk_data)
                risk_list.append(selected_risk_data)
            except IOError:
                print "Risk page for ticker %s does not exist...skipping" % ticker

        # Now list of profiles is available, write it to an intermediate CSV file
        unstd_output_filename = YfncFundpageScraper.insert_suffix(output_file, "__UNSTD__")
        YfncFundpageScraper.writecsv(YfncKeymappings.risk_fields, risk_list, unstd_output_filename)

        # Now list of fund risks is available, write it to a csvfile
        YfncFundpageScraper.standardize_risk(unstd_output_filename, output_file,
                                             range(1, len(YfncKeymappings.risk_fields)))

    def get_performance(self, output_file="./_performance.csv"):
        """
        Gets performance statistics. 1, 3, 5 and 10 yr returns.
        """
        performance_list = []
        for ticker in self.tickers:
            performance_page = "%s/%s_performance.html" % (self.fundpages_location, ticker)
            try:
                with open(performance_page) as fperf:
                    perf_soup = BeautifulSoup(fperf)
                    perf_tables = perf_soup.findAll("table", class_="yfnc_datamodoutline1")

                    # Scrape values of performance fields form the HTML tables and store them in
                    # raw_performance dictionary. This dictionary is "raw" in the sense that
                    # the labelkeys are unstandardized names (with parens, colons etc)
                    # The label keys will be standardized in the next step with the help
                    # of YfncKeymappings.performance_keymaps
                    try:
                        avg_returns = perf_tables[1]
                        intervals = [tag.text for tag in
                                     avg_returns.findAll("td", class_="yfnc_datamodlabel1")]
                        returns = [tag.text for tag in
                                   avg_returns.findAll("td", class_="yfnc_datamoddata1")]
                    except IndexError:
                        # No tables with specified class were found in the HTML
                        intervals = returns = []

                    raw_performance = dict(zip(intervals, returns))

                    # Standardize interesting fields using YfncKeymappings.profile_keymap
                    # and create a nice dictionary for output
                    selected_performance = {"ticker": ticker}
                    for key in YfncKeymappings.performance_keymap:
                        for field in raw_performance:
                            if field.startswith(YfncKeymappings.performance_keymap[key]):
                                # norm field removes "%" and "N/A" characters
                                norm_field = raw_performance[field]\
                                    .replace("%", "") \
                                    .replace("N/A", "")
                                selected_performance.update({key: norm_field})
                pprint(selected_performance)
                performance_list.append(selected_performance)
            except IOError:
                print "Performance page for ticker %s does not exist...skipping" % ticker
        # Now list of fund risks is available, write it to a csvfile
        YfncFundpageScraper.writecsv(YfncKeymappings.performance_fields, performance_list, output_file)

    @staticmethod
    def standardize_profiles(inputfile_name, outputfile_name):
        """
        Standardizes fields so they can be fed to database. This includes making
        sure that the field types are compatible with the types with which the database will
        ingest them. This includes removing commas, "M" and "B" for millions and billions etc.

        The fields are written to the input file in the order of
        yfnc_key_mappings.profile_keymappings

        For net_assets field, removes commas in amounts, if the amount ends in "M" removes "M"
        and converts to float, if the amount ends with "B", removes "B" converts to float and
        and multiplies by 1000.

        @param inputfile_name: filename string
        @type inputfile_name: str
        @param outputfile_name: output file name string
        @type outputfile_name: str
        @rtype: None
        """
        with open(inputfile_name, "rb") as infile, \
                open(outputfile_name, "wb") as outfile:

            reader = csv.reader(infile, delimiter="|")
            writer = csv.writer(outfile, delimiter="|")

            #extract the header and advance the cursor to next row
            header = reader.next()
            writer.writerow(header)

            net_assets_pattern = re.compile("[^\d\-\.MB]")
            turnover_pattern = re.compile("[^\d\-\.]")
            replacement = ""
            for record in reader:
                # Standardize "net_assets" field
                net_assets = record[3]
                net_assets_std = re.sub(net_assets_pattern, replacement, net_assets)
                if net_assets_std.endswith("M"):
                    net_assets_std = float(net_assets_std.replace("M", ""))
                elif net_assets_std.endswith("B"):
                    net_assets_std = 1000.0 * float(net_assets_std.replace("B", ""))
                record[3] = net_assets_std

                # Standardize
                # "sales_load" (record 2)
                # "turnover" (record 9),
                # "turnover_cat" (record 10)

                float_fields = [2, 9, 10]
                for fieldno in float_fields:
                    raw_field = record[fieldno]
                    if raw_field != "":
                        record[fieldno] = float(re.sub(turnover_pattern, replacement, raw_field))

                writer.writerow(record)

    @staticmethod
    def standardize_performance(filename):
            pass

    @staticmethod
    def standardize_risk(inputfile_name, outputfile_name, cols_to_stdize):
        """
        Standardizes risk. Non-numeric characters ("," etc) in fields which are supposed
        to be floats

        @param inputfile_name: filename string
        @type inputfile_name: str
        @param outputfile_name: output file name string
        @type outputfile_name: str
        @param cols_to_stdize: Columns to standardize
        @type cols_to_stdize: list
        """
        with open(inputfile_name, "rb") as infile, \
                open(outputfile_name, "wb") as outfile:
            reader = csv.reader(infile, delimiter="|")
            writer = csv.writer(outfile, delimiter="|")

            # Extract header and write to outputfile
            header = reader.next()
            writer.writerow(header)

            pattern = re.compile("[^\d\.\-]")
            replacement = ""
            for record in reader:
                for col in cols_to_stdize:
                    raw_field = record[col]
                    if raw_field != "":
                        record[col] = float(re.sub(pattern, replacement, raw_field))
                writer.writerow(record)



