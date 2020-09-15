import datetime
import pandas
import urllib
import json
import time
import sys
import time
import requests
from yahoo_earnings_calendar import YahooEarningsCalendar
import numpy as np
import os
import requests as r 
from influxdb_client import InfluxDBClient, Point, WritePrecision, WriteOptions
import rx
from rx import operators as ops
from collections import OrderedDict


# from influxdb_client.client.write_api import SYNCHRONOUS, PointSettings

def get_income_q(t):
    req = r.get("https://financialmodelingprep.com/api/v3/financials/income-statement/" + t + "?&period=quarter&apikey=6ef5e882b2142973ec6ff102347afc29")
    return json.loads(req.text)
    

def get_balancesheets_q(t):
    req = r.get("https://financialmodelingprep.com/api/v3/financials/balance-sheet-statement/" + t + "?&period=quarter&apikey=6ef5e882b2142973ec6ff102347afc29")
    return json.loads(req.text)


def get_cashflow_q(t):
    req = r.get("https://financialmodelingprep.com/api/v3/financials/cash-flow-statement/" + t + "?&period=quarter&apikey=6ef5e882b2142973ec6ff102347afc29")
    return json.loads(req.text)


def get_ev_q(t):
    req = r.get("https://financialmodelingprep.com/api/v3/enterprise-value/" + t + "?&period=quarter&apikey=6ef5e882b2142973ec6ff102347afc29")
    return json.loads(req.text)


def get_metrics_q(t):
    req = r.get("https://financialmodelingprep.com/api/v3/company-key-metrics/" + t + "?&period=quarter&apikey=6ef5e882b2142973ec6ff102347afc29")
    return json.loads(req.text)

def get_comp_profile(t):
    req = r.get("https://financialmodelingprep.com/api/v3/company/profile/" + t + "?&apikey=6ef5e882b2142973ec6ff102347afc29")
    return json.loads(req.text)


def get_valuation(t):
    metric_data_q = get_metrics_q(t)['metrics'][0]
    income_data_q = get_income_q(t)['financials'][0]
    profile_data_q = get_comp_profile(t)['profile']
    balance_data_q = get_balancesheets_q(t)['financials'][0]
    value_metrics =  {
                "ticker": t,
                "price": profile_data_q['price'],
                "p_e": metric_data_q["PE ratio"],
                "p_b": metric_data_q["PB ratio"],
                "p_s": metric_data_q["Price to Sales Ratio"],
                "sharesoutsanding": income_data_q['Weighted Average Shs Out'],
                "eps": income_data_q["EPS"], 
                "net_debt": balance_data_q['Net Debt'],
                "ncavps": (float(balance_data_q['Total current assets']) - float(balance_data_q['Total current liabilities'])) / float(income_data_q['Weighted Average Shs Out']),
                "debt_to_asset": metric_data_q['Debt to Assets'],
                "p_eps":float(profile_data_q['price']) /  float(income_data_q["EPS"]),
                "gross_profit": income_data_q["Gross Margin"],
                "revenue_earnings": float(income_data_q['Net Income']) / float(balance_data_q["Total shareholders equity"])
            }
    
    return value_metrics

def get_data(url):
	req = urllib.request.Request(url)
	response = urllib.request.urlopen(req)
	file = response.read()
	result = json.loads(file)
	result = pandas.DataFrame([result])
	return result



token = "B0d4WO3O60UArIrFbSGP5CggG9GwDjGxdTIEB4fTOWJyOFzk0HR8URTvJ4Ofj7fLYiigK8JucVA_smrMSUQV2Q=="

org = "wfclark5@gmail.com"

bucket = "financial-analysis"

client = InfluxDBClient(url="https://eastus-1.azure.cloud2.influxdata.com", token=token, org=org)

today = datetime.date.today()

path = os.getcwd()

today = datetime.date.today()

path = os.getcwd()

base = datetime.datetime.today()

date_calendar = [base + datetime.timedelta(days=x) for x in range(7)]

date_from = date_calendar[0].date()

date_to = date_calendar[-1].date()

yec = YahooEarningsCalendar()

earnings = yec.earnings_between(date_from, date_to)

earnings = json.dumps(earnings)

earnings = json.loads(earnings)

eps_df = pandas.DataFrame.from_records(earnings)

# point_settings = PointSettings(**{"type": "weekly"})

# write_api = client.write_api(write_options=SYNCHRONOUS, point_settings=point_settings)

write_api = client.write_api()

val_df = []

for i in range(1):
    stats = {}
    ticker = eps_df['ticker'].loc[i]
    stats["measurement"] = 'valuation'
    stats["Date"] = base.strftime("%Y-%m-%d") 
    stats= get_valuation(ticker)
    print(stats)
    data = Point("financial-analysis").tag("ticker", stats.get("ticker")).field("price", float(stats.get("price"))).field("p_e", float(stats.get("p_e"))).field("p_b", float(stats.get("p_b"))).field("p_s", float(stats.get("p_s"))).field("sharesoutsanding", float(stats.get("sharesoutsanding"))).field("eps", float(stats.get("eps"))).field("net_debt", float(stats.get("net_debt"))).field("ncavps", float(stats.get("ncavps"))).field("debt_to_asset", float(stats.get("debt_to_asset"))).field("p_eps", float(stats.get("p_eps"))).field("gross_profit", float(stats.get("gross_profit"))).field("revenue_earnings" , float(stats.get("revenue_earnings")))
    write_api.write(record=data, bucket=bucket, org=org)
    break

write_api.__del__()

query = '''from(bucket:"financial-analysis")
            |> range(start: 0, stop: now())'''

result = client.query_api().query_data_frame(query=query, org=org)

print(result)
