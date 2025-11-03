DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB doCHECK (mth$, mthless1$, ok%, chkonly%)
'///////////////////////////////////////////////////////////////////////
'>>> ASAUD06 - LOAD/UNLOAD  OPENING BALANCES FROM FILE
'///////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
apgm$ = "asaud01"
'$ NCLUDE: '\tpmanuf\src\pgmerr.inc'
	DIM SHARED rrn%(1100), rrn%, maxsup%, cha%, chb%
	DIM SHARED xxx$(50)
	RESET

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
	CALL setup("CLOSING BALANCE FILE INTEGRITY")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit                                  C - Check only"; : COLOR 2, 0
	IF db.or.cr$ = "CR" THEN
		COLOR 4
		LOCATE 5, 29: PRINT "C R E D I T O R S"
		ELSE
		COLOR 12
		LOCATE 5, 29: PRINT "  D E B T O R S "
		END IF
	COLOR 2, 0
	LOCATE 6, 29: PRINT "Continue (Y/N)..> "
	LOCATE 6, 46
	CALL inpnew(YorN$, 101!, updwn%, "13,59")
	YorN$ = UCASE$(YorN$)
	IF YorN$ <> "Y" THEN updwn% = 59
	IF updwn% = 59 THEN GOTO endpgm


	asclobal$ = "DBCL????.ASF"
	IF cha% = 45 THEN asclobal$ = "CRCL????.ASF"

	FOR n% = 1 TO 50: xxx$(n%) = "": NEXT
	n% = 0
	a$ = DIR$(asclobal$)
	DO WHILE a$ <> ""
		n% = n% + 1
		xxx$(n%) = a$
		a$ = DIR$
		LOOP



	FOR f% = 1 TO n%
	asclobal$ = xxx$(f%)
	LOCATE 6, 25: PRINT "Checking.."; asclobal$

	OPEN asclobal$ FOR RANDOM SHARED AS #60 LEN = 48

	chkonly% = -1
	CALL doCHECK(mth$, mthless1$, ok%, chkonly%)

	CLOSE #60
	NEXT f%


endpgm:
	CLOSE
	CALL exitpgm(apgm$)
	CHAIN apgm$

SUB doCHECK (mth$, mthless1$, ok%, chkonly%) STATIC
	'>> Clear out all customers first <<

	rec% = 1
	GET #60, rec%, clobal
	DO WHILE NOT EOF(60)
		keyin$ = clobal.cust$
		CALL searchindex(keyin$, cha%, found%)
		sno% = CVI(supx.wrrn$)
		IF found% = 0 THEN sno% = 1
		IF sno% >= 1 AND sno% <= maxsup% THEN sno% = 1
		GET #chb%, sno%, cus

		LOCATE 15, 12: PRINT USING "&-&"; clobal.cust$; cus.sname$
		LOCATE 19, 12: PRINT USING "#### '\  \'  \    \ ##,###.## ##,###.## ##,###.## ##,###.##"; clobal.rec%; clobal.mth$; clobal.cust$; clobal.ocur!; clobal.o30!; clobal.o60!; clobal.o90!


		IF NOT found% AND MID$(clobal.cust$, 1, 1) <> " " THEN
			SOUND 54, 1
			LOCATE 21, 14: COLOR 2, 0: PRINT "Enter "; D; " to delete...> "
			LOCATE 21, 37
			D$ = "D"
												CALL inpnew(D$, 101!, updwn%, "13")
			D$ = UCASE$(D$)
			IF D$ = "D" THEN
				GET #60, rec%, clobal
				clobal.cust$ = SPACE$(99)
				clobal.ocur = 0
				clobal.o30 = 0
				clobal.o60 = 0
				clobal.o90 = 0
				clobal.cur = 0
				clobal.c30 = 0
				clobal.c60 = 0
				clobal.c90 = 0
				PUT #60, rec%, clobal
				END IF
			END IF


		IF rec% MOD 100 = 0 THEN CALL sndmsg("Record" + STR$(rec%))
		GET #60, , clobal: rec% = rec% + 1
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

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB
