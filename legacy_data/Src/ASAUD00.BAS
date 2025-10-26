DECLARE SUB custtot (Tot.DB AS CURRENCY, Tot.CR AS CURRENCY, cf!, sno%, thisme$)
DECLARE SUB dolist (n%, cs%, sno%, thissup$, dsplyit$, onauto$, updwn%, DB.OR.CR$, STDOUT$)
DECLARE SUB dsply.result (updwn%, onauto$, DB.OR.CR$)
DECLARE SUB spec.upd (DB.OR.CR$)
DECLARE SUB quick.data (asup$, updwn%)
DECLARE SUB get.obal (thissup$, updwn%, onauto$)
DECLARE SUB selectsort (asup$, thissup$, dsplyit$, onauto$, opt$, updwn%, DB.OR.CR$)
DECLARE SUB checkaudit (updwn%, DB.OR.CR$)
DECLARE SUB rebldpe (ok%)
DECLARE FUNCTION getval! (in$)
DECLARE SUB print.it (islong%, STDOUT$)
DECLARE FUNCTION numonly$ (a$)
DECLARE SUB load.sort (pbeg$, pend$, thissup$, n%, updwn%, DB.OR.CR$)
DECLARE SUB dsplyfrom (dspfrom%)
DECLARE FUNCTION format$ (VALUE!, definition$)
DECLARE SUB new.mth (cf!)
DECLARE SUB opn.bal (cf!)
DECLARE SUB print.line ()
DECLARE SUB qsort (in$(), in%(), n%)
DECLARE SUB search.month (rec%, pe.ok%)
DECLARE SUB searchindex (keyin$, chi%, found%)
'///////////////////////////////////////////////////////////////////////
'////////////////// ASAUD03 - STATEMENT ROUTINE  ///////////////////////
'///////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "asaud01"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CONST maxlin% = 20
	CONST maxauditcodes% = 2500
	CONST maxprtlins% = 2500
	'STDOUT$ = "con"
'>>>---------------------------------------------------<<<
'>>> NOTE: This program is for Suppliers and Customers
'>>>       Pass parm of  /CR or /DB
'>>>---------------------------------------------------<<<
	DB.OR.CR$ = "DB"
	DB.OR.CR$ = ENVIRON$("DB.OR.CR$")
	cr% = INSTR(COMMAND$, "/CR")
	 'CR% = 1 '<<<-Swap to CR. System use cr% = 1
	 IF cr% > 0 THEN DB.OR.CR$ = "CR"


	RESET
	parm$ = ENVIRON$("PARM$")
	DIM SHARED k%(1500)
	DIM SHARED begymd$, endymd$, msg$
	DIM SHARED prtlin%, maxsup%, cs%
	DIM SHARED s90!, s60!, s30!, scur!
	DIM SHARED pbeg$, pend$, pbeg0$, pend0$
	DIM SHARED auditcodes$(maxauditcodes%)
	DIM SHARED updcusdata$, updcuscount%, updclobal$
	DIM SHARED mth%, yy%, cha%
	DIM SHARED updcbal$(24), updcbal%(24), file60opn%, asup$
	DIM SHARED cashonly$(9), cashonly$
	DIM SHARED j%, j1%, j2%
	DIM SHARED sav.L1$, sav.L2$
	DIM SHARED Tot.DB AS CURRENCY, Tot.CR AS CURRENCY
	DIM SHARED auditfile$(15), naudit%

FOR i% = 1 TO 9: READ a$: cashonly$(i%) = a$: NEXT
	DATA "9","0","1","2","3","4","5","N","Y"



	btmline% = 31

	IF DB.OR.CR$ = "CR" THEN cs% = 44 ELSE cs% = 43
	typefields% = -1
	cashonly$ = "N": auditname$ = "ASAUDIT.ASF"
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\CUSX.INC'
	'$INCLUDE: '\tpmanuf\src\CUS.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\ASAUDIT.INC'
	'$INCLUDE: '\tpmanuf\src\ASCLOBAL.INC'
	'$INCLUDE: '\tpmanuf\src\ascurbal.inc'

	 IF DB.OR.CR$ = "CR" THEN
		cha% = 45: chb% = 44
		ELSE
		cha% = 23: chb% = 43
	 END IF


	OPEN "c:\tpexe\ASAUD03.WRK" FOR RANDOM SHARED AS #97 LEN = 80
	TYPE RcdFmtAsaud03
		text AS STRING * 74
		cr AS STRING * 1
		lf AS STRING * 1
		END TYPE
	DIM SHARED Asaud03 AS RcdFmtAsaud03
	prtlin% = LOF(97) / 80

	cashonly$ = parm$
	GOSUB OPEN.AUDIT
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	GET #36, 1, msmisc


	maxsup% = CVI(msmisc.max1$)
	maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$): maxcus% = CVI(msmisc.max7$)
	IF DB.OR.CR$ = "CR" THEN
		maxsup% = maxsup%
		ELSE
		maxsup% = maxcus%
		END IF
	'>>>>>>>>>>>>>>>>>>  Find end of the audit file  <<<<<<<<<<<<<<<<<<<<<<<
	adlast% = LOF(8) / 92
	GET #8, 1, audit
	begin.addate$ = audit.addate$
	adnxtpe% = CVI(MID$(audit.ADSNAME$, 1, 2))
	adprepe% = CVI(MID$(audit.ADSNAME$, 3, 2))
	adlstpe% = CVI(MID$(audit.ADSNAME$, 5, 2))
	IF adlstpe% < 1 OR adlstpe% > adlast% THEN adlstpe% = 1
	GET #8, adlstpe%, audit

	dsplyit$ = "S"
	asup$ = "*"
	begymd$ = "  /  /  "
	endymd$ = "  /  /  "
	pbeg0$ = msmisc.DBmonth$
	IF DB.OR.CR$ = "CR" THEN pbeg0$ = msmisc.CRmonth$
	pend0$ = pbeg$
	pbeg$ = pbeg0$
	pend$ = "9999"

start:
	IF file60opn% THEN CLOSE #60: file60opn% = 0

	CALL setup("STATEMENT LISTING")
	CALL BOX(1, 2, 80, 12, 7, 0, 2)
	CALL BOX(1, 13, 80, 24, 7, 0, 2)
	CALL sndmsg(msg$): msg$ = ""
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit   F3-Statment run and month roll.  F5-Quick data  F6-Browse last."; : COLOR 2, 0
	COLOR 2, 0: LOCATE 3, 67: PRINT auditname$

	IF DB.OR.CR$ = "CR" THEN
		COLOR 4
		LOCATE 3, 25: PRINT "C R E D I T O R S    T O O L S"
		ELSE
		COLOR 12
		LOCATE 3, 25: PRINT "D E B T O R S    T O O L S"
		END IF

	IF NOT rebuiltpe% THEN
		CALL rebldpe(ok%)
		rebuiltpe% = -1
		END IF

	COLOR 2
	CALL selectsort(asup$, thissup$, dsplyit$, onauto$, opt$, updwn%, DB.OR.CR$)
	IF updwn% = 59 THEN GOTO ENDPGM
	IF updwn% = 60 THEN GOTO start

		
	'>- Write keyed closing date to file
	IF updclobal$ = "Y" THEN
		pbeg0$ = pbeg$: pend0$ = pend$
		GET #36, 1, msmisc
		IF cha% = 45 THEN msmisc.CRmonth$ = pbeg$ ELSE msmisc.DBmonth$ = pbeg$
		PUT #36, 1, msmisc
		END IF

	'>- Write keyed closing date to file
	IF updclobal$ = "Y" THEN
		asclobal$ = "DBCL" + pbeg$ + ".ASF"
		IF cha% = 45 THEN asclobal$ = "CRCL" + pbeg$ + ".ASF"
		IF file60opn% THEN CLOSE #60: file60opn% = 0
		OPEN asclobal$ FOR RANDOM SHARED AS #60 LEN = 48: file60opn% = -1
		IF LOF(60) > 0 THEN
			msg$ = "Closing balance file " + asclobal$ + " already exists!"
			GOTO start
			END IF
		END IF

	IF asup$ = "*" THEN
		recx% = 1
		ELSE
		skey$ = asup$
		CALL searchindex(skey$, cha%, found%)
		recx% = LOC(cha%)
		END IF

	'>>- Clear the current file -<<
	IF onauto$ = "Y" THEN
		CLOSE #67
		KILL "ascurbal.ASF"
		OPEN "ascurbal.ASF" FOR RANDOM SHARED AS #67 LEN = 48
		END IF

	GET #cha%, recx%, CUSX
	DO WHILE NOT EOF(cha%) AND CUSX.wcde$ < "~~~~~"
		stimer = TIMER
		sno% = CVI(CUSX.wrrn$)
		IF sno% < 1 OR sno% > maxsup% THEN sno% = 1: SOUND 2400, 1
		GET #cs%, sno%, CUS
		thissup$ = CUS.search$ + CUS.stype$

			CALL get.obal(thissup$, updwn%, onauto$)
			IF updwn% = 59 THEN EXIT DO

			''trial code to sort out file.
			begyymm$ = MID$(pbeg$, 3, 2) + MID$(pbeg$, 1, 2)
			SELECT CASE begyymm$
			CASE "8807" TO "8906": j1% = 1
			CASE "8907" TO "9006": j1% = 2
			CASE "9007" TO "9106": j1% = 3
			CASE "9107" TO "9206": j1% = 4
			CASE "9207" TO "9306": j1% = 5
			CASE "9307" TO "9406": j1% = 6
			CASE "9407" TO "9506": j1% = 7
			CASE ELSE: j1% = 7
			END SELECT
			endyymm$ = MID$(pend$, 3, 2) + MID$(pend$, 1, 2)
			SELECT CASE endyymm$
			CASE "8807" TO "8906": j2% = 1
			CASE "8907" TO "9006": j2% = 2
			CASE "9007" TO "9106": j2% = 3
			CASE "9107" TO "9206": j2% = 4
			CASE "9207" TO "9306": j2% = 5
			CASE "9307" TO "9406": j2% = 6
			CASE "9407" TO "9506": j2% = 7
			CASE ELSE: j2% = 7
			END SELECT
			onauto.sav$ = onauto$

			FOR i% = 1 TO prtlin%: Asaud03.text$ = "": PUT #97, i%, Asaud03: NEXT: prtlin% = 0


			FOR j% = j1% TO j2%
				CLOSE #8
				cashonly$ = cashonly$(j%)
				GOSUB OPEN.AUDIT
				onauto$ = "Y": IF j% = j2% THEN onauto$ = "N"
				IF onauto.sav$ = "Y" THEN onauto$ = "Y"

				COLOR 2, 0: LOCATE 3, 67: PRINT auditname$

				CALL load.sort(pbeg$, pend$, thissup$, n%, updwn%, DB.OR.CR$)
				IF updwn% = 59 THEN EXIT DO

				IF n% > 0 OR j% = 7 THEN
				CALL dolist(n%, cs%, sno%, thissup$, dsplyit$, onauto$, updwn%, DB.OR.CR$, STDOUT$)
				IF updwn% = 59 THEN EXIT DO
				END IF

				LSET CUS.opn$ = MKS$(scur!)
				LSET CUS.opn30$ = MKS$(s30!)
				LSET CUS.opn60$ = MKS$(s60!)
				LSET CUS.opn90$ = MKS$(s90!)
				updwn% = 13

				NEXT





