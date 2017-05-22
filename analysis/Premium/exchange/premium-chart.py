import json, requests
import pandas as pd
from datetime import datetime, timedelta
import dateutil.parser
import time
import numpy as np

def formatHeader(df, pair):
	cols = df.columns
	newcols = []
	for index in cols:
		if (index == 'time'):
			newcols.append(index)
		else:
			newcols.append(index + '_' + pair)
	return newcols

def getMinuteData(tsym, exchange):
	currentTS = str(int(time.time()))
	allData = []
	for i in range(1,6):
		url = 'https://min-api.cryptocompare.com/data/histominute?fsym=BTC&tsym='+ tsym +'&limit=2000&aggregate=1&e='+ exchange +'&toTs=' + currentTS
		print(url)
		resp = requests.get(url=url)
		data = json.loads(resp.text)
		dataSorted = sorted(data['Data'], key=lambda k: int(k['time']))
		allData += dataSorted
		currentTS = str(dataSorted[0]['time'])
	df = pd.DataFrame(allData)
	df = df.drop_duplicates()
	df = df.sort(columns=['time'], ascending=[1])
	df.to_csv('BTC'+ tsym + '_minute.csv')
	pair = 'BTC' + tsym
	df.columns = formatHeader(df, pair)
	return df

def getTSFromDateString(x):
	date = dateutil.parser.parse(x)
	return int(time.mktime(date.timetuple()))

conversion = pd.read_csv('exchange_close.csv')
#news_dates = ['2017-01-04', '2017-01-10', '2017-01-24', '2017-02-08']
#news_dates = list(map(getTSFromDateString, news_dates))
#x_news_dates = np.array(news_dates, dtype=np.datetime64)
#news_items = ['The PBoC warns citizens about the risks of using Bitcoin and warns exchanges to bear in mind regulations of the state.', 'The PBoC announces the formation of a task force to inspect Bitcoin trading platforms.', 'The PBoC announces that their task force will look to focus on payment and settlement, AML and forex management, information and financial security along with other matters', 'The PBoC announces a closed meeting with 9 chinese exchanges behind closed doors.The Chinese exchanges announce the immediate ban of bitcoin and litecoin withdrawals with Yuan RMB withdrawals unaffected.']
#news_prices = [1248.604854, 924.901938, 906.5488218, 1095.667203]


#plotting
import bokeh
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import column, row

from bokeh.models import LinearAxis, Range1d
from bokeh.models import ColumnDataSource, LabelSet, Label
from bokeh.models.glyphs import ImageURL

def formatChart(v):
	v.title.text_color = "white"
	v.xaxis.axis_label_text_color = "white"
	v.yaxis.axis_label_text_color = "white"
	v.border_fill_color = '#232933'
	v.min_border_left = 100
	v.min_border_right = 100
	v.xgrid.grid_line_color = 'white'
	v.xgrid.grid_line_alpha = 0.5
	v.xgrid.grid_line_dash = [6, 4]
	v.ygrid.grid_line_color = 'white'
	v.ygrid.grid_line_alpha = 0.5
	v.ygrid.grid_line_dash = [6, 4]
	v.xaxis.axis_line_color = "white"
	v.yaxis.axis_line_color = "white"
	v.xaxis.major_label_text_color = "white"
	v.yaxis.major_label_text_color = "white"
	v.background_fill_color = '#232933'
	v.xaxis.minor_tick_line_color = "white"
	v.yaxis.minor_tick_line_color = "white"
	v.legend.border_line_width = 0
	v.legend.border_line_color = None
	v.legend.background_fill_color = None
	v.legend.label_text_color = "white"
	v.toolbar_sticky = False
	return v

def getPriceChart(x_dates, y1, y2, ccy):
	title = "BTC Trading Prices USD vs " + ccy + ". Source: CryptoCompare"
	ccypair = "BTC" + ccy
	p = figure(title=title, x_axis_label='Date', y_axis_label='USD', plot_width=1000, plot_height=500, x_axis_type="datetime")	
	p.line(x_dates, y1, line_color="#ffaa0c", line_width=2, legend=ccypair)
	p.line(x_dates, y2, line_color="white", line_width=2, legend="BTCUSD")
	p = formatChart(p)
	
	source = ColumnDataSource(dict(
 	url = ['ccc-logo.png'],
    x  = [x_dates[0]],
    y  = [y1[0]]
	))

	image = ImageURL(url="url", x="x", y="y", w=100, h=100, anchor="center")
	p.add_glyph(source, image)
	return p

def getPremiumChart(x_dates, y, diff, ccy):
	title = "BTC Trading Premium USD vs " + ccy
	ccypair = "BTC" + ccy
	v = figure(title=title, x_axis_label='Date', y_axis_label='USD', plot_width=1000, plot_height=500, x_axis_type="datetime", y_range=(-120, 120))
	v.image_url(url=['ccc-logo.png'], x=0, y=1)
	limit = np.zeros(len(diff))
	band_x = np.append(x_dates, x_dates[::-1])
	band_y = np.append(diff, limit[::-1])
	v.patch(band_x, band_y, color='white', fill_alpha=0.2)
	v.line(x_dates, diff, line_color="white", legend="Premium vs USD")
	v.extra_y_ranges = {"price": Range1d(start=400, end=1400)}
	v.line(x_dates, y, line_color="#ffaa0c", line_width=2, legend=ccypair, y_range_name="price")
	v.add_layout(LinearAxis(y_range_name="price"), 'right')
	v = formatChart(v)
	return v

output_file("btc-trading.html")
dates = conversion["time"].apply(lambda x: datetime.fromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S'))
x_dates = np.array(dates, dtype=np.datetime64)

#CNY
p1 = getPriceChart(x_dates, conversion['Kraken'], conversion['Bitfinex'], "Kraken")
p2 = getPriceChart(x_dates, conversion['BTCE'], conversion['Coinbase'], "BTCE")

#source = ColumnDataSource(data=dict(date=x_news_dates, price=news_prices, news=news_items))

diff1 = conversion['Kraken'] - conversion['Bitfinex'] 
p3 = getPremiumChart(x_dates, conversion['Kraken'], diff1, 'Kraken')
diff2 = conversion['BTCE'] - conversion['Coinbase'] 
p4 = getPremiumChart(x_dates, conversion['BTCE'], diff2, 'BTCE')
#p1.scatter(x='date', y='price', size=10, color='white', source=source)

#news = LabelSet(x='date', y='price', text='news', level='glyph', x_offset=20, y_offset=50, render_mode='canvas', source=source , border_line_color='white', border_line_alpha=1.0,
                 #background_fill_color='white', background_fill_alpha=1.0)

#p1.add_layout(news)

show(column(p1, p2, p3, p4))

