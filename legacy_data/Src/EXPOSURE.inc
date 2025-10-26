'////////////////////////////////////////////////////////////////////
'>>>>>> Exposure Panels
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

OPEN "Exposure.DAT" FOR RANDOM SHARED AS #71 LEN = 1024

TYPE RcdFmtExposure
	no AS INTEGER
	rack AS STRING * 1
	row AS STRING * 1
	col AS STRING * 1
	desc1 AS STRING * 25
	desc2 AS STRING * 10
	Supplier AS STRING * 5
	tnta AS STRING * 4
	exposed AS STRING * 8 'Date
	year(1 TO 7) AS STRING * 2
	test(1 TO 7, 1 TO 10) AS SINGLE
	Date AS STRING * 8
	filler AS STRING * 665
END TYPE
DIM SHARED Exposure AS RcdFmtExposure
IF LEN(Exposure) <> 1024 THEN STOP

