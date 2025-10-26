'////////////////////////////////////////////////////////////////////
'>>>>>> DEVELOPMENT
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
OPEN "develop.DAT" FOR RANDOM SHARED AS #74 LEN = 1360

TYPE RcdFmtdevelop
	no AS INTEGER

	Name AS STRING * 30
	Addr AS STRING * 25
	sub AS STRING * 20
	pcode AS STRING * 4
	phone AS STRING * 10
	fax AS STRING * 10

	opened AS STRING * 8
	closed AS STRING * 8
	type AS STRING * 10
	product AS STRING * 10
	colour AS STRING * 10
	batch AS STRING * 10
	report AS STRING * 10

	text(1 TO 14) AS STRING * 78
END TYPE
DIM SHARED complnt AS RcdFmtdevelop

