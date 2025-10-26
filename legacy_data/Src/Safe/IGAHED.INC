'/////////////////////////////////////////////////////////////////////////////
'>>>> Order headers
'/////////////////////////////////////////////////////////////////////////////
SELECT CASE acstkf$
CASE "PRE": OPEN "igahed.pre" FOR RANDOM SHARED AS #48 LEN = 320
CASE ELSE: OPEN "igahed.acf" FOR RANDOM SHARED AS #48 LEN = 320
END SELECT

TYPE RcdFmtordhed
	hord AS STRING * 2
	hrrn AS STRING * 2
	hfiller AS STRING * 2
	hdate AS STRING * 8
	hordq AS STRING * 4
	hdollar AS STRING * 4
	hinvq AS STRING * 4
	hitems AS STRING * 2
	horgq AS STRING * 4
	htaxe AS STRING * 8
        fillera AS STRING * 1
	hreford AS STRING * 15
	linvnum AS STRING * 12
	ldisc AS STRING * 4
	hsup AS STRING * 5
	hnote1 AS STRING * 42
	hnote2 AS STRING * 42
	hinitials AS STRING * 3
        hpname1 AS STRING * 30
        hpname2 AS STRING * 30
        hpname3 AS STRING * 30	
        hpname4 AS STRING * 25
        hdeposit AS STRING * 4  ' total amount on deposit
        ldepnum AS STRING * 12
        hdepnew AS STRING * 4  ' new amount
        filler AS STRING * 21
END TYPE
DIM SHARED ordhed AS RcdFmtordhed

