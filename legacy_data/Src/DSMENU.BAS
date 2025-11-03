DECLARE SUB printpslip (updwn%)
'>>>>>>>>>>>>>>>>>>>>>> DEBTORS SYSTEM MENU <<<<<<<<<<<<<<<<<<<<<<<<<<<<
'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
	apgm$ = "MENUTP"
''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	'///////////////////////////////////////////////////////////////////////
	'////    ACCOUNTING AUDIT FILE RECORD TYPES
	'///////////////////////////////////////////////////////////////////////
	'///     CI - Creditors invoice
	'///     CC - Creditors credit note
	'///     CP - Creditors payment
	'///     CD - Creditors discount taken
	'///     CT - Credit sales tax (Portion of invoice)
	'///
	'///     DI - Debtors invoice
	'///     DC - Debtors credit note
	'///     DP - Debtors payment
	'///     DD - Debtors discount given
	'///     DT - Debtors sales tax (Portion of invoice)
	'///
	'///     JC - Credit journal entry
	'///     JD - Debit journal entry
	'///     PE - Period end.
	'///////////////////////////////////////////////////////////////////////
	CONST acctype$ = "DI"'Debtors invoice
	CONST acctaxtype$ = "DT"'- Sales tax portion of invoice.
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\msmisc.INC'
	GET #36, 1, msmisc
	cca$ = msmisc.cc$
	CLOSE
	CALL setup(cca$)
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : COLOR 2, 0
	x1 = 7: x2 = 47: y = 8
	COLOR 4, 0
	LOCATE 4, 24: PRINT "   D E B T O R S    S Y S T E M  "
	LOCATE 5, 24: PRINT " ================================"
	COLOR 2
	LOCATE 6, 26: PRINT "1....Debtors invoice entry."
	LOCATE , 26: PRINT "2....Debtors payment entry."
	LOCATE , 26: PRINT "3....Debtors file maintainance."
	LOCATE , 26: PRINT "5....Debtors listing."
	LOCATE , 26: PRINT "6....Pick up address."
	LOCATE , 26: PRINT "7....Reprint invoice or credit."
	LOCATE , 26: PRINT "8....Stand alone invoice."
	COLOR 10, 0
	LOCATE , 26: PRINT "9....Work Orders."
	COLOR 2, 0
	LOCATE , 25: PRINT "10....Print statements."
	LOCATE , 25: PRINT "11....Print selected statement."
	LOCATE , 25: PRINT "41....Debtors Tools."
	LOCATE , 25: PRINT "42....Print Aged Debtors Report."
	LOCATE , 25: PRINT "43....Load/unload opening balances."
	LOCATE , 25: PRINT "44....Debtors invoice entry. (Previous Prices)"
	LOCATE , 25: PRINT "92....Print keyed p/slips."
	LOCATE , 25: PRINT "93....List orders.  95..List orders previous prices"
	LOCATE , 25: PRINT "94....List stock on order."
	'>>>>> OPTIONS
getopt: LOCATE 23, 27: PRINT "Option..> ";
	a$ = "": updwn% = 1
	LOCATE 23, 36
	CALL inpnew(a$, 102!, updwn%, "59,13" + alt$): GOSUB alt
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	B% = VAL(a$)
	IF B% = 1 THEN achain$ = "DSINV01D": CALL exitpgm(achain$): CHAIN achain$
	IF B% = 2 THEN achain$ = "dspay01": CALL exitpgm(achain$): CHAIN achain$
	IF B% = 3 THEN
		achain$ = "XXWHO01":
		ENVIRON "DB.OR.CR$=DB"
		CALL exitpgm(achain$): CHAIN achain$
	END IF
	IF B% = 6 THEN achain$ = "dspic01": CALL exitpgm(achain$): CHAIN achain$
	IF B% = 5 THEN
	achain$ = "xxlbl02"
	ENVIRON "DB.OR.CR$=DB"
		CALL exitpgm(achain$): CHAIN achain$
	END IF
	IF B% = 7 THEN achain$ = "dsprt01": CALL exitpgm(achain$): CHAIN achain$
	IF B% = 8 THEN
		achain$ = "dsinv03d"
		ENVIRON "DB.OR.CR$=DB"
		CALL exitpgm(achain$): CHAIN achain$
	END IF

	IF B% = 9 THEN
		achain$ = "woinv01d"
		CALL exitpgm(achain$): CHAIN achain$
	END IF

	IF B% = 10 THEN
		CALL sndmsg("About to print Statments. Continue (Y/N)..>")
		dft$ = "N"
		DO
			LOCATE 24, 47
			CALL inpnew(dft$, 101!, updwn%, "13,59")
			dft$ = UCASE$(dft$)
			IF updwn% = 59 THEN dft$ = "N"
		LOOP UNTIL dft$ = "Y" OR dft$ = "N"
		CALL sndmsg("")

		IF dft$ = "Y" THEN
			LOCATE 2, 1
			SHELL "copy *.prn lpt1"
			SHELL "copy *.prn \statemen\*.*"
			SHELL "erase *.prn"
		END IF
	END IF
	IF B% = 11 THEN
					CALL sndmsg("                     Enter Account Code..>")
					acc$ = "?????mm"
					LOCATE 24, 46
					CALL inpnew(acc$, 107!, updwn%, "13,59")
					dft$ = UCASE$(dft$)
					IF updwn% = 59 THEN acc$ = "     "
					CALL sndmsg("")

					IF acc$ > " " THEN
						LOCATE 2, 1
						SHELL "copy \statement\" + acc$ + ".prn lpt1"
					END IF
	END IF

	IF B% = 41 THEN
					achain$ = "ASAUD03"
					ENVIRON "DB.OR.CR$=DB"
					CALL exitpgm(achain$): CHAIN achain$
					END IF

	IF B% = 42 THEN
					achain$ = "asaud04"
					ENVIRON "DB.OR.CR$=DB"
					CALL exitpgm(achain$): CHAIN achain$
					END IF

	IF B% = 43 THEN
					achain$ = "asaud02"
					ENVIRON "DB.OR.CR$=DB"
					CALL exitpgm(achain$): CHAIN achain$
					END IF
	IF B% = 44 THEN
					achain$ = "DSINV01D"
					ENVIRON "PARM2$=PRE..."
					ENVIRON "DB.OR.CR$=DB"
					CALL exitpgm(achain$): CHAIN achain$
	END IF


	IF B% = 91 THEN achain$ = "dspic01": CALL exitpgm(achain$): CHAIN achain$'ajd
	IF B% = 92 THEN
		CALL printpslip(updwn%)
		END IF
	IF B% = 93 THEN achain$ = "dsrep02": CALL exitpgm(achain$): CHAIN achain$
	IF B% = 94 THEN achain$ = "dsrep03": CALL exitpgm(achain$): CHAIN achain$
	IF B% = 95 THEN
					achain$ = "DSREP02"
					ENVIRON "PARM2$=PRE..."
					ENVIRON "DB.OR.CR$=DB"
					CALL exitpgm(achain$): CHAIN achain$
	END IF

GOTO getopt

SUB printpslip (updwn%)
	ON LOCAL ERROR RESUME NEXT
	PCOPY 0, 1
	LOCATE 1, 1

	IF DIR$("PSLIP.PIC") > "" THEN


		IF DIR$("PSLIP.PRT") > "" THEN
			SHELL "ERASE PSLIP.PRT"
		END IF


		SHELL "RENAME PSLIP.PIC PSLIP.PRT"

		SHELL "COPY PSLIP.PRT LPT1"
	END IF

	PCOPY 1, 0

END SUB
