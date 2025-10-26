DECLARE SUB printit (rec%, updwn%, STDOUT$)
DECLARE SUB rdelete (rec%, auto$, updwn%)
DECLARE SUB rinsert (ok%)
DECLARE SUB browse70 (firstonscreen%)
DECLARE SUB change (rec%, updwn%)
DECLARE SUB dsply (rec%, updwn%)
DECLARE SUB load.unpaid (cust$, startrec%, docnum$, VALUE!, updwn%)
DECLARE SUB browse.idx (first.on.screen%, ch1%, ch2%)
DECLARE SUB upd.who (ch.audit%, ch.sup%, upd%)
'.dc - Complete
'/////////////////////////////////////////////////////////////////////////////
'>>> Projects (74)
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
	'$INCLUDE: '\tpmanuf\src\PROJECT.INC'
	'$INCLUDE: '\tpmanuf\src\Qextra1.INC'
	'$INCLUDE: '\tpmanuf\src\qextra2.INC'
	DIM SHARED maxcus%, ch%
	DIM SHARED ss%
	'stdout$ = "shit.sht"
	ss% = 1'Screen start
	

	GET #36, 1, msmisc
	maxcus% = CVI(msmisc.max7$)

	ch% = 74
	IF ENVIRON$("PARM$") = "ext1" THEN ch% = 76
	IF ENVIRON$("PARM$") = "ext2" THEN ch% = 77

	acls% = -1
	pass% = -1
start:
	IF acls% = -1 THEN
	IF ch% = 74 THEN CALL setup("PROJECTS")
	IF ch% = 76 THEN CALL setup("Extra 1")
	IF ch% = 77 THEN CALL setup("Extra 2")
	btm$ = " F1-Exit  F3-New Project  F4-Delete  F6-Browse  F9-Print  F10-Change          "
	COLOR 0, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
	COLOR 7, 0: LOCATE 2, 3: PRINT "µ                             Æ": COLOR 2
	COLOR 7, 0: LOCATE 2, 45: PRINT "µ                                Æ": COLOR 2
	END IF
	acls% = 0

	IF NOT pass% THEN
		COLOR 2, 0
		IF ch% = 74 THEN LOCATE 2, 4: PRINT "Enter project number...> "
		IF ch% = 76 THEN LOCATE 2, 4: PRINT "Enter extra 1 number...> "
		IF ch% = 77 THEN LOCATE 2, 4: PRINT "Enter extra 2 number...> "
		LOCATE 2, 28: in$ = ""
		CALL inpnew(in$, 4!, updwn%, "13,59,61-62,64,66-68,72,80," + ALT$): GOSUB ALT
		END IF
		pass% = 0
	SELECT CASE updwn%
	CASE 59: CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
	CASE 61: CALL rinsert(rec%): pass% = -1: updwn% = 68
	CASE 62: CALL rdelete(rec%, "N", updwn%): acls% = -1: GOTO start
	CASE 64: s% = rec%
			 CALL browse70(s%)
			 in$ = STR$(s%): updwn% = 13: pass% = -1: acls% = -1
	CASE 67: CALL printit(rec%, updwn%, STDOUT$)
	CASE 68: CALL change(rec%, updwn%)
	CASE 72: rec% = rec% - 1
	CASE 80: rec% = rec% + 1
	CASE 13
			IF VAL(in$) > 0 THEN
				rec% = VAL(in$)
				ELSE
				rec% = rec% + 1
				END IF
	CASE ELSE
	END SELECT

	CALL dsply(rec%, updwn%)
	GOTO start

SUB browse.idx (firstonscreen%, ch1%, ch2%)
'$INCLUDE: '\tpmanuf\src\browse01.bi'
END SUB

SUB browse70 (firstonscreen%) STATIC
	max% = LOF(ch%) / LEN(project)
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

	GET #ch%, rec%, project
	lin% = 0
	LOCATE 4, 2
	DO WHILE NOT EOF(ch%) AND lin% < maxbpage%
	ok% = 0
	IF project.no% = rec% THEN ok% = -1
		IF ok% THEN
			IF firstonscreen% = 0 THEN firstonscreen% = rec%
			SELECT CASE btype%
			CASE 1:
			LOCATE lin% + 4, 2
						'seq name                      -date-   -due---          ---        ----      xxx
			PRINT USING "### \                       \ \      \ \      \         \        \ \        \"; project.no%; project.name$; FNDYY$(project.closed$); FNDYY$(project.duedate$); project.type$; project.report$
			

			IF project.closed$ < "19000101" THEN
				LOCATE lin% + 4, 2 + 30
				COLOR 10, 0: PRINT USING "&"; FNDYY$(project.opened$): COLOR 2, 0
				END IF
			CASE 2
			LOCATE lin% + 4, 2
			PRINT USING "### \                         \ & "; project.no%; project.name$; SPACE$(45)
			CASE ELSE
			END SELECT

			lin% = lin% + 1
			END IF

	GET #ch%, , project: rec% = rec% + 1
	LOOP

	'Clear out to the end of screen
	FOR i% = lin% + 1 TO maxbpage%
		LOCATE , 2: PRINT SPACE$(78)
		NEXT
RETURN
bret1:

END SUB

SUB change (rec%, updwn%) STATIC
	alast% = LOF(ch%) / LEN(project)
	IF rec% < 1 THEN GOTO x.change
	IF rec% > alast% THEN GOTO x.change
	IF MID$(project.opened$, 1, 1) <= "0" THEN project.opened$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
