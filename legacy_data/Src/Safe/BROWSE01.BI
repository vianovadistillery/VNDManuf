REM SUB browse.idx (firstonscreen%, ch1%, ch2%) STATIC
	max% = LOF(ch1%) / 7
	maxbpage% = 20
	bbtm$ = " F1-Return.      F3-Search       F5-Swap information     F7-Totals    "
	GOSUB binit
	bdatatype$ = "name"
	xsearch$ = ""
	btype$ = "keyed"
	GOSUB bsetfilekey
	skey$ = SPACE$(LEN(filekey$))
	'//////////////////////////////////////////////////////
	'>>>>> B R O W S E   T H E   F I L E
	'//////////////////////////////////////////////////////
	CALL setup(bheading$)
	CALL prtbtm(bbtm$)
	rec2% = firstonscreen%
	GOSUB b.dsply
	'>>>>> whats the next record to browse from
2540
	LOCATE 2, 21: COLOR 7, 0: PRINT "ÍÍµ"; : LOCATE , 49: PRINT "ÆÍÍ": COLOR 2, 0
	IF btype$ = "keyed" THEN
		COLOR 2, 0
		LOCATE 2, 24: PRINT "From key ..........>";
		LOCATE 2, 44
		CALL inpnew(keyed$, 205!, updwn%, "13,59-61,63,65,72-73,80-81")
		keyed$ = UCASE$(keyed$)
		IF VAL(keyed$) > 0 THEN arrival$ = keyed$: keyed$ = "": btype$ = "arrival"
		COLOR 2, 0
	ELSE
		COLOR 2, 0
		LOCATE 2, 24: PRINT "From number........>";
		LOCATE 2, 44
		CALL inpnew(arrival$, 205!, updwn%, "13,59-61,63,65,72-73,80-81")
		arrival$ = UCASE$(arrival$)
		IF VAL(arrival$) = 0 AND LEN(arrival$) > 1 THEN keyed$ = arrival$: arrival$ = "": btype$ = "keyed"
		COLOR 2, 0
	END IF

	IF updwn% = 61 THEN
		COLOR 2, 0
		LOCATE 2, 24: PRINT "Search.>";
		LOCATE 2, 32
		CALL inpnew(xsearch$, 117!, updwn%, "13,59-60,63,65,72-73,80-81")
		COLOR 2, 0
		arrival$ = "1"
		btype$ = "arrival"
		updwn% = 13
	END IF

	SELECT CASE updwn%
	CASE 59: GOTO bret

	CASE 13:
		IF btype$ = "keyed" THEN
			LSET skey$ = keyed$
			GOSUB bsearchindex
			SELECT CASE ch2%

			CASE 43: rec2% = CVI(cusx.wrrn$)
			CASE 44: rec2% = CVI(supx.wrrn$)
			CASE 64: rec2% = CVI(whox.wrrn$)

			CASE ELSE
			END SELECT
		ELSE
			rec2% = VAL(arrival$)
		END IF

		GOSUB b.dsply

	CASE 63:                        'Swap data typer
		SELECT CASE bdatatype$
		CASE "name": bdatatype$ = "data"
		CASE "data": bdatatype$ = "name"
		CASE ELSE: bdatatype$ = "name"
		END SELECT
		rec2% = firstonscreen% - maxbpage%
		GOSUB b.dsply
	CASE 65:
		t90@ = 0: t60@ = 0: t30@ = 0: tcur@ = 0
		rec% = 1
		GET #ch2%, rec%, who
		DO WHILE NOT EOF(ch2%)
			t90@ = t90@ + CVS(who.s90$)
			t60@ = t60@ + CVS(who.s60$)
			t30@ = t30@ + CVS(who.s30$)
			tcur@ = tcur@ + CVS(who.scur$)
			GET #ch2%, , who: rec% = rec% + 1
			LOOP
			ttotal@ = t90@ + t60@ + t30@ + tcur@
			LOCATE 24, 2
			PRINT USING "  &   $$###,###.## $$###,###.## $$###,###.## $$###,###.## $$####,###.##"; "Total"; t90@; t60@; t30@; tcur@; ttotal@;
			LOCATE 1, 1
	CASE 72:
			IF firstonscreen% < 1 THEN firstonscreen% = 1
			rec2% = firstonscreen% - 1
			GOSUB b.dsply
	CASE 80:
			IF firstonscreen% < 1 THEN firstonscreen% = 1
			rec2% = firstonscreen% + 1
			GOSUB b.dsply

	CASE 81:                'Next Page
		GOSUB b.dsply
	CASE 73:                'Prev page
		SELECT CASE btype$
		CASE "keyed"
			IF firstonscreen% < 1 THEN firstonscreen% = 1
			SELECT CASE ch2%
			CASE 43: GET #ch2%, firstonscreen%, cus
			CASE 44: GET #ch2%, firstonscreen%, sup
			CASE 64: GET #ch2%, firstonscreen%, who
			CASE ELSE
			END SELECT

			GOSUB bsetfilekey
			skey$ = filekey$
			GOSUB bsearchindex
			rec1% = rec1% - maxbpage%
			IF rec1% < 1 THEN rec1% = 1

			SELECT CASE ch2%
			CASE 43:
					GET #ch1%, rec1%, cusx
					rec2% = CVI(cusx.wrrn$)
			CASE 44:
					GET #ch1%, rec1%, supx
					rec2% = CVI(supx.wrrn$)
			CASE 64:
					GET #ch1%, rec1%, whox
					rec2% = CVI(whox.wrrn$)
			CASE ELSE
			END SELECT

		CASE "arrival"
			rec2% = firstonscreen% - maxbpage%
		END SELECT
		GOSUB b.dsply
	CASE ELSE
	END SELECT
