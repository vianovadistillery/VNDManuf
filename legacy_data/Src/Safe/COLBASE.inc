

	'/////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>>>>> COLOUR BASE FILE <<<<<<<<<<<<<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	OPEN "colbase.dat" FOR RANDOM SHARED AS #10 LEN = 15

IF NOT typefields% THEN FIELD #10, 1 AS bscode$, 12 AS bdesc$, 2 AS bperc$

TYPE RcdFmtcolbase
	bscode AS STRING * 1
	bdesc AS STRING * 12
	bperc AS STRING * 2
END TYPE
DIM SHARED colbase AS RcdFmtcolbase
