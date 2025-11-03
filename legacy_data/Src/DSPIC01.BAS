DECLARE SUB setact ()
DECLARE SUB listuse (rec%)
DECLARE SUB searchindex14 (keyin$, chi%, found%)
DECLARE SUB searchindex (keyin$, chi%, found%)
'.dc - Complete
'/////////////////////////////////////////////////////////////////////
'////////////////////    DSPIC01      ////////////////////////////////
'/////////////////////////////////////////////////////////////////////
DECLARE SUB browse (first.on.screen%, ch1%)
	CONST indent% = 14
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "DSMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CLOSE
	db.or.cr$ = "DB"
	db.or.cr$ = ENVIRON$("DB.OR.CR$")
	cr% = INSTR(COMMAND$, "/CR")
	IF cr% > 0 THEN db.or.cr$ = "CR"

	 IF db.or.cr$ = "CR" THEN
		ch% = 44: apgm$ = "CSMENU"
		ELSE
		ch% = 43: apgm$ = "DSMENU"
	 END IF

	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\PICKUP.INC'
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\cus.INC'
	'$INCLUDE: '\tpmanuf\src\PICKUPX.INC'

	'rec% = 1
	'GET #50, rec%, pickup
	'DO WHILE NOT EOF(50)
	'IF MID$(pickup.pphone2$, 3, 1) = "-" THEN
	'was$ = pickup.pphone2$
	'pickup.pphone2$ = " " + MID$(was$, 1, 2) + "-" + MID$(was$, 4, 4) + "-" + MID$(was$, 8, 4)
	'PUT #50, rec%, pickup
	'END IF
	'
	'GET #50, , pickup: rec% = rec% + 1
	'LOOP
	'END

start:
	btm$ = "F1-Exit        F4-Delete         F6-Browse     F7-Index F8-list F10-Change"
	CALL setup("UPDATE PICKUP ADDRESS")
	COLOR 0, 3
	LOCATE 25, 4: PRINT btm$;
get.num:
	COLOR 2, 0
	LOCATE 3, indent%: PRINT "Enter pickup number....> "
	IF NOT skip% THEN
		LOCATE 3, indent% + 24
		rec$ = ""
		CALL inpnew(rec$, 103!, updwn%, "13,59-62,64-66,68," + ALT$): GOSUB ALT
		ELSE
		skip% = 0
		updwn% = 13
		END IF
	SELECT CASE updwn%
	CASE 59: CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
	CASE 61: CALL setact
	CASE 62: GOSUB delrec
	CASE 64: CALL browse(first.on.screen%, 50)
		rec$ = MID$(STR$(first.on.screen%), 2)
		rec% = VAL(rec$)
		skip% = -1
		GOTO start
	CASE 65: CLOSE : bpgm$ = "DSPIC01X": CALL EXITPGM(bpgm$): CHAIN bpgm$
	CASE 66: CALL listuse(rec%)
	CASE 68: GOSUB chg
	CASE 13:
		IF LEN(rec$) = 0 THEN
			rec% = rec% + 1
			ELSE
			rec% = VAL(rec$)
			END IF
		GOSUB dsply
	CASE ELSE
	END SELECT
	GOTO get.num
'/////////////////////////////////////////////////////////////////////
'>>>>> Get record and display
'/////////////////////////////////////////////////////////////////////
dsply:
	IF rec% < 1 OR rec% > 999 THEN GOTO x.dsply
	GET #50, rec%, pickup
	IF CVI(pickup.pno$) <> rec% THEN : delauto$ = "y": GOSUB delrec
	LOCATE 5, indent%: PRINT USING "Pick up Number....>####    Activity..:!"; rec%; pickup.pactive$
	LOCATE 7, indent%: PRINT USING "Transport Company.>\                            \"; pickup.pname1$
	LOCATE 8, indent%: PRINT USING "Phone.............>\                            \"; pickup.pphone1$
	LOCATE 10, indent%: PRINT USING "Depot.............>\                            \"; pickup.pname2$
	LOCATE 11, indent%: PRINT USING " ' '  Phone.......>\                            \"; pickup.pphone2$
	LOCATE 12, indent%: PRINT USING " ' '  Address.....>\                            \"; pickup.pname3$
	LOCATE 13, indent%: PRINT USING " ' '  Suburb......>\                            \"; pickup.pname4$

	'IF MID$(pickup.pphone1$, 1, 2) = "03" THEN
	'IF MID$(pickup.pphone1$, 4, 4) <> "9" THEN
	'    a1$ = MID$(pickup.pphone1$, 1, 3) + "9" + MID$(pickup.pphone1$, 4)
	'    pickup.pphone1$ = a1$
	'    PUT #50, rec%, pickup
	'    END IF
	'    END IF
