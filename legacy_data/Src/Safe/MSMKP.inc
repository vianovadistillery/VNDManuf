	'///////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>>>>>> finished goods markup <<<<<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	OPEN "msmkp.DAT" FOR RANDOM SHARED AS #37 LEN = 64

IF NOT typefields% THEN FIELD #37, 4 AS mk$, 30 AS mm$, 2 AS mkon$

TYPE RcdFmtmsmkp
	mk AS STRING * 4
	mm AS STRING * 30
	mkon AS STRING * 2
END TYPE
DIM SHARED msmkp AS RcdFmtmsmkp
