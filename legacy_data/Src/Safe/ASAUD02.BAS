DECLARE SUB sub.one (mth$, mthless1$)
DECLARE SUB dolist (mthless1$, ok%)
DECLARE SUB doload (mth$, mthless1$, ok%, chkonly%)
DECLARE SUB dowrite (mthless1$, ok%)
DECLARE SUB searchindex (keyin$, chi%, found%)
'///////////////////////////////////////////////////////////////////////
'>>> ASAUD06 - LOAD/UNLOAD  OPENING BALANCES FROM FILE
'///////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
pgm$ = "asaud01"
'$ NCLUDE: '\tpmanuf\src\pgmerr.inc'
	RESET
	DIM SHARED rrn%(1100), rrn%, maxsup%, cha%, chb%

	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	'$INCLUDE: '\tpmanuf\src\ASclobal.INC'
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\CUSX.INC'
	'$INCLUDE: '\tpmanuf\src\CUS.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
'>>>---------------------------------------------------<<<
'>>> NOTE: This program is for Suppliers and Customers
'>>>       Pass parm of  /CR or /DB
'>>>---------------------------------------------------<<<
	db.or.cr$ = "DB"
	db.or.cr$ = ENVIRON$("DB.OR.CR$")
	cr% = INSTR(COMMAND$, "/CR")
	cr% = 1 '<<<-Swap to CR. System use cr% = 1
	'IF cr% > 0 THEN db.or.cr$ = "CR"

	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$)
	maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$): maxcus% = CVI(msmisc.max7$)
	 IF db.or.cr$ = "CR" THEN
		cha% = 45: chb% = 44: maxsup% = maxsup%
		ELSE
		cha% = 23: chb% = 43: maxsup% = maxcus%
	 END IF



START:
	CALL setup("LOAD/UNLOAD OPENING BALANCES FROM FILE")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit                                  C - Check only"; : COLOR 2, 0
	IF db.or.cr$ = "CR" THEN
		COLOR 4
		LOCATE 5, 29: PRINT "C R E D I T O R S"
		ELSE
		COLOR 12
		LOCATE 5, 29: PRINT "  D E B T O R S "
		END IF

	cont$ = " "
	mth$ = "$$$$"
	mth$ = msmisc.DBmonth$
	IF cha% = 45 THEN mth$ = msmisc.CRmonth$
	CALL sub.one(mth$, mthless1$)


cf1:
	COLOR 2
	LOCATE 7, 18: PRINT "Load opening balances from file or"
	LOCATE 8, 18: PRINT "Write opening balances to a file (L/W)..>"; cont$
	DO
		LOCATE 8, 59
		CALL inpnew(cont$, 101!, updwn%, "13,59-60,64" + ALT$): GOSUB ALT
		IF updwn% = 64 THEN CALL dolist(mthless1$, ok%): GOTO START
				cont$ = UCASE$(cont$)
		IF updwn% = 59 THEN GOTO ENDPGM
		LOOP UNTIL cont$ = "L" OR cont$ = "W" OR cont$ = "C"

cf2:
	LOCATE 10, 18: PRINT "Opening Balance for (MMYY)..>"; mthless1$
	DO
		LOCATE 10, 47
		CALL inpnew(mth$, 104!, updwn%, "13,59-60,64" + ALT$): GOSUB ALT
		IF updwn% = 64 THEN CALL dolist(mth$, ok%): GOTO START
		IF updwn% = 59 THEN GOTO ENDPGM
		IF updwn% = 60 THEN GOTO cf1
		ok% = -1
		IF MID$(mth$, 1, 2) > "12" OR MID$(mth$, 1, 2) < "01" THEN ok% = 0
		IF MID$(mth$, 3, 2) > "99" OR MID$(mth$, 3, 2) < "00" THEN ok% = 0
		IF mth$ = "$$$$" THEN ok% = -1
		LOOP UNTIL ok%

	CALL sub.one(mth$, mthless1$)

	asclobal$ = "DBCL$$$$.ASF"
	IF cha% = 45 THEN asclobal$ = "CRCL$$$$.ASF"
	MID$(asclobal$, 5, 4) = mthless1$
	IF mth$ = "$$$$" THEN asclobal$ = "ASclobal.ASF"

	OPEN asclobal$ FOR RANDOM SHARED AS #60 LEN = 48
	
	SELECT CASE cont$
	CASE "C": chkonly% = -1: CALL doload(mth$, mthless1$, ok%, chkonly%)
	CASE "L": chkonly% = 0: CALL doload(mth$, mthless1$, ok%, chkonly%)
	CASE "W": CALL dowrite(mthless1$, ok%)
	CASE ELSE
	END SELECT

	CLOSE #60

	GOTO START

ENDPGM:
	CLOSE
	CALL exitpgm(pgm$)
	CHAIN pgm$

