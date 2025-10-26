'>>>>>>>>>>>>>>>>>>>>>> B08 -  MISCELLANEOUS FILE <<<<<<<<<<<<<<<<<<<<<<<<
'.dc - Complete
	panic$ = CHR$(79) + CHR$(5) + CHR$(72) + CHR$(83) + CHR$(78) + CHR$(70)
	DIM order%(6)
	b08 = 2.3
	KEY 1, "^"
	FOR i% = 1 TO 6: READ order%(i%): NEXT
	DATA 3,6,5,1,4,2
	OPEN "msmisc.msf" FOR RANDOM SHARED AS #8 LEN = 128
	FIELD #8, 2 AS QTYF$, 2 AS BCHNO$, 2 AS BCHOFF$, 40 AS CC$, 6 AS CCDE$, 20 AS max$, 10 AS olddate$, 2 AS version$, 1 AS special$, 1 AS inside$, 2 AS bchist$
	FIELD #8, 52 AS FIL$, 2 AS MAX1$, 2 AS MAX2$, 2 AS MAX3$, 2 AS MAX4$, 2 AS max5$, 2 AS max6$, 2 AS max7$, 2 AS max8$, 2 AS max9$, 2 AS max10$
	FIELD #8, 88 AS FIL$, 1 AS TRDISC$, 2 AS SYSUNT$, 2 AS SYSNUM$
	FIELD #8, 93 AS FIL$, 1 AS PRTHI$, 1 AS PRTDB$, 1 AS PRTSUB$, 1 AS PRTSUP$, 1 AS prthi1$, 20 AS filler$
140  CLS
	GET #8, 1
	QTYF% = CVI(QTYF$)
	BCHNO% = CVI(BCHNO$)
	BCHOFF% = CVI(BCHOFF$): bchist% = CVI(bchist$)
	MAX1 = CVI(MAX1$): MAX2 = CVI(MAX2$): MAX3 = CVI(MAX3$): MAX4 = CVI(MAX4$)
	max5 = CVI(max5$): max6 = CVI(max6$): max7 = CVI(max7$): max8 = CVI(max8$)
	max9 = CVI(max9$): max10 = CVI(max10$): SYSNUM% = CVI(SYSNUM$)
	version = CVI(version$) / 10
	IF SYSNUM% = 0 THEN LSET special$ = "D"
	LOCATE 3, 1: COLOR 4: PRINT "SYSTEM HEADER UTILITY.    Version:"; b08
	LOCATE 5, 1: COLOR 3
	IF special$ = "D" THEN code$ = CCDE$: GOSUB 1060: PRINT "System password:"; pword$
				  PRINT "Number of formulas on file  QTYF% "; QTYF%
				  PRINT "Last batch number          BCHNO% "; BCHNO%
				  PRINT "Last batch number of old"
				  PRINT "file. Batch offset        BCHOFF% "; BCHOFF%
				  PRINT "Number of hist records    BCHIST% "; bchist%
				  PRINT "Company name                  CC$."; CC$; "."
				  PRINT "Date system last used    OLDDATE$ "; olddate$
				  PRINT "version number of sys    VERSION$ "; version
				  PRINT "ASCII of trade disc flg   TRDISC$ "; TRDISC$
				  PRINT "System costing unit       SYSUNT$ "; SYSUNT$
				  PRINT "Unique system number      SYSNUM% "; SYSNUM%
		 COLOR 2: PRINT "Printer controls ASCII    ": COLOR 3
				  PRINT "DB/print  DB/Width   Sub script   Super script DB/With off"
				  PRINT ASC(PRTHI$); "     "; ASC(PRTDB$); "         "; ASC(PRTSUB$); "             "; ASC(PRTSUP$); "         "; ASC(prthi1$)
	 COLOR 2: PRINT "                                    Supp   form   Rmat   Hist   Accs"
		  COLOR 3
		  PRINT USING "Maxcounters            MAX (1-5)   #####  #####  #####  #####  #####"; MAX1; MAX2; MAX3; MAX4; max5
	 COLOR 2: PRINT "                                    Type   Cust  F/HIS   XXXX   Ledg": COLOR 3
		  PRINT USING "                       MAX (6-10)  #####  #####  #####  #####  #####"; max6; max7; max8; max9; max10
	LOCATE 25, 1: PRINT " "; "C"; " To change or F1 to exit.";
	IF special$ = "D" THEN PRINT " P-change password. to 'hello'";
	LOCATE 1, 1
