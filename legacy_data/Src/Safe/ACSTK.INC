'-ACSTK ACCESSORY STOCK FILE
SELECT CASE acstkf$
CASE "NEW": OPEN "acstk.new" FOR RANDOM SHARED AS #3 LEN = 256
CASE "PRE": OPEN "acstk.pre" FOR RANDOM SHARED AS #3 LEN = 256
CASE ELSE: OPEN "acstk.acf" FOR RANDOM SHARED AS #3 LEN = 256
END SELECT

TYPE RcdFmtacstk
	'Product Description
	no AS INTEGER
	search AS STRING * 10
	ean13 AS CURRENCY
	desc1 AS STRING * 25
	desc2 AS STRING * 10
	suplr AS STRING * 5
	size AS STRING * 3
	unit AS STRING * 2
	pack AS INTEGER
	dgflag AS STRING * 1
	form AS STRING * 4
	pkge AS INTEGER
	label AS INTEGER
	manu AS INTEGER
	active AS STRING * 1
	
	'Finalcial Description
	taxinc AS STRING * 1
	salestaxcde AS STRING * 1
	purcost AS SINGLE
	purtax AS SINGLE
	wholesalecost AS SINGLE
	disccdeone AS STRING * 1
	disccdetwo AS STRING * 1
	
	wholesalecde AS STRING * 1
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

	'Stock holding
	cogs AS SINGLE
	gpc AS SINGLE
	rmc AS SINGLE
	gpr AS SINGLE
	soh  AS INTEGER
	sohv AS SINGLE
	sip AS INTEGER
	soo AS INTEGER
	sold AS INTEGER
	date AS STRING * 8
	
	'Filler
	bulk AS SINGLE
	lid AS INTEGER
	pbox AS INTEGER
	boxlbl AS INTEGER


	filler AS STRING * 69


END TYPE
DIM SHARED acstk AS RcdFmtacstk
DIM SHARED acstk4cost AS RcdFmtacstk