GOTO 2540
'/////////////////////////////////////////////////////////////////////////////
'>>>      L I S T   A   P A G E
'/////////////////////////////////////////////////////////////////////////////
b.dsply:
	IF rec2% < 1 OR rec2% > max% THEN rec2% = 1
	COLOR 6, 0: LOCATE 3, 2
	IF bdatatype$ = "name" THEN PRINT bheadingname$ ELSE PRINT bheadingdata$
	COLOR 2, 0

	SELECT CASE ch2%
	CASE 43: GET #ch2%, rec2%, cus
	CASE 44: GET #ch2%, rec2%, sup
	CASE 64: GET #ch2%, rec2%, who
	CASE ELSE
	END SELECT

	'>> The index must be kept in sync
	saverec2% = rec2%
	GOSUB bsetfilekey
	skey$ = filekey$
	GOSUB bsearchindex
	SELECT CASE ch2%
	CASE 43:
		rec2% = CVI(cusx.wrrn$)
		IF rec2% < 1 OR rec2% > max% THEN GET #ch1%, 1, cusx
		rec2% = CVI(cusx.wrrn$)
	CASE 44:
		rec2% = CVI(supx.wrrn$)
		IF rec2% < 1 OR rec2% > max% THEN GET #ch1%, 1, supx
		rec2% = CVI(supx.wrrn$)
	CASE 64:
		rec2% = CVI(whox.wrrn$)
		IF rec2% < 1 OR rec2% > max% THEN GET #ch1%, 1, whox
		rec2% = CVI(whox.wrrn$)

	CASE ELSE
	END SELECT

	IF rec2% < 1 OR rec2% > max% THEN GOTO x.B.dsply
	IF rec2% <> saverec2% THEN rec2% = saverec2%: SOUND 50, 1
	firstonscreen% = 0
	n% = 0
	SELECT CASE ch2%
	CASE 43: GET #ch2%, rec2%, cus
	CASE 44: GET #ch2%, rec2%, sup
	CASE 64: GET #ch2%, rec2%, who
	CASE ELSE
	END SELECT

	LOCATE 4, 2
	missed% = 0
	DO WHILE n% < maxbpage% AND rec2% >= 1 AND rec2% <= max%
		SELECT CASE ch2%
		CASE 43: GET #ch2%, rec2%, cus
		CASE 44: GET #ch2%, rec2%, sup
		CASE 64: GET #ch2%, rec2%, who
		CASE ELSE
		END SELECT

		GOSUB btest
		IF ok% THEN
			'> Save the first record on screen
			IF firstonscreen% = 0 THEN firstonscreen% = rec2%
			LOCATE , 2
			SELECT CASE ch2%
			CASE 43:
					xxx% = CVI(cus.sno$)
					IF xxx% >= 1000 THEN xxx% = xxx% - 1000
					IF xxx% >= 1000 THEN xxx% = xxx% - 1000
					scur! = CVS(cus.scur$): s30! = CVS(cus.s30$): s60! = CVS(cus.s60$): s90! = CVS(cus.s90$)
					stotal! = scur! + s30! + s60! + s90!
					IF bdatatype$ = "name" THEN
					phone$ = MID$(cus.sphone$, 1, 13)
					PRINT USING "### & & & &! &"; xxx%; LEFT$(cus.sname$, 35); LEFT$(cus.scont$, 16); phone$; cus.search$; cus.stype$; cus.active$
					ELSE
					PRINT USING "### &   $$###,###.## $$###,###.## $$###,###.## $$###,###.## $$####,###.##"; xxx%; cus.search$ + cus.stype$; s90!; s60!; s30!; scur!; stotal!
					END IF
			CASE 44:
					xxx% = CVI(sup.sno$)
					IF xxx% >= 1000 THEN xxx% = xxx% - 1000
					IF xxx% >= 1000 THEN xxx% = xxx% - 1000
					scur! = CVS(sup.scur$): s30! = CVS(sup.s30$): s60! = CVS(sup.s60$): s90! = CVS(sup.s90$)
					stotal! = scur! + s30! + s60! + s90!
					IF bdatatype$ = "name" THEN
					phone$ = MID$(sup.sphone$, 1, 13)
					PRINT USING "### & & & && &"; xxx%; LEFT$(sup.sname$, 35); LEFT$(sup.scont$, 16); phone$; sup.search$; sup.stype$; sup.active$
					ELSE
					PRINT USING "### &   $$###,###.## $$###,###.## $$###,###.## $$###,###.## $$####,###.##"; xxx%; sup.search$ + sup.stype$; s90!; s60!; s30!; scur!; stotal!
					END IF
			CASE 64:
					xxx% = CVI(who.sno$)
					IF xxx% >= 1000 THEN xxx% = xxx% - 1000
					IF xxx% >= 1000 THEN xxx% = xxx% - 1000
					scur! = CVS(who.scur$): s30! = CVS(who.s30$): s60! = CVS(who.s60$): s90! = CVS(who.s90$)
					stotal = scur! + s30! + s60! + s90!
					IF bdatatype$ = "name" THEN
					phone$ = MID$(who.sphone$, 1, 13)
					PRINT USING "### & & & &! &"; xxx%; LEFT$(who.sname$, 35); LEFT$(who.scont$, 16); phone$; who.search$; who.stype$; who.active$
					ELSE
					PRINT USING "### &   $$###,###.## $$###,###.## $$###,###.## $$###,###.## $$####,###.##"; xxx%; who.search$ + who.stype$; s90!; s60!; s30!; scur!; stotal!
					END IF
			CASE ELSE

			END SELECT
			n% = n% + 1
			END IF
		'>>> Read area for loop
		IF btype$ = "keyed" THEN
			SELECT CASE ch2%
			CASE 43:
				GET #ch1%, , cusx
				rec2% = CVI(cusx.wrrn$)
			CASE 44:
				GET #ch1%, , supx
				rec2% = CVI(supx.wrrn$)
			CASE 64:
				GET #ch1%, , whox
				rec2% = CVI(whox.wrrn$)

			CASE ELSE
			END SELECT

			ELSE
			rec2% = rec2% + 1
			END IF
	LOOP
	'Clear out to the end of screen
	rec% = 0
	FOR i% = n% + 1 TO maxbpage%
		IF rec% THEN
			 ttotal = scur! + s30! + s60! + s90!
			 PRINT USING "### &   $$###,###.## $$###,###.## $$###,###.## $$###,###.## $$####,###.##"; xxx%; "Total"; t90!; t60!; t30!; tcur!; ttotal!
			 rec% = 0
			 END IF
		LOCATE , 2
		PRINT SPACE$(78)
		NEXT
