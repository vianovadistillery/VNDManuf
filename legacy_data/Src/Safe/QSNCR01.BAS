DECLARE SUB printit (rec%, updwn%, stdout$)
DECLARE SUB rdelete (rec%, auto$, updwn%)
DECLARE SUB rinsert (ok%)
DECLARE SUB browsech (firstonscreen%)
DECLARE SUB change (rec%, updwn%)
DECLARE SUB dsply (rec%, updwn%)
DECLARE SUB load.unpaid (cust$, startrec%, docnum$, VALUE!, updwn%)
DECLARE SUB browse.idx (first.on.screen%, ch1%, ch2%)
DECLARE SUB upd.who (ch.audit%, ch.sup%, upd%)
'.dc - Complete
'/////////////////////////////////////////////////////////////////////////////
'>>> QSCOM01- Complaint form
'>>> QSNCR01- Non Comformances
'/////////////////////////////////////////////////////////////////////////////
	'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
	'ONST ch% = 70
	CONST ch% = 73
	'stdout$ = "SHIT.SHT"'??
	RESET
	apgm$ = "QSMENU"
	''$INCLUDE: '\tpmanuf\src\pgmerr.INC'

	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\cus.INC'
	'$INCLUDE: '\tpmanuf\src\cusX.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	'$INCLUDE: '\tpmanuf\src\msmisc.INC'
	'$INCLUDE: '\tpmanuf\src\complnt.INC'
	'$INCLUDE: '\tpmanuf\src\nonconf.INC'
	DIM SHARED maxcus%

	GET #36, 1, msmisc
	maxcus% = CVI(msmisc.max7$)
	acls% = -1
start:
	IF acls% = -1 THEN
	IF ch% = 70 THEN CALL setup("COMPLAINT")
	IF ch% = 73 THEN CALL setup("NON CONFORMANCES")
	btm$ = " F1-Exit   F3-New Complaint  F4-Delete   F6-Browse   F9-Print   F10-Change"
	COLOR 0, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
	COLOR 7, 0: LOCATE 2, 22: PRINT "µ                                Æ": COLOR 2
	END IF
	acls% = 0

	IF NOT pass% THEN
		COLOR 2, 0
		LOCATE 2, 23: PRINT "Enter incident number...> "
		IF ch% = 73 THEN LOCATE 2, 23: PRINT "Enter non conformance #.> "
		LOCATE 2, 49: in$ = ""
		CALL inpnew(in$, 4!, updwn%, "13,59,61-62,64,66-68,72,80," + ALT$): GOSUB ALT
		END IF
		pass% = 0
	SELECT CASE updwn%
	CASE 59: CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
	CASE 61: CALL rinsert(rec%): pass% = -1: updwn% = 68
	CASE 62: CALL rdelete(rec%, "N", updwn%): acls% = -1: GOTO start
	CASE 64:
			s% = rec%
			CALL browsech(s%)
			in$ = STR$(s%): updwn% = 13: pass% = -1: acls% = -1
	CASE 67: CALL printit(rec%, updwn%, stdout$)
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

SUB browsech (firstonscreen%) STATIC
	max% = LOF(ch%) / LEN(complnt)
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
tagch:
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
	GOSUB bdsplych
GOTO tagch
'/////////////////////////////////////////////////////////////////////////////
'>>>      L I S T   A   P A G E
'/////////////////////////////////////////////////////////////////////////////
bdsplych:
	IF rec% < 1 OR rec% > max% THEN rec% = 1
	firstonscreen% = 0
	COLOR 6, 0: LOCATE 3, 2
	SELECT CASE btype%
	CASE 1: PRINT "Seq Name................ Date.... Product... Colour.... Batch..... Type.....  "
	CASE 2: PRINT "Seq Name........................                                             ."
	CASE ELSE
	END SELECT

	COLOR 2, 0

	GET #ch%, rec%, complnt
	lin% = 0
	LOCATE 4, 2
	DO WHILE NOT EOF(ch%) AND lin% < maxbpage%
	ok% = 0
	IF complnt.no% = rec% THEN ok% = -1
		IF ok% THEN
			IF firstonscreen% = 0 THEN firstonscreen% = rec%
			SELECT CASE btype%
			CASE 1:
			LOCATE lin% + 4, 2
			PRINT USING "### \                  \ & & & & & "; complnt.no%; complnt.Name$; complnt.closed$; complnt.product$; complnt.colour$; complnt.batch$; complnt.type$
			IF complnt.closed$ < "00/00/00" THEN
				LOCATE lin% + 4, 2 + 25
				COLOR 10, 0: PRINT USING "&"; complnt.opened$: COLOR 2, 0
				END IF
			CASE 2
			LOCATE lin% + 4, 2
			PRINT USING "### \                         \ & "; complnt.no%; complnt.Name$; SPACE$(45)
			CASE ELSE
			END SELECT

			lin% = lin% + 1
			END IF

	GET #ch%, , complnt: rec% = rec% + 1
	LOOP

	'Clear out to the end of screen
	FOR i% = lin% + 1 TO maxbpage%
		LOCATE , 2: PRINT SPACE$(78)
		NEXT
RETURN
bret1:

END SUB

SUB change (rec%, updwn%) STATIC
	alast% = LOF(ch%) / LEN(complnt)
	IF rec% < 1 THEN GOTO x.change
	IF rec% > alast% THEN GOTO x.change
	IF MID$(complnt.opened$, 1, 1) <= "0" THEN complnt.opened$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
	IF MID$(complnt.cname$, 1, 1) > " " THEN GOTO cf88
	IF MID$(complnt.Name$, 1, 1) > " " THEN GOTO cf7

cf0:
	LOCATE 3, 26
        CALL inpnew(keyin$, 105!, updwn%, "13,59-60,64")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf0
	IF updwn% = 64 THEN
			CALL browse.idx(s%, 23, 43)
			in$ = STR$(s%): updwn% = 13
			IF s% < 1 OR s% > maxcus% THEN s% = 1
			GET #43, s%, cus
			keyin$ = cus.search$ + cus.stype$
			CALL setup("COMPLAINT FORMS")
			btm$ = " F1-Exit  F6-Browse                                         F10-Change"
			COLOR 0, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
			END IF

	chi% = 23
	CALL searchindex(keyin$, chi%, found%)
	IF found% THEN
		rec43% = CVI(supx.wrrn$)
		IF rec43% >= 1 AND rec43% <= maxcus% THEN
			GET #43, rec43%, cus
			complnt.Name$ = cus.sname$
			complnt.Addr$ = cus.saddr$
			complnt.sub$ = cus.suburb$
			complnt.pcode$ = cus.spcode$
			complnt.phone$ = cus.sphone$
			complnt.fax$ = cus.sphone1$
			PUT #ch%, rec%, complnt
			CALL dsply(rec%, updwn%)
			GOTO cf7
			END IF
		END IF