x.dsply:
RETURN
'//////////////////////////////////////////////////////////////////////////
'>>>>> C H A N G E
'//////////////////////////////////////////////////////////////////////////
chg:
	IF rec% < 1 OR rec% > 999 THEN GOTO x.chg
cf1:
	LOCATE 7, indent% + 19
	a$ = pickup.pname1$
	CALL inpnew(a$, 130!, updwn%, "13,59-61")
	pickup.pname1$ = a$
	IF updwn% = 59 THEN GOTO upd.chg
	IF updwn% = 60 THEN GOTO cf1
cf2:
	LOCATE 8, indent% + 19
	a1$ = MID$(pickup.pphone1$, 1, 3)
	a2$ = MID$(pickup.pphone1$, 5, 4)
	a3$ = MID$(pickup.pphone1$, 10, 4)
	CALL inpnew(a1$, 103!, updwn%, "13,59-61")
	IF updwn% = 13 THEN
		LOCATE 8, indent% + 23
		CALL inpnew(a2$, 104!, updwn%, "13,59-61")
		END IF
	IF updwn% = 13 THEN
		LOCATE 8, indent% + 28
		CALL inpnew(a3$, 104!, updwn%, "13,59-61")
		END IF
	LSET pickup.pphone1$ = a1$ + "-" + a2$ + "-" + a3$

	IF updwn% = 59 THEN GOTO upd.chg
	IF updwn% = 60 THEN GOTO cf1
cf3:
	LOCATE 10, indent% + 19
	a$ = pickup.pname2$
	CALL inpnew(a$, 130!, updwn%, "13,59-61")
	LSET pickup.pname2$ = a$
	IF updwn% = 59 THEN GOTO upd.chg
	IF updwn% = 60 THEN GOTO cf2
cf4:
	LOCATE 11, indent% + 19
	a1$ = MID$(pickup.pphone2$, 1, 3)
	a2$ = MID$(pickup.pphone2$, 5, 4)
	a3$ = MID$(pickup.pphone2$, 10, 4)
	CALL inpnew(a1$, 103!, updwn%, "13,59-61")
	IF updwn% = 13 THEN
		LOCATE 11, indent% + 23
		CALL inpnew(a2$, 104!, updwn%, "13,59-61")
		END IF
	IF updwn% = 13 THEN
		LOCATE 11, indent% + 28
		CALL inpnew(a3$, 104!, updwn%, "13,59-61")
		END IF
	LSET pickup.pphone2$ = a1$ + "-" + a2$ + "-" + a3$

	IF updwn% = 59 THEN GOTO upd.chg
	IF updwn% = 60 THEN GOTO cf3
cf5:
	LOCATE 12, indent% + 19
	a$ = pickup.pname3$
	CALL inpnew(a$, 130!, updwn%, "13,59-61")'??
	LSET pickup.pname3$ = a$
	IF updwn% = 59 THEN GOTO upd.chg
	IF updwn% = 60 THEN GOTO cf4

cf6:
	LOCATE 13, indent% + 19
	a$ = pickup.pname4$
	CALL inpnew(a$, 130!, updwn%, "13,59-61")
	LSET pickup.pname4$ = a$
	IF updwn% = 59 THEN GOTO upd.chg
	IF updwn% = 60 THEN GOTO cf5

upd.chg:
	pickup.pno$ = MKI$(rec%)
	PUT #50, rec%, pickup
x.chg:
RETURN
'//////////////////////////////////////////////////////////////////////////
'>>>>>
'//////////////////////////////////////////////////////////////////////////
delrec:
	IF rec% < 1 OR rec% > 999 THEN GOTO x.delrec
	IF delauto$ = "y" THEN
		updwn% = 68
		ELSE
		COLOR 0, 7: LOCATE 25, 1: PRINT SPACE$(80);
		COLOR 0, 7: LOCATE 25, 4: PRINT "F1-Exit"; : LOCATE 25, 68: PRINT "F10-Continue";
		COLOR 2, 0: LOCATE 1, 1
		CALL inpnew(a$, 0!, updwn%, "59,68")
		COLOR 3, 3: LOCATE 25, 1: PRINT SPACE$(80);
		LOCATE 25, 1: COLOR 0, 3: PRINT btm$;
		LOCATE 1, 1
		END IF
	delauto$ = "N"
	IF updwn% = 68 THEN
		LSET pickup.pno$ = MKI$(0)
		LSET pickup.pname1$ = SPACE$(99)
		LSET pickup.pname2$ = SPACE$(99)
		LSET pickup.pname3$ = SPACE$(99)
		LSET pickup.pname4$ = SPACE$(99)
		LSET pickup.pphone1$ = SPACE$(99)
		LSET pickup.pphone2$ = SPACE$(99)
		LSET pickup.pactive$ = " "
		PUT #50, rec%, pickup
		END IF
RETURN
x.delrec:
RETURN

'>>>>> B R O W S E   T H E   F I L E
SUB browse (first.on.screen%, ch1%) STATIC
	max% = LOF(ch1%) / 122
	max.b.page% = 20
	b.btm$ = "F1-Exit                    F3-List by name  "
	CALL setup("BROWSE THE FILE")
	COLOR 0, 3: LOCATE 25, 4: PRINT b.btm$; : LOCATE 25, 71: PRINT CHR$(24); CHR$(25); "-Move";
	COLOR 2, 0
	COLOR 6, 0: LOCATE 3, 2
	PRINT "No. Transport Company.............|Transport Depot...............|Address...."
	COLOR 2, 0
	order.by$ = "number"
	GOSUB dsply.b
2540     '>>>>> Get next record to browse from
	LOCATE 2, 21: COLOR 7, 0: PRINT "ÍÍµ"; : LOCATE , 49: PRINT "ÆÍÍ": COLOR 2, 0
	COLOR 2, 0
	IF order.by$ = "number" THEN
		LOCATE 2, 24: PRINT "From number........>";
		ELSE
		LOCATE 2, 24: PRINT "Start from name....>";
		END IF
	LOCATE 2, 44
	CALL inpnew(bkey$, 205!, updwn%, "13,59,61,72,73,80,81")
	COLOR 2, 0
	SELECT CASE updwn%
		 CASE 59: GOTO bret
		 CASE 13:
			 IF order.by$ = "number" THEN rec% = VAL(bkey$)
			 IF order.by$ = "name" THEN
					keyin$ = bkey$
					CALL searchindex14(keyin$, 51, found%)
					rec% = CVI(PICKUPX.pxrrn$)
					END IF
			GOSUB dsply.b
		 CASE 61:
			SELECT CASE order.by$
			CASE IS = "number": order.by$ = "name"
			CASE IS = "name": order.by$ = "number"
			CASE ELSE
			END SELECT
		 CASE 72:                'UP  arrow
			rec% = first.on.screen% - 1
			GOSUB dsply.b
		 CASE 73:                'PGUP
			rec% = first.on.screen% - max.b.page%
			GOSUB dsply.b
		 CASE 80:                '**** DN arrow
			rec% = first.on.screen% + 1
			GOSUB dsply.b
		 CASE 81:                '**** PGDN
			GOSUB dsply.b
		 CASE ELSE
	END SELECT
	GOTO 2540
bret:
EXIT SUB
'/////////////////////////////////////////////////////////////////////////////
'>>>      L I S T   A   P A G E
'/////////////////////////////////////////////////////////////////////////////
dsply.b:
	IF rec% < 1 OR rec% > max% THEN rec% = 1
	first.on.screen% = 0
	n% = 0
	IF order.by$ = "name" THEN
		recx% = LOC(51)
		rec% = CVI(PICKUPX.pxrrn$)
		IF rec% < 1 OR rec% > max% THEN rec% = 1
		END IF

	GET #ch1%, rec%, pickup

	LOCATE 4, 2
	missed% = 0
	DO WHILE n% < max.b.page% AND rec% >= 1 AND rec% <= max%
		ok% = 0
		IF CVI(pickup.pno$) = rec% THEN ok% = -1
		IF ok% THEN
			'> Save the first record on screen
			IF first.on.screen% = 0 THEN first.on.screen% = rec%
			LOCATE , 2
			PRINT USING "### &|&|&"; CVI(pickup.pno$); pickup.pname1$; pickup.pname2$; LEFT$(pickup.pname3$, 12)'??
			n% = n% + 1
			END IF

		'>>> Read area for loop
		rec% = rec% + 1
		GET #ch1%, rec%, pickup
		IF order.by$ = "name" THEN
			recx% = recx% + 1
			GET #51, recx%, PICKUPX
			rec% = CVI(PICKUPX.pxrrn$)
			IF rec% > 0 AND rec% <= max% THEN
				GET #ch1%, rec%, pickup
				ELSE
				rec% = max% + 1
				END IF
			END IF

	LOOP
	'Clear out to the end of screen
	FOR i% = n% + 1 TO max.b.page%
		LOCATE , 2
		PRINT SPACE$(78)
		NEXT
x.dsply.b:
RETURN
END SUB

SUB listuse (rec%)
	COLOR 6, 0: LOCATE 14, 2
	PRINT "Code   *-------Customer Name-------*        (Pickup addres usage)"
	COLOR 2, 0

	lin% = 999
	trec% = 1
	GET #43, trec%, cus
	DO WHILE NOT EOF(43)
		test% = VAL(MID$(cus.spname$, 1, 3))
		IF CVI(cus.sno$) = trec% THEN
		IF test% = rec% THEN
			lin% = lin% + 1
			IF lin% > 22 THEN
				pag% = pag% + 1
					IF pag% > 1 THEN
																				LOCATE 22, 78: CALL inpnew(a$, 1!, updwn%, "13,59,60")
					IF updwn% = 59 THEN GOTO x.lstuse
					IF updwn% = 60 THEN GOTO x.lstuse
					END IF
				lin% = 15
				END IF

			COLOR 2, 0
			LOCATE lin%, 2: PRINT USING "\    \ \                           \ &"; cus.search$ + cus.stype$; cus.sname$; SPACE$(25)
			END IF
		END IF


		GET #43, , cus: trec% = trec% + 1
		LOOP
x.lstuse:

END SUB

SUB searchindex14 (keyin$, chi%, found%) STATIC
	keyin$ = UCASE$(keyin$)
	filein$ = keyin$
	found% = 0
	max% = LOF(chi%) / 16
	s% = 0: e% = max%

SEARCHAGAIN:
	p% = (e% - s%) / 2 + s%
	IF p% = 0 THEN GOTO X.SEARCHINDEX
	GET #chi%, p%, PICKUPX
	LSET filein$ = PICKUPX.pxcde$

	IF CVI(PICKUPX.pxrrn$) = 0 THEN LSET filein$ = STRING$(99, CHR$(255))
	IF filein$ = keyin$ THEN found% = -1: GOTO X.SEARCHINDEX
	IF filein$ < keyin$ AND s% <> p% THEN s% = p%: GOTO SEARCHAGAIN
	IF filein$ > keyin$ AND e% <> p% THEN e% = p%: GOTO SEARCHAGAIN

X.SEARCHINDEX:
'END SUB

END SUB

SUB setact
	rec% = 1
	GET #50, rec%, pickup
	DO WHILE NOT EOF(50)
	pickup.pactive$ = "S"
	PUT #50, rec%, pickup
	GET #50, , pickup: rec% = rec% + 1
	LOOP



	trec% = 1
	GET #43, trec%, cus
	DO WHILE NOT EOF(43)

		IF CVI(cus.sno$) = trec% THEN
			rec% = VAL(cus.spname)

			IF rec% >= 1 AND rec% < 999 THEN
			GET #50, rec%, pickup
				IF CVI(pickup.pno) = rec% THEN
					pickup.pactive$ = "A"
					PUT #50, rec%, pickup
				END IF
			END IF
		END IF

		IF trec% MOD 100 = 0 THEN CALL sndmsg("Searching..." + STR$(trec%))
		GET #43, , cus: trec% = trec% + 1
		LOOP
		CALL sndmsg("Done.")

x.setact:


END SUB
