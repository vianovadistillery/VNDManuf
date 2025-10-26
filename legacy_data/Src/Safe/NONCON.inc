'////////////////////////////////////////////////////////////////////
'>>>>>> COMPLAINTS
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

OPEN "noncon.DAT" FOR RANDOM SHARED AS #73 LEN = 1024

TYPE RcdFmtnoncon
	no AS INTEGER
	Name AS STRING * 30
	Addr1 AS STRING * 25
	Addr2 AS STRING * 25
	sub AS STRING * 20
	pcode AS STRING * 4
	opened AS STRING * 8
	closed AS STRING * 8
	atext1 AS STRING * 78
	atext2 AS STRING * 78
	atext3 AS STRING * 78
	atext4 AS STRING * 78
	btext1 AS STRING * 78
	btext2 AS STRING * 78
	btext3 AS STRING * 78
	btext4 AS STRING * 78
END TYPE
DIM SHARED complnt AS RcdFmtnoncon