next.in.loop:
		etimer = TIMER
		LOCATE 3, 69: PRINT USING "##.# Secs."; ABS(etimer - stimer)
		GET #cha%, , CUSX: recx% = recx% + 1
		IF asup$ <> "*" THEN EXIT DO
		LOOP

	IF updclobal$ = "Y" AND updwn% <> 59 THEN
		'>- Add one to the month
		yy% = VAL(MID$(pbeg$, 3, 2))
		mm% = VAL(MID$(pbeg$, 1, 2))
		mm% = mm% + 1: IF mm% > 12 THEN mm% = 1: yy% = yy% + 1
		IF yy% > 99 THEN yy% = 0
		IF yy% < 0 OR yy% > 99 THEN yy% = 0
		IF mm% < 1 OR mm% > 12 THEN mm% = 0
		yy$ = RIGHT$("0" + MID$(STR$(yy%), 2, 2), 2)
		mm$ = RIGHT$("0" + MID$(STR$(mm%), 2, 2), 2)
		GET #36, 1, msmisc
		IF cha% = 45 THEN msmisc.CRmonth$ = mm$ + yy$ ELSE msmisc.DBmonth$ = mm$ + yy$
		PUT #36, 1, msmisc

		pbeg$ = msmisc.DBmonth$
		pend$ = msmisc.DBmonth$
		IF cha% = 45 THEN
			pbeg$ = msmisc.CRmonth$
			pend$ = msmisc.CRmonth$
			END IF
		pbeg0$ = pbeg$: pend0$ = pend$
		'>---

		END IF

	GOTO start
ENDPGM:
	CLOSE
	CALL EXITPGM(apgm$)
	CHAIN apgm$

SUB checkaudit (updwn%, DB.OR.CR$)
'$INCLUDE: '\tpmanuf\src\checkaud.bi'
END SUB

