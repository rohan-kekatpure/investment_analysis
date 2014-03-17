class GfncKeymappings(object):
    """
    Holds mapping between field names in HTML fund pages and the
    names which we want to store in database.
    """
    allocations_keymap = {
        "Cash": "pct_cash",
        "Stocks": "pct_stock",
        "Bonds": "pct_bonds",
        "Preferred": "pct_preferred",
        "Convertible": "pct_convertible",
        "Other": "pct_other"
    }

