DECLARE SUB setaudit (n%)
DECLARE SUB checkaudit (updwn%)
DECLARE SUB searchindex (keyin$, chi%, found%)
'.dc - Complete
	'>>>>>>>>>>>>>>>>>> FIMENU - ACCESSORY FILE MENU <<<<<<<<<<<<<<<<<<<<<<<
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "menutp"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	RESET
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\sup.inc'
	'$INCLUDE: '\tpmanuf\src\supx.inc'
	'$INCLUDE: '\tpmanuf\src\cus.inc'
	'$INCLUDE: '\tpmanuf\src\cusx.inc'
	'$INCLUDE: '\tpmanuf\src\who.inc'
	'$INCLUDE: '\tpmanuf\src\whox.inc'
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	DIM SHARED cha%, chb%
	DIM SHARED auditfile$(15), naudit%
	CALL setaudit(naudit%)
	cashonly$ = "M": auditname$ = auditfile$(naudit%)
	'$INCLUDE: '\tpmanuf\src\asaudit.inc'

	GOSUB OPEN.AUDIT
	 IF DB.OR.CR$ = "CR" THEN
		cha% = 45: chb% = 44
		ELSE
		cha% = 23: chb% = 43
	 END IF
	GET #36, 1, msmisc
	cca$ = msmisc.cc
	parm3$ = ENVIRON$("PARM3$"): IF MID$(parm3$, 1, 1) <> "." THEN cca$ = parm3$

START:
	CALL setup(cca$)
	COLOR 8, 3: LOCATE 25, 33: PRINT "F1 - Return.";
	COLOR 4, 0
	LOCATE 4, 20: PRINT "  F I L E   M A I N T A I N A N C E  "
	LOCATE 5, 20: PRINT "====================================="
	COLOR 2, 0
	LOCATE 7
	LOCATE , 13: PRINT "1...Rebuild Accessory Index.      2...Print Accessory Index.       "
	LOCATE , 13: PRINT "3...Rebuild Phone Index.          4...Print Phone List.            "
	LOCATE , 13: PRINT "5...Print Lead File.              6...Check Invoice Sequence.      "
	LOCATE , 13: PRINT ""
	LOCATE , 13: PRINT "7...Condense Audit File.          8...Condense Stock File.         "
	LOCATE , 13: PRINT "9...Rebuild G/L Account Number.   10..Sort/Replace Raw Materials   "
	LOCATE , 13: PRINT "11..Open Cash Drawer.             12..Condense/Repair Order File.  "
	LOCATE , 13: PRINT ""
	LOCATE , 13: PRINT "13..Raw material order list.      14..Install New Index Files.     "
	LOCATE , 13: PRINT "15..Test Network Printers.        16..Rebuild Accessory Indices    "
	LOCATE , 13: PRINT "17..Check Audit files for error.  18..Maintain Help Text           "
	LOCATE , 13: PRINT "19..Check index files for error   20..Lead File maintenance        "
	LOCATE , 13: PRINT "           88..Update stock with sales.  21..Build Rmat alpha index"
	LOCATE , 13: PRINT "           98..B08"
	LOCATE , 13: PRINT "           99..Rebuild Stock File and Index.                       "
	'>>>>> OPTIONS
