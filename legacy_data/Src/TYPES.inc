
	'////////////////////////////////////////////////////////////////////
	'>>>>>>>>>> TYPES - SUPPLIER/CUSTOMER TYPE FILE <<<<<<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	OPEN "types.dat" FOR RANDOM SHARED AS #42 LEN = 80

IF NOT typefields% THEN FIELD #42, 1 AS dftype$, 25 AS dfdesc$, 1 AS x1$, 1 AS x2$, 1 AS x3$, 1 AS x4$, 1 AS x5$, 1 AS x6$, 1 AS x7$, 1 AS x8$, 1 AS x9$, 1 AS x10$, 1 AS x11$, 1 AS x12$, 1 AS x13$, 1 AS x14$, 1 AS x15$, 1 AS x16$, 1 AS x17$, 1 AS  _
x18$, 1 AS x19$, 1 AS x20$

TYPE RcdFmttypes
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
DIM SHARED types AS RcdFmttypes
