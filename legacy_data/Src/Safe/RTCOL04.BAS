	'>>>>>>>>>>>>>>>>>>>>>>> RTCOL04 - Colour card <<<<<<<<<<<<<<<<<<<<<<<<<<
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	pgm$ = "ACMENU"
		OPEN "colcard.DAT" FOR RANDOM AS #1 LEN = 22
 FIELD #1, 22 AS CCDESC$
	GET #1: IF EOF(1) THEN GOSUB setfile
	CALL setup("C O L O U R   C A R D")
	'COLOR 8, 3: LOCATE 25, 1: PRINT SPACE$(80); : LOCATE 1, 1
570 'COLOR 8, 3: LOCATE 24, 21: PRINT ; "f1 - end.                f7/f8 - roll.";
	 COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : LOCATE 25, 71: PRINT CHR$(24); CHR$(25); "-Move";
	COLOR 2, 0
	k% = 1: GOSUB dsply
4200 LOCATE 3, 23: PRINT "Enter card number..> "
	LOCATE 3, 43: CALL inpnew(a$, 102!, updwn%, "13,59,72,73,80,81" + alt$): GOSUB alt
	IF updwn% = 59 THEN CLOSE : call exitpgm(pgm$):CHAIN pgm$
	IF updwn% = 72 OR updwn% = 73 THEN k% = 1: GOSUB dsply
	IF updwn% = 80 OR updwn% = 81 THEN k% = 50: GOSUB dsply
	 b$ = "  ": LSET b$ = a$: b% = VAL(b$)
	IF b% < 1 OR b% > 99 THEN 4200
	GET #1, b%
	LOCATE 3, 23: PRINT "Enter card description..>"
	a$ = CCDESC$
	LOCATE 3, 48: CALL inpnew(a$, 122!, updnwn%, "13,59" + alt$): GOSUB alt
	IF updwn% = 59 THEN GOTO 4200
	LSET CCDESC$ = a$
	PUT #1, b%
	LOCATE 3, 23: PRINT CHR$(fne)
	k% = 50: IF b% < 50 THEN k% = 1
	GOSUB dsply
	GOTO 4200
	'////////////////////////////////////////////////////////////////////////
	'//// DISLPAY THE PAGE
	'////////////////////////////////////////////////////////////////////////
dsply:
	LOCATE 5, 1: COLOR 2, 0
	FOR i% = k% TO k% + 16: j% = i% + 17: kk% = j% + 17
	GET #1, i%: a$ = CCDESC$
	GET #1, j%: b$ = CCDESC$
	IF kk% < 100 THEN GET #1, kk%: c$ = CCDESC$
	LOCATE , 2: PRINT USING "### \                    \### \                    \"; i%; a$; j%; b$;
	IF kk% < 100 THEN PRINT USING "### \                    \"; kk%; c$;
	IF kk% > 99 THEN PRINT CHR$(fne);
	PRINT : NEXT
	 GOTO 4200
	'////////////////////////////////////////////////////////////////////////
	'//// CLEAR 99 RECORDS
	'////////////////////////////////////////////////////////////////////////
setfile:
	FOR i% = 1 TO 99
		LSET bscode$ = " "
		LSET bdesc$ = SPACE$(99)
		LSET bperc$ = MKI$(0)
		PUT #1, i%
		NEXT
	RETURN

