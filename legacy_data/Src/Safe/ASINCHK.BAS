DECLARE SUB setaudit (n%)
'.dc - Complete
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "FIMENU"
	typefields% = -1

	DIM inv&(1000)
	DIM SHARED auditfile$(15), naudit%
	CALL setaudit(naudit%)
	cashonly$ = "M": auditname$ = auditfile$(naudit%)
	'$INCLUDE: '\tpmanuf\src\ASAUDIT.INC'

	CALL setup("INVOICE SEQUENCE CHECK")
	LOCATE 25, 2: COLOR 0, 3: PRINT "Shit"; : LOCATE 1, 1
	COLOR 2, 0

	GOSUB OPEN.AUDIT
	OPEN stdout$ FOR OUTPUT AS #99
	rec% = 1
	GET #8, rec%, Audit
	DO WHILE NOT EOF(8)
		IF Audit.adtype$ = "DI" THEN
			thisinv& = VAL(Audit.addocnum$)
			IF thisinv& <> lastinv& + 1 AND lastinv& > 0 THEN
				PRINT Audit.adtype$, FNDYY$(Audit.addate$), lastinv&; " gap "; Audit.addocnum$
				PRINT #99, Audit.adtype$, FNDYY$(Audit.addate$), lastinv&; " gap "; Audit.addocnum$
				END IF
			lastinv& = thisinv&
			END IF

		GET #8, , Audit: rec% = rec% + 1
		LOOP
	CLOSE
	CALL exitpgm(apgm$): CHAIN apgm$
	END

SUB setaudit (n%)
'    DIM SHARED auditfile$(15), naudit%
'    CALL setaudit(naudit%)
'    cashonly$ = "M": auditname$ = auditfile$(naudit%)
'$INCLUDE: '\tpmanuf\src\setaudit.bi'
END SUB
