
	'///////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>> RAW MATERIAL CLASS FILE <<<<<<<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	OPEN "msclass.dat" FOR RANDOM SHARED AS #29 LEN = 57

IF NOT typefields% THEN FIELD #29, 25 AS cldesc$, 8 AS clya$, 8 AS clyt$, 8 AS clyay$, 8 AS clyty$

TYPE RcdFmtmsclass
	cldesc AS STRING * 25
	clya AS STRING * 8
	clyt AS STRING * 8
	clyay AS STRING * 8
	clyty AS STRING * 8
END TYPE
DIM SHARED msclass AS RcdFmtmsclass