SUB custtot (Tot.DB AS CURRENCY, Tot.CR AS CURRENCY, cf!, sno%, thisme$) STATIC
'///////////////////////////////////////////////////////////////////////
'//////  PRINT THE CUSTOMERS TOTAL ON THE BOTTOM OF THE STATEMENT  /////
'///////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>  Print 30,60,90+ days from the last customer.  <<<<<<
	prtbuf$ = "  dd/mm/yy    Invoice     111111     $99999.99   $99999.99                "
	prtbuf$ = "                        Subtotal     $99999.99   $99999.99                "

	SELECT CASE cha%
	CASE 45'<<< CREDITORS >>>
		wrkDB = Tot.DB
		wrkCR = Tot.CR
		MID$(prtbuf$, 37, 10) = format$(wrkDB, "$$#,###.b#")
		MID$(prtbuf$, 50, 10) = format$(wrkCR, "$$#,###.b#")
	CASE ELSE'<<< DEBTORS >>>
		wrkDB = Tot.DB
		wrkCR = Tot.CR
		MID$(prtbuf$, 37, 10) = format$(wrkCR, "$$#,###.b#")
		MID$(prtbuf$, 50, 10) = format$(wrkDB, "$$#,###.b#")
	END SELECT

	prtlin% = prtlin% + 1: IF prtlin% > maxprtlins% THEN prtlin% = maxprtlins%
	Asaud03.text$ = prtbuf$
	PUT #97, prtlin%, Asaud03

	IF CUS.stype$ = "L" THEN Tot.CR = 0 'eg WAGEL


	tmp$ = msmisc.DBmonth$
	IF cha% = 45 THEN tmp$ = msmisc.CRmonth$

	roll% = -1
	tot.db.thismonth! = Tot.DB



	'> --- This section is copied to UPDWHO.BI --- < (TOP)
	'Test on       02/11/94 (Try to fix -ve rolling)
	'Patch for CR  10/12/94
	SELECT CASE cha%
	CASE 45 '<<<  Creditors  >>>>

	IF roll% THEN
		s90! = s90! + s60!
		s60! = s30!
		s30! = scur!
		scur! = 0
		END IF

	'If there is +ve values in any bucket they reduce the total CREDITS
	IF s90! < 0 THEN
		wrk! = s90!: s90! = s90! + Tot.CR: Tot.CR = 0
		IF s90! > 0 THEN Tot.CR = s90!: s90! = 0
		END IF
	IF s60! < 0 THEN
		wrk! = s60!: s60! = s60! + Tot.CR: Tot.CR = 0
		IF s60! > 0 THEN Tot.CR = s60!: s60! = 0
		END IF
	IF s30! < 0 THEN
		wrk! = s30!: s30! = s30! + Tot.CR: Tot.CR = 0
		IF s30! > 0 THEN Tot.CR = s30!: s30! = 0
		END IF

	s0! = Tot.DB - Tot.CR

	IF s90! > 0 THEN
		s90! = s90! - Tot.DB: Tot.DB = 0: CALL ROUND(s90!, 2.5)
		IF s90! < 0 THEN Tot.DB = ABS(s90!): s90! = 0
		END IF
	IF s60! > 0 THEN
		s60! = s60! - Tot.DB: Tot.DB = 0: CALL ROUND(s60!, 2.5)
		IF s60! < 0 THEN Tot.DB = ABS(s60!): s60! = 0
		END IF
	IF s30! > 0 THEN
		s30! = s30! - Tot.DB: Tot.DB = 0: CALL ROUND(s30!, 2.5)
		IF s30! < 0 THEN Tot.DB = ABS(s30!): s30! = 0
		END IF

	scur! = scur! + Tot.CR - Tot.DB: CALL ROUND(scur!, 2.5)
	Tot.CR = 0: Tot.DB = 0


	CASE ELSE'<<< DEBTORS >>>
	IF roll% THEN
		s90! = s90! + s60!
		s60! = s30!
		s30! = scur!
		scur! = 0
		END IF

	scurplus! = Tot.DB + scur!
	scur.s30! = Tot.DB + scur! + s30!
	scur.s30.s60! = Tot.DB + scur! + s30! + s60!
	scur.s30.s60.s90! = Tot.DB + scur! + s30! + s60! + s90!
	s30.s60! = s30! + s60!
	s30.s60.s90! = s30! + s60! + s90!
	s60.s90! = s60! + s90!

	IF Tot.CR = scur.s30.s60! THEN Tot.DB = 0: scur! = 0: s30! = 0: s60! = 0: Tot.CR = 0
	IF Tot.CR = s30.s60.s90! THEN s30! = 0: s60! = 0: s90! = 0: Tot.CR = 0
	IF Tot.CR = s60.s90! THEN s60! = 0: s90! = 0: Tot.CR = 0
	IF Tot.CR = s30.s60! THEN s30! = 0: s60! = 0: Tot.CR = 0
	IF Tot.CR = scur.s30! THEN Tot.DB = 0: scur! = 0: s30! = 0: Tot.CR = 0
	IF Tot.CR = scurplus! THEN Tot.DB = 0: scur! = 0: Tot.CR = 0
	IF Tot.CR = s30! THEN s30! = 0: Tot.CR = 0
	IF Tot.CR = s60! THEN s60! = 0: Tot.CR = 0

	'If there is -ve values in any bucket they reduce the total debits
	IF s90! < 0 THEN
		wrk! = s90!: s90! = s90! + Tot.DB: Tot.DB = 0
		IF s90! > 0 THEN Tot.DB = s90!: s90! = 0
		END IF
	IF s60! < 0 THEN
		wrk! = s60!: s60! = s60! + Tot.DB: Tot.DB = 0
		IF s60! > 0 THEN Tot.DB = s60!: s60! = 0
		END IF
	IF s30! < 0 THEN
		wrk! = s30!: s30! = s30! + Tot.DB: Tot.DB = 0
		IF s30! > 0 THEN Tot.DB = s30!: s30! = 0
		END IF

	IF s90! > 0 THEN
		s90! = s90! - Tot.CR: Tot.CR = 0: CALL ROUND(s90!, 2.5)
		IF s90! < 0 THEN Tot.CR = ABS(s90!): s90! = 0
		END IF
	IF s60! > 0 THEN
		s60! = s60! - Tot.CR: Tot.CR = 0: CALL ROUND(s60!, 2.5)
		IF s60! < 0 THEN Tot.CR = ABS(s60!): s60! = 0
		END IF
	IF s30! > 0 THEN
		s30! = s30! - Tot.CR: Tot.CR = 0: CALL ROUND(s30!, 2.5)
		IF s30! < 0 THEN Tot.CR = ABS(s30!): s30! = 0
		END IF

	scur! = scur! + Tot.DB - Tot.CR: CALL ROUND(scur!, 2.5)
	Tot.DB = 0: Tot.CR = 0
	END SELECT

	stotal! = scur! + s30! + s60! + s90!
	CALL ROUND(stotal!, 2.5)
	cf! = stotal!


	'> --- This section is copied to UPDWHO.BI --- <  (BOTTOM)

	prtbuf$ = "  dd/mm/yy    Invoice     111111     $99999.99   $99999.99                "
	prtbuf$ = "September  $99,999.99(90)  $99,999.99(60)  $99,999.99(30)  $99,999.99(Cur)"
				'123456789 123465789 123456789 123456789 123456789 123465789 1
	MID$(prtbuf$, 12, 10) = format$(s90, "$$#,###.##")
	MID$(prtbuf$, 28, 10) = format$(s60, "$$#,###.##")
	MID$(prtbuf$, 44, 10) = format$(s30, "$$#,###.##")
	MID$(prtbuf$, 60, 10) = format$(scur, "$$#,###.##")

	SELECT CASE mth%
	CASE 1: mthd$ = "JANUARY  "
	CASE 2: mthd$ = "FEBRUARY "
	CASE 3: mthd$ = "MARCH    "
	CASE 4: mthd$ = "APRIL    "
	CASE 5: mthd$ = "MAY      "
	CASE 6: mthd$ = "JUNE     "
	CASE 7: mthd$ = "JULY     "
	CASE 8: mthd$ = "AUGUST   "
	CASE 9: mthd$ = "SEPTEMBER"
	CASE 10: mthd$ = "OCTOBER  "
	CASE 11: mthd$ = "NOVEMBER "
	CASE 12: mthd$ = "DECEMBER "
	CASE ELSE: mthd$ = "XXXXXXXXX"
	END SELECT
	MID$(prtbuf$, 1, 10) = mthd$
	 MID$(prtbuf$, 10, 2) = MID$(thisme$, 3, 2)

	prtlin% = prtlin% + 1: IF prtlin% > maxprtlins% THEN prtlin% = maxprtlins%
	Asaud03.text$ = prtbuf$
	PUT #97, prtlin%, Asaud03

	IF updcusdata$ = "Y" THEN
		GET #cs%, sno%, CUS
		LSET CUS.s0$ = MKS$(s0!)
		LSET CUS.scur$ = MKS$(scur!)
		LSET CUS.s30$ = MKS$(s30!)
		LSET CUS.s60$ = MKS$(s60!)
		LSET CUS.s90$ = MKS$(s90!)
		PUT #cs%, sno%, CUS
		IF updcuscount% = 0 THEN
			msg$ = "Updated Current,30,60+90 for " + CUS.sname$
			SOUND 22000, 1
			olast% = LOF(67) / LEN(curbal)
			curbal.rec% = olast% + 1
			IF cha% = 45 THEN curbal.mth$ = msmisc.CRmonth$ ELSE curbal.mth$ = msmisc.DBmonth$
			curbal.cust$ = UCASE$(CUS.search$ + CUS.stype$)
			curbal.ocur! = CVS(CUS.scur$) - tot.db.thismonth!
			curbal.o30! = CVS(CUS.s30$)
			curbal.o60! = CVS(CUS.s60$)
			curbal.o90! = CVS(CUS.s90$)
			curbal.cur! = 0
			curbal.c30! = 0
			curbal.c60! = 0
			curbal.c90! = 0
			ok% = 0
			IF curbal.ocur! <> 0 THEN ok% = -1
			IF curbal.o30! <> 0 THEN ok% = -1
			IF curbal.o60! <> 0 THEN ok% = -1
			IF curbal.o90! <> 0 THEN ok% = -1
			IF ok% THEN
				PUT #67, curbal.rec%, curbal
				END IF

			END IF
		updcuscount% = updcuscount% + 1
		END IF


	tmp$ = msmisc.DBmonth$
	IF cha% = 45 THEN tmp$ = msmisc.CRmonth$

	IF updclobal$ = "Y" AND thisme$ = tmp$ THEN
		GET #cs%, sno%, CUS
		LSET CUS.opn$ = MKS$(scur!)
		LSET CUS.opn30$ = MKS$(s30!)
		LSET CUS.opn60$ = MKS$(s60!)
		LSET CUS.opn90$ = MKS$(s90!)
		PUT #cs%, sno%, CUS
		SOUND 22000, 1
		msg$ = "Updated Closing & Current,30,60+90 for " + CUS.sname$


		END IF

	IF updclobal$ = "Y" AND thisme$ = tmp$ THEN
		olast% = LOF(60) / LEN(clobal)
		clobal.rec% = olast% + 1
		IF cha% = 45 THEN clobal.mth$ = msmisc.CRmonth$ ELSE clobal.mth$ = msmisc.DBmonth$
		clobal.cust$ = UCASE$(CUS.search$ + CUS.stype$)
		clobal.ocur! = CVS(CUS.opn$)
		clobal.o30! = CVS(CUS.opn30$)
		clobal.o60! = CVS(CUS.opn60$)
		clobal.o90! = CVS(CUS.opn90$)
		ok% = 0
		IF clobal.ocur! <> 0 THEN ok% = -1
		IF clobal.o30! <> 0 THEN ok% = -1
		IF clobal.o60! <> 0 THEN ok% = -1
		IF clobal.o90! <> 0 THEN ok% = -1
		IF ok% THEN
			PUT #60, clobal.rec%, clobal
			END IF
		msg$ = "Updated Closing, CBAL & Current,30,60+90 for " + CUS.sname$
		END IF

END SUB

SUB dolist (n%, cs%, sno%, thissup$, dsplyit$, onauto$, updwn%, DB.OR.CR$, STDOUT$)
'///////////////////////////////////////////////////////////////////////
'////// PRINT THE LISTING FROM THE SORTED INDEX  (MEM INDEX ONLY) //////
'///////////////////////////////////////////////////////////////////////
	anew.mth% = 0
	sav.L2$ = "~~~~~"
	sav.L1$ = "~~~~~~~~~~"

	IF n% = 0 THEN
		audit.addate$ = "01/" + MID$(pbeg$, 1, 2) + "/" + MID$(pbeg$, 3, 2)
		mth% = VAL(MID$(audit.addate$, 4, 2))
		CALL opn.bal(cf!)
		END IF

	'//////////////////  For now find start of customer data  //////////////
	'Sorted by Customer,date (yymmdd)
	'Level break by Customer, yymm
	FOR rec% = 1 TO n%
		rrn% = k%(rec%)
		GET #8, rrn%, audit


		'>>- Load level break buffers
		yymm$ = "  /  "
		MID$(yymm$, 1, 2) = MID$(audit.addate$, 7, 2)
		MID$(yymm$, 4, 2) = MID$(audit.addate$, 4, 2)
		L2$ = CUS.search$ + CUS.stype$
		L1$ = CUS.search$ + CUS.stype$ + yymm$

		'>>- L2 Change of Customer
		IF sav.L2$ <> L2$ THEN
				sav.L2$ = L2$
				sav.L1$ = L1$
				CALL opn.bal(cf!)
				anew.mth% = -1
				updcuscount% = 0
				END IF

		'>>- L1 Change of month
		IF sav.L1$ <> L1$ THEN
			thisme$ = MID$(sav.L1$, 9, 2) + MID$(sav.L1$, 6, 2)
			sav.L1$ = L1$
			CALL custtot(Tot.DB, Tot.CR, cf!, sno%, thisme$)
			anew.mth% = -1

			'>> - Wheel on screen
			chr% = rec% MOD 4: chrlist$ = "|/-\"
			char$ = MID$(chrlist$, chr% + 1, 1)
			LOCATE 22, 78: PRINT char$
			END IF


		'>>- First line of a new month
		IF anew.mth% THEN
			anew.mth% = 0
			CALL new.mth(cf!)
			END IF


		cr! = 0: DB! = 0
		IF audit.advalue > 0 AND audit.advalue < .01 THEN audit.advalue = 0
		IF audit.advalue < 0 AND audit.advalue > -.01 THEN audit.advalue = 0
		IF audit.advalue > 0 THEN DB! = ABS(audit.advalue)
		IF audit.advalue < 0 THEN cr! = ABS(audit.advalue)
		IF audit.ADTYPE$ = "PE" THEN audit.advalue = 0

		CALL ROUND(DB!, 2.5)
		CALL ROUND(cr!, 2.5)

		CALL print.line
		mth% = VAL(MID$(audit.addate$, 4, 2))
		yy% = VAL(MID$(audit.addate$, 7, 2))

		IF audit.ADTYPE$ = "DC" THEN DB! = 0 - cr!: cr! = 0
		IF audit.ADTYPE$ = "CC" THEN cr! = 0 - DB!: DB! = 0
		Tot.CR = Tot.CR + cr!
		Tot.DB = Tot.DB + DB!

		'PRINT Tot.DB, Tot.CR; db!, cr!, rrn%
		'x$ = INPUT$(1)
						 
		NEXT


	IF n% > 0 THEN
		thisme$ = MID$(sav.L1$, 9, 2) + MID$(sav.L1$, 6, 2)
		CALL custtot(Tot.DB, Tot.CR, cf!, sno%, thisme$)
		END IF


		'>- Display the customer on the screen
		IF dsplyit$ = "S" THEN
			CALL dsply.result(updwn%, onauto$, DB.OR.CR$)
			END IF


		IF dsplyit$ = "P" THEN
			prtbuf$ = " A dummy total record to make the print work...............     $99999.99 "
			MID$(prtbuf$, 65, 10) = format$(cf!, "$$#,###.b#")
			prtlin% = prtlin% + 1
			Asaud03.text$ = prtbuf$
			PUT #97, prtlin%, Asaud03


			CALL print.it(-1, STDOUT$)
			END IF

		 IF onauto$ = "Y" THEN CALL sndmsg(msg$)

