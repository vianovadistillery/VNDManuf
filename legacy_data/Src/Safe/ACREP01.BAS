DECLARE SUB browse.idx (firstonscreen%, ch1%, ch2%)
DECLARE SUB printcodes ()
DECLARE SUB rightprice (PRICE!, stype$)
DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB retail.round (PRICE!, round.type$)
'.dc - Complete
	'>>>>>>>>>>>>>>>>> Acrep01 - Accessory price lists <<<<<<<<<<<<<<<<<<
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	DB.OR.CR$ = "CR"
	acstkf$ = "ACF"
	apgm$ = "ACMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	keyl% = 7: qk$ = SPACE$(keyl%)
	CALL index("OPEN ", ind%, "ACSTKX2.ACF", 2, keyl%)
	sfx$ = "  "
	COLOR 2
	cursup$ = "    ": savsup$ = "@@@@": skey$ = "    "
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'    '***** #43 LEN=300
	'$INCLUDE: '\tpmanuf\src\sup.INC'     '***** #44
	'$INCLUDE: '\tpmanuf\src\supX.INC'    '***** #45
	'$INCLUDE: '\tpmanuf\src\ACSTK.INC'   '***** #3
	'$INCLUDE: '\tpmanuf\src\ACMGN.INC'   '***** #1
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'  '***** #36
	'$INCLUDE: '\tpmanuf\src\COMPANY.INC' '***** #18
	stdout$ = "acrep01.wrk"
	'stdout$ = "CON"
	GET #36, 1, msmisc

	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxhst% = CVI(msmisc.max4$): maxacc% = CVI(msmisc.max5$)
	DIM mm(81)
	'////////////////  load the margin file into an array ///////////////
	GET #1, 1, acmgn: mm(1) = CVS(acmgn.margin$): mm(81) = 0
	FOR i% = 2 TO 80: GET #1, , acmgn: mm(i%) = CVS(acmgn.margin$): NEXT
	CLOSE #1
	cha% = 45: chb% = 44
start:
	CALL setup(" PRINT ACCESSORY PRICE LISTS")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit";
	COLOR 2, 0: X = 28
	LOCATE 4, 1
	LOCATE , X: PRINT "1.  Retail price list"
	LOCATE , X: PRINT "2.  Counter Price list"
	LOCATE , X: PRINT "3.  Trade price list"
	LOCATE , X: PRINT "4.  Contractor price list"
	LOCATE , X: PRINT "5.  Industrial/Painter price list"
	LOCATE , X: PRINT "6.  Distributor price list"
	LOCATE , X: PRINT "7.  Wholesale list"
	LOCATE , X: PRINT " "
	LOCATE , X: PRINT "8.  Identical Product list"
	LOCATE , X: PRINT "9.  Decorative Representative list"
	LOCATE , X: PRINT "10. Industrial Representative list"
	LOCATE , X: PRINT "11. Print search codes"
cf0:
	LOCATE 17, X: PRINT CHR$(FNE)
	LOCATE 17, X: PRINT "Enter option..> "; CHR$(FNH);
	A$ = "  "
	CALL inpnew(A$, 2!, updwn%, "13,59" + ALT$): GOSUB ALT
	opt% = VAL(A$)
	IF updwn% = 59 THEN GOTO ENDPGM
	IF opt% < 1 OR opt% > 11 THEN GOTO start
cf1:
	GOSUB get.supcode
	IF updwn% = 59 THEN GOTO ENDPGM
	IF updwn% = 60 THEN GOTO start
cf2:
	GOSUB get.the.activity
	IF updwn% = 59 THEN GOTO ENDPGM
	IF updwn% = 60 THEN GOTO cf1
cf3:
	GOSUB do.list
	GOTO cf0
ENDPGM:
	CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
'//////////////////////////////////////////////////////////////////////////
'>>>>> Lookup index file. Passed skey$. Returns SKEY, 0 if not found. <<<<<
'>>>>> SKEY1, one after insertion place                               <<<<<
'//////////////////////////////////////////////////////////////////////////
searchindex.sup:
	 skey = 0: skey1 = 0: found% = 0
	 IF skey$ = "     " THEN skey1 = 0: RETURN
	 s% = 0: e% = maxsup%
searchagain.sup:
	 p% = (e% - s%) / 2 + s%
	 IF p% = 0 THEN skey = 0: skey1 = s%: RETURN
	 GET #45, p%, supx
	 IF CVI(supx.wrrn$) = 0 THEN LSET supx.wcde$ = STRING$(99, CHR$(255))
	 IF supx.wcde$ + wtyp$ = skey$ THEN skey = p%: skey1 = p%: found% = -1: RETURN
	 IF e% - s% = 1 THEN skey = 0: skey1 = s%: RETURN
	 IF supx.wcde$ + wtyp$ < skey$ THEN s% = p%: GOTO searchagain.sup
	 IF supx.wcde$ + wtyp$ > skey$ THEN e% = p%: GOTO searchagain.sup
	 RETURN
'//////////////////////////////////////////////////////////////////////
'///>
'//////////////////////////////////////////////////////////////////////
get.supcode:
get.supcode.0:
		COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit               F6-Browse";
		supa$ = "*ALL*"
		COLOR 2, 0
		LOCATE 17, X: PRINT "Enter Supplier code ..>"
		LOCATE 17, X + 23
		CALL inpnew(supa$, 105!, updwn%, "13,59-60,64")
				supa$ = UCASE$(supa$)
		IF updwn% = 59 THEN GOTO x.get.supcode
		IF updwn% = 60 THEN GOTO x.get.supcode
		IF updwn% = 64 THEN
			 CALL browse.idx(first.on.screen%, cha%, chb%)
			 p = first.on.screen%
			 GOTO get.supcode.0
			 END IF
		skey$ = supa$: GOSUB searchindex.sup
		rec = 1
		IF skey1 > 0 THEN rec = CVI(supx.wrrn$)
		GET #44, rec, sup
		LOCATE 17, X: PRINT USING "\                           \"; sup.sname$
x.get.supcode:
RETURN
'//////////////////////////////////////////////////////////////////////
'///>
'//////////////////////////////////////////////////////////////////////
get.the.activity:
	activity$ = "A"
