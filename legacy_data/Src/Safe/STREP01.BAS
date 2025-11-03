DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB chkdta (opt%, ok%)
DECLARE SUB qsort (in$(), in%(), n%, ok%)
'.dc - Complete
'/////////////////////////////////////////////////////////////////////////////
'>>>--- RAW MATERIAL STOCKTAKE SYSTEM
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
	CONST maxlines% = 20'19
	'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "MSMENU"
	''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	'$INCLUDE: '\tpmanuf\src\MSRMat.INC'
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	'STDOUT$ = "CON"
	OPEN STDOUT$ FOR OUTPUT AS #99

	DIM h%(15)
	sorted% = 0
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxhst% = CVI(msmisc.max4$): maxacc% = CVI(msmisc.max5$)
	DIM rrn%(maxlines%), k%(maxrmat%), s$(maxrmat%)

START:
	CALL setup("RAW MATERIAL STOCKTAKE SYSTEM")
	COLOR 0, 3: LOCATE 25, 4:  PRINT "F1-Exit"; : COLOR 2, 0
	LOCATE 6, 20: PRINT "1... Print costed stock list."
	LOCATE 7, 20: PRINT "2... Print stocktake sheet.(Active)"
	LOCATE 8, 20: PRINT "3... Print stocktake sheet.(Suspended)"
	LOCATE 9, 20: PRINT "4... Print stocktake sheet.(Miscellanious)"
	LOCATE 10, 20: PRINT "5... Print stocktake sheet.(All)"
	LOCATE 11, 20: PRINT "6... Enter stocktake count.(Active only)"
	LOCATE 12, 20: PRINT "7... Enter stocktake count.(Suspended)"
	LOCATE 13, 20: PRINT "8... Enter stocktake count.(Miscellanious)"
	LOCATE 14, 20: PRINT "9... Enter stocktake count.(All stock)"
	LOCATE 16, 20: PRINT "Enter option..> ";
	CALL inpnew(opt$, 1!, updwn%, "13,59" + ALT$)': GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	opt% = VAL(opt$)
	IF opt% < 1 OR opt% > 9 THEN GOTO START

	IF opt% < 6 THEN
		COLOR 2: LOCATE 18, 18: PRINT "Enter month and year for print..>";
		CALL inpnew(c$, 120!, updwn%, "13,59" + ALT$)': GOSUB ALT
		IF updwn% = 59 THEN GOTO START
		mthyr$ = SPACE$(20): LSET mthyr$ = c$
		END IF

	IF NOT sorted% THEN
				GOSUB LOAD.SORT
				CALL qsort(s$(), k%(), rmx%, ok%)
				sorted% = -1
				END IF

	SELECT CASE opt%
	CASE 1 TO 5: GOSUB DO.LIST
	CASE 6 TO 9: GOSUB ENTER.COUNTS
	CASE ELSE
	END SELECT

GOTO START
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'>>>>>>>>>>  P R I N T   S T O C K   L I S T S
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
DO.LIST:
	s$ = SPACE$(15)
	valsoh = 0: totsoh = 0
	savsup% = 9999
	lin = 9999: pag = 0
	vtotstock = 0
	cursup$ = "": savsup$ = ""

	FOR i% = 1 TO rmx%
	IF STDOUT$ <> "CON" THEN
	LOCATE 20, 20: PRINT "Printing raw material "; i%; " out of "; rmx%: LOCATE 1, 1
	END IF
	IF lin > 50 THEN GOSUB heading
	rec% = k%(i%)

	'>-- L1 - PROCESSING --<
	cursup$ = LEFT$(s$(i%), 5)
	IF cursup$ <> savsup$ THEN
	   savsup$ = cursup$
	   IF lin > 46 THEN GOSUB heading
	   GET #38, rec%, msrmat

	   keyin$ = msrmat.search$: chi% = 45
	   CALL searchindex(keyin$, chi%, found%)
	   supno% = CVI(supx.wcde$)
	   IF supno% < 1 OR supno% > maxsup% THEN supno% = 1
	   GET #44, supno%, sup
	   FETCH = 1
	END IF
	'>>--  END L1 --<<

	GET #38, rec%, msrmat
	rosoh = msrmat.osoh
	sg = msrmat.sg
	extval = msrmat.soh * msrmat.usecost
	valsoh = valsoh + extval
	IF supa = supno% THEN supno% = -1: GOTO 1250
	supa = supno%
	LSET dat$ = "        "
1250
	IF opt% = 1 AND FETCH = 1 AND msrmat.soh <> 0 THEN GOSUB FETCH
	IF opt% = 2 AND FETCH = 1 AND msrmat.active$ = "A" THEN GOSUB FETCH
	IF opt% = 2 AND FETCH = 1 AND msrmat.active$ = "a" THEN GOSUB FETCH
	IF opt% = 3 AND FETCH = 1 AND msrmat.active$ = "S" THEN GOSUB FETCH
	IF opt% = 3 AND FETCH = 1 AND msrmat.active$ = "s" THEN GOSUB FETCH
	IF opt% = 4 AND FETCH = 1 AND msrmat.active$ = "M" THEN GOSUB FETCH
	IF opt% = 5 AND FETCH = 1 THEN GOSUB FETCH
	IF opt% = 1 AND msrmat.soh <> 0 THEN PRINT #99, USING "#### \                       \ ###   !  ####.#### \\   #####.## \\    #####.##"; rec%; msrmat.desc1$; msrmat.group%; msrmat.active$; msrmat.usecost; msrmat.Useunit$; msrmat.soh; msrmat. _
Useunit$; msrmat.soh * msrmat.usecost: lin = lin + 1
	IF opt% = 2 AND msrmat.active$ = "A" THEN PRINT #99, USING "#### \                       \          ####.#### \\   #####.## \\    |_______________|"; rec%; msrmat.desc1$; msrmat.usecost; msrmat.Useunit$; msrmat.soh; msrmat.Useunit$: lin = lin +  _
1
	IF opt% = 2 AND msrmat.active$ = "a" THEN PRINT #99, USING "#### \                       \          ####.#### \\   #####.## \\    |_______________|"; rec%; msrmat.desc1$; msrmat.usecost; msrmat.Useunit$; msrmat.soh; msrmat.Useunit$: lin = lin +  _
1
	IF opt% = 3 AND msrmat.active$ = "S" THEN PRINT #99, USING "#### \                       \          ####.#### \\   #####.## \\    |_______________|"; rec%; msrmat.desc1$; msrmat.usecost; msrmat.Useunit$; msrmat.soh; msrmat.Useunit$: lin = lin +  _
1
	IF opt% = 3 AND msrmat.active$ = "s" THEN PRINT #99, USING "#### \                       \          ####.#### \\   #####.## \\    |_______________|"; rec%; msrmat.desc1$; msrmat.usecost; msrmat.Useunit$; msrmat.soh; msrmat.Useunit$: lin = lin +  _
1
	IF opt% = 4 AND msrmat.active$ = "M" THEN PRINT #99, USING "#### \                       \          ####.#### \\   #####.## \\    |_______________|"; rec%; msrmat.desc1$; msrmat.usecost; msrmat.Useunit$; msrmat.soh; msrmat.Useunit$: lin = lin +  _
1
	IF opt% = 5 THEN PRINT #99, USING "#### \                       \          ####.#### \\   #####.## \\   |_______________|"; rec%; msrmat.desc1$; msrmat.usecost; msrmat.Useunit$; msrmat.soh; msrmat.Useunit$: lin = lin + 1
	vtotstock = vtotstock + value
	X$ = INKEY$: IF ASC(MID$(X$ + "  ", 2)) = 59 THEN EXIT FOR

	NEXT
	IF lin > 50 THEN PRINT #99, CHR$(12); : GOSUB heading
	IF lin > 45 THEN PRINT #99, CHR$(12);
	IF opt% = 1 THEN PRINT #99, "Total Value of S.O.H :"; valsoh
	PRINT #99, CHR$(12);
