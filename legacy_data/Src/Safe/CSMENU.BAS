	'>>>>>>>>>>>>>>>> CSMENU.BAS - CREDITORS SYSTEM MENU <<<<<<<<<<<<<<<<<<<
	'************** ALSO DSMENU.BAS - BOTH FROM ASMENU.BAS *****************
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "MENUTP"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
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
	CONST acctype$ = "CI"'Debtors invoice
	CONST acctaxtype$ = "CT"'- Sales tax portion of invoice.
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	GET #36, 1, msmisc
	cca$ = msmisc.cc$
	CLOSE
	CALL setup(cca$)
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : COLOR 2, 0
	x1 = 7: x2 = 47: y = 8
	COLOR 4, 0
	LOCATE 4, 22: PRINT "   C R E D I T O R S    S Y S T E M  "'********
	LOCATE 5, 22: PRINT " ===================================="'********
	COLOR 2
	LOCATE 6, 26: PRINT "1....Creditors invoice entry."
	LOCATE , 26: PRINT "2....Creditors payment entry."
	LOCATE , 26: PRINT "3....Creditors file maintainance."
	LOCATE , 26: PRINT "4....Creditors label listing."
	LOCATE , 26: PRINT "5....Creditors address listing."
	LOCATE , 26: PRINT "6....Pick up address."
	LOCATE , 26: PRINT "8....Stand alone invoice"
	LOCATE , 26: PRINT "9....Page eject."
	LOCATE , 25: PRINT "10....Print Statements."
	LOCATE , 25: PRINT "11....Print Selected Statement."
	LOCATE , 26: PRINT ""
	LOCATE , 25: PRINT "31....Creditors tools"
	LOCATE , 25: PRINT "32....Print Aged Creditors Report."
	LOCATE , 25: PRINT "33....Load/unload opening balances"
	LOCATE , 25: PRINT
	'>>>>> OPTIONS
getopt: LOCATE 21, 27: PRINT "Option..> ";
	a$ = "": updwn% = 1: LOCATE 21, 36
	CALL inpnew(a$, 102!, updwn%, "59,13" + ALT$): GOSUB ALT
		IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	b% = VAL(a$)
	IF b% = 1 THEN achain$ = "csinv01d": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 2 THEN achain$ = "cspay01": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 3 THEN
					achain$ = "XXWHO01"
					ENVIRON "DB.OR.CR$=CR"
					CALL exitpgm(achain$): CHAIN achain$
					END IF
	IF b% = 4 THEN achain$ = "cslbl01": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 5 THEN
					achain$ = "xxlbl02"
					ENVIRON "DB.OR.CR$=CR"
					CALL exitpgm(achain$): CHAIN achain$
					END IF
	IF b% = 6 THEN achain$ = "dspic01": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 8 THEN
					achain$ = "dsinv03d"
					ENVIRON "DB.OR.CR$=CR"
					CALL exitpgm(achain$): CHAIN achain$
					END IF

	IF b% = 9 THEN LPRINT CHR$(12)

	IF b% = 10 THEN
					CALL sndmsg("About to print Statements. Continue (Y/N)..>")
					dft$ = "N"
					DO
						LOCATE 24, 48
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
	IF b% = 11 THEN
					CALL sndmsg("                     Enter Account Code..>")
					acc$ = "?????mm"
					LOCATE 24, 46
					CALL inpnew(acc$, 107!, updwn%, "13,59")
					dft$ = UCASE$(dft$)
					IF updwn% = 59 THEN acc$ = "     "
					CALL sndmsg("")

					IF acc$ > " " THEN
						LOCATE 2, 1
						SHELL "copy \statemen\" + acc$ + ".prn lpt1"
					END IF
	END IF


	IF b% = 31 THEN
					achain$ = "ASAUD03"
					ENVIRON "DB.OR.CR$=CR"
					CALL exitpgm(achain$): CHAIN achain$
					END IF
	IF b% = 32 THEN
					achain$ = "ASAUD04"
					ENVIRON "DB.OR.CR$=CR"
					CALL exitpgm(achain$): CHAIN achain$
					END IF
	IF b% = 33 THEN
					achain$ = "asaud02"
					ENVIRON "DB.OR.CR$=CR"
					CALL exitpgm(achain$): CHAIN achain$
					END IF
GOTO getopt
