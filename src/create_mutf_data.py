import csv
from pprint import pprint
import re
import string

from bs4 import BeautifulSoup

from ticker_generator import TickerGenerator


def get_profile(tkr):
    """
    Gets mutual fund data for fidelity mutual funds given a ticker symbol list.
    """
    profile_filename = "../html_full/%s_profile.html" % tkr
    with open(profile_filename) as fprofile:
        profile_soup = BeautifulSoup(fprofile)
        title_tables = profile_soup.findAll("table", class_="yfnc_mod_table_title1")
        string_translations = string.maketrans("", "")
        string_deletions = ":\n"
        raw_profile = {"ticker": tkr}
        for table in title_tables:
            data_table = table.findNextSibling()

            labels = data_table.findAll("td", class_="yfnc_datamodlabel1")
            labelkeys = [re.sub("[ ]+", "", l.text
                                .encode("ascii")
                                .translate(string_translations, string_deletions))
                         for l in labels]

            values = data_table.findAll("td", class_="yfnc_datamoddata1")
            labelvals = [v.text for v in values]
            raw_profile.update(dict(zip(labelkeys, labelvals)))

        # Pick interesting data after standardizing key names of interest
        keymappings = {
            "ticker": "ticker",
            "turnover": "AnnualHoldingsTurnover",
            "turnover_cat": "AverageforCategory",
            "prospectus_net_expense_ratio": "ProspectusNetExpenseRatio",
            "sales_load": "MaxFrontEndSalesLoad",
            "inception": "FundInceptionDate",
            "12b1_fees": "Max12b1Fee",
            "net_assets": "NetAssets",
            "ar_expense_ratio": "AnnualReportExpenseRatio(net)",
            "family": "FundFamily",
            "gross_expense_ratio": "ProspectusGrossExpenseRatio"
        }

        selected_profile_data = dict()
        for key in keymappings:
            for field in raw_profile:
                if field.startswith(keymappings[key]):
                    norm_field = raw_profile[field] \
                        .replace("%", "") \
                        .replace("N/A", "")
                    selected_profile_data.update({key: norm_field})

    print selected_profile_data
    return selected_profile_data


def get_risk(tkr):
    """
    Gets the risk statistics for a mutual fund ticker symbol.
    The function assumes the knowledge of the schema for Yahoo
    finance pages for the give security.
    """
    risk_filename = "../html_full/%s_risk.html" % tkr
    with open(risk_filename) as frisk:
        risk_soup = BeautifulSoup(frisk)
        risk_tables = risk_soup.findAll("table", class_="yfnc_tableout1")

        raw_risk_data = dict()

        for table in risk_tables:
            interval = table.find("td", class_="yfnc_tablehead1").text
            intervaldata = table.findAll("td", class_="yfnc_tabledata1")
            assert len(intervaldata) % 3 == 0, \
                "ticker = %s, len(intervaldata) = %d (should be multiple if 3) " \
                % (tkr, len(intervaldata))

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

            raw_risk_data.update(securitydata)
            raw_risk_data.update(categorydata)
        key_mappings = {"alpha3": "Alpha (against Standard Index)(3 Years)__SEC",
                        "alpha5": "Alpha (against Standard Index)(5 Years)__SEC",
                        "alpha10": "Alpha (against Standard Index)(10 Years)__SEC",
                        "alpha3_cat": "Alpha (against Standard Index)(3 Years)__CAT",
                        "alpha5_cat": "Alpha (against Standard Index)(5 Years)__CAT",
                        "alpha10_cat": "Alpha (against Standard Index)(10 Years)__CAT",
                        "treynor3": "Treynor Ratio(3 Years)__SEC",
                        "treynor5": "Treynor Ratio(5 Years)__SEC",
                        "treynor10": "Treynor Ratio(10 Years)__SEC",
                        "treynor3_cat": "Treynor Ratio(3 Years)__CAT",
                        "treynor5_cat": "Treynor Ratio(5 Years)__CAT",
                        "treynor10_cat": "Treynor Ratio(10 Years)__CAT",
                        "beta3": "Beta (against Standard Index)(3 Years)__SEC",
                        "beta5": "Beta (against Standard Index)(5 Years)__SEC",
                        "beta10": "Beta (against Standard Index)(10 Years)__SEC",
                        "beta3_cat": "Beta (against Standard Index)(3 Years)__CAT",
                        "beta5_cat": "Beta (against Standard Index)(5 Years)__CAT",
                        "beta10_cat": "Beta (against Standard Index)(10 Years)__CAT",
                        "sd3": "Standard Deviation(3 Years)__SEC",
                        "sd5": "Standard Deviation(5 Years)__SEC",
                        "sd10": "Standard Deviation(10 Years)__SEC",
                        "sd3_cat": "Standard Deviation(3 Years)__CAT",
                        "sd5_cat": "Standard Deviation(5 Years)__CAT",
                        "sd10_cat": "Standard Deviation(10 Years)__CAT",
                        "sharpe3": "Sharpe Ratio(3 Years)__SEC",
                        "sharpe5": "Sharpe Ratio(5 Years)__SEC",
                        "sharpe10": "Sharpe Ratio(10 Years)__SEC",
                        "sharpe3_cat": "Sharpe Ratio(3 Years)__CAT",
                        "sharpe5_cat": "Sharpe Ratio(5 Years)__CAT",
                        "sharpe10_cat": "Sharpe Ratio(10 Years)__CAT"
        }
        selected_risk_data = {"ticker": tkr}
        for key in key_mappings:
            for field in raw_risk_data:
                if field.startswith(key_mappings[key]):
                    norm_field = raw_risk_data[field].replace("N/A", "")
                    selected_risk_data.update({key: norm_field})

    return selected_risk_data


def get_performance(tkr):
    """
    Gets performance statistics. 3, 5, 10 yr returns.
    """
    perf_filename = "../html_full/%s_performance.html" % tkr
    with open(perf_filename) as fperf:
        perf_soup = BeautifulSoup(fperf)
        perf_tables = perf_soup.findAll("table", class_="yfnc_datamodoutline1")

        try:
            avg_returns = perf_tables[1]
            intervals = [tag.text for tag in
                         avg_returns.findAll("td", class_="yfnc_datamodlabel1")]
            returns = [tag.text for tag in
                       avg_returns.findAll("td", class_="yfnc_datamoddata1")]
        except IndexError:
            # No tables with specified class were found in the HTML
            intervals = returns = []

        raw_performance_data = dict(zip(intervals, returns))
        keymappings = {"R1": "1-Year",
                       "R3": "3-Year",
                       "R5": "5-Year",
                       "R10": "10-Year"
        }
        selected_performance_data = {"ticker": tkr}
        for k in keymappings:
            for field in raw_performance_data:
                if field.startswith(keymappings[k]):
                    # norm field removes "%" and "N/A" characters
                    norm_field = raw_performance_data[field] \
                        .replace("%", "") \
                        .replace("N/A", "")
                    selected_performance_data.update({k: norm_field})
    return selected_performance_data


def generate_data_file(profile_field_list, fund_list, generator_fn, output_filename):
    with open(output_filename, "wb") as f:
        writer = csv.DictWriter(f, fieldnames=profile_field_list,
                                delimiter='|',
                                quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()

        for fund in fund_list:
            p = generator_fn(fund)
            writer.writerow(p)
            pprint(p)


def standardize_profile(inputfile_name, outputfile_name):
    """
    Standardizes fields so they can be fed to database. This includes making
    sure that the field types are compatible with the types with which the database will
    ingest them. This includes removing commas, "M" and "B" for millions and billions etc.

    The fields are written to the input file in the following order:
    profile_fields = [0: "ticker",
                      1: "family",
                      2: "sales_load",
                      3: "net_assets",
                      4: "prospectus_net_expense_ratio",
                      5: "gross_expense_ratio",
                      6: "ar_expense_ratio",
                      7: "inception",
                      8: "12b1_fees",
                      9: "turnover",
                      10: "turnover_cat"]

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

            # Standardize assets under management
            net_assets = record[3]
            net_assets_std = re.sub(net_assets_pattern, replacement, net_assets)
            if net_assets_std.endswith("M"):
                net_assets_std = float(net_assets_std.replace("M", ""))
            elif net_assets_std.endswith("B"):
                net_assets_std = 1000.0 * float(net_assets_std.replace("B", ""))
            record[3] = net_assets_std

            # Standardize
            # sales_load (record 2)
            # turnover (record 9),
            # turnover_cat (record 10)

            floatlike_fields = [2, 9, 10]
            for fieldno in floatlike_fields:
                raw_field = record[fieldno]
                if raw_field != "":
                    record[fieldno] = float(re.sub(turnover_pattern, replacement, raw_field))

            writer.writerow(record)


def standardize_performance(filename):
        pass


def standardize_risk(inputfile_name, outputfile_name, cols_to_stdize):
    """
    Standardizes risk
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


def main():
    td = TickerGenerator(downloads_folder="../test_ticker_downloader")
    td.download_marketwatch_ticker_pages("http://www.marketwatch.com/tools/mutual-fund/list/")
    td.extract_marketwatch_tickers("../csv/test_ticker_list.csv")

    download_fund_pages("../marketwatch_mutf_tickers/marketwatch_ticker_list.csv",
                        delimiter="|")

    # # Generate list of tickers
    # with open("../marketwatch_mutf_tickers/marketwatch_ticker_list.csv", "rb") as f:
    #     reader = csv.reader(f, delimiter="|")
    #     tickers = [record[0] for record in reader]
    #     # print tickers[:10]

    # # Generate CSV file for profile data
    profile_fields = ["ticker", "family", "sales_load", "net_assets",
                      "prospectus_net_expense_ratio", "gross_expense_ratio",
                      "ar_expense_ratio", "inception", "12b1_fees",
                      "turnover", "turnover_cat"]
    # generate_data_file(profile_fields, tickers, get_profile, "../csv/fund_profiles.csv")
    # standardize_profile("../csv/fund_profiles.csv", "../csv/fund_profiles_std.csv")

    # # Generate CSV file for performance data
    performance_fields = ["ticker", "R1", "R3", "R5", "R10"]
    # generate_data_file(performance_fields, tickers, get_performance, "../csv/fund_performance.csv")

    # # Generate CSV file for risk
    risk_fields = ["ticker",
                   "sharpe3", "sharpe5", "sharpe10",
                   "sharpe3_cat", "sharpe5_cat", "sharpe10_cat",
                   "treynor3", "treynor5", "treynor10",
                   "treynor3_cat", "treynor5_cat", "treynor10_cat",
                   "alpha3", "alpha5", "alpha10",
                   "alpha3_cat", "alpha5_cat", "alpha10_cat",
                   "beta3", "beta5", "beta10",
                   "beta3_cat", "beta5_cat", "beta10_cat",
                   "sd3", "sd5", "sd10",
                   "sd3_cat", "sd5_cat", "sd10_cat"
                   ]
    # generate_data_file(risk_fields, tickers, get_risk, "../csv/fund_risk.csv")
    # standardize_risk("../csv/fund_risk.csv", "../csv/fund_risk_std.csv", range(1, len(risk_fields)))


if __name__ == "__main__":
    main()
    # pass