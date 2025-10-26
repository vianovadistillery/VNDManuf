'///////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>> SUPPLIER FILE INDEX <<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
OPEN "supx.who" FOR RANDOM SHARED AS #45 LEN = 7

IF NOT typefields% THEN FIELD #45, 5 AS wcde$, 2 AS wrrn$

TYPE RcdFmtsupx
	wcde AS STRING * 5
	wrrn AS STRING * 2
END TYPE
DIM SHARED supx AS RcdFmtsupx

