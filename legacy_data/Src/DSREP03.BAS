DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB dsplywho (selitem%)
'.dc - Complete
'///////////////////////////////////////////////////////////////////////
'///   L I S T   O F   S T O C K   O N   O R D E R
'///////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	acstkf$ = "ACF"
	apgm$ = "DSMENU"
	DIM qty%(10000), orn$(5000)
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	keyl% = 20: qk$ = SPACE$(keyl%)
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\ACSTK.inc'
	'$INCLUDE: '\tpmanuf\src\cus.INC'
	'$INCLUDE: '\tpmanuf\src\cusx.INC'
	'$INCLUDE: '\tpmanuf\src\supx.INC'
	'$INCLUDE: '\tpmanuf\src\ORDHED.INC'
	'$INCLUDE: '\tpmanuf\src\ORDDET.INC'
	CALL index("OPEN ", ind%, "acstkx3.acf", 7, keyl%)
	'stdout$ = "CON"
	stdout$ = "DSREP03.PRT"
	OPEN stdout$ FOR OUTPUT AS #99
'///////////////////////////////////////////////////////////////////////
'>>>>  M A I N L I N E
'///////////////////////////////////////////////////////////////////////
start:
	CALL setup("STOCK REPORTS")
	LOCATE 25, 4: COLOR 0, 3: PRINT "F1-Exit";
	COLOR 2, 0
	LOCATE 10, 23: PRINT "1...Stock on order report"
	LOCATE 11, 23: PRINT "2...Stock on Backorder report"
	LOCATE 12, 23: PRINT "3...Out of stock report"
	LOCATE 13, 23: PRINT "4...Display where items are used"
	LOCATE 14, 23: PRINT "5...Repair Order Detail file"
	LOCATE 15, 23: PRINT "9...Page eject"
getopt:
	LOCATE 16, 23: PRINT "Option..> "; CHR$(fnh);
	CALL inpnew(OPT$, 1!, updwn%, "13,59" + alt$): GOSUB alt
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	OPT% = VAL(OPT$)
	IF OPT% = 9 THEN LPRINT CHR$(12);
	IF OPT% < 1 OR OPT% > 5 THEN GOTO getopt

	IF OPT% = 4 THEN
		CALL dsplywho(selitem%)
		GOTO start
	END IF
	IF OPT% = 5 THEN
		CLOSE
		apgm$ = "ASBLD03"
		CALL exitpgm(apgm$)
		CHAIN apgm$
		GOTO start
	END IF


	'>>>-- Cont
	maxdordq% = 0
	i% = 1
	GET #49, i%, orddet
	DO
		dord% = orddet.dord%
		ditem% = CVI(orddet.ditem$)
		dordq% = CVI(orddet.dordq$)
		ok% = 0
		IF OPT% <> 2 AND dordq% > 0 AND dord% > 0 THEN ok% = -1
		IF OPT% = 2 AND dordq% > 0 AND dord% > 0 AND orddet.dbo$ = "Y" THEN ok% = -1
		IF ok% THEN
			qty%(ditem%) = qty%(ditem%) + dordq%
			IF ditem% < 5000 THEN
				orn$(ditem%) = orn$(ditem%) + STR$(dord%)
			END IF
			IF ditem% > maxdordq% THEN maxdordq% = ditem%
		END IF
		GET #49, , orddet: i% = i% + 1
		IF i% MOD 100 = 0 THEN LOCATE 18, 30: PRINT i%
	LOOP WHILE NOT EOF(49)
'///////////////////////////////////////////////////////////////////////
'/// DO THE ACTUAL PRINT
'///////////////////////////////////////////////////////////////////////
	pag% = 0: lin% = 9999
	FOR i% = 1 TO maxdordq%
		SELECT CASE OPT%
		CASE 1, 2: 'Stock on order report,backorder
			IF qty%(i%) > 0 THEN
				IF lin% > 45 THEN GOSUB heading
				GET #3, i%, acstk
				tmp$ = "N/A"
				IF i% < 5000 THEN
					tmp$ = orn$(i%)
				END IF
				PRINT #99, USING "#### & &  & & ###,### &"; i%; acstk.desc1$; acstk.desc2$; acstk.size$; acstk.unit$; qty%(i%); tmp$
				lin% = lin% + 1
			END IF

		CASE 3: 'Out of stock report
			IF qty%(i%) > acstk.soh THEN
				IF lin% > 45 THEN GOSUB heading
				diff = qty%(i%) - acstk.soh
				GET #3, i%, acstk
				PRINT #99, USING "#### & &  & & ###,### ###,###     ###,###"; i%; acstk.desc1$; acstk.desc2$; acstk.size$; acstk.unit$; qty%(i%); acstk.soh; diff
				lin% = lin% + 1
			END IF
		CASE ELSE
		END SELECT
		NEXT
	PRINT #99, CHR$(12);
	CLOSE
	SHELL "COPY DSREP03.PRT LPT1"
	CALL exitpgm(apgm$)
	CHAIN apgm$
