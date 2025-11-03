	'///////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>>>>> CUSTOMER FILE INDEX <<<<<<<<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	OPEN "CUSX.WHO" FOR RANDOM SHARED AS #23 LEN = 7

IF NOT typefields% THEN FIELD #23, 5 AS wcde$, 2 AS wrrn$

TYPE RcdFmtCUSX
	wcde AS STRING * 5
	wrrn AS STRING * 2
END TYPE
DIM SHARED CUSX AS RcdFmtCUSX


