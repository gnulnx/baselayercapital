conda activate blc


# To fetch historical data and distribution data and save in Dynamo use this:
python fetch_symbol_div_info.py --ticker MSTY
python fetch_symbol_div_info.py --ticker IMST
...


# This will run the current best simulator code
python btc_msty_rolling_loans.py   


# This will test the google sheet
python src/python/scripts/test_sheet.py