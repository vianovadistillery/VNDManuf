'///////////////////////////////////////////////////////////////////
'/////  A S S E T    R E G I S T E R
'///////////////////////////////////////////////////////////////////////

TYPE RcdFmtassets
    no AS INTEGER
    key AS STRING * 4
    name AS STRING * 35
    desc AS STRING * 35
    suplr AS STRING * 35
    purdate AS STRING * 8
    purcost AS SINGLE
    finance AS STRING * 35
    depreciation AS SINGLE
    calibreq AS STRING * 1
    disposaldate AS STRING * 8
    date AS STRING * 8

END TYPE
DIM SHARED Assets AS RcdFmtassets
OPEN "ASSETS.dat" FOR RANDOM SHARED AS #61 LEN = LEN(Assets)

