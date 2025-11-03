DECLARE SUB dsply (rec%, updwn%, getit%)
DECLARE SUB rmove (rec%)
DECLARE SUB zcpyfmt ()
DECLARE SUB printit (rec%, updwn%, stdout$)
DECLARE SUB rdelete (rec%, auto$, updwn%)
DECLARE SUB rinsert (ok%)
DECLARE SUB browse70 (firstonscreen%)
DECLARE SUB change (rec%, updwn%)
DECLARE SUB load.unpaid (cust$, startrec%, docnum$, VALUE!, updwn%)
DECLARE SUB browse.idx (first.on.screen%, ch1%, ch2%)
DECLARE SUB upd.who (ch.audit%, ch.sup%, upd%)
'.dc - Complete
'/////////////////////////////////////////////////////////////////////////////
'>>> Extra 1  (76)
'>>> Extra 2  (77)
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
	'$INCLUDE: '\tpmanuf\src\Qextra1.INC'
	'$INCLUDE: '\tpmanuf\src\qextra2.INC'
	DIM SHARED maxcus%, ch%
	DIM SHARED ss%
	stdout$ = "LPT1"
	ss% = 1'Screen start

	'>-Copy old format to new
	TYPE RcdFmtOld
		no AS INTEGER
		name AS STRING * 25
		opened AS STRING * 8
		closed AS STRING * 8
		duedate AS STRING * 8
		type AS STRING * 10
		report AS STRING * 10
		text(1 TO 18) AS STRING * 78
		filler AS STRING * 125
	END TYPE
	DIM SHARED old AS RcdFmtOld
	'CALL zcpyfmt

	GET #36, 1, msmisc
	maxcus% = CVI(msmisc.max7$)

	ch% = 76
	IF ENVIRON$("PARM$") = "ext1" THEN ch% = 76
	IF ENVIRON$("PARM$") = "ext2" THEN ch% = 77

	acls% = -1
	pass% = -1
	ss% = 1
start:
	IF acls% = -1 THEN
	IF ch% = 76 THEN CALL setup("Australian Projects")
	IF ch% = 77 THEN CALL setup("Overseas Projects")
	btm$ = " F1-Exit  F3-New Project  F4-Delete  F5-Move  F6-Browse  F9-Print  F10-Change"
	COLOR 0, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
	COLOR 7, 0: LOCATE 2, 3: PRINT "µ                             Æ": COLOR 2
	COLOR 7, 0: LOCATE 2, 45: PRINT "µ                                Æ": COLOR 2
	END IF
	acls% = 0

	IF NOT pass% THEN
		COLOR 2, 0
		IF ch% = 76 THEN LOCATE 2, 4: PRINT "Enter extra 1 number...> "
		IF ch% = 77 THEN LOCATE 2, 4: PRINT "Enter extra 2 number...> "
		LOCATE 2, 28: in$ = ""
		CALL inpnew(in$, 4!, updwn%, "13,59,61-64,66-68,72-73,80-81," + ALT$): GOSUB ALT
		END IF
		pass% = 0
	SELECT CASE updwn%
	CASE 59: CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
	CASE 61: CALL rinsert(rec%): pass% = -1: updwn% = 68
	CASE 62: CALL rdelete(rec%, "N", updwn%): acls% = -1: GOTO start
	CASE 63: CALL rmove(rec%)
	CASE 64: s% = rec%
			 CALL browse70(s%)
			 in$ = STR$(s%): updwn% = 13: pass% = -1: acls% = -1
	CASE 67: CALL printit(rec%, updwn%, stdout$)
	CASE 68: CALL change(rec%, updwn%)
	CASE 72: rec% = rec% - 1
	CASE 80: rec% = rec% + 1
	CASE 73: ss% = 1
	CASE 81: ss% = 19

	CASE 13
			IF VAL(in$) > 0 THEN
				rec% = VAL(in$)
				ELSE
				rec% = rec% + 1
				END IF
	CASE ELSE
	END SELECT

	getit% = -1
	CALL dsply(rec%, updwn%, getit%)
	GOTO start

SUB browse.idx (firstonscreen%, ch1%, ch2%)
'$INCLUDE: '\tpmanuf\src\browse01.bi'
END SUB