SUB dolist (mthless1$, ok%) STATIC

	asclobal$ = "DBCL$$$$.ASF"
	IF cha% = 45 THEN asclobal$ = "CRCL$$$$.ASF"
	MID$(asclobal$, 5, 4) = mthless1$
	IF mthless1$ = "$$$$" THEN asclobal$ = "ASclobal.ASF"

	OPEN asclobal$ FOR RANDOM SHARED AS #60 LEN = 48

	COLOR 6, 0
	LOCATE 4, 12: PRINT "Rec. Month   Cust.    Current   30 days   60 days   90 days"
	COLOR 2, 0

	rec% = 1
	oplast% = LOF(60) / LEN(clobal)
DOLIST0:

	IF rec% < 1 OR rec% > oplast% THEN rec% = 1
	lin% = 999
	GET #60, rec%, clobal
	DO WHILE NOT EOF(60)
	IF clobal.mth$ = mthless1$ THEN
		lin% = lin% + 1: IF lin% > 20 THEN lin% = 5

		LOCATE lin%, 12
		PRINT USING "#### '\  \'  \    \ ##,###.## ##,###.## ##,###.## ##,###.##"; clobal.rec%; clobal.mth$; clobal.cust$; clobal.ocur!; clobal.o30!; clobal.o60!; clobal.o90!

		IF lin% = 20 THEN
			LOCATE 22, 12: PRINT "Next.. ";
			a$ = ""
			LOCATE 22, 18
			CALL inpnew(a$, 104!, updwn%, "13,59")
			IF updwn% = 59 THEN EXIT DO
			IF VAL(a$) > 0 THEN rec% = VAL(a$): GOTO DOLIST0
			END IF
		END IF

	GET #60, , clobal: rec% = rec% + 1
	LOOP

	LOCATE 22, 12: PRINT "F1-Exit.. ";

	IF updwn% <> 59 THEN
		a$ = ""
		LOCATE 22, 21
		CALL inpnew(a$, 104!, updwn%, "59")
		IF VAL(a$) > 0 THEN rec% = VAL(a$): GOTO DOLIST0
		END IF

	CLOSE #60
END SUB

SUB doload (mth$, mthless1$, ok%, chkonly%) STATIC
	'>> Clear out all customers first <<
	IF NOT chkonly% THEN
		rrn% = 0
		rec% = 1
		GET #chb%, rec%, cus
		DO WHILE NOT EOF(chb%)
			IF rec% MOD 50 = 0 THEN
				LOCATE 15, 20: PRINT USING "#### Clearing all customers"; rec%
				END IF
			LSET cus.opn$ = MKS$(0)
			LSET cus.opn30$ = MKS$(0)
			LSET cus.opn60$ = MKS$(0)
			LSET cus.opn90$ = MKS$(0)

			LSET cus.scur$ = MKS$(0)
			LSET cus.s30$ = MKS$(0)
			LSET cus.s60$ = MKS$(0)
			LSET cus.s90$ = MKS$(0)


			PUT #chb%, rec%, cus
			GET #chb%, , cus: rec% = rec% + 1
			LOOP
		END IF
	'>> Now load from the file <<
	COLOR 6, 0
	LOCATE 18, 12: PRINT "Rec. Month   Cust.    Current   30 days   60 days   90 days"
	COLOR 2, 0

	rec% = 1
	GET #60, rec%, clobal
	DO WHILE NOT EOF(60)
	IF clobal.mth$ = mthless1$ THEN
		keyin$ = clobal.cust$
		CALL searchindex(keyin$, cha%, found%)
		sno% = CVI(supx.wrrn$)
		IF found% = 0 THEN sno% = 0
		IF sno% >= 1 AND sno% <= maxsup% THEN
			GET #chb%, sno%, cus
			IF CVI(cus.sno$) <> sno% THEN sno% = 0 '> Error
			IF rec% MOD 50 = 0 THEN
			LOCATE 15, 12: PRINT USING "&-&"; clobal.cust$; cus.sname$
			LOCATE 19, 12: PRINT USING "#### '\  \'  \    \ ##,###.## ##,###.## ##,###.## ##,###.##"; clobal.rec%; clobal.mth$; clobal.cust$; clobal.ocur!; clobal.o30!; clobal.o60!; clobal.o90!
			END IF
			END IF

		IF chkonly% THEN
			IF CVS(cus.opn$) <> clobal.ocur! THEN sno% = 0
			IF CVS(cus.opn30$) <> clobal.o30! THEN sno% = 0
			IF CVS(cus.opn60$) <> clobal.o60! THEN sno% = 0
			IF CVS(cus.opn90$) <> clobal.o90! THEN sno% = 0
			END IF

		IF sno% >= 1 THEN
			GET #chb%, sno%, cus
			LSET cus.opn$ = MKS$(clobal.ocur)
			LSET cus.opn30$ = MKS$(clobal.o30)
			LSET cus.opn60$ = MKS$(clobal.o60)
			LSET cus.opn90$ = MKS$(clobal.o90)
			IF NOT chkonly% THEN PUT #chb%, sno%, cus
			ELSE

			IF clobal.cust$ <> "     " THEN
			SOUND 54, 1
			rrn% = rrn% + 1: rrn%(rrn%) = rec%
			END IF

			END IF
		END IF
		GET #60, , clobal: rec% = rec% + 1
		LOOP


	GET #36, 1, msmisc
	IF cha% = 45 THEN msmisc.CRmonth$ = mth$ ELSE msmisc.DBmonth$ = mth$
	PUT #36, 1, msmisc

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
		GET #60, rrn%(rec%), clobal
		n% = n% + 1
		LOCATE n%, 4: PRINT USING "####"; rec%
		LOCATE n%, 12: PRINT USING "#### '\  \'  \    \ ##,###.## ##,###.## ##,###.## ##,###.##"; clobal.rec%; clobal.mth$; clobal.cust$; clobal.ocur!; clobal.o30!; clobal.o60!; clobal.o90!
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

