import urllib.request
import json
import datetime
from datetime import timedelta
import pandas as pd
import time

def getJSONfromURL(url):
	with urllib.request.urlopen(url) as response:
		str_response = response.read().decode('utf-8')
		data = json.loads(str_response)
		return data

def getBTCAggHistoDay(_ccy):
	url = 'https://min-api.cryptocompare.com/data/histominute?fsym=BTC&tsym='+ _ccy +'&limit=600'
	data = getJSONfromURL(url)
	return data['Data']

def getFixerDayUSD(_currencies):
	closingdate = datetime.date.today()
	fxData = []
	for i in range(1,2):
		closingdate = closingdate - timedelta(days=1)
		closing = closingdate.strftime("%Y-%m-%d")
		url = 'http://api.fixer.io/' + closing + '?base=USD'
		data = getJSONfromURL(url)
		current = {}
		current['date'] = closing
		current['time'] = int(time.mktime(datetime.datetime.strptime(closing, "%Y-%m-%d").timetuple()))
		for ccy in _currencies:
			current[ccy] = data['rates'][ccy]		
		fxData.append(current)
	df = pd.DataFrame(fxData)
	return df

def getCloseBTCTable(_currencies):
	close_btc = pd.DataFrame()
	_currencies.append('USD')
	for ccy in _currencies:
		btc_ccy = getBTCAggHistoDay(ccy)
		df = pd.DataFrame(btc_ccy)
		df_close = df[['time', 'close']]
		df_close.columns = ['time', ccy]
		if len(close_btc.columns) < 1:
			close_btc[ccy] = df_close[ccy]
			close_btc['time'] = df['time']			
		else:
			close_btc = close_btc.merge(df_close, on='time', how='inner')
	_currencies.pop()
	return close_btc

def calcConversionTable(_currencies, btc_df, fiat_df):
	row = btc_df.shape[0]
	fiat_df = fiat_df.append([fiat_df]*(row-1), ignore_index=True)
	conversion_df = btc_df[currencies]/(fiat_df[currencies])
	conversion_df['time'] = btc_df['time']
	conversion_df['USD'] = btc_df['USD']
	print(conversion_df)
	return conversion_df

currencies = ['CNY', 'JPY', 'INR', 'EUR', 'GBP']
currenciesfull = ['CNY', 'JPY', 'INR', 'EUR', 'GBP', 'USD']

close_btc = getCloseBTCTable(currencies)
fiat = getFixerDayUSD(currencies)
conversion_close = calcConversionTable(currencies, close_btc, fiat)
conversion_close.to_csv('conversion.csv')
rolling_7day = conversion_close[currenciesfull].rolling(60).mean().dropna()
rolling_30day = conversion_close[currenciesfull].rolling(600).mean().dropna()

def calcMatrix(df):
	matrix = []
	for ccy1 in currenciesfull:
		row = []
		for ccy2 in currenciesfull:
			diff = df[ccy1].tail(1) - df[ccy2].tail(1)
			row.extend(diff)
		matrix.append(row)
	df_matrix =  pd.DataFrame(matrix)
	df_matrix.columns = currenciesfull
	return matrix

def calcMatrixHeatMap(df):
	matrix = {'from': [], 'to':[], 'diff':[], 'formatted':[], 'percent':[]}
	for ccy1 in currenciesfull:
		for ccy2 in currenciesfull:
			diff = (df[ccy1].tail(1) - df[ccy2].tail(1)).values[0]
			percent = (diff/df[ccy2].tail(1)).values[0]*100
			matrix['diff'].append(diff)
			matrix['formatted'].append("{0:.2f}".format(diff))
			matrix['percent'].append("{0:.2f}".format(percent) + '%')
			matrix['from'].append(ccy1)
			matrix['to'].append(ccy2)
	df_matrix =  pd.DataFrame(matrix)
	return df_matrix

prem_last = calcMatrixHeatMap(conversion_close)
prem_7day = calcMatrixHeatMap(rolling_7day)
prem_30day = calcMatrixHeatMap(rolling_30day)

from bokeh.layouts import row
from bokeh.plotting import figure, show, output_file
from bokeh.charts import HeatMap, bins, output_file, show
from bokeh.palettes import RdBu, magma
from bokeh.models import ColumnDataSource, LabelSet, Label

output_file("ccy-premium.html", title="BTC premia")

dateToDisplay = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

hm1 = HeatMap(prem_last, x='from', y='to', values='diff', title=dateToDisplay+' Premia Last Minute Closing (USD). diff = from - to, % = (from - to)/to', stat=None, palette=['green', 'gray', 'red'], legend=False)
source1 = ColumnDataSource(data=prem_last)
labels1a = LabelSet(x='from', y='to', text='formatted', level='glyph', x_offset=-15, y_offset=-10, render_mode='canvas', source=source1)
labels1b = LabelSet(x='from', y='to', text='percent', level='glyph', x_offset=-15, y_offset=-30, render_mode='canvas', source=source1)
hm1.add_layout(labels1a)
hm1.add_layout(labels1b)

hm2 = HeatMap(prem_7day, x='from', y='to', values='diff', title=dateToDisplay+' Premia Last 10 minutes average (USD)', stat=None, palette=['green', 'gray', 'red'], legend=False)
source2 = ColumnDataSource(data=prem_7day)
labels2a = LabelSet(x='from', y='to', text='formatted', level='glyph', x_offset=-15, y_offset=-10, render_mode='canvas', source=source2)
labels2b = LabelSet(x='from', y='to', text='percent', level='glyph', x_offset=-15, y_offset=-30, render_mode='canvas', source=source2)
hm2.add_layout(labels2a)
hm2.add_layout(labels2b)

hm3 = HeatMap(prem_30day, x='from', y='to', values='diff', title=dateToDisplay+' Premia last 60 minutes average (USD)', stat=None, palette=['green', 'gray', 'red'], legend=False)
source3 = ColumnDataSource(data=prem_30day)
labels3a = LabelSet(x='from', y='to', text='formatted', level='glyph', x_offset=-15, y_offset=-10, render_mode='canvas', source=source3)
labels3b = LabelSet(x='from', y='to', text='percent', level='glyph', x_offset=-15, y_offset=-30, render_mode='canvas', source=source3)
hm3.add_layout(labels3a)
hm3.add_layout(labels3b)

show(row(hm1, hm2, hm3)) 



