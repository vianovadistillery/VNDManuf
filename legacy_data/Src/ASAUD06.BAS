DECLARE SUB dolist (mth$, ok%)
DECLARE SUB dowrite (mth$, ok%)
DECLARE SUB load (mth$, ok%)
DECLARE SUB searchindex (keyin$, chi%, found%)
'///////////////////////////////////////////////////////////////////////
'>>> ASAUD06 - LOAD/UNLOAD  OPENING BALANCES FROM FILE
'///////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
pgm$ = "asaud01"
'$ NCLUDE: '\tpmanuf\src\pgmerr.inc'
	RESET
	DIM SHARED rrn%(999), rrn%, maxsup%

	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	'$INCLUDE: '\tpmanuf\src\ASOPNBAL.INC'
	'$INCLUDE: '\tpmanuf\src\CUS.INC'
	'$INCLUDE: '\tpmanuf\src\CUSX.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$)
	maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$): maxcus% = CVI(msmisc.max7$)
	IF cr.or.db$ = "CREDITORS" THEN
		maxsup% = maxsup%
		ELSE
		maxsup% = maxcus%
		END IF
START:
	CALL setup("LOAD/UNLOAD OPENING BALANCES FROM FILE")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : COLOR 2, 0
	IF cr.or.db$ = "CREDITORS" THEN
		COLOR 4
		LOCATE 5, 29: PRINT "C R E D I T O R S"
		ELSE
		COLOR 12
		LOCATE 5, 29: PRINT "  D E B T O R S "
		END IF

	cont$ = " "
	mth$ = "$$$$"
cf1:
	COLOR 2
	LOCATE 7, 18: PRINT "Load opening balances from file or"
	LOCATE 8, 18: PRINT "Write opening balances to a file (L/W)..>"; cont$
	DO
		LOCATE 8, 59
		CALL inpnew(cont$, 101!, updwn%, "13,59-60,64" + ALT$): GOSUB ALT
		IF updwn% = 64 THEN CALL dolist(mth$, ok%): GOTO START
				cont$ = UCASE$(cont$)
		IF updwn% = 59 THEN GOTO ENDPGM
		LOOP UNTIL cont$ = "L" OR cont$ = "W"

cf2:
	LOCATE 10, 18: PRINT "Which month (YYMM)..>"; mth$
	DO
		LOCATE 10, 39
		CALL inpnew(mth$, 104!, updwn%, "13,59-60,64" + ALT$): GOSUB ALT
		IF updwn% = 64 THEN CALL dolist(mth$, ok%): GOTO START
		IF updwn% = 59 THEN GOTO ENDPGM
		IF updwn% = 60 THEN GOTO cf1
		ok% = -1
		IF MID$(mth$, 1, 2) > "99" OR MID$(mth$, 1, 2) < "00" THEN ok% = 0
		IF MID$(mth$, 3, 2) > "12" OR MID$(mth$, 3, 2) < "01" THEN ok% = 0
		IF mth$ = "$$$$" THEN ok% = -1
		LOOP UNTIL ok%


	SELECT CASE cont$
	CASE "L": CALL load(mth$, ok%)
	CASE "W": CALL dowrite(mth$, ok%)
	CASE ELSE
	END SELECT

	GOTO START

ENDPGM:
	CLOSE
	CALL exitpgm(pgm$)
	CHAIN pgm$

SUB dolist (mth$, ok%) STATIC
	COLOR 6, 0
	LOCATE 4, 12: PRINT "Rec. Month   Cust.    Current   30 days   60 days   90 days"
	COLOR 2, 0

	rec% = 1
	oplast% = LOF(54) / LEN(opnbal)
