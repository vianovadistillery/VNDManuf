'-INDIVIDUAL PRICING FILE

OPEN "acstk.ip" FOR RANDOM SHARED AS #4 LEN = 128


TYPE RcdFmtIprice
	no AS INTEGER
	item AS INTEGER
	search AS STRING * 5
	iprice AS SINGLE
	date AS STRING * 8
	notes AS STRING * 50
	filler AS STRING * 57
END TYPE

TYPE ArrayFmtIprice
	no AS INTEGER
	item AS INTEGER
	price AS SINGLE
END TYPE

DIM SHARED iprice AS RcdFmtIprice
DIM SHARED iparray AS ArrayFmtIprice


