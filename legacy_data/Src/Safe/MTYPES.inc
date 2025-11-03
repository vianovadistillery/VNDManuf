'////////////////////////////////////////////////////////////////////
'>>>>>>>>>> TYPES - SUPPLIER/CUSTOMER TYPE FILE <<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

OPEN "mtypes.dat" FOR RANDOM SHARED AS #56 LEN = 80


TYPE RcdFmtmtypes
	dftype AS STRING * 1
	dfdesc AS STRING * 25
	x1 AS STRING * 1
	x2 AS STRING * 1
	x3 AS STRING * 1
	x4 AS STRING * 1
	x5 AS STRING * 1
	x6 AS STRING * 1
	x7 AS STRING * 1
	x8 AS STRING * 1
	x9 AS STRING * 1
	x10 AS STRING * 1
	x11 AS STRING * 1
	x12 AS STRING * 1
	x13 AS STRING * 1
	x14 AS STRING * 1
	x15 AS STRING * 1
	x16 AS STRING * 1
	x17 AS STRING * 1
	x18 AS STRING * 1
	x19 AS STRING * 1
	x20 AS STRING * 1
END TYPE
DIM SHARED mtypes AS RcdFmtmtypes