cf1:
	LOCATE 2, 53
        CALL inpnew(project.name$, 125!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf1
cf2:

	LOCATE 4, 4
        CALL inpnew(project.opened$, 108!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf1
cf3:
	LOCATE 4, 13
        CALL inpnew(project.closed$, 108!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf2

cf4:
	LOCATE 4, 23
        CALL inpnew(project.duedate$, 108!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf3

cf5:
	LOCATE 4, 55
        CALL inpnew(project.type$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf4

cf6:
	LOCATE 4, 66
        CALL inpnew(project.report$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf5


cf88:
	i% = 1
	DO
		IF i% < 1 THEN GOTO cf6
		IF i% > 18 THEN i% = 1
		LOCATE 6 + i% - 1, 2
		IF i% = 1 OR i% = 4 OR i% = 16 THEN
			in$ = MID$(project.text$(i%), 13)
			LOCATE 6 + i% - 1, 14
			CALL inpnew(in$, 166, updwn%, "13,59-60")
			MID$(project.text$(i%), 13, 66) = in$ + SPACE$(99)
			ELSE
			CALL inpnew(project.text$(i%), 178, updwn%, "13,59-60")
			END IF
		IF updwn% = 59 THEN GOTO x.change
		IF updwn% = 60 THEN i% = i% - 1
		IF updwn% = 13 THEN i% = i% + 1
		LOOP
x.change:
	IF rec% >= 1 AND rec% <= alast% THEN
	PUT #ch%, rec%, project
	END IF

END SUB

SUB dsply (rec%, updwn%) STATIC
	alast% = LOF(ch%) / LEN(project)
	IF rec% > alast% THEN rec% = adlast%
	IF rec% < 1 THEN rec% = 1
	GET #ch%, rec%, project
	LOCATE 2, 47: PRINT USING "####.>\                       \"; project.no%; project.name$

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

	LOCATE 4, 2: PRINT USING "  \      \³\      \³ \       \³\        \³\        \³\        \³\        \³!"; FNDYY$(project.opened$); FNDYY$(project.closed$); FNDYY$(project.duedate$); " "; " "; project.type$; project.report$;
	LOCATE 5, 2: PRINT USING "ÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄ!"; "Ä"
	MID$(project.text$(1), 1, 12) = " Problem  : "
	MID$(project.text$(4), 1, 12) = " Action.  : "
	MID$(project.text$(16), 1, 12) = " Report.  : "

	FOR i% = 1 TO 18
	X% = ss% + i% - 1
	IF X% >= 1 AND X% <= 18 THEN LOCATE 5 + i%, 2: PRINT USING "&"; project.text$(X%)
	NEXT

	COLOR 6, 0
	X% = 4 + ss% + 1
	IF X% > 4 AND X% < 24 THEN LOCATE X%, 2: PRINT " Problem  : "
	X% = 4 + ss% + 4
	IF X% > 4 AND X% < 24 THEN LOCATE X%, 2: PRINT " Action.  : "
	X% = 4 + ss% + 16
	IF X% > 4 AND X% < 24 THEN LOCATE X%, 2: PRINT " Report.  : "


	COLOR 2, 0

x.dsply:
END SUB

SUB printit (rec%, updwn%, STDOUT$)
alast% = LOF(ch%) / LEN(project)
IF rec% < 1 THEN GOTO x.print
IF rec% > alast% THEN GOTO x.print
OPEN STDOUT$ FOR OUTPUT AS #99

	lin% = 9999: pag% = 0

	IF lin% > 50 THEN GOSUB heading
	PRINT #99, " "
	PRINT #99, USING "Title : &"; project.name$
	PRINT #99, " "
	PRINT #99, USING "ÚÄÄÄÄÂÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄ!"; "¿"
	PRINT #99, USING "³ No.³ Opened ³ Closed ³ Type     ³          ³          ³          ³ Report  !³"; " "
	PRINT #99, USING "³####³\      \³\      \³\        \³          ³          ³          ³\        \³"; project.no%; FNDYY$(project.opened$); FNDYY$(project.closed$); project.type$; project.report$
	PRINT #99, USING "ÀÄÄÄÄÁÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄ!"; "Ù"
	PRINT #99, " "
	PRINT #99, " "

	FOR i% = 1 TO 18
	IF i% = 1 THEN PRINT #99, STRING$(79, "Ä")
	IF i% = 4 THEN PRINT #99, " "
	IF i% = 9 THEN PRINT #99, " "
	PRINT #99, USING "&"; project.text$(i%)
	NEXT
	PRINT #99, STRING$(79, "Ä")
	PRINT #99, CHR$(12);

CLOSE #99
GOTO x.print
'////////////////////////////////////////////////////////////////////////////
'>>>
'////////////////////////////////////////////////////////////////////////////
heading:
	DATE1$ = "  /  /  ": MID$(DATE1$, 1, 2) = MID$(DATE$, 4, 2):         MID$(DATE1$, 4, 2) = MID$(DATE$, 1, 2): MID$(DATE1$, 7, 2) = MID$(DATE$, 9, 2)
	PRINT #99, ; TAB(1); CHR$(14); msmisc.cc$
	PRINT #99, "#qscom01"; TAB(70); DATE1$
	PRINT #99, : PRINT #99, TAB(5); "Q U A L I T Y   C O N T R O L  -   P R O J E C T S "

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
   CALL inpnew(A$, 0!, updwn%, "59,68")
   IF updwn% <> 68 THEN GOTO x.delete
   END IF

   project.name$ = SPACE$(99)

   project.opened$ = SPACE$(99)
   project.closed$ = SPACE$(99)



   FOR i% = 1 TO 18: project.text$(i%) = SPACE$(99): NEXT
   project.no = 0
   PUT #ch%, rec%, project

x.delete:
END SUB

SUB rinsert (rec%)

found% = 0
rec% = 1
GET #ch%, rec%, project
DO WHILE NOT EOF(ch%)
	IF project.no% <> rec% THEN found% = -1: EXIT DO
	GET #ch%, , project: rec% = rec% + 1
	LOOP

	IF rec% <> project.no% THEN
		auto$ = "Y"
		CALL rdelete(rec%, auto$, updwn%)
		project.no% = rec%
		PUT #ch%, rec%, project
		END IF




END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

