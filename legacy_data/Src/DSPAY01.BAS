DECLARE SUB setaudit (n%)
DECLARE SUB selectfile (filecode$, updwn%)
DECLARE SUB load.unpaid (cust$, startrec%, docnum$, VALUE!, updwn%)
DECLARE SUB browse.idx (first.on.screen%, ch1%, ch2%)
DECLARE SUB upd.who (ch.audit%, ch.sup%, upd%)
'.dc - Complete
'>>>>>>>>>>>>>>> DSPAY01 - DEBTORS PAYMENT ENTRY. <<<<<<<<<<<<<<<<<<<<
'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
	RESET: apgm$ = "DSMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	CONST acctype$ = "DP"   '- Debtors payment.
	CONST accdisctype$ = "DD"'- Debtors payment discount.
	DIM SHARED chq#(500)
	DIM SHARED auditfile$(15), naudit%
	CALL setaudit(naudit%)

	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\CUS.INC'
	'$INCLUDE: '\tpmanuf\src\CUSX.INC'
	'$INCLUDE: '\tpmanuf\src\msmisc.INC'
	'$INCLUDE: '\tpmanuf\src\ASAUDIT.INC'
	 parm$ = ENVIRON$("PARM$"): parm% = VAL(parm$)
	 DB.OR.CR$ = "DB"
	 cashonly$ = "M": auditname$ = auditfile$(naudit%)
	 GOSUB OPEN.AUDIT

	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxcus% = CVI(msmisc.max7$)
	'// Find the end of the audit file
	Adlast% = LOF(8) / 92
	GET #8, 1, Audit
	adnxtpe% = CVI(MID$(Audit.adsname$, 1, 2))
	adprepe% = CVI(MID$(Audit.adsname$, 3, 2))
	adlstpe% = CVI(MID$(Audit.adsname$, 5, 2))
	lstpe.on.file% = adlstpe%
	IF lstpe.on.file% < 1 THEN lstpe.on.file% = 1
	GET #8, lstpe.on.file%, Audit
	adnxtpe% = CVI(MID$(Audit.adsname$, 1, 2))
	adprepe% = CVI(MID$(Audit.adsname$, 3, 2))
	adlstpe% = CVI(MID$(Audit.adsname$, 5, 2))
	snd.lstpe.on.file% = adprepe%
	IF snd.lstpe.on.file% < 1 THEN snd.lstpe.on.file% = 1
	'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
300
	CALL setup("DEBTORS PAYMENT ENTRY")
	btm$ = " F1-Exit   F5-History   F6-Browse   F8-Payment   F9-Insert Total   F10-Invoices"
	LOCATE 3, 67: PRINT auditname$
370 COLOR 0, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
	IF NOT pass% THEN
		COLOR 2, 0
		LOCATE 3, 20: PRINT "Enter debtors number...> "
		LOCATE 3, 44: in$ = ""
		CALL inpnew(in$, 105!, updwn%, "13,59,63,64,66-68" + ALT$): GOSUB ALT
				in$ = UCASE$(in$)
		END IF
		pass% = 0
	IF updwn% = 68 AND LEN(in$) > 1 THEN pass% = -1: GOTO search.rec
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	IF updwn% = 63 THEN
		CALL selectfile(filecode$, updwn%)
		parm$ = "PARM$=" + filecode$: ENVIRON parm$: RUN
		END IF
	IF updwn% = 64 THEN
		CALL browse.idx(s%, 23, 43)
		in$ = STR$(s%)
		updwn% = 13
		pass% = -1
		GOTO 300
		END IF
	IF updwn% = 66 THEN
		cust$ = cus.search$ + cus.stype$
		docnum$ = "": VALUE! = 0
		CALL load.unpaid(cust$, 1, docnum$, VALUE!, updwn%)
		in$ = cust$
		updwn% = 13
		pass% = -1
		GOTO 300
		END IF
	IF updwn% = 67 THEN GOSUB add.total: GOTO 300
	IF updwn% = 68 THEN

			GOSUB enter.details
			IF rec > 0 AND rec <= maxcus% THEN
				VIEW PRINT 2 TO 23: CLS : VIEW PRINT
				CALL BOX(1, 2, 80, 24, 7, 8, 2)
				END IF
		  COLOR 2, 0
		  GOTO 520
		  END IF