END SUB

SUB dsply.result (updwn%, onauto$, DB.OR.CR$) STATIC
	IF SCREEN(13, 1) <> 186 THEN
		CALL setup("STATEMENT LISTING")
		COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit        F5-Quick print         F10-Update Closing balances"; : COLOR 2, 0
		END IF

	a$ = ""
	dspfrom% = 1
	CALL dsplyfrom(dspfrom%)

	DO
		CALL sndmsg(msg$): msg$ = ""
		COLOR 2, 0
		LOCATE 3, 2: PRINT "Display from..> ";
		LOCATE 3, 17

		IF onauto$ = "Y" THEN
			updwn% = 60
			x$ = INKEY$
			DO WHILE x$ <> ""
				IF x$ = CHR$(0) + CHR$(59) THEN updwn% = 59
				x$ = INKEY$
				LOOP
			END IF
		IF onauto$ = "N" THEN
			CALL inpnew(a$, 3!, updwn%, "13,59-60,63,68,81,73,80,72")
			END IF
		SELECT CASE updwn%
		CASE 13: dspfrom% = VAL(a$): CALL dsplyfrom(dspfrom%)
		CASE 63: CALL print.it(0, STDOUT$)
		CASE 68: CALL spec.upd(DB.OR.CR$): CALL dsplyfrom(dspfrom%)
		CASE 73: dspfrom% = dspfrom% - maxlin%: CALL dsplyfrom(dspfrom%)
		CASE 81: dspfrom% = dspfrom% + maxlin%: CALL dsplyfrom(dspfrom%)
		CASE 72: dspfrom% = dspfrom% - 1: CALL dsplyfrom(dspfrom%)
		CASE 80: dspfrom% = dspfrom% + 1: CALL dsplyfrom(dspfrom%)
		END SELECT
		LOOP UNTIL updwn% = 59 OR updwn% = 60
			
END SUB

SUB dsplyfrom (dspfrom%) STATIC
	IF dspfrom% < 1 THEN dspfrom% = 1
	IF dspfrom% > prtlin% THEN dspfrom% = prtlin%

	COLOR 6, 0: LOCATE 3, 27: PRINT CUS.sname$: COLOR 2, 0

	FOR i% = 1 TO maxlin%
	rec% = i% + dspfrom% - 1
	IF rec% > 0 AND rec% <= prtlin% THEN
		GET #97, rec%, Asaud03
		prtbuf$ = Asaud03.text$

		IF INSTR(prtbuf$, "$") < 20 THEN COLOR 10 ELSE COLOR 2
		show% = rec%: IF show% >= 1000 THEN show% = rec% - 1000
		LOCATE i% + 3, 2: PRINT USING "### &"; show%; prtbuf$
		ELSE
		LOCATE i% + 3, 2: PRINT SPACE$(78)
		END IF
	NEXT
		

END SUB

FUNCTION format$ (VALUE!, definition$) STATIC
	dp% = 0

	'>- Find out how many decimal places,neg etc... -<
	work$ = STR$(VALUE!)
	edtcde$ = " ": dp% = 0
	x% = INSTR(definition$, ".")
	IF x% > 0 THEN
		FOR i% = x% TO LEN(definition$)
			IF MID$(definition$, i%, 1) = "b" THEN MID$(definition$, i%, 1) = "#": edtcde$ = "b"
			IF MID$(definition$, i%, 1) = "#" THEN dp% = dp% + 1
			NEXT
		x% = INSTR(work$, ".")
		IF x% = 0 THEN work$ = work$ + "."
		work$ = work$ + STRING$(dp%, "0")
		x% = INSTR(work$, ".")
		work$ = MID$(work$, 1, x% + dp%)
		END IF


	'>- Move from work pad into definition, from right to left -<
	neg% = MID$(work$, 1, 1) = "-"
	dollars% = 0
	work$ = MID$(work$, 2)
	defwork$ = definition$
	FOR i% = 1 TO LEN(definition$)
		IF MID$(definition$, i%, 1) = "$" THEN dollars% = -1: EXIT FOR
		NEXT

	'>- NOTE: The "d" represents the $ that i have added! -<
	IF dollars% THEN work$ = "d" + work$
	IF neg% THEN work$ = "-" + work$

	num.dollars% = 0
	w% = LEN(work$)

	FOR i% = LEN(defwork$) TO 1 STEP -1
		IF w% < 1 THEN EXIT FOR
		SELECT CASE MID$(defwork$, i%, 1)
		CASE "#": MID$(defwork$, i%, 1) = MID$(work$, w%, 1): w% = w% - 1
		CASE "$": MID$(defwork$, i%, 1) = MID$(work$, w%, 1): w% = w% - 1
		CASE ",": IF MID$(work$, w%, 1) = "d" THEN MID$(defwork$, i%, 1) = "#": i% = i% + 1
		CASE ".": w% = w% - 1
		CASE ELSE
		END SELECT

		NEXT

	FOR i% = 1 TO LEN(defwork$)
		IF MID$(defwork$, i%, 1) >= "1" AND MID$(defwork$, i%, 1) <= "9" THEN EXIT FOR
		IF MID$(defwork$, i%, 1) = "#" THEN MID$(defwork$, i%, 1) = " "
		IF MID$(defwork$, i%, 1) = "$" THEN MID$(defwork$, i%, 1) = " "
		IF MID$(defwork$, i%, 1) = "d" THEN MID$(defwork$, i%, 1) = "$"
		IF MID$(defwork$, i%, 1) = "," THEN MID$(defwork$, i%, 1) = " "
		NEXT

	'>- Zero suppress
	IF edtcde$ = "b" AND VALUE! = 0 THEN defwork$ = STRING$(LEN(defwork$), " ")

	format$ = defwork$
END FUNCTION

SUB get.obal (thissup$, updwn%, onauto$) STATIC
		IF onauto$ = "N" THEN
		LOCATE 8, 2: PRINT SPACE$(78)
		LOCATE 9, 2: PRINT SPACE$(78)
		LOCATE 10, 2: PRINT SPACE$(78)
		LOCATE 8, 15: PRINT "          Searching for opening data...." + SPACE$(20)
		END IF

		'>- Sub one to the month
		yy% = VAL(MID$(pbeg$, 3, 2))
		mm% = VAL(MID$(pbeg$, 1, 2))
		mm% = mm% - 1: IF mm% < 1 THEN mm% = 12: yy% = yy% - 1
		IF yy% < 0 THEN yy% = 99
		IF yy% < 0 OR yy% > 99 THEN yy% = 0
		IF mm% < 1 OR mm% > 12 THEN mm% = 0
		yy$ = RIGHT$("0" + MID$(STR$(yy%), 2, 2), 2)
		mm$ = RIGHT$("0" + MID$(STR$(mm%), 2, 2), 2)

		asopnbal$ = "DBCL" + mm$ + yy$ + ".ASF"'yy%
		IF cha% = 45 THEN asopnbal$ = "CRCL" + mm$ + yy$ + ".ASF"
		a$ = DIR$(asclobal$)
		IF a$ = "" THEN
			LSET CUS.opn$ = MKS$(0!)
			LSET CUS.opn30$ = MKS$(0!)
			LSET CUS.opn60$ = MKS$(0!)
			LSET CUS.opn90$ = MKS$(0!)
			found% = 0
			msg$ = "Opening balance file " + asopnbal$ + " does not exist!"
			CALL sndmsg(msg$)
			updwn% = 59
			GOTO x.get.obal
			END IF

		OPEN asopnbal$ FOR RANDOM SHARED AS #61 LEN = 48: file61opn% = -1
		rec61% = 1: found% = 0
		GET #61, rec61%, clobal
		DO WHILE NOT EOF(61)

			IF clobal.cust$ = thissup$ THEN
				LSET CUS.opn$ = MKS$(clobal.ocur!)
				LSET CUS.opn30$ = MKS$(clobal.o30!)
				LSET CUS.opn60$ = MKS$(clobal.o60!)
				LSET CUS.opn90$ = MKS$(clobal.o90!)
				LOCATE 11, 15: PRINT "          Opening data loaded.             "
				found% = -1
				EXIT DO
				END IF
			GET #61, , clobal: rec60% = rec60% + 1
			LOOP
		CLOSE #61
		IF NOT found% THEN
			LSET CUS.opn$ = MKS$(0!)
			LSET CUS.opn30$ = MKS$(0!)
			LSET CUS.opn60$ = MKS$(0!)
			LSET CUS.opn90$ = MKS$(0!)
			END IF

