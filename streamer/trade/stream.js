var streamUrl = "https://streamer.cryptocompare.com/";
var fsym = "BTC";
var tsym = "USD";
var currentSubs;
var dataUrl = "https://min-api.cryptocompare.com/data/subs?fsym=" + fsym + "&tsyms=" + tsym;
var socket = io(streamUrl);

$.getJSON(dataUrl, function(data) {
	currentSubs = data['USD']['CURRENT'];
	socket.emit('SubAdd', { subs: currentSubs });
});

socket.on('m', function(currentData) {
	unpackData(currentData);
});

var unpackData = function(data) {
	var coinfsym = CCC.STATIC.CURRENCY.getSymbol(fsym);
	var cointsym = CCC.STATIC.CURRENCY.getSymbol(tsym) 
	var incomingTrade = CCC.CURRENT.unpack(data);
	var newTrade = {
		Market: incomingTrade['MARKET'],
		Type: incomingTrade['TYPE'],
		ID: incomingTrade['LASTTRADEID'],
		Price: CCC.convertValueToDisplay(cointsym, incomingTrade['PRICE']),
		Quantity: CCC.convertValueToDisplay(coinfsym, incomingTrade['LASTVOLUME']),
		Total: CCC.convertValueToDisplay(cointsym, incomingTrade['LASTVOLUME'] * incomingTrade['PRICE'])
	};

	if (incomingTrade['FLAGS'] == 1) {
		newTrade['Type'] = "SELL";
	}
	else if (incomingTrade['FLAGS'] == 2) {
		newTrade['Type'] = "BUY";
	}
	else if (incomingTrade['MARKET'] == 'LOADCOMPLETE') {
		newTrade.Type = "-";
		newTrade.ID = "-";
		newTrade.Price = "-";
		newTrade.Quantity = "-";
		newTrade.Total = "-";
	}
	else {
		newTrade['Type'] = "UNKNOWN";
	}
	displayData(newTrade);
};

var displayData = function(dataUnpacked) {
	var maxTableSize = 30;
	var length = $('table tr').length;
	$('#trades').after(
		"<tr class="+dataUnpacked.Type+"><th>" + dataUnpacked.Market + "</th><th>" + dataUnpacked.Type + "</th><th>" + dataUnpacked.ID + "</th><th>" + dataUnpacked.Price + "</th><th>" + dataUnpacked.Quantity + "</th><th>" + dataUnpacked.Total + "</th></tr>"
	);

	if (length >= (maxTableSize)) {
		$('table tr:last').remove();
	}
};

$('#unsubscribe').click(function() {
	$('#subscribe').removeClass('subon');
	$(this).addClass('subon');
	$('#stream-text').text('Stream stopped');
	socket.emit('SubRemove', { subs: currentSubs });
});

$('#subscribe').click(function() {
	$('#unsubscribe').removeClass('subon');
	$(this).addClass('subon');
	$('#stream-text').text("Streaming...");
	socket.emit('SubAdd', { subs: currentSubs });
});