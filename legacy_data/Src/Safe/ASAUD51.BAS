DECLARE SUB setaudit (n%)
DECLARE SUB checkit (errorcnt%, auditname$, updwn%)
'/////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>         A S A U D 0 1       <<<<<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "FIMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	DIM SHARED file$(20), file%
	DIM SHARED auditfile$(15), naudit%'max 15 years
	CALL setaudit(naudit%)
	RESET
	'$INCLUDE: '\tpmanuf\src\ASAUDIT.INC'
	cashonly$ = "M": auditname$ = auditfile$(naudit%)
	GOSUB OPEN.AUDIT

	errorlevel% = 0

START:
	CALL setup("AUDIT FILE CHECKING PROCEDURE")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit  (Anytime)      F2- Next file"; : COLOR 2, 0
	CALL checkit(errorcnt%, auditname$, updwn%)
	CLOSE

	CALL exitpgm(apgm$)
	IF INSTR(COMMAND$, "/SHELL") = 0 THEN
		CALL exitpgm(apgm$)
		CHAIN apgm$
		END IF

	IF errorlevel% > 0 THEN
		CALL sndmsg("Errors were found in Audit files. Backup stopped.")
		LOCATE 22, 1: CALL inpnew(a$, 0!, updwn%, "59")
		END IF

END errorlevel%

SUB checkit (errorcnt%, auditname$, updwn%) STATIC
	rec% = 1: errcnt% = 0
	GET #8, rec%, Audit
	 DO WHILE NOT EOF(8)
		typeok% = -1
		valok% = -1

		value! = Audit.advalue
		value! = value! * 100
		test# = FIX(value#)
		IF value# <> test# THEN valok% = 0: STOP


		SELECT CASE Audit.adtype$
		CASE "DI": typeok% = -1
		CASE "DC": typeok% = -1
		CASE "DP": typeok% = -1
		CASE "DD": typeok% = -1
		CASE "PT": typeok% = -1
		CASE "DJ": typeok% = -1
		CASE "CI": typeok% = -1
		CASE "CC": typeok% = -1
		CASE "CD": typeok% = -1
		CASE "CP": typeok% = -1
		CASE "CT": typeok% = -1
		CASE "CJ": typeok% = -1
		CASE "PE": typeok% = -1
		CASE "XX": typeok% = -1
		CASE "LC": typeok% = -1
		CASE "LD": typeok% = -1
		CASE ELSE: typeok% = 0
		END SELECT
		IF rec% MOD 200 = 0 THEN
			LOCATE 3, 15
			PRINT USING "Checking & as record ###,###"; auditname$; rec%
			X$ = INKEY$
			IF RIGHT$(" " + X$, 1) = CHR$(59) THEN updwn% = 59: EXIT DO
			IF RIGHT$(" " + X$, 1) = CHR$(60) THEN updwn% = 60: EXIT DO
			END IF

		IF NOT typeok% THEN
			COLOR 4
			errcnt% = errcnt% + 1
			LOCATE errcnt% + 5, 2: PRINT USING "Type invalid: #### &  #####.####"; Audit.adrec%; Audit.adsname$; Audit.advalue
			BEEP: BEEP
			COLOR 2
			END IF

		IF NOT valok% THEN
			COLOR 4
			errcnt% = errcnt% + 1
			LOCATE errcnt% + 5, 2: PRINT USING "Bad Value   : #### &  $####.####"; Audit.adrec%; Audit.adsname$; Audit.advalue
			BEEP: BEEP
			COLOR 2
			END IF


	 GET #8, , Audit: rec% = rec% + 1
	 LOOP


END SUB

SUB setaudit (n%)
'$INCLUDE: '\tpmanuf\src\setaudit.bi'
END SUB