RETURN
'////////////////////////////////////////////////////////////////////////////
'>>> HEADING
'////////////////////////////////////////////////////////////////////////////
heading:
	 pag = pag + 1: lin = 0
	 IF pag > 1 THEN PRINT #99, CHR$(12);

	 IF opt% = 1 THEN head$ = "C O S T E D   S T O C K   L I S T "
	 IF opt% = 2 THEN head$ = "A C T I V E   S T O C K T A K E   L I S T"
	 IF opt% = 3 THEN head$ = "S U S P E N D E D   S T O C K T A K E   L I S T"
	 IF opt% = 4 THEN head$ = "M I S C E L L A N I O U S   L I S T"
	 IF opt% = 5 THEN head$ = "S T O C K T A K E   L I S T"
	 IF opt% = 1 THEN col$ = "No.  Description               Gr.   A   Pur/Cost Ut      Stock Ut       Value"
	 IF opt% = 2 THEN col$ = "No.  Description               Gr.   A   Pur/Cost Ut    O/Stock Ut     S/Count"
	 IF opt% = 3 THEN col$ = "No.  Description               Gr.   A   Pur/Cost Ut    O/Stock Ut     S\Count"
	 IF opt% = 4 THEN col$ = "No.  Description               Gr.   A   Pur/Cost Ut    O/Stock Ut     S\Count"
	 IF opt% = 5 THEN col$ = "No.  Description               Gr.   A   Pur/Cost Ut    O/Stock Ut     S\Count"
	 '***** Print Actual Heading
	 PRINT #99, "strep01"; TAB(66); "Date:"; DATE1$
	 PRINT #99, TAB(66); "Time:"; TIME$
	 PRINT #99,
	 PRINT #99, CHR$(14); msmisc.cc$
	 PRINT #99,
	 PRINT #99, "    R A W   M A T E R I A L   "; head$
	 PRINT #99, mthyr$; TAB(70); "Page:"; pag
	 PRINT #99, STRING$(79, "=")
	 PRINT #99, col$
RETURN

'////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>  K E Y   S T O C K T A K E
'////////////////////////////////////////////////////////////////////////////
ENTER.COUNTS:
	CLS
	CALL setup("STOCK TAKE ENTRY")
	COLOR 4: LOCATE 3, 2: PRINT " No. DESCRIPTION               SUPL'R    STOCK      COST      VALUE   COUNT   ";
	COLOR 7, 0: LOCATE 2, 20: PRINT "µ                            Æ": COLOR 2
	COLOR 0, 3: LOCATE 25, 4: PRINT "   F1-Exit                                                   "; CHR$(24); CHR$(25); " - Move ";
	COLOR 2, 0: LOCATE 1, 1
	FOR i% = 1 TO maxlines%: rrn%(i%) = 0: NEXT
	stno$ = "": r% = 1: skip% = -1
	oldn% = 1 'Line of subfile

