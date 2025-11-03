DECLARE SUB setaudit (n%)
DECLARE SUB browse.idx (first.on.screen%, ch1%, ch2%)
DECLARE SUB upd.who (ch.audit%, ch.sup%, upd%)
'.dc - Complete
'>>>>>>>>>>>>>>> CSPAY01 - CREDITORS PAYMENT ENTRY. <<<<<<<<<<<<<<<<<<<<
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	RESET
	DB.OR.CR$ = "CR"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	DIM SHARED maxwho%, chi%, ch%
	DIM chq#(500)
	DIM SHARED auditfile$(15), naudit%
	CONST acctype$ = "CP"   '- Creditors payment.
	CONST accdisctype$ = "CD"'- Creditors payment discount.
	CALL setaudit(naudit%)
	cashonly$ = "M": auditname$ = auditfile$(naudit%)
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	f% = 4
   '$INCLUDE: '\tpmanuf\src\ASAUDIT.INC'
	GOSUB OPEN.AUDIT
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	GET #36, 1, msmisc
	maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
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

	SELECT CASE "CR"  'DB.OR.CR$
	CASE "CR": chi% = 45: ch% = 44: apgm$ = "CSMENU"
	CASE "DB": chi% = 23: ch% = 43: apgm$ = "DSMENU"
	CASE "--": chi% = 65: ch% = 64: apgm$ = "FIMENU"
	CASE ELSE
	END SELECT

	SELECT CASE ch%
	CASE 44: maxwho% = CVI(msmisc.max1$)
	CASE 43: maxwho% = CVI(msmisc.max7$)
	CASE 64: maxwho% = CVI(msmisc.max9$)
	CASE ELSE
	END SELECT

	'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
300 CALL setup("CREDITOR PAYMENT ENTRY")
	btm$ = "     F1-Exit                   F6-Browse             F10-Enter invoice details "
370 COLOR 0, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
390 updwn% = 0:
	IF NOT pass% THEN
		COLOR 2, 0: in$ = ""
		LOCATE 3, 20: PRINT "Enter creditor number..> "
		LOCATE 3, 44
		CALL inpnew(in$, 105!, updwn%, "13,59,64,68" + ALT$): GOSUB ALT
				in$ = UCASE$(in$)
	END IF
		pass% = 0
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	IF updwn% = 64 THEN
		CALL browse.idx(first.on.screen%, chi%, ch%)
		in$ = STR$(first.on.screen%)
		pass% = -1
		GOTO 300
		END IF
	IF updwn% = 68 THEN
			GOSUB 1010
			IF rec > 0 AND rec <= maxcus% THEN
				VIEW PRINT 2 TO 23: CLS : VIEW PRINT
				CALL BOX(1, 2, 80, 24, 7, 8, -2)
				END IF
		  COLOR 2, 0
		  GOTO 520
		  END IF
	p = VAL(in$)
	'>>>>> EDIT ENTRY
	IF LEN(in$) = 0 THEN p = p + 1: GOTO 520
	p = VAL(in$)
	IF p > 0 THEN 520
	skey$ = in$: GOSUB searchindex
	IF found% THEN p = CVI(supx.wrrn$)
	'/////////////////////////////////////////////////////
