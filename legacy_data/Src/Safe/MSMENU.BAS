	' M S M E N U
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "MENUTP"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	'$INCLUDE: '\tpmanuf\src\forhed.inc'
	DIM sets$(9)
	FOR i% = 1 TO 9
		sets$(i%) = MID$(setsk$, i% * 4 - 2, 3)
	NEXT


	GET #36, 1, msmisc
	cca$ = msmisc.cc$
	CLOSE
	parm3$ = ENVIRON$("PARM3$"): IF MID$(parm3$, 1, 1) <> "." THEN cca$ = parm3$

	CALL SETUP(cca$)
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : COLOR 2, 0
	COLOR 4, 0
	LOCATE 4, 21: PRINT " M A N U F A C T U R I N G   S Y S T E M"
	LOCATE 5, 21: PRINT "========================================="
	COLOR 2, 0
	LOCATE 6, 5: PRINT "1.....Raw material file"
	LOCATE 8, 5: PRINT "2.....Formulation file"
	LOCATE 10, 5: PRINT "3.....Tinters file"
	LOCATE 12, 5: PRINT "4.....Print a formula"
	LOCATE 14, 5: PRINT "5.....Batch processing"
	LOCATE 16, 5: PRINT "6.....Batch reporting"
	LOCATE 6, 45: PRINT "7.....History formulations"
	LOCATE 8, 45: PRINT "8.....List raw materials"
	LOCATE 10, 45: PRINT "9.....Print price lists"
	LOCATE 12, 45: PRINT "10....Change class descriptions"
	LOCATE 14, 45: PRINT "11....Change mark-up values"
	LOCATE 16, 45: PRINT "12....Raw material stocktake."
	LOCATE 18, 45: PRINT "13....Condition types"
	LOCATE 20, 45: PRINT "14....Set file system"
	'>>>>> OPTIONS
getopt: LOCATE 22, 27: PRINT "Option..> ";
	a$ = "": updwn% = 1: LOCATE 22, 36
	CALL inpnew(a$, 102!, updwn%, "59,13" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
	b% = VAL(a$)
	IF b% = 1 THEN ACHAIN$ = "msupd01": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'IF b% = 2 THEN achain$ = "msupd02d": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 2 THEN ACHAIN$ = "msupd02d": ENVIRON "TINTS.OR.A-F$=A - F": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 3 THEN ACHAIN$ = "msupd02d": ENVIRON "TINTS.OR.A-F$=Tints": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 4 THEN ACHAIN$ = "msbch01p": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 5 THEN ACHAIN$ = "msbch02": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 6 THEN ACHAIN$ = "msbch04": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 7 THEN ACHAIN$ = "mshst01": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 8 THEN ACHAIN$ = "msrep02": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 9 THEN ACHAIN$ = "ccost02": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 10 THEN ACHAIN$ = "mscls02": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 11 THEN ACHAIN$ = "msmkp01": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 12 THEN ACHAIN$ = "strep01": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 13 THEN ACHAIN$ = "mstyp01": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$

	IF b% = 14 THEN
		a$ = ""
		LOCATE 23, 2: PRINT setsD$;
		LOCATE 22, 27: PRINT "Set.....> ";
		LOCATE 22, 36: CALL inpnew(a$, 110!, updwn%, "13,59")
		a$ = MID$(RTRIM$(UCASE$(a$)), 1, 3)
		a% = 0
		FOR i% = 1 TO 9
			IF a$ = sets$(i%) THEN a% = i%: EXIT FOR
		NEXT

		IF a% > 0 THEN
			ENVIRON "PARM3$=" + a$
		ELSE
			ENVIRON "PARM3$=......"
		END IF
		CLOSE
		RUN
	END IF

	GOTO getopt