get.obal.50:
		IF onauto$ = "Y" THEN GOTO x.get.obal

			LOCATE 8, 25: PRINT "Key opening balance...>               "
			IF found% THEN
				LOCATE 10, 25: PRINT "Opening balance for "; thissup$
				ELSE
				LOCATE 10, 25: PRINT "*** No Opening balance found ***"
				END IF

			k90$ = STR$(CVS(CUS.opn90$))
			k60$ = STR$(CVS(CUS.opn60$))
			k30$ = STR$(CVS(CUS.opn30$))
			kcur$ = STR$(CVS(CUS.opn$))
			keyit$ = "N"
			GOTO kctl

k90:
			GOSUB dsply.line.k
			LOCATE 11, 3
												CALL inpnew(k90$, -7.2, updwn%, "13,59-60")
			IF updwn% = 59 THEN GOTO x.get.obal
			IF updwn% = 60 THEN GOTO k90
k60:
			GOSUB dsply.line.k
			LOCATE 11, 18
												CALL inpnew(k60$, -7.2, updwn%, "13,59-60")
			IF updwn% = 59 THEN GOTO x.get.obal
			IF updwn% = 60 THEN GOTO k90
k30:
			GOSUB dsply.line.k
			LOCATE 11, 33
												CALL inpnew(k30$, -7.2, updwn%, "13,59-60")
			IF updwn% = 59 THEN GOTO x.get.obal
			IF updwn% = 60 THEN GOTO k60
kcur:
			GOSUB dsply.line.k
			LOCATE 11, 48
												CALL inpnew(kcur$, -7.2, updwn%, "13,59-60")
			IF updwn% = 59 THEN GOTO x.get.obal
			IF updwn% = 60 THEN GOTO k30

kctl:
			GOSUB dsply.line.k
			LOCATE 11, 78
												CALL inpnew(keyit$, 101!, updwn%, "13,59-60")
			IF updwn% = 59 THEN GOTO x.get.obal
			IF updwn% = 60 THEN keyit$ = "Y"
			IF updwn% = 60 THEN GOTO kcur

			IF keyit$ = "Y" THEN
				LSET CUS.opn$ = MKS$(kcur!)
				LSET CUS.opn30$ = MKS$(k30!)
				LSET CUS.opn60$ = MKS$(k60!)
				LSET CUS.opn90$ = MKS$(k90!)
				END IF

x.get.obal:
EXIT SUB

dsply.line.k:
			k90 = VAL(k90$)
			k60 = VAL(k60$)
			k30 = VAL(k30$)
			kcur = VAL(kcur$)
			ktot = k90 + k60 + k30 + kcur
			LOCATE 11, 2
			COLOR 2, 0
			PRINT USING "  #####.##(90)   #####.##(60)   #####.##(30)   #####.##(Cur)  $$##,###.##"; k90; k60; k30; kcur; ktot
RETURN
END SUB

FUNCTION getval (in$)
wrkbuf$ = ""
ndot% = 0
FOR i% = 1 TO LEN(in$)
	wrk$ = MID$(in$, i%, 1)
	IF wrk$ > "0" AND wrk$ <= "9" THEN wrkbuf$ = wrkbuf$ + wrk$
	IF wrk$ = "." AND ndot% = 0 THEN wrkbuf$ = wrkbuf$ + wrk$: ndot% = ndot% + 1
	NEXT
getval! = VAL(wrkbuf$)

END FUNCTION

SUB load.sort (pbeg$, pend$, thissup$, n%, updwn%, DB.OR.CR$) STATIC
	'-----------------------------------------------------------------------
	n% = 0
	CALL search.month(rec%, pe.ok%)
	IF updwn% = 59 THEN GOTO xload.sort
	IF NOT pe.ok% THEN GOTO xload.sort
	IF rec% < 1 THEN GOTO xload.sort

	first.pe.rrn% = rec%
	IF auditcodeoffset% = 0 THEN auditcodeoffset% = rec% 'Only set once for each run of the program
	adlast% = LOF(8) / 92
	GET #8, rec%, audit
	DO WHILE NOT EOF(8)
		IF STDOUT$ <> "con" AND rec% MOD 500 = 0 THEN
			msg$ = "Record" + STR$(rec%) + " out of" + STR$(adlast%) + "      Selected" + STR$(n%) + "     Last record:" + thissup$ + " " + audit.addate$
			CALL sndmsg(msg$)
			x$ = INKEY$
			IF x$ = CHR$(0) + CHR$(59) THEN updwn% = 59: GOTO xload.sort
			END IF


		yymmdd$ = "  /  /  "
		MID$(yymmdd$, 1, 2) = MID$(audit.addate$, 7, 2)
		MID$(yymmdd$, 4, 2) = MID$(audit.addate$, 4, 2)
		MID$(yymmdd$, 7, 2) = MID$(audit.addate$, 1, 2)
		IF audit.ADTYPE$ = "PE" AND yymmdd$ > endymd$ THEN EXIT DO

		auditcode% = rec% - auditcodeoffset%
		IF auditcode% > 0 AND auditcode% <= maxauditcodes% AND cashonly$ = "N" THEN
			auditcodes$(auditcode%) = audit.adcust$
			END IF

		ok% = -1
		IF thissup$ <> audit.adcust$ THEN ok% = 0
		IF yymmdd$ > endymd$ THEN ok% = 0
		IF audit.ADTYPE$ = "PE" THEN ok% = -1
		IF NOT ok% THEN GOTO skip

		'>>>>>>>>>>>>  And now....
		IF audit.ADTYPE$ = "PE" THEN
			n% = n% + 1
			k%(n%) = rec%
			END IF
		IF DB.OR.CR$ = "CR" THEN
		IF audit.ADTYPE$ = "CI" OR audit.ADTYPE$ = "CC" OR audit.ADTYPE$ = "CD" OR audit.ADTYPE$ = "CJ" OR audit.ADTYPE$ = "CP" THEN
			n% = n% + 1
			k%(n%) = rec%
			END IF
			END IF
		'>>>>>>>>>>>  And now....
		IF DB.OR.CR$ <> "CR" THEN
		IF audit.ADTYPE$ = "DI" OR audit.ADTYPE$ = "DC" OR audit.ADTYPE$ = "DD" OR audit.ADTYPE$ = "DJ" OR audit.ADTYPE$ = "DP" THEN
			n% = n% + 1
			k%(n%) = rec%
			END IF
			END IF

skip:
		rec% = rec% + 1
		auditcode% = rec% - auditcodeoffset%
		IF auditcode% > 0 AND auditcode% <= maxauditcodes% AND cashonly$ = "N" THEN
		IF auditcodes$(auditcode%) > "" THEN
			IF auditcodes$(auditcode%) <> thissup$ THEN GOTO skip
			END IF
			END IF

		GET #8, rec%, audit

		LOOP
xload.sort:

END SUB

SUB new.mth (cf!) STATIC
	IF cf! >= 0 THEN cf.db! = cf!: cf.cr! = 0
	IF cf! < 0 THEN cf.cr! = cf!: cf.db! = 0

	'          123456789+123456789+123456789+123456789+123456789+123456789+123456789
	prtbuf$ = "Carried forward from last statement  $99999.99   $99999.99      $99999.99 "
	cf.tot = cf.db! - cf.cr!
	MID$(prtbuf$, 37, 10) = format$(cf.db!, "$$#,###.b#")
	MID$(prtbuf$, 50, 10) = format$(cf.cr!, "$$#,###.b#")
	MID$(prtbuf$, 65, 10) = format$(cf!, "$$#,###.b#")

	prtlin% = prtlin% + 1: IF prtlin% > maxprtlins% THEN prtlin% = maxprtlins%
	Asaud03.text$ = prtbuf$
	PUT #97, prtlin%, Asaud03


END SUB

FUNCTION numonly$ (a$) STATIC
	b$ = ""
	FOR i% = 1 TO LEN(a$)
		SELECT CASE MID$(a$, i%, 1)
		CASE "0" TO "9": b$ = b$ + MID$(a$, i%, 1)
		CASE ".": b$ = b$ + MID$(a$, i%, 1)
		CASE " "
		CASE ELSE: MID$(a$, i%, 1) = " "
		END SELECT
		NEXT
	numonly$ = b$
END FUNCTION

