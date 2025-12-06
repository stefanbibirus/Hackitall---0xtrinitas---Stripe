# test.py
from anaf_api import get_companies_info, get_financial_info, get_cui

cui=get_cui(["ENRON COMMERCE ONLINE"])
date=get_companies_info(cui)
date_fin=get_financial_info(cui)
print(date)
print(date_fin)