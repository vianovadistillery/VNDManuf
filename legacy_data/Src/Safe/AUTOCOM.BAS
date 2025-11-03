'$ INCLUDE: 'z:\tpmanuf\src\pgmhead.INC'
' $ INCLUDE: 'z:\tpmanuf\src\pgmerr.INC'
	CONST debug% = 0
	DIM exists$(500)
	sp80$ = SPACE$(80)
	CLS
	'CALL setup("BUILDING AUTOCOM.BAT")

	'//////////////////////////////////////////////////////////////////
	'>>> Load existing programs into an array
	'//////////////////////////////////////////////////////////////////
	n% = 0
	exists$(1) = "B08.BAS": n% = 1
	exists$(2) = "HLPKEY01.BAS": n% = 2
	exists$(3) = "TPLIB.BAS": n% = 3


	existpgm$ = DIR$("C:\TPEXE\*.exe")
'  existpgm$ = DIR$("Z:\TPMANUF\*.exe")
	DO WHILE existpgm$ <> ""
		n% = n% + 1
		x% = INSTR(existpgm$, ".")
		IF x% > 1 THEN
			pgmsfx$ = LEFT$(existpgm$, x% - 1)
			exists$(n%) = pgmsfx$ + ".BAS"
		END IF
		existpgm$ = DIR$
	LOOP

	'//////////////////////////////////////////////////////////////////
	'>>> compile each *.bas that does not have a *.exe
	'//////////////////////////////////////////////////////////////////
	options$ = " /EX /NOE /NOD:BCL71EFR.LIB "
	count% = 0

	nextpgm$ = DIR$("z:\TPMANUF\SRC\*.BAS")
	DO WHILE nextpgm$ <> ""
	ok% = -1
	FOR i% = 1 TO n%
		IF nextpgm$ = exists$(i%) THEN ok% = 0: EXIT FOR
	NEXT
	IF NOT ok% THEN nextpgm$ = ""

		IF nextpgm$ <> "" THEN
			COLOR 7, 0
			FOR i% = 3 TO 20
				LOCATE i%, 2: PRINT "º"; SPACE$(78)
				NEXT
			COLOR 2, 0
			x% = INSTR(nextpgm$, ".")
			pgmsfx$ = LEFT$(nextpgm$, x% - 1)
			pgmexe$ = pgmsfx$ + ".EXE"
			ON ERROR RESUME NEXT
			ERR = 0
			OPEN pgmexe$ FOR INPUT AS #1: CLOSE #1
			ON ERROR GOTO 0
			count% = count% + 1
			b$ = "BC Z:\TPMANUF\SRC\" + pgmsfx$ + " /E/X/Ot/G2/S/Fs/Lr/Fpi/C:1;"
			IF pgmexe$ = "MSUPD02D.EXE" THEN
			b$ = "BC Z:\TPMANUF\SRC\" + pgmsfx$ + "     /Ot/G2/S/Fs/Lr/Fpi/C:1;"
			END IF

			c$ = "LINK" + options$ + "c:\TPEXE\" + pgmsfx$ + ".OBJ,,,z:\qB7\LIB\BRT71EFR.LIB+z:\QB7\LIB\QBX.LIB;"
			c$ = "LINK" + options$ + pgmsfx$ + ".OBJ,,,z:\QB7\LIB\BRT71EFR.LIB+z:\QB7\LIB\QBX.LIB;"
			x% = INSTR(c$, ".OBJ") + 6
			FOR i% = 5 TO 23: LOCATE i%, 1: PRINT sp80$; : NEXT
			LOCATE 13, 1: PRINT "   99 <-Pre set error value."
			LOCATE 4, 1: PRINT USING "Program count #,### |&"; count%; pgmsfx$
			LOCATE 5, 1: PRINT USING "&"; b$
			IF NOT debug% THEN SHELL b$
			'>> Read the error code off the screen
			sev$ = "******" '->>Severe<<'
			FOR i% = 1 TO 6
				a% = SCREEN(13, i% + 6)
				MID$(sev$, i%, 1) = CHR$(a%)
			NEXT

			a$ = "00000"
			FOR i% = 1 TO 5
				a% = SCREEN(13, i%)
				MID$(a$, i%, 1) = CHR$(a%)
				NEXT
			IF sev$ <> "Severe" THEN a$ = "00099"

			LOCATE 13, 23: PRINT USING "   Program reads error code as###"; VAL(a$)
			ok% = 0: IF VAL(a$) = 0 THEN ok% = -1
			IF ok% THEN
				LOCATE 14, 1: PRINT USING "&"; MID$(c$, 1, x%)
				LOCATE 15, 1: PRINT USING "&"; MID$(c$, x% + 1)
				IF NOT debug% THEN SHELL c$
			ELSE
				'D$ = "RENAME  z:\TPMANUF\SRC\" + nextpgm$ + "  " + pgmsfx$ + ".BAD"
				'IF NOT debug% THEN SHELL D$
			END IF
			ON ERROR RESUME NEXT
			KILL pgmsfx$ + ".OBJ"
			KILL pgmsfx$ + ".MAP"
			ON ERROR GOTO 0
			SLEEP 1
		END IF

		nextpgm$ = DIR$
		xx$ = INKEY$
		IF xx$ = CHR$(27) THEN GOTO ENDPGM
		LOOP
	CLOSE


part2:
	CLS
	'CALL setup("SEARCHING FOR MISSING PROGRAMS")
	nextpgm$ = DIR$("z:\TPMANUF\SRC\*.BAS")
	count% = 0
	DO WHILE nextpgm$ <> ""
	IF nextpgm$ <> "" THEN
		x% = INSTR(nextpgm$, ".")
		pgmsfx$ = LEFT$(nextpgm$, x% - 1)
		pgmexe$ = pgmsfx$ + ".EXE"
		ON ERROR RESUME NEXT
		ERR = 0
		OPEN pgmexe$ FOR INPUT AS #1: CLOSE #1
		IF ERR > 0 THEN PRINT pgmexe$
		ON ERROR GOTO 0
	END IF
	nextpgm$ = DIR$

	LOOP


ENDPGM:
	CLOSE
END