SUB opn.bal (cf!) STATIC
	opncur = CVS(CUS.opn$)
	opn30 = CVS(CUS.opn30$)
	opn60 = CVS(CUS.opn60$)
	opn90 = CVS(CUS.opn90$)
	ototal = opncur + opn30 + opn60 + opn90

	s90! = opn90!
	s60! = opn60!
	s30! = opn30!
	scur! = opncur!
	stotal! = scur! + s30! + s60! + s90!
	cf! = stotal!
	
	prtbuf$ = "September  $99,999.99(90)  $99,999.99(60)  $99,999.99(30)  $99,999.99(Cur)"
				'123456789 123465789 123456789 123456789 123456789 123465789 1
	MID$(prtbuf$, 12, 10) = format$(opn90, "$$#,###.##")
	MID$(prtbuf$, 28, 10) = format$(opn60, "$$#,###.##")
	MID$(prtbuf$, 44, 10) = format$(opn30, "$$#,###.##")
	MID$(prtbuf$, 60, 10) = format$(opncur, "$$#,###.##")

	thismth% = VAL(MID$(audit.addate$, 4, 2))
	prevmth% = thismth% - 1
	 SELECT CASE prevmth%
	 CASE 0: mthd$ = "December "
	 CASE 1: mthd$ = "JANUARY  "
	 CASE 2: mthd$ = "FEBRUARY "
	 CASE 3: mthd$ = "MARCH    "
	 CASE 4: mthd$ = "APRIL    "
	 CASE 5: mthd$ = "MAY      "
	 CASE 6: mthd$ = "JUNE     "
	 CASE 7: mthd$ = "JULY     "
	 CASE 8: mthd$ = "AUGUST   "
	 CASE 9: mthd$ = "SEPTEMBER"
	 CASE 10: mthd$ = "OCTOBER  "
	 CASE 11: mthd$ = "NOVEMBER "
	 CASE 12: mthd$ = "DECEMBER "
	 CASE ELSE: mthd$ = "XXXXXXXXX"
	 END SELECT
	 MID$(prtbuf$, 1, 10) = mthd$

IF prtlin% = 0 THEN
	prtlin% = prtlin% + 1: IF prtlin% > maxprtlins% THEN prtlin% = maxprtlins%
	Asaud03.text$ = prtbuf$
	PUT #97, prtlin%, Asaud03
	END IF

END SUB

SUB print.it (islong%, STDOUT$) STATIC
	IF STDOUT$ <> "con" THEN
		mm$ = MID$(pbeg$, 1, 2)
		STDOUT$ = CUS.search$ + CUS.stype$ + mm$ + ".prn"
		END IF
	IF islong% = 0 THEN STDOUT$ = "LPT1"
	len.of.page% = 55
	OPEN STDOUT$ FOR OUTPUT AS #99

	SELECT CASE MID$(pbeg$, 1, 2)
	CASE "01": stmtdesc$ = "January '" + MID$(pbeg$, 3, 2)
	CASE "02": stmtdesc$ = "February '" + MID$(pbeg$, 3, 2)
	CASE "03": stmtdesc$ = "March '" + MID$(pbeg$, 3, 2)
	CASE "04": stmtdesc$ = "April '" + MID$(pbeg$, 3, 2)
	CASE "05": stmtdesc$ = "May '" + MID$(pbeg$, 3, 2)
	CASE "06": stmtdesc$ = "June '" + MID$(pbeg$, 3, 2)
	CASE "07": stmtdesc$ = "July '" + MID$(pbeg$, 3, 2)
	CASE "08": stmtdesc$ = "August '" + MID$(pbeg$, 3, 2)
	CASE "09": stmtdesc$ = "September '" + MID$(pbeg$, 3, 2)
	CASE "10": stmtdesc$ = "October '" + MID$(pbeg$, 3, 2)
	CASE "11": stmtdesc$ = "November '" + MID$(pbeg$, 3, 2)
	CASE "12": stmtdesc$ = "December '" + MID$(pbeg$, 3, 2)
	CASE ELSE
	END SELECT



	lin% = 9999: pag% = 0: n.det% = 0
	FOR rec% = 1 TO prtlin% - 1
		IF lin% > len.of.page% THEN GOSUB heading
		GET #97, rec%, Asaud03
		prtbuf$ = Asaud03.text$

		tt% = INSTR(prtbuf$, "(90)")
		IF rec% = 1 THEN tt% = -1
		
		IF tt% = 0 OR islong% = 0 THEN
			PRINT #99, USING "&"; prtbuf$
			lin% = lin% + 1

			chk1% = INSTR(prtbuf$, "Carried")
			chk2% = INSTR(prtbuf$, "Subtotal")
			IF chk1% = 0 AND chk2% = 0 THEN n.det% = n.det% + 1
			END IF
		'>> It its a total
		IF tt% > 0 AND islong% THEN
			GET #97, rec%, Asaud03
			prtbuf$ = Asaud03.text$

			s90$ = MID$(prtbuf$, 12, 10)
			s60$ = MID$(prtbuf$, 28, 10)
			s30$ = MID$(prtbuf$, 44, 10)
			scur$ = MID$(prtbuf$, 60, 10)
			GET #97, rec% + 1, Asaud03
			prtbuf2$ = Asaud03.text$

			stotal$ = MID$(prtbuf2$, 65, 10)

			FOR i% = lin% TO len.of.page% - 5: PRINT #99, "": NEXT
			PRINT #99, "      90 DAYS       60 DAYS       30 DAYS         CURRENT            TOTAL  "
			PRINT #99, "    -----------    ----------    ----------      ----------      -----------"
			PRINT #99, USING "    \         \   \         \   \         \     \         \     \          \"; s90$; s60$; s30$; scur$; stotal$
			PRINT #99, CHR$(12)
			IF getval(stotal$) <> 0 THEN n.det% = n.det% + 1
			lin% = 9999: pag% = 0
			END IF
		NEXT
		IF pag% > 0 THEN PRINT #99, CHR$(12)
		CLOSE #99
		IF n.det% = 0 AND STDOUT$ <> "con" THEN KILL STDOUT$
		'SHELLA$ = "COPY " + STDOUT$ + " LPT1"
		'SHELL SHELLA$
	IF STDOUT$ = "con" THEN x$ = INPUT$(1)

EXIT SUB

heading:
	IF rec% = prtlin% THEN GOTO x.heading
	pag% = pag% + 1: lin% = 0
	DATE1$ = "  /  /  ": MID$(DATE1$, 1, 2) = MID$(DATE$, 4, 2):         MID$(DATE1$, 4, 2) = MID$(DATE$, 1, 2): MID$(DATE1$, 7, 2) = MID$(DATE$, 9, 2)
	'-----------------------------------------------------------------------
	IF pag% > 1 THEN PRINT #99, CHR$(12)
	IF islong% THEN
		PRINT #99, USING "!!"; CHR$(18); CHR$(20)
		'PRINT #99, USING "!        TRADEPAINTS PTY. LTD."; CHR$(14)
		PRINT #99, USING "! JANGER P/L. Trading as TRADEPAINTS."; CHR$(14)
		PRINT #99, "                          142  FITZGERALD ROAD."
		PRINT #99, "                          LAVERTON NORTH. 3026."
		PRINT #99, "               Phone. (03) 369-3455     Fax. (03) 360-0876"
		PRINT #99, ""
		PRINT #99, USING "         \                            \ "; CUS.sname$
		PRINT #99, USING "         \                            \ "; CUS.saddr$
		PRINT #99, USING "         \                    \    \  \ "; CUS.suburb$; CUS.spcode$
		PRINT #99, ""
		PRINT #99, USING "CUSTOMER - \   \                                    STATEMENT - \           \"; CUS.search$ + CUS.stype$; stmtdesc$
		PRINT #99, ""
		'PRINT #99, "  DATE        TRANS.    REF.             DEBIT       CREDIT        BALANCE"
		PRINT #99, "  DATE        TRANS.    REF.            CREDIT        DEBIT        BALANCE"
		PRINT #99, STRING$(76, "-")
		lin% = lin% + 14
		END IF

	IF NOT islong% THEN
		PRINT #99, USING "CUSTOMER - \   \-###                                STATEMENT - \      \."; CUS.search$ + CUS.stype$; CVI(CUS.sno$); DATE1$
		PRINT #99, ""
		lin% = lin% + 2
		END IF


x.heading:
RETURN

END SUB

SUB print.line STATIC
	IF audit.advalue > 0 THEN DB! = ABS(audit.advalue): cr! = 0
	IF audit.advalue < 0 THEN cr! = ABS(audit.advalue): DB! = 0
	IF audit.ADTYPE$ = "DC" THEN DB! = 0 - cr!: cr! = 0
	IF audit.ADTYPE$ = "CC" THEN cr! = 0 - DB!: DB! = 0
	IF audit.advalue = 0 THEN GOTO x.print.line

	tmp6$ = "      "
	j9% = 7
	FOR i% = 8 TO 1 STEP -1
	IF MID$(audit.addocnum$, i%, 1) <> " " THEN
			j9% = j9% - 1: IF j9% < 1 THEN EXIT FOR
			MID$(tmp6$, j9%, 1) = MID$(audit.addocnum$, i%, 1)
			END IF
	NEXT

	SELECT CASE audit.ADTYPE$
	CASE "DI": tmp8$ = "Invoice "
	CASE "DC": tmp8$ = "Credit. "
	CASE "DP": tmp8$ = "Payment "
	CASE "DD": tmp8$ = "Discount"
	CASE "DJ": tmp8$ = "Journal "
	CASE "CI": tmp8$ = "Invoice "
	CASE "CC": tmp8$ = "Credit. "
	CASE "CP": tmp8$ = "Payment "
	CASE "CD": tmp8$ = "Discount"
	CASE "CJ": tmp8$ = "Journal "
	CASE ELSE: tmp8$ = SPACE$(9)
	END SELECT
	'                    1         2         3         4         5
	'          123456789+123456789+123456789+123456789+123456789+123456789+
	prtbuf$ = "  dd/mm/yy    Invoice     111111     $99999.99   $99999.99                "
	MID$(prtbuf$, 3, 8) = audit.addate$
	MID$(prtbuf$, 15, 8) = tmp8$
	MID$(prtbuf$, 27, 6) = tmp6$
	IF cha% = 45 THEN
		MID$(prtbuf$, 37, 10) = format$(DB!, "$$#,###.b#")
		MID$(prtbuf$, 50, 10) = format$(cr!, "$$#,###.b#")
		ELSE
		MID$(prtbuf$, 37, 10) = format$(cr!, "$$#,###.b#")
		MID$(prtbuf$, 50, 10) = format$(DB!, "$$#,###.b#")
		END IF


	x% = INSTR(MID$(prtbuf$, 37, 10), "-")
	IF x% > 0 THEN
		MID$(prtbuf$, 37 + x% - 1, 1) = "("
		MID$(prtbuf$, 47, 1) = ")"
		END IF



	prtlin% = prtlin% + 1: IF prtlin% > maxprtlins% THEN prtlin% = maxprtlins%
	Asaud03.text$ = prtbuf$
	PUT #97, prtlin%, Asaud03

