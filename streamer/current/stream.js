$(document).ready(function() {

	var socket = io.connect('https://streamer.cryptocompare.com/');
	//Format: {SubscriptionId}~{ExchangeName}~{FromSymbol}~{ToSymbol}
	//Use SubscriptionId 0 for TRADE, 2 for CURRENT and 5 for CURRENTAGG
	//For aggregate quote updates use CCCAGG as market
	var subscription = ['5~CCCAGG~BTC~USD', '5~CCCAGG~ETH~USD'];
	socket.emit('SubAdd', { subs: subscription });
	socket.on("m", function(message) {
		dataUnpack(message);
	});

	var dataUnpack = function(message) {

		var newPrice = CCC.CURRENT.unpack(message);
		var from = newPrice['FROMSYMBOL'];
		var fsym = CCC.STATIC.CURRENCY.getSymbol(from);
		var to = newPrice['TOSYMBOL'];
		var tsym = CCC.STATIC.CURRENCY.getSymbol(to);
		var current = {};

		for (var key in newPrice) {
			current[key] = newPrice[key];
			if (key == 'LASTVOLUMETO' || key == 'VOLUME24HOURTO') {
				current[key] = CCC.convertValueToDisplay(tsym, newPrice[key]);
			}
			else if (key == 'LASTVOLUME' || key == 'VOLUME24HOUR' || key == 'OPEN24HOUR' || key == 'OPENHOUR' || key == 'HIGHHOUR' || key == 'LOWHOUR' || key == 'LOW24HOUR') {
				current[key] = CCC.convertValueToDisplay(fsym, newPrice[key]);
			}
		}

		if (current['HIGH24HOUR']) {
			current.CHANGE = CCC.convertValueToDisplay(fsym, (current['PRICE'] - current['HIGH24HOUR']));
			current.CHANGEPCT = ((current['PRICE'] - current['HIGH24HOUR']) / current['HIGH24HOUR'] * 100).toFixed(2) + "%";
			current.HIGH24HOUR = CCC.convertValueToDisplay(fsym, current.HIGH24HOUR);
		}

		if (current['LASTTRADEID']) {
			current['LASTTRADEID'] = newPrice['LASTTRADEID'].toFixed(0);
		}

		displayData(current, from);
	};

	var displayData = function(current, from) {

		var direction = current.FLAGS;

		for (var key in current) {
			if (key == 'CHANGEPCT') {
				$('#' + key + '_' + from).text(' (' + current[key] + ')');
			}
			else {
				$('#' + key + '_' + from).text(current[key]);
			}
		}

		$('#PRICE_' + from).removeClass();

		if (direction == 1) {
			$('#PRICE_' + from).addClass("up");
		}
		else if (direction == 2) {
			$('#PRICE_' + from).addClass("down");
		}
	};
});