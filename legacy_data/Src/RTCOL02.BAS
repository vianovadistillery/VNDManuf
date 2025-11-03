	'>>>>>>>>>>>>>>>>>>>>>>>> RTCOL02 - Tint bases. <<<<<<<<<<<<<<<<<<<<<<<<<
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	pgm$ = "ACMENU"
		OPEN "colbase.DAT" FOR RANDOM AS #1 LEN = 15
	FIELD #1, 1 AS BSCODE$, 12 AS BDESC$, 2 AS BPERC$
	GET #1: IF EOF(1) THEN GOSUB setfile
	CALL setup("T I N T  B A S E S ")
	COLOR 8, 3: LOCATE 25, 1: PRINT SPACE$(80); : LOCATE 1, 1
570 COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : LOCATE 25, 71: PRINT CHR$(24); CHR$(25); "-Move";
	COLOR 2, 0
	updwn% = 0
	k% = 1: GOSUB dsply
4200 LOCATE 3, 23: PRINT "Enter base number..> "
	LOCATE 3, 43: CALL inpnew(a$, 102!, updwn%, "13,59,72,73,80,81" + alt$): GOSUB alt
	IF updwn% = 59 THEN CLOSE : call exitpgm(pgm$):CHAIN pgm$
	IF updwn% = 72 OR updwn% = 73 THEN k% = 1: GOSUB dsply
	IF updwn% = 80 OR updwn% = 81 THEN k% = 50: GOSUB dsply
	 b$ = "  ": LSET b$ = a$: b% = VAL(b$)
	IF b% < 1 OR b% > 99 THEN 4200
	GET #1, b%
	LOCATE 3, 23: PRINT "Enter base description..>"
	a$ = BDESC$
	LOCATE 3, 48: CALL inpnew(a$, 112!, updnwn%, "13,59" + alt$): GOSUB alt
	IF updwn% = 59 THEN GOTO 4200
	LSET BDESC$ = a$
	PUT #1, b%
	LOCATE 3, 23: PRINT CHR$(fne)
	 k% = 50: IF b% < 50 THEN k% = 1
	GOSUB dsply
	GOTO 4200
	'///////////////////////////////////////////////////////////////////////
	'//// DISLPAY THE PAGE
	'///////////////////////////////////////////////////////////////////////
dsply:
	LOCATE 5, 1: COLOR 2, 0
	FOR i% = k% TO k% + 16: j% = i% + 17: kk% = j% + 17
	GET #1, i%: a$ = BDESC$
	GET #1, j%: b$ = BDESC$
	IF kk% < 100 THEN GET #1, kk%: c$ = BDESC$
	LOCATE , 2: PRINT USING "### \                    \### \                    \"; i%; a$; j%; b$;
	IF kk% < 100 THEN PRINT USING "### \                    \"; kk%; c$;
	IF kk% > 99 THEN PRINT CHR$(fne);
	PRINT
	NEXT
	RETURN
	'///////////////////////////////////////////////////////////////////////
	'//// CLEAR 99 RECORDS
	'///////////////////////////////////////////////////////////////////////
setfile:
	FOR i% = 1 TO 99
		LSET BSCODE$ = " "
		LSET BDESC$ = SPACE$(99)
		LSET BPERC$ = MKI$(0)
		PUT #1, i%
		NEXT
	RETURN


