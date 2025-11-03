DECLARE SUB load.unpaid (cust$, startrec%, docnum$, Value!, updwn%)
DECLARE SUB rebldpe (ok%)
DECLARE SUB upd.who (chaudit%, chcus%, upd%)
DECLARE FUNCTION MYOB$ ()
DECLARE SUB setmhdr ()
DECLARE SUB search.month (Rec%, begyymd$)
DECLARE SUB selectfile (sel%, updwn%)
DECLARE SUB setaudit (ok%)
DECLARE FUNCTION paidsts$ (X$, set$)
'/////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>         A S A U D 0 1       <<<<<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'.dc - Complete
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "MENUTP"
''$INCLUDE: '\tpmanuf\src\pgmerr.INC'

	 typefields% = -1
	 CONST paglen% = 20
	 STDOUT$ = "LPT1"
	 'sTDOUT$ = "shit.sht"
	 RESET

	 parm$ = ENVIRON$("PARM$"): parm% = VAL(parm$)
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	'$INCLUDE: '\tpmanuf\src\CUS.INC'
	'$INCLUDE: '\tpmanuf\src\CUSX.INC'
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'

	 IF DB.OR.CR$ = "DB" THEN
	chw% = 43       '***** Channel of sup file
	 ELSE
	chw% = 44       '***** Channel of cus file
	 END IF
	 DIM SHARED rrn%(999)
	 DIM SHARED gltot.p@(999), gltot.n@(999)
	 DIM SHARED auditfile$(15), naudit%'max 15 years
	 DIM SHARED mhdr$(1 TO 100)

	 '$INCLUDE: '\tpmanuf\src\ASAUDIT.INC'

	 DB.OR.CR$ = "DB"
	 CALL setaudit(naudit%)
	 cashonly$ = "M": auditname$ = auditfile$(naudit%)
	 GOSUB OPEN.AUDIT
start:
	 opt$ = ""
	 GET #36, 1, msmisc
	 maxsup% = CVI(msmisc.max1$)
	 maxcus% = CVI(msmisc.max7$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)

	'>>>>>>>>>>>>>>>>>  Find end of audit file <<<<<<<<<<<<<<<<<<<<<
	 adlast% = LOF(8) / 92
	 temp1$ = " "
	 st$ = "1"
	 GET #8, 1, audit
	 beg$ = "mmyy"
	 MID$(beg$, 1, 2) = MID$(FNDYY$(audit.aDdate$), 4, 2)
	 MID$(beg$, 3, 2) = MID$(FNDYY$(audit.aDdate$), 7, 2)
	adnxtpe% = CVI(MID$(audit.adsname$, 1, 2))
	adprepe% = CVI(MID$(audit.adsname$, 3, 2))
	adlstpe% = CVI(MID$(audit.adsname$, 5, 2))
	 IF adlstpe% > 0 AND adlstpe% <= adlast% THEN
	GET #8, adlstpe%, audit
	end$ = "mmyy"
	MID$(end$, 1, 2) = MID$(FNDYY$(audit.aDdate$), 4, 2)
	MID$(end$, 3, 2) = MID$(FNDYY$(audit.aDdate$), 7, 2)
	 END IF
	 begday$ = "01"
	 endday$ = "31"
	 supa$ = "*"
	 CorD$ = "D"
	 opt2$ = "2"
	'-----------------------------------------------------------------------
	 CALL setup("ACCOUNTING AUDIT FILE LIST")
	 CALL prtbtm(" F1-Exit")
	 CALL sndmsg(msg$)
	 COLOR 2, 0: LOCATE 3, 67: PRINT auditname$
	 COLOR 4, 0
	 LOCATE 3, 25: PRINT "VIEW  AUDIT  FILE"
	 COLOR 2: X = 28: x1 = 60
	 LOCATE 5, X - 8: PRINT "1.  Browse audit file"
	 LOCATE , X - 8: PRINT "2.  Produce extract file"
	 LOCATE , X - 8: PRINT "3.  Creditor/Debtor entries"
	 LOCATE , X - 8: PRINT "4.  Select file"
	 LOCATE , X - 8: PRINT "5.  Daily totals"
	 LOCATE , X - 8: PRINT "6.  Display totals"
	 LOCATE , X - 8: PRINT "7.  List debtor payments"
	 LOCATE , X - 8: PRINT "8.  Link period end records"
	 LOCATE , X - 8: PRINT "9.  Page eject"
	 LOCATE , X - 8: PRINT "10  Set Active/Inactive flag"
	 LOCATE , X - 20: PRINT ""
	 LOCATE , X - 20: PRINT "31.   Creditors tools                  41.  Debtors tools           "
	 LOCATE , X - 20: PRINT "32.   Aged creditors report            42.  Aged debtors report     "
	 LOCATE , X - 20: PRINT "33.   Reload creditors o/balance       43.  Reload debtors o/balance"
	 LOCATE , X - 20: PRINT "34.   Current creditors report         44.  Current debtors report  "
	 LOCATE , X - 20: PRINT "35.   Closing balance integrity        45.  Closing balance integrity"
	 LOCATE , X - 20: PRINT ""
	 LOCATE , X - 20: PRINT "51.  Archive previous months"
'>>>>> Right hand side
	 LOCATE 5, x1: PRINT "99.  Daily Total"

	COLOR 2, 0
	LOCATE 22, X: PRINT "Enter option..> "; CHR$(FNH);
	CALL inpnew(opt$, 102!, updwn%, "13,59" + ALT$): GOSUB ALT
	msg$ = ""
	IF updwn% = 59 THEN GOTO endpgm
	opt% = VAL(opt$): opt2% = 1
	IF opt% = 1 THEN GOSUB browse: GOTO start

	IF opt% = 2 OR opt% = 3 THEN
		 GOSUB get.types
		 IF opt2% = 6 THEN CLOSE : npgm$ = "ASAUD02": CALL EXITPGM(npgm$): CHAIN npgm$
		 IF updwn% = 59 THEN opt% = 0
		 IF updwn% = 60 THEN opt% = 0
		END IF

	IF opt% = 7 THEN
		 opt2% = 8
		 GOSUB get.pay.types
		 IF updwn% = 59 THEN opt% = 0
		 IF updwn% = 60 THEN opt% = 0
		END IF

	IF opt% = 5 THEN
		begyymd$ = "00000000": beg$ = "0000": begday$ = "00"
		endyymd$ = "99999999": end$ = "9999": endday$ = "99"
		PCOPY 0, 1
		CALL BOX(21, 9, 56, 11, 14, 0, 1)
		COLOR 7, 0
		begdmy$ = DATE1$
		LOCATE 10, X - 5: PRINT "Enter start date...>"; begdmy$
		LOCATE 10, X + 15: CALL inpnew(begdmy$, 100!, updwn%, "13,59-60" + ALT$): GOSUB ALT
		begyymd$ = FNDY$(begdmy$) '.dc
		endyymd$ = begyymd$ '.dc
		IF updwn% = 59 THEN GOTO start
		IF updwn% = 60 THEN GOTO start
		PCOPY 1, 0

		GOSUB SUMJRNLS
		GOTO start
		END IF

	IF opt% = 6 THEN
		 GOSUB get.dates
		 IF updwn% = 59 THEN updwn% = 0: GOTO start
		 GOSUB SUMJRNLS
		 GOTO start
	END IF

	IF opt% = 8 THEN CALL rebldpe(ok%): opt$ = "1"
	IF opt% = 9 THEN LPRINT CHR$(12)
	IF opt% = 10 THEN
		begyymd$ = "00000000": beg$ = "0000": begday$ = "00"
		endyymd$ = "99999999": end$ = "9999": endday$ = "99"
		PCOPY 0, 1
		CALL BOX(21, 9, 56, 11, 14, 0, 1)
		COLOR 7, 0
		begdmy$ = DATE1$
		LOCATE 10, X - 5: PRINT "Enter start date...>"; begdmy$
		LOCATE 10, X + 15: CALL inpnew(begdmy$, 100!, updwn%, "13,59-60" + ALT$): GOSUB ALT
		begyymd$ = FNDY$(begdmy$) '.dc
		IF updwn% = 59 THEN GOTO start
		IF updwn% = 60 THEN GOTO start
		PCOPY 1, 0

		GOSUB LISTNONACTIVE
		GOTO start
		END IF

	IF opt% = 1 OR opt% = 2 OR opt% = 3 OR opt% = 7 THEN
		GOSUB get.dates
		IF updwn% = 59 THEN GOTO start
		IF updwn% = 60 THEN GOTO start
		GOSUB do.list
	END IF


	IF opt% = 31 THEN CLOSE : ENVIRON "DB.OR.CR$=CR": npgm$ = "ASAUD03": CALL EXITPGM(npgm$): CHAIN npgm$
	IF opt% = 32 THEN CLOSE : ENVIRON "DB.OR.CR$=CR": npgm$ = "ASAUD04": CALL EXITPGM(npgm$): CHAIN npgm$
	IF opt% = 33 THEN CLOSE : ENVIRON "DB.OR.CR$=CR": npgm$ = "ASAUD02": CALL EXITPGM(npgm$): CHAIN npgm$
	IF opt% = 34 THEN CLOSE : ENVIRON "DB.OR.CR$=CR": npgm$ = "ASAUD05": CALL EXITPGM(npgm$): CHAIN npgm$
	IF opt% = 35 THEN CLOSE : ENVIRON "DB.OR.CR$=CR": npgm$ = "ASAUD60": CALL EXITPGM(npgm$): CHAIN npgm$

	IF opt% = 41 THEN CLOSE : ENVIRON "DB.OR.CR$=DB": npgm$ = "ASAUD03": CALL EXITPGM(npgm$): CHAIN npgm$
	IF opt% = 42 THEN CLOSE : ENVIRON "DB.OR.CR$=DB": npgm$ = "ASAUD04": CALL EXITPGM(npgm$): CHAIN npgm$
	IF opt% = 43 THEN CLOSE : ENVIRON "DB.OR.CR$=DB": npgm$ = "ASAUD02": CALL EXITPGM(npgm$): CHAIN npgm$
	IF opt% = 44 THEN CLOSE : ENVIRON "DB.OR.CR$=DB": npgm$ = "ASAUD05": CALL EXITPGM(npgm$): CHAIN npgm$
	IF opt% = 45 THEN CLOSE : ENVIRON "DB.OR.CR$=DB": npgm$ = "ASAUD60": CALL EXITPGM(npgm$): CHAIN npgm$

	IF opt% = 51 THEN CLOSE : npgm$ = "ASAUD07": CALL EXITPGM(npgm$): CHAIN npgm$
	IF opt$ = "99" THEN
		CLOSE #8
		cashonly$ = "Y"
		GOSUB OPEN.AUDIT
		GOTO start
	END IF
	IF opt$ = "70" THEN parm$ = "PARM$=V": ENVIRON parm$: RUN
	IF opt$ = "71" THEN parm$ = "PARM$=W": ENVIRON parm$: RUN
	IF opt$ = "4" THEN
		CALL selectfile(sel%, updwn%)
		IF updwn% = 13 THEN
				CLOSE #8
				cashonly$ = "M": auditname$ = auditfile$(sel%)
				GOSUB OPEN.AUDIT
				GOTO start
				END IF
		END IF
	GOTO start
endpgm:
	 CLOSE
	 CALL EXITPGM(apgm$)
	 CHAIN apgm$
	 END