SUB browse70 (firstonscreen%) STATIC
	max% = LOF(ch%) / LEN(extra)
	updwn% = 13: arrival$ = STR$(firstonscreen%)
	btype% = 1
	maxbpage% = 20
	bbtm$ = "F1-Return."
'//////////////////////////////////////////////////////
'>>>>> B R O W S E   T H E   F I L E
'//////////////////////////////////////////////////////
	CALL setup("BROWSE")
	COLOR 0, 3: LOCATE 25, 1: PRINT bbtm$; : COLOR 2, 0
	skip% = -1
tag70:
	IF NOT skip% THEN
		LOCATE 2, 21: COLOR 7, 0: PRINT "ÍÍµ"; : LOCATE , 49: PRINT "ÆÍÍ": COLOR 2, 0
		COLOR 2, 0
		LOCATE 2, 24: PRINT "From number........>";
		LOCATE 2, 44
		CALL inpnew(arrival$, 205!, updwn%, "13,59-61,63,72-73,80-81")
		arrival$ = UCASE$(arrival$)
		END IF
	skip% = 0
	SELECT CASE updwn%
	CASE 59: GOTO bret1
	CASE 13: rec% = VAL(arrival$)
	CASE 61: rec% = firstonscreen%: IF btype% = 1 THEN btype% = 2 ELSE btype% = 1
	CASE 72: rec% = firstonscreen% - 1
	CASE 80: rec% = firstonscreen% + 1
	CASE 81: rec% = firstonscreen% + maxbpage% 'Next Page
	CASE 73: rec% = firstonscreen% - maxbpage% 'Prev page
	CASE ELSE
	END SELECT
	GOSUB bdsply70
GOTO tag70
'/////////////////////////////////////////////////////////////////////////////
'>>>      L I S T   A   P A G E
'/////////////////////////////////////////////////////////////////////////////
bdsply70:
	IF rec% < 1 OR rec% > max% THEN rec% = 1
	firstonscreen% = 0
	COLOR 6, 0: LOCATE 3, 2
	SELECT CASE btype%
	CASE 1: PRINT "Seq Name..................... Date.... Due....... ..... Type...... Report...  "
	CASE 2: PRINT "Seq Name......................                                               ."
	CASE ELSE
	END SELECT

	COLOR 2, 0

	GET #ch%, rec%, extra
	lin% = 0
	LOCATE 4, 2
	DO WHILE NOT EOF(ch%) AND lin% < maxbpage%
	ok% = 0
	IF extra.no% <> rec% AND MID$(extra.opened$, 1, 1) > " " THEN
		extra.no% = rec%
		PUT #ch%, rec%, extra
	END IF
	IF extra.no% = rec% THEN ok% = -1
		IF ok% THEN
			IF firstonscreen% = 0 THEN firstonscreen% = rec%
			SELECT CASE btype%
			CASE 1:
			LOCATE lin% + 4, 2
						'seq name                      -date-   -due---          ---        ----      xxx
			PRINT USING "### \                       \ \      \ \      \         \        \ \        \"; extra.no%; extra.name$; FNDYY$(extra.closed$); FNDYY$(extra.duedate$); extra.type$; extra.report$


			IF extra.closed$ < "19000101" THEN
				LOCATE lin% + 4, 2 + 30
				COLOR 10, 0: PRINT USING "&"; FNDYY$(extra.opened$): COLOR 2, 0
				END IF
			CASE 2
			LOCATE lin% + 4, 2
			PRINT USING "### \                         \ & "; extra.no%; extra.name$; SPACE$(45)
			CASE ELSE
			END SELECT

			lin% = lin% + 1
			END IF

	GET #ch%, , extra: rec% = rec% + 1
	LOOP

	'Clear out to the end of screen
	FOR i% = lin% + 1 TO maxbpage%
		LOCATE , 2: PRINT SPACE$(78)
		NEXT
RETURN
bret1:

END SUB

SUB change (rec%, updwn%) STATIC
	alast% = LOF(ch%) / LEN(extra)

	IF rec% < 1 THEN GOTO x.change
	IF rec% > alast% THEN GOTO x.change
	IF MID$(extra.opened$, 1, 1) <= "0" THEN extra.opened$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
cf1:
	LOCATE 2, 53
				CALL inpnew(extra.name$, 125!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf1
cf2:

	LOCATE 4, 4
				CALL inpnew(extra.opened$, 108!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf1
cf3:
	LOCATE 4, 13
				CALL inpnew(extra.closed$, 108!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf2

cf4:
	LOCATE 4, 23
				CALL inpnew(extra.duedate$, 108!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf3

cf5:
	LOCATE 4, 55
				CALL inpnew(extra.type$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf4

cf6:
	LOCATE 4, 66
				CALL inpnew(extra.report$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf5


cf88:
	i% = 1
	DO
		IF i% < 1 AND ss% > 1 THEN ss% = ss% - 1: i% = 1
		IF i% > 18 AND ss% < 36 THEN ss% = ss% + 1: i% = 18

		IF i% < 1 THEN i% = 1
		IF i% > 18 THEN i% = 1
		IF ss% < 1 THEN ss% = 1: i% = 1
		IF ss% > 36 THEN ss% = 36: i% = 18

		IF ss% + i% - 1 > 36 THEN ss% = 36 - i% + 1

		getit% = 0
		IF ss% <> oldss% THEN CALL dsply(rec%, updwn%, getit%)
		oldss% = ss%
		X% = ss% - 1 + i%
		LOCATE 5 + i%, 2
		CALL inpnew(extra.text$(X%), 178, updwn%, "13,59-62,72-73,80-81")
		SELECT CASE updwn%
		CASE 59: GOTO x.change
		CASE 60: i% = i% - 1
		CASE 72: i% = i% - 1
		CASE 13: i% = i% + 1
		CASE 80: i% = i% + 1
		CASE 73: ss% = ss% - 18
		CASE 81: ss% = ss% + 18

		CASE 61 'Insert a line
				ok% = -1
				X% = ss% - 1 + i%
				IF X% = 36 THEN BEEP: ok% = 0
				IF extra.text$(36) > SPACE$(78) THEN BEEP: ok% = 0
				IF ok% THEN
					FOR ii% = 36 TO X% + 1 STEP -1
						extra.text$(ii%) = extra.text$(ii% - 1)
						NEXT
					extra.text$(X%) = ""
					END IF
				getit% = 0
				CALL dsply(rec%, updwn%, getit%)
		CASE 62 'Delete a line
				X% = ss% - 1 + i%
				FOR ii% = X% TO 36 - 1
						extra.text$(ii%) = extra.text$(ii% + 1)
						NEXT
				extra.text$(36) = ""
				getit% = 0
				CALL dsply(rec%, updwn%, getit%)
		CASE ELSE
		END SELECT

		LOOP
x.change:
	IF rec% >= 1 AND rec% <= alast% THEN
	PUT #ch%, rec%, extra
	END IF

END SUB

SUB dsply (rec%, updwn%, getit%) STATIC
	alast% = LOF(ch%) / LEN(extra)
	IF rec% > alast% THEN rec% = adlast%
	IF rec% < 1 THEN rec% = 1
	IF ss% < 1 THEN ss% = 1
	IF ss% > 36 THEN ss% = 36

	IF getit% THEN
		GET #ch%, rec%, extra
		getit% = 0
	END IF

	LOCATE 2, 47: PRINT USING "####.>\                       \"; extra.no%; extra.name$

	COLOR 2, 0
	LOCATE 3, 2: PRINT USING "   Opened ³ Closed ³ Due      ³          ³          ³  type    ³ Report   ³!"; " ";
	COLOR 6, 0
	LOCATE 3, 4: PRINT " Opened "
	LOCATE 3, 13:  PRINT " Closed "
	LOCATE 3, 22:  PRINT " Due    "
	LOCATE 3, 33:  PRINT "        "
	LOCATE 3, 45:  PRINT "        "
	LOCATE 3, 56:  PRINT " Type   "
	LOCATE 3, 66:  PRINT " Report "
	COLOR 2, 0

	LOCATE 4, 2: PRINT USING "  \      \³\      \³ \       \³\        \³\        \³\        \³\        \³!"; FNDYY$(extra.opened$); FNDYY$(extra.closed$); FNDYY$(extra.duedate$); " "; " "; extra.type$; extra.report$;
	LOCATE 5, 2: PRINT USING "ÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄ!"; "Ä"

	FOR i% = 1 TO 18
	X% = ss% + i% - 1
	IF X% >= 1 AND X% <= 36 THEN LOCATE 5 + i%, 2: PRINT USING "&"; extra.text$(X%)
	NEXT

	COLOR 6, 0


	COLOR 2, 0

x.dsply:
END SUB

SUB printit (rec%, updwn%, stdout$)
alast% = LOF(ch%) / LEN(extra)
IF rec% < 1 THEN GOTO x.print
IF rec% > alast% THEN GOTO x.print
wrkout$ = "QSPRO02.PRT"

OPEN wrkout$ FOR OUTPUT AS #99

	lin% = 9999: pag% = 0

	IF lin% > 50 THEN GOSUB heading
	PRINT #99, " "
	PRINT #99, USING "Title : &"; extra.name$
	PRINT #99, " "
	PRINT #99, USING "ÚÄÄÄÄÂÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄ!"; "¿"
	PRINT #99, USING "³ No.³ Opened ³ Closed ³ Type     ³          ³          ³          ³ Report  !³"; " "
	PRINT #99, USING "³####³\      \³\      \³\        \³          ³          ³          ³\        \³"; extra.no%; FNDYY$(extra.opened$); FNDYY$(extra.closed$); extra.type$; extra.report$
	PRINT #99, USING "ÀÄÄÄÄÁÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄ!"; "Ù"
	PRINT #99, " "
	PRINT #99, " "

	FOR i% = 1 TO 36
	IF i% = 1 THEN PRINT #99, STRING$(79, "Ä")
	IF i% = 4 THEN PRINT #99, " "
	IF i% = 9 THEN PRINT #99, " "
	PRINT #99, USING "&"; extra.text$(i%)
	NEXT
	PRINT #99, STRING$(79, "Ä")
	PRINT #99, CHR$(12);

CLOSE #99
LOCATE 2, 1
SHELL "Copy " + wrkout$ + " " + stdout$
GOTO x.print
'////////////////////////////////////////////////////////////////////////////
'>>>
'////////////////////////////////////////////////////////////////////////////
heading:
	DATE1$ = "  /  /  ": MID$(DATE1$, 1, 2) = MID$(DATE$, 4, 2):         MID$(DATE1$, 4, 2) = MID$(DATE$, 1, 2): MID$(DATE1$, 7, 2) = MID$(DATE$, 9, 2)
	PRINT #99, ; TAB(1); CHR$(14); msmisc.cc$
	PRINT #99, "#qscom01"; TAB(70); DATE1$
	IF ch% = 76 THEN
	PRINT #99, : PRINT #99, TAB(5); "           A U S T R A L I A N    P R O J E C T S "
	END IF
	IF ch% = 77 THEN
	PRINT #99, : PRINT #99, TAB(5); "             O V E R S E A S    P R O J E C T S "
	END IF

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

	 extra.name$ = SPACE$(99)
	 extra.opened$ = SPACE$(99)
	 extra.closed$ = SPACE$(99)
	 FOR i% = 1 TO 36: extra.text$(i%) = SPACE$(99): NEXT
	 extra.no = 0
	 PUT #ch%, rec%, extra

	IF auto$ = "N" THEN
		 '>-Now condense the file.
		 lastrec% = LOF(ch%) / LEN(extra)
		 GET #ch%, lastrec%, extra
		 DO WHILE extra.no% = 0
		lastrec% = lastrec% - 1
		GET #ch%, lastrec%, extra
		LOOP


		 DO WHILE rec% < lastrec%
		GET #ch%, rec% + 1, extra
		extra.no = rec%
		PUT #ch%, rec%, extra
		rec% = rec% + 1
		 LOOP
		 'Clear the last record
		 extra.opened$ = SPACE$(99)
		 extra.closed$ = SPACE$(99)
		 FOR i% = 1 TO 36: extra.text$(i%) = SPACE$(99): NEXT
		 extra.no = 0
		 PUT #ch%, rec%, extra
	 END IF
x.delete:
END SUB

SUB rinsert (rec%)

'Find an unused location
	found% = 0
	rec% = 1
	GET #ch%, rec%, extra
	DO WHILE NOT EOF(ch%)
		IF extra.no% <> rec% THEN found% = -1: EXIT DO
		GET #ch%, , extra: rec% = rec% + 1
	LOOP

	IF rec% <> extra.no% THEN
		auto$ = "Y"
		CALL rdelete(rec%, auto$, updwn%)
		extra.no% = rec%
		PUT #ch%, rec%, extra
	END IF




END SUB

SUB rmove (rec%)
	lastrec% = LOF(ch%) / LEN(extra)

	'Find the first unused location
	found% = 0
	urec% = 1
	GET #ch%, urec%, extra
	DO WHILE NOT EOF(ch%)
		IF extra.no% <> urec% THEN found% = -1: EXIT DO
		GET #ch%, , extra: urec% = urec% + 1
	LOOP

	IF urec% <> extra.no% THEN
		auto$ = "Y"
		CALL rdelete(urec%, auto$, updwn%)
		extra.no% = urec%
		PUT #ch%, urec%, extra
	END IF


	 CALL sndmsg("Move to number...>")
	 DO
		 COLOR 2, 0: LOCATE 24, 22
		 CALL inpnew(a$, 4!, updwn%, "13,59")
		 IF updwn% = 59 THEN GOTO x.move
		 torec% = VAL(a$)
	 LOOP UNTIL torec% > 0 AND torec% < urec%

	 '>-Now the move
	 '>1 - Store this record in the unused location
	 GET #ch%, rec%, extra
	 extra.no% = urec%
	 PUT #ch%, urec%, extra

	 '>-Shuffle the records up or down
	IF torec% < rec% THEN
		FOR rec% = rec% TO torec% + 1 STEP -1
			GET #ch%, rec% - 1, extra
			extra.no% = rec%
			PUT #ch%, rec%, extra
		NEXT

		GET #ch%, urec%, extra
		extra.no% = torec%
		PUT #ch%, torec%, extra
	END IF
	IF torec% > rec% THEN
		FOR rec% = rec% TO torec% - 1 STEP 1
			GET #ch%, rec% + 1, extra
			extra.no% = rec%
			PUT #ch%, rec%, extra
		NEXT

		GET #ch%, urec%, extra
		extra.no% = torec%
		PUT #ch%, torec%, extra
	END IF



	 '>4 - Clear the unused location
	 GET #ch%, urec%, extra
	 auto$ = "Y"
	 CALL rdelete(urec%, auto$, updwn%)
	 extra.no% = 0
	 PUT #ch%, urec%, extra


x.move:
		 CALL sndmsg("")
END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

SUB zcpyfmt
	OPEN "\tpmanuf\qextra1.Old" FOR RANDOM AS #16 LEN = 1600
	OPEN "\tpmanuf\qextra2.Old" FOR RANDOM AS #17 LEN = 1600
	rec% = 1
	GET #16, rec%, old
	DO WHILE NOT EOF(16)
		extra.no = old.no
		extra.name = old.name
		extra.opened = old.opened
		extra.closed = old.closed
		extra.duedate = old.duedate
		extra.type = old.type
		extra.report = old.report
		FOR f% = 1 TO 18
		extra.text(f%) = old.text(f%)
		NEXT
		FOR f% = 19 TO 36
		extra.text(f%) = SPACE$(78)
		NEXT
		extra.filler = SPACE$(150)
		PUT #76, , extra
	GET #16, , old: rec1% = rec1% + 1
	LOOP

	rec% = 1
	GET #17, rec%, old
	DO WHILE NOT EOF(17)
		extra.no = old.no
		extra.name = old.name
		extra.opened = old.opened
		extra.closed = old.closed
		extra.duedate = old.duedate
		extra.type = old.type
		extra.report = old.report
		FOR f% = 1 TO 18
		extra.text(f%) = old.text(f%)
		NEXT
		FOR f% = 19 TO 36
		extra.text(f%) = SPACE$(78)
		NEXT

		extra.filler = SPACE$(150)
		PUT #77, , extra

	GET #17, , old: rec1% = rec1% + 1
	LOOP


END SUB
