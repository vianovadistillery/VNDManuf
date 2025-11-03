DECLARE SUB chk4exe ()
'///////////////////////////////////////////////////////////////////
'>>>>> LOGON
'///////////////////////////////////////////////////////////////////
'> Reset count xxxMMDDYY/25
'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
'.dc - Complete
	apgm$ = "MENUTP"
''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	DIM SHARED auditfile$(15), naudit%
	DIM SHARED order%(6)

	typefields% = -1
	skipsec$ = "Y"
	pwdRqd% = -1

	sp$ = "Tlqwhu1"
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'

	GET #36, 1, msmisc
	LSET msmisc.inside$ = "N"
	ENVIRON ("SO=N")
	PUT #36, 1, msmisc


	set.count% = 0
next.screen:
	set.count% = set.count% + 1
	SELECT CASE set.count%
	CASE 1: set.screen% = 8
	CASE 2: set.screen% = 2
	CASE ELSE: CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
	END SELECT

	ON ERROR GOTO next.screen
	SCREEN set.screen%
	ON ERROR GOTO 0
	'>>- Enforce signon once a day -<<
	'>> That way only one or two people need to know the password
	IF DATE$ = msmisc.oldate$ THEN
		LSET msmisc.inside$ = "Y"
		pwdRqd% = 0
		ok% = -1
	END IF

	Y0% = 20: X0% = -35
	CLS
	GOSUB dsply

	IF pwdRqd% THEN
		FOR chances% = 1 TO 3
			IF set.screen% = 8 THEN COLOR 7, 15
			LOCATE 1, 1: PRINT "Enter password:";
			IF set.screen% = 8 THEN COLOR 15, 15
			newword$ = ""
			DO
				a$ = ""
				DO UNTIL a$ <> "": a$ = INKEY$
				: LOOP
				IF LEN(a$) = 1 AND a$ = CHR$(13) THEN EXIT DO
				IF LEN(a$) = 2 AND RIGHT$(a$, 1) = CHR$(68) THEN EXIT DO
				IF LEN(a$) = 2 AND RIGHT$(a$, 1) = CHR$(59) THEN EXIT DO
				newword$ = newword$ + a$
			LOOP
			IF LEN(a$) = 2 AND RIGHT$(a$, 1) = CHR$(68) THEN EXIT FOR
			IF LEN(a$) = 2 AND RIGHT$(a$, 1) = CHR$(59) THEN EXIT FOR
			IF set.screen% = 8 THEN COLOR 7, 15
			GOSUB test.pass
			IF ok% THEN EXIT FOR
			LOCATE 24, 2: PRINT "Password invalid"; : LOCATE 1, 1
		NEXT
	ELSE
		IF set.screen% = 8 THEN COLOR 7, 15
		LOCATE 1, 1: PRINT "Press Enter to continue...";
		IF set.screen% = 8 THEN COLOR 15, 15
		DO
		: x$ = INKEY$: LOOP UNTIL x$ <> ""
		IF LEN(x$) = 2 AND RIGHT$(x$, 1) = CHR$(68) THEN ok% = 0: signoff% = -1
		IF LEN(x$) = 2 AND RIGHT$(x$, 1) = CHR$(59) THEN ok% = 0
		IF x$ = CHR$(27) THEN ok% = 0
	END IF
	SCREEN 0, 0, 0

	IF signoff% THEN
		GET #36, 1, msmisc
		LSET msmisc.inside$ = "N"
		LSET msmisc.oldate$ = "00/00/00"
		ENVIRON ("SO=N")
		PUT #36, 1, msmisc
	END IF

	IF ok% THEN
		CALL setup("")
		IF pwdRqd% THEN
			CALL chk4exe
		END IF

		LSET msmisc.inside$ = "Y"
		LSET msmisc.oldate$ = DATE$
		PUT #36, 1, msmisc
		ENVIRON ("SO=Y"): SOUND 800, 5
		CLOSE
		CALL setsec(25, 4, "", 42, "1o4ap03")

		ON ERROR RESUME NEXT
		CALL EXITPGM(apgm$)
		CHAIN apgm$
		IF ERR = 53 THEN
				apgm$ = "MENUTP"
				COLOR 0, 3: LOCATE 1, 60: PRINT "QBX": COLOR 2, 0
				CALL EXITPGM(apgm$)
				CHAIN apgm$
				END IF
		ON ERROR GOTO 0

		END IF
END 0
'///////////////////////////////////////////////////////////////
'>>>> Test the password
'///////////////////////////////////////////////////////////////
test.pass:
	term$ = "NORMAL"
	RESTORE sec.data
	FOR i% = 1 TO 6: READ order%(i%): NEXT
	spa$ = sp$
	FOR i% = 1 TO 6: MID$(spa$, i%, 1) = CHR$(ASC(MID$(sp$, i%, 1)) - 3): NEXT
sec.data:
	DATA 3,6,5,1,4,2
	'* Key password
	'>>>>> E N C O D E   P A S S W O R D
	pword$ = "123456"
	a$ = "1"
	FOR i% = 1 TO 6
		LSET a$ = MID$(newword$, i%, 1)
		a% = ASC(a$) - &O41 + i%
		IF a% < 0 OR a% > 255 THEN a% = 0
		LSET a$ = CHR$(a%)
		MID$(pword$, order%(i%), 1) = a$
		NEXT
	ok% = 0
	IF pword$ = msmisc.ccde$ THEN ok% = -1
	IF pword$ = spa$ THEN ok% = -1

'Reset by the date
	a$ = MID$(date1$, 4, 2) + MID$(date1$, 1, 2) + MID$(date1$, 7, 2)
	a# = VAL(a$) / 25
	a% = FIX(a#)

	IF LCASE$(MID$(newword$, 1, 3)) = "ajd" THEN
	IF VAL(MID$(newword$, 4, 5)) = a% THEN
		CALL setsec(25, 4, spa$, 42, "1o4ap03")
		SOUND 500, 4
		SOUND 800, 8
		SOUND 500, 4
		ok% = -1
		SLEEP 2
		END IF
		END IF

RETURN
'//////////////////////////////////////////////////////////////////////
'///////
'//////////////////////////////////////////////////////////////////////
dsply:
logo.data:
	'Y:   1  2  3  4  5
	DATA 92,75,42,25,8
	'X:  1  2   3   4   5   6   7   8
	DATA 72,156,201,218,247,310,314,280
	'X:  9   10  11  12  13  14  15  16
	DATA 377,360,364,410,524,495,512,608
	RESTORE logo.data
	READ y1%, y2%, y3%, y4%, y5%
	READ x1%, x2%, x3%, x4%, x5%, x6%, x7%, x8%, x9%, x10%, x11%, x12%, x13%, x14%, x15%, x16%
	y1% = y1% + Y0%: y2% = y2% + Y0%: y3% = y3% + Y0%: y4% = y4% + Y0%: y5% = y5% + Y0%
	x1% = x1% + X0%: x2% = x2% + X0%: x3% = x3% + X0%: x4% = x4% + X0%: x5% = x5% + X0%: x6% = x6% + X0%
	x7% = x7% + X0%: x8% = x8% + X0%: x9% = x9% + X0%: x10% = x10% + X0%: x11% = x11% + X0%
	x12% = x12% + X0%: x13% = x13% + X0%: x14% = x14% + X0%: x15% = x15% + X0%: x16% = x16% + X0%
	IF set.screen% = 8 THEN c% = 1 ELSE c% = 0
	'Box 2 (Accross the whole screen)
	LINE (0, y1% + 0)-(639, y1% + 0), c%
	LINE (0, y1% - 1)-(639, y1% - 1), c%
	LINE (0, y5% + 0)-(639, y5% + 0), c%
	LINE (0, y5% + 1)-(639, y5% + 1), c%
	LINE (0, y1% - 2)-(639, y5% + 2), 14, BF
	'First half of T
	LINE (x4%, y4%)-(x10%, y4%), c%
	LINE -(x6%, y2%), c%
	LINE -(x5%, y2%), c%
	LINE -(x8%, y3%), c%
	LINE -(x3%, y3%), c%
	LINE -(x4%, y4%), c%
	'Second half of T
	LINE (x11%, y4%)-(x15%, y4%), c%
	LINE -(x14%, y3%), c%
	LINE -(x12%, y3%), c%
	LINE -(x9%, y2%), c%
	LINE -(x7%, y2%), c%
	LINE -(x11%, y4%), c%
	'PSET (X5% + 10, Y2% - 3), 14
	IF set.screen% = 8 THEN PAINT (x5% + 10, y2% - 3), c%
	'PSET (X10% + 10, Y2% - 3), 14
	IF set.screen% = 8 THEN PAINT (x10% + 10, y2% - 3), c%
	'Box 2 (White background)
	IF set.screen% = 8 THEN LINE (0, y1% + 2)-(639, 200), 15, BF
	IF set.screen% = 8 THEN LINE (0, y5% - 2)-(639, 0), 15, BF
	IF set.screen% = 8 THEN COLOR 9, 15
	LOCATE 16, 26: PRINT "T R A D E P A I N T S"
	LOCATE 17, 26: PRINT "Paint Manufacutures"
	LOCATE 18, 26: PRINT "142 Fitzgeralds Rd"
	LOCATE 19, 26: PRINT "Laverton North,3028"
	LOCATE 20, 26: PRINT "Phone (03) 9369-3455"
	IF set.screen% = 8 THEN COLOR 7, 15
	LOCATE 1, 73: PRINT USING "V####.#"; CVI(msmisc.version$) / 10
	LOCATE 25, 20: PRINT "F1 - Exit.      F10 - Signoff";
	RETURN

SUB chk4exe

	shella$ = "XCOPY Z:\TPMANUF\*.EXE W:\TPEXE\*.EXE /Y /D"
	SHELL shella$

	shella$ = "XCOPY W:\TPEXE\*.EXE C:\TPEXE\*.EXE /Y /D"
	SHELL shella$


END SUB
