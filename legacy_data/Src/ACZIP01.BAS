DECLARE SUB clrrcdfmt ()
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
	'>>>>>>>>>>>>>>>> ACZIP01 - Accessory file compress <<<<<<<<<<<<<<<<<<<<
	'///////////////////////////////////////////////////////////////////////
'.dc - Complete
	'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
	apgm$ = "fimenu"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	keyl% = 7
	qk$ = SPACE$(keyl%)
	cursup$ = "     ": savsup$ = "@@@@@": skey$ = "     "
	ag$ = "20"
	CALL setup("ACCESSORY FILES COMPRESS")
	LOCATE 25, 4: COLOR 0, 3: PRINT "F1-Exit"; : COLOR 2, 0
	COLOR 2: x = 24
	LOCATE 6, x - 8: PRINT "  This is a major file compression."

350  T$ = "N"
	LOCATE 8, x: PRINT "Are you sure (Y/N)..> ";
	CALL inpnew(T$, 101!, updwn%, "59,13")
	T$ = UCASE$(T$)
	IF updwn% = 59 THEN T$ = "N"
	IF T$ <> "Y" THEN CLOSE : GOTO endpgm

	BEEP
	T$ = "N"
	LOCATE 8, x - 8: PRINT "This program will destroy the links between"
	LOCATE , x - 8: PRINT "the orders in the system and stock file,"
	LOCATE , x - 8: PRINT ""
	LOCATE , x - 8: PRINT "                 N O W  "
	LOCATE , x - 8: PRINT ""
	LOCATE , x - 8: PRINT "NOTE: The index must be built before and after "
	LOCATE , x - 8: PRINT "      this program run. Records may be lost."
	LOCATE , x - 8: PRINT ""
	LOCATE , x: PRINT "Are you REALLY sure (Y/N)..> ";
	CALL inpnew(T$, 101!, updwn%, "59,13")
		T$ = UCASE$(T$)
	IF updwn% = 59 THEN T$ = "N"
	IF T$ <> "Y" THEN CLOSE : GOTO endpgm
	'
360  LOCATE 15, x: PRINT "Enter supplier gap (20)..>"; ag$;
	LOCATE 15, x + 26
	CALL inpnew(ag$, 2!, updwn%, "59,13")
	IF updwn% = 59 THEN GOTO 350
	anew% = VAL(ag$)
	IF anew% < 2 THEN 360
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\ACSTK.INC'
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	DB.OR.CR$ = "CR"
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxhst% = CVI(msmisc.max4$): maxacc% = CVI(msmisc.max5$)
	'
	DIM k%(maxacc%), s$(maxacc%), h%(15)
	'
	anew% = anew% - 1'ADJUST
	'//// Open Output files ////
		OPEN "acstk.new" FOR RANDOM AS #10 LEN = 160: CLOSE #10
		KILL "acstk.new"
		OPEN "acstk.new" FOR RANDOM AS #10 LEN = 160
	'////////////////////////////
	GOSUB filecompress
	CLOSE

endpgm:
	CALL exitpgm(apgm$)
	CHAIN apgm$
	END
	'//////////////////////////////////////////////////////////////////////////
540  '\\\\\ Lookup index file Passed skey$ Returns SKEY, 0 if not found \\\\\
	'///// SKEY1, one after insertion place                               /////
	'//////////////////////////////////////////////////////////////////////////
	skey = 0: skey1 = 0
	IF skey$ = "    " THEN skey1 = 0: GOTO 650
	s% = 0: e% = maxsup%
590 P% = (e% - s%) / 2 + s%
IF P% < 1 THEN P% = 1
	GET #45, P%, supx
	IF supx.wcde$ = skey$ THEN skey = P%: skey1 = P%: GOTO 650
	IF e% - s% = 1 THEN skey = 0: skey1 = s%: GOTO 650
	IF supx.wcde$ < skey$ THEN s% = P%: GOTO 590
	IF supx.wcde$ > skey$ THEN e% = P%: GOTO 590
650  RETURN
	 '//////////////////////////////////////////////////////////////////////
	'///////     A C C E S S O R Y    F I L E   C O M P R E S S      //////
	'//////////////////////////////////////////////////////////////////////
