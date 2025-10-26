	'///////////////////////////////////////////////////////////////////////
	'////    R E P R I N T   A N   I N V O I C E /  C R E D I T
	'///////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "DSMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	RESET
	CALL setup("REPRINT AN INVOICE/CREDIT/STATEMENT")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1 - Exit";
	COLOR 2, 0
	LOCATE 6, 29: PRINT "1.....Invoice to form"
	LOCATE , 29: PRINT "2.....Invoice to sheet"
	LOCATE , 29: PRINT "3.....Invoice directory"
	LOCATE , 29: PRINT
	LOCATE , 29: PRINT "4.....Credit to form"
	LOCATE , 29: PRINT "5.....Credit to sheet"
	LOCATE , 29: PRINT "6.....Credit directory"
	LOCATE , 29: PRINT
	LOCATE , 29: PRINT "7....Cash Sale to form"
	LOCATE , 29: PRINT "9....Page Eject"
	LOCATE , 29: PRINT
	LOCATE , 29: PRINT "10....Print Statement to Sheet"
	LOCATE , 29: PRINT "11....Statement Directory"

	'>>>>> OPTIONS
GETOPT:
	LOCATE 20, 29: PRINT SPACE$(40)
	A$ = ""
	LOCATE 20, 27: PRINT "  Option..> "; CHR$(fnh);
	CALL inpnew(A$, 102!, updwn%, "59,13,17,23,30,31,32,33,46,50" + alt$): GOSUB alt
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	opt% = VAL(A$)
	IF opt% = 1 OR opt% = 2 OR opt% = 4 OR opt% = 5 OR opt% = 7 THEN
		GOSUB get.num
		IF updwn% = 59 THEN GOTO GETOPT
		IF updwn% = 60 THEN GOTO GETOPT
		END IF
	'///////////////////////////////////////
	PCOPY 0, 1
	num$ = "j:\tpmanuf\invoices\" + num$
	IF opt% = 1 THEN
		num$ = num$ + ".INS"
		SHELL "COPY " + num$ + " LPT2"
		END IF
	IF opt% = 2 THEN
		num$ = num$ + ".INS"
		SHELL "COPY " + num$ + " LPT1"
		LPRINT CHR$(12)
		END IF
	IF opt% = 3 THEN
		PCOPY 0, 1
		CLS
		SHELL "DIR *.INS | SORT | MORE"
		x$ = INPUT$(1)
		PCOPY 1, 0
		END IF
	IF opt% = 4 THEN
		num$ = num$ + ".CRS"
		SHELL "COPY " + num$ + " LPT2"
		END IF
	IF opt% = 5 THEN
		num$ = num$ + ".CRS"
		SHELL "COPY " + num$ + " LPT1"
		LPRINT CHR$(12)
		END IF
	IF opt% = 6 THEN
		PCOPY 0, 1
		CLS
		SHELL "DIR *.CRS | SORT | MORE"
		x$ = INPUT$(1)
		PCOPY 1, 0
		END IF
	IF opt% = 7 THEN
		num$ = num$ + ".INS"
		SHELL "COPY " + num$ + " LPT3"
		END IF
	IF opt% = 9 THEN
		LPRINT CHR$(12)
		PCOPY 1, 0
		END IF
	IF opt% = 10 THEN
	A$ = ""
		LOCATE 20, 27: PRINT "Enter Customer..> "; A$
		LOCATE 20, 44: CALL inpnew(A$, 105!, updwn%, "13,59,60")
		num$ = A$ + ".PRN"
		IF updwn% = 59 THEN GOTO GETOPT 'EXIT DO
		IF updwn% = 60 THEN GOTO GETOPT 'EXIT DO
		'/// search ////
		LOCATE 21, 45
		SHELL "COPY " + num$ + " LPT1"
		LOCATE 21, 45: PRINT "                        "
		END IF
	IF opt% = 11 THEN
		PCOPY 0, 1
		CLS
		SHELL "DIR *.PRN | SORT | MORE"
		x$ = INPUT$(1)
		PCOPY 1, 0
		END IF

GOTO GETOPT
'///////////////////////////////////////////////////////////////////////
'////
'///////////////////////////////////////////////////////////////////////
get.num:
	A$ = ""
	DO
		LOCATE 20, 29: PRINT "Enter number..> "; CHR$(fnh);
		CALL inpnew(A$, 8!, updwn%, "13,59,60")
		A$ = STR$(VAL(A$)): MID$(A$, 1, 1) = "0"
		num$ = "00000000" + A$
		num$ = RIGHT$(num$, 8)
		IF updwn% = 59 THEN EXIT DO
		IF updwn% = 60 THEN EXIT DO
		'/// search ////
		IF VAL(num$) = 0 THEN
		IF opt% = 1 OR opt% = 2 THEN
			PCOPY 0, 1
			CLS
			SHELL "DIR *.INS | SORT | MORE"
			x$ = INPUT$(1)
			PCOPY 1, 0
			END IF
		IF opt% = 4 OR opt% = 5 THEN
			PCOPY 0, 1
			CLS
			SHELL "DIR *.CRS | SORT | MORE"
			x$ = INPUT$(1)
			PCOPY 1, 0
			END IF
			END IF
		LOOP UNTIL VAL(num$) > 0
RETURN

