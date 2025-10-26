	'////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>>>>>>>>> Colour cards <<<<<<<<<<<<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	OPEN "colcard.dat" FOR RANDOM SHARED AS #11 LEN = 22

IF NOT typefields% THEN FIELD #11, 22 AS ccdesc$

TYPE RcdFmtcolcard
	ccdesc AS STRING * 22
END TYPE
DIM SHARED colcard AS RcdFmtcolcard

