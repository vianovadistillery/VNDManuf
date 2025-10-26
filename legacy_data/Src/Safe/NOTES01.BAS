DECLARE SUB dsply (start%, max%)
DECLARE SUB save (max%)
DECLARE SUB load (max%)
'.dc - Complete
	'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "FIMENU"
	'$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	max% = 250
	DIM SHARED lin$(max%)

	CALL load(max%)

	CALL setup("NOTES")
	COLOR 0, 3: LOCATE 25, 1: PRINT "F1- Exit.     F3-Insert      F4-Delete     "; : COLOR 2, 0

	start% = 1
	CALL dsply(start%, max%)

	lin% = 1
	DO WHILE updwn% <> 59
		oldstart% = start%
		IF lin% < 1 THEN lin% = 1: start% = start% - 1
		IF lin% > 21 THEN lin% = 21: start% = start% + 1'???
		IF start% < 1 THEN start% = 1
		IF start% > max% - 20 THEN start% = max% - 20'???
		IF oldstart% <> start% THEN CALL dsply(start%, max%)
														   

		LOCATE lin% + 2, 2
		rec% = start% + lin% - 1
		IF rec% < 1 OR rec% > max% THEN rec% = 1

		CALL inpnew(lin$(rec%), 178!, updwn%, "13,59-62,71,72-73,80-81" + ALT$): GOSUB ALT

		SELECT CASE updwn%
		CASE 60: lin% = lin% - 1
		CASE 61 'Insert a line
				ok% = -1
				IF lin% = max% THEN BEEP: ok% = 0
				IF lin$(max%) <> "" THEN BEEP: ok% = 0
				IF ok% THEN
					FOR i% = max% TO rec% + 1 STEP -1
						lin$(i%) = lin$(i% - 1)
						NEXT
					END IF
				lin$(rec%) = ""
				CALL dsply(start%, max%)
		CASE 62 'Delete a line
				FOR i% = rec% TO max% - 1
						lin$(i%) = lin$(i% + 1)
						NEXT
				lin$(max%) = ""
				CALL dsply(start%, max%)
		CASE 72: lin% = lin% - 1
		CASE 73: 'page up
				start% = start% - 21'???
				IF start% < 1 THEN start% = 1
				CALL dsply(start%, max%)
		CASE 81: 'page down
				start% = start% + 21'???
				IF start% > (max% - 20) THEN start% = max% - 20'???
				CALL dsply(start%, max%)
		CASE ELSE
			lin% = lin% + 1
		END SELECT

	LOOP


	'>>> UPDATE <<<<
	CALL save(max%)
CLOSE
CALL exitpgm(apgm$)
CHAIN apgm$
END

SUB dsply (start%, max%) STATIC
	COLOR 2, 0
	lin% = 0
	IF start% < 1 OR start% > max% THEN start% = 1

	FOR i% = start% TO start% + 20'???
		lin% = lin% + 1
		LOCATE lin% + 2, 2: PRINT USING "\                                                                            \"; lin$(i%)
		NEXT


END SUB

SUB load (max%) STATIC
	CALL sndmsg("Loading..")

	OPEN "NOTES.WHO" FOR RANDOM SHARED AS #1: CLOSE #1
	OPEN "NOTES.WHO" FOR INPUT SHARED AS #1
	rec% = 1
	IF LOF(1) > 0 THEN
	LINE INPUT #1, lin$(rec%)
	DO WHILE NOT EOF(1)
		rec% = rec% + 1
		LINE INPUT #1, lin$(rec%)
		LOOP
		END IF

	CLOSE #1

	CALL sndmsg("")
END SUB

SUB save (max%) STATIC
	CALL sndmsg("Saving..")
	'>> SAVE anything still in memory
	OPEN "NOTES.WHO" FOR OUTPUT SHARED AS #1

	'Find the last entry
	last% = max%
	FOR i% = max% TO 1 STEP -1
		IF lin$(i%) <> "" THEN last% = i%: EXIT FOR
		NEXT


	CALL sndmsg("Saving..")
	FOR rec% = 1 TO last%
		PRINT #1, lin$(rec%)
		NEXT

	CALL sndmsg("")
END SUB

