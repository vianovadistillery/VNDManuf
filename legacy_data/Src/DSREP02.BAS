DECLARE SUB searchindex (keyin$, chi%, found%)
'.dc - Complete
	'//////////////////////////////////////////////////////////////////////
	'///   List orders
	'//////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	RESET: apgm$ = "DSMENU"

	parm2$ = ENVIRON$("PARM2$")
	IF parm2$ = "PRE..." THEN acstkf$ = "PRE"

''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\CUS.INC'
	'$INCLUDE: '\tpmanuf\src\CUSx.INC'
	'$INCLUDE: '\tpmanuf\src\supx.INC'
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	'$INCLUDE: '\tpmanuf\src\ordhed.inc'
	stdout$ = "DSREP02.PRT"
	'stdout$ = "LPT1"
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxcus% = CVI(msmisc.max7$)
	maxcus% = 9999'
	CALL setup("L I S T    O R D E R S")
	IF acstkf$ = "PRE" THEN
		CALL BOX(1, 2, 80, 24, 13, 0, 2)
		CALL SNDMSG("")
		LOCATE 23, 2: COLOR 0, 13: PRINT SPACE$(29); "--PREVIOUS PRICES-- " + SPACE$(29): COLOR 2, 0
	END IF

	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : COLOR 2, 0
	COLOR 2: X = 28
	LOCATE 6, X: PRINT "1. Outstanding orders"
	LOCATE 8, X: PRINT "9. Page Eject"
DO WHILE updwn% <> 59
	LOCATE 14, X: PRINT "Enter option..> "; CHR$(FNH);
	a$ = ""
	CALL inpnew(a$, 101!, updwn%, "13,59" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN EXIT DO
	opt% = VAL(a$)
	IF opt% = 1 THEN GOSUB dolist
	IF opt% = 9 THEN LPRINT CHR$(12);
	LOOP
	CLOSE

	ENVIRON "PARM2$=......":
	CALL exitpgm(apgm$)
	CHAIN apgm$
	 '//////////////////////////////////////////////////////////////////////
	'///////     M A S T E R   L I S T
	'//////////////////////////////////////////////////////////////////////
dolist:
	OPEN stdout$ FOR OUTPUT AS #99
	WIDTH #99, 132
	IF stdout$ = "CON" THEN CLS
	lin% = 32766: pag% = 0
	hrec% = 1
	GET #48, hrec%, ordhed
	WHILE NOT EOF(48)
		IF lin% > 45 THEN GOSUB heading
		IF stdout$ <> "CON" THEN
			LOCATE 20, 20: PRINT "Checking order record "; hrec%: LOCATE 1, 1
		END IF

		IF CVI(ordhed.hord$) = hrec% THEN
			'/// Convert fields to numeric
			hord% = CVI(ordhed.hord$)
			keyin$ = ordhed.hsup$
			CALL searchindex(keyin$, 23, found%)
			IF NOT found% THEN
				keyin$ = "ZZZZZ"
				CALL searchindex(keyin$, 23, found%)
				IF NOT found% THEN
					suplr% = 1
					GET #43, suplr%, cus
				END IF
				GET #48, hrec%, ordhed
				ordhed.hsup$ = cus.search$ + cus.stype$
				PUT #48, hrec%, ordhed
				keyin$ = ordhed.hsup$
				CALL searchindex(keyin$, 23, found%)

			END IF

			suplr% = CVI(supx.wrrn$)
			IF NOT found% THEN suplr% = 1
			horgq = CVS(ordhed.horgq$)
			hinvq = CVS(ordhed.hinvq$)
			hordq = CVS(ordhed.hordq$)
			hdollar = CVS(ordhed.hdollar$)
			'/// And now the actual print
			SELECT CASE opt%
			CASE 1:
				IF hord% <> 0 THEN
					IF suplr% < 1 OR suplr% > maxcus% THEN suplr% = 1
					GET #43, suplr%, cus
					a$ = cus.search$ + cus.stype$
					PRINT #99, USING "  ###  &   &-####   ###,###   ###,###   ###,###    $$#,###.##  \       \  \          \"; hord%; cus.sname$; a$; suplr%; horgq; hinvq; hordq; hdollar; FNDYY$(ordhed.hdate$); FNDYY$(ordhed.hreford$)
					lin% = lin% + 1
				END IF

			END SELECT
		END IF

		GET #48, , ordhed: hrec% = hrec% + 1
	WEND

	PRINT #99, CHR$(18);
	IF pag% > 0 THEN PRINT #99, CHR$(18); CHR$(12);

	CLOSE #99
	LOCATE 20, 2
	shella$ = "COPY DSREP02.PRT LPT1"
	SHELL shella$
	RETURN
	 '///////////////////////////////////////////////////////////////////
	 '///////////      G E N R A L      H E A D I N G       ////////////
	 '///////////////////////////////////////////////////////////////////
heading:
	pag% = pag% + 1: lin% = 0
	IF pag% > 1 THEN PRINT #99, CHR$(12);
	 '/////
	IF opt% = 1 THEN head$ = "F I L E    L I S T I N G"
	 '/////
	IF opt% = 1 THEN col$ = "O/No.  Customer..............................     Code......    L/Inv.    L/Ord.    B/Ord.       Amount.  Ord/Date   Ord/Ref...."
	'/////  print actual heading

	PRINT #99, CHR$(18);
	PRINT #99, "#dsrep02"; TAB(64); "Date:"; DATE1$
	PRINT #99, TAB(64); "Time:"; TIME$
	PRINT #99, " "
	PRINT #99, CHR$(14); msmisc.cc$
	PRINT #99, " "
	PRINT #99, SPC(22); "O R D E R   "; head$
	PRINT #99,
	PRINT #99, TAB(70); "Page:"; pag%
	PRINT #99, CHR$(15);
	PRINT #99, STRING$(131, "=")
	PRINT #99, col$
	PRINT #99, STRING$(131, "-")
	IF stdout$ = "CON" THEN X$ = INPUT$(1)
	 RETURN

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB
