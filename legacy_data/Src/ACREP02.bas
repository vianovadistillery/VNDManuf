DECLARE SUB searchindex (keyin$, chi%, found%)
'/////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>         A C R E P 0 2       <<<<<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'.dc - Complete
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	CONST maxlines% = 20
	apgm$ = "ACMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	'$INCLUDE: '\tpmanuf\src\ACSTK.INC'
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\supx.INC'
	keyl% = 7: qk$ = SPACE$(keyl%)
	CALL index("OPEN ", ind%, "acstkx2.acf", 2, keyl%)
	'STDOUT$ = "CON"
	OPEN STDOUT$ FOR OUTPUT AS #99


	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxhst% = CVI(msmisc.max4$): maxacc% = CVI(msmisc.max5$)
	DIM rrn%(maxlines%)

	CALL setup("STOCKTAKE SYSTEM")
	COLOR 0, 3: LOCATE 25, 4: PRINT SPACE$(75);

REDSPLY:
	CALL setup("STOCKTAKE SYSTEM")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit  "; : COLOR 2, 0
	X = 22
	LOCATE 6, X: PRINT "1. Print costed stock list.";
	LOCATE 7, X: PRINT "2. Print stocktake sheet. (Active)";
	LOCATE 8, X: PRINT "3. Print stocktake sheet. (Suspended)";
	LOCATE 9, X: PRINT "4. Print stocktake sheet. (All)";
	LOCATE 10, X: PRINT "5. Enter stocktake count. (Active)";
	LOCATE 11, X: PRINT "6. Enter stocktake count. (All)";
	LOCATE 12, X: PRINT "7. List stock sold to date.";
	LOCATE 13, X: PRINT "8. List & clear sales figures.";
	DO     '***** Top of main loop
	   LOCATE 15, X: PRINT "Enter option..> "; CHR$(FNH);
	   a$ = ""
	   CALL inpnew(a$, 1!, updwn%, "13,59,67")
	   IF updwn% = 59 THEN EXIT DO
	   opt% = VAL(a$)
	   IF opt% = 8 THEN
			GOSUB check.del
			IF updwn% = 60 THEN GOTO loop1
			IF updwn% = 59 THEN EXIT DO
			END IF

	   IF opt% < 5 THEN
			GOSUB stkdate
			IF updwn% = 60 THEN GOTO loop1
			IF updwn% = 59 THEN EXIT DO
			END IF

	   ON opt% GOSUB mstkl, mstkl, mstkl, mstkl, cf3, cf3, mstkl, mstkl
	   IF opt% = 5 THEN updwn% = 67: EXIT DO
	   IF opt% = 6 THEN updwn% = 67: EXIT DO
loop1:
	LOOP
	IF updwn% = 67 THEN GOTO REDSPLY
mlend:
	CLOSE :
	CALL exitpgm(apgm$)
	CHAIN apgm$
'>>>>>  P R I N T   S T O C K T A K E   D A T E
stkdate:
	LOCATE 18, 10: PRINT "Enter month and year for print..> "; CHR$(FNH);
	CALL inpnew(mthyr$, 125!, updwn%, "13,59,60")
	RETURN
'>>>>>  C H E C K    B E F O R E   C L E A R I N G  S A L E S
check.del:
	yorn$ = ""
	LOCATE 18, 10: PRINT "Are you sure you want to clear the sales figures..> "; CHR$(FNH);
	CALL inpnew(yorn$, 101!, updwn%, "13,59,60")
	yorn$ = UCASE$(yorn$)
	IF yorn$ <> "Y" THEN updwn% = 60
	RETURN
'/////////////////////////////////////////////////////////////////////////////
'>>>>>  M A S T E R   S T O C K T A K E   L I S T
'/////////////////////////////////////////////////////////////////////////////
mstkl:
	acc% = 0
	savsup$ = "~~~~"
	valsoh! = 0: totsoh! = 0
	lin = 9999: pag = 0
	vtotstock = 0
	i% = 0: ind% = 0
	CALL index("FIRST", ind%, qk$, 2, keyl%)
	DO WHILE ind% > 0 AND i% < maxacc%'??
	   i% = i% + 1
	   rec% = ind%
	   IF rec% < 1 OR rec% > maxacc% THEN GOTO m100
	   GET #3, rec%, acstk

	   IF STDOUT$ <> "CON" THEN
		LOCATE 20, 22: PRINT "Printing accessory "; i%: LOCATE 1, 1
		END IF

	   IF lin > 50 THEN GOSUB heading
	 '***** L1 - Processing
	IF LEFT$(qk$, 4) <> savsup$ THEN
	   IF lin > 46 THEN GOSUB heading
	   LSET savsup$ = qk$
	   CALL searchindex(acstk.suplr$, 45, found%)
	   asuplr% = CVI(supx.wrrn$)
	   IF NOT found% THEN asuplr% = 0
	   IF asuplr% < 1 OR asuplr% > maxsup% THEN
		  LSET sname$ = "**UNKNOWN**"
		  sno% = 0
	   ELSE
		  GET #44, asuplr%, sup
		  sno% = CVI(sup.sno$)
		  fetch = 1
	   END IF
	END IF     '***** End L1-Processing

	IF opt% = 1 AND acstk.soh% = 0 THEN GOTO m100
	IF opt% = 2 AND acstk.active$ = "S" THEN GOTO m100
	IF opt% = 3 AND acstk.active$ <> "S" THEN GOTO m100
	IF opt% = 7 AND acstk.sold% = 0 THEN GOTO m100 '*****Sales listing
	IF opt% = 8 AND acstk.sold% = 0 THEN GOTO m100
	a$ = acstk.desc1$: GOSUB m200: LSET acstk.desc1$ = a$

	SELECT CASE acstk.pack%
	CASE 0: atcost = acstk.wholesalecost
	CASE ELSE: atcost = acstk.wholesalecost / acstk.pack%
	END SELECT

	value! = atcost! * acstk.soh%
	IF fetch = 1 THEN GOSUB m300
	IF opt% = 1 THEN PRINT #99, USING "#### & \        \ & & ### #######  ####.##  #####.##"; acstk.no%; acstk.desc1$; acstk.desc2$; acstk.size$; acstk.unit$; acstk.pack%; acstk.soh%; atcost!; value!
	IF opt% = 2 THEN PRINT #99, USING "#### & \        \ & & ### ..... ########  |________|"; acstk.no%; acstk.desc1$; acstk.desc2$; acstk.size$; acstk.unit$; acstk.pack%; acstk.soh%
	IF opt% = 3 THEN PRINT #99, USING "#### & \        \ & & ### ..... ########  |________|"; acstk.no%; acstk.desc1$; acstk.desc2$; acstk.size$; acstk.unit$; acstk.pack%; acstk.soh%
	IF opt% = 4 THEN PRINT #99, USING "#### & \        \ & & ### ..... ########  |________|"; acstk.no%; acstk.desc1$; acstk.desc2$; acstk.size$; acstk.unit$; acstk.pack%; acstk.soh%
	IF opt% = 7 THEN PRINT #99, USING "#### & \        \ & & ### ..... ########      ##,###"; acstk.no%; acstk.desc1$; acstk.desc2$; acstk.size$; acstk.unit$; acstk.pack%; acstk.soh%; acstk.sold
	IF opt% = 8 THEN PRINT #99, USING "#### & \        \ & & ### ..... ########      ##,###"; acstk.no%; acstk.desc1$; acstk.desc2$; acstk.size$; acstk.unit$; acstk.pack%; acstk.soh%; acstk.sold
	lin = lin + 1
	vtotstock! = vtotstock! + value!
	'***** Option 8 clears the sales figures
	IF opt% = 8 THEN
	   acstk.sold = 0
	   PUT #3, rec%, acstk
	END IF
m100:
	CALL index("READ ", ind%, qk$, 2, keyl%)
	LOOP


	'>----
	IF opt% = 2 OR opt% = 3 OR opt% = 4 OR opt% = 6 OR opt% = 7 THEN PRINT #99, CHR$(12); : RETURN
	GOSUB heading
	PRINT #99, : PRINT #99, : PRINT #99, : PRINT #99,
	IF opt% = 1 THEN PRINT #99, "Total Stock Value :"; vtotstock
	PRINT #99, CHR$(18); CHR$(12);
