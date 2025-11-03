'/////////////////////////////////////////////////////////////////////////////
'>>>> Order headers
'/////////////////////////////////////////////////////////////////////////////
SELECT CASE acstkf$
CASE "PRE": OPEN "ordhed.pre" FOR RANDOM SHARED AS #48 LEN = 256
CASE ELSE: OPEN "ordhed.acf" FOR RANDOM SHARED AS #48 LEN = 256
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
	htaxe AS STRING * 12
	hreford AS STRING * 12
	linvnum AS STRING * 12
	ldisc AS STRING * 4
	hsup AS STRING * 5
	hnote1 AS STRING * 42
	hnote2 AS STRING * 42
	hinitials AS STRING * 3
	hscheduled AS STRING * 8
	hstatus AS STRING * 2
	hupdated AS STRING * 8
	filler AS STRING * 74
END TYPE
DIM SHARED ordhed AS RcdFmtordhed
