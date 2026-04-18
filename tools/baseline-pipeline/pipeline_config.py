from __future__ import annotations

ACTIVE_STORES: dict[str, str] = {
    "6": "Echt",
    "8": "Weert",
    "9": "Stein",
    "11": "Brunssum",
    "12": "Kerkrade",
    "13": "Budel",
    "31": "Tilburg",
    "38": "Tegelen",
}

STORE_NAME_TO_CODE: dict[str, str] = {
    name.lower(): code
    for code, name in ACTIVE_STORES.items()
}

EXCLUDED_STORES: set[str] = {"0", "2", "3", "5", "14", "15", "16", "27", "39", "99"}

STORE_SIZES: dict[str, str] = {
    "11": "groot",
    "12": "groot",
    "6": "groot",
    "8": "groot",
    "38": "groot",
    "9": "middel",
    "31": "middel",
    "13": "klein",
}

STORE_SALES_RANK: dict[str, int] = {
    "8": 1,
    "31": 2,
    "9": 3,
    "6": 4,
    "38": 5,
    "12": 6,
    "13": 7,
    "11": 8,
}

ONE_SIZE_LABEL = "ONE_SIZE"

SIZE_ORDER = ["XXXS", "XXS", "XS", "S", "M", "L", "XL", "XXL", "3XL", "4XL", "XXXL", "XXXXL", ONE_SIZE_LABEL]
