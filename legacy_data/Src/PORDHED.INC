'/////////////////////////////////////////////////////////////////////////////
'>>>> Order headers
'/////////////////////////////////////////////////////////////////////////////
SELECT CASE acstkf$
CASE "PRE": OPEN "pordhed.pre" FOR RANDOM SHARED AS #48 LEN = 256
CASE ELSE: OPEN "pordhed.acf" FOR RANDOM SHARED AS #48 LEN = 256
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
	hstatus AS STRING * 1
	hreford AS STRING * 15
	linvnum AS STRING * 12
	ldisc AS STRING * 4
	hsup AS STRING * 5
	hnote1 AS STRING * 42
	hnote2 AS STRING * 42
	hinitials AS STRING * 3
	hdocket AS STRING * 10
	hdddate AS STRING * 8
	hinvdate AS STRING * 8
	hdolrecd AS STRING * 4
	filler AS STRING * 62
END TYPE
DIM SHARED ordhed AS RcdFmtordhed
