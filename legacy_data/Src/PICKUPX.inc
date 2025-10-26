	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
	'>>> Pickup address file
	'//////////////////////////////////////////////////////////////////

	OPEN "PICKUPX.WHO" FOR RANDOM SHARED AS #51 LEN = 16

IF NOT typefields% THEN 	FIELD #51, 14 AS PXCDE$, 2 AS PXRRN$

TYPE RcdFmtPICKUPX
	pxcde AS STRING * 14
	pxrrn AS STRING * 2
END TYPE 
DIM SHARED PICKUPX AS RcdFmtPICKUPX