search.rec:
	p = VAL(in$)
	'>>>>> EDIT ENTRY
	IF LEN(in$) = 0 THEN p = p + 1: GOTO 520
	p = VAL(in$)
	IF p > 0 THEN 520
	skey$ = in$: GOSUB searchindex
	IF found% THEN p = CVI(cusx.wrrn$)
	in$ = ""
	'/////////////////////////////////////////////////////
520 '>>>>> Get record and display
	'/////////////////////////////////////////////////////
	rec = p
	IF rec < 1 OR rec > maxcus% THEN COLOR 14: LOCATE 4, 20: PRINT "Not found on file.": COLOR 2: GOTO 370
	LOCATE 4, 20: PRINT CHR$(FNE)
	GET #43, rec, cus
	sno% = CVI(cus.sno$)
	scur = CVS(cus.scur$): s30 = CVS(cus.s30$): s60 = CVS(cus.s60$): s90 = CVS(cus.s90$)
	sdays% = CVI(cus.sdays$): climit = CVS(cus.climit$)
	sterms = CVS(cus.sterms$): daysmax% = CVI(cus.daysmax$)
	IF sno% = 0 THEN sno% = rec
	total = scur + s30 + s60 + s90
	X0 = 5: COLOR 2, 0
	LOCATE 4, X0: PRINT "File number.......:"; sno%; "  "; cus.search$; CHR$(FNE)
	LOCATE 4, X0 + 45: PRINT "Type.>"; cus.stype$; CHR$(FNE)
	LOCATE 5, X0: PRINT "         Name......:"; cus.sname$; CHR$(FNE)
	LOCATE , X0: PRINT "         Address...:"; cus.saddr$; CHR$(FNE)
	LOCATE , X0: PRINT "Suburb / Post code.:"; CHR$(FNE); cus.suburb$; " "; cus.spcode$
	LOCATE , X0: PRINT "Contact............:"; cus.scont$; CHR$(FNE)
	LOCATE , X0: PRINT "Telephone .........:"; CHR$(FNE);
	LOCATE , X0 + 36: PRINT "(Bus.)........:"; CHR$(FNE);
	LOCATE , X0: PRINT "Trading terms......:"; daysmax%; " Days."; CHR$(FNE);
	LOCATE , X0 + 35: PRINT sdays%; " Days for "; sterms; "% discount."; CHR$(FNE)
	IF climit < 1 THEN a$ = "Trading terms"
	IF climit = 0 THEN a$ = "C.O.D        "
	IF climit > 0 THEN a$ = STR$(climit)
	IF total < 0 THEN
		LOCATE , 2: PRINT CHR$(FNE)
		COLOR 14
		LOCATE , 2: PRINT CHR$(FNE);
		LOCATE , 2: PRINT USING "                      Account is in credit $$#,###.## "; ABS(total): COLOR 2
	ELSE
		COLOR 6
		LOCATE , X0: PRINT "Total        90+ Days     60 Days     30 Days      Current    C/Limit"
		COLOR 2
		LOCATE , 2: PRINT USING "###,###.##   ###,###.##   ###,###.##   ###,###.## #,###,###.##  \          \"; total; s90; s60; s30; scur; a$
		END IF
	GOTO 370
'//////////////////////////////////////////////////////////////////////////
'>>>>> Lookup index file. Passed skey$. Returns SKEY, 0 if not found. <<<<<
'>>>>> SKEY1, one after insertion place                               <<<<<
'//////////////////////////////////////////////////////////////////////////
searchindex:
	skey = 0: skey1 = 0: found% = 0
	IF skey$ = "     " THEN skey1 = 0: RETURN
	s% = 0: e% = maxcus%
searchagain:
	p% = (e% - s%) / 2 + s%
	IF p% = 0 THEN skey = 0: skey1 = s%: RETURN
	GET #23, p%, cusx
	IF CVI(cusx.wrrn$) = 0 THEN LSET cusx.wcde$ = STRING$(99, CHR$(255))
	IF cusx.wcde$ + wtyp$ = skey$ THEN skey = p%: skey1 = p%: found% = -1: RETURN
	IF e% - s% = 1 THEN skey = 0: skey1 = s%: RETURN
	IF cusx.wcde$ + wtyp$ < skey$ THEN s% = p%: GOTO searchagain
	IF cusx.wcde$ + wtyp$ > skey$ THEN e% = p%: GOTO searchagain