SUB dowrite (mthless1$, ok%)
	'>>- Read through existing opening balance file and clear out old copies
	'>>  of this month.
	'>>- Load the address of the empty records in an array.
	rrn% = 0
	rec% = 1
	GET #60, rec%, clobal
	DO WHILE NOT EOF(60)
		IF clobal.rec% <> rec% OR clobal.mth$ = mthless1$ THEN
			rrn% = rrn% + 1: IF rrn% > 999 THEN rrn% = 999
			rrn%(rrn%) = rec%
			END IF

		GET #60, , clobal: rec% = rec% + 1
		LOOP

	'>> The rrn() must hold all the possible addresses for the records.
	'>> add the number of customers to the rrn array
	adlast% = LOF(chb%) / LEN(cus)
	opnlast% = LOF(60) / LEN(clobal)
	needed% = adlast% - rrn% + 1
	FOR i% = 1 TO needed%
		rrn% = rrn% + 1: rrn%(rrn%) = opnlast% + i%
		NEXT
	'> Now rrn() hold the addresses for all the records
	n.rrn% = rrn%

	COLOR 6, 0
	LOCATE 18, 12: PRINT "Rec. Month   Cust.    Current   30 days   60 days   90 days"
	COLOR 2, 0
	'>> Read through customer index and write to file <<
	rec% = 1
	rrn% = 0
	GET #cha%, rec%, CUSX
	DO WHILE NOT EOF(cha%) AND CUSX.wcde$ <> "~~~~~"
		rec2% = CVI(CUSX.wrrn$)
		GET #chb%, rec2%, cus
		clobal.rec% = 0
		clobal.mth$ = mthless1$
		clobal.cust$ = UCASE$(cus.search$ + cus.stype$)
		clobal.ocur! = CVS(cus.opn$)
		clobal.o30! = CVS(cus.opn30$)
		clobal.o60! = CVS(cus.opn60$)
		clobal.o90! = CVS(cus.opn90$)
		ok% = 0
		IF clobal.ocur! <> 0 THEN ok% = -1
		IF clobal.o30! <> 0 THEN ok% = -1
		IF clobal.o60! <> 0 THEN ok% = -1
		IF clobal.o90! <> 0 THEN ok% = -1
		IF ok% THEN
			rrn% = rrn% + 1
			clobal.rec% = rrn%(rrn%)
			PUT #60, rrn%(rrn%), clobal
			numok% = numok% + 1

		IF numok% MOD 1 = 0 THEN
			LOCATE 19, 12: PRINT USING "#### '\  \'  \    \ ##,###.## ##,###.## ##,###.## ##,###.##"; clobal.rec%; clobal.mth$; clobal.cust$; clobal.ocur!; clobal.o30!; clobal.o60!; clobal.o90!
			END IF
			END IF

		GET #cha%, , CUSX: rec% = rec% + 1
		LOOP
	currec% = rec%
	FOR rec% = currec% + 1 TO n.rrn%
		clobal.rec% = 0
		clobal.mth$ = "    "
		clobal.cust$ = "    "
		clobal.ocur! = 0
		clobal.o30! = 0
		clobal.o60! = 0
		clobal.o90! = 0
		rrn% = rrn% + 1
		PUT #60, rrn%(rrn%), clobal
		NEXT


END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

SUB sub.one (mth$, mthless1$)
	'>- sub one from the sel month
	yy% = VAL(MID$(mth$, 3, 2))
	mm% = VAL(MID$(mth$, 1, 2))
	mm% = mm% - 1: IF mm% < 1 THEN mm% = 12: yy% = yy% - 1
	IF yy% > 99 THEN yy% = 0
	IF yy% < 0 OR yy% > 99 THEN yy% = 0
	IF mm% < 1 OR mm% > 12 THEN mm% = 0
	yy$ = RIGHT$("0" + MID$(STR$(yy%), 2, 2), 2)
	mm$ = RIGHT$("0" + MID$(STR$(mm%), 2, 2), 2)
	mthless1$ = mm$ + yy$

END SUB

