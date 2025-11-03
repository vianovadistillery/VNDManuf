'///////////////////////////////////////////////////////////////////////////
'>>>> List all formula's on file
'///////////////////////////////////////////////////////////////////////////
'.dc - Complete
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	CONST maxformseq% = 38
	apgm$ = "MSBCH01P"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CALL setup("LIST ALL FORMULA'S ON FILE")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : COLOR 2, 0
	do.list$ = "C"
start:
	LOCATE 4, 20: PRINT "Print formulation list or create extract file"
	LOCATE 5, 20: PRINT "Options (P=print, C=Cancel, F=File..> "
	DO
		LOCATE 5, 57
		CALL inpnew(do.list$, 101!, updwn%, "13,59" + alt$): GOSUB alt
				do.list$ = UCASE$(do.list$)
		IF updwn% = 59 THEN do.list$ = "C"
		LOOP UNTIL do.list$ = "P" OR do.list$ = "C" OR do.list$ = "F"
	 IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	 IF do.list$ = "C" THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	 GOSUB do.list
	 do.list$ = "N"
	 GOTO start
'///////////////////////////////////////////////////////////////////////////
'>>>> Print the List
'///////////////////////////////////////////////////////////////////////////
do.list:
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\MSCLASS.INC'
	'$INCLUDE: '\tpmanuf\src\tnthedx.INC'
	'$INCLUDE: '\tpmanuf\src\tnthed.INC'
	'$INCLUDE: '\tpmanuf\src\tntdet.INC'
	'$INCLUDE: '\tpmanuf\src\forhedx.INC'
	'$INCLUDE: '\tpmanuf\src\forhed.INC'
	'$INCLUDE: '\tpmanuf\src\fordet.INC'
	'$INCLUDE: '\tpmanuf\src\msrmat.inc'
	'$INCLUDE: '\tpmanuf\src\mscomt.inc'
	'stdout$ = "Junk.jnk"
	DIM SHARED open98%
	OPEN stdout$ FOR OUTPUT AS #99
	GET #63, 1, tnthedx

	lin% = 9999: pag% = 0
	FOR i% = 1 TO 999
		form% = tnthedx.rrn%(i%)
		IF form% < 1 THEN EXIT FOR
		GET #64, form%, tnthed

		IF i% MOD 50 = 0 THEN
			msg$ = "Printing up to formula " + tnthed.tnta$
			CALL sndmsg(msg$)
			END IF


		IF tnthed.class% < 1 OR tnthed.class% > 99 THEN
			LSET msclass.cldesc$ = "** NO CLASS **"
			ELSE
			GET #29, tnthed.class%, msclass
			END IF

		SELECT CASE UCASE$(tnthed.SorW$)
		CASE "S": type$ = "SOLVENT"
		CASE "W": type$ = "WATER  "
		CASE ELSE: type$ = "......."
		END SELECT

		IF lin% > 50 THEN GOSUB heading
		IF do.list$ = "P" THEN
			PRINT #99, USING "\  \    &  ####   &   ##.##  ##.##"; tnthed.tnta$; tnthed.desc$; tnthed.yield!; type$; tnthed.rawcost!; tnthed.alccost!
			lin% = lin% + 1
			END IF
		IF do.list$ = "F" THEN

			IF NOT open98% THEN
				OPEN "FORMULA.PSI" FOR OUTPUT AS #98
				WRITE #98, "Code:", "Desc:", "Yield", "Type", "Raw cost", "Allocated Cost"
				open98% = -1
				END IF
			WRITE #98, tnthed.tnta$, tnthed.desc$, STR$(tnthed.yield!), type$, STR$(tnthed.rawcost!), STR$(tnthed.alccost!)
			END IF
		NEXT

	IF do.list$ = "P" THEN
		PRINT #99, CHR$(12);
		END IF
	CLOSE
	open98% = 0

	CALL sndmsg("Print Complete")
	COLOR 2, 0

RETURN
'////////////////////////////////////////////////////////////////////////////
'>>>>>  H E A D I N G
'////////////////////////////////////////////////////////////////////////////
heading:
	IF do.list$ = "P" THEN
	pag% = pag% + 1: lin% = 0
	IF pag% > 1 THEN PRINT #99, CHR$(12)
	PRINT #99, ; CHR$(14); msmisc.cc$
	PRINT #99, "#Msrep03"; TAB(66); "Page: "; pag%
	PRINT #99, TAB(66); "Date: "; date1$
	PRINT #99, TAB(25); " FORMULATIONS ON FILE"
	PRINT #99, STRING$(79, "=")
	PRINT #99, "No..    Description................... Yield   Base...   Cost.  Alc."
	PRINT #99, STRING$(79, "-")
	END IF
RETURN