540
LOCATE 18, X: PRINT "Active,Extended or All (A/E/*)..>"; activity$; CHR$(FNE)
	LOCATE 18, X + 33
	CALL inpnew(activity$, 101!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.get.the.activity
	IF updwn% = 60 THEN GOTO x.get.the.activity
		activity$ = UCASE$(activity$)
	IF activity$ <> "A" AND activity$ <> "E" AND activity$ <> "*" THEN
		COLOR 14: LOCATE 20, 2
		PRINT "Enter 'A' for active records only, 'E' for Extended list or '*'"
		COLOR 2
		GOTO 540
	END IF
x.get.the.activity:
RETURN
'//////////////////////////////////////////////////////////////////////
'///////     M A S T E R      A C C E S S O R Y      L I S T   ////////
'//////////////////////////////////////////////////////////////////////
do.list:
	OPEN stdout$ FOR OUTPUT AS #99

	savsup$ = "~~~~"
	valsoh = 0: totsoh = 0
	lin = 9999: pag = 0
	vtotstock = 0
	i% = 0:
	CALL index("FIRST", ind%, qk$, 2, keyl%)
	DO WHILE ind% > 0
		i% = i% + 1
		rec% = ind%
		IF rec% < 1 OR rec% > maxacc% THEN GOTO nxtrec
		GET #3, rec%, acstk

		IF INSTR(stdout$, ".wrk") > 0 THEN
			LOCATE 20, 20: PRINT "Printing accessory "; i%: LOCATE 1, 1
		END IF

	 '///////////////////////
	 '>>>>> L1 - Processing
	 '///////////////////////
	'  IF LEFT$(qk$, 4) <> savsup$ THEN
		IF MID$(acstk.suplr$, 1, 4) <> savsup$ THEN
			CALL searchindex(acstk.suplr$, 45, found%)
			asuplr% = CVI(supx.wrrn$)
			IF NOT found% THEN asuplr% = 0

			IF lin > 48 THEN GOSUB heading ' was 51 ajd
			'LSET savsup$ = qk$
			LSET savsup$ = acstk.suplr$

			IF asuplr% < 1 OR asuplr% > maxsup% THEN
				LSET sup.sname$ = acstk.suplr$ + " **UNKNOWN**": sno% = 0
			ELSE
				GET #44, asuplr%, sup
				sno% = CVI(sup.sno$)
			END IF
			sname1$ = SPACE$(28): LSET sname1$ = sup.sname$
			fetch = 1
		END IF
	 '///////////////////////
	 '>>>>> End L1-Processing
	 '///////////////////////

		'>>>-- All Select must be here --------------------------------------
		IF supa$ <> "*ALL*" AND supa$ <> acstk.suplr$ THEN GOTO nxtrec
		ok% = 0
		SELECT CASE activity$
		CASE "A":   IF acstk.active$ = "A" THEN ok% = -1
		CASE "E":   IF acstk.active$ = "A" THEN ok% = -1
					IF acstk.active$ = "a" THEN ok% = -1
		CASE ELSE:  ok% = -1
		END SELECT
		IF NOT ok% THEN GOTO nxtrec
		'>>>-- End of selects -----------------------------------------------
		IF lin > 48 THEN GOSUB heading
		tp% = 0
		IF asuplr% = 282 THEN tp% = -1
		IF asuplr% = 282 THEN tp% = -1
		'>>- Take into account the rounding etc..
		stype$ = sup.stype$
		IF opt% = 1 THEN stype$ = "R"   'Retail
		IF opt% = 2 THEN stype$ = "A"   'Counter
		IF opt% = 3 THEN stype$ = "T"   'Trade
		IF opt% = 4 THEN stype$ = "C"   'Contractor
		IF opt% = 5 THEN stype$ = "I"   'Industrial
		IF opt% = 6 THEN stype$ = "D"   'Distibutor
		IF opt% = 7 THEN stype$ = "W"   'wholesale cost
		IF opt% = 8 THEN stype$ = "A"   'Counter
		CALL rightprice(PRICE!, stype$)

		IF opt% = 9 THEN
			stype$ = "R": CALL rightprice(PRICE!, stype$): price5! = PRICE!
			stype$ = "A": CALL rightprice(PRICE!, stype$): price4! = PRICE!
			stype$ = "T": CALL rightprice(PRICE!, stype$): price3! = PRICE!
			stype$ = "C": CALL rightprice(PRICE!, stype$): price2! = PRICE!
			stype$ = "D": CALL rightprice(PRICE!, stype$): price1! = PRICE!
			END IF
		IF opt% = 10 THEN
			stype$ = "R": CALL rightprice(PRICE!, stype$): price5! = PRICE!
			stype$ = "A": CALL rightprice(PRICE!, stype$): price4! = PRICE!
			stype$ = "T": CALL rightprice(PRICE!, stype$): price3! = PRICE!
			stype$ = "C": CALL rightprice(PRICE!, stype$): price2! = PRICE!
			stype$ = "I": CALL rightprice(PRICE!, stype$): price1! = PRICE!
		END IF
	'// actual print
		IF opt% > 1 THEN A$ = acstk.desc1$: GOSUB 2230: LSET acstk.desc1$ = A$: A$ = acstk.desc2$: GOSUB 2230: LSET acstk.desc2$ = A$
		SELECT CASE opt%
		CASE 1 TO 7:
				IF fetch = 1 THEN
					PRINT #99, USING "!& & &!"; CHR$(15); sup.sname$; sup.sphone$; sup.scont$; CHR$(18)
					PRINT #99, STRING$(79, "-")
					fetch = 0:
					lin = lin + 2 'ajd
				END IF
				PRINT #99, USING "####....\                       \..\        \...\ \ \\ .... ###.## - \        \"; acstk.no%; acstk.desc1$; acstk.desc2$; acstk.size$; acstk.unit$; PRICE!; acstk.search$
				lin = lin + 1
		CASE 8:
				IF acstk.search$ = ACprv.search$ AND acstk.size$ = ACprv.size$ AND acstk.unit$ = ACprv.unit$ THEN
					IF NOT prv.printed% THEN
					PRINT #99, USING "#### \   \-\                       \ \        \.\ \ \\ .. ###.## - \        \ !"; ACprv.No%; ACprv.suplr$; ACprv.desc1$; ACprv.desc2$; ACprv.size$; ACprv.unit$; ACprv.PRICE!; ACprv.search$; acprv.active$:                  _
prv.printed% = -1: lin = lin + 1
					END IF
					PRINT #99, USING "#### \   \-\                       \ \        \.\ \ \\ .. ###.## - \        \ !"; acstk.no%; acstk.suplr$; acstk.desc1$; acstk.desc2$; acstk.size$; acstk.unit$; PRICE!; acstk.search$; acstk.active$
					lin = lin + 1
				ELSE
					prv.printed% = 0
				END IF
				ACprv.No% = acstk.no%
				ACprv.suplr$ = acstk.suplr$
				ACprv.desc1$ = acstk.desc1$
				ACprv.desc2$ = acstk.desc2$
				ACprv.size$ = acstk.size$
				ACprv.unit$ = acstk.unit$
				ACprv.PRICE! = PRICE!
				ACprv.search$ = acstk.search$
				acprv.active$ = acstk.active$

		CASE 9 TO 10:
						IF fetch = 1 THEN PRINT #99, STRING$(79, "-"): PRINT #99, USING "!&!!&-& !"; CHR$(14); sup.sname$; CHR$(20); CHR$(15); " "; sup.sphone$; CHR$(18): fetch = 0: lin = lin + 2
						IF price1! > 99.99 OR price2! > 99.99 THEN
						PRINT #99, USING "#### \                       \\      \ \ \\\ ###.## ###.## ###.## ###.## ###.##"; acstk.no%; acstk.desc1$; acstk.desc2$; acstk.size$; acstk.unit$; price1!; price2!; price3!; price4!; price5!
						ELSE
						PRINT #99, USING "#### \                       \\        \ \ \\\ ##.## ##.## ###.## ###.## ###.##"; acstk.no%; acstk.desc1$; acstk.desc2$; acstk.size$; acstk.unit$; price1!; price2!; price3!; price4!; price5!
						END IF
						lin = lin + 1

		CASE 11:        IF fetch = 1 THEN PRINT #99, STRING$(79, "-"): PRINT #99, USING "!&!!&-& !"; CHR$(14); sup.sname$; CHR$(20); CHR$(15); " "; sup.sphone$; CHR$(18): fetch = 0: lin = lin + 2
						PRINT #99, USING "#### \                       \\        \ \ \\\  |\                   \        "; acstk.no%; acstk.desc1$; acstk.desc2$; acstk.size$; acstk.unit$; acstk.search$
						lin = lin + 1
		CASE ELSE
		END SELECT

		IF stdout$ = "CON" THEN X$ = INPUT$(1)
		'IF i% > 123 THEN EXIT DO
nxtrec:
		CALL index("READ ", ind%, qk$, 2, keyl%)

	LOOP
	PRINT #99, CHR$(18); CHR$(12);
	CLOSE #99

	IF INSTR(stdout$, ".wrk") > 0 THEN
		shella$ = "copy " + stdout$ + " LPT1"
		SHELL shella$
	END IF
	RETURN
	 '///////////////////////////////////////////////////////////////////
	 '///////////      G E N E R A L     H E A D I N G       ////////////
	 '///////////////////////////////////////////////////////////////////
heading:
	pag = pag + 1: lin = 0
	IF pag > 1 THEN PRINT #99, CHR$(12);
	 '/////
	IF opt% = 1 THEN head$ = "R E T A I L    P R I C E    L I S T"
	IF opt% = 2 THEN head$ = "C O U N T E R    P R I C E    L I S T "
	IF opt% = 3 THEN head$ = "T R A D E    P R I C E    L I S T "
	IF opt% = 4 THEN head$ = "C O N T R A C T O R    L I S T  "
	IF opt% = 5 THEN head$ = "I N D U S T R I A L   P R I C E   L I S T  "
	IF opt% = 6 THEN head$ = "D I S T R I B U T O R    L I S T  "
	IF opt% = 7 THEN head$ = "W H O L E S A L E    L I S T"
	IF opt% = 8 THEN head$ = "I D E N T I C A L    P R O D U C T S"
	IF opt% = 9 THEN head$ = "D E C O R A T I V E   R E P R E S E N T I T I V E"
	IF opt% = 10 THEN head$ = "I N D U S T R I A L   R E P R E S E N T I T I V E"
	IF opt% = 1 THEN col$ = "Code Product description                           Size.                 Retail"
	IF opt% = 2 THEN col$ = "Code Product description                           Size.                Counter"
	IF opt% = 3 THEN col$ = "Code Product description                           Size.                 Trade "
	IF opt% = 4 THEN col$ = "Code Product description                           Size.             Contractor"
	IF opt% = 5 THEN col$ = "Code Product description                           Size.     Painter/Industrial"
	IF opt% = 6 THEN col$ = "Code Product description                           Size.            Distributor"
	IF opt% = 7 THEN col$ = "Code Product description                           Size.              Wholesale"
	IF opt% = 8 THEN col$ = "Code Product description                        Size..                  Counter"
	IF opt% = 9 THEN col$ = "Code Product description                       Distr. Contr.  Trade Coun. Ret'l"
	IF opt% = 10 THEN col$ = "Code Product description                       Indus. Contr.  Trade Coun. Ret'l"
	'/////  print actual heading
	PRINT #99, "#acrep01"; TAB(66); "Date:"; DATE1$
	PRINT #99, CHR$(14); company.codesc$
	PRINT #99, "        A C C E S S O R Y   "; head$
	A$ = " "
	IF activity$ = "A" THEN A$ = "Active price list only"
	IF activity$ = "E" THEN A$ = "All active items"
	PRINT #99, A$; TAB(70); "Page:"; pag
	PRINT #99, STRING$(79, "=")
	PRINT #99, col$
	RETURN
	 '//////////////////////////////////////////////////////////////////////
2230 '/////// add .. to the trailing blank chars in a string ///////////////
	 '//////////////////////////////////////////////////////////////////////
	L% = LEN(A$)
	FOR k% = L% TO 1 STEP -1
		IF MID$(A$, k%, 1) <> " " THEN k% = 1: GOTO 2290
		MID$(A$, k%, 1) = "."
2290
	NEXT
	RETURN

SUB browse.idx (firstonscreen%, ch1%, ch2%) STATIC
'$INCLUDE: '\tpmanuf\src\browse01.bi'
END SUB

SUB retail.round (PRICE, round.type$) STATIC
SELECT CASE round.type$
CASE "5 Cents"
	work# = PRICE * 1: dollars% = FIX(work#)
	work# = (PRICE - dollars%) * 10: tens% = FIX(work#)
	work# = (PRICE - dollars% - (tens% / 10)) * 100: digit% = work#
	SELECT CASE digit%
	CASE 0 TO 2: digit% = 0
	CASE 3 TO 5: digit% = 5
	CASE 6 TO 7: digit% = 5
	CASE 8 TO 9: digit% = 10
	CASE -2 TO 0: digit% = 0
	CASE -5 TO -3: digit% = -5
	CASE -7 TO -6: digit% = -5
	CASE -9 TO -8: digit% = -10
	END SELECT
	PRICE = dollars% + tens% / 10 + digit% / 100
CASE ELSE
END SELECT
END SUB

SUB rightprice (PRICE!, stype$) STATIC
'///////////////////////////////////////////
'//// Determine which price to use ////
'///////////////////////////////////////////

	SELECT CASE stype$
	CASE "A": 'Factory Price
				PRICE! = acstk.counter
	CASE "C": 'Contractor Price
				PRICE! = acstk.contract
	CASE "D": 'Distributor Price
				PRICE! = acstk.distributor
	CASE "G": 'Group Price
				PRICE! = acstk.distributor
	CASE "H": 'Hardware Price
				PRICE! = acstk.distributor
	CASE "I": 'Industrial Price
				PRICE! = acstk.industrial
	CASE "M": 'Mitre Ten Price
				PRICE! = acstk.distributor
	CASE "P": 'Painter Price
				PRICE! = acstk.industrial
	CASE "T": 'Trade Price
				PRICE! = acstk.trade
	CASE "Y": 'Group Office Price
				PRICE! = acstk.distributor
	CASE "Z": 'Group store price
				PRICE! = acstk.distributor
	CASE "W": 'Best Possible Price
				PRICE! = acstk.wholesalecost
	CASE ELSE: 'All Other Codes Are Retail Price
				PRICE! = acstk.retail
	END SELECT

	'IF acstk.pack% < 1 THEN acstk.pack% = 1
	'price!= price! / pack%



END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB
