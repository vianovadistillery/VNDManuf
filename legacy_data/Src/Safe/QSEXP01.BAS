DECLARE SUB printit (rec%, updwn%, stdout$)
DECLARE SUB rinsert (rec%, updwn%)
DECLARE SUB rdelete (rec%, auto$, updwn%)
DECLARE SUB browse71 (firstonscreen%)
DECLARE SUB browse71 (firstonscreen%)
DECLARE SUB browse.xx (firstonscreen%)
DECLARE SUB dodelete (rec%, auto$, updwn%)
DECLARE SUB change (rec%, updwn%)
DECLARE SUB dsply (rec%, updwn%)
DECLARE SUB load.unpaid (cust$, startrec%, docnum$, VALUE!, updwn%)
DECLARE SUB browse.idx (first.on.screen%, ch1%, ch2%)
DECLARE SUB upd.who (ch.audit%, ch.sup%, upd%)
'.dc - Complete
'/////////////////////////////////////////////////////////////////////////////
'>>> QSEXP01 - Exposure panels
'/////////////////////////////////////////////////////////////////////////////
	'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
	RESET
	apgm$ = "QSMENU"
	''$INCLUDE: '\tpmanuf\src\pgmerr.INC'

	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\cus.INC'
	'$INCLUDE: '\tpmanuf\src\cusX.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	'$INCLUDE: '\tpmanuf\src\msmisc.INC'
	'$INCLUDE: '\tpmanuf\src\exposure.INC'
	DIM SHARED maxcus%

	GET #36, 1, msmisc
	maxcus% = CVI(msmisc.max7$)
	acls% = -1
	skip% = -1
start:
	IF acls% = -1 THEN
	CALL setup("EXPOSURE PANELS")
	btm$ = " F1-Exit  F3-New Panel F4-Delete  F6-Browse                F9-Print  F10-Change"
	COLOR 0, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
	END IF
	acls% = 0

	IF NOT skip% THEN
		COLOR 2, 0
		LOCATE 3, 20: PRINT "Enter exposure number...> "
		LOCATE 3, 45: in$ = ""
		CALL inpnew(in$, 4!, updwn%, "13,61-62,59,64,72,80,66-68" + ALT$): GOSUB ALT
		END IF
		skip% = 0
	SELECT CASE updwn%
	CASE 59: CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
	CASE 61: CALL rinsert(rec%, updwn%): updwn% = 68: skip% = -1
	CASE 62: CALL rdelete(rec%, auto$, updwn%): in$ = STR$(rec%): acls% = -1: skip% = -1: updwn% = 13
	CASE 64:
			s% = rec%
			CALL browse71(s%)
			in$ = STR$(s%): updwn% = 13: skip% = -1: acls% = -1: GOTO start
	CASE 67: CALL printit(rec%, updwn%, stdout$)
	CASE 68: CALL change(rec%, updwn%)
	CASE 13
			IF VAL(in$) > 0 THEN
				rec% = VAL(in$)
				ELSE
				rec% = rec% + 1
			END IF
	CASE 72: rec% = rec% - 1
	CASE 80: rec% = rec% + 1
	CASE ELSE
	END SELECT

	CALL dsply(rec%, updwn%)
	GOTO start

SUB browse.idx (firstonscreen%, ch1%, ch2%)
'$INCLUDE: '\tpmanuf\src\browse01.bi'
END SUB

SUB browse71 (firstonscreen%) STATIC
	max% = LOF(71) / LEN(exposure)
	maxbpage% = 20
	bbtm$ = " F1-Return."
'//////////////////////////////////////////////////////
'>>>>> B R O W S E   T H E   F I L E
'//////////////////////////////////////////////////////
	CALL setup("BROWSE")
	COLOR 0, 3: LOCATE 25, 1: PRINT bbtm$; : COLOR 2, 0
	skip% = -1: updwn% = 13: arrival$ = STR$(firstonscreen%)
tag71:
	IF NOT skip% THEN
		LOCATE 2, 21: COLOR 7, 0: PRINT "ÍÍµ"; : LOCATE , 49: PRINT "ÆÍÍ": COLOR 2, 0
		COLOR 2, 0
		LOCATE 2, 24: PRINT "From number........>";
		LOCATE 2, 44
		CALL inpnew(arrival$, 205!, updwn%, "13,59-60,63,72-73,80-81")
		arrival$ = UCASE$(arrival$)
		END IF
	skip% = 0
	SELECT CASE updwn%
	CASE 59: GOTO bret1
	CASE 13: rec71% = VAL(arrival$)
	CASE 72: rec71% = firstonscreen% - 1
	CASE 80: rec71% = firstonscreen% + 1
	CASE 81: rec71% = firstonscreen% + maxbpage% 'Next Page
	CASE 73: rec71% = firstonscreen% - maxbpage% 'Prev page
	CASE ELSE
	END SELECT
	GOSUB bdsply71
GOTO tag71
'/////////////////////////////////////////////////////////////////////////////
'>>>      L I S T   A   P A G E
'/////////////////////////////////////////////////////////////////////////////
bdsply71:
	IF rec71% < 1 OR rec71% > max% THEN rec71% = 1
	COLOR 6, 0: LOCATE 3, 2
	PRINT "Seq. R-R-C Form. Description               Exposed "
	COLOR 2, 0
	firstonscreen% = 0

	GET #71, rec71%, exposure
	lin% = 0
	LOCATE 4, 2
	DO WHILE NOT EOF(71)

		ok% = -1
		IF exposure.no% <> rec71% THEN ok% = 0
		IF ok% THEN
			IF firstonscreen% = 0 THEN firstonscreen% = rec71%
			LOCATE , 2
			PRINT USING "###  !-!-! &  & &"; exposure.no%; exposure.rack$; exposure.row$; exposure.col$; exposure.tnta$; exposure.desc1$; FNDYY$(exposure.exposed$)
			lin% = lin% + 1
			END IF

	GET #71, , exposure: rec71% = rec71% + 1
	LOOP

	'Clear out to the end of screen
	FOR i% = lin% + 1 TO maxbpage%
		LOCATE , 2: PRINT SPACE$(78)
		NEXT
RETURN
bret1:

END SUB

SUB change (rec%, updwn%) STATIC
	adlast% = LOF(71) / LEN(exposure)
	IF rec% < 1 THEN GOTO x.change
	IF rec% > adlast% THEN GOTO x.change
cf1:
	CALL sndmsg("F10 - Jump to exposure entry")
	LOCATE 6, 39
				CALL inpnew(exposure.rack$, 101!, updwn%, "13,59-60,68")
	CALL sndmsg("")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO x.change
	IF updwn% = 68 THEN GOTO cf7
cf2:
	LOCATE 6, 41
				CALL inpnew(exposure.row$, 101!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf1
cf3:
	LOCATE 6, 43
				CALL inpnew(exposure.col$, 101!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf2
cf4:
	LOCATE 7, 39
				CALL inpnew(exposure.desc1$, 125!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf3
cf4a:
	LOCATE 7, 65
				CALL inpnew(exposure.desc2$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf4

cf4b:
	LOCATE 8, 39
				CALL inpnew(exposure.Supplier$, 105!, updwn%, "13,59-60")
	exposure.Supplier$ = UCASE$(exposure.Supplier$)
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf4

cf5:
	LOCATE 9, 39
				CALL inpnew(exposure.tnta$, 104!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf4
cf6:
	LOCATE 10, 39
				CALL inpnew(exposure.exposed$, 108!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf5

cf7:
	CALL sndmsg("Press F10 again to  change  results")
	FOR year% = 1 TO 7
		LOCATE year% + 15, 4
								CALL inpnew(exposure.year$(year%), 102!, updwn%, "13,59-60,68")
		IF updwn% = 59 THEN EXIT FOR
		IF updwn% = 68 THEN
			FOR test% = 1 TO 10
			X% = 9 + (test% - 1) * 7
			LOCATE year% + 15, X%
			a$ = MID$(STR$(exposure.test!(year%, test%)), 2)
												CALL inpnew(a$, 3.1, updwn%, "13,59-60")
			exposure.test!(year%, test%) = VAL(a$)
			IF updwn% = 59 THEN EXIT FOR
			IF updwn% = 60 AND test% = 1 THEN year% = year% + 1: EXIT FOR
			IF updwn% = 60 AND test% > 1 THEN test% = test% - 2
			NEXT
			END IF

		IF updwn% = 59 THEN EXIT FOR
		IF updwn% = 60 AND year% = 1 THEN EXIT FOR
		IF updwn% = 60 AND year% > 1 THEN year% = year% - 2
		NEXT
	CALL sndmsg("")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf6


x.change:
	IF rec% >= 1 AND rec% <= alast% THEN
	exposure.no% = rec%
	date1$ = "  /  /  ": MID$(date1$, 1, 2) = MID$(DATE$, 4, 2):         MID$(date1$, 4, 2) = MID$(DATE$, 1, 2): MID$(date1$, 7, 2) = MID$(DATE$, 9, 2)
	exposure.Date$ = FNDY$(date1$)
	PUT #71, rec%, exposure
	END IF

END SUB

SUB dsply (rec%, updwn%) STATIC
	adlast% = LOF(71) / LEN(exposure)
	IF rec% > adlast% THEN rec% = adlast%
	IF rec% < 1 THEN rec% = 1
	GET #71, rec%, exposure
	COLOR 2, 0
	LOCATE 5, 20: PRINT USING "Exposure number...:####        Exposure to AS1580-481"; exposure.no%
	LOCATE 6, 20: PRINT USING "Rack/Row/Column...>!-!-!"; exposure.rack$; exposure.row$; exposure.col$
	LOCATE 7, 20: PRINT USING "Desc..............>& &"; exposure.desc1$; exposure.desc2$
	LOCATE 8, 20: PRINT USING "Supplier..........>&"; exposure.Supplier$
	LOCATE 9, 20: PRINT USING "Formulation.......>&"; exposure.tnta$
	LOCATE 10, 20: PRINT USING "First Exposed.....>&"; FNDYY$(exposure.exposed$)

	COLOR 6, 0
	LOCATE 12, 3: PRINT USING "     DISCO. GLOSS. CHECK. CRACK. BLIST. CRACK. F/PEE. COLOR. ...... ......!"; ""
	LOCATE 13, 3: PRINT USING "                                                                          !"; " "
	LOCATE 14, 3: PRINT USING "       1.2    1.5    1.7    1.8    1.9   1.10   1.11   1.13   1.14   1.15 !"; ""
	LOCATE 15, 3: PRINT "ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ"
	COLOR 2, 0

	FOR year% = 1 TO 7
	LOCATE year% + 15, 3: PRINT USING "'\ \ ###.#% ###.#% ###.#% ###.#% ###.#% ###.#% ###.#% ###.#% ###.#% ###.#%"; exposure.year$(year%); exposure.test!(year%, 1); exposure.test!(year%, 2); exposure.test!(year%, 3); exposure.test!(year%, 4); exposure _
.test!(year%, 5); exposure.test!(year%, 6); exposure.test!(year%, 7); exposure.test!(year%, 8); exposure.test!(year%, 9); exposure.test!(year%, 10);
	NEXT


END SUB

SUB printit (rec%, updwn%, stdout$)
alast% = LOF(71) / LEN(exposure)
IF rec% < 1 THEN GOTO x.print
IF rec% > alast% THEN GOTO x.print
OPEN stdout$ FOR OUTPUT AS #99

	lin% = 9999: pag% = 0

	IF lin% > 50 THEN GOSUB heading
CLOSE #99
GOTO x.print
'////////////////////////////////////////////////////////////////////////////
'>>>
'////////////////////////////////////////////////////////////////////////////
heading:
	date1$ = "  /  /  ": MID$(date1$, 1, 2) = MID$(DATE$, 4, 2):         MID$(date1$, 4, 2) = MID$(DATE$, 1, 2): MID$(date1$, 7, 2) = MID$(DATE$, 9, 2)
	PRINT #99, ; TAB(1); CHR$(14); msmisc.cc$
	PRINT #99, "#qscom01"; TAB(70); date1$
	IF ch% = 70 THEN PRINT #99, : PRINT #99, TAB(5); "      Q U A L I T Y   C O N T R O L  -  C O M P L A I N T     "
	IF ch% = 73 THEN PRINT #99, : PRINT #99, TAB(5); "Q U A L I T Y   C O N T R O L  -  N O N  C O N F O R M A N C E"

	pag% = pag% + 1
	PRINT #99, TAB(70); "Page: "; pag%
	PRINT #99, STRING$(79, "=")
	lin% = 0
	fetch% = 1
	RETURN

x.print:
END SUB

SUB rdelete (rec%, auto$, updwn%) STATIC
	 IF auto$ <> "Y" THEN
	 COLOR 14: LOCATE 2, 23: PRINT "D E L E T I O N    P E N D I N G"
	 LOCATE 25, 1: COLOR 0, 7: PRINT SPACE$(80);
	 LOCATE 25, 21: PRINT "F1 - Abort.     F10 -  Continue.";
	 COLOR 2, 0: LOCATE 1, 1
	 CALL inpnew(a$, 0!, updwn%, "59,68")
	 IF updwn% <> 68 THEN GOTO x.delete
	 END IF

	 exposure.no% = 0
	 exposure.rack$ = " "
	 exposure.row$ = " "
	 exposure.col$ = " "
	 exposure.desc1$ = SPACE$(99)
	 exposure.desc2$ = SPACE$(99)
	 exposure.tnta$ = "    "
	 exposure.exposed$ = SPACE$(8)
	 FOR i% = 1 TO 7
	exposure.year$(i%) = "  "
	exposure.test(i%, 1) = 0
	exposure.test(i%, 2) = 0
	exposure.test(i%, 3) = 0
	exposure.test(i%, 4) = 0
	exposure.test(i%, 5) = 0
	exposure.test(i%, 6) = 0
	NEXT

	 exposure.Date$ = SPACE$(8)
	 PUT #71, rec%, exposure

x.delete:
END SUB

SUB rinsert (rec%, updwn%)

found% = 0
rec% = 1
GET #71, rec%, exposure
DO WHILE NOT EOF(71)
	IF exposure.no% <> rec% THEN found% = -1: EXIT DO
	GET #71, , exposure: rec% = rec% + 1
	LOOP

	IF rec% <> exposure.no% THEN
		auto$ = "Y"
		CALL rdelete(rec%, auto$, updwn%)
		exposure.no% = rec%
		PUT #71, rec%, exposure
		END IF



END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