520 '>>>>> Get record and display
	'/////////////////////////////////////////////////////
	rec = p
	IF rec < 1 OR rec > maxcus% THEN COLOR 14: LOCATE 4, 20: PRINT "Not found on file.": COLOR 2: GOTO 390
	LOCATE 4, 20: PRINT CHR$(FNE)
	GET #ch%, rec, sup
	sno% = CVI(sup.sno$)
	scur = CVS(sup.scur$): s30 = CVS(sup.s30$): s60 = CVS(sup.s60$): s90 = CVS(sup.s90$)
	sdays% = CVI(sup.sdays$): climit = CVS(sup.climit$)
	sterms = CVS(sup.sterms$): daysmax% = CVI(sup.daysmax$)
	IF sno% = 0 THEN sno% = rec
	total = scur + s30 + s60 + s90
	X0 = 5: COLOR 2, 0
	LOCATE 4, X0: PRINT "File number.......:"; sno%; "  "; sup.search$; CHR$(FNE)
	LOCATE 4, X0 + 45: PRINT "Type.>"; sup.stype$; CHR$(FNE)
	LOCATE 5, X0: PRINT "         Name......:"; sup.sname$; CHR$(FNE)
	LOCATE , X0: PRINT "         Address...:"; sup.saddr$; CHR$(FNE)
	LOCATE , X0: PRINT "Suburb / Post code.:"; CHR$(FNE); sup.suburb$; " "; sup.spcode$
	LOCATE , X0: PRINT "Contact............:"; sup.scont$; CHR$(FNE)
	LOCATE , X0: PRINT "Telephone .........:"; : PRINT USING "\         \"; sup.sphone$;
	LOCATE , X0 + 36: PRINT "(Bus.)........:"; : PRINT USING "\         \(A.H.)"; sup.sphone1$
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
	GET #45, p%, supx
	IF CVI(supx.wrrn$) = 0 THEN LSET supx.wcde$ = STRING$(99, CHR$(255))
	IF supx.wcde$ + wtyp$ = skey$ THEN skey = p%: skey1 = p%: found% = -1: RETURN
	IF e% - s% = 1 THEN skey = 0: skey1 = s%: RETURN
	IF supx.wcde$ + wtyp$ < skey$ THEN s% = p%: GOTO searchagain
	IF supx.wcde$ + wtyp$ > skey$ THEN e% = p%: GOTO searchagain
RETURN
	 '//////////////////////////////////////////////////
1010 '>>>>> E N T E R     D E T A I L S
	 '//////////////////////////////////////////////////
	IF rec < 1 OR rec > maxcus% THEN RETURN
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
	 LOCATE , 2: PRINT USING "   Gen. Ledger account...>  ###.##"; CVS(sup.sgl$)
	 '////////////////////////////////////////////////////////////
	 '>> Find the last cheque number.
	 '////////////////////////////////////////////////////////////
	 docnum$ = Audit.addocnum$: LSET docnum$ = SPACE$(99)
	'/////////////////// Find last cheque number
	number.of.goes% = 0
	rec% = lstpe.on.file%
	FOR chq% = 1 TO 500: chq#(chq%) = 0: NEXT
	chq% = 0