x.B.dsply:
RETURN
'//////////////////////////////////////////////////////////////////////////
'>>>>> Lookup index file Passed skey$ Returns SKEY, 0 if not found <<<<<
'>>>>> SKEY1, one after insertion place                               <<<<<
'//////////////////////////////////////////////////////////////////////////
bsearchindex:
	skey = 0: skey1 = 0: found% = 0
	IF skey$ = "     " THEN skey1 = 0: RETURN
	s% = 0: e% = max%
bsearchagain:
	rec1% = (e% - s%) / 2 + s%
	IF rec1% = 0 THEN skey = 0: skey1 = s%: RETURN
	SELECT CASE ch2%
	CASE 43:
		GET #ch1%, rec1%, cusx
		IF CVI(cusx.wrrn$) = 0 THEN LSET cusx.wcde$ = STRING$(99, CHR$(255))

		aaa$ = cusx.wcde$ + wtyp$
		IF cusx.wcde$ + wtyp$ = skey$ THEN skey = rec1%: skey1 = rec1%: found% = -1: RETURN
		IF e% - s% = 1 THEN skey = 0: skey1 = s%: RETURN
		IF cusx.wcde$ + wtyp$ < skey$ THEN s% = rec1%: GOTO bsearchagain
		IF cusx.wcde$ + wtyp$ > skey$ THEN e% = rec1%: GOTO bsearchagain
	CASE 44:
		GET #ch1%, rec1%, supx
		IF CVI(supx.wrrn$) = 0 THEN LSET supx.wcde$ = STRING$(99, CHR$(255))

		aaa$ = supx.wcde$ + wtyp$
		IF supx.wcde$ + wtyp$ = skey$ THEN skey = rec1%: skey1 = rec1%: found% = -1: RETURN
		IF e% - s% = 1 THEN skey = 0: skey1 = s%: RETURN
		IF supx.wcde$ + wtyp$ < skey$ THEN s% = rec1%: GOTO bsearchagain
		IF supx.wcde$ + wtyp$ > skey$ THEN e% = rec1%: GOTO bsearchagain
	CASE 64:
		GET #ch1%, rec1%, whox
		IF CVI(whox.wrrn$) = 0 THEN LSET whox.wcde$ = STRING$(99, CHR$(255))

		aaa$ = supx.wcde$ + wtyp$
		IF whox.wcde$ + wtyp$ = skey$ THEN skey = rec1%: skey1 = rec1%: found% = -1: RETURN
		IF e% - s% = 1 THEN skey = 0: skey1 = s%: RETURN
		IF whox.wcde$ + wtyp$ < skey$ THEN s% = rec1%: GOTO bsearchagain
		IF whox.wcde$ + wtyp$ > skey$ THEN e% = rec1%: GOTO bsearchagain

	CASE ELSE
	END SELECT

