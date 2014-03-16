import csv
import os

class AbstractScraper(object):
    """
    Super class for yahoo and google finance scraper classes
    """
    # Utility method for writing CSV files
    @staticmethod
    def writecsv(csvfields, funddata, outputfile):
        """
        @param csvfields: fieldnames in the funddata dictionary
        @type csvfields: list
        @param funddata: list of dicts containing data
        @type funddata: list (of dicts)
        @param outputfile: output file name
        @type outputfile: str
        """
        with open(outputfile, "wb") as f:
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
        Constructs abstract page scraper object.
        @param fundpages_location: Location of downloaded html fund pages (string)
        @type fundpages_location: str
        @param tickerlist_file: Location of csv file containing ticker symbol list
        @type tickerlist_file: str
        @param delimiter: delimiter in tickerlist_file
        @type delimiter: str
        """
        self.fundpages_location = fundpages_location
        assert os.path.exists(self.fundpages_location), \
            "[AbstractScraper] Folder %s does not exist" % self.fundpages_location

        assert os.path.exists(tickerlist_file), \
            "[AbstractScraper] Folder %s does not exist" % tickerlist_file

        # Generate list of tickers from tickerlist_file and store in self.tickers
        with open(tickerlist_file, "rb") as f:
            reader = csv.reader(f, delimiter=delimiter)
            self.tickers = [record[0] for record in reader]
