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

def getBTCAggHistoDay(_exchange):
    url = 'https://min-api.cryptocompare.com/data/histoday?fsym=BTC&tsym=USD&limit=100&e='+ _exchange
    print(url)
    data = getJSONfromURL(url)
    return data['Data']

def getCloseBTCTable(_exchanges):
	close_btc = pd.DataFrame()
	for ex in _exchanges:
		btc_ex = getBTCAggHistoDay(ex)
		df = pd.DataFrame(btc_ex)
		df_close = df[['time', 'close']]
		df_close.columns = ['time', ex]
		if len(close_btc.columns) < 1:
			close_btc[ex] = df_close[ex]
			close_btc['time'] = df['time']			
		else:
			close_btc = close_btc.merge(df_close, on='time', how='inner')
	return close_btc

exchanges=['Bitfinex', 'Coinbase', 'Bitstamp','Poloniex', 'BTCE', 'Gemini', 'OKCoin', 'Kraken']

close_btc = getCloseBTCTable(exchanges)
close_btc.to_csv('exchange_close.csv')
rolling_7day = close_btc[exchanges].rolling(7).mean().dropna()
rolling_30day = close_btc[exchanges].rolling(30).mean().dropna()

def calcMatrix(df):
	matrix = []
	for ex1 in exchanges:
		row = []
		for ex2 in exchanges:
			diff = df[ex1].tail(1) - df[ex2].tail(1)
			row.extend(diff)
		matrix.append(row)
	df_matrix =  pd.DataFrame(matrix)
	df_matrix.columns = exchanges
	return matrix

def calcMatrixHeatMap(df):
	matrix = {'from': [], 'to':[], 'diff':[], 'formatted':[], 'percent':[]}
	for ex1 in exchanges:
		for ex2 in exchanges:
			diff = (df[ex1].tail(1) - df[ex2].tail(1)).values[0]
			percent = (diff/df[ex2].tail(1)).values[0]*100
			matrix['diff'].append(diff)
			matrix['formatted'].append("{0:.2f}".format(diff))
			matrix['percent'].append("{0:.2f}".format(percent) + '%')
			matrix['from'].append(ex1)
			matrix['to'].append(ex2)
	df_matrix =  pd.DataFrame(matrix)
	return df_matrix

prem_last = calcMatrixHeatMap(close_btc)
prem_7day = calcMatrixHeatMap(rolling_7day)
prem_30day = calcMatrixHeatMap(rolling_30day)

from bokeh.layouts import row
from bokeh.plotting import figure, show, output_file
from bokeh.charts import HeatMap, bins, output_file, show
from bokeh.palettes import RdBu, magma
from bokeh.models import ColumnDataSource, LabelSet, Label

output_file("index.html", title="BTC premia")

dateToDisplay = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

custompalette = ['#00814c', '#1ebd7c', '#26cc88', '#3ee09e', '#71ffc5', 'grey','#fcffc8', '#ffeb66', '#ffca49', '#ff9600', '#d00031']

hm1 = HeatMap(prem_last, x='from', y='to', values='diff', title=dateToDisplay+' Premia Last Closing (USD). diff = from - to, % = (from - to)/to', stat=None, palette=custompalette, legend=False)
source1 = ColumnDataSource(data=prem_last)
#labels1a = LabelSet(x='from', y='to', text='formatted', level='glyph', x_offset=-10, y_offset=-10, render_mode='canvas', source=source1, text_font_size='9pt')
labels1b = LabelSet(x='from', y='to', text='percent', level='glyph', x_offset=-10, y_offset=-10, render_mode='canvas', source=source1, text_font_size='9pt')
#hm1.add_layout(labels1a)
hm1.add_layout(labels1b)

hm2 = HeatMap(prem_7day, x='from', y='to', values='diff', title=dateToDisplay+' Premia 7 days average (USD)', stat=None, palette=custompalette, legend=False)
source2 = ColumnDataSource(data=prem_7day)
#labels2a = LabelSet(x='from', y='to', text='formatted', level='glyph', x_offset=-10, y_offset=-10, render_mode='canvas', source=source2, text_font_size='9pt')
labels2b = LabelSet(x='from', y='to', text='percent', level='glyph', x_offset=-10, y_offset=-10, render_mode='canvas', source=source2, text_font_size='9pt')
#hm2.add_layout(labels2a)
hm2.add_layout(labels2b)

hm3 = HeatMap(prem_30day, x='from', y='to', values='diff', title=dateToDisplay+' Premia 30 days average (USD)', stat=None, palette=custompalette, legend=False)
source3 = ColumnDataSource(data=prem_30day)
#labels3a = LabelSet(x='from', y='to', text='formatted', level='glyph', x_offset=-10, y_offset=-10, render_mode='canvas', source=source3, text_font_size='9pt')
labels3b = LabelSet(x='from', y='to', text='percent', level='glyph', x_offset=-10, y_offset=-10, render_mode='canvas', source=source3, text_font_size='9pt')
#hm3.add_layout(labels3a)
hm3.add_layout(labels3b)

show(row(hm1, hm2, hm3)) 



