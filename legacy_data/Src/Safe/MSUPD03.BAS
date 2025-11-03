   'MSUPD03 - Update raw matrial group description.
   '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'.dc - Complete
	 OPEN "msrmgp.dat" FOR RANDOM AS #7 LEN = 22
	 FIELD #7, 22 AS RMGROUP$
   '>>>>>  U P D A T E    A    C O M M E N T
   CALL setup(" UPDATE RAW MATERIAL GROUP DESCRIPTION")
   KEY 7, "f" + CHR$(13): KEY 8, "b" + CHR$(13)
   COLOR 0, 3: LOCATE 25, 1: PRINT "F1 - Return.  F7 - Roll Foward.  F8 - Roll Backward.";
   COLOR 2, 0
   k% = 1
   GOTO 220

110 LOCATE 4, 23: PRINT "Enter group number..>"; : INPUT ; "", a$
	IF a$ = "f" THEN k% = 50: GOTO 220
	IF a$ = "b" THEN k% = 1: GOTO 220
	b$ = "  ": LSET b$ = a$: b% = VAL(b$)
	IF b% < 1 OR b% > 99 THEN CLOSE : bpgm$ = "msmenu": CALL exitpgm(bpgm$): CHAIN bpgm$
	LOCATE 4, 63: PRINT "<-"
	LOCATE 4, 23: PRINT "Enter new group..>"; : LINE INPUT ; "", a$
	IF a$ = "END" THEN 110
	IF LEN(a$) > 0 THEN LSET RMGROUP$ = a$
	PUT #7, b%
	k% = 50: IF b% < 50 THEN k% = 1
220 LOCATE 5, 1: FOR i% = k% TO k% + 16: j% = i% + 17: kk% = j% + 17
	GET #7, i%: a$ = RMGROUP$
	GET #7, j%: b$ = RMGROUP$
	IF kk% < 100 THEN GET #7, kk%: c$ = RMGROUP$
	LOCATE , 2
	PRINT USING "### \                    \### \                   \"; i%; a$; j%; b$;
	IF kk% < 100 THEN PRINT USING "### \                    \"; kk%; c$;
	IF kk% > 99 THEN PRINT SPACE$(79);
	PRINT : NEXT