RETURN
'//////////////////////////////////////////////////////////////////////////
'>>>
'//////////////////////////////////////////////////////////////////////////
binit:
	bheading$ = "BROWSE CUSTOMER FILE"
	btype$ = "keyed"
	btype$ = "arrival"
	bheadingname$ = "No. Supplier/Customer name              Contact              Telephone    KEY"
	bheadingdata$ = "No. Search          90+ days     60 Days     30 Days     Current        Total"

RETURN
'>>> -
bsetfilekey:
	filekey$ = "12345"
	SELECT CASE ch2%
	CASE 43: LSET filekey$ = cus.search$ + cus.stype$
	CASE 44: LSET filekey$ = sup.search$ + sup.stype$
	CASE 64: LSET filekey$ = who.search$ + who.stype$
	CASE ELSE
	END SELECT

RETURN
'>>> -
btest:
	SELECT CASE ch2%
	CASE 43:
		ok% = -1
		IF CVI(cus.sno$) <> rec2% THEN ok% = 0
		IF cus.sdate$ <= SPACE$(8) THEN ok% = 0 '.dc
	CASE 44:
		ok% = -1
		IF CVI(sup.sno$) <> rec2% THEN ok% = 0
		IF sup.sdate$ <= SPACE$(8) THEN ok% = 0 '.dc
	CASE 64:
		ok% = -1
		IF CVI(who.sno$) <> rec2% THEN ok% = 0
		IF who.sdate$ <= SPACE$(8) THEN ok% = 0 '.dc
	CASE ELSE
	END SELECT

	IF ok% AND xsearch$ > "" THEN
		ok1% = 0
		tmp$ = LCASE$(xsearch$)
		'??
		SELECT CASE ch2%
		CASE 43:
		IF ok1% = 0 AND INSTR(LCASE$(cus.sname$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(cus.saddr$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(cus.saddr2$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(cus.email$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(cus.www$), tmp$) > 0 THEN ok1% = -1
		CASE 44:
		IF ok1% = 0 AND INSTR(LCASE$(sup.sname$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(sup.saddr$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(sup.saddr2$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(sup.email$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(sup.www$), tmp$) > 0 THEN ok1% = -1
		CASE 64:
		IF ok1% = 0 AND INSTR(LCASE$(who.sname$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(who.saddr$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(who.saddr2$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(who.email$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(who.www$), tmp$) > 0 THEN ok1% = -1
		CASE ELSE
		END SELECT

		'??

		IF NOT ok1% THEN
			ok% = 0
		END IF
	END IF

RETURN
bret:

REM END SUB