RETURN
	'//////////////////////////////////////////////////
	'>>>>> E N T E R     D E T A I L S
	'//////////////////////////////////////////////////
enter.details:
	IF rec < 1 OR rec > maxcus% THEN RETURN
	 '////////////////////////////////////////////////////////////
	 '>> Find the last cheque number.
	 '////////////////////////////////////////////////////////////
	 docnum$ = Audit.addocnum$: LSET docnum$ = SPACE$(99)
	'/////////////////// Find last cheque number
	NUMBER.OF.GOES% = 0
	rec% = lstpe.on.file%
	FOR chq% = 1 TO 500: chq#(chq%) = 0: NEXT
	chq% = 0
search.again:
	cheque# = 0
	GET #8, rec%, Audit
	DO WHILE NOT EOF(8)
		IF Audit.adtype$ = acctype$ AND VAL(Audit.addocnum$) > cheque# THEN
			cheque# = VAL(Audit.addocnum$)
			IF chq% = 500 THEN EXIT DO
			chq% = chq% + 1: chq#(chq%) = cheque#
			END IF
		GET #8, , Audit: rec% = rec% + 1
		LOOP
	IF cheque# = 0 AND NUMBER.OF.GOES% = 0 THEN
		rec% = snd.lstpe.on.file%
		NUMBER.OF.GOES% = 1
		GOTO search.again
		END IF
	'/////////////////// Increment the last cheque number by one
	IF cheque# <> 0 THEN
		IF cheque# = 999999999999# THEN cheque# = 0
		cheque# = cheque# + 1
		a$ = STR$(cheque#)
		LSET docnum$ = MID$(a$, 2)
		END IF
	'/////////////////// Initilize strings
	text$ = Audit.adtext$: LSET text$ = SPACE$(99)
	VALUE = 0: disc = 0: thischeque = 0
	docdate$ = FNDY$(DATE1$)
	glacc = CVS(cus.sgl$)
	thischeque = 0

enter.details10:
	LOCATE 13, 2: PRINT SPACE$(78)
	LOCATE 14, 2: PRINT SPACE$(78)
	COLOR 4: LOCATE 13, 2
	PRINT "อออออออออออออออออออออออออต  P A Y M E N T   E N T R Y ฦออออออออออออออออออออออ"
	COLOR 2
	 LOCATE 14, 2: PRINT "   Payment date..........> "
	 LOCATE , 2: PRINT "   Payment number........> "; SPACE$(50)
	 LOCATE , 2: PRINT "   Associated text.......> "
	 LOCATE , 2: PRINT "   This cheque...........> "
	 LOCATE , 2: PRINT "   Discount (if any).....> "
	 LOCATE , 2: PRINT "   Total payment.........> "
	 LOCATE , 2: PRINT USING "   Gen. Ledger account...>  ###.##"; CVS(cus.sgl$)
1180 '///////////////////  get , date
	 updwn% = 0:
		LOCATE 14, 28
		in$ = docdate$
		CALL inpnew(in$, 108!, updwn%, "13,59,60,72,80")
		LSET docdate$ = in$
	 IF updwn% = 59 THEN GOTO endinp'Back to start
	 GOSUB xer1
	 IF updwn% = 72 THEN updwn% = 60
	 IF updwn% = 60 THEN 1180
	 ' SKIP DOC FIELD
	 LOCATE 15, 28
	 PRINT docnum$ + SPACE$(12)
	 GOTO 1500 'This cheque
1250 '/////////////////// document number
	 updwn% = 0:
		LOCATE 15, 28
		in$ = docnum$
		CALL inpnew(in$, 112!, updwn%, "13,59,60,72,80")
		LSET docnum$ = in$
	IF updwn% = 59 THEN GOTO endinp'end
	 GOSUB xer1
	 IF updwn% = 72 THEN updwn% = 60
	 IF updwn% = 60 THEN 1180
1320 '/////////////////// text
	 updwn% = 0:
		LOCATE 16, 28
		in$ = text$
		CALL inpnew(in$, 120!, updwn%, "13,59,60,72,80")
		LSET text$ = in$
	 IF updwn% = 59 THEN GOTO endinp'end
	 GOSUB xer1
	 IF updwn% = 72 THEN updwn% = 60
	 IF updwn% = 60 THEN 1250
1500 '/////////////////// This cheque
	 updwn% = -3
		LOCATE 17, 28
		in$ = STR$(thischeque)
                CALL inpnew(in$, 11.2!, updwn%, "13,59,60,72,80")
		a = VAL(in$)
		thischeque = ABS(a)
		IF updwn% = 59 THEN GOTO endinp'end
	 GOSUB xer1
	 IF updwn% = 72 THEN updwn% = 60
	 IF updwn% = 60 THEN 1320
1470 '/////////////////// discount
	updwn% = -3
	LOCATE 18, 28
	a = 0 - disc
	in$ = STR$(a)
        CALL inpnew(in$, 7.2!, updwn%, "13,59,60,72,80")
	disc = VAL(in$)
	disc = ABS(disc)
	IF updwn% = 59 THEN GOTO endinp'end
	GOSUB xer1
	IF updwn% = 72 THEN updwn% = 60
	IF updwn% = 60 THEN 1500
	'/////////////////// prompt for the correct cheque amount ////
	VALUE = thischeque + disc
	 'display on screen only
	 updwn% = -3
		LOCATE 19, 28
		in$ = STR$(VALUE)
         CALL inpnew(in$, 7.2!, updwn%, "")
	IF disc <> 0 THEN GOTO endinp
1390 '/////////////////// Total value
	 updwn% = -3
		LOCATE 19, 28
		in$ = STR$(VALUE)
                CALL inpnew(in$, 7.2!, updwn%, "13,59,60,72,80")
		VALUE = VAL(in$)
		VALUE = ABS(VALUE)
	 IF updwn% = 59 THEN GOTO endinp'end
	 GOSUB xer1
	 IF updwn% = 72 THEN updwn% = 60
	 IF updwn% = 60 THEN 1470
	'/////////////////// prompt for the correct cheque amount ////
	disc = VALUE - thischeque
	'/////////////////// display on screen only
	 updwn% = -3
		LOCATE 18, 28
		in$ = STR$(disc)
         CALL inpnew(in$, 7.2!, updwn%, "")
	 '////////////////// G/L account number
	 GOTO endinp
1600 updwn% = 0:
	 LOCATE 20, 30: updwn% = 1
	 in$ = STR$(glacc)
         CALL inpnew(in$, -5.2!, updwn%, "13,59,60,72,80")
	 glacc = VAL(in$)
	 IF updwn% = 59 THEN GOTO endinp'end
	 GOSUB xer1
	 IF updwn% = 72 THEN updwn% = 60
	 IF updwn% = 60 THEN 1390
endinp:
	 IF updwn% = 59 OR updwn% = 1 THEN GOTO xchg
	'/////////////////// EDIT KEY PARTS ////
	 '*-DATE--*'
	IF docdate$ = SPACE$(8) THEN msg$ = "Date not valid.": GOSUB er1: GOTO 1180
	 '*-VALUE--*'
	IF VALUE <= 0 THEN msg$ = "Value must be entered.": GOSUB er1: GOTO 1390
	'*-CHECK THE PAYMENT ADDS UP --*'
	test = thischeque + disc
	IF VALUE <> test THEN msg$ = "This Cheque + Discount is not the same as keyed Total payment.": GOSUB er1: GOTO 1390
	 '*-G/L NUMBER--*'
	 IF glacc < 1! OR glacc > 999.99 THEN
			   msg$ = "G/L Number not valid."
			   GOSUB er1
			   GOTO 1600
			   END IF
	'/// CONFIRM FINISHED ////
	GOSUB xer1

	allok$ = "Y"
	DO
	COLOR 14: LOCATE 21, 7: PRINT "All correct? (Y/N/Z)..>    (Z- Don't mark invoices)";
	updwn% = 0
		LOCATE 21, 30
		CALL inpnew(allok$, 101!, updwn%, "13,59-60")
				allok$ = UCASE$(allok$)
		IF updwn% = 59 THEN allok$ = "N"
		IF updwn% = 60 THEN allok$ = "N"
		LOOP UNTIL allok$ = "Y" OR allok$ = "N" OR allok$ = "Z"

		IF allok$ = "N" THEN
			LOCATE 21, 2: PRINT SPACE$(40)
			GOTO 1600
			END IF
	'/////////////////// Make sure the cheque number has not already been used.
	ok% = -1
	FOR i% = 1 TO chq%
		IF VAL(docnum$) = chq#(i%) THEN ok% = 0: EXIT FOR
		NEXT
	IF NOT ok% THEN msg$ = "Cheque number already used.": GOSUB er1: GOTO 1250
'////////////////////////////////////////////////////////////
'>>>>>>
'////////////////////////////////////////////////////////////
	IF allok$ <> "Z" THEN
		cust$ = cus.search$ + cus.stype$
		CALL load.unpaid(cust$, 1, docnum$, VALUE!, updwn%)
		IF updwn% = 59 THEN GOTO enter.details10
		END IF

upd.rec.chg:
	'>>>> Set up static fields for raw material entry
	LSET Audit.addate$ = docdate$
	LSET Audit.adtype$ = acctype$
	LSET Audit.adsname$ = cus.sname$
	LSET Audit.adcust$ = cus.search$ + cus.stype$
	'>>>> Set up other fields
	LSET Audit.adtext$ = text$
	Audit.adglacc! = glacc!
	LSET Audit.addocnum$ = docnum$
	LSET Audit.adpaid$ = "?"
	IF updwn% = -1 THEN LSET Audit.adpaid$ = "A"
	 '////////////////////////////////////////////////////////////
	 '>>>>>>>>>>>> Write to audit file record <<<<<<<<<<<<<<<<<<<<
	 '////////////////////////////////////////////////////////////
	IF thischeque <> 0 THEN
		CALL ROUND(thischeque!, 2.5)
		Audit.advalue = 0 - thischeque!
		Audit.adtax! = 0
		cha% = 8'Channel of audit file
		chw% = 43'Channel of sup file
		CALL upd.who(cha%, chw%, -1)

		'- record the last cheque date
		GET #43, rec, cus
		LSET cus.addate$ = FNDY$(DATE1$)
		LSET cus.addocnum$ = docnum$
		LSET cus.advalue$ = MKS$(0 - thischeque - disc)
		PUT #43, rec, cus
		END IF
	'
	'// If a discount is offered take it
	IF disc <> 0 THEN
		LSET Audit.adtype$ = accdisctype$
		CALL ROUND(disc!, 2.5)
		Audit.advalue = (0 - disc!)
		Audit.adtax! = 0
		cha% = 8'Channel of audit file
		chw% = 43'Channel of sup file
		CALL upd.who(cha%, chw%, -1)
		END IF
xchg:
RETURN
'////////////////////////////////////////////////////////////
'/////  ADD A PAYMENT TOTALS RECORD
'////////////////////////////////////////////////////////////
add.total:
	'>-
	'>-- Display the payment batch on the screen
	'>-
	CALL setup("DISPLAY A PAYMENT BATCH")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : COLOR 2, 0
	COLOR 6, 0
	LOCATE 3, 6: PRINT "Rec.    Cust.   PT        Value"
	LOCATE 3, 46: PRINT "Rec.    Cust.   PT        Value"
	COLOR 2, 0
	'// Find the end of the audit file
	Adlast% = LOF(8) / 92
	'>- Search for the last payment total or Two P.E.
	rec% = Adlast%
	GET #8, rec%, Audit
	DO UNTIL Audit.adtype$ = "PT" OR rec% = 1
		rec% = rec% - 1
		GET #8, rec%, Audit
		LOOP
	IF Audit.adtype$ <> "PT" THEN GOTO x.add.total
	start% = rec% + 1
	max.lines% = 16
	x1% = 6
	rec% = start%
	chk.total = 0
top.of.browse:
	lin% = 0
	GET #8, rec%, Audit
	DO WHILE NOT EOF(8) AND lin% < max.lines%
	IF Audit.adtype$ = "DP" THEN chk.total = chk.total - Audit.advalue
	IF Audit.adtype$ = "DP" OR Audit.adtype$ = "DD" THEN
		LOCATE lin% + 4, x1%
		IF Audit.adtype$ = "DD" THEN COLOR 4, 0
		PRINT USING "#####   &   &   $$#,###.##"; rec%; Audit.adcust$; Audit.adtype$; ABS(Audit.advalue)
		COLOR 2, 0
		lin% = lin% + 1
		END IF
	GET #8, , Audit: rec% = rec% + 1
	LOOP
	IF NOT EOF(8) THEN x1% = 46: GOTO top.of.browse
	'>-
	'>--
	'>-
	COLOR 14
	LOCATE 21, 20: PRINT USING "The payment total is $$###,###.##"; chk.total
	COLOR 2
	in2$ = "N"
	DO
		LOCATE 22, 20: PRINT "Write this payment total (Y/N)...> "; CHR$(FNH);
		CALL inpnew(in2$, 101!, updwn%, "13,59-60")
				in2$ = UCASE$(in2$)
		IF updwn% = 59 THEN in2$ = "N"
		IF updwn% = 60 THEN in2$ = "N"
		IF in2$ = "Y" AND chk.total = 0 THEN in2$ = "n"
		LOOP UNTIL in2$ = "Y" OR in2$ = "N"
		IF in2$ = "N" GOTO x.add.total
upd.rec.payment.total:
	'>>>> Set up TOTAL <<<<<
	LSET Audit.addate$ = FNDY$(DATE1$)
	LSET Audit.adtype$ = "PT"
	LSET Audit.adtext$ = "Payment total"
	LSET Audit.adsname$ = SPACE$(99)
	LSET Audit.adcust$ = SPACE$(99)
	Audit.adglacc! = 0
	LSET Audit.addocnum$ = SPACE$(99)
	 '////////////////////////////////////////////////////////////
	 '>>>>>>>>>>>> Write to audit file record <<<<<<<<<<<<<<<<<<<<
	 '////////////////////////////////////////////////////////////
	Audit.advalue = chk.total!
	Audit.adtax! = 0
	cha% = 8'Channel of audit file
	chw% = 43'Channel of sup file
	CALL upd.who(cha%, chw%, -1)
x.add.total:
RETURN
'//////////////////////////////////////////////////////
' ERROR ROUTINE 1
'//////////////////////////////////////////////////////
er1: COLOR 14, 0: LOCATE 21, 2: PRINT msg$ + CHR$(FNE): COLOR 2
	 RETURN
xer1: LOCATE 21, 2: PRINT SPACE$(78): COLOR 2
	 RETURN

SUB browse.idx (firstonscreen%, ch1%, ch2%)
'$INCLUDE: '\tpmanuf\src\browse01.bi'
END SUB

SUB load.unpaid (cust$, startrec%, docnum$, VALUE!, updwn%) STATIC
'$INCLUDE: '\tpmanuf\src\dsunpaid.bi'
 END SUB

SUB selectfile (filecode$, updwn%)
	PCOPY 0, 1
	CALL BOX(4, 21, 22, 45, 2, 0, 1)

	FOR i% = 1 TO 15
	p% = 88 + i% - 1
	s% = p% + 1
	p$ = RIGHT$("00" + MID$(STR$(p%), 2), 2)
	s$ = RIGHT$("00" + MID$(STR$(s%), 2), 2)
	wrk$ = "YEAR" + p$ + s$ + ".HST"
	ok% = 0
		a$ = DIR$(wrk$)
		IF a$ <> "" THEN
		OPEN wrk$ FOR RANDOM SHARED AS #99
		IF LOF(99) > 0 THEN ok% = -1
		CLOSE #99
		END IF

	IF ok% THEN LOCATE 5 + i%, 23: PRINT USING "## &"; i%; wrk$
	NEXT

	DO
	LOCATE 21, 23: PRINT "Option..>";
	LOCATE 21, 32:
        CALL inpnew(opt$, 2!, updwn%, "13,59")
	IF updwn% = 59 THEN EXIT DO
	LOOP UNTIL updwn% = 13

	i% = VAL(opt$)
	IF i% < 0 OR i% > 15 THEN i% = 1
	p% = 88 + i% - 1
	s% = p% + 1
	p$ = RIGHT$("00" + MID$(STR$(p%), 2), 2)
	s$ = RIGHT$("00" + MID$(STR$(s%), 2), 2)
	wrk$ = "YEAR" + p$ + s$ + ".HST"
	filecode$ = s$
	IF VAL(opt$) = 0 THEN filecode$ = "N"

	PCOPY 1, 0
END SUB

SUB setaudit (n%)
'$INCLUDE: '\tpmanuf\src\setaudit.bi'
END SUB

SUB upd.who (chaudit%, chcus%, upd%) STATIC
'$INCLUDE: '\tpmanuf\src\updwho.bi'
END SUB
