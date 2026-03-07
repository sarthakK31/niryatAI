import pandas
import requests
import comtradeapicall
import time

import importlib.metadata
version = importlib.metadata.version("comtradeapicall")
print("comtradeapicall version:", version)

# comtrade api subscription key 
subscription_key = '29387053f432451ca1762717ed244c5f'
directory = 'apidata'  # output directory for downloaded files
proxy_url = '<PROXY URL>'  # optional if you need proxy url

# set some variables
from datetime import date
from datetime import timedelta
today = date.today()
yesterday = today - timedelta(days=1)
lastweek = today - timedelta(days=7)



reporter_codes = [
    "842",
    "156",
    "278",
    "392",
    "826",
    "251",
    "380",
    "643",
    "124",
    "76",
    "724",
    "484",
    "36",
    "410",
    "792",
    "360",
    "528",
    "682",
    "616",
    "757",
    "56",
    "372",
    "752",
    "32",
    "376",
    "702",
    "40",
    "784",
    "764",
    "579",
    "608",
    "50",
    "458",
    "710",
    "170",
    "208",
    "152",
    "246",
    "818",
    "868",
    "586",
    "604",
    "200",
    "642",
    "300",
    "620",
    "554",
    "368",
    "634",
    "414",
]


for code in reporter_codes:
    print(f"Downloading data for reporter code: {code}")
    mydf1 = comtradeapicall.getFinalData(subscription_key, typeCode='C', freqCode='A', clCode='HS', period='2019',
                                    reporterCode=code, cmdCode=None, flowCode='M', partnerCode=None,
                                    partner2Code=None,
                                    customsCode=None, motCode=None, maxRecords=250000, format_output='JSON',
                                    aggregateBy=None, breakdownMode='classic', countOnly=None, includeDesc=True)
    filename = f"./apidata/comtrade_{code}_2019.csv"
    mydf1.to_csv(filename, index=False)
    print(f"Saved: {filename}")

    time.sleep(5)

    mydf2 = comtradeapicall.getFinalData(subscription_key, typeCode='C', freqCode='A', clCode='HS', period='2020',
                                    reporterCode=code, cmdCode=None, flowCode='M', partnerCode=None,
                                    partner2Code=None,
                                    customsCode=None, motCode=None, maxRecords=250000, format_output='JSON',
                                    aggregateBy=None, breakdownMode='classic', countOnly=None, includeDesc=True)
    filename = f"./apidata/comtrade_{code}_2020.csv"
    mydf2.to_csv(filename, index=False)
    print(f"Saved: {filename}")

    time.sleep(5)

    mydf3 = comtradeapicall.getFinalData(subscription_key, typeCode='C', freqCode='A', clCode='HS', period='2021',
                                    reporterCode=code, cmdCode=None, flowCode='M', partnerCode=None,
                                    partner2Code=None,
                                    customsCode=None, motCode=None, maxRecords=250000, format_output='JSON',
                                    aggregateBy=None, breakdownMode='classic', countOnly=None, includeDesc=True)
    filename = f"./apidata/comtrade_{code}_2021.csv"
    mydf3.to_csv(filename, index=False)
    print(f"Saved: {filename}")

    time.sleep(5)
    mydf4 = comtradeapicall.getFinalData(subscription_key, typeCode='C', freqCode='A', clCode='HS', period='2022',
                                    reporterCode=code, cmdCode=None, flowCode='M', partnerCode=None,
                                    partner2Code=None,
                                    customsCode=None, motCode=None, maxRecords=250000, format_output='JSON',
                                    aggregateBy=None, breakdownMode='classic', countOnly=None, includeDesc=True)
    filename = f"./apidata/comtrade_{code}_2022.csv"
    mydf4.to_csv(filename, index=False)
    print(f"Saved: {filename}")

    time.sleep(5)

    mydf5 = comtradeapicall.getFinalData(subscription_key, typeCode='C', freqCode='A', clCode='HS', period='2023',
                                    reporterCode=code, cmdCode=None, flowCode='M', partnerCode=None,
                                    partner2Code=None,
                                    customsCode=None, motCode=None, maxRecords=250000, format_output='JSON',
                                    aggregateBy=None, breakdownMode='classic', countOnly=None, includeDesc=True)
    filename = f"./apidata/comtrade_{code}_2023.csv"
    mydf5.to_csv(filename, index=False)
    print(f"Saved: {filename}")

    time.sleep(5)

    mydf6 = comtradeapicall.getFinalData(subscription_key, typeCode='C', freqCode='A', clCode='HS', period='2024',
                                    reporterCode=code, cmdCode=None, flowCode='M', partnerCode=None,
                                    partner2Code=None,
                                    customsCode=None, motCode=None, maxRecords=250000, format_output='JSON',
                                    aggregateBy=None, breakdownMode='classic', countOnly=None, includeDesc=True)
    filename = f"./apidata/comtrade_{code}_2024.csv"
    mydf6.to_csv(filename, index=False)
    print(f"Saved: {filename}")

    time.sleep(5)