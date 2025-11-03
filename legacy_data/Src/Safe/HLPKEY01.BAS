	'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "FIMENU"
	''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	RESET
	DIM lin$(22)
	CALL setup("HELP KEYING")
	top% = 2
	OPEN "HELP.HLP" FOR RANDOM AS #98 LEN = 78
	FIELD #98, 78 AS a$
	LOCATE 3, 2
	FOR i% = 1 TO 20
		GET #98, i%
		lin$(i%) = MID$(a$, 1, 78)
		LOCATE top% + i%, 2: PRINT MID$(a$, 1, 78)
		NEXT

	lin% = 1

	DO WHILE updwn% <> 59
		IF lin% < 1 OR lin% > 20 THEN lin% = 1
		LOCATE lin% + top%, 2
		CALL inpnew(lin$(lin%), 178!, updwn%, "13,59,60,72,80")
		IF updwn% = 60 THEN lin% = lin% - 2
		IF updwn% = 72 THEN lin% = lin% - 2
		lin% = lin% + 1
	LOOP


	'>>> UPDATE <<<<
	FOR i% = 1 TO 20
		LSET a$ = lin$(i%)
		PUT #98, i%
		NEXT
	CLOSE
	CALL exitpgm(apgm$)
	CHAIN apgm$
