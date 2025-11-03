'////////////////////////////////////////////////////////////////////
'>>>>>> COMPLAINTS
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
OPEN "complnt.DAT" FOR RANDOM SHARED AS #70 LEN = 1360

TYPE RcdFmtcomplnt
	no AS INTEGER

	Name AS STRING * 30
	Addr AS STRING * 25
	sub AS STRING * 20
	pcode AS STRING * 4
	phone AS STRING * 12
	fax AS STRING * 12

	cName AS STRING * 30
	cAddr AS STRING * 25
	csub AS STRING * 20
	cpcode AS STRING * 4
	cphone AS STRING * 12
	cfax AS STRING * 12

	opened AS STRING * 8
	closed AS STRING * 8
	type AS STRING * 10
	product AS STRING * 10
	colour AS STRING * 10
	batch AS STRING * 10
	report AS STRING * 10

	text(1 TO 12) AS STRING * 78
	filler AS STRING * 150
END TYPE
DIM SHARED complnt AS RcdFmtcomplnt
IF LEN(complnt) <> 1360 THEN STOP
