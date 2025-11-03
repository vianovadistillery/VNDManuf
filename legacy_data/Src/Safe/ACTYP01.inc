
	'>>>>>>>>>>>>>>>>>>>>> ACTYP01 - SUP/CUS/LED types <<<<<<<<<<<<<<<<<<<<<<<
		OPEN "types.acf"  FOR RANDOM SHARED AS #7  LEN=80

IF NOT typefields% THEN
FIELD #7,1  AS DFTYPE$,    25 AS DFDESC$,    1  AS X1$,    1  AS X2$,_
    1  AS X3$,    1  AS X4$,    1  AS X5$,    1  AS X6$,    1  AS X7$,_
    1  AS X8$,    1  AS X9$,    1  AS X10$,    1  AS X11$,    1  AS X12$,_
    1  AS X13$,    1  AS X14$,    1  AS X15$,    1  AS X16$,    1  AS X17$,_
    1  AS X18$,    1  AS X19$,		    1  AS X20$
END IF

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

