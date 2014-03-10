class YfncKeymappings:
    """
    Holds mapping between field names in HTML fund pages and the
    names which we want to store in database.

    For example, holdings turnover is referred to by "AnnualHoldingsTurnover".
    We want to store it just as "turnover". We need to know "AnnualHoldingsTurnover"
    for the scraping part, but then we refer to the keymapping to store the value of
    "AnnualHoldingsTurnover" as "turnover"
    """

    profile_keymap = {
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

    profile_fields = [
        "ticker", "family", "sales_load", "net_assets",
        "prospectus_net_expense_ratio", "gross_expense_ratio",
        "ar_expense_ratio", "inception", "12b1_fees",
        "turnover", "turnover_cat"
    ]

    risk_keymap = {
        "alpha3": "Alpha (against Standard Index)(3 Years)__SEC",
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

    risk_fields = [
        "ticker",
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

    performance_keymap = {
        "R1": "1-Year",
        "R3": "3-Year",
        "R5": "5-Year",
        "R10": "10-Year"
    }

    performance_fields = ["ticker", "R1", "R3", "R5", "R10"]

