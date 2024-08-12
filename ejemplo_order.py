""" Ejemplo de una posicion abierta

[{'adl': '1', 'availPos': '16.5', 'avgPx': '60346.5', 'baseBal': '', 'baseBorrowed': '', 'baseInterest': '', 'bePx': '60415.92084603453', 'bizRefId': '', 'bizRefType': '', 'cTime': '1723230709343', 'ccy': 'USDT', 'clSpotInUseAmt': '', 'closeOrderAlgo': [], 'deltaBS': '', 'deltaPA': '', 'fee': '-0.497858625', 'fundingFee': '-0.1491539875899736', 'gammaBS': '', 'gammaPA': '', 'idxPx': '60346.6', 'imr': '', 'instId': 'BTC-USDT-SWAP', 'instType': 'SWAP', 'interest': '', 'last': '60347.5', 'lever': '1', 'liab': '', 'liabCcy': '', 'liqPenalty': '0', 'liqPx': '9.180497851849454', 'margin': '995.5680960124100264', 'markPx': '60349.6', 'maxSpotInUseAmt': '', 'mgnMode': 'isolated', 'mgnRatio': '222.18893603782877', 'mmr': '3.9830736', 'notionalUsd': '996.296157252', 'optVal': '', 'pendingCloseOrdLiabVal': '', 'pnl': '0', 'pos': '16.5', 'posCcy': '', 'posId': '1702124423656050688', 'posSide': 'long', 'quoteBal': '', 'quoteBorrowed': '', 'quoteInterest': '', 'realizedPnl': '-0.6470126125899736', 'spotInUseAmt': '', 'spotInUseCcy': '', 'thetaBS': '', 'thetaPA': '', 'tradeId': '1132863035', 'uTime': '1723363200374', 'upl': '0.051149999999976', 'uplLastPx': '0.0165', 'uplRatio': '0.0000513700048883', 'uplRatioLastPx': '0.000016570969319', 'usdPx': '', 'vegaBS': '', 'vegaPA': ''}]

    # Paso el json por un json viewer para verlo mejor. El que yo uso es https://jsonformatter.curiousconcept.com/#
    "adl":"1",
    "availPos":"16.5",
    "avgPx":"60346.5",
    "baseBal":"",
    "baseBorrowed":"",
    "baseInterest":"",
    "bePx":"60415.92084603453",
    "bizRefId":"",
    "bizRefType":"",
    "cTime":"1723230709343",
    "ccy":"USDT",
    "clSpotInUseAmt":"",
    "closeOrderAlgo":[

    ],
    "deltaBS":"",
    "deltaPA":"",
    "fee":"-0.497858625",
    "fundingFee":"-0.1491539875899736",
    "gammaBS":"",
    "gammaPA":"",
    "idxPx":"60346.6",
    "imr":"",
    "instId":"BTC-USDT-SWAP",
    "instType":"SWAP",
    "interest":"",
    "last":"60347.5",
    "lever":"1",
    "liab":"",
    "liabCcy":"",
    "liqPenalty":"0",
    "liqPx":"9.180497851849454",
    "margin":"995.5680960124100264",
    "markPx":"60349.6",
    "maxSpotInUseAmt":"",
    "mgnMode":"isolated",
    "mgnRatio":"222.18893603782877",
    "mmr":"3.9830736",
    "notionalUsd":"996.296157252",
    "optVal":"",
    "pendingCloseOrdLiabVal":"",
    "pnl":"0",
    "pos":"16.5",
    "posCcy":"",
    "posId":"1702124423656050688",
    "posSide":"long",
    "quoteBal":"",
    "quoteBorrowed":"",
    "quoteInterest":"",
    "realizedPnl":"-0.6470126125899736",
    "spotInUseAmt":"",
    "spotInUseCcy":"",
    "thetaBS":"",
    "thetaPA":"",
    "tradeId":"1132863035",
    "uTime":"1723363200374",
    "upl":"0.051149999999976",
    "uplLastPx":"0.0165",
    "uplRatio":"0.0000513700048883",
    "uplRatioLastPx":"0.000016570969319",
    "usdPx":"",
    "vegaBS":"",
    "vegaPA":""

    De esta posicion me sirve para este bot:
    - instId: id del instrumento  (BTC-USDT-SWAP)
    - posSide: long o short  (long o short)
    - avgPx: precio promedio de la apertura
    - markPx: last mark price
    - fee: fee
    - lever: leverage
    - margin: margen o colateral
    - notionalUsd: notional en usd

    Otros datos que podrian ser utiles:
    - upl: profit and loss no realizado con el mark price
    - uplRatio: profit and loss no realizado en porcentaje con el mark price
    - uplLastPx: profit and loss no realizado en el ultimo precio con el last price
    - uplRatioLastPx: profit and loss no realizado en el ultimo precio en porcentaje con el last price
    - realizedPnl: profit and loss realizado
"""