RETURN
'>>>>> G E N E R A L    H E A D I N G
heading:
	pag = pag + 1: lin = 0
	IF pag > 1 THEN PRINT #99, CHR$(12);
	IF opt% = 1 THEN head$ = "C O S T E D    S T O C K    L I S T"
	IF opt% = 2 THEN head$ = "A C T I V E   S T O C K T A K E    L I S T"
	IF opt% = 3 THEN head$ = "S U S P E N D E D   S T O C K T A K E    L I S T"
	IF opt% = 4 THEN head$ = "S T O C K T A K E    L I S T"
	IF opt% = 7 THEN head$ = "S A L E S    L I S T I N G"
	IF opt% = 8 THEN head$ = "S A L E S    L I S T I N G"

	IF opt% = 1 THEN col$ = "Code   Product description                 Size  Box   S.O.H   G/Cost    Value "
	IF opt% = 2 THEN col$ = "Code   Product description                 Size  Box           S.O.H     Count "
	IF opt% = 3 THEN col$ = "Code   Product description                 Size  Box           S.O.H     Count "
	IF opt% = 4 THEN col$ = "Code   Product description                 Size  Box           S.O.H     Count "
	IF opt% = 7 THEN col$ = "Code   Product description                 Size  Box           S.O.H     Sales "
	IF opt% = 8 THEN col$ = "Code   Product description                 Size  Box           S.O.H     Sales "
	'***** Print actual heading
	PRINT #99, "#acrep02"; TAB(67); "Date:"; DATE1$
	PRINT #99, CHR$(14); msmisc.cc$
	PRINT #99, "                  "; head$
	PRINT #99, mthyr$;
	PRINT #99, TAB(70); USING "Page:##"; pag
	PRINT #99, STRING$(79, "=")
	PRINT #99, col$
	RETURN
'>>>>> Add .. to trailing blank chars in a string
m200:
	l% = LEN(a$)
	FOR k% = l% TO 1 STEP -1
	   IF MID$(a$, k%, 1) <> " " THEN k% = 1: GOTO m250
	   MID$(a$, k%, 1) = "."
m250:
	NEXT
	RETURN

'>>>>>  Fetch print of supplier information
m300:
	PRINT #99, STRING$(79, "-")
   'PRINT #99, USING "!&!!                  ####!"; CHR$(14); sup.sname$; CHR$(20); CHR$(15); sno%; CHR$(18)
	PRINT #99, USING " & !(####)!"; sup.sname$; CHR$(15); sno%; CHR$(18)
	PRINT #99, STRING$(79, "-")
	lin = lin + 3
	fetch = 0
	RETURN
'////////////////////////////////////////////////////////////////////////////
'>>>>>  K E Y   S T O C K T A K E   D A T A
'////////////////////////////////////////////////////////////////////////////
cf3:
	CALL setup("STOCK TAKE ENTRY")
	COLOR 4: LOCATE 3, 2: PRINT "No.  DESCRIPTION                           SIZE  STOCK  COST    VALUE    COUNT";
	COLOR 7, 0: LOCATE 2, 20: PRINT "µ                            Æ"; : COLOR 2
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : LOCATE 25, 71: PRINT CHR$(24); CHR$(25); "-Move"; : COLOR 2, 0
	rrn%(maxlines%) = 0: fst% = 1
entry:
	COLOR 2: LOCATE 2, 22: PRINT "Enter from number....>";
	frm$ = "    "
	CALL inpnew(frm$, 4!, updwn%, "13,59")
	IF updwn% = 59 THEN GOTO REDSPLY
cf3a:
	fst% = 1: rrn%(maxlines%) = 0
	frm% = VAL(frm$)
	IF frm% = 0 THEN frm% = 1
	IF frm% >= maxacc% THEN
	   COLOR 14, 3: LOCATE 5, 25
	   PRINT "Number not valid"
	   COLOR 2, 0
	   frm$ = "    "
	   GOTO entry
	END IF
	n% = 0: r% = 0: fst% = 0
	'***** set first screen with details
	DO WHILE n% <= maxlines% - 1 AND r% < 9999
	   r% = r% + 1
	   IF r% < 1 OR r% >= maxacc% THEN r% = 9999: EXIT DO
	   GET #3, r%, acstk
	   IF EOF(3) THEN EXIT DO'R% = RNN%(1)
	   IF r% >= frm% THEN
	  IF acstk.wholesalecost > .0001 THEN
		 n% = n% + 1
		 LOCATE n% + 3, 2
		 GOSUB prtline
		 rrn%(n%) = r%   '***** Save record number
	  END IF
	   END IF
	LOOP

	'***** If maxlines% records not found clear to end of screen
	FOR i% = n% TO maxlines% - 1
	   LOCATE i% + 4, 2
	   PRINT CHR$(FNE)
	   rrn%(i% + 1) = 0
	NEXT
	'***** Key in new stock value
	FOR i% = 1 TO maxlines%
cf3b:
	  r% = rrn%(i%)
	  IF r% < 1 OR r% > 9999 THEN EXIT FOR     '***** No record
	  LOCATE i% + 3, 75
	  GET #3, r%, acstk
	  IF acstk.wholesalecost > .0001 THEN
	  a$ = STR$(acstk.soh%)
	  CALL inpnew(a$, 4!, updwn%, "13,59,60,72,73,80,81")
	  IF updwn% = 59 THEN     '***** F1 pressed
		   LOCATE i% + 3, 2
			GOSUB prtline
			EXIT FOR
			END IF
	  IF updwn% = 72 THEN     '***** UP ARROW back one line browse
			r% = rrn%(1): lin% = 0
			DO
				r% = r% - 1
				IF r% < 1 OR r% > maxacc% THEN r% = rrn%(1)
				GET #3, r%, acstk
				IF acstk.wholesalecost > .0001 THEN EXIT DO
				LOOP
			frm% = r%
			IF frm% < 1 OR frm% >= maxacc% THEN frm% = 1
			frm$ = STR$(frm%)
			LOCATE 2, 44: PRINT USING "####"; frm%
			IF fst% = 0 THEN roll = 1
			fst% = 0
			GOTO cf3a
			END IF
	  IF updwn% = 73 THEN     '***** PAGE UP reverse browse pressed
			r% = rrn%(1): lin% = 0
			GET #3, r%, acstk
			DO WHILE lin% < maxlines%
				IF acstk.wholesalecost > .0001 THEN lin% = lin% + 1
				IF lin% = maxlines% THEN EXIT DO
				r% = r% - 1
				IF r% < 1 OR r% > maxacc% THEN r% = 1: EXIT DO
				GET #3, r%, acstk
				LOOP
			frm% = r%
			IF frm% < 1 OR frm% >= maxacc% THEN frm% = 1
			frm$ = STR$(frm%)
			LOCATE 2, 44: PRINT USING "####"; frm%
			IF fst% = 0 THEN roll = 1
			fst% = 0
			GOTO cf3a
			END IF
	  IF updwn% = 80 THEN         '***** DOWN ARROW back one line browse
			IF rrn%(2) = 0 THEN
				r% = rrn%(1)
				ELSE
				r% = rrn%(2)
				END IF
			frm% = r%
			IF frm% < 1 OR frm% > maxacc% THEN frm% = 1
			frm$ = STR$(frm%)
			LOCATE 2, 44: PRINT USING "####"; frm%
			IF fst% = 0 THEN roll = 1
			fst% = 0
			GOTO cf3a
			END IF
	  IF updwn% = 81 THEN     '***** PAGE DOWN browse pressed
			IF rrn%(maxlines%) = 0 THEN
				r% = rrn%(1)
				ELSE
				r% = rrn%(maxlines%)
				END IF
			frm% = r%
			LOCATE 2, 44: PRINT USING "####"; frm%
			IF frm% < 1 OR frm% > maxacc% THEN frm% = 1
			frm$ = STR$(frm%)
			IF fst% = 0 THEN roll = 1
			fst% = 0
			GOTO cf3a
			END IF

	'***** Calculate stock value and print on screen
	  GET #3, r%, acstk
	  acstk.soh% = VAL(a$)
	  extval = acstk.soh% * acstk.wholesalecost
	  PUT #3, r%, acstk

	  LOCATE i% + 3, 2
	  GOSUB prtline
	  frm% = r%
	   END IF
	NEXT

	 '>>>>> Go back to start of browse
	IF updwn% = 59 THEN GOTO entry
	roll = 1': GOTO ENTRY
'***** If enter is pressed at end of screen fields, start next screen
	 frm% = r%
	 LOCATE 2, 44: PRINT USING "####"; frm%
	 IF frm% < 1 OR frm% > maxacc% THEN frm% = 1
	 frm$ = STR$(frm%)
	 IF fst% = 0 THEN roll = 1
	 fst% = 0
	 GOTO cf3a
'>>>>>  P R I N T    A   L I N E
prtline:
	extval = acstk.soh% * wholesalecost
	IF acstk.soh% < -999 THEN acstk.soh% = -999 '??
	COLOR 2
	PRINT USING "#### \                        \\         \ \  \\\ #### ####.## #####.## |________|"; r%; acstk.desc1$; acstk.desc2$; acstk.size$; acstk.unit$; acstk.soh%; acstk.wholesalecost; extval
	RETURN

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB
