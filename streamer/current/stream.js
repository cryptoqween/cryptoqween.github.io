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

var subscription = ['5~CCCAGG~BTC~USD'];

socket.emit('SubAdd', {subs:subscription} );

socket.on("m", function(message){
	var messageType = message.substring(0, message.indexOf("~"));
	var res = {};
	switch(messageType){
			case CCC.STATIC.TYPE.TRADE:
				res = CCC.TRADE.unpack(message);
			break;
			case CCC.STATIC.TYPE.CURRENT:
				res = CCC.CURRENT.unpack(message);
			break;
			case CCC.STATIC.TYPE.CURRENTAGG:
				res = CCC.CURRENT.unpack(message);
				updateQuote(res);
			break;
			case CCC.STATIC.TYPE.ORDERBOOK:
				res = CCC.ORDER.unpack(message);
			break;
			case CCC.STATIC.TYPE.FULLORDERBOOK:
				res = CCC.ORDER.unpack(message);
			break;
		
	}

});

