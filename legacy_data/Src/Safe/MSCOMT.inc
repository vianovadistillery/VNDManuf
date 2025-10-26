
	'////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>>> FORMULA COMMENT FILE <<<<<<<<<<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	OPEN "mscomt.DAT" FOR RANDOM SHARED AS #30 LEN = 22

IF NOT typefields% THEN FIELD #30, 22 AS spk$

TYPE RcdFmtmscomt
	spk AS STRING * 22
END TYPE
DIM SHARED mscomt AS RcdFmtmscomt
IF NOT typefields% THEN FIELD #30, 2 AS spkno$

TYPE RcdFmtmscomt2
	spkno AS STRING * 2
END TYPE
DIM SHARED mscomt2 AS RcdFmtmscomt2