DOLIST0:

	IF rec% < 1 OR rec% > oplast% THEN rec% = 1
	lin% = 999
	GET #54, rec%, opnbal
	DO WHILE NOT EOF(54)
	IF opnbal.mth$ = mth$ THEN
		lin% = lin% + 1: IF lin% > 20 THEN lin% = 5

		LOCATE lin%, 12
		PRINT USING "#### '\  \'  \    \ ##,###.## ##,###.## ##,###.## ##,###.##"; opnbal.rec%; opnbal.mth$; opnbal.cust$; opnbal.cur!; opnbal.o30!; opnbal.o60!; opnbal.o90!

		IF lin% = 20 THEN
			LOCATE 22, 12: PRINT "Next.. ";
			a$ = ""
			LOCATE 22, 18
			CALL inpnew(a$, 104!, updwn%, "13,59")
			IF updwn% = 59 THEN EXIT DO
			IF VAL(a$) > 0 THEN rec% = VAL(a$): GOTO DOLIST0
			END IF
		END IF

	GET #54, , opnbal: rec% = rec% + 1
	LOOP

	LOCATE 22, 12: PRINT "F1-Exit.. ";

	IF updwn% <> 59 THEN
		a$ = ""
		LOCATE 22, 21
		CALL inpnew(a$, 104!, updwn%, "59")
		IF VAL(a$) > 0 THEN rec% = VAL(a$): GOTO DOLIST0
		END IF

END SUB

SUB dowrite (mth$, ok%)
	'>> Read through existing opening balance file and clear out old copiews of this month
	'>> Load the address of the empty records in an array
	rrn% = 0
	rec% = 1
	GET #54, rec%, opnbal
	DO WHILE NOT EOF(54)
		IF opnbal.rec% <> rec% OR opnbal.mth$ = mth$ THEN
			rrn% = rrn% + 1: IF rrn% > 999 THEN rrn% = 999
			rrn%(rrn%) = rec%
			END IF

		GET #54, , opnbal: rec% = rec% + 1
		LOOP

	'>> The rrn() must hold all the possible addresses for the records.
	'>> add the number of customers to the rrn array
	adlast% = LOF(43) / LEN(cus)
	opnlast% = LOF(54) / LEN(opnbal)
	needed% = adlast% - rrn% + 1
	FOR i% = 1 TO needed%
		rrn% = rrn% + 1: rrn%(rrn%) = opnlast% + i%
		NEXT
	'> Now rrn() hold the addresses for all the records
	n.rrn% = rrn%

	COLOR 6, 0
	LOCATE 18, 12: PRINT "Rec. Month   Cust.    Current   30 days   60 days   90 days"
	COLOR 2, 0
	'>> Read through customers and write to file <<
	rec% = 1
	rrn% = 0
	GET #43, rec%, cus
	DO WHILE NOT EOF(43)
		opnbal.rec% = 0
		opnbal.mth$ = mth$
		opnbal.cust$ = UCASE$(cus.search$ + cus.stype$)
		opnbal.cur! = CVS(cus.opn$)
		opnbal.o30! = CVS(cus.opn30$)
		opnbal.o60! = CVS(cus.opn60$)
		opnbal.o90! = CVS(cus.opn90$)
		ok% = 0
		IF opnbal.cur! <> 0 THEN ok% = -1
		IF opnbal.o30! <> 0 THEN ok% = -1
		IF opnbal.o60! <> 0 THEN ok% = -1
		IF opnbal.o90! <> 0 THEN ok% = -1
		IF ok% THEN
			rrn% = rrn% + 1
			opnbal.rec% = rrn%(rrn%)
			PUT #54, rrn%(rrn%), opnbal
			END IF

		IF rec% MOD 50 = 0 THEN
			LOCATE 19, 12: PRINT USING "#### '\  \'  \    \ ##,###.## ##,###.## ##,###.## ##,###.##"; opnbal.rec%; opnbal.mth$; opnbal.cust$; opnbal.cur!; opnbal.o30!; opnbal.o60!; opnbal.o90!
			END IF
		GET #43, , cus: rec% = rec% + 1
		LOOP
	currec% = rec%
	FOR rec% = currec% + 1 TO n.rrn%
		opnbal.rec% = 0
		opnbal.mth$ = "    "
		opnbal.cust$ = "    "
		opnbal.cur! = 0
		opnbal.o30! = 0
		opnbal.o60! = 0
		opnbal.o90! = 0
		rrn% = rrn% + 1
		PUT #54, rrn%(rrn%), opnbal
		NEXT


END SUB

