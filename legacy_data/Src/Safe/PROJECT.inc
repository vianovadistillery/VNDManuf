'////////////////////////////////////////////////////////////////////
'>>>>>> COMPLAINTS
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
OPEN "PROJECT.DAT" FOR RANDOM SHARED AS #74 LEN = 1600

TYPE RcdFmtproject
	no AS INTEGER
	name AS STRING * 25
	opened AS STRING * 8
	closed AS STRING * 8
	duedate AS STRING * 8
	type AS STRING * 10
	report AS STRING * 10
	text(1 TO 18) AS STRING * 78
	filler AS STRING * 125
END TYPE
DIM SHARED project AS RcdFmtproject
IF LEN(project) <> 1600 THEN STOP