filecompress:
	'<<<<<<<<<<<<<<  O P E N  I N D E X
	CALL index("OPEN ", ind%, "acstkx2.acf", 2, keyl%)
	osuplr$ = "~~": n% = 0
	'
	CALL setup("FILE COMPRRESS IN PROGRESS")
	supcnt% = 9999: thissup% = 0: rec2% = 0: extra% = 1
	LOCATE 4, 3: PRINT "  Records      Records      Number of    Records    Rec/this"
	LOCATE 5, 3: PRINT "   Read        Written      Suppliers    Skipped    Supplier"
	LOCATE 6, 65: PRINT "Per/supplier"
	LOCATE 7, 2: PRINT "Supplier Name   Typr  Phone  Contact "
	'
	i% = 0: ind% = 0: rec1% = 0
	CALL index("FIRST", ind%, qk$, 2, keyl%)
	DO WHILE ind% > 0
		i% = i% + 1
		rec% = ind%
		GET #3, rec%, acstk: rec1% = rec1% + 1
		IF rec% MOD 100 = 0 THEN
			LOCATE 3, 26: PRINT USING "Reading record ##,###"; rec%
		END IF
		'///////////////////////
		'/// L1 - Processing ///
		'///////////////////////
		LSET cursup$ = qk$
		IF cursup$ <> savsup$ THEN
			LSET savsup$ = cursup$
			skey$ = cursup$: GOSUB 540
			wrrn% = CVI(supx.wrrn$): IF wrrn% < 1 OR wrrn% > maxsup% THEN skey = 0
			IF skey = 0 THEN LSET sup.sname$ = "** UNKNOWN**": GOTO 1390
			GET #44, wrrn%, sup
1390
			IF supcnt% = 9999 THEN supcnt% = 0: GOTO 1420
			'///////  clear out records /////
			GOSUB addblanks
			GET #3, rec%, acstk
1420
			lin% = supcnt% MOD 15: LOCATE lin% + 7, 2
			supcnt% = supcnt% + 1
			PRINT USING "\                   \   \ \-\         \ &"; sup.sname$; "   "; sup.sphone$; sup.scont$; : LOCATE , 65: COLOR 14: PRINT "<--Writing ": COLOR 2
		END IF
		'/////////////////////////
		'//// End L1-Processing///
		'/////////////////////////
		thissup% = thissup% + 1
		IF thissup% > anew% THEN thissup% = 1: extra% = extra% + 1
		IF rec1% MOD 100 = 0 THEN
			LOCATE 6, 2
			PRINT USING "  #####      #####          #####        #####      #####"; rec1%; rec2% + 1; supcnt%; rec2% - rec1% + 1; (extra% - 1) * anew% + thissup%
		END IF
		rec2% = rec2% + 1
		acstk.no% = rec2%
		PUT #10, , acstk
		'
		CALL index("READ ", ind%, qk$, 2, keyl%)
	LOOP
	'
	GOSUB addblanks '//// add up to ANEW records////
	IF thissup% MOD 10 = 0 THEN
		LOCATE 6, 2
		PRINT USING "  #####      #####          #####        #####      #####"; rec1%; rec2% + 1; supcnt%; rec2% - rec1% + 1; thissup%
		END IF
	RETURN
	'
	'//////////////////////////////////////
	'///////  clear out blank records /////
	'//////////////////////////////////////
addblanks:
	'
	FOR i% = 1 TO anew%'****** THISSUP%+1 TO 48
		'>>>>> Delete integers
		CALL clrrcdfmt
		acstk.no% = rec2%
		rec2% = rec2% + 1
		PUT #10, , acstk
	NEXT
	LOCATE lin% + 7, 65: PRINT USING "#####      "; extra% * anew% + thissup%: thissup% = 0: extra% = 1
	RETURN
	'

SUB clrrcdfmt
		sp99$ = SPACE$(99)
		acstk.no% = 0
		acstk.search = sp99$
		acstk.suplr = sp99$
		acstk.search = sp99$
		acstk.desc1 = sp99$
		acstk.desc2 = sp99$
		acstk.suplr = sp99$
		acstk.size = sp99$
		acstk.unit = sp99$
		acstk.pack = 0
		acstk.dgflag = sp99$
		acstk.taxinc = sp99$
		acstk.salestaxcde = sp99$
		acstk.purcost = 0
		acstk.purtax = 0
		acstk.disccdeone = sp99$
		acstk.disccdetwo = sp99$
		acstk.wholesalecost = 0
		acstk.filler4$ = SPACE$(4)
		'acstk.wholesale-tax = 0
		acstk.retailcde = sp99$
		acstk.countercde = sp99$
		acstk.tradecde = sp99$
		acstk.contractcde = sp99$
		acstk.industrialcde = sp99$
		acstk.distributorcde = sp99$
		acstk.retail = 0
		acstk.counter = 0
		acstk.trade = 0
		acstk.contract = 0
		acstk.industrial = 0
		acstk.distributor = 0
		acstk.suplr4stdcost$ = SPACE$(5)
		acstk.search4stdcost$ = SPACE$(10)
		'acstk.retail-tax = 0
		'acstk.counter-tax = 0
		'acstk.trade-tax = 0
		'acstk.contract-tax = 0
		'acstk.industrial-tax = 0
		'acstk.distributor-tax = 0
		acstk.soh = 0
		acstk.active = sp99$
		acstk.sold = 0
		acstk.date = sp99$

END SUB