ENTER.COUNTS.0:
	IF NOT skip% THEN
		LOCATE 2, 22: PRINT "Enter from suplier...>";
		CALL inpnew(stno$, 105!, updwn%, "13,59")
		stno$ = UCASE$(stno$)
		IF updwn% = 59 THEN GOTO X.ENTER.COUNTS
		END IF
	skip% = 0

	'>>- Lookup starting position
	r% = sav.first.r%
	IF stno$ > "" THEN
		nearest% = 32676
		FOR i% = 1 TO rmx%
		IF LEFT$(s$(i%), 5) >= LEFT$(stno$, 5) THEN r% = i%: EXIT FOR
		NEXT
		stno$ = ""
		END IF

	'>>- Fill the screen
	n% = 0
	IF r% = 0 THEN r% = nearest%
	IF r% < 1 OR r% > maxrmat% THEN r% = 1
	'>> Display a screen full of details
	DO WHILE n% < maxlines% AND r% < rmx%
		GET #38, k%(r%), msrmat
		CALL chkdta(opt%, ok%)
		IF ok% THEN
			n% = n% + 1: rrn%(n%) = k%(r%) '>>- Load rrn array
			IF n% = 1 THEN sav.first.r% = r%
			IF n% = maxlines% THEN sav.last.r% = r%
			LOCATE n% + 3, 2: COLOR 2: GOSUB PRTLINE
			END IF

		r% = r% + 1
		IF r% < 1 OR r% >= maxrmat% THEN r% = 9999: EXIT DO
	 LOOP

	'***** If maxlines% records not found clear to end of screen
	 FOR i% = n% + 1 TO maxlines%
		LOCATE i% + 3, 2
		PRINT CHR$(FNE)
		rrn%(i%) = 0
		NEXT

	 '***** Now key in corresponding new stock value
	 FOR n% = oldn% TO maxlines%
		rec% = rrn%(n%)
		IF rec% = 0 THEN EXIT FOR
		LOCATE n% + 3, 71       '***** Enter new stock value
		GET #38, rec%, msrmat
		CALL chkdta(opt%, ok%)
		a$ = STR$(msrmat.soh)
                CALL inpnew(a$, 7.2!, updwn%, "13,59,60,72,73,80,81")
		IF updwn% = 59 THEN EXIT FOR

		'***** Recalculate stock value and print on screen
		GET #38, rec%, msrmat
		msrmat.soh = VAL(a$)
		PUT #38, rec%, msrmat

		LOCATE n% + 3, 2
		GOSUB PRTLINE

		'>>-- up/down   pg up/down, Note: finish current line first
		IF updwn% = 72 THEN n% = n% - 2: IF n% < 0 THEN n% = 0
		IF updwn% = 80 THEN n% = n%
		IF updwn% = 73 THEN EXIT FOR
		IF updwn% = 81 THEN EXIT FOR
	 NEXT

	 oldn% = n%: IF n% > maxlines% THEN oldn% = 1

	 IF updwn% = 59 THEN GOTO ENTER.COUNTS.0
	 IF updwn% = 13 THEN sav.first.r% = sav.last.r% + 1: skip% = -1 '>-Roll the screen at end of page
	 IF updwn% = 73 THEN
				n% = 0: result% = 1
				test.r% = sav.first.r% - 1
				DO UNTIL n% = maxlines%
					test.r% = test.r% - 1
					IF test.r% < 1 THEN result% = 1: EXIT DO
					rec% = k%(test.r%)
					GET #38, rec%, msrmat
					CALL chkdta(opt%, ok%)
					IF ok% THEN n% = n% + 1: result% = test.r%
					LOOP
				sav.first.r% = result%: skip% = -1
				END IF
	 IF updwn% = 81 THEN sav.first.r% = sav.last.r% + 1: skip% = -1 'pg up

	 GOTO ENTER.COUNTS.0

X.ENTER.COUNTS:
RETURN
'/////////////////////////////////////////////////////////////////////////////
'>>> Screen print line
'/////////////////////////////////////////////////////////////////////////////
PRTLINE:
	 PRINT USING "#### \                       \  \   \ #####.## ####.#### \\ ####.## |________________|"; msrmat.no%; msrmat.desc1$; msrmat.search$; msrmat.soh; msrmat.usecost; msrmat.Useunit$; msrmat.soh * msrmat.usecost
	'PRINT USING "#### \                       \  \   \ #####.## ####.#### \\ ####.## |________________|"; msrmat.no%; msrmat.desc1$; s$(r%); msrmat.soh; msrmat.usecost; msrmat.Useunit$; msrmat.soh * msrmat.usecost
RETURN
'/////////////////////////////////////////////////////////////////////////////
'>>>  Fetch print of supplier information
'/////////////////////////////////////////////////////////////////////////////
FETCH:
	 PRINT #99, STRING$(79, "-")
	'PRINT #99, USING "!&!!                (####)!"; CHR$(14); sup.sname$; CHR$(20); CHR$(15); supno%; CHR$(18)
	'PRINT #99, USING " & !(####)!";  sup.sname$;  CHR$(15); supno%; CHR$(18)
	 PRINT #99, STRING$(79, "-")
	 lin = lin + 3
	 FETCH = 0
RETURN
'/////////////////////////////////////////////////////////////////////////////
'>>--
'/////////////////////////////////////////////////////////////////////////////
LOAD.SORT:
	'***** Read r/m file
	IF Sort = 1 THEN LOCATE 15, 30: PRINT "*** FILE SORTED ***": RETURN
	LOCATE 20, 20: PRINT "Loading raw materials for sort.": LOCATE 1, 1
	GET #38, 1, msrmat: rmx% = 0: wrk$ = "  ": wrk2$ = "  ": oldsup = 32767
	FOR i% = 1 TO maxrmat%
	   'IF msrmat.date$ <= "19000101" THEN GOTO 600
	   'IF msrmat.date$ >= "20991231" THEN GOTO 600
	   IF i% <> msrmat.no% THEN GOTO 600
	   IF supno% <> oldsup THEN
		  oldsup = supno
		  IF supno% < 1 OR supno% > maxsup% THEN
			 oldsup = 32767
			 LSET sup.search$ = STRING$(4, 255)
		  ELSE
			 GET #44, supno%, sup
			 IF sup.sdate$ = SP8$ OR sup.sdate$ = NUL8$ THEN '.dc
				oldsup = 32767
				LSET sup.search$ = STRING$(4, 255)
			 END IF
		  END IF
	   END IF
	   wrk2$ = MKI$(i%)
	   MID$(wrk$, 1, 1) = MID$(wrk2$, 2, 1): MID$(wrk$, 2, 1) = MID$(wrk2$, 1, 1)
	   rmx% = rmx% + 1: IF rmx% > 4000 THEN i% = maxrmat% + 99: GOTO 600
	   s$(rmx%) = sup.search$ + sup.stype$ + wrk$: k%(rmx%) = i%
600    GET #38, , msrmat
	NEXT

RETURN

SUB chkdta (opt%, ok%) STATIC
	ok% = 0
	IF opt% = 6 AND msrmat.active$ = "S" THEN GOTO X.CHKDTA   '*****Skip suspened r/m records
	IF opt% = 6 AND msrmat.active$ = "s" THEN GOTO X.CHKDTA   '*****Skip suspened stock records
	IF opt% = 6 AND msrmat.active$ = "M" THEN GOTO X.CHKDTA   '*****Skip misc records
	IF opt% = 7 AND msrmat.active$ = "A" THEN GOTO X.CHKDTA   '*****Skip suspened r/m records
	IF opt% = 7 AND msrmat.active$ = "a" THEN GOTO X.CHKDTA   '*****Skip suspened stock records
	IF opt% = 7 AND msrmat.active$ = "M" THEN GOTO X.CHKDTA   '*****Skip misc records
	IF opt% = 8 AND msrmat.active$ = "A" THEN GOTO X.CHKDTA   '*****Skip suspened r/m records
	IF opt% = 8 AND msrmat.active$ = "a" THEN GOTO X.CHKDTA   '*****Skip suspened stock records
	IF opt% = 8 AND msrmat.active$ = "S" THEN GOTO X.CHKDTA   '*****Skip suspened stock records
	IF opt% = 8 AND msrmat.active$ = "s" THEN GOTO X.CHKDTA   '*****Skip suspened stock records
	ok% = -1
X.CHKDTA:
END SUB

SUB qsort (in$(), in%(), n%, ok%) STATIC
'$INCLUDE: '\tpmanuf\src\qsort.bi'
END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB
