'-ACSTK ACCESSORY STOCK FILE
SELECT CASE acstkf$
CASE "NEW": OPEN "acstk.new" FOR RANDOM SHARED AS #3 LEN = 160
CASE "PRE": OPEN "acstk.pre" FOR RANDOM SHARED AS #3 LEN = 160
CASE ELSE: OPEN "acstk.acf" FOR RANDOM SHARED AS #3 LEN = 160
END SELECT

TYPE RcdFmtacstk
	no AS INTEGER
	search AS STRING * 10
	desc1 AS STRING * 25
	desc2 AS STRING * 10
	suplr AS STRING * 5
	size AS STRING * 3
	unit AS STRING * 2
	pack AS INTEGER
	dgflag AS STRING * 1
	taxinc AS STRING * 1
	salestaxcde AS STRING * 1
	purcost AS SINGLE
	purtax AS SINGLE
	disccdeone AS STRING * 1
	disccdetwo AS STRING * 1
	wholesalecost AS SINGLE
	filler4 AS STRING * 4
	'wholesale-tax AS SINGLE
	retailcde AS STRING * 1
	countercde AS STRING * 1
	tradecde AS STRING * 1
	contractcde AS STRING * 1
	industrialcde AS STRING * 1
	distributorcde AS STRING * 1

	retail AS SINGLE
	counter AS SINGLE
	trade AS SINGLE
	contract AS SINGLE
	industrial AS SINGLE
	distributor AS SINGLE

	suplr4stdcost AS STRING * 5
	search4stdcost AS STRING * 10
	filler9 AS STRING * 7
	'retail-tax AS SINGLE
	'counter-tax AS SINGLE
	'trade-tax AS SINGLE
	'contract-tax AS SINGLE
	'industrial-tax AS SINGLE
	'distributor-tax AS SINGLE
	soo AS INTEGER
	soh  AS INTEGER
	active AS STRING * 1
	sold AS INTEGER
	date AS STRING * 8
	wholesalecde AS STRING * 1
	ean13 AS CURRENCY
	filler AS STRING * 4
END TYPE
DIM SHARED acstk AS RcdFmtacstk
DIM SHARED acstk4cost AS RcdFmtacstk

