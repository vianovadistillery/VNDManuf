	'>>>>>>>>>>>>>>>>>> RTCOL03  - Tint formula print <<<<<<<<<<<<<<<<<<<<<<
	'>>>>>>>>>>>>                    KEY MAPS                   <<<<<<<<<<<<
	'>>>>> In all cases the supplier comes fisrt and the TNO$ is last <<<<<<
	'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	' The key lenght is the lenght of the record + 6
	'>>>> KEY MAP 1
	'          KFLD       SEARCH$    4A   1  Supplier search code
	'          KFLD       SNO$       2I   5  Supplier # (High byte, Low byte)
	'          KFLD       TDESC$    30A   7  Tint desciption
	'          KFLD       TNO$       2I  37  Tint number (High byte, Low byte)
	'//
	'>>>> KEY MAP 2
	'          KFLD       SEARCH$    4A   1  Supplier search code
	'          KFLD       SNO$       2I   5  Supplier # (High byte, Low byte)
	'          KFLD       TSUPID$    8A   7  Supplier ID
	'          KFLD       TNO$       2I   9  Tint number (High byte, Low byte)
	'//
	'>>>> KEY MAP 3
	'          KFLD       SEARCH$    4A   1  Supplier search code
	'          KFLD       SNO$       2I   5  Supplier # (High byte, Low byte)
	'          KFLD       CCDESC$   22A   7  Colour card description
	'          KFLD       TCNO$      2I  29  Colour card # (High byte, Low byte)
	'          KFLD       TDESC$    30A  39  Tint desciption
	'          KFLD       TNO$       2I  41  Tint number (High byte, Low byte)
	'//
	'>>>> KEY MAP 4
	'          KFLD       SEARCH$    4A   1  Supplier search code
	'          KFLD       SNO$       2I   5  Supplier # (High byte, Low byte)
	'          KFLD       CCDESC$   22A   7  Colour card description
	'          KFLD       TCNO$      2I  29  Colour card # (High byte, Low byte)
	'          KFLD       TSUPID$    8A  31  Supplier ID
	'          KFLD       TNO$       2I  39  Tint number (High byte, Low byte)
	'//

		OPEN "colchtx1.dat" FOR RANDOM SHARED AS #1 LEN = 78
		OPEN "colchtx2.fxc" FOR RANDOM SHARED AS #2 LEN = 78
		OPEN "colchtx3.fxc" FOR RANDOM SHARED AS #3 LEN = 78
		OPEN "colchtx4.fxc" FOR RANDOM SHARED AS #4 LEN = 78
		CLOSE
		OPEN "colcht.fcc" FOR RANDOM SHARED AS #1 LEN = 128
		OPEN "colbase.fcc" FOR RANDOM SHARED AS #5 LEN = 15
		OPEN "colcard.fcc" FOR RANDOM SHARED AS #6 LEN = 22

IF NOT typefields% THEN
FIELD #1, 2 AS TNO$, 2 AS TSUPLR$, 2 AS TCNO$, 1 AS TINEX$, 2 AS TBASE$, 4 AS TBPERC$, 30 AS TDESC$, 8 AS TSUPID$, 2 AS TC$(1), 2 AS TV$(1), 2 AS TC$(2), 2 AS TV$(2), 2 AS TC$(3), 2 AS TV$(3), 2 AS TC$(4), 2 AS TV$(4), 2 AS TC$(5), 2 AS TV$(5), 49  _
AS filler$, 8 AS TDATE$
END IF

IF NOT typefields% THEN
FIELD #3, 2 AS sno$, 30 AS sname$, 20 AS saddr$, 4 AS spcode$, 3 AS sacode$, 7 AS sphone$, 8 AS sdate$, 20 AS scont$, 20 AS suburb$, 6 AS spbox$, 1 AS sdist$, 1 AS sret$
END IF

TYPE RcdFmtcolcard
	sno AS STRING * 2
	sname AS STRING * 30
	saddr AS STRING * 20
	spcode AS STRING * 4
	sacode AS STRING * 3
	sphone AS STRING * 7
	sdate AS STRING * 8
	scont AS STRING * 20
	suburb AS STRING * 20
	spbox AS STRING * 6
	sdist AS STRING * 1
	sret AS STRING * 1
END TYPE
DIM SHARED colcard AS RcdFmtcolcard
IF NOT typefields% THEN FIELD #3, 122 AS places$, 20 AS spaddr$, 20 AS spsub$, 4 AS scur$, 4 AS s30$, 4 AS s60$, 4 AS s90$, 1 AS stype$, 2 AS sdays$, 4 AS sterms$, 4 AS search$

TYPE RcdFmtcolcard2
	places AS STRING * 122
	spaddr AS STRING * 20
	spsub AS STRING * 20
	scur AS STRING * 4
	s30 AS STRING * 4
	s60 AS STRING * 4
	s90 AS STRING * 4
	stype AS STRING * 1
	sdays AS STRING * 2
	sterms AS STRING * 4
	search AS STRING * 4
END TYPE
DIM SHARED colcard2 AS RcdFmtcolcard2
IF NOT typefields% THEN FIELD #3, 189 AS places$, 2 AS daysmax$, 3 AS sacode1$, 7 AS sphone1$, 4 AS opn$, 4 AS opn30$, 4 AS opn60$, 4 AS opn90$, 2 AS agent$, 4 AS account$, 2 AS finvn$, 2 AS fpayn$, 4 AS climit$, 10 AS taxe$, 2 AS fcrnn$, 30 AS  _
spname$, 1 AS scont1$, 1 AS scont2$, 2 AS sunpoz$, 4 AS smlpoz$, 12 AS filler$

TYPE RcdFmtcolcard3
	places AS STRING * 189
	daysmax AS STRING * 2
	sacode1 AS STRING * 3
	sphone1 AS STRING * 7
	opn AS STRING * 4
	opn30 AS STRING * 4
	opn60 AS STRING * 4
	opn90 AS STRING * 4
	agent AS STRING * 2
	account AS STRING * 4
	finvn AS STRING * 2
	fpayn AS STRING * 2
	climit AS STRING * 4
	taxe AS STRING * 10
	fcrnn AS STRING * 2
	spname AS STRING * 30
	scont1 AS STRING * 1
	scont2 AS STRING * 1
	sunpoz AS STRING * 2
	smlpoz AS STRING * 4
	filler AS STRING * 12
END TYPE
DIM SHARED colcard3 AS RcdFmtcolcard3
IF NOT typefields% THEN FIELD #4, 4 AS wcde$, 1 AS wtyp$, 2 AS wrrn$

TYPE RcdFmtcolcard4
	wcde AS STRING * 4
	wtyp AS STRING * 1
	wrrn AS STRING * 2
END TYPE
DIM SHARED colcard4 AS RcdFmtcolcard4
IF NOT typefields% THEN FIELD #5, 1 AS bscode$, 12 AS bdesc$, 2 AS bperc$

TYPE RcdFmtcolcard5
	bscode AS STRING * 1
	bdesc AS STRING * 12
	bperc AS STRING * 2
END TYPE
DIM SHARED colcard5 AS RcdFmtcolcard5
IF NOT typefields% THEN FIELD #6, 22 AS ccdesc$

TYPE RcdFmtcolcard6
	ccdesc AS STRING * 22
END TYPE
DIM SHARED colcard6 AS RcdFmtcolcard6

