	'/////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>>>>>>> COLOUR CHART FILE <<<<<<<<<<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	OPEN "colcht.dat" FOR RANDOM SHARED AS #12 LEN = 128

FIELD #12, 2 AS TNO$, 2 AS TSUPLR$, 2 AS TCNO$, 1 AS TINEX$, 2 AS TBASE$, 4 AS TBPERC$, 30 AS TDESC$, 8 AS TSUPID$, 2 AS TC$(1), 2 AS TV$(1), 2 AS TC$(2), 2 AS TV$(2), 2 AS TC$(3), 2 AS TV$(3), 2 AS TC$(4), 2 AS TV$(4), 2 AS TC$(5), 2 AS TV$(5), 49  _
AS FILLER$, 8 AS TDATE$

