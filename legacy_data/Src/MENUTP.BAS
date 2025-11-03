	'>>>>>>>>>>>>>>>>>>> MENUTP - MASTER DIRECTORY <<<<<<<<<<<<<<<<<<<<<<<<<
'.dc - Complete
	'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "SIGNON"
	''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'

	GET #36, 1, msmisc
	cca$ = msmisc.cc$
	CLOSE

	parm3$ = ENVIRON$("PARM3$"): IF MID$(parm3$, 1, 1) <> "." THEN cca$ = parm3$
again:
	CALL setup(cca$)
	CALL prtbtm(" F1-Exit")
	COLOR 4, 0
	LOCATE 4, 24: PRINT " M A S T E R    D I R E C T O R Y "
	LOCATE 5, 24: PRINT "=================================="
	COLOR 2, 0
	LOCATE 7, 1
	LOCATE , 24: PRINT " 1...Manufacturing menu."
	LOCATE , 24: PRINT " 2...Accessory processing."
	LOCATE , 24: PRINT " 3...Creditors system."
	LOCATE , 24: PRINT " 4...Debtors system."
	LOCATE , 24: PRINT " 5...Accounting system."
	LOCATE , 24: PRINT " 6...(STOP) Product label print."
	LOCATE , 24: PRINT " 7...(STOP) General label print."
	LOCATE , 24: PRINT " 8...Quality System."
	LOCATE , 24: PRINT " 9...Page Eject."
	LOCATE , 24: PRINT "10...(STOP) Asset register."
	LOCATE , 24: PRINT "97...Change password."
	LOCATE , 24: PRINT "98...Change date and time."
	LOCATE , 24: PRINT "99...Shell to DOS."
	'>>>>> OPTIONS
getopt: LOCATE 21, 27: PRINT "Option..> ";
	a$ = "": updwn% = 1: LOCATE 21, 36
	CALL inpnew(a$, 102!, updwn%, "13,59" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
	b% = VAL(a$)
	IF b% = 1 THEN ACHAIN$ = "MSMENU": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 2 THEN ACHAIN$ = "ACMENU": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 3 THEN ACHAIN$ = "CSMENU": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 4 THEN ACHAIN$ = "DSMENU": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 5 THEN ACHAIN$ = "ASAUD01": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 6 THEN ACHAIN$ = "LBLPROD": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 7 THEN ACHAIN$ = "LBLGNRL": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 8 THEN ACHAIN$ = "QSMENU": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 9 THEN LPRINT CHR$(12)
	'IF b% = 10 THEN achain$ = "ASSET01": CALL exitpgm(achain$): CHAIN achain$
	IF a$ = "BM" THEN ACHAIN$ = "BMENU": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 97 THEN ACHAIN$ = "PWORD": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	IF b% = 98 THEN CLS : SHELL "date": CLS : SHELL "time": GOTO again
	IF b% = 99 THEN CLS : SHELL: GOTO again
	IF updwn% = 27 THEN
		IF sysnum% = 0 OR msmisc.special$ = "D" THEN ACHAIN$ = "BMENU": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
		END IF
	GOTO getopt
