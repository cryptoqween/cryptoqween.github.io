# CryptoCompare API Tutorial
These examples show how you can use the CryptoCompare API.

Read official UPDATED documentation [here](https://min-api.cryptocompare.com/).

## Content

### Streamer API
1. [Trade streamer example](https://cryptoqween.github.io/streamer/trade/)
2. [Current streamer example](https://cryptoqween.github.io/streamer/current/)


## Notes
1. The Total Volume in USD is calculated using:
```
[(total volume across all coins in BTC - total volume for BTC/USD pair) * current BTC/USD Price] + direct volumeto BTC-USD
```
This is to give a closer approximation of the total volume in USD as the price will change over the period giving a different value. It is important to note that this is the best approximation for the total volume in USD but is NOT an exact solution.

2. ccc-streamer-utilities.js file should be included in your project to get utility functions and fields.
