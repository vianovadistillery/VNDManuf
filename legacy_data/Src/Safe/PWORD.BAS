' P W O R D - Change the system password
'////////////////////////////////////////
'.dc - Complete
	'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	DIM order%(10)
	ON ERROR GOTO 700
	RESET
	pgm$ = "MENUTP"
	pgmerr$ = "SIGNON"
'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	GET #36, 1
	GOTO 240
80 '>>>>> ROUTINE TO DECODE PASSWORD
	pword$ = "123456": a$ = "1"
	FOR i% = 1 TO 6
	  LSET a$ = MID$(code$, order%(i%), 1)
	  a% = ASC(a$) + &O41 - i%: LSET a$ = CHR$(a%)
	  MID$(pword$, i%, 1) = RIGHT$(a$, 1)
	NEXT
	RETURN
160 '>>>>> ROUTINE TO ENCODE PASSWORD
	 a$ = "1": pword$ = "123456"
	 FOR i% = 1 TO 6
		 LSET a$ = MID$(newword$, i%, 1)
	  a% = ASC(a$) - &O41 + i%: LSET a$ = CHR$(a%)
	  MID$(pword$, order%(i%), 1) = a$
	NEXT
	RETURN
	'/////////////////////////////////////////////////////////////
240 '>>>>>  M A I N L I N E
	'/////////////////////////////////////////////////////////////
	CALL setup("CHANGE SYSTEM PASSWORD")
	COLOR 8, 3: LOCATE 25, 31: PRINT "F1 - Exit"; ' CHR$(fne)
	COLOR 2, 0
	FOR i% = 1 TO 6: READ order%(i%): NEXT
	DATA 3,6,5,1,4,2
	'* Is he authorised to change password
	IF special$ = "D" THEN 450
	cnt% = 0
350 LOCATE 5, 25: PRINT "Enter password..> "; CHR$(FNH);
	a$ = ""
	CALL inpnew(a$, 106!, updwn%, "13,59" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL EXITPGM(pgm$): CHAIN pgm$
	IF LEN(a$) < 2 THEN 350
	newword$ = "      ": LSET newword$ = a$
	GOSUB 160
	GET #36, 1
	IF cnt% > 2 THEN CALL EXITPGM(pgmerr$): CHAIN pgmerr$
	IF ccde$ <> pword$ THEN COLOR 14: LOCATE 21, 2: PRINT "Not authorised to update password. Try again.": COLOR 2: cnt% = cnt% + 1: GOTO 350
	LOCATE 21, 2: PRINT CHR$(FNE)
450 '* Continue
460 LOCATE 11, 23: PRINT "Enter password..> "; CHR$(FNH);
	a$ = ""
	CALL inpnew(a$, 106!, updwn%, "13,59" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL EXITPGM(pgm$): CHAIN pgm$
	IF updwn% = 60 THEN 350
	IF LEN(a$) < 2 THEN 460
	newword$ = SPACE$(6): LSET newword$ = a$
	GOSUB 160'* Encode
	code$ = pword$
	GOSUB 80'* Decode
540 LOCATE 13, 23: PRINT "Enter password..> "; CHR$(FNH);
	b$ = ""
	CALL inpnew(b$, 106!, updwn%, "13,59,60" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL EXITPGM(pgm$): CHAIN pgm$
	IF updwn% = 60 THEN 460
	IF LEN(b$) < 2 THEN 540
	a$ = SPACE$(6): LSET a$ = b$
	IF a$ <> pword$ THEN COLOR 14: LOCATE 21, 2: PRINT "Not the same as previous attempt. Key both again.": COLOR 2: GOTO 460
	GET #36, 1
	LSET msmisc.ccde$ = code$
	PUT #36, 1
	ON ERROR GOTO 0
	LOCATE 16, 23: COLOR 4: PRINT "Password updated"; CHR$(FNE): COLOR 2
	CLOSE
	CALL EXITPGM(pgm$)
	CHAIN pgm$
700 '///////////////////
	COLOR 14: LOCATE 21, 2: PRINT "Password change request denied"
	FOR i = 1 TO 10000: NEXT
	CLOSE :
	CALL EXITPGM(pgmerr$)
	CHAIN pgmerr$
