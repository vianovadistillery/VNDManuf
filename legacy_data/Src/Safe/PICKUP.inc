	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
	'>>> Pickup address file
	'//////////////////////////////////////////////////////////////////

	OPEN "PICKUP.WHO" FOR RANDOM SHARED AS #50 LEN = 144

IF NOT typefields% THEN FIELD #50, 2 AS pno$, 30 AS pname1$, 30 AS pname2$, 30 AS pname3$, 30 AS pname4$, 11 AS pphone1$, 11 AS pphone2$

TYPE RcdFmtPICKUP
	pno AS STRING * 2
	pname1 AS STRING * 30
	pname2 AS STRING * 30
	pname3 AS STRING * 30
	pname4 AS STRING * 25
	pactive AS STRING * 1
	pphone1 AS STRING * 13
	pphone2 AS STRING * 13
END TYPE

DIM SHARED PICKUP AS RcdFmtPICKUP