'///////////////////////////////////////////////////////////////////////
'>>>> Get types
'///////////////////////////////////////////////////////////////////////
get.types:
	 PCOPY 0, 1
	 CALL BOX(26, 6, 51, 17, 14, 0, 1)
	 COLOR 7, 0
	 DO
	LOCATE 7, X: PRINT "Credit/Debtor.>"; CorD$
	LOCATE , X: PRINT "1. All"
	LOCATE , X: PRINT "2. Invoices"
	LOCATE , X: PRINT "3. Credits"
	LOCATE , X: PRINT "4. Payments/Discounts"
	LOCATE , X: PRINT "5. Journal Entries"
	LOCATE , X: PRINT "6. Summary listing"
	LOCATE , X: PRINT "7. Select GL number"
	DO
		LOCATE 7, X + 15: COLOR 2, 0
		CALL inpnew(CorD$, 101!, updwn%, "13,59,60" + ALT$): GOSUB ALT
		IF updwn% = 59 THEN EXIT DO
		CorD$ = UCASE$(CorD$)
	LOOP UNTIL CorD$ = "C" OR CorD$ = "D"

	LOCATE 15, X + 5: PRINT "Option..> "; CHR$(FNH);
	CALL inpnew(opt2$, 1!, updwn%, "13,59,60" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN EXIT DO
	IF updwn% = 60 THEN EXIT DO
	opt2% = VAL(opt2$)
	LOOP UNTIL opt2% >= 1 AND opt2% <= 7

	IF opt% = 2 THEN
		repost$ = "N"
		DO
		LOCATE 16, X + 5: PRINT "Repost...>"; repost$; CHR$(FNH);
		CALL inpnew(repost$, 101!, updwn%, "13,59,60" + ALT$): GOSUB ALT
		IF updwn% = 59 THEN GOTO xget.types
		IF updwn% = 60 THEN GOTO xget.types
		repost$ = UCASE$(repost$)
		LOOP UNTIL repost$ = "Y" OR repost$ = "N"
	END IF


	 selgl% = 0
	 IF opt2% = 7 THEN
		opt2% = 1
		LOCATE 16, X + 5: PRINT "Enter GL..> "; CHR$(FNH);
		CALL inpnew(selgl$, 3!, updwn%, "13,59,60" + ALT$): GOSUB ALT
		selgl% = VAL(selgl$)
	 END IF

xget.types:
	 PCOPY 1, 0
RETURN
'///////////////////////////////////////////////////////////////////////
'>>> GET pay types
'///////////////////////////////////////////////////////////////////////
get.pay.types:
	 PCOPY 0, 1
	 CALL BOX(26, 6, 51, 12, 14, 0, 1)
	 COLOR 7, 0
	 opt3$ = "1"
	 DO
	LOCATE 7, X: PRINT "Credit/Debtor.>"; CorD$
	LOCATE , X: PRINT "1. Error details only"
	LOCATE , X: PRINT "2. All payment totals"
	LOCATE , X: PRINT "3. All payment details"
	LOCATE 11, X + 5: PRINT "Option..> "; CHR$(FNH);

	IF CordD$ <> "C" AND CordD$ <> "D" THEN CorD$ = "D"
	DO
		LOCATE 7, X + 15
		CALL inpnew(CorD$, 101!, updwn%, "13,59,60" + ALT$): GOSUB ALT
		CorD$ = UCASE$(CorD$)
		LOOP UNTIL CorD$ = "C" OR CorD$ = "D"

	LOCATE 11, X + 15
	CALL inpnew(opt3$, 1!, updwn%, "13,59,60" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN EXIT DO
	IF updwn% = 60 THEN EXIT DO
	opt3% = VAL(opt3$)
	 LOOP UNTIL opt3% >= 1 AND opt3% <= 3
xget.pay.types:
	 PCOPY 1, 0
RETURN
'///////////////////////////////////////////////////////////////////////
'>>>>>  Get start and finish dates
'///////////////////////////////////////////////////////////////////////
get.dates:
	 PCOPY 0, 1
	 CALL BOX(21, 9, 56, 13, 14, 0, 1)
	 COLOR 7, 0
	 LOCATE 10, X - 5: PRINT "Enter start month..>"; beg$; "  Day "; begday$
	 LOCATE 11, X - 5: PRINT "       last month..>"; end$; "      "; endday$
	 IF opt% <> 2 THEN
		LOCATE 12, X - 5: PRINT "Supplier  (*=All)..>"; supa$
		END IF
	 COLOR 0, 3: LOCATE 25, 30: PRINT "F10-Search all audit files"; : COLOR 2, 0
scf1:
	 LOCATE 10, X + 15: CALL inpnew(beg$, 4!, updwn%, "13,59-60" + ALT$): GOSUB ALT
	 IF updwn% = 59 THEN GOTO xget.dates
	 IF updwn% = 60 THEN GOTO scf1
scf2:
	 LOCATE 11, X + 15: CALL inpnew(end$, 4!, updwn%, "13,59-60" + ALT$): GOSUB ALT
	 IF updwn% = 59 THEN GOTO xget.dates
	 IF updwn% = 60 THEN GOTO scf1
	 IF opt% = 2 THEN GOTO scf99
scf3:
	 LOCATE 12, X + 15: CALL inpnew(supa$, 105!, updwn%, "13,59-60" + ALT$): GOSUB ALT
	 supa$ = UCASE$(supa$)
	 IF updwn% = 59 THEN GOTO xget.dates
	 IF updwn% = 60 THEN GOTO scf4
	 GOTO scf99
scf4:
	 LOCATE 10, X + 25: CALL inpnew(begday$, 2!, updwn%, "13,59-60" + ALT$): GOSUB ALT
	 IF updwn% = 59 THEN GOTO xget.dates
	 IF updwn% = 60 THEN GOTO scf1
scf5:
	 LOCATE 11, X + 25: CALL inpnew(endday$, 2!, updwn%, "13,59-60" + ALT$): GOSUB ALT
	 IF updwn% = 59 THEN GOTO xget.dates
	 IF updwn% = 60 THEN GOTO scf4


scf99:
	'.dc
	 begyymd$ = "yyyymm01"
	 MID$(begyymd$, 3, 2) = MID$(beg$, 3, 2)
	 MID$(begyymd$, 5, 2) = MID$(beg$, 1, 2)
	 IF MID$(begyymd$, 3, 2) > "73" THEN
		MID$(begyymd$, 1, 2) = "19"
	 ELSE
		MID$(begyymd$, 1, 2) = "20"
	 END IF
	 endyymd$ = "yyyymm99"
	 MID$(endyymd$, 3, 2) = MID$(end$, 3, 2)
	 MID$(endyymd$, 5, 2) = MID$(end$, 1, 2)
	 IF MID$(endyymd$, 3, 2) > "73" THEN
		MID$(endyymd$, 1, 2) = "19"
	 ELSE
		MID$(endyymd$, 1, 2) = "20"
	 END IF
	 '.dc

	'>> Should the search look through history files?
	 yy% = VAL(MID$(beg$, 3, 2)): mm% = VAL(MID$(beg$, 1, 2))
	 yynow% = VAL(MID$(DATE$, 9, 2))
	 IF mm% > 6 THEN yy% = yy% + 1
	 IF yy% > 99 THEN yy% = 0
	 IF yy% < yynow% THEN spec$ = "y" ELSE spec$ = "n"

xget.dates:
	PCOPY 1, 0
RETURN
'/////////////////////////////////////////////////////////////////////////////
'>>>>>   M A S T E R    A C C E S S O R Y    L I S T
'/////////////////////////////////////////////////////////////////////////////
do.list:
	tot.list@ = 0: tot.paymt@ = 0
	fetch% = -1
	count% = 0

	OPEN STDOUT$ FOR OUTPUT SHARED AS #99
	IF opt% = 2 THEN OPEN "Z:\FORDEX\MYOBIO\ASAUDIT.txt" FOR OUTPUT AS #98
	 CALL setmhdr

	 FOR i% = 1 TO naudit%
	 CLOSE #8
	 cashonly$ = "M": auditname$ = auditfile$(i%)
	 COLOR 2, 0: LOCATE 3, 67: PRINT auditname$
	 GOSUB OPEN.AUDIT


	 CALL search.month(Rec%, begyymd$)
	 IF Rec% = -1 THEN GOTO xdo.next

	 GET #8, Rec%, audit
	 DO WHILE NOT EOF(8)
		'.dc
		'dymd$ = "  /  /  "
		'MID$(dymd$, 1, 2) = MID$(FNDYY$(Audit.addate$), 7, 2)
		'MID$(dymd$, 4, 2) = MID$(FNDYY$(Audit.addate$), 4, 2)
		'MID$(dymd$, 7, 2) = MID$(FNDYY$(Audit.addate$), 1, 2)
		'IF dymd$ > end ymd$ AND Audit.adtype$ = "PE" THEN EXIT DO
		IF audit.aDdate > endyymd$ AND audit.adtype$ = "PE" THEN EXIT DO
		ok% = -1
		IF audit.aDdate < begyymd$ THEN ok% = 0
		IF supa$ <> "*" AND supa$ <> audit.adcust$ THEN ok% = 0
		IF audit.adtype$ <> "LC" THEN
		IF audit.adtype$ <> "LD" THEN
		IF audit.adtype$ <> "PT" THEN
			IF CorD$ <> MID$(audit.adtype$, 1, 1) THEN ok% = 0
		END IF
		END IF
		END IF

		IF opt2% = 4 THEN
			tmp$ = MID$(audit.adtype$, 2, 1)
			IF audit.adtype$ <> "PT" AND tmp$ <> "P" THEN ok% = 0
		END IF
		IF audit.adtype$ = "PE" THEN ok% = 0

		IF opt% = 2 THEN
			ok% = 0
			IF audit.adtype$ = "DI" THEN ok% = -1
			IF audit.adtype$ = "DC" THEN ok% = -1
			IF repost$ = "N" AND ok% AND audit.adpaid$ = "M" THEN ok% = 0'MYOB Posted
		END IF

		IF NOT ok% THEN GOTO do.next

		IF selgl% > 0 OR opt% = 2 THEN
		IF MID$(audit.adtype$, 1, 1) = "D" THEN
				skey$ = audit.adcust$
				GOSUB searchindex.cus
				sno% = CVI(supx.wrrn$)
				chw% = 43'Channel of cus file
				IF sno% < 1 OR sno% > maxcus% THEN LSET audit.adcust$ = "AAAAA": sno% = 1
		ELSE
				skey$ = audit.adcust$
				GOSUB searchindex.sup
				sno% = CVI(supx.wrrn$)
				chw% = 44       '***** Channel of sup file
				IF sno% < 1 OR sno% > maxsup% THEN LSET audit.adcust$ = "AAAAA": sno% = 1
		END IF

			GET #chw%, sno%, sup
			audit.adglacc! = CVS(sup.sgl$)
			IF selgl% > 0 AND audit.adglacc! <> selgl% THEN GOTO do.next
			END IF

		IF lin% >= 48 THEN fetch% = -1
		adnxtpe% = CVI(MID$(audit.adsname$, 1, 2))
		adprepe% = CVI(MID$(audit.adsname$, 3, 2))
		adlstpe% = CVI(MID$(audit.adsname$, 5, 2))

	'>>>>>  And now the actual print
	IF Rec% MOD 100 = 0 THEN
		msg$ = "Printing audit record " + STR$(Rec%) + " out of " + STR$(adlast%) + " off " + auditname$
		CALL sndmsg(msg$)
		X$ = INKEY$: IF X$ = CHR$(0) + CHR$(59) THEN EXIT FOR
	END IF

	SELECT CASE opt%
	CASE 2
		PRINT #98, MYOB$ + CHR$(13) + CHR$(10) + CHR$(13) + CHR$(10);
		audit.adpaid$ = "M"
		PUT #8, Rec%, audit
		count% = count% + 1


	CASE 3: '**** Cred/debtor file
		tot.list@ = tot.list@ + audit.advalue
		IF fetch% THEN GOSUB heading
		'AJD
		PRINT #99, USING "#####  \      \  ###  \   \-\                            \  \\  \       \  \   \  $$##,###.##  $$#,###.##  $$#,###.##  \            \"; audit.adrec%; FNDYY$(audit.aDdate$); audit.adglacc!; audit.adcust$; audit.adsname$; audit. _
adtype$; audit.addocnum$; paidsts(audit.adpaid$, "L"); audit.advalue; audit.adtax; (audit.advalue / 11); audit.adtext$

			'PRINT #99, USING "##,###    \      \     ###     \   \-\                       \    \\  \       \   \      \   $$###,###.##     \              \";
			'Audit.adrec%; FNDYY$(Audit.addate$); Audit.adglacc!; Audit.adcust$; Audit.adsname$; Audit.adtype$; Audit.addocnum$; paidsts(Audit.adpaid$, "L"); Audit.advalue; Audit.adtext$
		lin% = lin% + 1

	CASE 7: '***** Debtor payment details (check)
		IF audit.adtype$ = "DP" OR audit.adtype$ = "DD" OR audit.adtype$ = "LC" THEN
		num.in.batch% = num.in.batch% + 1
		rrn%(num.in.batch%) = Rec%
		IF audit.adtype$ = "DP" THEN tot.paymt@ = tot.paymt@ + audit.advalue
		IF audit.adtype$ = "LC" THEN tot.paymt@ = tot.paymt@ + audit.advalue
		END IF
		IF audit.adtype$ = "PT" THEN
		work@ = tot.paymt@ - audit.advalue
		batch.bal% = -1: IF ABS(work@) >= .01 THEN batch.bal% = 0
		IF NOT batch.bal% OR opt3% = 2 OR opt3% = 3 THEN
		GOSUB prt.batch
		END IF
		FOR ii% = 1 TO num.in.batch%: rrn%(ii%) = 0: NEXT
		num.in.batch% = 0
		tot.paymt@ = 0
		END IF
	CASE ELSE: BEEP
	END SELECT

do.next:
	IF Rec% MOD 500 = 0 THEN msg$ = "Record" + STR$(Rec%) + " off " + auditname$: CALL sndmsg(msg$)
	GET #8, , audit: Rec% = Rec% + 1
	LOOP

	CALL sndmsg(msg$)

xdo.next:
	 NEXT

xdo.list:
	IF opt% = 2 THEN CLOSE #98
	IF pag% > 0 THEN PRINT #99, "End of Report"
	IF pag% > 0 THEN PRINT #99, CHR$(18); CHR$(12);
	CLOSE #99

	IF opt% = 2 THEN
		msg$ = (STR$(count%) + " invoices prepared for MYOB.")
	END IF

RETURN
'/////////////////////////////////////////////////////////////////////////////
'>>>>>   G E N E R A L      H E A D I N G
'/////////////////////////////////////////////////////////////////////////////
heading:
	 fetch% = 0
	 pag% = pag% + 1: lin% = 0
	 IF pag% > 1 THEN PRINT #99, CHR$(12)
	 IF opt% = 2 THEN head$ = "A U D I T    F I L E    L I S T I N G"
	 head$ = "A U D I T    F I L E    L I S T I N G"
	 'ajd
	 IF opt% = 3 THEN col$ = "Num Date  GL Name                    Ref.  Sta   Amt.   Amt.   Amt.  Notes."
	 'IF opt% = 3 THEN col$ = "Num.  Date   G/L  Name                Ref...   Status  Amount   Notes          "
	 IF opt% = 7 THEN col$ = " Date.  No.     Date.  Cde. Name.                  Amt.   T              Total."
	 head2$ = ""
	 IF opt2% = 1 THEN head2$ = "(All)"
	 IF opt2% = 2 THEN head2$ = "(Invoices)"
	 IF opt2% = 3 THEN head2$ = "(Credits)"
	 IF opt2% = 4 THEN head2$ = "(Payments/Discounts)"
	 IF opt2% = 5 THEN head2$ = "(Journal Entries)"
	 IF opt2% = 8 THEN head2$ = "(Payment Reconciliation)"
	 IF opt2% = 9 THEN head2$ = "(Control Entries)"
'//////////////////  print actual heading       ////////////////////////
	 PRINT #99, CHR$(18);
	 PRINT #99, "#asaud01"; TAB(66); "Date:"; DATE1$
	 PRINT #99, CHR$(14); msmisc.cc$
	 PRINT #99, " "
	 IF DB.OR.CR$ = "CREDITORS" THEN
	PRINT #99, "          C R E D I T O R S    "; head$
	 ELSE
	PRINT #99, "              D E B T O R S    "; head$
	 END IF
	 PRINT #99,
	 PRINT #99, head2$, TAB(73); "Page:"; pag%
	 PRINT #99, ""
	 PRINT #99, col$
	 PRINT #99, STRING$(79, "-")
'//////////////////  Condensed mode              ///////////////////////
	 IF opt% = 1 THEN PRINT #99, CHR$(15);
	 IF opt% = 2 THEN PRINT #99, CHR$(15);
	 IF opt% = 3 THEN PRINT #99, CHR$(15);
	 IF opt% = 4 THEN PRINT #99, CHR$(15);
	 IF opt% = 7 THEN PRINT #99, CHR$(15);
RETURN
'/////////////////////////////////////////////////////////////////////////////
'>>>>- Print a payment batch
'/////////////////////////////////////////////////////////////////////////////
prt.batch:      '>>>>> Print a payment batch
	 hld.rec% = Rec%
	 IF opt3% = 2 THEN GOTO total.only
	 tot.paymt@ = 0
'/////////////////  List the details of the batch //////////////////////
	 FOR J% = 1 TO num.in.batch%
		IF lin% >= 48 THEN fetch% = -1
		GET #8, rrn%(J%), audit
		'/////////////////  Convert fields to numeric     //////////////////////
		adnxtpe% = CVI(MID$(audit.adsname$, 1, 2))
		adprepe% = CVI(MID$(audit.adsname$, 3, 2))
		adlstpe% = CVI(MID$(audit.adsname$, 5, 2))
		IF audit.adtype$ = "DP" THEN tot.paymt@ = tot.paymt@ + audit.advalue
		IF audit.adtype$ = "LC" THEN tot.paymt@ = tot.paymt@ + audit.advalue
		tot.list@ = tot.list@ + audit.advalue
		IF fetch% THEN GOSUB heading
		PRINT #99, USING "  \       \    \          \\       \    &   &    $$###,###.##     \\   \              \    $$###,###.##"; FNDYY$(audit.aDdate$); audit.addocnum$; FNDYY$(audit.aDdate$); audit.adcust$; audit.adsname$; audit.advalue; audit. _
adtype$; audit.adtext$; tot.paymt@
		lin% = lin% + 1
		rrn%(J%) = 0
		NEXT
total.only:
	GET #8, hld.rec%, audit
	'/////////////////  Convert fields to numeric     //////////////////////
	adnxtpe% = CVI(MID$(audit.adsname$, 1, 2))
	adprepe% = CVI(MID$(audit.adsname$, 3, 2))
	adlstpe% = CVI(MID$(audit.adsname$, 5, 2))
	LSET audit.addocnum$ = "Rec" + MID$(STR$(audit.adrec%), 2)

	IF NOT batch.bal% THEN
		a$ = " ** ERROR *** "
		IF fetch% THEN GOSUB heading
		PRINT #99, USING "  \       \    \          \\       \    &   &    $$###,###.##     \\      \              \ $$###,###.##"; FNDYY$(audit.aDdate$); audit.addocnum$; FNDYY$(audit.aDdate$); audit.adcust$; audit.adsname$; audit.advalue; audit. _
adtype$; a$; tot.paymt@
		ELSE
		a$ = "-------------->"
		IF fetch% THEN GOSUB heading
		PRINT #99, USING "  \       \    \          \\       \    &   &    $$###,###.##     \\      \              \             "; FNDYY$(audit.aDdate$); audit.addocnum$; FNDYY$(audit.aDdate$); audit.adcust$; audit.adsname$; audit.advalue; audit. _
adtype$; a$
		END IF

	lin% = lin% + 1
	tot.paymt@ = 0
RETURN
'/////////////////////////////////////////////////////////////////////////////
'>>>>>  S U M
'/////////////////////////////////////////////////////////////////////////////
SUMJRNLS:
SUMJRNLS.0:
	'/////////////////  Clear out totals            ////////////////////////
	 tot.di@ = 0: tot.dc@ = 0: tot.dp@ = 0: tot.dd@ = 0: tot.dt@ = 0
	 tot.ci@ = 0: tot.cc@ = 0: tot.cp@ = 0: tot.cd@ = 0: tot.ct@ = 0
	 tot.cj@ = 0: tot.dj@ = 0: tot.pt@ = 0: tot.ot@ = 0
	 tot.lc@ = 0: tot.ld@ = 0

	 tot.cash% = 0: tot.cheq% = 0: tot.card% = 0: tot.counter% = 0
	 tot.cash@ = 0: tot.cheq@ = 0: tot.card@ = 0: tot.counter@ = 0


	 '>-GST Summary Totals
	 tot.ci.incgst0@ = 0: tot.ci.nogst0@ = 0: tot.ci.partgst0@ = 0
	 tot.ci.incgst1@ = 0: tot.ci.nogst1@ = 0: tot.ci.partgst1@ = 0
	 tot.di.incgst0@ = 0: tot.di.nogst0@ = 0: tot.di.partgst0@ = 0
	 tot.di.incgst1@ = 0: tot.di.nogst1@ = 0: tot.di.partgst1@ = 0


	 FOR i% = 1 TO 999: gltot.p@(i%) = 0: gltot.n@(i%) = 0: NEXT

	 FOR i% = 1 TO naudit%
	 IF opt% = 5 AND i% > 1 THEN EXIT FOR

	 CLOSE #8
	 cashonly$ = "M"
	 IF opt% = 5 THEN cashonly$ = "Y"
	 auditname$ = auditfile$(i%)
	 GOSUB OPEN.AUDIT


	 CALL search.month(Rec%, begyymd$)
	 IF opt% = 5 THEN Rec% = 1
	 IF Rec% < 0 THEN GOTO J.next
	 GET #8, Rec%, audit
	 hld.addate$ = "  /  /  "

	IF audit.aDdate$ < begyymd$ THEN '.dc
		COLOR 7: LOCATE 24, 26
		PRINT USING "¹ Searching... \          \ Ì"; begyymd$; '.dc
		hld.addate$ = FNDYY$(audit.aDdate$)
	END IF

	'/////////////////   Now read forward           ////////////////////////
	 DO WHILE NOT EOF(8)
	'dymd$ = "  /  /  " '.dc
	'MID$(dymd$, 1, 2) = MID$(FNDYY$(Audit.addate$), 7, 2)
	'MID$(dymd$, 4, 2) = MID$(FNDYY$(Audit.addate$), 4, 2)
	'MID$(dymd$, 7, 2) = MID$(FNDYY$(Audit.addate$), 1, 2)
	IF audit.aDdate > endyymd$ AND audit.adtype$ = "PE" THEN EXIT DO '.dc
	'///////////  Edit tranaction to see if it should be included  /////////
	ok% = -1
	IF supa$ <> "*" AND supa$ <> audit.adcust$ THEN ok% = 0
	'IF MID$(dymd$, 7, 2) < begday$ THEN ok% = 0  '.dc
	'IF MID$(dymd$, 7, 2) > endday$ THEN ok% = 0  '.dc
	IF audit.aDdate > endyymd$ THEN ok% = 0  'I wonder. '.dc
	IF opt% = 5 AND audit.aDdate <> begyymd$ THEN ok% = 0 '.dc


	IF ok% THEN
		IF hld.addate$ <> FNDYY$(audit.aDdate$) THEN
			COLOR 7: LOCATE 24, 26
			PRINT USING "¹ Loading..... \          \ Ì"; FNDYY$(audit.aDdate$);
			hld.addate$ = FNDYY$(audit.aDdate$)
			END IF

		 Value@ = audit.advalue
		 Value@ = Value@ * 100
		 Value@ = FIX(Value@) / 100
		 dp3@ = audit.advalue - Value@
		 IF Value@ > 0 AND dp3@ >= .005 THEN Value@ = Value@ + .01
		 IF Value@ < 0 AND dp3@ <= -.005 THEN Value@ = Value@ - .01
		 IF dp3@ <> 0 THEN
				CALL sndmsg("3 decimal places found on record " + STR$(Rec%) + " " + STR$(audit.advalue) + " Enter to continue. Z=Fix")
				X$ = INPUT$(1)
				IF X$ = "Z" OR X$ = "z" THEN
					 audit.advalue = Value@
					 PUT #8, Rec%, audit
				END IF
			END IF

		 tax! = audit.adtax
		 CALL ROUND(tax!, 2.5)
		 dp3@ = audit.adtax - tax!
		 IF tax! > 0 AND dp3@ >= .005 THEN tax! = tax! + .01
		 IF tax! < 0 AND dp3@ <= -.005 THEN tax! = tax! - .01
		 IF dp3@ <> 0 THEN
		CALL sndmsg("3 decimal places found on tax " + STR$(Rec%) + " " + STR$(audit.adtax) + " Enter to continue. Z=Fix")
		X$ = INPUT$(1)
		IF X$ = "Z" OR X$ = "z" THEN
			 audit.adtax = tax!
			 PUT #8, Rec%, audit
		END IF
		END IF


		 'DMR111: Fix the sign on GST (G.S.T)
		 IF audit.adtax <> 0 THEN
		 IF (Value@ < 0 AND tax! > 0) OR (Value@ > 0 AND tax! < 0) THEN
			 CALL sndmsg("Wrong tax sign " + audit.adcust + " " + audit.adtype$ + STR$(Rec%) + " " + STR$(audit.adtax) + " of " + STR$(audit.advalue) + " Enter,Z=Fix.")
			 X$ = INPUT$(1)
			 IF X$ = "Z" OR X$ = "z" THEN
					audit.adtax = 0 - audit.adtax
					PUT #8, Rec%, audit
			 END IF
		 END IF
		 END IF

		 'DMR: The G.S.T. should be 10% of the total.
		 IF NOT skipall% THEN
		 IF audit.adtax <> 0 THEN
			 tmp = audit.advalue / 11
			 CALL ROUND(tmp, 2.5)
			 IF audit.adtype$ = "PE" AND (audit.advalue <> 0 OR audit.adtax <> 0) THEN
					 audit.advalue = 0
					 audit.adtax = 0
					 PUT #8, Rec%, audit
			 END IF

			 IF audit.adtax > tmp THEN
				 CALL sndmsg("GST Wrong " + audit.adcust$ + STR$(Rec%) + " " + audit.adtype$ + ":" + STR$(audit.adtax) + " of " + STR$(audit.advalue) + " Enter,Z=Fix,Esc=Skip All.")
				 X$ = INPUT$(1)
				 IF X$ = "Z" OR X$ = "z" THEN
					 audit.adtax = tmp
					 PUT #8, Rec%, audit
				 END IF
				 IF X$ = CHR$(27) THEN skipall% = -1: CALL sndmsg("")
			 END IF
			 IF audit.adtax < tmp THEN
				 CALL sndmsg("GST Sus? " + audit.adcust$ + STR$(Rec%) + " " + audit.adtype$ + ":" + STR$(audit.adtax) + " of " + STR$(audit.advalue) + " Enter,Z=Fix,Esc=Skip All.")
				 X$ = INPUT$(1)
				 IF X$ = "Z" OR X$ = "z" THEN
				audit.adtax = tmp
				PUT #8, Rec%, audit
				 END IF
				 IF X$ = CHR$(27) THEN skipall% = -1: CALL sndmsg("")
			 END IF

		 END IF
		 END IF



		 SELECT CASE audit.adtype$
			CASE "DI": tot.di@ = tot.di@ + Value@
					 tot.dt@ = tot.dt@ + tax!
			CASE "DC": tot.dc@ = tot.dc@ + Value@
					 tot.dt@ = tot.dt@ + tax!
			CASE "DP": tot.dp@ = tot.dp@ + Value@
			CASE "DD": tot.dd@ = tot.dd@ + Value@
					 tot.dt@ = tot.dt@ + tax!
			CASE "DT": tot.dt@ = tot.dt@ + Value@
			CASE "PT": tot.pt@ = tot.pt@ + Value@
			CASE "DJ": tot.dj@ = tot.dj@ + Value@
			CASE "CI": tot.ci@ = tot.ci@ + Value@
					 tot.ct@ = tot.ct@ + tax!
			CASE "CC": tot.cc@ = tot.cc@ + Value@
					 tot.ct@ = tot.ct@ + tax!
			CASE "CP": tot.cp@ = tot.cp@ + Value@
			CASE "CD": tot.cd@ = tot.cd@ + Value@
					 tot.ct@ = tot.ct@ + tax!
			CASE "CT": tot.ct@ = tot.ct@ + Value@
			CASE "CJ": tot.cj@ = tot.cj@ + Value@
			CASE "LC": tot.lc@ = tot.lc@ + Value@
			CASE "LD": tot.ld@ = tot.ld@ + Value@
			CASE ELSE: tot.ot@ = tot.ot@ + Value@
		 END SELECT


		 SELECT CASE audit.adtype$
		 CASE "CI", "CC", "CD"  'DMR 01/03/02
		 IF tax! = 0 THEN
			 tot.ci.nogst0@ = tot.ci.nogst0@ + tax!
			 tot.ci.nogst1@ = tot.ci.nogst1@ + Value@
		 ELSE
			 theoryGST = (Value@ / 11): CALL ROUND(theoryGST, 2.5)
			 IF tax! <> theoryGST THEN  'ajd
				 tot.ci.partgst0@ = tot.ci.partgst0@ + tax!
				 tot.ci.partgst1@ = tot.ci.partgst1@ + Value@
			 ELSE
				 tot.ci.incgst0@ = tot.ci.incgst0@ + tax!
				 tot.ci.incgst1@ = tot.ci.incgst1@ + Value@
			 END IF
		 END IF

		 CASE "DI", "DC", "DD"  'DMR 01/03/02
		 IF tax! = 0 THEN
			 tot.di.nogst0@ = tot.di.nogst0@ + tax!
			 tot.di.nogst1@ = tot.di.nogst1@ + Value@
		 ELSE
			 theoryGST = (Value@ / 11): CALL ROUND(theoryGST, 2.5)
			 IF tax! <> theoryGST THEN  'ajd
				 tot.di.partgst0@ = tot.di.partgst0@ + tax!
				 tot.di.partgst1@ = tot.di.partgst1@ + Value@
			 ELSE
				 tot.di.incgst0@ = tot.di.incgst0@ + tax!
				 tot.di.incgst1@ = tot.di.incgst1@ + Value@
			 END IF
		 END IF

		 END SELECT

		 IF INSTR(audit.adtext$, "Cash") > 0 THEN tot.cash@ = tot.cash@ + Value@: tot.cash% = tot.cash% + 1
		 IF INSTR(audit.adtext$, "Cheque") > 0 THEN tot.cheq@ = tot.cheq@ + Value@: tot.cheq% = tot.cheq% + 1
		 IF INSTR(audit.adtext$, "Card") > 0 THEN tot.card@ = tot.card@ + Value@: tot.card% = tot.card% + 1
		 IF INSTR(audit.adtext$, "Counter") > 0 THEN tot.counter@ = tot.counter@ + Value@: tot.counter% = tot.counter% + 1

		 '>>- Accumulate journal screen
		 gl% = audit.adglacc!
		 IF gl% < 1 OR gl% > 998 THEN gl% = 999
		 IF Value@ >= 0 THEN
			gltot.p@(gl%) = gltot.p@(gl%) + Value@
			ELSE
			gltot.n@(gl%) = gltot.n@(gl%) + Value@
			END IF


	END IF
	GET #8, , audit: Rec% = Rec% + 1
	LOOP

J.next:
	NEXT

SUMJRNLS.1:
	 FOR i% = 1 TO 26: X$ = INKEY$: NEXT
	 CALL setup("ACCOUNTING AUDIT FILE LIST")
	 CALL prtbtm("F1-Exit")
	 LOCATE 3, 10
	 COLOR 6, 0
	 LOCATE , 12: PRINT "           ACCOUNTING AUDIT FILE RECORD TYPES "
	 LOCATE , 12: PRINT "          ===================================="
	 tot.db@ = tot.di@ + tot.dc@ + tot.dp@ + tot.dd@ + tot.dj@
	 tot.cr@ = tot.ci@ + tot.cc@ + tot.cp@ + tot.cd@ + tot.cj@
	 COLOR 2, 0
	 IF opt% = 5 THEN
	 LOCATE , 24: PRINT "For date "; begdmy$; "      Code: "; supa$;
	 ELSE
	 LOCATE , 24: PRINT "Period "; beg$; "-"; end$; "      Code: "; supa$;
	 END IF
	 LOCATE , 8: PRINT
	 LOCATE , 8: PRINT USING "     CI - Creditors invoice            $$#,###,###.##-"; tot.ci@
	 LOCATE , 8: PRINT USING "     CC - Creditors credit             $$#,###,###.##-"; tot.cc@
	 LOCATE , 8: PRINT USING "     CP - Creditors payment            $$#,###,###.##-"; tot.cp@
	 LOCATE , 8: PRINT USING "     CD - Creditors discount           $$#,###,###.##-"; tot.cd@
	 LOCATE , 8: PRINT USING "     CJ - Creditors journal            $$#,###,###.##-"; tot.cj@
	 LOCATE , 8: PRINT USING "     CT - Creditors G.S.T.             $$#,###,###.##-"; tot.ct@
	 LOCATE , 8: PRINT USING "                                       $$#,###,###.##-"; tot.cr@
	 LOCATE , 8: PRINT USING "     DI - Debtors invoice              $$#,###,###.##-"; tot.di@
	 LOCATE , 8: PRINT USING "     DC - Debtors credit               $$#,###,###.##-"; tot.dc@
	 LOCATE , 8: PRINT USING "     DP - Debtors payment              $$#,###,###.##-"; tot.dp@
	 LOCATE , 8: PRINT USING "     DD - Debtors discount (calculate) $$#,###,###.##-"; tot.dd@
	 LOCATE , 8: PRINT USING "     DJ - Debtors entry                $$#,###,###.##-"; tot.dj@
	 LOCATE , 8: PRINT USING "     DT - Debtors G.S.T.               $$#,###,###.##-"; tot.dt@


	 SELECT CASE opt%
	 CASE 5
	 COLOR 10, 0
	 LOCATE , 8: PRINT USING "     DI - Cash                            #,### $$#,###,###.##-"; tot.cash%; tot.cash@
	 LOCATE , 8: PRINT USING "     DI - Cheque                          #,### $$#,###,###.##-"; tot.cheq%; tot.cheq@
	 LOCATE , 8: PRINT USING "     DI - Credit Cards                    #,### $$#,###,###.##-"; tot.card%; tot.card@
	 LOCATE , 8: PRINT USING "     DI - Counter                         #,### $$#,###,###.##-"; tot.counter%; tot.counter@
	 COLOR 2, 0
	 LOCATE , 8: PRINT USING "                                          #,### $$#,###,###.##-"; tot.cash% + tot.cheq% + tot.card% + tot.counter%; tot.cash@ + tot.cheq@ + tot.card@ + tot.counter@
	 CASE ELSE
	 LOCATE , 8: PRINT USING "                                       $$#,###,###.##-"; tot.db@
	 LOCATE , 8: PRINT USING "     PT - Payment total                $$#,###,###.##-"; tot.pt@
	 LOCATE , 8: PRINT
	 LOCATE , 8: PRINT USING "     LC - Ledger Credits               $$#,###,###.##-"; tot.lc@
	 LOCATE , 8: PRINT USING "     LD - Ledger Debits                $$#,###,###.##-"; tot.ld@
	 END SELECT

	 supsav$ = supa$
	 COLOR 7: LOCATE 24, 26
	 a$ = LEFT$(supa$ + "     ", 5)
	 PRINT "¹Supplier  (*=All)..>"; a$; "Ì";
	 COLOR 2
	 CALL prtbtm("F1-Exit,  F6=GL  F7=GST")

	 DO
		LOCATE 24, 26 + 21
		CALL inpnew(supa$, 105!, updwn%, "13,59,64,65" + ALT$): GOSUB ALT
		supa$ = UCASE$(supa$)
		LOOP UNTIL updwn% = 59 OR updwn% = 64 OR updwn% = 65 OR supa$ <> supsav$
	 IF updwn% = 13 THEN GOTO SUMJRNLS.0
	 IF updwn% = 64 THEN
		GOSUB LIST.GL
		GOTO SUMJRNLS.1
		END IF
	 IF updwn% = 65 THEN
		GOSUB LIST.GST
		GOTO SUMJRNLS.1
		END IF


	 updwn% = 13
xsumjrnls:

	 RETURN
'/////////////////////////////////////////////////////////////////////////////
'>>>>>>
'/////////////////////////////////////////////////////////////////////////////
LIST.GL:
	CALL setup("LIST GL TOTALS")
	CALL prtbtm("F1-Exit")
	gln% = 0
	FOR i% = 1 TO 499
		IF gltot.p@(i%) <> 0 OR gltot.n@(i%) <> 0 THEN
			gln% = gln% + 1
			SELECT CASE gln%
			CASE 1 TO 20: glx1% = 2: glx2% = 22
			CASE 21 TO 40: glx1% = 42: glx2% = 62
			CASE ELSE: glx1% = 2: glx2% = 22
			END SELECT

			gly% = gly% + 1
			IF gln% = 1 THEN gly% = 3
			IF gln% = 21 THEN gly% = 3
			IF gln% = 41 THEN gly% = 3
			IF gln% = 61 THEN gly% = 3
			IF gln% = 81 THEN gly% = 3
			IF gln% = 101 THEN gly% = 3
			IF gln% = 121 THEN gly% = 3
			IF gln% = 141 THEN gly% = 3
			IF gln% = 161 THEN gly% = 3
			IF gln% > 160 THEN gly% = 3

			LOCATE gly%, glx1%
			COLOR 2, 0: PRINT USING "### ##,###,###.##"; i%; gltot.p@(i%);
			LOCATE gly%, glx2%
			COLOR 2, 0: PRINT USING "### ##,###,###.##"; i%; gltot.n@(i%);
			COLOR 7, 0: PRINT "³";
		END IF

	IF gln% = 80 THEN BEEP: X$ = INPUT$(1)
	IF gln% > 161 THEN BEEP: X$ = INPUT$(1)
	NEXT



	CALL inpnew(a$, 0!, updwn%, "13,59")
	IF updwn% = 13 THEN GOTO LIST.GL
RETURN
'/////////////////////////////////////////////////////////////////////////////
'>>>>>>
'/////////////////////////////////////////////////////////////////////////////
LIST.GST:
	CALL setup("LIST GST SUMMARY")
	CALL prtbtm("F1-Exit")
	gln% = 0
	LOCATE 3, 10
	COLOR 6, 0
	LOCATE , 25: PRINT " G.S.T SUMMARY"
	LOCATE , 25: PRINT "==============="
	COLOR 2, 0

	IF opt% = 5 THEN
	LOCATE , 24: PRINT "For date "; begdmy$; "      Code: "; supa$;
	ELSE
	LOCATE , 24: PRINT "Period "; beg$; "-"; end$; "      Code: "; supa$;
	END IF

	LOCATE 7
	LOCATE , 6: PRINT USING "!                            Total...        G.S.T...  (     Theory...)"; " "
	LOCATE , 6: PRINT USING "CI - Invoice Inc. GST  $$#,###,###.##- $$#,###,###.##- ($$#,###,###.##) "; tot.ci.incgst1@; tot.ci.incgst0@; tot.ci.incgst1@ / 11
	LOCATE , 6: PRINT USING "CI - Invoiced No GST   $$#,###,###.##- $$#,###,###.##- ($$#,###,###.##) "; tot.ci.nogst1@; tot.ci.nogst0@ / 11; 0
	LOCATE , 6: PRINT USING "CI - Invoice Part GST  $$#,###,###.##- $$#,###,###.##- ($$#,###,###.##) "; tot.ci.partgst1@; tot.ci.partgst0@; tot.ci.partgst1@ / 11
	LOCATE , 6: PRINT
	LOCATE , 6: PRINT USING "DI - Invoice Inc. GST  $$#,###,###.##- $$#,###,###.##- ($$#,###,###.##) "; tot.di.incgst1@; tot.di.incgst0@; tot.di.incgst1@ / 11
	LOCATE , 6: PRINT USING "DI - Invoiced No GST   $$#,###,###.##- $$#,###,###.##- ($$#,###,###.##) "; tot.di.nogst1@; tot.di.nogst0@ / 11; 0
	LOCATE , 6: PRINT USING "DI - Invoice Part GST  $$#,###,###.##- $$#,###,###.##- ($$#,###,###.##) "; tot.di.partgst1@; tot.di.partgst0@; tot.di.partgst1@ / 11


	CALL inpnew(a$, 0!, updwn%, "13,59")
	IF updwn% = 13 THEN GOTO LIST.GST
RETURN

'/////////////////////////////////////////////////////////////////////////////
'>>>>>  NON ACTIVE
'/////////////////////////////////////////////////////////////////////////////
LISTNONACTIVE:
	chw% = 43
	CALL sndmsg("Resetting customers to Inactive.")
	Rec% = 1
	GET #chw%, Rec%, sup
	DO WHILE NOT EOF(chw%)
		IF sup.active$ <> "I" THEN
			sup.active$ = "I"
			PUT #chw%, Rec%, sup
			END IF
		IF Rec% MOD 100 = 0 THEN CALL sndmsg("Record" + STR$(Rec%))
		IF INKEY$ = CHR$(0) + CHR$(59) THEN EXIT DO
		GET #chw%, , sup: Rec% = Rec% + 1
		LOOP

	chw% = 44
	CALL sndmsg("Resetting Suppliers to Inactive.")
	Rec% = 1
	GET #chw%, Rec%, sup
	DO WHILE NOT EOF(chw%)
		IF sup.active$ <> "I" THEN
			sup.active$ = "I"
			PUT #chw%, Rec%, sup
			END IF
		IF Rec% MOD 100 = 0 THEN CALL sndmsg("Record" + STR$(Rec%))
		IF INKEY$ = CHR$(0) + CHR$(59) THEN EXIT DO
		GET #chw%, , sup: Rec% = Rec% + 1
		LOOP
	CALL sndmsg("")

	 FOR i% = 1 TO naudit%
	 CLOSE #8
	 cashonly$ = "M": auditname$ = auditfile$(i%)
	 GOSUB OPEN.AUDIT


	 CALL search.month(Rec%, begyymd$)
	 IF opt% = 10 THEN Rec% = 1
	 IF Rec% < 0 THEN GOTO J.next.nonactive
	 GET #8, Rec%, audit
	 hld.addate$ = "  /  /  "
	'/////////////////   Now read forward           ////////////////////////
	 DO WHILE NOT EOF(8)
	 '.dc
	'dymd$ = "  /  /  "
	'MID$(dymd$, 1, 2) = MID$(FNDYY$(Audit.addate$), 7, 2)
	'MID$(dymd$, 4, 2) = MID$(FNDYY$(Audit.addate$), 4, 2)
	'MID$(dymd$, 7, 2) = MID$(FNDYY$(Audit.addate$), 1, 2)
	'IF dymd$ > end ymd$ AND Audit.adtype$ = "PE" THEN EXIT DO
	IF audit.aDdate > endyymd$ AND audit.adtype$ = "PE" THEN EXIT DO
	'///////////  Edit tranaction to see if it should be included  /////////
	ok% = -1
	IF supa$ <> "*" AND supa$ <> audit.adcust$ THEN ok% = 0
	'IF MID$(dymd$, 7, 2) < begday$ THEN ok% = 0 '.dc
	'IF MID$(dymd$, 7, 2) > endday$ THEN ok% = 0 '.dc
	'IF ok% AND dymd$ > end ymd$ THEN ok% = 0  'I wonder. '.dc
	IF audit.aDdate < begyymd$ THEN ok% = 0  '.dc
	IF opt% = 5 AND audit.aDdate <> begyymd$ THEN ok% = 0 '.dc

	IF NOT ok% THEN
	IF hld.addate$ <> FNDYY$(audit.aDdate$) THEN
		 COLOR 7: LOCATE 24, 26
		 PRINT USING "¹ Searching... \          \ Ì"; FNDYY$(audit.aDdate$);
		 hld.addate$ = audit.aDdate$
	END IF
	END IF



	IF ok% THEN

		 IF hld.addate$ <> FNDYY$(audit.aDdate$) THEN
			COLOR 7: LOCATE 24, 26
			PRINT USING "¹ Loading..... \          \ Ì"; FNDYY$(audit.aDdate$);
			hld.addate$ = audit.aDdate$
		 END IF

		 Value@ = audit.advalue
		 Value@ = Value@ * 100
		 Value@ = FIX(Value@) / 100
		 dp3@ = audit.advalue - Value@
		 IF Value@ > 0 AND dp3@ >= .005 THEN Value@ = Value@ + .01
		 IF Value@ < 0 AND dp3@ <= -.005 THEN Value@ = Value@ - .01
	'LOCATE 10, 10: PRINT Audit.adcust$
	'/////////////////  Search the index for strings  //////////////////////
	 IF MID$(audit.adtype$, 1, 1) = "D" THEN
		skey$ = audit.adcust$
		GOSUB searchindex.cus
		sno% = CVI(supx.wrrn$)
		chw% = 43'Channel of cus file
		IF sno% < 1 OR sno% > maxcus% THEN LSET audit.adcust$ = "AAAAA": sno% = 1
	 ELSE
		skey$ = audit.adcust$
		GOSUB searchindex.sup
		sno% = CVI(supx.wrrn$)
		chw% = 44       '***** Channel of sup file
		IF sno% < 1 OR sno% > maxsup% THEN LSET audit.adcust$ = "AAAAA": sno% = 1
		END IF

	 GET #chw%, sno%, sup
	'LOCATE 11, 10: PRINT sup.search$ + sup.stype$

	IF sno% <> 1 AND sup.active$ <> "A" THEN
		sup.active$ = "A" 'Active
		PUT #chw%, sno%, sup
		END IF

	END IF
	GET #8, , audit: Rec% = Rec% + 1
	LOOP

J.next.nonactive:
	NEXT

	 updwn% = 13
xnonactive:
	 RETURN

'/////////////////////////////////////////////////////////////////////////////
'>>>>>  B R O W S E   T H E   F I L E
'/////////////////////////////////////////////////////////////////////////////
browse:
	 CALL setup("BROWSE AUDIT FILE")
	 in$ = STR$(adlast% - 16)
	 GOTO 2580       '***** LIST FIRST PAGE
	'/////////////////  Get next record to browse from  ////////////////////
2540
	 LOCATE 2, 21: COLOR 7, 0: PRINT "ÍÍµ"; : LOCATE , 49: PRINT "ÆÍÍ": COLOR 2, 0
	 COLOR 2: LOCATE 2, 24: PRINT "Start browse from..>     ";
	 CALL prtbtm("F1-Exit    Esc - Update.     F2-Change Suplier    F10-Display.  " + CHR$(24) + CHR$(25) + "-Move")
	 COLOR 6, 0: LOCATE 3, 2
	 PRINT " No.    Date  Type Supplier/Customer...          Code. .. Document      Value."
	 COLOR 2, 0
	 updwn% = 0: in$ = "Y"
	 LOCATE 2, 44: updwn% = 1: in$ = MID$(STR$(ebrw%), 2)
	 CALL inpnew(in$, 205!, updwn%, "13,27,59,60,68,72,73,80,81" + ALT$): GOSUB ALT
	 IF updwn% = 59 THEN GOTO bret
	'/////////////////  F3 - Find                    ///////////////////////
	 IF updwn% = 27 THEN GOSUB find.doc: in$ = STR$(st.brw%)
	 IF updwn% = 60 THEN GOSUB globaL.update: in$ = STR$(st.brw%)
	 IF updwn% = 68 THEN GOSUB chgbrowse: in$ = STR$(st.brw%)
	 IF updwn% = 72 THEN in$ = STR$(st.brw% - 1)       '***** UP arrow
	 IF updwn% = 73 THEN in$ = STR$(st.brw% - paglen%)   '***** PGUP
	 IF updwn% = 80 THEN in$ = STR$(st.brw% + 1)       '***** DN arrow
	 IF updwn% = 81 THEN in$ = STR$(ebrw%)              '***** PGDN
	'/////////////////  L I S T   A   P A G E        ///////////////////////
2580 :
	 b = VAL(in$): IF b > 32000 THEN in$ = "32000"
	 b% = VAL(in$)
	 IF b% < 1 OR b% > 32000 THEN b% = 1
	 Rec% = b%
	 st.brw% = 0: n% = 0
	 GET #8, Rec%, audit
	 IF EOF(8) THEN GOTO 2540 '**** Get next record to browse from
	 LOCATE 4, 2
	 missed% = 0
	 DO
	'/////////////////  Convert fields to numeric    ///////////////////////
	adnxtpe% = CVI(MID$(audit.adsname$, 1, 2))
	adprepe% = CVI(MID$(audit.adsname$, 3, 2))
	adlstpe% = CVI(MID$(audit.adsname$, 5, 2))
	IF st.brw% = 0 THEN st.brw% = Rec%'* Set to first record on screen for return
	LOCATE , 2
	GOSUB dsply.rec
	n% = n% + 1
	GET #8, , audit: Rec% = Rec% + 1
	ebrw% = Rec%
	 LOOP WHILE n% < paglen% AND NOT EOF(8)
	 FOR Rec% = n% + 1 TO paglen%: LOCATE , 2: PRINT CHR$(FNE): NEXT
	 GOTO 2540 '**** Get next record to browse from
bret:
	 updwn% = 13
RETURN
'/////////////////////////////////////////////////////////////////////////////
'/////////////////  find a document number       ///////////////////////
'/////////////////////////////////////////////////////////////////////////////
find.doc:
	 first.found% = 0
	 last.found% = 0
	 COLOR 15, 10
	 LOCATE 24, 1: PRINT SPACE$(80);
	 LOCATE 25, 1: PRINT SPACE$(80);
	 LOCATE 24, 1: PRINT "  F1)Exit......  F2)$ Value..  F3)Document....  F4)Sup/Cust..   F5) G/L Accnt.";
	 LOCATE 25, 1: PRINT "  F6)G.S.T <>10% F7)Doc/Date.  F8)History Pmt.  F9)Doc/Text..  F10) ..........";
	 COLOR 2, 0
	 n% = 0
	 old.updwn% = 0
find.get:
	 LOCATE 2, 21: COLOR 7, 0: PRINT "ÍÍµ"; : LOCATE , 58: PRINT "ÆÍÍ": COLOR 2, 0
	 LOCATE 2, 24: PRINT "Enter search key...>              ";
	 LOCATE 2, 44
	 CALL inpnew(find$, 114!, updwn%, "13,59-64,65-68,80" + ALT$): GOSUB ALT
	 IF updwn% = 27 THEN GOTO x.find.doc
	 IF updwn% = 66 THEN
				cust$ = LEFT$(find$, 5)
				docnum$ = "": Value! = 0
				CALL load.unpaid(cust$, startrec%, docnum$, Value!, updwn%)
				'IF updwn% = 59 THEN GOTO x.find.doc
				GOTO find.doc
	 END IF
	 IF updwn% = 64 THEN
		 LOCATE 3, 45: PRINT "Calculated     G.S.T   "
	 END IF

	 IF updwn% = 68 THEN GOSUB chgbrowse: in$ = STR$(st.brw%): GOTO find.get
	 IF updwn% = 59 THEN GOTO x.find.doc

	'///////////////// Hit (CR) to continue search   ///////////////////////
	newsearch% = -1
	 IF updwn% = 13 AND last.found% > 0 THEN
		updwn% = old.updwn%: Rec% = last.found%'(CR) More
		last.found% = 0: first.found% = 0
		IF old.updwn% = 0 THEN GOTO find.get
		newsearch% = 0
	 END IF
	 IF updwn% = 80 AND first.found% > 0 THEN  '\/
		updwn% = old.updwn%: Rec% = first.found% + 1'(CR) More
		last.found% = 0: first.found% = 0
		IF old.updwn% = 0 THEN GOTO find.get
		newsearch% = 0
	 END IF

	'///////////////// Hit (CR) to continue search   ///////////////////////
	IF newsearch% THEN
		Rec% = 1
		a$ = STR$(Rec%)
		COLOR 2: LOCATE 2, 24: PRINT "Start period end...>    "; : COLOR 7: PRINT "ÆÍÍÍÍÍÍÍÍÍÍ"; : COLOR 2
		LOCATE 2, 44
		CALL inpnew(beg$, 104!, updwn1%, "13,59" + ALT$): GOSUB ALT
		IF updwn1% = 59 THEN GOTO find.get
		'.dc
		 begyymd$ = "yyyymm01"
		 MID$(begyymd$, 3, 2) = MID$(beg$, 3, 2)
		 MID$(begyymd$, 5, 2) = MID$(beg$, 1, 2)
		 IF MID$(begyymd$, 3, 2) > "73" THEN
			MID$(begyymd$, 1, 2) = "19"
		 ELSE
			MID$(begyymd$, 1, 2) = "20"
		 END IF
		 endyymd$ = "yyyymm99"
		 MID$(endyymd$, 3, 2) = MID$(end$, 3, 2)
		 MID$(endyymd$, 5, 2) = MID$(end$, 1, 2)
		 IF MID$(endyymd$, 3, 2) > "73" THEN
			MID$(endyymd$, 1, 2) = "19"
		 ELSE
			MID$(endyymd$, 1, 2) = "20"
		 END IF
		 '.dc

		CALL search.month(Rec%, begyymd$)
		Rec% = Rec%
	END IF

	'-----------------------------------------------------------------------
	 old.updwn% = updwn%
	 find$ = UCASE$(find$)
	 LOCATE 4, 2
	 lin% = 0
	 IF Rec% < 1 THEN Rec% = 1
	 st.brw% = 0
	 GET #8, Rec%, audit
	 DO WHILE NOT EOF(8)
	SELECT CASE updwn%
		CASE 13: EXIT DO  'Enter should not get to here
		 CASE 60 '**** Dollar value F2
			find@ = ABS(VAL(find$))
			'VALUE@
			ok% = 0
			IF (find$ <> "RED" AND ABS(find@ - ABS(audit.advalue)) < .005) THEN ok% = -1
			IF (find$ = "RED" AND ABS(audit.advalue) < 1.01 AND audit.adtype$ <> "PE") THEN ok% = -1
			IF ok% THEN
			 GOSUB dsply.rec
			 n% = n% + 1: lin% = lin% + 1
			 IF n% = 1 THEN first.found% = Rec%
			 IF first.found% = 0 THEN first.found% = Rec%
			 last.found% = Rec%
			END IF
		 CASE 61 '**** Document scan F3
			find2$ = audit.adtype$ + audit.addocnum$
			IF INSTR(find2$, find$) > 0 THEN
		 GOSUB dsply.rec
		 n% = n% + 1: lin% = lin% + 1
		 IF n% = 1 THEN first.found% = Rec%
		 IF first.found% = 0 THEN first.found% = Rec%
		 last.found% = Rec%
			END IF
		 CASE 62 '**** Supplier/Cust F4
			find2$ = audit.adtype$ + audit.adcust$
			IF INSTR(find2$, find$) > 0 THEN
		 GOSUB dsply.rec
		 n% = n% + 1: lin% = lin% + 1
		 IF n% = 1 THEN first.found% = Rec%
		 IF first.found% = 0 THEN first.found% = Rec%
		 last.found% = Rec%
			END IF
		 CASE 63 '**** G/L  F5
			'find2$ = Audit.adtype$ + STR$(Audit.adglacc!)
			find2$ = LTRIM$(STR$(audit.adglacc!))
			IF VAL(find2$) = VAL(find$) THEN
			GOSUB dsply.rec
			n% = n% + 1: lin% = lin% + 1
			IF n% = 1 THEN first.found% = Rec%
			 IF first.found% = 0 THEN first.found% = Rec%
			last.found% = Rec%
			END IF
		 CASE 64 '**** Tax value F6
		 IF INSTR("DI,DC,DP,DD,DT,DJ,PT,CI,CC,CP,CD,CT,CJ,CT,", find$ + ",") > 0 THEN
		find$ = "<>10%" + find$
		 END IF

		IF find$ = "" THEN find$ = "<>10%"
		IF find$ = "DI" THEN find$ = "<>10%DI"
		sel% = 0
		SELECT CASE MID$(find$, 1, 1)
		CASE "<":
			IF MID$(find$, 1, 2) = "<>" THEN
				perc$ = ""
				FOR i = 3 TO LEN(find$)
				IF MID$(find$, i, 1) >= "0" AND MID$(find$, i, 1) <= "9" THEN perc$ = perc$ + MID$(find$, i, 1)
				NEXT
				backperc = (100 + VAL(perc$)) / 10
				CALL ROUND(backperc, 2.5)
				tmp = audit.advalue / backperc  'i.e 11
				CALL ROUND(tmp, 2.5)
				IF audit.adtax <> tmp AND audit.adtax <> 0 THEN sel% = -1
				IF INSTR("DI,DC,DP,DD,DT,DJ,PT,CI,CC,CP,CD,CT,CJ,CT,", RIGHT$(find$, 2) + ",") > 0 THEN
					IF audit.adtype <> RIGHT$(find$, 2) THEN sel% = 0
				END IF

			 ELSE
				IF audit.adtax < VAL(MID$(find$, 2)) THEN sel% = -1
			 END IF

		CASE ">": IF audit.adtax > VAL(MID$(find$, 2)) THEN sel% = -1
		CASE "=": IF audit.adtax = VAL(MID$(find$, 2)) THEN sel% = -1
		CASE ELSE: IF audit.adtax = VAL(find$) THEN sel% = -1
		END SELECT
		IF INSTR(find$, ":") > 0 THEN 'eg 25.00-50.00
			sel% = 0
			X = INSTR(find$, ":")
			lowval = VAL(MID$(find$, 1, X - 1))
			highval = VAL(MID$(find$, X + 1))
			IF audit.adtax >= lowval AND audit.adtax <= highval THEN sel% = -1
		END IF


		IF sel% THEN
			 GOSUB dsply.rec
			 n% = n% + 1: lin% = lin% + 1
			 IF n% = 1 THEN first.found% = Rec%
			IF first.found% = 0 THEN first.found% = Rec%
			last.found% = Rec%
		END IF

		 CASE 65 '**** Document date F7
			find2$ = audit.adtype$ + FNDYY$(audit.aDdate$)
			IF INSTR(find2$, find$) > 0 THEN
		 GOSUB dsply.rec
		 n% = n% + 1: lin% = lin% + 1
		 IF n% = 1 THEN first.found% = Rec%
		 IF first.found% = 0 THEN first.found% = Rec%
		 last.found% = Rec%
			END IF
		 CASE 67 '**** Document scan extended F3
			find2$ = audit.adtype$ + audit.addocnum$ + audit.adtext$
			IF INSTR(find2$, find$) > 0 THEN
		 GOSUB dsply.rec
		 n% = n% + 1: lin% = lin% + 1
		 IF n% = 1 THEN first.found% = Rec%
		 IF first.found% = 0 THEN first.found% = Rec%
		 last.found% = Rec%
			END IF
		 CASE 68
		 CASE ELSE
		 END SELECT
	'/////////////////   Test for F1 as a hot key     //////////////////////
	hot.key.exit% = 0
	hot.key% = hot.key% + 1
	IF hot.key% > 100 THEN
		 X$ = RIGHT$("0" + INKEY$, 1)
		 IF X$ = CHR$(59) THEN hot.key.exit% = -1: EXIT DO
		 hot.key% = 0
	END IF
	IF lin% > 17 THEN EXIT DO
	GET #8, , audit: Rec% = Rec% + 1
	 LOOP
	 IF hot.key.exit% = -1 THEN
	LSET audit.adtype$ = "hk"
	GOSUB dsply.rec
	lin% = lin% + 1
	 END IF
'TESTING
	 IF EOF(8) THEN SOUND 100, 1
	 FOR Rec% = lin% + 1 TO 19: LOCATE , 2: PRINT CHR$(FNE): NEXT
	 GOTO find.get


x.find.doc:     '>>>>>  Reset the screen
	 CALL setup("BROWSE AUDIT FILE")
	 CALL prtbtm("F1-Exit")
	 COLOR 2, 0
	 RETURN
'/////////////////////////////////////////////////////////////////////////////
'>>>>>  DISPLAY A FOUND RECORD
'/////////////////////////////////////////////////////////////////////////////
dsply.rec:
	'*****  Convert fields to numeric
	 adnxtpe% = CVI(MID$(audit.adsname$, 1, 2))
	 adprepe% = CVI(MID$(audit.adsname$, 3, 2))
	 adlstpe% = CVI(MID$(audit.adsname$, 5, 2))
	 IF st.brw% = 0 THEN st.brw% = Rec%'* Set to first record on screen for return

	 Y0% = CSRLIN
	 LOCATE , 2: COLOR 2, 0
	 SELECT CASE audit.adtype$
	CASE "PE"
		 COLOR 5
		 PRINT USING "##### & \\ ==================== Next#####      Prev#####      Last#####"; audit.adrec%; FNDYY$(audit.aDdate$); audit.adtype$; adnxtpe%; adprepe%; adlstpe%
	CASE "PT"
		 COLOR 9
		 PRINT USING "##### & \\     &              !&     "; audit.adrec%; FNDYY$(audit.aDdate$); audit.adtype$; audit.addocnum$; audit.adpaid$; audit.adtext$;
		 PRINT USING "$$###,###.##"; audit.advalue
	CASE "hk"
		 COLOR 14
		 PRINT "Not a complete list. Search aborted by F1 Key.                        "
	CASE ELSE
		 COLOR 2: IF LEFT$(audit.adtype$, 1) = "C" THEN COLOR 3
		 PRINT USING "##### & \\ &-&    &"; audit.adrec%; FNDYY$(audit.aDdate$); audit.adtype$; audit.adsname$; audit.adcust$; audit.addocnum$;
		IF ABS(audit.advalue) < 1.01 THEN COLOR 4
		PRINT USING "$$###,###.##"; audit.advalue


		'>> Overprint color parts
		IF audit.adtype$ = "DI" OR audit.adtype$ = "DC" OR audit.adtype$ = "DP" THEN
		COLOR 7: LOCATE Y0%, 57: PRINT USING "!"; paidsts$(audit.adpaid$, "L"): COLOR 2
		END IF



		 IF audit.adtax! <> 0 THEN tfortax$ = "T" ELSE tfortax$ = " "
		 COLOR 4
		 LOCATE Y0%, 58
		 PRINT USING "!"; tfortax$
		 COLOR 2

		 IF updwn% = 64 THEN   'GST Search
			 LOCATE Y0%, 54
			 IF ABS(audit.adtax!) < .01 THEN COLOR 4
			 IF audit.adtax <> audit.advalue / 11 THEN COLOR 13
			 PRINT USING "$$###,###.##"; audit.adtax!

			 IF updwn% = 64 AND audit.adtax <> audit.advalue / 11 THEN
				 LOCATE Y0%, 42
				 PRINT USING "$$###,###.##"; audit.advalue / 11
			 END IF

			 END IF


	 END SELECT
	 RETURN
'/////////////////////////////////////////////////////////////////////////////
'>>>>>  C H A N G E   I N   B R O W S E
'/////////////////////////////////////////////////////////////////////////////
chgbrowse:
	 IF st.brw% < 1 OR st.brw% > 32000 THEN RETURN
	 GET #8, st.brw%, audit
	 org.advaluE = audit.advalue
	 GOSUB dsply.box
	 CALL inpnew(in$, 0!, updwn%, "13,59,61,68" + ALT$): GOSUB ALT
	 IF updwn% = 59 THEN GOTO x.chg.browse
	 IF updwn% = 61 THEN
				GOSUB Rec.insert
				GET #8, st.brw%, audit
				org.advaluE = audit.advalue
				GOSUB dsply.box
				END IF
	 IF updwn% = 13 THEN GOTO x.chg.browse
	'-----------------------------------------------------------------------
	'/////  Begin the change sequence                                  /////
	'/////  Back out the old record off the customer file              /////
	'/////  the allow the keying of the new details                    /////
	'-----------------------------------------------------------------------
	 skey$ = "     ": LSET skey$ = audit.adcust$
	'>>> Set DB.OR.CR from the file
	 LSET temp1$ = audit.adtype$
	 IF temp1$ = "D" THEN DB.OR.CR$ = "DB" ELSE DB.OR.CR$ = "CR"
	'/////////////////  Search the index for strings  //////////////////////
	 IF MID$(audit.adtype$, 1, 1) = "D" THEN
		GOSUB searchindex.cus
		sno% = CVI(supx.wrrn$)
		chw% = 43'Channel of cus file
		IF sno% < 1 OR sno% > maxcus% THEN LSET audit.adcust$ = "AAAAA": sno% = 1
	 ELSE
		GOSUB searchindex.sup
		sno% = CVI(supx.wrrn$)
		chw% = 44       '***** Channel of sup file
		IF sno% < 1 OR sno% > maxsup% THEN LSET audit.adcust$ = "AAAAA": sno% = 1
		END IF

	 GET #chw%, sno%, sup
	'/////////////////  Clear for before/after image  //////////////////////
	 LOCATE 20, 2: PRINT STRING$(78, "=")
	 LOCATE 21, 2: PRINT STRING$(78, " ")
	 LOCATE 22, 2: PRINT STRING$(78, " ")
	 IF MID$(audit.adtype$, 1, 1) = "D" THEN
	LOCATE 21, 3: PRINT USING "Before (DB):### \   \:"; sno%; sup.search$ + sup.stype$;
	PRINT USING "######.##"; CVS(sup.scur$); CVS(sup.s30$); CVS(sup.s60$); CVS(sup.s90$) '; CVS(S120$); CVS(S150$)
	 ELSE
	LOCATE 21, 3: PRINT USING "Before (CR):### \   \:"; sno%; sup.search$ + sup.stype$;
	PRINT USING "######.##"; CVS(sup.scur$); CVS(sup.s30$); CVS(sup.s60$); CVS(sup.s90$) '; CVS(S120$); CVS(S150$)
	 END IF
	'/////////////////  BACK OUT THE OLD AUDIT RECORD //////////////////////
	 cha% = 8
	 upd.audit% = st.brw%
	 audit.advalue = 0 - audit.advalue
	 sav.advalue@ = audit.advalue
	 CALL upd.who(cha%, chw%, upd.audit%)
	 audit.advalue = sav.advalue@
	'/////////////////  Convert fields to numeric     //////////////////////
	 GOTO cf5
cf0: '/////////////////  Record Creation Date          //////////////////////
	 LOCATE Y% + 1, X% + 19
	 in$ = audit.aDdate$ '.dc
	 CALL inpnew(in$, 108!, updwn%, "13,59,60")
	 in$ = UCASE$(in$)
	 IF updwn% = 59 THEN GOTO chg.upd.xit
	 IF updwn% = 60 THEN GOTO cf1
	 LSET audit.aDdate$ = in$ '.dc
cf1: '/////////////////  Entry Type                    //////////////////////
	 LOCATE Y% + 2, X% + 19
	 in$ = audit.adtype$
	'**** Only accept a type entry if the original value is 0
	 IF org.advaluE = 0 THEN
	CALL inpnew(in$, 102!, updwn%, "13,59,60")
	 ELSE
	CALL inpnew(in$, 102!, updwn%, "13,59,60")
	 END IF
	 in$ = UCASE$(in$)
	 IF updwn% = 59 THEN GOTO chg.upd.xit
	 IF updwn% = 60 THEN GOTO cf0
	 LSET audit.adtype$ = in$
	 IF audit.adtype$ = "PE" THEN GOTO cf3
	 IF audit.adtype$ = "PT" THEN GOTO cf3
cf2: '/////////////////  G/L NUMBER                    //////////////////////
	 LOCATE Y% + 3, X% + 19
	 in$ = STR$(audit.adglacc!)
	 CALL inpnew(in$, 3!, updwn%, "13,59,60")
	 IF updwn% = 59 THEN GOTO chg.upd.xit
	 IF updwn% = 60 THEN GOTO cf1
	 audit.adglacc! = VAL(in$)
	 GOTO cf5'Skip Supplier
cf3: '/////////////////  SUPPLIER                      //////////////////////
	 LOCATE Y% + 4, X% + 19: PRINT "      "
	 LOCATE Y% + 4, X% + 19
	 in$ = audit.adcust$
	 CALL inpnew(in$, 105!, updwn%, "13,59,60")
	 in$ = UCASE$(in$)
	 LSET audit.adcust$ = in$
	 IF updwn% = 59 THEN GOTO chg.upd.xit
	 IF updwn% = 60 THEN GOTO cf2
	 skey$ = "     ": LSET skey$ = audit.adcust$
	 IF MID$(audit.adtype$, 1, 1) = "D" THEN 'DI,DP,DD etc.
	GOSUB searchindex.cus
	sno% = CVI(supx.wrrn$)
	chw% = 43'Channel of cus file
	IF sno% < 1 OR sno% > maxcus% THEN LSET audit.adcust$ = "AAAAA": sno% = 1
	 ELSE
	GOSUB searchindex.sup
	sno% = CVI(supx.wrrn$)
	chw% = 44'Channel of sup file
	IF sno% < 1 OR sno% > maxsup% THEN LSET audit.adcust$ = "AAAAA": sno% = 1
	 END IF
	 IF MID$(audit.adtype$, 1, 1) = "D" THEN
	chw% = 43'Channel of CUS file
	GET #chw%, sno%, sup
	LSET audit.adcust$ = sup.search$ + sup.stype$
	LSET audit.adsname$ = sup.sname$
	audit.adglacc! = CVS(sup.sgl$)
	GOSUB dsply.box
	 ELSE
	chw% = 44'Channel of sup file
	GET #chw%, sno%, sup
	LSET audit.adcust$ = sup.search$ + sup.stype$
	LSET audit.adsname$ = sup.sname$
	audit.adglacc! = CVS(sup.sgl$)
	GOSUB dsply.box
	 END IF
cf5: '/////////////////  DOC NUMBER                    //////////////////////
	 LOCATE Y% + 7, X% + 19
	 in$ = audit.addocnum$
	 CALL inpnew(in$, 112!, updwn%, "13,59,60")
	 IF updwn% = 59 THEN GOTO chg.upd.xit
	 IF updwn% = 60 THEN GOTO cf3
	 LSET audit.addocnum$ = in$
cf6: '/////////////////  DOC VALUE                     //////////////////////
	 LOCATE Y% + 8, X% + 19: PRINT "            ";
	 LOCATE Y% + 8, X% + 18
	 in$ = STR$(audit.advalue)
	 cents$ = in$ + "00"
	 cx% = INSTR(cents$, ".")
	 IF cx% > 0 THEN cents$ = MID$(cents$, cx% + 1, 2)
				 CALL inpnew(in$, -8.2, updwn%, "13,59,60")
	 IF updwn% = 59 THEN GOTO chg.upd.xit
	 IF updwn% = 60 THEN GOTO cf5
	 audit.advalue = VAL(in$)
	 LOCATE Y% + 8, X% + 17: PRINT USING "$$###,###.##  "; audit.advalue
	 GOTO cf9
cf7: '/////////////////  DOC tax                      //////////////////////
	'IF MID$(Audit.adtype$, 1, 1) = "C" THEN GOTO cf6
	 LOCATE Y% + 9, X% + 19: PRINT "            ";
	 LOCATE Y% + 9, X% + 19
	 in$ = STR$(audit.adtax!)
	 IF INSTR("DI,DC,DJ,CI,CC,CJ", audit.adtype) > 0 THEN
								CALL inpnew(in$, -7.2, updwn%, "13,59,60")
	 ELSE
		in$ = "0.0"
	 END IF
	 IF updwn% = 59 THEN GOTO chg.upd.xit
	 IF updwn% = 60 THEN GOTO cf6
	 audit.adtax! = VAL(in$)
	 CALL ROUND(audit.adtax!, 2.5)
	 LOCATE Y% + 9, X% + 17: PRINT USING "$$###,###.##  "; audit.adtax!
cf8: '/////////////////  DOC tax                      //////////////////////
	 LOCATE Y% + 10, X% + 19
	 in$ = audit.adpaid$
	 CALL inpnew(in$, 101!, updwn%, "13,59,60")
	 IF updwn% = 59 THEN GOTO chg.upd.xit
	 IF updwn% = 60 THEN GOTO cf7
	 LSET audit.adpaid$ = in$
	 LOCATE Y% + 10, X% + 19: PRINT USING "! - &"; audit.adpaid$; paidsts$(audit.adpaid$, "L")
cf9: '/////////////////  DOC TEXT                      //////////////////////
	 LOCATE Y% + 11, X% + 19
	 in$ = audit.adtext$
	 CALL inpnew(in$, 116!, updwn%, "13,59,60")
	 IF updwn% = 59 THEN GOTO chg.upd.xit
	 IF updwn% = 60 THEN GOTO cf8
	 LSET audit.adtext$ = in$
chg.upd.xit:
	'/////////////////  A C T U A L    U P D A T E    //////////////////////
	 IF audit.adtype$ = "PE" THEN
		LSET audit.adsname$ = "Period end"
		LSET audit.adcust$ = SPACE$(99)
		audit.advalue = 0
		audit.adglacc! = 0
		LSET audit.adtext$ = STRING$(99, "*")
		PUT #8, st.brw%, audit
		GOTO x.chg.browse
		END IF

	 IF audit.adtype$ = "PT" THEN
		LSET audit.adtext$ = "Payment total"
		LSET audit.adsname$ = SPACE$(99)
		LSET audit.adcust$ = SPACE$(99)
		audit.adglacc! = 0
		PUT #8, st.brw%, audit
		GOTO x.chg.browse
		END IF

	 PUT #8, st.brw%, audit
	 cha% = 8
	 upd.audit% = st.brw%
	 CALL upd.who(cha%, chw%, upd.audit%)
	'-----------------------------------------------------------------------
	 IF MID$(audit.adtype$, 1, 1) = "D" THEN
	LOCATE 22, 3: PRINT USING "After      :### \   \:"; sno%; sup.search$ + sup.stype$;
	PRINT USING "######.##"; CVS(sup.scur$); CVS(sup.s30$); CVS(sup.s60$); CVS(sup.s90$) '; CVS(S120$); CVS(S150$)
	 ELSE
	LOCATE 22, 3: PRINT USING "After      :### \   \:"; sno%; sup.search$ + sup.stype$;
	PRINT USING "######.##"; CVS(sup.scur$); CVS(sup.s30$); CVS(sup.s60$); CVS(sup.s90$)'; CVS(S120$); CVS(S150$)
	 END IF
	 'x$ = INPUT$(1)
x.chg.browse:
	 RETURN
dsply.box:      '>>>>>  D I S P L A Y   C H A N G E   B O X
	'/////////////////  Convert fields to numeric     //////////////////////
	 X% = 17: Y% = 6
	 CALL BOX(15, 5, 66, 18, 14, 0, 1)
	 COLOR 7, 0
	 tmp = audit.advalue / 11
	 CALL ROUND(tmp, 2.5)
	 LOCATE Y%, X%
	 LOCATE , X%: PRINT USING "Record..........>  ##,### !"; audit.adrec%; audit.adactive$
	 LOCATE , X%: PRINT USING "Record date.....>  &"; FNDYY$(audit.aDdate$)
	 LOCATE , X%: PRINT USING "Entry Type......>  \\"; audit.adtype$
	 LOCATE , X%: PRINT USING "G/L Number......>  ###"; audit.adglacc!
	 LOCATE , X%: PRINT USING "Supplier........>  &"; audit.adcust$
	 LOCATE , X%: PRINT USING "                   &"; audit.adsname$
	 LOCATE , X%: PRINT USING "&"; " "
	 LOCATE , X%: PRINT USING "Document No.....>  &"; audit.addocnum$
	 LOCATE , X%: PRINT USING "Value...........>  $$###,###.##  "; audit.advalue
	 LOCATE , X%: PRINT USING "G.S.T...........>  $$###,###.### $$###,###.###"; audit.adtax!; tmp!
	 LOCATE , X%: PRINT USING "Paid status.....>  ! - &"; audit.adpaid$; paidsts$(audit.adpaid$, "L")
	 LOCATE , X%: PRINT USING "Associated text.>  &"; audit.adtext$
	 RETURN
'////////////////////////////////////////////////////////////////////////////
'>>>>>  I N S E R T   A   R E C O R D
'////////////////////////////////////////////////////////////////////////////
Rec.insert:
	 add% = 0: IF st.brw% < adlast% THEN add% = 1
	 st.brw% = st.brw% + add%
	 FOR Rec% = adlast% TO st.brw% STEP -1
		GET #8, Rec%, audit
		audit.adrec% = Rec% + 1
		PUT #8, Rec% + 1, audit
		NEXT
	 CALL BOX(2, 5, 79, 21, 0, 0, 0)
	 GET #8, st.brw% - add%, audit
	 audit.adrec% = st.brw%
	 audit.advalue = 0
	 LSET audit.addocnum$ = "***"
	 PUT #8, st.brw%, audit
	 adlast% = LOF(8) / 92
	 RETURN
'//////////////////////////////////////////////////////////////////////////
'>>>>> Lookup index file. Passed skey$. Returns SKEY, 0 if not found. <<<<<
'>>>>> SKEY1, one after insertion place                               <<<<<
'//////////////////////////////////////////////////////////////////////////
searchindex.cus:
	 skey = 0: skey1 = 0: found% = 0
	 IF skey$ = "     " THEN skey1 = 0: RETURN
	 s% = 0: e% = maxcus%
searchagain.cus:
	 p% = (e% - s%) / 2 + s%
	 IF p% = 0 THEN skey = 0: skey1 = s%: RETURN
	 GET #23, p%, supx
	 IF CVI(supx.wrrn$) = 0 THEN LSET supx.wcde$ = STRING$(99, CHR$(255))
	 IF supx.wcde$ + wtyp$ = skey$ THEN skey = p%: skey1 = p%: found% = -1: RETURN
	 IF e% - s% = 1 THEN skey = 0: skey1 = s%: RETURN
	 IF supx.wcde$ + wtyp$ < skey$ THEN s% = p%: GOTO searchagain.cus
	 IF supx.wcde$ + wtyp$ > skey$ THEN e% = p%: GOTO searchagain.cus
	 RETURN
'//////////////////////////////////////////////////////////////////////////
'>>>>> Lookup index file. Passed skey$. Returns SKEY, 0 if not found. <<<<<
'>>>>> SKEY1, one after insertion place                               <<<<<
'//////////////////////////////////////////////////////////////////////////
searchindex.sup:
	 skey = 0: skey1 = 0: found% = 0
	 IF skey$ = "     " THEN skey1 = 0: RETURN
	 s% = 0: e% = maxcus%
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
'/////////////////////////////////////////////////////////////////////////////
'>>>>>  DISPLAY A FOUND RECORD
'/////////////////////////////////////////////////////////////////////////////
globaL.update:
	 CALL setup("GLOBAL CHANGE")
	 CALL BOX(21, 9, 56, 13, 14, 0, 1)
	 COLOR 7, 0
	 LOCATE 10, X - 5: PRINT "Enter from Supplier.>"; fromsup$
	 LOCATE , X - 5:   PRINT "        to Supplier.>"; tosup$
gcf1:
	LOCATE 10, X + 16: CALL inpnew(fromsup$, 105!, updwn%, "13,59-60" + ALT$): GOSUB ALT
	fromsup$ = UCASE$(fromsup$)
	IF updwn% = 59 THEN GOTO xglobal.update
	IF updwn% = 60 THEN GOTO gcf1

gcf2:
	LOCATE 11, X + 16: CALL inpnew(tosup$, 105!, updwn%, "13,59-60" + ALT$): GOSUB ALT
	tosup$ = UCASE$(tosup$)
	IF updwn% = 59 THEN GOTO xglobal.update
	IF updwn% = 60 THEN GOTO gcf1

gcf3:
	a$ = "N"
	LOCATE 12, X - 5:   PRINT "       Are you sure.>"; a$
	LOCATE 12, X + 16: CALL inpnew(a$, 101!, updwn%, "13,59-60" + ALT$): GOSUB ALT
	LOCATE 12, X - 5:   PRINT "                       "
	IF updwn% = 59 THEN GOTO xglobal.update
	IF updwn% = 60 THEN GOTO gcf1
	a$ = UCASE$(a$)
	IF a$ <> "Y" THEN GOTO gcf1

	Rec% = 1
	GET #8, Rec%, audit
	DO WHILE NOT EOF(8)
		IF audit.adcust$ = fromsup$ THEN
			audit.adcust$ = tosup$
			PUT #8, Rec%, audit: SOUND 20000, 1
			END IF


		IF Rec% MOD 100 = 0 THEN LOCATE 21, 35: PRINT USING "##,###"; Rec%
		GET #8, , audit: Rec% = Rec% + 1
		LOOP


xglobal.update:
RETURN

SUB load.unpaid (cust$, startrec%, docnum$, Value!, updwn%) STATIC
'$INCLUDE: '\tpmanuf\src\dsunpaid.bi'
END SUB

FUNCTION MYOB$

	ret$ = ""
	FOR i% = 1 TO 53
		ths$ = ""
		SELECT CASE i%
			CASE 1: ths$ = RTRIM$(sup.sname$)
			CASE 2: ' "First Name"
			CASE 3: ' "Addr 1 - Line 1"
			CASE 4: ' "       - Line 2"
			CASE 5: ' "       - Line 3"
			CASE 6: ' "       - Line 4"
			CASE 7: ths$ = "X"' "Inclusive"
			CASE 8: ths$ = RTRIM$(audit.addocnum$) ' "Invoice #"
			CASE 9: ths$ = FNDYY$(audit.aDdate$)' "Date"
			CASE 10:          ' "Customer PO"
			CASE 11:          ' "Ship Via"
			CASE 12: ths$ = "P"' "Delivery Status"
			CASE 13: ths$ = audit.adtype$' "Description"
			CASE 14: ths$ = "41000"  '42000' "Account #"
			CASE 15: ths$ = STR$(audit.advalue - audit.adtax)' "Amount"
			CASE 16: ths$ = STR$(audit.advalue)' "Inc-Tax Amount"
			CASE 17: ' "Job"
			CASE 18: ths$ = audit.adtext$' "Comment"
			CASE 19: ' "Journal Memo"
			CASE 20: ' "Salesperson Last Name"
			CASE 21: ' "Salesperson First Name"
			CASE 22: ' "Shipping Date"
			CASE 23: ' "Referral Source"
			CASE 24: ths$ = "GST"' "Tax Code"
			CASE 25: ' "Non-GST Amount"
			CASE 26: ths$ = STR$(audit.adtax)' "GST Amount"
			CASE 27: ' "LCT Amount"
			CASE 28: ' "Freight Amount"
			CASE 29: ' "Inc-Tax Freight Amount"
			CASE 30: ths$ = "GST"   ' "Freight Tax Code"
			CASE 31: ' "Freight Non-GST Amount"
			CASE 32: ' "Freight GST Amount"
			CASE 33: ' "Freight LCT Amount"
			CASE 34: ' "Sale Status"
			CASE 35: ' "Currency Code"
			CASE 36: ' "Exchange Rate"
			CASE 37: ths$ = "5"' "Terms - Payment is Due"
			CASE 38: ths$ = "1"' "      - Discount Days"
			CASE 39: ths$ = "30"' "      - Balance Due Days"
			CASE 40: ths$ = "0"' "      - % Discount"
			CASE 41: ths$ = "0"' "      - % Monthly Charge"
			CASE 42: ' "Amount Paid"
			CASE 43: ' "Payment Method"
			CASE 44: ' "Payment Notes"
			CASE 45: ' "Name on Card"
			CASE 46: ths$ = "00004220404"' "Card Number"
			CASE 47: ' "Expiry Date"
			CASE 48: ' "Authorisation Code"
			CASE 49: ' "BSB"
			CASE 50: ' "Account Number"
			CASE 51: ' "Drawer/Account Name"
			CASE 52: ' "Cheque Number"
			CASE 53: ' "Category"

			CASE ELSE
			ths$ = STR$(i%)
		END SELECT
		IF ret$ > "" THEN ret$ = ret$ + ","
		ret$ = ret$ + ths$

	NEXT


MYOB$ = ret$
END FUNCTION

FUNCTION paidsts$ (X$, set$) STATIC
			d$ = "           "
SELECT CASE X$
CASE "U": DD$ = "Unpaid"
CASE "P": DD$ = "Paid"
CASE "I": DD$ = "Instalment"
CASE "A": DD$ = "Allocated"
CASE "Q": DD$ = "Query"
CASE "M": DD$ = "Posted MYOB"
CASE ELSE: DD$ = "Unpaid."
END SELECT

IF audit.adtype$ = "DD" THEN DD$ = "Discount"
IF audit.adtype$ = "PT" THEN DD$ = "Total"
IF set$ = "L" THEN LSET d$ = DD$
IF set$ = "R" THEN RSET d$ = DD$

paidsts$ = d$
END FUNCTION

SUB rebldpe (ok%)
'$INCLUDE: '\tpmanuf\src\rebldpe.bi'
END SUB

SUB search.month (Rec%, begyymd$) STATIC
'/////////////////////////////////////////////////////////////////////////////
'//////////  SEARCH THE MONTH BY SKIPPING OVER "pe" RECORDS  ///////////
'/////////////////////////////////////////////////////////////////////////////
'.dc
search.month:
	 adlast% = LOF(8) / 92
	 Rec% = 1
	 GET #8, Rec%, audit
	 ' dymd$ = "  /  /  "
	 'MID$(dymd$, 1, 2) = MID$(FNDYY$(Audit.addate$), 7, 2)
	 'MID$(dymd$, 4, 2) = MID$(FNDYY$(Audit.addate$), 4, 2)
	 'MID$(dymd$, 7, 2) = MID$(FNDYY$(Audit.addate$), 1, 2)
	'//////////////////  Use PE records to jump old months  ////////////////
	 DO WHILE audit.aDdate < begyymd$
		adnxtpe% = CVI(MID$(audit.adsname$, 1, 2))
		adprepe% = CVI(MID$(audit.adsname$, 3, 2))
		adlstpe% = CVI(MID$(audit.adsname$, 5, 2))
		IF adnxtpe% < 1 OR adlstpe% > adlast% THEN Rec% = -1: EXIT DO
		Rec% = adnxtpe%
		GET #8, Rec%, audit
		dymd$ = "  /  /  "
		'MID$(dymd$, 1, 2) = MID$(FNDYY$(Audit.addate$), 7, 2)
		'MID$(dymd$, 4, 2) = MID$(FNDYY$(Audit.addate$), 4, 2)
		'MID$(dymd$, 7, 2) = MID$(FNDYY$(Audit.addate$), 1, 2)
		LOOP

END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

SUB selectfile (sel%, updwn%)
	PCOPY 0, 1
	CALL BOX(4, 21, 22, 45, 2, 0, 1)

	FOR i% = 1 TO naudit%
		LOCATE 5 + i%, 23: PRINT USING "## &"; i%; auditfile$(i%)
	NEXT

	DO
	LOCATE 21, 23: PRINT "Option..>";
	LOCATE 21, 32:
				CALL inpnew(opt$, 2!, updwn%, "13,59")
	IF updwn% = 59 THEN EXIT DO
	LOOP UNTIL updwn% = 13

	IF updwn% = 13 THEN sel% = VAL(opt$)
	IF sel% < 1 OR sel% > naudit% THEN sel% = naudit%


	PCOPY 1, 0
END SUB

SUB setaudit (n%)
'$INCLUDE: '\tpmanuf\src\setaudit.bi'
END SUB

SUB setmhdr
mhdr$(1) = "Co./Last Name"
mhdr$(2) = "First Name"
mhdr$(3) = "Addr 1 - Line 1"
mhdr$(4) = "       - Line 2"
mhdr$(5) = "       - Line 3"
mhdr$(6) = "       - Line 4"
mhdr$(7) = "Inclusive"
mhdr$(8) = "Invoice #"
mhdr$(9) = "Date"
mhdr$(10) = "Customer PO"
mhdr$(11) = "Ship Via"
mhdr$(12) = "Delivery Status"
mhdr$(13) = "Description"
mhdr$(14) = "Account #"
mhdr$(15) = "Amount"
mhdr$(16) = "Inc-Tax Amount"
mhdr$(17) = "Job"
mhdr$(18) = "Comment"
mhdr$(19) = "Journal Memo"
mhdr$(20) = "Salesperson Last Name"
mhdr$(21) = "Salesperson First Name"
mhdr$(22) = "Shipping Date"
mhdr$(23) = "Referral Source"
mhdr$(24) = "Tax Code"
mhdr$(25) = "Non-GST Amount"
mhdr$(26) = "GST Amount"
mhdr$(27) = "LCT Amount"
mhdr$(28) = "Freight Amount"
mhdr$(29) = "Inc-Tax Freight Amount"
mhdr$(30) = "Freight Tax Code"
mhdr$(31) = "Freight Non-GST Amount"
mhdr$(32) = "Freight GST Amount"
mhdr$(33) = "Freight LCT Amount"
mhdr$(34) = "Sale Status"
mhdr$(35) = "Currency Code"
mhdr$(36) = "Exchange Rate"
mhdr$(37) = "Terms - Payment is Due"
mhdr$(38) = "      - Discount Days"
mhdr$(39) = "      - Balance Due Days"
mhdr$(40) = "      - % Discount"
mhdr$(41) = "      - % Monthly Charge"
mhdr$(42) = "Amount Paid"
mhdr$(43) = "Payment Method"
mhdr$(44) = "Payment Notes"
mhdr$(45) = "Name on Card"
mhdr$(46) = "Card Number"
mhdr$(47) = "Expiry Date"
mhdr$(48) = "Authorisation Code"
mhdr$(49) = "BSB"
mhdr$(50) = "Account Number"
mhdr$(51) = "Drawer/Account Name"
mhdr$(52) = "Cheque Number"
mhdr$(53) = "Category"

IF opt% = 2 THEN
	FOR i% = 1 TO 53
	IF i% > 1 THEN PRINT #98, ",";
		PRINT #98, mhdr$(i%);
	NEXT
	PRINT #98, ""
END IF
END SUB

'////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>> sup00 -  UPDATE THE SUPPLIER FILE <<<<<<<<<<<<<<<<<<<<<<
'////////////////////////////////////////////////////////////////////////////
SUB upd.who (chaudit%, chcus%, upd%) STATIC
'$INCLUDE: '\tpmanuf\src\updwho.bi'
END SUB