SUB load (mth$, ok%) STATIC
	'>> Clear out all customers first <<
	rrn% = 0
	rec% = 1
	GET #43, rec%, cus
	DO WHILE NOT EOF(43)
		IF rec% MOD 50 = 0 THEN
			LOCATE 15, 20: PRINT USING "#### Clearing all customers"; rec%
			END IF
		LSET cus.opn$ = MKS$(0)
		LSET cus.opn30$ = MKS$(0)
		LSET cus.opn60$ = MKS$(0)
		LSET cus.opn90$ = MKS$(0)
		PUT #43, rec%, cus
		GET #43, , cus: rec% = rec% + 1
		LOOP
	'>> Now load from the file <<
	COLOR 6, 0
	LOCATE 18, 12: PRINT "Rec. Month   Cust.    Current   30 days   60 days   90 days"
	COLOR 2, 0

	rec% = 1
	GET #54, rec%, opnbal
	DO WHILE NOT EOF(54)
	IF opnbal.mth$ = mth$ THEN
		keyin$ = opnbal.cust$: chi% = 23
		CALL searchindex(keyin$, chi%, found%)
		sno% = CVI(supx.wrrn$)
		IF found% = 0 THEN sno% = 0
		IF sno% >= 1 AND sno% <= maxsup% THEN
			GET #43, sno%, cus
			IF CVI(cus.sno$) <> sno% THEN sno% = 0 '> Error

			IF rec% MOD 50 = 0 THEN
			LOCATE 15, 12: PRINT USING "&-&"; opnbal.cust$; cus.sname$
			LOCATE 19, 12: PRINT USING "#### '\  \'  \    \ ##,###.## ##,###.## ##,###.## ##,###.##"; opnbal.rec%; opnbal.mth$; opnbal.cust$; opnbal.cur!; opnbal.o30!; opnbal.o60!; opnbal.o90!
			END IF

			END IF

		IF sno% >= 1 THEN
			GET #43, sno%, cus
			LSET cus.opn$ = MKS$(opnbal.cur)
			LSET cus.opn30$ = MKS$(opnbal.o30)
			LSET cus.opn60$ = MKS$(opnbal.o60)
			LSET cus.opn90$ = MKS$(opnbal.o90)
			PUT #43, sno%, cus
			ELSE

			IF opnbal.cust$ <> "     " THEN
			SOUND 54, 1
			rrn% = rrn% + 1: rrn%(rrn%) = rec%
			END IF

			END IF
		END IF
		GET #54, , opnbal: rec% = rec% + 1
		LOOP

IF rrn% = 0 THEN GOTO x.load

	'>>-----------------------------------------<<
	'>> List all the records that did not match <<
	'>>-----------------------------------------<<
	br.start% = 1
BR.ERRORS:
	COLOR 6, 0
	LOCATE 3, 25: PRINT "Records without current customer details"
	LOCATE 4, 12: PRINT "Rec. Month   Cust.    Current   30 days   60 days   90 days"
	COLOR 2, 0
	LOCATE 5, 2
	IF br.start% < 1 OR br.start% > rrn% THEN br.start% = 1
	br.end% = br.start% + 16: IF br.end% > rrn% THEN br.end% = rrn%
	n% = 4
	FOR rec% = br.start% TO br.end%
		GET #54, rrn%(rec%), opnbal
		n% = n% + 1
		LOCATE n%, 4: PRINT USING "####"; rec%
		LOCATE n%, 12: PRINT USING "#### '\  \'  \    \ ##,###.## ##,###.## ##,###.## ##,###.##"; opnbal.rec%; opnbal.mth$; opnbal.cust$; opnbal.cur!; opnbal.o30!; opnbal.o60!; opnbal.o90!
		NEXT
	FOR i% = n% + 1 TO 4 + 16
		LOCATE i%, 2: PRINT SPACE$(75)
		NEXT


	LOCATE 3, 2: PRINT "Start from..>";
	a$ = ""
	CALL inpnew(a$, 4!, updwn%, "59,13")
	IF updwn% = 13 THEN
		br.start% = VAL(a$)
		GOTO BR.ERRORS
		END IF


x.load:
END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