cf1:
	LOCATE 4, 12
        CALL inpnew(complnt.Name$, 130!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf0
cf2:
	LOCATE 5, 12
        CALL inpnew(complnt.Addr$, 125!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf1
cf3:
	LOCATE 6, 12
        CALL inpnew(complnt.sub$, 120!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf2
cf4:
	LOCATE 6, 33
        CALL inpnew(complnt.pcode$, 104!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf3
cf5:
	LOCATE 7, 12
        CALL inpnew(complnt.phone$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf4

cf6:
	LOCATE 7, 28
        CALL inpnew(complnt.fax$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf5

cf7:
	LOCATE 4, 47
        IF ch% <> 73 THEN CALL inpnew(complnt.cname$, 130!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf6
cf8:
	LOCATE 5, 47
        IF ch% <> 73 THEN CALL inpnew(complnt.caddr$, 125!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf7
cf9:
	LOCATE 6, 47
        IF ch% <> 73 THEN CALL inpnew(complnt.csub$, 120!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf8
cf10:
	LOCATE 6, 68
        IF ch% <> 73 THEN CALL inpnew(complnt.cpcode$, 104!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf9
cf11:
	LOCATE 7, 47
        IF ch% <> 73 THEN CALL inpnew(complnt.cphone$, 112!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf10

cf12:
	LOCATE 7, 61
        IF ch% <> 73 THEN CALL inpnew(complnt.cfax$, 112!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf11


cf13:
	IF updwn% = 60 THEN
	LOCATE 10, 4
        CALL inpnew(complnt.opened$, 100!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf12
	END IF

cf14:
	LOCATE 10, 13
        CALL inpnew(complnt.closed$, 100!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf13

cf15:
	LOCATE 10, 22
        CALL inpnew(complnt.type$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf14

cf16:
	LOCATE 10, 33
        CALL inpnew(complnt.product$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf15

cf17:
	LOCATE 10, 44
        CALL inpnew(complnt.colour$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf16

cf18:
	LOCATE 10, 55
        CALL inpnew(complnt.batch$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf17

cf19:
	LOCATE 10, 66
        CALL inpnew(complnt.report$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf18



cf88:
	i% = 1
	DO
		IF i% < 1 THEN GOTO cf19
		IF i% > 12 THEN i% = 1
		LOCATE 12 + i% - 1, 2
		IF i% = 1 OR i% = 4 OR i% = 9 THEN
			in$ = MID$(complnt.text$(i%), 13)
			LOCATE 12 + i% - 1, 14
			CALL inpnew(in$, 166, updwn%, "13,59-60")
			MID$(complnt.text$(i%), 13, 66) = in$ + SPACE$(99)
			ELSE
			CALL inpnew(complnt.text$(i%), 178, updwn%, "13,59-60")
			END IF
		IF updwn% = 59 THEN GOTO x.change
		IF updwn% = 60 THEN i% = i% - 1
		IF updwn% = 13 THEN i% = i% + 1
		LOOP
x.change:

	FOR i% = 1 TO 10
		IF MID$(complnt.opened$, i%, 1) = CHR$(0) THEN MID$(complnt.opened$, i%, 1) = " "
		NEXT
	FOR i% = 1 TO 10
		IF MID$(complnt.closed$, i%, 1) = CHR$(0) THEN MID$(complnt.closed$, i%, 1) = " "
		NEXT
	FOR i% = 1 TO 10
		IF MID$(complnt.type$, i%, 1) = CHR$(0) THEN MID$(complnt.type$, i%, 1) = " "
		NEXT
	FOR i% = 1 TO 10
		IF MID$(complnt.product$, i%, 1) = CHR$(0) THEN MID$(complnt.product$, i%, 1) = " "
		NEXT
	FOR i% = 1 TO 10
		IF MID$(complnt.colour$, i%, 1) = CHR$(0) THEN MID$(complnt.colour$, i%, 1) = " "
		NEXT
	FOR i% = 1 TO 10
	IF MID$(complnt.batch$, i%, 1) = CHR$(0) THEN MID$(complnt.batch$, i%, 1) = " "
	NEXT
	FOR i% = 1 TO 10
	IF MID$(complnt.report$, i%, 1) = CHR$(0) THEN MID$(complnt.report$, i%, 1) = " "
	NEXT

	FOR i% = 1 TO 30
		IF MID$(complnt.cname$, i%, 1) = CHR$(0) THEN MID$(complnt.cname$, i%, 1) = " "
		NEXT
	FOR i% = 1 TO 25
		IF MID$(complnt.caddr$, i%, 1) = CHR$(0) THEN MID$(complnt.caddr$, i%, 1) = " "
		NEXT
	FOR i% = 1 TO 20
		IF MID$(complnt.csub$, i%, 1) = CHR$(0) THEN MID$(complnt.csub$, i%, 1) = " "
		NEXT
	FOR i% = 1 TO 5
		IF MID$(complnt.cpcode$, i%, 1) = CHR$(0) THEN MID$(complnt.cpcode$, i%, 1) = " "
		NEXT
	FOR i% = 1 TO 12
		IF MID$(complnt.cphone$, i%, 1) = CHR$(0) THEN MID$(complnt.cphone$, i%, 1) = " "
		NEXT
	FOR i% = 1 TO 12
		IF MID$(complnt.cfax$, i%, 1) = CHR$(0) THEN MID$(complnt.cfax$, i%, 1) = " "
		NEXT

	IF rec% >= 1 AND rec% <= alast% THEN
	PUT #ch%, rec%, complnt
	END IF

END SUB

SUB dsply (rec%, updwn%) STATIC
	alast% = LOF(ch%) / LEN(complnt)
	IF rec% > alast% THEN rec% = adlast%
	IF rec% < 1 THEN rec% = 1
	GET #ch%, rec%, complnt

	COLOR 2, 0
	LOCATE 3, 2: PRINT USING "ÄÄÄÄÄ´Customer Search..>\     \ÃÄÄÄÄÄÄÄÄÄÅÄÄÄÄÄ´Incident Number...:####ÃÄÄÄÄÄÄ"; "     "; complnt.no%
	IF ch% = 70 THEN
	LOCATE 4, 3: PRINT USING "Name....>& ³..>&"; complnt.Name$; complnt.cname$
	LOCATE 5, 3: PRINT USING "Address.>&      ³..>&"; complnt.Addr$; complnt.caddr$
	LOCATE 6, 3: PRINT USING "Suburb..>& &      ³..>& &"; complnt.sub$; complnt.pcode$; complnt.csub$; complnt.cpcode$
	LOCATE 7, 3: PRINT USING "Phone/F.>&    &   ³..>&  &"; complnt.phone$; complnt.fax$; complnt.cphone$; complnt.cfax$
	END IF
	IF ch% = 73 THEN
	LOCATE 4, 3: PRINT USING "Name....>&"; complnt.Name$
	LOCATE 5, 3: PRINT USING "Address.>&"; complnt.Addr$
	LOCATE 6, 3: PRINT USING "Suburb..>& &"; complnt.sub$; complnt.pcode$
	LOCATE 7, 3: PRINT USING "Phone/F.>&      &"; complnt.phone$; complnt.fax$
	END IF

	LOCATE 8, 2: PRINT USING "ÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÅÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÂÄÄ!"; "Ä"
	LOCATE 9, 2: PRINT USING "   Opened ³ Closed ³ Type     ³ Product  ³  Colour  ³  Batch.  ³ Report   ³!"; " ";
	COLOR 6, 0
	LOCATE 9, 4: PRINT " Opened "
	LOCATE 9, 13:  PRINT " Closed "
	LOCATE 9, 22:  PRINT " Type   "
	LOCATE 9, 33:  PRINT " Product"
	LOCATE 9, 45:  PRINT " Colour "
	LOCATE 9, 56:  PRINT " Batch. "
	LOCATE 9, 66:  PRINT " Report "
	COLOR 2, 0
	LOCATE 10, 2: PRINT USING "  \      \³\      \³\        \³\        \³\        \³\        \³\        \³!"; complnt.opened$; complnt.closed$; complnt.type$; complnt.product$; complnt.colour$; complnt.batch$; complnt.report$;
	LOCATE 11, 2: PRINT USING "ÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄ!"; "Ä"
	MID$(complnt.text$(1), 1, 12) = " Problem  : "
	MID$(complnt.text$(4), 1, 12) = " Report.  : "
	MID$(complnt.text$(9), 1, 12) = " Action.  : "
	FOR i% = 1 TO 12
	LOCATE 12 + i% - 1, 2: PRINT USING "&"; complnt.text$(i%)
	NEXT

	COLOR 6, 0
	LOCATE 11 + 1, 2: PRINT " Problem  : "
	LOCATE 11 + 4, 2: PRINT " Report.  : "
	LOCATE 11 + 9, 2: : PRINT " Action.  : "

	LOCATE 3, 8: PRINT "Customer Search..>"
	LOCATE 3, 50: PRINT "Incident Number...:"

	COLOR 2, 0

x.dsply:
END SUB

SUB printit (rec%, updwn%, stdout$)
alast% = LOF(ch%) / LEN(complnt)
IF rec% < 1 THEN GOTO x.print
IF rec% > alast% THEN GOTO x.print
OPEN stdout$ FOR OUTPUT AS #99

	lin% = 9999: pag% = 0

	IF lin% > 50 THEN GOSUB heading
	PRINT #99, " "
	PRINT #99, " "
	PRINT #99, USING "ÚÄÄÄÄÂÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄ!"; "¿"
	PRINT #99, USING "³ No.³ Opened ³ Closed ³ Type     ³ Product  ³  Colour  ³  Batch.  ³ Report  !³"; " "
	PRINT #99, USING "³####³\      \³\      \³\        \³\        \³\        \³\        \³\        \³"; complnt.no%; complnt.opened$; complnt.closed$; complnt.type$; complnt.product$; complnt.colour$; complnt.batch$; complnt.report$
	PRINT #99, USING "ÀÄÄÄÄÁÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄ!"; "Ù"
	PRINT #99, " "
	PRINT #99, " "
	PRINT #99, USING "ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ!"; "¿"
	IF ch% = 70 THEN
	PRINT #99, USING "³Name....>& ³..>&   ³"; complnt.Name$; complnt.cname$
	PRINT #99, USING "³Address.>&      ³..>&        ³"; complnt.Addr$; complnt.caddr$
	PRINT #99, USING "³Suburb..>& &      ³..>& &        ³"; complnt.sub$; complnt.pcode$; complnt.csub$; complnt.cpcode$
	PRINT #99, USING "³Phone/F.>&    &   ³..>&    &     ³"; complnt.phone$; complnt.fax$; complnt.cphone$; complnt.cfax$
	END IF
	IF ch% = 73 THEN
	PRINT #99, USING "³Name....>&"; complnt.Name$
	PRINT #99, USING "³Address.>&"; complnt.Addr$
	PRINT #99, USING "³Suburb..>& &"; complnt.sub$; complnt.pcode$
	PRINT #99, USING "³Phone/F.>&  &"; complnt.phone$; complnt.fax$
	END IF
	PRINT #99, USING "ÀÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ!"; "Ù"

	PRINT #99, " "
	PRINT #99, " "

	FOR i% = 1 TO 12
	IF i% = 1 THEN PRINT #99, STRING$(79, "Ä")
	IF i% = 4 THEN PRINT #99, " "
	IF i% = 9 THEN PRINT #99, " "
	PRINT #99, USING "&"; complnt.text$(i%)
	NEXT
	PRINT #99, STRING$(79, "Ä")
	PRINT #99, CHR$(12);
						 
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

   complnt.Name$ = SPACE$(99)
   complnt.Addr$ = SPACE$(99)
   complnt.sub$ = SPACE$(99)
   complnt.pcode$ = SPACE$(99)
   complnt.phone$ = SPACE$(99)
   complnt.fax$ = SPACE$(99)
   complnt.type$ = SPACE$(99)
   complnt.product$ = SPACE$(99)
   complnt.colour$ = SPACE$(99)
   complnt.batch$ = SPACE$(99)
   complnt.report$ = SPACE$(99)

   complnt.opened$ = SPACE$(99)
   complnt.closed$ = SPACE$(99)

   complnt.cname$ = SPACE$(99)
   complnt.caddr$ = SPACE$(99)
   complnt.csub$ = SPACE$(99)
   complnt.cpcode$ = SPACE$(99)
   complnt.cphone$ = SPACE$(99)
   complnt.cfax$ = SPACE$(99)

   complnt.filler$ = SPACE$(99)

   FOR i% = 1 TO 12: complnt.text$(i%) = SPACE$(99): NEXT
   complnt.no = 0
   PUT #ch%, rec%, complnt

x.delete:
END SUB

SUB rinsert (rec%)

found% = 0
rec% = 1
GET #ch%, rec%, complnt
DO WHILE NOT EOF(ch%)
	IF complnt.no% <> rec% THEN found% = -1: EXIT DO
	GET #ch%, , complnt: rec% = rec% + 1
	LOOP

	IF rec% <> complnt.no% THEN
		auto$ = "Y"
		CALL rdelete(rec%, auto$, updwn%)
		complnt.no% = rec%
		PUT #ch%, rec%, complnt
		END IF




END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