x.print.line:
END SUB

SUB quick.data (thissup$, updwn%)
		skey$ = asup$
		CALL searchindex(skey$, cha%, found%)
		recx% = LOC(cha%)
		GET #cha%, recx%, CUSX
		sno% = CVI(CUSX.wrrn$)
		IF sno% < 1 OR sno% > maxsup% THEN sno% = 1: SOUND 2400, 1
		GET #cs%, sno%, CUS

		opntot = CVS(CUS.opn$) + CVS(CUS.opn30$) + CVS(CUS.opn60$) + CVS(CUS.opn90$)
		total = CVS(CUS.scur$) + CVS(CUS.s30$) + CVS(CUS.s60$) + CVS(CUS.s90$)
		tmp$ = msmisc.DBmonth$
		IF cha% = 45 THEN tmp$ = msmisc.CRmonth$

		COLOR 6, 0
		LOCATE 14, 3: PRINT USING "              Data for &"; CUS.sname$
		LOCATE 15, 3: PRINT USING "              90+ days     60 Days     30 Days     Current        Total!"; CHR$(32)
		COLOR 10, 0
		LOCATE 16, 3: PRINT USING "Closing Bal $$#,###.##  $$#,###.##  $$#,###.##  $$#,###.##   $$#,###.##"; CVS(CUS.s90$); CVS(CUS.s60$); CVS(CUS.s30$); CVS(CUS.scur$); total
		COLOR 2, 0


		ddd$ = pbeg$
		FOR file% = 1 TO 5
			'>- Sub one to the month
			yy% = VAL(MID$(ddd$, 3, 2))
			mm% = VAL(MID$(ddd$, 1, 2))
			IF file% > 1 THEN mm% = mm% - 1: IF mm% < 1 THEN mm% = 12: yy% = yy% - 1
			IF yy% < 0 THEN yy% = 99
			IF yy% < 0 OR yy% > 99 THEN yy% = 0
			IF mm% < 1 OR mm% > 12 THEN mm% = 0
			yy$ = RIGHT$("0" + MID$(STR$(yy%), 2, 2), 2)
			mm$ = RIGHT$("0" + MID$(STR$(mm%), 2, 2), 2)

			file$ = "DBCL" + mm$ + yy$ + ".ASF"'yy%
			IF cha% = 45 THEN file$ = "CRCL" + mm$ + yy$ + ".ASF"
			fileok$ = DIR$(file$)
			found% = 0
			IF fileok$ <> "" THEN
				OPEN file$ FOR RANDOM SHARED AS #62 LEN = 48
				rec62% = 1
				GET #62, rec62%, clobal
				DO WHILE NOT EOF(62)
					IF thissup$ = clobal.cust$ THEN found% = -1: EXIT DO
					GET #62, , clobal: rec62% = rec62% + 1
					LOOP
				CLOSE #62
				END IF

			IF NOT found% THEN
				clobal.o90! = 0
				clobal.o60! = 0
				clobal.o30! = 0
				clobal.ocur! = 0
				END IF

			clobaltot! = clobal.o90! + clobal.o60 + clobal.o30! + clobal.ocur!
			badnmth$ = "    ": IF found% AND clobal.mth$ <> MID$(file$, 5, 4) THEN badmth$ = " Bad"

			IF fileok$ <> "" THEN
			LOCATE 16 + file%, 3: PRINT USING "\      \\  \$$#,###.##  $$#,###.##  $$#,###.##  $$#,###.##   $$#,###.##"; file$; badmth$; clobal.o90!; clobal.o60!; clobal.o30!; clobal.ocur!; clobaltot
			END IF
			ddd$ = mm$ + yy$
			NEXT

END SUB

SUB rebldpe (ok%)
'$INCLUDE: '\tpmanuf\src\rebldpe.bi'
END SUB

SUB search.month (rec%, pe.ok%) STATIC
	pe.ok% = -1
	rec% = 1
	adlast% = LOF(8) / 92
	GET #8, rec%, audit
	IF audit.ADTYPE$ <> "PE" THEN pe.ok% = 0: GOTO x.search.month
	dymd$ = "  /  /  "
	MID$(dymd$, 1, 2) = MID$(audit.addate$, 7, 2)
	MID$(dymd$, 4, 2) = MID$(audit.addate$, 4, 2)
	MID$(dymd$, 7, 2) = MID$(audit.addate$, 1, 2)
	'>>>>>>>>>>>>  Use the period end records to jump old months  <<<<<<<<<<
	DO WHILE dymd$ < begymd$
		adnxtpe% = CVI(MID$(audit.ADSNAME$, 1, 2))
		adprepe% = CVI(MID$(audit.ADSNAME$, 3, 2))
		adlstpe% = CVI(MID$(audit.ADSNAME$, 5, 2))
		IF adnxtpe% < 1 OR adlstpe% > adlast% THEN rec% = -1: EXIT DO
		rec% = adnxtpe%
		GET #8, rec%, audit
		IF audit.ADTYPE$ <> "PE" THEN pe.ok% = 0: GOTO x.search.month
		dymd$ = "  /  /  "
		MID$(dymd$, 1, 2) = MID$(audit.addate$, 7, 2)
		MID$(dymd$, 4, 2) = MID$(audit.addate$, 4, 2)
		MID$(dymd$, 7, 2) = MID$(audit.addate$, 1, 2)
		LOOP
x.search.month:
	IF pe.ok% = 0 AND LOF(8) > 0 THEN
		CALL BOX(17, 15, 63, 17, 6, 9, 1)
		COLOR 7, 1
		LOCATE 16, 20: PRINT "Period end not found, rebuild Audit file."
		COLOR 2, 0
		CALL inpnew(a$, 0!, updwn%, "13,59")
		updwn% = 59
		END IF

END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

SUB selectsort (asup$, thissup$, dsplyit$, onauto$, opt$, updwn%, DB.OR.CR$) STATIC
'///////////////////////////////////////////////////////////////////////
'>>>> Select the paramaters
'///////////////////////////////////////////////////////////////////////
select.sort:
	LOCATE 5, 25: PRINT "Opening Balance Date..>"; pbeg$
	LOCATE 6, 25: PRINT "Closing Balance Date..>"; pend$
	LOCATE 7, 25: PRINT "Customer (*-All)......>"; asup$
	LOCATE 8, 25: PRINT
	LOCATE 9, 25: PRINT "Screen/Printer (S,P)..>"; dsplyit$; "     F10 - Run all Customers."
	LOCATE 11, 15: PRINT "Note: Customer data is only updated if end date is 9999"
	COLOR 4
	LOCATE 14, 25: PRINT "M O N T H    E N D    R O L L"
	COLOR 2
	updclobal$ = "N"

	GOTO cf2

cf1:
	LOCATE 5, 48
	CALL inpnew(pbeg$, 4!, updwn%, "13,59-60,63" + ALT)': GOSUB ALT
	IF updwn% = 59 THEN GOTO xselect.sort
	IF updwn% = 60 THEN GOTO cf1
	IF updwn% = 63 THEN CALL quick.data(asup$, updwn%): GOTO cf1
cf2:
	LOCATE 6, 48
	CALL inpnew(pend$, 4!, updwn%, "13,59-61,63-64,68" + ALT$)': GOSUB ALT
	IF updwn% = 59 THEN GOTO xselect.sort
	IF updwn% = 60 THEN GOTO cf1
	IF updwn% = 61 THEN GOTO cf50
	IF updwn% = 63 THEN CALL quick.data(asup$, updwn%): GOTO cf2
	IF updwn% = 64 THEN
						CALL setup("STATEMENT LISTING")
						COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit        F5-Quick print         F10-Update Closing balances"; : COLOR 2, 0
						onauto$ = "N"
						CALL dsply.result(updwn%, onauto$, DB.OR.CR$)
						updwn% = 60
						GOTO xselect.sort
						END IF
	IF updwn% = 68 THEN GOTO cf50

