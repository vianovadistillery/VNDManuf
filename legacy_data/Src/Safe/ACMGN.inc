	'////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>> ACMGN - ACCESSORY MARGIN FILE <<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	 OPEN "acmgn.dat" FOR RANDOM SHARED AS #1 LEN = 5

IF NOT typefields% THEN FIELD #1, 1 AS mcode$, 4 AS margin$

TYPE RcdFmtacmgn
	mcode AS STRING * 1
	margin AS STRING * 4
END TYPE
DIM SHARED acmgn AS RcdFmtacmgn