search.again:
	cheque# = 0
	GET #8, rec%, Audit
	DO WHILE NOT EOF(8)
		IF Audit.adtype$ = acctype$ AND VAL(Audit.addocnum$) > cheque# THEN
			cheque# = VAL(Audit.addocnum$)
			IF chq% = UBOUND(chq#, 1) THEN EXIT DO
			chq% = chq% + 1: chq#(chq%) = cheque#
		END IF
		GET #8, , Audit: rec% = rec% + 1
		LOOP
	IF cheque# = 0 AND number.of.goes% = 0 THEN
		number.of.goes% = 1
		rec% = snd.lstpe.on.file%
		GOTO search.again
		END IF
	'/////////////////// Increment the last cheque number by one
	IF cheque# <> 0 THEN
		IF cheque# = 999999999999# THEN cheque# = 0
		cheque# = cheque# + 1
		a$ = STR$(cheque#)
		LSET docnum$ = MID$(a$, 2) + "?"'??

		END IF
	'/////////////////// Initilize strings
	text$ = Audit.adtext$: LSET text$ = SPACE$(99)
	VALUE = 0: disc = 0: thischeque = 0
	wrkd$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)'??
	docdate$ = FNDY$(wrkd$)
	glacc = CVS(sup.sgl$)
	thischeque = 0
1180 '///////////////////  get date
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
	 GOTO 1500
1250 '/////////////////// document number
	 updwn% = 0:
		LOCATE 15, 28
		in$ = docnum$
		CALL inpnew(in$, 112!, updwn%, "13,59,60,72,80")
		LSET docnum$ = in$
	IF updwn% = 59 THEN GOTO endinp
	 GOSUB xer1
	 IF updwn% = 72 THEN updwn% = 60
	 IF updwn% = 60 THEN 1180
1320 '/////////////////// text
	 updwn% = 0:
		LOCATE 16, 28
		in$ = text$
		CALL inpnew(in$, 120!, updwn%, "13,59,60,72,80")
		LSET text$ = in$
	 IF updwn% = 59 THEN GOTO endinp
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
		IF updwn% = 59 THEN GOTO endinp
	 GOSUB xer1
	 IF updwn% = 72 THEN updwn% = 60
	 IF updwn% = 60 THEN 1320
	'>-First time in prompt all fields and goto "all correct?"
	 IF VALUE = 0 THEN
		VALUE = thischeque + disc
		GOTO endinp
		END IF
1470 '/////////////////// discount
	updwn% = -3
	LOCATE 18, 28
	a = 0 - disc
	in$ = STR$(a)
        CALL inpnew(in$, 7.2!, updwn%, "13,59,60,72,80")
	disc = VAL(in$)
	disc = ABS(disc)
	IF updwn% = 59 THEN GOTO endinp
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
	 IF updwn% = 59 THEN GOTO endinp
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
	 IF updwn% = 59 THEN GOTO endinp
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
	IF VALUE <> thischeque + disc THEN msg$ = "Payment does not compute.": GOSUB er1: GOTO 1390
	 '*-G/L NUMBER--*'
	 IF glacc < 1! OR glacc > 999.99 THEN
			   msg$ = "G/L Number not valid."
			   GOSUB er1
			   GOTO 1600
			   END IF
	'/////////////////// CONFIRM FINISHED ////
	 GOSUB xer1
	 COLOR 14: LOCATE 21, 7: PRINT "All correct? (Y/N)..>";
	 updwn% = 0: in$ = "Y"
		LOCATE 21, 28
		CALL inpnew(in$, 101!, updwn%, "13,59-60")
	 IF updwn% = 59 OR updwn% = 1 THEN GOTO xchg
	 IF updwn% = 60 THEN in$ = "N"
	 IF in$ = "y" THEN in$ = "Y"
	 IF in$ = "n" THEN in$ = "N"
	 IF in$ <> "Y" AND in$ <> "N" THEN GOTO endinp
	 IF in$ = "N" THEN
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
	'/////              UPDATE THE FILE                  //////
	'////////////////////////////////////////////////////////////
	'>>>> Set up static fields for raw material entry
	LSET Audit.adtype$ = acctype$
	LSET Audit.adsname$ = sup.sname$
	LSET Audit.adcust$ = sup.search$ + sup.stype$
	'>>>> Set up other fields
	LSET Audit.adtext$ = text$
	LSET Audit.addate$ = docdate$
	Audit.adglacc! = glacc!
	LSET Audit.addocnum$ = docnum$
	 '////////////////////////////////////////////////////////////
	 '>>>>>>>>>>>> Write to audit file record <<<<<<<<<<<<<<<<<<<<
	 '////////////////////////////////////////////////////////////
	 '/// Save payment total to update the cumstomer file.
	Audit.advalue = 0 - thischeque!
	cha% = 8'Channel of audit file
	chw% = ch%'Channel of sup file
	CALL upd.who(cha%, chw%, -1)

	IF thischeque <> 0 THEN
		GET #ch%, rec, sup
		wrkd$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)'??
		LSET sup.addate$ = FNDY$(wrkd$)
		LSET sup.addocnum$ = docnum$
		LSET sup.advalue$ = MKS$(0 - thischeque)
		PUT #ch%, rec, sup
		END IF

	'// If a discount is offered take it
	IF disc <> 0 THEN
		LSET Audit.adtype$ = accdisctype$
		Audit.advalue = 0 - disc!
		CALL upd.who(cha%, chw%, -1)
		END IF
xchg: RETURN
	 '//////////////////////////////////////////////////////
	 ' ERROR ROUTINE 1
	 '//////////////////////////////////////////////////////
er1: COLOR 14, 0: LOCATE 21, 2: PRINT msg$ + CHR$(FNE): COLOR 2
	 RETURN
xer1: LOCATE 21, 2: PRINT SPACE$(78): COLOR 2
	 RETURN

SUB browse.idx (firstonscreen%, ch1%, ch2%) STATIC
'$INCLUDE: '\tpmanuf\src\browse01.bi'
END SUB

SUB setaudit (n%)
'    DIM SHARED auditfile$(15), naudit%
'    CALL setaudit(naudit%)
'    cashonly$ = "M": auditname$ = auditfile$(naudit%)
'$INCLUDE: '\tpmanuf\src\setaudit.bi'
END SUB

'////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>> @sup00 -  UPDATE THE SUPPLIER FILE <<<<<<<<<<<<<<<<<<<<<<
'////////////////////////////////////////////////////////////////////////////
SUB upd.who (chaudit%, chcus%, upd%) STATIC
'$INCLUDE: '\tpmanuf\src\updwho.bi'
END SUB