cf3:
	LOCATE 7, 48
	CALL inpnew(asup$, 105!, updwn%, "13,59-60,63-64")
	asup$ = UCASE$(asup$)
	IF updwn% = 59 THEN GOTO xselect.sort
	IF updwn% = 60 THEN GOTO cf2
	IF updwn% = 63 THEN CALL quick.data(asup$, updwn%): GOTO cf3
	IF updwn% = 64 THEN
						CALL setup("STATEMENT LISTING")
						COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit        F5-Quick print         F10-Update Closing balances"; : COLOR 2, 0
						onauto$ = "N"
						CALL dsply.result(updwn%, onauto$, DB.OR.CR$)
						updwn% = 60
						GOTO xselect.sort
						END IF

cf4:
	LOCATE 9, 48
	onauto$ = "N"
	CALL inpnew(dsplyit$, 101!, updwn%, "13,59-60,63-64,68")
	IF updwn% = 59 THEN GOTO xselect.sort
	IF updwn% = 60 THEN GOTO cf3
	IF updwn% = 63 THEN CALL quick.data(asup$, updwn%): GOTO cf4
	IF updwn% = 64 THEN
						CALL setup("STATEMENT LISTING")
						COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit        F5-Quick print         F10-Update Closing balances"; : COLOR 2, 0
						onauto$ = "N"
						CALL dsply.result(updwn%, onauto$, DB.OR.CR$)
						updwn% = 60
						GOTO xselect.sort
						END IF
	IF updwn% = 68 THEN onauto$ = "Y"
	dsplyit$ = UCASE$(dsplyit$)
	IF dsplyit$ <> "S" AND dsplyit$ <> "P" GOTO cf4

	IF onauto$ = "Y" THEN
		LOCATE 9, 25: PRINT "Display on screen.>"; dsplyit$; "     ** Auto run **  "
		END IF
	GOTO xselect.sort
'---------------------------------------------
'>>>- Here on update closing balances
'---------------------------------------------
cf50:
	pbeg$ = pbeg0$
	pend$ = pbeg0$
	asup$ = "*"
	updclobal$ = " "
	FOR i% = 14 TO 22
		LOCATE i%, 2: PRINT SPACE$(78)
		NEXT
	LOCATE 16, 25: PRINT "Enter Month.(mmyy)>"; pbeg$
	LOCATE 18, 25: PRINT "End of month roll about to start!"
	LOCATE 20, 25: PRINT "Confirm (Y/N).....>";
	GOTO cf53
cf51:
	LOCATE 16, 44
	CALL inpnew(pbeg$, 104!, updwn%, "13,59-60,68")
	IF updwn% = 59 THEN GOTO xselect.sort
	IF updwn% = 60 THEN GOTO xselect.sort
	mm% = VAL(MID$(pbeg$, 1, 2))
	yy% = VAL(MID$(pbeg$, 3, 2))
	IF mm% < 1 OR mm% > 12 THEN GOTO cf51
	IF yy% < 1 OR yy% > 99 THEN GOTO cf51
	pend$ = pbeg$
cf53:
	DO UNTIL updclobal$ = "Y" OR updclobal$ = "N"
		LOCATE 20, 44
		CALL inpnew(updclobal$, 101!, updwn%, "13,59-60,68")
		IF updwn% = 59 THEN GOTO xselect.sort
		IF updwn% = 60 THEN GOTO cf51
		updclobal$ = UCASE$(updclobal$)
		LOOP
	IF updclobal$ <> "Y" GOTO cf1

	IF NOT checkauditok% THEN
		CALL checkaudit(updwn%, DB.OR.CR$)
		checkauditok% = -1
		IF updwn% = 59 THEN checkauditok% = 0: GOTO cf51
		IF updwn% = 60 THEN checkauditok% = 0
		END IF

	updclobal$ = " "
	LOCATE 21, 25: PRINT "Again   (Y/N).....>";
	DO UNTIL updclobal$ = "Y" OR updclobal$ = "N"
		LOCATE 21, 44
		CALL inpnew(updclobal$, 101!, updwn%, "13,59-60,68")
		IF updwn% = 60 THEN checkauditok% = 0: GOTO cf53
		updclobal$ = UCASE$(updclobal$)
		LOOP
	IF updclobal$ <> "Y" GOTO cf1

	dsplyit$ = "P"
	onauto$ = "Y"


xselect.sort:
	updcusdata$ = "N"
	IF pend$ = "9999" THEN updcusdata$ = "Y"

	MID$(begymd$, 1, 2) = MID$(pbeg$, 3, 2)
	MID$(begymd$, 4, 2) = MID$(pbeg$, 1, 2)
	MID$(begymd$, 7, 2) = "00"
	MID$(endymd$, 1, 2) = MID$(pend$, 3, 2)
	MID$(endymd$, 4, 2) = MID$(pend$, 1, 2)
	MID$(endymd$, 7, 2) = "99"

END SUB

SUB spec.upd (DB.OR.CR$) STATIC
	wrkmth$ = pbeg$
	updcbal% = 0

	CALL setup("CLOSING BALANCE UPDATE")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit        F10-Continue"; : COLOR 2, 0
	COLOR 6, 0: LOCATE 3, 27: PRINT CUS.sname$: COLOR 2, 0
	COLOR 12, 0
	LOCATE 5, 7: PRINT "About to update..."
	COLOR 2, 0
	lin% = 0
	FOR rec% = 2 TO prtlin%
		GET #97, rec%, Asaud03
		prtbuf$ = Asaud03.text$

	IF INSTR(prtbuf$, "$") > 0 AND INSTR(prtbuf$, "$") < 20 THEN
		updcbal% = updcbal% + 1
		asclobal$ = "DBCL" + wrkmth$ + ".ASF"
		IF DB.OR.CR$ = "CR" THEN asclobal$ = "CRCL" + wrkmth$ + ".ASF"
		updcbal$(updcbal%) = asclobal$
		updcbal%(updcbal%) = rec%

		IF lin% > 17 THEN
		LOCATE lin% + 5, 4: PRINT "+++++++ more ";
		ELSE
		LOCATE lin% + 6, 4: PRINT prtbuf$
		LOCATE lin% + 6, 4: PRINT updcbal$(updcbal%)
		lin% = lin% + 1
		END IF

		'>- Add one to the month
		yy% = VAL(MID$(wrkmth$, 3, 2))
		mm% = VAL(MID$(wrkmth$, 1, 2))
		mm% = mm% + 1: IF mm% > 12 THEN mm% = 1: yy% = yy% + 1
		IF yy% > 99 THEN yy% = 0
		IF yy% < 0 OR yy% > 99 THEN yy% = 0
		IF mm% < 1 OR mm% > 12 THEN mm% = 0
		yy$ = RIGHT$("0" + MID$(STR$(yy%), 2, 2), 2)
		mm$ = RIGHT$("0" + MID$(STR$(mm%), 2, 2), 2)
		wrkmth$ = mm$ + yy$



	END IF
	NEXT

	CALL inpnew(a$, 0!, updwn%, "13,59,68")
	IF updwn% <> 68 THEN GOTO x.spec.upd

	'----------------------
	'>-- Acutual update <--
	'----------------------
	FOR i% = 1 TO updcbal%
		asclobal$ = updcbal$(i%)
		IF file60opn% THEN CLOSE #60: file60opn% = 0
		chk$ = DIR$(asclobal$)
		IF chk$ = "" THEN
			msg$ = "The file " + asclobal$ + " does not exist.  The month has not been built."
			SOUND 200, 3
			GOTO x.spec.upd
			END IF

		OPEN asclobal$ FOR RANDOM SHARED AS #60 LEN = 48: file60opn% = -1

		'>-- Find then record <--
		found% = 0
		rec% = 1
		GET #60, rec%, clobal
		DO WHILE NOT EOF(60)
			IF clobal.cust$ = asup$ THEN found% = -1: EXIT DO
			IF clobal.cust$ > asup$ THEN found% = 0: EXIT DO
			GET #60, , clobal: rec% = rec% + 1
			LOOP

		'>-- If it not found then clear a space in the file <--
		IF NOT found% THEN
			file60last% = LOF(60) / LEN(clobal)
			FOR r% = file60last% TO rec% STEP -1
				GET #60, r%, clobal
				PUT #60, r% + 1, clobal
				NEXT
			clobal.rec% = rec%
			clobal.cust$ = asup$
			PUT #60, rec%, clobal
			END IF


		'>-- Change/Insert then record <--
		GET #60, rec%, clobal
		IF MID$(clobal.cust$, 1, 4) <> MID$(asup$, 1, 4) THEN
			msg$ = "Did not update " + asclobal$ + "  " + asup$ + " is missing or duplicated."
			SOUND 200, 3
			GOTO x.spec.upd
			END IF

		GET #97, updcbal%(i%), Asaud03
		prtbuf$ = Asaud03.text$

		o90$ = numonly$(MID$(prtbuf$, 12, 10))
		o60$ = numonly$(MID$(prtbuf$, 28, 10))
		o30$ = numonly$(MID$(prtbuf$, 44, 10))
		ocur$ = numonly$(MID$(prtbuf$, 60, 10))

		o90! = VAL(o90$)
		o60! = VAL(o60$)
		o30! = VAL(o30$)
		ocur! = VAL(ocur$)

		clobal.o90! = o90!
		clobal.o60! = o60!
		clobal.o30! = o30!
		clobal.ocur! = ocur!
		PUT #60, rec%, clobal

		IF file60opn% THEN CLOSE #60: file60opn% = 0


	NEXT

x.spec.upd:
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit        F5-Quick print         F10-Update Closing balances"; : COLOR 2, 0

END SUB

