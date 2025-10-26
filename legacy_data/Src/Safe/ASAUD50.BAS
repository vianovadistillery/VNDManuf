DECLARE SUB setaudit (n%)
'.dc - Complete
	'>>>> ASAUD50 <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
	'>>>> Remove zero,tagged records from the audit file
	'>>>>
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "FIMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CONST maxpe% = 100
	DIM pe%(maxpe%)
	DIM SHARED auditfile$(15), naudit%'max 15 years
	CALL setaudit(naudit%)
	RESET
START:
	CALL setup("REMOVE ZERO RECORDS FROM AUDIT FILE")
	COLOR 8, 3: LOCATE 25, 32: PRINT "F1 - exit."; : COLOR 2, 0
	LOCATE 10, 25: PRINT "1...Rebuild CSAUDIT.ASF"
	LOCATE 11, 25: PRINT "2...Rebuild ASAUDIT.ASF"
	LOCATE 13, 25: PRINT "Option..> "; CHR$(FNH);
	opt$ = ""
	CALL inpnew(opt$, 101!, updwn%, "13,59,64" + ALT): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
	opt% = VAL(opt$)
	IF opt% < 1 OR opt% > 2 THEN GOTO START

	cashonly$ = "Y"
	IF opt% = 2 THEN cashonly$ = "M": auditname$ = auditfile$(naudit%)
	GOSUB DO.UPD
	GOTO START
'////////////////////////////////////////////////////////////////////////////
'>>>>> do update
'////////////////////////////////////////////////////////////////////////////
DO.UPD:
	IF cashonly$ = "Y" THEN
	OPEN "csaudit.new" FOR RANDOM AS #8 LEN = 92: CLOSE #8
	KILL "csaudit.new"
	ELSE
	OPEN "asaudit.new" FOR RANDOM AS #8 LEN = 92: CLOSE #8
	KILL "asaudit.new"
	END IF
	typefields% = -1

	'$INCLUDE: '\tpmanuf\src\ASAUDIT.INC'
	 '?? cashonly$ = "M": auditname$ = auditfile$(naudit%)
	 GOSUB OPEN.AUDIT

	LOCK #8

	IF cashonly$ = "Y" THEN
	OPEN "csaudit.new" FOR RANDOM AS #2 LEN = 92'output only
	ELSE
	OPEN "asaudit.new" FOR RANDOM AS #2 LEN = 92'output only
	END IF
	'// Find the end of the audit file
	adlast% = LOF(8) / 92
	GOSUB do.read
	GOSUB rebuild.pe.list.2

	UNLOCK #8

	IF cashonly$ = "Y" THEN
	CLOSE
	OPEN "csaudit.old" FOR RANDOM AS #8 LEN = 92: CLOSE #8
	KILL "csaudit.old"
	CLOSE
	SHELL "RENAME CSAUDIT.ASF CSAUDIT.OLD"
	SHELL "RENAME CSAUDIT.NEW CSAUDIT.ASF"
	ELSE
	CLOSE
	OPEN "asaudit.old" FOR RANDOM AS #8 LEN = 92: CLOSE #8
	KILL "asaudit.old"
	CLOSE
	SHELL "RENAME ASAUDIT.ASF ASAUDIT.OLD"
	SHELL "RENAME ASAUDIT.NEW ASAUDIT.ASF"
	END IF
RETURN
'/////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>  Read file <<<<<<<<<<<<<<<<<<<<
'/////////////////////////////////////////////////
do.read:
	LOCATE 15, 20: PRINT "Deletion of marked records in progress"
	rec% = 1: rec2% = 0
	GET #8, rec%, audit
	DO WHILE NOT EOF(8)
		IF rec% MOD 100 = 0 THEN
			LOCATE 16, 20: PRINT "Reading audit record "; rec%; " out of "; adlast%: LOCATE 1, 1
			END IF
		skip% = 0
		IF audit.adtype$ = "XX" AND audit.advalue = 0 THEN skip% = -1
		IF skip% THEN
			del.count% = del.count% + 1
			LOCATE 17, 20: PRINT "Deleted "; del.count%; " records": LOCATE 1, 1
			ELSE
			rec2% = rec2% + 1
			audit.adrec% = rec2%
			PUT #2, , audit
			END IF
		GET #8, , audit: rec% = rec% + 1
		LOOP
RETURN
'//////////////////////////////////////////////////////////////////////////
'>>>>> Rebuild the PE linked list. ---- ON THE NEW FILE ----
'//////////////////////////////////////////////////////////////////////////
rebuild.pe.list.2:
	'// Find the end of the audit file
	adlast2% = LOF(2) / 92
	LOCATE 19, 20: PRINT "Update of the period records in progress"
	FOR i% = 1 TO maxpe%
		pe%(i%) = 0
		NEXT
	'>>>> First time through get the address of the records <<<<
	rec2% = 1: n.pe% = 0
	GET #2, rec2%, audit
	DO WHILE NOT EOF(2)
		IF audit.adtype$ = "PE" THEN
			IF n.pe% = maxpe% THEN
						BEEP: BEEP: BEEP
						COLOR 14
						PRINT "Too many period ends. Records will be lost."
						PRINT "Go back to *.OLD files"
						X$ = INPUT$(1)
						EXIT DO
						END IF
			n.pe% = n.pe% + 1
			pe%(n.pe%) = rec2%
			END IF
		IF rec% MOD 500 = 0 THEN
			LOCATE 20, 20: PRINT "Reading audit record "; rec2%; " out of "; adlast2%: LOCATE 1, 1
			END IF
		GET #2, , audit: rec2% = rec2% + 1
		LOOP
	'>>>> Go back and update the file <<<<
	FOR i% = 1 TO n.pe%
		rec2% = pe%(i%)
		GET #2, rec2%, audit
		MID$(audit.adsname$, 1, 2) = MKI$(pe%(i% + 1))
		MID$(audit.adsname$, 3, 2) = MKI$(pe%(i% - 1))
		MID$(audit.adsname$, 5, 2) = MKI$(pe%(n.pe%))
		PUT #2, rec2%, audit
		NEXT
RETURN

SUB setaudit (n%)
'$INCLUDE: '\tpmanuf\src\setaudit.bi'
END SUB