getopt:
	LOCATE 22, 27: PRINT "Option..>  ";
	a$ = "": updwn% = 1: LOCATE 22, 36
	CALL inpnew(a$, 102!, updwn%, "13,59" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL EXITPGM(apgm$): CLOSE : CHAIN apgm$
	opt% = VAL(a$)
	IF opt% = 2 THEN ACHAIN$ = "ACIDX03L": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	IF opt% = 3 THEN ACHAIN$ = "PHONE1X": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	IF opt% = 4 THEN ACHAIN$ = "PHONEL1": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	IF opt% = 5 THEN
			ACHAIN$ = "XXLBL02"
			ENVIRON "DB.OR.CR$=--"
			CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	END IF
	IF opt% = 6 THEN ACHAIN$ = "ASINCHK": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	IF opt% = 7 THEN ACHAIN$ = "ASAUD50": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	IF opt% = 8 THEN ACHAIN$ = "ACSTK50": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	IF opt% = 9 THEN ACHAIN$ = "ASGLBLD": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	IF opt% = 10 THEN ACHAIN$ = "MSBLD03": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	IF opt% = 11 THEN
			OPEN "com1:" FOR OUTPUT AS #97
			PRINT #97, "Open drawer"
			CLOSE #97
	END IF
	IF opt% = 12 THEN ACHAIN$ = "ASBLD01": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	IF opt% = 13 THEN ACHAIN$ = "MSORD01": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	IF opt% = 14 THEN
		CALL sndmsg("Checking for ACSTKX2.NEW")
		OPEN "acstkx2.new" FOR RANDOM SHARED AS #1
		length = LOF(1)
		CLOSE #1
		IF length = 0 THEN
			KILL "acstkx2.new"
			GOTO getopt
		END IF

		CALL sndmsg("Checking for ACSTKX3.NEW")
		OPEN "acstkx3.new" FOR RANDOM SHARED AS #1
		length = LOF(1)
		CLOSE #1
		IF length = 0 THEN
			KILL "acstkx3.new"
			GOTO getopt
		END IF
		CALL sndmsg("All the ACSTK*.NEW file found")
		'>>- Now we know the ACSTK*.NEW file are present
		CALL BOX(10, 6, 72, 15, 8, 4, 1)
		COLOR 0, 4
		LOCATE 8, 22: PRINT "About to move the new ACSTK indecies"
		LOCATE 9, 22: PRINT "over the existing live files"
		LOCATE 10, 22: PRINT "Continue...(Y/N)..>"; yorn$
		BEEP
		COLOR 2, 0
		yorn$ = "N"
		DO
			LOCATE 10, 41
			CALL inpnew(yorn$, 101!, updwn%, "13,59-60" + ALT$): GOSUB ALT
			IF updwn% = 59 THEN yorn$ = "N"
			IF updwn% = 60 THEN yorn$ = "N"
			yorn$ = UCASE$(yorn$)
			LOOP WHILE yorn$ <> "Y" AND yorn$ <> "N"

			'>-- Go for it --<
			IF yorn$ = "Y" THEN
			SHELL "COPY  ACSTKX*.NEW *.ACF"
			SHELL "ERASE ACSTKX*.NEW"
			END IF
		GOTO START
	END IF

	IF opt% = 15 THEN
		SHELL "TEST"
		GOTO START
	END IF

	IF opt% = 1 THEN
		ACHAIN$ = "ACBLD02": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	END IF

	IF opt% = 17 THEN ACHAIN$ = "ASAUD51": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	IF opt% = 18 THEN ACHAIN$ = "HLPKEY01": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	IF opt% = 19 THEN CALL checkaudit(updwn%)
	IF opt% = 20 THEN CLOSE : ENVIRON "DB.OR.CR$=--": npgm$ = "XXWHO01": CALL EXITPGM(npgm$): CLOSE : CHAIN npgm$
	IF opt% = 21 THEN ACHAIN$ = "MSBLD02": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$

	IF opt% = 88 THEN ACHAIN$ = "ACSTK10": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	IF opt% = 98 THEN ACHAIN$ = "B08": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	IF opt% = 99 THEN ACHAIN$ = "ACZIP01": CALL EXITPGM(ACHAIN$): CLOSE : CHAIN ACHAIN$
	GOTO getopt

SUB checkaudit (updwn%)
'$INCLUDE: '\tpmanuf\src\checkaud.bi'
END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

SUB setaudit (n%)
'    DIM SHARED auditfile$(15), naudit%
'    CALL setaudit(naudit%)
'    cashonly$ = "M": auditname$ = auditfile$(naudit%)
'$INCLUDE: '\tpmanuf\src\setaudit.bi'
END SUB

