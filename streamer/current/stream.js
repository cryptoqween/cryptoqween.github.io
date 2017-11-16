$(document).ready(function() {

	var currentPrice = {};
	var socket = io.connect('https://streamer.cryptocompare.com/');
	//Format: {SubscriptionId}~{ExchangeName}~{FromSymbol}~{ToSymbol}
	//Use SubscriptionId 0 for TRADE, 2 for CURRENT and 5 for CURRENTAGG
	//For aggregate quote updates use CCCAGG as market
	var subscription = ['11~BTC']; //, '5~CCCAGG~BTC~USD', '5~CCCAGG~ETH~USD', '2~Coinbase~BTC~USD', '0~Coinbase~BTC~USD', '11~ETH', '11~CCCAGG~BTC~USD', 'JPX', '9ROCKSTAR'];
	socket.emit('SubAdd', { subs: subscription });
	socket.on("m", function(message) {
		console.log(message);
		/*var messageType = message.substring(0, message.indexOf("~"));
		var res = {};
		if (messageType == CCC.STATIC.TYPE.CURRENTAGG) {
			res = CCC.CURRENT.unpack(message);
			dataUnpack(res);
		}*/
	});

	var dataUnpack = function(data) {
		var from = data['FROMSYMBOL'];
		var to = data['TOSYMBOL'];
		var fsym = CCC.STATIC.CURRENCY.getSymbol(from);
		var tsym = CCC.STATIC.CURRENCY.getSymbol(to);
		var pair = from + to;

		if (!currentPrice.hasOwnProperty(pair)) {
			currentPrice[pair] = {};
		}

		for (var key in data) {
			currentPrice[pair][key] = data[key];
		}

		if (currentPrice[pair]['LASTTRADEID']) {
			currentPrice[pair]['LASTTRADEID'] = parseInt(currentPrice[pair]['LASTTRADEID']).toFixed(0);
		}
		currentPrice[pair]['CHANGE24HOUR'] = CCC.convertValueToDisplay(tsym, (currentPrice[pair]['PRICE'] - currentPrice[pair]['OPEN24HOUR']));
		currentPrice[pair]['CHANGE24HOURPCT'] = ((currentPrice[pair]['PRICE'] - currentPrice[pair]['OPEN24HOUR']) / currentPrice[pair]['OPEN24HOUR'] * 100).toFixed(2) + "%";;
		displayData(currentPrice[pair], from, tsym, fsym);
	};

	var decorateWithFullVolume = function() {

	}

	var displayData = function(current, from, tsym, fsym) {
		var priceDirection = current.FLAGS;
		var fields = CCC.CURRENT.DISPLAY.FIELDS;

		for (var key in fields) {
			if (fields[key].Show) {
				switch (fields[key].Filter) {
					case 'String':
						$('#' + key + '_' + from).text(current[key]);
						break
					case 'Number':
						var symbol = fields[key].Symbol == 'TOSYMBOL' ? tsym : fsym;
						$('#' + key + '_' + from).text(CCC.convertValueToDisplay(symbol, current[key]))
						break
				}
			}
		}

		$('#PRICE_' + from).removeClass();
		if (priceDirection & 1) {
			$('#PRICE_' + from).addClass("up");
		}
		else if (priceDirection & 2) {
			$('#PRICE_' + from).addClass("down");
		}

		if (current['PRICE'] > current['OPEN24HOUR']) {
			$('#CHANGE24HOURPCT_' + from).removeClass();
			$('#CHANGE24HOURPCT_' + from).addClass("pct-up");
		}
		else if (current['PRICE'] < current['OPEN24HOUR']) {
			$('#CHANGE24HOURPCT_' + from).removeClass();
			$('#CHANGE24HOURPCT_' + from).addClass("pct-down");
		}
	};
});