'///////////////////////////////////////////////////////////////////
'///////////      G E N R A L      H E A D I N G       ////////////
'///////////////////////////////////////////////////////////////////
heading:
	pag% = pag% + 1: lin% = 0
	IF pag% > 1 THEN PRINT #99, CHR$(12);
	'/////
	IF OPT% = 1 THEN head$ = "S T O C K    O N    O R D E R "
	IF OPT% = 2 THEN head$ = "S T O C K    O N   B A C K O R D E R "
	IF OPT% = 3 THEN head$ = "O U T    O F    S T O C K    R E P O R T"
	'/////
	IF OPT% = 1 THEN col$ = "P/No. Product                              Size/Ut    Qty    Orders.   "
	IF OPT% = 2 THEN col$ = "P/No. Product                              Size/Ut    Qty    Orders.   "
	IF OPT% = 3 THEN col$ = "P/No. Product                              Size/Ut    Ord.     SOH        Reqd."
	'/////  print actual heading
	PRINT #99, "#asrep03"; TAB(66); "Date:"; date1$
	PRINT #99, TAB(66); "Time:"; TIME$
	PRINT #99, " "
	PRINT #99, CHR$(14); cc$
	PRINT #99, " "
	PRINT #99, SPC(18); head$
	PRINT #99,
	PRINT #99, TAB(72); "Page:"; pag%
	PRINT #99, STRING$(79, "=")
	PRINT #99, col$
	PRINT #99, STRING$(79, "-")
	RETURN

SUB dsplywho (selitem%) STATIC

	CALL setup("CUSTOMERS OUTSTANDING ORDERS")
	LOCATE 25, 4: COLOR 0, 3: PRINT "F1-Exit";
	COLOR 2, 0
	keyl% = 20: qk$ = SPACE$(keyl%)
	maxacc% = 9999

dsplywho0:
	COLOR 2, 0
	LOCATE 3, 20: PRINT "Enter stock item...> "
	LOCATE 3, 40
	CALL inpnew(in$, 118!, updwn%, "13,59,60,62")
	IF updwn% = 59 THEN GOTO x.dsplywho
	in$ = UCASE$(in$)

	IF VAL(in$) > 1 AND VAL(in$) < maxacc% THEN
		selitem% = VAL(in$)
	ELSE

		LSET qk$ = in$
		CALL index("CHAIN", ind%, qk$, 7, keyl%)
		IF ind% < 0 AND qk$ < search.key$ THEN CALL index("READ ", ind%, qk$, 7, keyl%)
		IF ind% < 0 THEN ind% = 0 - ind%
		selitem% = ind%
	END IF

	GET #3, selitem%, acstk

	CALL box(2, 4, 79, 22, 0, 0, 0)
	COLOR 2, 0
	LOCATE 4, 2
	PRINT USING "Searching for #### & &"; selitem%; acstk.desc1$; acstk.desc2$
	COLOR 6, 0
	LOCATE 5, 2: PRINT " Cust.  ord   Cust.  ord   Cust.  ord   Cust.  ord   Cust.  ord   Cust.  ord  "
	COLOR 2, 0

	i% = 1:  lin% = 0: col% = 0
	GET #49, i%, orddet
	DO
		IF orddet.dord% > 0 AND CVI(orddet.ditem$) = selitem% THEN
			hord% = orddet.dord%
			IF hord% > 0 AND hord% < 9999 THEN
				GET #48, hord%, ordhed
				keyin$ = ordhed.hsup$
				CALL searchindex(keyin$, 23, found%)
				ano% = CVI(supx.wrrn$)
				IF ano% < 1 OR ano% > maxsup% THEN ano% = 1

				GET #43, ano%, CUS
				ditem% = CVI(orddet.ditem$)
				dordq% = CVI(orddet.dordq$)

				lin% = lin% + 1
				IF lin% > 15 THEN lin% = 1: col% = col% + 1:
				IF col% > 5 THEN col% = 5: lin% = 15: plus$ = "++"

				LOCATE lin% + 5, col% * 13 + 2
				PRINT USING " \   \####\\³"; CUS.search$ + CUS.stype$; hord%; plus$
				END IF
				END IF

		IF i% MOD 100 = 0 THEN LOCATE 22, 2: PRINT USING "####"; i%

		GET #49, , orddet: i% = i% + 1
		LOOP WHILE NOT EOF(49)

	GOTO dsplywho0

x.dsplywho:

END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

