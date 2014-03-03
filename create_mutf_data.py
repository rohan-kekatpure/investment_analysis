import csv
from pprint import pprint
from BeautifulSoup import BeautifulSoup
import os
import re
import string

import requests
import shutil


def download_marketwatch_mutf_symbol_pages():
    """
    We want to decouple downloading of fund ticker web pages from
    their scraping. Too many programmatic hits to morningstar is likely
    to get us banned for an interval of time; so we download the HTMLs
    containing ticker symbols and _then_ scrape the HTMLs to extract
    <ticker>:<name> key-value pairs.

    To ensure clean download, this function creates
    "./marketwatch_mutf_tickers" folder to store the HTMLs if the folder
    doesnt exist already. If it exists, the folder tree is deleted and
    recreated.

    In a typical situation, this function should be run once at the start of
    the data gathering pipeine.
    """

    marketwatch_download_folder = "./marketwatch_mutf_tickers"
    if os.path.exists(marketwatch_download_folder):
        shutil.rmtree(marketwatch_download_folder)
        os.makedirs(marketwatch_download_folder)
    else:
        os.makedirs(marketwatch_download_folder)

    marketwatch_url_base = "http://www.marketwatch.com/tools/mutual-fund/list/"

    for startletter in string.ascii_uppercase:
        marketwatch_url = marketwatch_url_base + startletter
        print "downloading %s..." % (marketwatch_url)
        response = requests.get(marketwatch_url)
        with open(marketwatch_download_folder + "/" + startletter + ".html", "w") as f:
            f.write(response.content)


def generate_marketwatch_tickers():
    """
    This function, scrapes ticker HTMLs in "./marketwatch_mutf_tickers" and generates
    <ticker>:<name> key-value pairs and writes it as a DSV file.
    """
    # Generate a regex pattern to match mutual funds. Ticker ymbols are anywhere between
    # UPPERCASE 2-5 characters

    pattern = re.compile("/[A-Z]{2,5}")
    marketwatch_download_folder = "./marketwatch_mutf_tickers"
    assert os.path.exists(marketwatch_download_folder), \
        "Folder %s does not exist" % marketwatch_download_folder

    tickerlist_file = "%s/%s" % (marketwatch_download_folder,
                                 "marketwatch_ticker_list.csv")
    with open(tickerlist_file, "w") as f:
        for startletter in string.ascii_uppercase:
            html_filepath = "%s/%s.html" % (marketwatch_download_folder, startletter)
            soup = BeautifulSoup(open(html_filepath).read())
            fundname_tags = soup.findAll("td", class_="quotelist-name")
            fundnames = [tag.text for tag in fundname_tags]
            fundtickers = [re.findall(pattern, tag.find("a").attrs["href"])[0][1:]
                           for tag in fundname_tags]
            for ticker, name in zip(fundtickers, fundnames):
                print "%s:%s" % (ticker, name)
                f.write("%s|%s\n" % (ticker, name))


def download_fund_page(ticker):
    """
    Downloads profile, performance and risk pages for a mutual fund with symbol 'ticker'
    from Yahoo Finance.
    @type ticker: str
    @param ticker: Ticker symbol
    @return: None
    """
    profileurl = "http://finance.yahoo.com/q/pr?s=" + ticker
    performanceurl = "http://finance.yahoo.com/q/pm?s=" + ticker
    riskurl = "http://finance.yahoo.com/q/rk?s=" + ticker

    urls = {"profile": profileurl,
            "performance": performanceurl,
            "risk": riskurl}
    for kind in urls:
        response = requests.get(urls[kind])
        filename = "./html/%s_%s.html" % (ticker, kind)
        with open(filename, "w") as f:
            f.write(response.content)


def download_fund_pages(csvfile, delimiter="|"):
    """
    Reads records from the supplied delimited file, extracts ticker symbol and passes
    on to download_fund_page(ticker) for the actual download task
     @param: None
     @return: None
    """
    download_folder = "./html"
    if os.path.exists(download_folder):
        shutil.rmtree(download_folder)
        os.makedirs(download_folder)
    else:
        os.makedirs(download_folder)

    ticker_reader = csv.reader(open(csvfile, "rb"), delimiter=delimiter)
    for ticker, name in ticker_reader:
        print "downloading %s: %s..." % (ticker, name)
        download_fund_page(ticker)


# def download_morningstar_tickers():
#     """
#     Generate list of all fidelity mutual fund names
#     """
#     soup = BeautifulSoup(open("./fidelity_funds.html"))
#     pattern = re.compile("t=[A-Z]{5}")
#
#     #Mutual fund information is contained in td tags with class = "msNormal"
#     mtf_list = soup.find_all("td", class_="msNormal")
#     fundtags = [mf.find("a") for mf in mtf_list]
#     fundnames = [l.text for l in fundtags]
#     fundlinks = [t["href"].lstrip() for t in fundtags]
#     fundtickers = [re.findall(pattern, l)[0].split("=")[1] for l in fundlinks]
#     return dict(zip(fundtickers, fundnames))


def get_profile(tkr):
    """
    Gets mutual fund data for fidelity mutual funds given a ticker symbol list.
    """
    profile_filename = "./html/%s_profile.html" % tkr
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
                    norm_field = raw_profile[field]\
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
    risk_filename = "./html/%s_risk.html" % tkr
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
    perf_filename = "./html/%s_performance.html" % tkr
    with open(perf_filename) as fperf:
        perf_soup = BeautifulSoup(fperf)
        perf_tables = perf_soup.findAll("table", class_="yfnc_datamodoutline1")

        avg_returns = perf_tables[1]
        intervals = [tag.text for tag in
                     avg_returns.findAll("td", class_="yfnc_datamodlabel1")]
        returns = [tag.text for tag in
                   avg_returns.findAll("td", class_="yfnc_datamoddata1")]

        raw_performance_data = dict(zip(intervals, returns))
        keymappings = {"R1": "1-Year",
                        "R3": "3-Year",
                        "R5": "5-Year",
                        "R10": "10-Year"
                        }
        selected_performance_data = {"ticker": tkr}
        translations = string.maketrans("", "")
        for k in keymappings:
            for field in raw_performance_data:
                if field.startswith(keymappings[k]):
                    # norm field removes "%" and "N/A" characters
                    norm_field = raw_performance_data[field] \
                                    .replace("%", "") \
                                    .replace("N/A", "")
                    selected_performance_data.update({k: norm_field})
    return selected_performance_data


def generate_data_file(profile_field_list, fund_list, generator_fn,  filename):
    with open(filename, "wb") as f:
        writer = csv.DictWriter(f, fieldnames=profile_field_list,
                                delimiter='|',
                                quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()

        for fund in fund_list:
            p = generator_fn(fund)
            writer.writerow(p)
            pprint(p)


def main():
    # download_marketwatch_mutf_symbol_pages()
    # generate_marketwatch_tickers()
    download_fund_pages("./marketwatch_mutf_tickers/marketwatch_ticker_list.csv",
                        delimiter="|")

    # funds = download_morningstar_tickers()
    # # download_fund_pages(funds.keys())
    #
    # # Generate CSV file for profile data
    # profile_fields = ["ticker", "family", "sales_load", "net_assets",
    #                   "prospectus_net_expense_ratio", "gross_expense_ratio",
    #                   "ar_expense_ratio", "inception", "12b1_fees",
    #                   "turnover", "turnover_cat"]
    # generate_data_file(profile_fields, funds, get_profile, "./fund_profiles.csv")
    #
    # # Generate CSV file for performance data
    # performance_fields = ["ticker", "R1", "R3", "R5", "R10"]
    # generate_data_file(performance_fields, funds, get_performance, "./fund_performance.csv")
    #
    # # Generate CSV file for risk
    # risk_fields = ["ticker",
    #                "sharpe3", "sharpe5", "sharpe10",
    #                "sharpe3_cat", "sharpe5_cat", "sharpe10_cat",
    #                "treynor3", "treynor5", "treynor10",
    #                "treynor3_cat", "treynor5_cat", "treynor10_cat",
    #                "alpha3", "alpha5", "alpha10",
    #                "alpha3_cat", "alpha5_cat", "alpha10_cat",
    #                "beta3", "beta5", "beta10",
    #                "beta3_cat", "beta5_cat", "beta10_cat",
    #                "sd3", "sd5", "sd10",
    #                "sd3_cat", "sd5_cat", "sd10_cat"
    #                ]
    #
    # generate_data_file(risk_fields, funds, get_risk, "./fund_risk.csv")

if __name__ == "__main__":
    # main()
    pass