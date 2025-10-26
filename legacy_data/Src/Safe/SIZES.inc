
	'///////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>>>> ACCESSORY SIZES FILE <<<<<<<<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	OPEN "sizes.dat" FOR RANDOM SHARED AS #41 LEN = 80

IF NOT typefields% THEN
FIELD #41, 2 AS skey$, 15 AS sdesc$, 5 AS short$, 2 AS cst$(1), 2 AS cst$(2), 2 AS cst$(3), 2 AS cst$(4), 2 AS cst$(5), 2 AS cst$(6), 2 AS cst$(7), 2 AS cst$(8), 2 AS cst$(9), 2 AS cst$(10), 4 AS prcret$, 4 AS prctrd$, 4 AS prcdst$
END IF

TYPE RcdFmtsizes
	skey AS STRING * 2
	sdesc AS STRING * 15
	short AS STRING * 5
	cst(1 TO 10) AS STRING * 2
	prcret AS STRING * 4
	prctrd AS STRING * 4
	prcdst AS STRING * 4
END TYPE
DIM SHARED sizes AS RcdFmtsizes

