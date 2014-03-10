# import csv
# from pprint import pprint
# import re
# import string
# from bs4 import BeautifulSoup
# from ticker_generator import TickerGenerator
#
#
# def main():
#     td = TickerGenerator(downloads_folder="../test_ticker_downloader")
#     td.download_marketwatch_ticker_pages("http://www.marketwatch.com/tools/mutual-fund/list/")
#     td.extract_marketwatch_tickers("../csv/test_ticker_list.csv")
#
#     download_fund_pages("../marketwatch_mutf_tickers/marketwatch_ticker_list.csv",
#                         delimiter="|")
#
#
#     # # Generate CSV file for profile data
#     profile_fields = ["ticker", "family", "sales_load", "net_assets",
#                       "prospectus_net_expense_ratio", "gross_expense_ratio",
#                       "ar_expense_ratio", "inception", "12b1_fees",
#                       "turnover", "turnover_cat"]
#     # generate_data_file(profile_fields, tickers, get_profile, "../csv/fund_profiles.csv")
#     # standardize_profiles("../csv/fund_profiles.csv", "../csv/fund_profiles_std.csv")
#
#     # # Generate CSV file for performance data
#
#     # generate_data_file(performance_fields, tickers, get_performance, "../csv/fund_performance.csv")
#
#     # # Generate CSV file for risk
#     # generate_data_file(risk_fields, tickers, get_risk, "../csv/fund_risk.csv")
#     # standardize_risk("../csv/fund_risk.csv", "../csv/fund_risk_std.csv", range(1, len(risk_fields)))
#
#
# if __name__ == "__main__":
#     main()
#     # pass