""" Ejemplo de una orden market:
    {'code': '0',
    'data': [{'accFillSz': '1',
           'algoClOrdId': '',
           'algoId': '',
           'attachAlgoClOrdId': '',
           'attachAlgoOrds': [],
           'avgPx': '60413.1',
           'cTime': '1723387670831',
           'cancelSource': '',
           'cancelSourceReason': '',
           'category': 'normal',
           'ccy': '',
           'clOrdId': 'test',
           'fee': '-0.03020655',
           'feeCcy': 'USDT',
           'fillPx': '60413.1',
           'fillSz': '1',
           'fillTime': '1723387670831',
           'instId': 'BTC-USDT-SWAP',
           'instType': 'SWAP',
           'isTpLimit': 'false',
           'lever': '1.0',
           'linkedAlgoOrd': {'algoId': ''},
           'ordId': '1707426359926136832',
           'ordType': 'market',
           'pnl': '0',
           'posSide': 'long',
           'px': '',
           'pxType': '',
           'pxUsd': '',
           'pxVol': '',
           'quickMgnType': '',
           'rebate': '0',
           'rebateCcy': 'USDT',
           'reduceOnly': 'false',
           'side': 'buy',
           'slOrdPx': '',
           'slTriggerPx': '',
           'slTriggerPxType': '',
           'source': '',
           'state': 'filled',
           'stpId': '',
           'stpMode': 'cancel_maker',
           'sz': '1',
           'tag': '',
           'tdMode': 'isolated',
           'tgtCcy': '',
           'tpOrdPx': '',
           'tpTriggerPx': '',
           'tpTriggerPxType': '',
           'tradeId': '1134416981',
           'uTime': '1723387670833'}],
    'msg': ''}

    De aca me sirve para este bot:
    - instId: id del instrumento  (BTC-USDT-SWAP)
    - posSide: long o short  (long o short)
    - side: buy o sell
    - avgPx: precio promedio de la apertura
    - fee: fee
    - lever: leverage
    - sz: size de la orden
    - state: estado de la orden
    - tradeId: id de la orden

"""

""" Ejemplo de orden de cierre

    {'code': '0',
    'data': [{'accFillSz': '1',
           'algoClOrdId': '',
           'algoId': '',
           'attachAlgoClOrdId': '',
           'attachAlgoOrds': [],
           'avgPx': '59087.8',
           'cTime': '1723414079787',
           'cancelSource': '',
           'cancelSourceReason': '',
           'category': 'normal',
           'ccy': '',
           'clOrdId': 'test123',
           'fee': '-0.0295439',
           'feeCcy': 'USDT',
           'fillPx': '59087.8',
           'fillSz': '1',
           'fillTime': '1723414079788',
           'instId': 'BTC-USDT-SWAP',
           'instType': 'SWAP',
           'isTpLimit': 'false',
           'lever': '1',
           'linkedAlgoOrd': {'algoId': ''},
           'ordId': '1708312497444429824',
           'ordType': 'market',
           'pnl': '-0.02283',
           'posSide': 'long',
           'px': '',
           'pxType': '',
           'pxUsd': '',
           'pxVol': '',
           'quickMgnType': '',
           'rebate': '0',
           'rebateCcy': 'USDT',
           'reduceOnly': 'true',
           'side': 'sell',
           'slOrdPx': '',
           'slTriggerPx': '',
           'slTriggerPxType': '',
           'source': '',
           'state': 'filled',
           'stpId': '',
           'stpMode': 'cancel_maker',
           'sz': '1',
           'tag': '',
           'tdMode': 'isolated',
               'tgtCcy': '',
               'tpOrdPx': '',
               'tpTriggerPx': '',
               'tpTriggerPxType': '',
               'tradeId': '1135191789',
               'uTime': '1723414079789'}],
            'msg': ''}

    De aca me sirve para este bot:
    - instId: id del instrumento  (BTC-USDT-SWAP)
    - posSide: long o short  (long o short)
    - side: buy o sell
    - avgPx: precio promedio del cierre
    - fee: fee

"""