470  x$ = INKEY$: IF x$ <> "^" AND x$ <> "c" AND x$ <> "C" AND x$ <> "P" AND x$ <> "p" THEN 470
	IF x$ = "p" OR x$ = "P" AND special$ = "D" THEN LSET CCDE$ = panic$: PUT #8, 1: GOTO 140
	CLS
	INPUT "New qtyf%", x$: b$ = "   ": LSET b$ = x$: b% = VAL(b$)
	IF LEN(x$) > 0 THEN LSET QTYF$ = MKI$(b%)
	INPUT "New bchno%", x$: b$ = "   ": LSET b$ = x$: b% = VAL(b$)
	IF LEN(x$) > 0 THEN LSET BCHNO$ = MKI$(b%)
	INPUT "New bchoff%", x$: b$ = "    ": LSET b$ = x$: b% = VAL(b$)
	IF LEN(x$) > 0 THEN LSET BCHOFF$ = MKI$(b%)
	INPUT "New bchist%", x$: b$ = "    ": LSET b$ = x$: b% = VAL(b$)
	'save "b08"
	IF LEN(x$) > 0 THEN LSET bchist$ = MKI$(b%)
	PRINT "       ."; SPACE$(40); "."; : LOCATE , 1: LINE INPUT "New desc", x$
	IF LEN(x$) > 0 THEN LSET CC$ = x$
	LINE INPUT "New date (MM-DD-YYYY)..>", d$
	IF LEN(d$) > 0 THEN LSET olddate$ = d$
	LINE INPUT "New version number *10.>", a$
	IF LEN(a$) > 0 THEN b$ = "1000": LSET b$ = a$: b% = VAL(b$): LSET version$ = MKI$(b%)
	LINE INPUT "New ASCII trade discount flag..>", a$
	IF LEN(a$) > 0 THEN LSET TRDISC$ = a$
	LINE INPUT "Enter new number on history file.>", a$
	IF LEN(a$) > 0 THEN b$ = "1000": LSET b$ = a$: b% = VAL(b$): LSET bchist$ = MKI$(b%)
	LINE INPUT "max1 .>", a$
	IF LEN(a$) > 0 THEN b$ = "1000": LSET b$ = a$: b% = VAL(b$): LSET MAX1$ = MKI$(b%)
	LINE INPUT "max2 .>", a$
	IF LEN(a$) > 0 THEN b$ = "1000": LSET b$ = a$: b% = VAL(b$): LSET MAX2$ = MKI$(b%)
	LINE INPUT "max3 .>", a$
	IF LEN(a$) > 0 THEN b$ = "1000": LSET b$ = a$: b% = VAL(b$): LSET MAX3$ = MKI$(b%)
	LINE INPUT "max4 .>", a$
	IF LEN(a$) > 0 THEN b$ = "1000": LSET b$ = a$: b% = VAL(b$): LSET MAX4$ = MKI$(b%)
	LINE INPUT "max5 .>", a$
	IF LEN(a$) > 0 THEN b$ = "1000": LSET b$ = a$: b% = VAL(b$): LSET max5$ = MKI$(b%)
	LINE INPUT "max6 .>", a$
	IF LEN(a$) > 0 THEN b$ = "1000": LSET b$ = a$: b% = VAL(b$): LSET max6$ = MKI$(b%)
	LINE INPUT "max7 .>", a$
	IF LEN(a$) > 0 THEN b$ = "1000": LSET b$ = a$: b% = VAL(b$): LSET max7$ = MKI$(b%)
	LINE INPUT "max8 .>", a$
	IF LEN(a$) > 0 THEN b$ = "1000": LSET b$ = a$: b% = VAL(b$): LSET max8$ = MKI$(b%)
	LINE INPUT "max9 .>", a$
	IF LEN(a$) > 0 THEN b$ = "1000": LSET b$ = a$: b% = VAL(b$): LSET max9$ = MKI$(b%)
	LINE INPUT "max10.>", a$
	IF LEN(a$) > 0 THEN b$ = "1000": LSET b$ = a$: b% = VAL(b$): LSET max10$ = MKI$(b%)
	LINE INPUT "System unit.>", a$
	IF LEN(a$) > 0 THEN LSET SYSUNT$ = a$
	LINE INPUT "SYSNUM...>", a$
	IF LEN(a$) > 0 THEN b$ = "000000": LSET b$ = a$: b% = VAL(b$): LSET SYSNUM$ = MKI$(b%)
	LINE INPUT "Printer double print.(ascii)..>", a$
	IF LEN(a$) > 0 THEN b$ = "000": LSET b$ = a$: b% = VAL(b$): LSET PRTHI$ = CHR$(b%)
	LINE INPUT "Printer double width.(ascii)..>", a$
	IF LEN(a$) > 0 THEN b$ = "000": LSET b$ = a$: b% = VAL(b$): LSET prtdw$ = CHR$(b%)
	LINE INPUT "Printer sub script...(ascii)..>", a$
	IF LEN(a$) > 0 THEN b$ = "000": LSET b$ = a$: b% = VAL(b$): LSET PRTSUB$ = CHR$(b%)
	LINE INPUT "Printer super script...(ascii)..>", a$
	IF LEN(a$) > 0 THEN b$ = "000": LSET b$ = a$: b% = VAL(b$): LSET PRTSUP$ = CHR$(b%)
	 LINE INPUT "Printer double width off...(ascii)..>", a$
	 IF LEN(a$) > 0 THEN b$ = "000": LSET b$ = a$: b% = VAL(b$): LSET prthi1$ = CHR$(b%)
	 PUT #8, 1
	 GOTO 140
	 '>>>>> R O U T I N E   T O   D E C O D E    P A S S W O R D
1060  pword$ = "123456": a$ = "1"
	  FOR i% = 1 TO 6
		  LSET a$ = MID$(code$, order%(i%), 1)
		  a% = ASC(a$) + &O41 - i%: IF a% < 1 OR a% > 127 THEN a% = ASC("?")
		  LSET a$ = CHR$(a%)
		  MID$(pword$, i%, 1) = RIGHT$(a$, 1)
		  NEXT
RETURN

