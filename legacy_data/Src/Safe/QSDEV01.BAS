DECLARE SUB rdelete (rec%, auto$, updwn%)
DECLARE SUB rinsert (ok%)
DECLARE SUB browse74 (firstonscreen%)
DECLARE SUB change (rec%, updwn%)
DECLARE SUB dsply (rec%, updwn%)
DECLARE SUB load.unpaid (cust$, startrec%, docnum$, VALUE!, updwn%)
DECLARE SUB browse.idx (first.on.screen%, ch1%, ch2%)
DECLARE SUB upd.who (ch.audit%, ch.sup%, upd%)
'.dc - Complete
'/////////////////////////////////////////////////////////////////////////////
'>>> MSNBG01- development form
'/////////////////////////////////////////////////////////////////////////////
	'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
	RESET
	apgm$ = "QSMENU"
	''$INCLUDE: '\tpmanuf\src\pgmerr.INC'

	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	'$INCLUDE: '\tpmanuf\src\msmisc.INC'
	'$INCLUDE: '\tpmanuf\src\develop.INC'
	DIM SHARED maxcus%
	DIM SHARED auditfile$(15), naudit%
	DIM SHARED develop.text$(14)

	GET #36, 1, msmisc
	maxcus% = CVI(msmisc.max7$)
	acls% = -1
start:
	IF acls% = -1 THEN
	CALL setup("DEVELOPMENT FORMS")
	btm$ = " F1-Exit          F3-New Project           F6-Browse        F10-Change"
	COLOR 0, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
	COLOR 7, 0: LOCATE 2, 22: PRINT "µ                                Æ": COLOR 2
	END IF
	acls% = 0

	IF NOT pass% THEN
		COLOR 2, 0
		LOCATE 2, 23: PRINT "Enter project number....> "
		LOCATE 2, 49: in$ = ""
		CALL inpnew(in$, 4!, updwn%, "13,59,61,64,66-68" + ALT$): GOSUB ALT
		END IF
		pass% = 0
	SELECT CASE updwn%
	CASE 59: CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
	CASE 61: CALL rinsert(rec%): pass% = -1: updwn% = 68
	CASE 64:
			CALL browse74(s%)
			in$ = STR$(s%): updwn% = 13: pass% = -1: acls% = -1
	CASE 68: CALL change(rec%, updwn%)
	CASE 13
			IF LEN(in$) > 0 THEN
				rec% = VAL(in$)
			END IF
			alast% = LOF(74) / LEN(develop)
			IF LEN(in$) = 0 AND rec% < alast% THEN rec% = rec% + 1

	CASE ELSE
	END SELECT

	CALL dsply(rec%, updwn%)
	GOTO start

SUB browse.idx (firstonscreen%, ch1%, ch2%)
'$INCLUDE: '\tpmanuf\src\browse01.bi'
END SUB

SUB browse74 (firstonscreen%) STATIC
	max% = LOF(74) / LEN(develop)
	maxbpage% = 19
	bbtm$ = "F1-Return."
'//////////////////////////////////////////////////////
'>>>>> B R O W S E   T H E   F I L E
'//////////////////////////////////////////////////////
	CALL setup("BROWSE")
	COLOR 0, 3: LOCATE 25, 1: PRINT bbtm$; : COLOR 2, 0
	skip% = -1
tag74:
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
	CASE 13: rec% = VAL(arrival$)
	CASE 72: rec% = firstonscreen% - 1
	CASE 80: rec% = firstonscreen% + 1
	CASE 81: rec% = firstonscreen% + maxbpage% 'Next Page
	CASE 73: rec% = firstonscreen% - maxbpage% 'Prev page
	CASE ELSE
	END SELECT
	GOSUB bdsply74
GOTO tag74
'/////////////////////////////////////////////////////////////////////////////
'>>>      L I S T   A   P A G E
'/////////////////////////////////////////////////////////////////////////////
bdsply74:
	IF rec% < 1 OR rec% > max% THEN rec% = 1
	COLOR 6, 0: LOCATE 3, 2
	PRINT "dffgdgdfgdfgdsfgdgsd"
	COLOR 2, 0

	GET #74, rec%, develop
	lin% = 0
	LOCATE 4, 2
	DO WHILE NOT EOF(74)
	ok% = 0
	IF develop.no% = rec% THEN ok% = -1
		IF ok% THEN
			IF firstonscreen% = 0 THEN firstonscreen% = rec%
			LOCATE , 2
			PRINT USING "### & & "; develop.no%; develop.Name$; develop.opened$
			lin% = lin% + 1
			END IF

	GET #74, , develop: rec% = rec% + 1
	LOOP

	'Clear out to the end of screen
	FOR i% = lin% + 1 TO maxbpage%
		LOCATE , 2: PRINT SPACE$(78)
		NEXT
RETURN
bret1:

END SUB

SUB change (rec%, updwn%) STATIC
	alast% = LOF(74) / LEN(develop)
	IF rec% < 1 THEN GOTO x.change
	IF rec% > alast% THEN GOTO x.change
	IF MID$(develop.opened$, 1, 1) <= "0" THEN develop.opened$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
	IF MID$(develop.Name$, 1, 1) > " " THEN GOTO cf7
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
			CALL setup("DEVELOPMENT FORMS")
			btm$ = " F1-Exit  F6-Browse                                         F10-Change"
			COLOR 0, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
			END IF

	chi% = 23
	CALL searchindex(keyin$, chi%, found%)
	IF found% THEN
		rec43% = CVI(supx.wrrn$)
		IF rec43% >= 1 AND rec43% <= maxcus% THEN
			GET #43, rec43%, cus
			develop.Name$ = cus.sname$
			develop.Addr$ = cus.saddr$
			develop.sub$ = cus.suburb$
			develop.pcode$ = cus.spcode$
			develop.phone$ = cus.sphone$
			develop.fax$ = cus.sphone1$
			PUT #74, rec%, develop
			CALL dsply(rec%, updwn%)
			GOTO cf7
			END IF
		END IF


cf1:
	LOCATE 4, 12
        CALL inpnew(develop.Name$, 130!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf0
cf2:
	LOCATE 5, 12
        CALL inpnew(develop.Addr$, 125!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf1
cf3:
	LOCATE 6, 12
        CALL inpnew(develop.sub$, 120!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf2
cf4:
	LOCATE 6, 33
        CALL inpnew(develop.pcode$, 104!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf3
cf5:
	LOCATE 7, 12
        CALL inpnew(develop.phone$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf4

cf6:
	LOCATE 7, 28
        CALL inpnew(develop.fax$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf5

cf7:
	LOCATE 4, 47
        CALL inpnew(develop.cName$, 130!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf6
cf8:
	LOCATE 5, 47
        CALL inpnew(develop.cAddr$, 125!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf7
cf9:
	LOCATE 6, 47
        CALL inpnew(develop.csub$, 120!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf8
cf10:
	LOCATE 6, 68
        CALL inpnew(develop.cpcode$, 104!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf9
cf11:
	LOCATE 7, 47
        CALL inpnew(develop.cphone$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf10

cf12:
	LOCATE 7, 63
        CALL inpnew(develop.cfax$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf11


cf13:
	IF updwn% = 60 THEN
	LOCATE 10, 4
        CALL inpnew(develop.opened$, 100!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf12
	END IF

cf14:
	LOCATE 10, 13
        CALL inpnew(develop.closed$, 100!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf13

cf15:
	LOCATE 10, 22
        CALL inpnew(develop.type$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf14

cf16:
	LOCATE 10, 33
        CALL inpnew(develop.product$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf15

cf17:
	LOCATE 10, 44
        CALL inpnew(develop.colour$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf16

cf18:
	LOCATE 10, 55
        CALL inpnew(develop.batch$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf17

cf19:
	LOCATE 10, 66
        CALL inpnew(develop.report$, 110!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf18


	i% = 1

cf88:
	DO
		IF i% < 1 THEN GOTO cf19
		IF i% > 12 THEN i% = 1
		LOCATE 12 + i% - 1, 2
		IF i% = 1 OR i% = 5 OR i% = 9 THEN
			in$ = MID$(develop.text$(i%), 13)
			LOCATE 12 + i% - 1, 14
			CALL inpnew(in$, 166, updwn%, "13,59-60")
			MID$(develop.text$(i%), 13, 66) = in$ + SPACE$(99)
			ELSE
			CALL inpnew(develop.text$(i%), 178, updwn%, "13,59-60")
			END IF
		IF updwn% = 59 THEN GOTO x.change
		IF updwn% = 60 THEN i% = i% - 1
		IF updwn% = 13 THEN i% = i% + 1
		LOOP
x.change:
	IF rec% >= 1 AND rec% <= alast% THEN
	PUT #74, rec%, develop
	END IF

END SUB

SUB dsply (rec%, updwn%) STATIC
	alast% = LOF(74) / LEN(develop)
	IF rec% < 1 THEN rec% = 1
	IF rec% > alast% + 1 THEN rec% = adlast%
	IF rec% < 1 THEN GOTO x.dsply
	GET #74, rec%, develop
	COLOR 2, 0
	LOCATE 3, 2: PRINT USING "ÄÄÄÄÄÄCustomer Search..>\     \ÃÄÄÄÄÄÄÄÄÄ³ÄÄÄÄÄÄIncident Number...:####ÄÄÄÄÄÄ"; "     "; develop.no%
	LOCATE 4, 3: PRINT USING "Name....>& ³..>&"; develop.Name$; develop.cName$
	LOCATE 5, 3: PRINT USING "Address.>&      ³..>&"; develop.Addr$; develop.cAddr$
	LOCATE 6, 3: PRINT USING "Suburb..>& &      ³..>& &"; develop.sub$; develop.pcode$; develop.csub$; develop.cpcode$
	LOCATE 7, 3: PRINT USING "Phone/F.>&      &     ³..>&      &"; develop.phone$; develop.fax$; develop.cphone$; develop.cfax$
	LOCATE 8, 2: PRINT STRING$(78, "Ä")
	LOCATE 9, 2:  PRINT USING "   Opened ³ Closed ³ Type     ³ Product  ³  Colour  ³  Batch.  ³ Report   ³!"; " ";
	LOCATE 10, 2: PRINT USING "  \      \³\      \³\        \³\        \³\        \³\        \³\        \³!"; develop.opened$; develop.closed$; develop.type$; develop.product$; develop.colour$; develop.batch$; develop.report$;
	LOCATE 11, 2: PRINT STRING$(78, "Ä")
	MID$(develop.text$(1), 1, 13) = " Problem  : "
	MID$(develop.text$(5), 1, 12) = " Report.  : "
	MID$(develop.text$(9), 1, 12) = " Action.  : "
	FOR i% = 1 TO 12
	LOCATE 12 + i% - 1, 2: PRINT USING "&"; develop.text$(i%)
	NEXT
x.dsply:
END SUB

SUB rdelete (rec%, auto$, updwn%) STATIC
   IF auto$ <> "Y" THEN
        CALL inpnew(a$, 101!, updwn%, "59,68")
	GOTO x.delete
	END IF

   develop.Name$ = SPACE$(99)
   develop.Addr$ = SPACE$(99)
   develop.sub$ = SPACE$(99)
   develop.pcode$ = SPACE$(99)
   develop.opened$ = SPACE$(99)
   develop.closed$ = SPACE$(99)
   FOR i% = 1 TO 12: develop.text$(i%) = SPACE$(99): NEXT
   PUT #74, rec%, develop

x.delete:
END SUB

SUB rinsert (rec%)

found% = 0
rec% = 1
GET #74, rec%, develop
DO WHILE NOT EOF(74)
	IF develop.no% <> rec% THEN found% = -1
	GET #74, , develop: rec% = rec% + 1
	LOOP

	IF rec% <> develop.no% THEN
		auto$ = "Y"
		CALL rdelete(rec%, auto$, updwn%)
		develop.no% = rec%
		PUT #74, rec%, develop
		END IF




END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB
