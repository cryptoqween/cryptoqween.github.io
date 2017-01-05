var quote = {};

var displayQuote = function(_quote) {

	var fsym = CCC.STATIC.CURRENCY.SYMBOL[_quote.FROMSYMBOL];
	var tsym = CCC.STATIC.CURRENCY.SYMBOL[_quote.TOSYMBOL];

	document.getElementById("market").innerHTML = _quote.LASTMARKET;
	document.getElementById("fsym").innerHTML = _quote.FROMSYMBOL;
	document.getElementById("tsym").innerHTML = _quote.TOSYMBOL;
	document.getElementById("price").innerHTML = _quote.PRICE;
	document.getElementById("volume").innerHTML = CCC.convertValueToDisplay(fsym, _quote.LASTVOLUME);
	document.getElementById("volumeto").innerHTML = CCC.convertValueToDisplay(tsym, _quote.LASTVOLUMETO);
	document.getElementById("24volume").innerHTML = CCC.convertValueToDisplay(fsym, _quote.VOLUME24HOUR);	
	document.getElementById("24volumeto").innerHTML = CCC.convertValueToDisplay(tsym, _quote.VOLUME24HOURTO);
	document.getElementById("tradeid").innerHTML = _quote.LASTTRADEID.toFixed(0);

	if (quote.FLAGS === "1"){
		document.getElementById("price").className = "up";
	} 
	else if (quote.FLAGS === "2") {
		document.getElementById("price").className = "down";
	}
	else if (quote.FLAGS === "4") {
		document.getElementById("price").className = "";
	}
}

var updateQuote = function(result) {

	var keys = Object.keys(result);

	for (var i = 0; i <keys.length; ++i) {
		quote[keys[i]] = result[keys[i]];
	}

	displayQuote(quote);
}

var socket = io.connect('https://streamer.cryptocompare.com/');

//Format: {SubscriptionId}~{ExchangeName}~{FromSymbol}~{ToSymbol}
//Use SubscriptionId 0 for TRADE, 2 for CURRENT and 5 for CURRENTAGG
//For aggregate quote updates use CCCAGG as market
var subscription = ['5~CCCAGG~BTC~USD'];

socket.emit('SubAdd', {subs:subscription} );

socket.on("m", function(message){
	var messageType = message.substring(0, message.indexOf("~"));
	var res = {};
	if (messageType === CCC.STATIC.TYPE.CURRENTAGG) {
		res = CCC.CURRENT.unpack(message);
		console.log(res);
		updateQuote(res);
	}						
});

