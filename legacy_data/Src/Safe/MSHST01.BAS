DECLARE SUB FixHydroxinol ()
DECLARE SUB browse34 (browse34.result%, updwn%)
DECLARE SUB dsply (keyedform$, STDOUT$)
DECLARE SUB dsplycurr (recHdr%)
DECLARE SUB dsplyform (hstrec%, updwn%)
DECLARE FUNCTION format$ (VALUE!, definition$)
DECLARE SUB openup (swapfile%)
DECLARE SUB printform (hstrec%, STDOUT$, ok%)
DECLARE SUB qsort (in$(), in%(), n%)
'/////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>         M S H S T 0 1       <<<<<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'.dc - Complete
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "MSMENU"
'$ INCLUDE: '\tpmanuf\src\pgmerr.INC'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	'$INCLUDE: '\tpmanuf\src\fmhist.inc'
	CLOSE #34
	'$INCLUDE: '\tpmanuf\src\tnhist.inc'
	CLOSE #72
	'$INCLUDE: '\tpmanuf\src\tnthed.inc'
	'$INCLUDE: '\tpmanuf\src\tnthedx.inc'
	'$INCLUDE: '\tpmanuf\src\forhed.inc'
	'$INCLUDE: '\tpmanuf\src\forhedx.inc'

	DIM SHARED mode$, open34%
	DIM SHARED in$(1500), in%(1500)
	DIM SHARED text(50) AS STRING * 78
	DIM SHARED msg$, datafile$, btm$, btm2$
	DIM SHARED maxbrw%, hstrec%
	DIM SHARED brrn%(5001)
	DIM SHARED ch.hdr%

	maxbrw% = 5001
	datafile$ = "Hist."
	datafile$ = "Batch"

	mode$ = "A - F": swapfile% = 0
	CALL openup(swapfile%)

	'stdout$ = "CON"
	STDOUT$ = "c:\tpexe\history.PRN"
	GET #36, 1, msmisc

	'CALL FixHydroxinol
	'END
start:
	CALL setup("LIST HISTORY FILE")
	btm$ = "F1-Exit             F3-Swap files (Tints/Forms)           F6-Browse"
	btm2$ = "F1-Exit               Select Formula"
	CALL prtbtm(btm$)
	COLOR 2, 0
	LOCATE 3, 74: PRINT mode$
	a$ = " "
	LOCATE 3, 26: PRINT "Enter formula...> ";
	LOCATE 3, 43
	CALL inpnew(keyedform$, 3!, updwn%, "13,59,61,64" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN GOTO ENDPGM
	IF updwn% = 61 THEN CALL openup(-1): GOTO start
	IF updwn% = 64 THEN
		CALL browse34(browse34result%, updwn%)
		IF browse34result% > 0 THEN
			idx34% = browse34result%
			rec34% = brrn%(idx34%)
			IF rec34% < 1 OR rec34% > 32000 THEN
				rec34% = 1
			END IF

			GET #34, rec34%, fmhisth1
			keyedform$ = STR$(fmhisth1.form%)
				CALL dsply(keyedform$, STDOUT$)
		END IF
		GOTO start
	END IF
	IF updwn% = 13 THEN
		CALL dsply(keyedform$, STDOUT$)
	END IF

	GOTO start


ENDPGM:
	CLOSE
	CALL EXITPGM(apgm$)
	CHAIN apgm$

SUB browse34 (browse34.result%, updwn%)
	maxrmat% = 32000
	btlast% = LOF(34) / 62
	CALL setup("BROWSE FILE")
	COLOR 6, 0
	LOCATE 4, 2: PRINT "Seq Description................... Batch   Form... Theory  Actual    Date.";
	COLOR 0, 3: LOCATE 25, 2: PRINT " F1-Exit    F3-Alpha Search      F7-Search on Recipe Number    "; : COLOR 2, 0
	COLOR 2, 0
	len.of.browse% = 19
	IF browse34.result% < 1 THEN browse34.result% = 1
	IF browse34.result% > btlast% THEN browse34.result% = btlast%
	s% = browse34.result%
	skip% = -1
	GOSUB loadrrn34


2510
	LOCATE 3, 2: PRINT "Current number.:"; browse34.result%;
	IF NOT skip% THEN
		z$ = ""
		IF updwn% = 61 THEN
			LOCATE 3, 23: PRINT "Search on Name......> ";
			LOCATE 3, 44: CALL inpnew(z$, 125!, updwn%, "13,59-61,63-65,72,73,80,81")
			IF updwn% = 13 THEN updwn% = 61
		ELSE
			LOCATE 3, 23: PRINT "Browse from number..> ";
			LOCATE 3, 44: CALL inpnew(z$, 204!, updwn%, "13,59-61,63-65,72,73,80,81")
		END IF
	END IF
	skip% = 0

	LOCATE 3, 44
	SELECT CASE updwn%
	CASE 59: GOTO x.browse34
	CASE 61: IF RTRIM$(z$) > "" THEN GOSUB loadrrn34
	CASE 65: GOSUB loadrrn34
	CASE 72: startrrn% = startrrn% - 1
	CASE 73: startrrn% = startrrn% - len.of.browse%
	CASE 80: startrrn% = startrrn% + 1
	CASE 81: startrrn% = startrrn% + len.of.browse%
	CASE 13: startrrn% = VAL(z$)

	CASE ELSE
	END SELECT

	GOSUB listpage34
	GOTO 2510
'>>----------------------------------------------------------------
'>> - load
'>>----------------------------------------------------------------
loadrrn34:
	CALL sndmsg("loading..")
	FOR i% = 1 TO maxbrw%: brrn%(i%) = 0: NEXT

	n% = 0
	rec34% = 1
	GET #34, rec34%, fmhisth1

	DO WHILE NOT EOF(34)
		ok% = -1
		IF fmhisth1.form% = 0 THEN ok% = 0
		IF fmhisth1.seq% <> 1 THEN ok% = 0

		IF updwn% = 61 THEN
			IF INSTR(LCASE$(fmhisth1.desc), LCASE$(z$)) <= 0 THEN ok% = 0
		END IF

		IF updwn% = 65 THEN
			wrk% = VAL(z$)
			IF wrk% <> 0 AND fmhisth1.form% <> wrk% THEN ok% = 0
		END IF

		 IF ok% THEN
			n% = n% + 1
			brrn%(n%) = rec34%
			END IF


		IF rec34% MOD 100 = 0 THEN CALL sndmsg("loading.." + STR$(rec34%))
		GET #34, , fmhisth1: rec34% = rec34% + 1
		LOOP
	startrrn% = 1

	CALL sndmsg(""): COLOR 2, 0
RETURN

'>>----------------------------------------------------------------
'>> - display a page (startrrn%)
'>>----------------------------------------------------------------
listpage34:
	wrk% = n% - len.of.browse% + 1: IF wrk% < 1 THEN wrk% = startrrn%
	IF startrrn% > wrk% THEN startrrn% = wrk%
	IF startrrn% < 1 THEN startrrn% = 1

	COLOR 2, 0
	FOR lin% = 1 TO len.of.browse%
		LOCATE lin% + 4, 2

		idx34% = lin% + startrrn% - 1
		rec34% = brrn%(idx34%)
		IF rec34% < 1 OR rec34% > 32000 THEN
			load$ = SPACE$(77)
			END IF

		IF rec34% >= 1 AND rec34% <= 32000 THEN
			GET #34, rec34%, fmhisth1

			tnta$ = RIGHT$("000" + LTRIM$(STR$(fmhisth1.form)), 3)
			tnta$ = tnta$ + fmhisth1.cost$
			load$ = "   " + STR$(idx34%): load$ = RIGHT$(load$, 3)
			load$ = load$ + " " + fmhisth1.desc$ + SPACE$(10)
			load$ = load$ + " " + tnta$ + "-" + STR$(fmhisth1.rev)
			load$ = load$ + "  " + format(fmhisth1.yld!, "####.#")
			load$ = load$ + "  " + "     "
			load$ = load$ + "   " '+ "dd/mm/yy"
			END IF

		PRINT load$
		NEXT
RETURN

x.browse34:
	browse34.result% = startrrn%

END SUB

SUB dsply (keyedform$, STDOUT$)
	CALL prtbtm(btm2$)

	FOR i% = 1 TO 999
		wrk% = VAL(MID$(tnthedx.tnta$(i%), 1, 3))
		IF VAL(keyedform$) = wrk% THEN
			SELECT CASE MID$(tnthedx.tnta$(i%), 4, 1)
			CASE "A"
				recHdr% = tnthedx.rrn%(i%)
				CALL dsplycurr(recHdr%)
			CASE "B"
			CASE "C"
			CASE "D"
			CASE "E"
			CASE "F"
			CASE ELSE
			END SELECT

			END IF
		NEXT

'>>- Search history file
	n% = 0
	FOR i% = 1 TO maxbrw%: brrn%(i%) = 0: NEXT

	rec34% = 1
	GET #34, rec34%, fmhisth1

	DO WHILE NOT EOF(34)
		ok% = -1
		IF fmhisth1.form% = 0 THEN ok% = 0
		IF fmhisth1.seq% <> 1 THEN ok% = 0
		IF fmhisth1.form% <> VAL(keyedform$) THEN ok% = 0

		'IF fmhisth1.seq% = 1 AND MID$(fmhisth1.hdate, 1, 2) <> "19" THEN
		'    GET #34, rec34%, fmhisth1
		'    fmhisth1.hdate = "19980718"
		'    PUT #34, rec34%, fmhisth1
		'END IF

		 IF ok% THEN
			n% = n% + 1
			brrn%(n%) = rec34%
			END IF
	IF rec34% MOD 100 = 0 THEN CALL sndmsg("Searching..." + STR$(rec34%))
	GET #34, , fmhisth1: rec34% = rec34% + 1
	LOOP
	CALL sndmsg("")
dsply10:
'>- Display the info
	CALL BOX(6, 2, 23, 79, 0, 0, 0)
	COLOR 2, 0
	startrrn% = 1
	FOR lin% = 1 TO 7
		idx34% = lin% + startrrn% - 1
		rec34% = brrn%(idx34%)
		IF rec34% < 1 OR rec34% > 32000 THEN
			load$ = SPACE$(77)
		END IF

		IF rec34% >= 1 AND rec34% <= 32000 THEN
			GET #34, rec34%, fmhisth1
			tnta$ = RIGHT$("000" + LTRIM$(STR$(fmhisth1.form)), 3)
			tnta$ = tnta$ + fmhisth1.cost$

			hhh$ = RIGHT$("000" + MID$(STR$(fmhisth1.form), 2), 3)
			load$ = ""
			load$ = load$ + " " + fmhisth1.desc$ + SPACE$(11)
			load$ = load$ + hhh$ + fmhisth1.cost$ + "-" + STR$(fmhisth1.rev)
			load$ = load$ + "  " + format(fmhisth1.yld!, "####.#")
			load$ = load$ + "  " + "      "
			IF MID$(fmhisth1.hdate$, 3, 1) = "/" THEN
				load$ = load$ + "  " + fmhisth1.hdate$
			ELSE
				load$ = load$ + "  " + FNDYY$(fmhisth1.hdate$)
			END IF
			'PRINT fmhisth1.form, fmhisth1.cost, fmhisth1.rev, fmhisth1.seq, fmhisth1.rel
			'PRINT fmhisth1.desc, fmhisth1.type, fmhisth1.class, fmhisth1.yld
			'PRINT fmhisth1.visl, fmhisth1.vish, fmhisth1.hdate

			GET #34, rec34% - 1 + 2, fmhisth2
			GET #34, rec34% - 1 + 3, fmhisth2
			GET #34, rec34% - 1 + 4, fmhisth2
			GET #34, rec34% - 1 + 5, fmhisth2
			GET #34, rec34% - 1 + 6, fmhisth2

			GET #34, rec34%, fmhisth1


			LOCATE 5 + lin%, 3
			PRINT USING "#####|&"; rec34%; load$

			END IF


		NEXT


dsply20:
	IF NOT skip% THEN
		a$ = STR$(brrn%(1))
		COLOR 2, 0
		LOCATE 23, 23: PRINT "Enter History Number..>";
		LOCATE 23, 46
		CALL inpnew(a$, 5!, updwn%, "13,59")
		IF updwn% = 59 THEN GOTO x.dsply
	END IF
	skip% = 0

	found% = 0
	FOR i% = 1 TO n%
		IF brrn%(i%) = VAL(a$) THEN found% = -1: EXIT FOR
	NEXT
	IF NOT found% THEN GOTO dsply20

	rec34% = brrn%(i%)
	IF rec34% < 1 OR rec34% > 32000 THEN GOTO dsply20
	hstrec% = rec34%

'>>- Disply the formula header
	GET #34, rec34%, fmhisth1

	tnta$ = RIGHT$("000" + LTRIM$(STR$(fmhisth1.form)), 3)
	tnta$ = tnta$ + fmhisth1.cost$

	LOCATE 6, 3: PRINT CHR$(FNE)
	LOCATE 7, 3: PRINT CHR$(FNE)
	LOCATE 8, 3: PRINT CHR$(FNE)
	LOCATE 9, 3: PRINT CHR$(FNE)

	CALL BOX(10, 2, 21, 79, 7, 0, 2)
	COLOR 2, 0
	LOCATE 10, 24: PRINT "µ Selected History Information Æ"
	LOCATE 11, 12: PRINT USING "Formula Number.> \   \ Rev##   Date:\      \"; tnta$; fmhisth1.rev; FNDYY$(fmhisth1.hdate$)
	LOCATE 12, 12: PRINT USING "Description....> \                             \"; fmhisth1.desc$
	LOCATE 13, 12: PRINT USING "Solvent/Water..> !##    Class \       \ \             \"; fmhisth1.type$; fmhisth1.class%; cldesc$; sw$
	LOCATE 14, 12: PRINT USING "Yield..........> ####.#                        "; fmhisth1.yld!

	SELECT CASE fmhisth1.visl
	CASE IS < 10: LOCATE 15, 12: PRINT USING "Visc Low/High.> #.# to #.# pse. - Rotothinner. "; fmhisth1.visl!; fmhisth1.vish!
	CASE ELSE: LOCATE 15, 12: PRINT USING "Visc Low/High.> ### to ### sec. - Ford Cup _# 4."; fmhisth1.visl!; fmhisth1.vish!
	END SELECT

	LOCATE 16, 12: PRINT "History Text.........."
	'>- The text records are seq 3,4,5 & 6
	FOR seq% = 3 TO 6
		GET #34, rec34% + seq% - 1, fmhisth3
		FOR i% = 1 TO 4
			IF MID$(fmhisth3.text$, i%, 1) < " " THEN MID$(fmhisth3.text$, i%, 1) = " "
			NEXT

		LOCATE 13 + seq%, 12: PRINT "...>"; fmhisth3.text$; "<"
		NEXT

LOCATE 25, 1: COLOR 0, 7: PRINT SPACE$(80);
LOCATE 25, 26: COLOR 0, 7: PRINT "F1-Cancel   F9-Display   F10-Print Formula";
CALL inpnew(a$, 0!, updwn%, "59,67-68")
CALL prtbtm(btm2$)
IF updwn% = 59 THEN GOTO dsply10
IF updwn% = 67 THEN
	CALL dsplyform(hstrec%, updwn%)
	IF updwn% = 60 THEN
		CALL dsplycurr(recHdr%)
		skip% = -1: a$ = STR$(rec34%)
		GOTO dsply10
		END IF
	GOTO dsply10
END IF

IF updwn% = 68 THEN
	CALL printform(hstrec%, STDOUT$, ok%)
	GOTO dsply10
END IF

x.dsply:
END SUB

SUB dsplycurr (recHdr%)
GET #ch.hdr%, recHdr%, tnthed
CALL BOX(3, 2, 5, 79, 7, 0, 2)
COLOR 2, 0
LOCATE 3, 24: PRINT "µ Current Formula Information Æ"
LOCATE 4, 4: PRINT "...| "; tnthed.desc$; "      "; tnthed.tnta$; "-"; tnthed.revision; " "; format(tnthed.yield!, "####.#"); "          "; FNDYY$(tnthed.date$)

END SUB

SUB dsplyform (hstrec%, updwn%)

	CALL setup("DISPLAY HISTORY")
	btm$ = "F1-Exit  F2=Return"
	maxlines% = 19
	CALL prtbtm(btm$)
	

	prev.seq% = 0
	GET #34, hstrec%, fmhistd1
	DO WHILE NOT EOF(34) AND fmhistd1.seq% > prev.seq%
		prev.seq% = fmhistd1.seq%

		IF fmhistd1.seq% = 1 THEN GET #34, hstrec%, fmhisth1
		IF fmhistd1.seq% = 2 THEN GET #34, hstrec%, fmhisth2
		IF fmhistd1.seq% = 3 THEN GET #34, hstrec%, fmhisth3
		IF fmhistd1.seq% = 4 THEN GET #34, hstrec%, fmhisth3
		IF fmhistd1.seq% = 5 THEN GET #34, hstrec%, fmhisth3
		IF fmhistd1.seq% = 6 THEN GET #34, hstrec%, fmhisth3

		SELECT CASE fmhistd1.seq%
		CASE 1:
			u$ = " poise": IF UCASE$(fmhisth1.type$) = "S" THEN u$ = " sec."

			wrk$ = wrk$ + "Form:" + MID$(STR$(fmhisth1.form%), 2) + fmhisth1.cost$ + " - " + MID$(STR$(fmhisth1.rev%), 2)
			wrk$ = wrk$ + "        " + fmhisth1.desc$
			wrk$ = wrk$ + "        YIELD:" + STR$(fmhisth1.yld!) + u$
			text$(fmhistd1.seq%) = wrk$

		CASE 2:
			text$(fmhistd1.seq%) = "---"
		CASE 3
			 text$(fmhistd1.seq%) = "         Comments....>³" + fmhisth3.text$
		CASE 4 TO 6:
			 text$(fmhistd1.seq%) = "                      ³" + fmhisth3.text$
		CASE ELSE
			cmtqty$ = STR$(fmhistd1.cmtqty%): IF fmhistd1.cmtqty% = 0 THEN cmtqty$ = ""
			qty$ = STR$(fmhistd1.qty!): IF fmhistd1.qty! = 0 THEN qty$ = " "
			qty$ = RIGHT$("     " + LTRIM$(qty$), 4)
			'prtbuf$ = "1234³6789 123456789 123456789 123456789 123456789 123456789 123456789 12345678"
			'prtbuf$ = "####³\                       \  ####\\   #### \                    \  $$###.##"

			MID$(text$(fmhistd1.seq%), 1, 2) = LTRIM$(STR$(fmhistd1.seq% - 6))
			MID$(text$(fmhistd1.seq%), 3, 2) = "  "
			MID$(text$(fmhistd1.seq%), 5, 1) = "|"
			MID$(text$(fmhistd1.seq%), 6, 25) = fmhistd1.desc$
			MID$(text$(fmhistd1.seq%), 33, 4) = qty$
			MID$(text$(fmhistd1.seq%), 38, 2) = fmhistd1.unit$
			MID$(text$(fmhistd1.seq%), 41, 1) = "|"
			MID$(text$(fmhistd1.seq%), 42, 4) = cmtqty$
			MID$(text$(fmhistd1.seq%), 47, 10) = fmhistd1.cmt$
		END SELECT

		GET #34, , fmhistd1: hstrec% = hstrec% + 1
		LOOP
	start% = 7: skip% = -1
	COLOR 2, 0
	'LOCATE 3, 2: PRINT text$(1)
	'LOCATE 4, 2: PRINT STRING$(78, "Ä")
	'LOCATE 5, 2: PRINT text$(3)
	'LOCATE 6, 2: PRINT text$(4)
	'LOCATE 7, 2: PRINT text$(5)
	'LOCATE 8, 2: PRINT text$(6)
	'LOCATE 9, 2: PRINT STRING$(78, "Ä")
	'COLOR 6, 0
	'LOCATE 10, 2: PRINT "    |Description                 Qty Ut | ...   Comment...."
	COLOR 6, 0
	LOCATE 3, 2: PRINT "    |Description                 Qty Ut | ...   Comment...."


dsplyform01:

	IF NOT skip% THEN
		LOCATE 4, 2
		a$ = STR$(start% - 6)
								CALL inpnew(a$, 2!, updwn%, "13,59-60,72-73,80-81")
		IF updwn% = 59 THEN GOTO x.dsplyform
		IF updwn% = 60 THEN GOTO x.dsplyform
		start% = VAL(a$) + 6
	END IF
	skip% = 0
	IF updwn% = 73 THEN start% = start% - maxlines%
	IF updwn% = 81 THEN start% = start% + maxlines%
	IF updwn% = 72 THEN start% = start% - 1
	IF updwn% = 80 THEN start% = start% + 1

	IF start% < 1 THEN start% = 1
	IF start% < 7 THEN start% = 7
	IF start% > 30 THEN start% = 30

	FOR lin% = 1 TO maxlines%
		i% = start% + lin% - 1
		COLOR 2, 0: LOCATE lin% + 3, 2: PRINT text$(i%)
	NEXT
	GOTO dsplyform01

x.dsplyform:

END SUB

SUB findform (form%, costflg$, rev%, hstrec%, ok%) STATIC
	ok% = 0
	hstrec% = 1
	GET #34, hstrec%, fmhisth1
	DO WHILE NOT EOF(34)
		IF fmhisth1.seq% = 1 THEN
		IF fmhisth1.form% = form% THEN
		IF fmhisth1.cost$ = costflg$ THEN
		IF fmhisth1.rev% = rev% THEN
			ok% = -1
			EXIT DO
			END IF
			END IF
			END IF
			END IF
		IF hstrec% MOD 100 = 0 THEN LOCATE 22, 25: PRINT USING "Searching..Rcd#,#### for ###!-#"; hstrec%; form%; costflg$; rev%: x$ = INKEY$
		IF x$ = CHR$(0) + CHR$(59) THEN updwn% = 59: EXIT DO
		GET #34, , fmhisth1: hstrec% = hstrec% + 1
		LOOP


END SUB

SUB FixHydroxinol

	CALL setup("DISPLAY HISTORY")


	hstrec% = 1
	GET #34, hstrec%, fmhistd1
	DO WHILE NOT EOF(34)

		IF fmhistd1.seq% = 1 THEN GET #34, hstrec%, fmhisth1
		IF fmhistd1.seq% = 2 THEN GET #34, hstrec%, fmhisth2
		IF fmhistd1.seq% = 3 THEN GET #34, hstrec%, fmhisth3
		IF fmhistd1.seq% = 4 THEN GET #34, hstrec%, fmhisth3
		IF fmhistd1.seq% = 5 THEN GET #34, hstrec%, fmhisth3
		IF fmhistd1.seq% = 6 THEN GET #34, hstrec%, fmhisth3

		SELECT CASE fmhistd1.seq%
		CASE 1:
		CASE 2:
		CASE 3
		CASE 4 TO 6:
		CASE ELSE
			cmtqty$ = STR$(fmhistd1.cmtqty%): IF fmhistd1.cmtqty% = 0 THEN cmtqty$ = ""
			qty$ = STR$(fmhistd1.qty!): IF fmhistd1.qty! = 0 THEN qty$ = " "
			qty$ = RIGHT$("     " + LTRIM$(qty$), 4)
			IF RTRIM$(fmhistd1.desc$) = "" AND RTRIM$(fmhistd1.cmt$) > "" THEN
				ok% = 0
				IF RTRIM$(fmhistd1.cmt$) = "FROM TOP" THEN
					fmhistd1.desc$ = "HYDROXINOL"
					PUT #34, hstrec%, fmhistd1
					ok% = -1
				END IF
				IF RTRIM$(fmhistd1.cmt$) = "ON SIDE" THEN
					fmhistd1.desc$ = "HYDROXINOL"
					PUT #34, hstrec%, fmhistd1
					ok% = -1
				END IF

				IF RTRIM$(fmhistd1.cmt$) = "PREMIX" THEN ok% = -1

				IF NOT ok% THEN
					'PRINT fmhistd1.form
				'    STOP'??
				END IF
			END IF
		END SELECT

		GET #34, , fmhistd1: hstrec% = hstrec% + 1
		LOOP

END SUB

FUNCTION format$ (VALUE!, definition$) STATIC
	dp% = 0

	'>- Find out how many decimal places,neg etc... -<
	work$ = STR$(VALUE!)
	edtcde$ = " ": dp% = 0
	x% = INSTR(definition$, ".")
	IF x% > 0 THEN
		FOR i% = x% TO LEN(definition$)
			IF MID$(definition$, i%, 1) = "b" THEN MID$(definition$, i%, 1) = "#": edtcde$ = "b"
			IF MID$(definition$, i%, 1) = "#" THEN dp% = dp% + 1
			NEXT
		x% = INSTR(work$, ".")
		IF x% = 0 THEN work$ = work$ + "."
		work$ = work$ + STRING$(dp%, "0")
		x% = INSTR(work$, ".")
		work$ = MID$(work$, 1, x% + dp%)
		END IF


	'>- Move from work pad into definition, from right to left -<
	neg% = MID$(work$, 1, 1) = "-"
	dollars% = 0
	work$ = MID$(work$, 2)
	defwork$ = definition$
	FOR i% = 1 TO LEN(definition$)
		IF MID$(definition$, i%, 1) = "$" THEN dollars% = -1: EXIT FOR
		NEXT

	'>- NOTE: The "d" represents the $ that i have added! -<
	IF dollars% THEN work$ = "d" + work$
	IF neg% THEN work$ = "-" + work$

	num.dollars% = 0
	w% = LEN(work$)

	FOR i% = LEN(defwork$) TO 1 STEP -1
		IF w% < 1 THEN EXIT FOR
		SELECT CASE MID$(defwork$, i%, 1)
		CASE "#": MID$(defwork$, i%, 1) = MID$(work$, w%, 1): w% = w% - 1
		CASE "$": MID$(defwork$, i%, 1) = MID$(work$, w%, 1): w% = w% - 1
		CASE ",": IF MID$(work$, w%, 1) = "d" THEN MID$(defwork$, i%, 1) = "#": i% = i% + 1
		CASE ".": w% = w% - 1
		CASE ELSE
		END SELECT

		NEXT

	FOR i% = 1 TO LEN(defwork$)
		IF MID$(defwork$, i%, 1) >= "1" AND MID$(defwork$, i%, 1) <= "9" THEN EXIT FOR
		IF MID$(defwork$, i%, 1) = "#" THEN MID$(defwork$, i%, 1) = " "
		IF MID$(defwork$, i%, 1) = "$" THEN MID$(defwork$, i%, 1) = " "
		IF MID$(defwork$, i%, 1) = "d" THEN MID$(defwork$, i%, 1) = "$"
		IF MID$(defwork$, i%, 1) = "," THEN MID$(defwork$, i%, 1) = " "
		NEXT

	'>- Zero suppress
	IF edtcde$ = "b" AND VALUE! = 0 THEN defwork$ = STRING$(LEN(defwork$), " ")

	format$ = defwork$
END FUNCTION

SUB openup (swapfile%)
	IF swapfile% THEN
		IF mode$ = "Tints" THEN mode$ = "A - F" ELSE mode$ = "Tints"
		END IF

	IF open34% THEN CLOSE #34: open34% = 0

	SELECT CASE mode$
	CASE "Tints": OPEN "tnhist.hst" FOR RANDOM SHARED AS #34 LEN = 62
					GET #53, 1, tnthedx
					ch.hdr% = 54
	CASE "A - F": OPEN "fmhist.hst" FOR RANDOM SHARED AS #34 LEN = 62
					GET #63, 1, tnthedx
					ch.hdr% = 64
	CASE ELSE
	END SELECT

	open34% = -1

END SUB

SUB printform (hstrec%, STDOUT$, ok%)

	LOCATE 18, 10: PRINT "Printing formula "; fmhisth1.desc$; " Revision "; fmhisth1.rev%

	OPEN STDOUT$ FOR OUTPUT AS #99

	seen.first.det% = 0
	prev.seq% = 0
	GET #34, hstrec%, fmhistd1
	DO WHILE NOT EOF(34) AND fmhistd1.seq% > prev.seq%
		prev.seq% = fmhistd1.seq%

		IF fmhistd1.seq% = 1 THEN GET #34, hstrec%, fmhisth1
		IF fmhistd1.seq% = 2 THEN GET #34, hstrec%, fmhisth2
		IF fmhistd1.seq% = 3 THEN GET #34, hstrec%, fmhisth3
		IF fmhistd1.seq% = 4 THEN GET #34, hstrec%, fmhisth3
		IF fmhistd1.seq% = 5 THEN GET #34, hstrec%, fmhisth3
		IF fmhistd1.seq% = 6 THEN GET #34, hstrec%, fmhisth3

		SELECT CASE fmhistd1.seq%
		CASE 1:
			'**Heading print
			PRINT #99, "mshst01"; TAB(67); "DATE:"; MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
			PRINT #99, TAB(22); msmisc.cc$
			PRINT #99, TAB(15); "H I S T O R Y    F O R M U L A T I O N    P R I N T "
			PRINT #99, " "
			PRINT #99, TAB(28); fmhisth1.desc$
			PRINT #99, STRING$(79, "_")
			PRINT #99, "Formula "; fmhisth1.form%; fmhisth1.cost$; ".  Revision "; fmhisth1.rev%; " Dated:"; fmhisth1.hdate$; TAB(67); "Yield:"; fmhisth1.yld!
			PRINT #99, STRING$(79, "_")
			u$ = " poise": IF UCASE$(fmhisth1.type$) = "S" THEN u$ = " sec."
			visl! = fmhisth1.visl
			vish! = fmhisth1.vish

		CASE 2:
			'PRINT #99, USING "&"; " "
		CASE 3
			 PRINT #99, "     Comments....>" + fmhisth3.text$
		CASE 4 TO 6:
			 PRINT #99, "                  " + fmhisth3.text$
		CASE ELSE
			IF NOT seen.first.det% THEN
				PRINT #99, " "
				PRINT #99, " "
				PRINT #99, " "
				PRINT #99, STRING$(79, "_")
				PRINT #99, "     Product.                     Lt/Kg             Comment"
				PRINT #99, STRING$(79, "_")
				seen.first.det% = -1
				END IF

			cmtqty$ = STR$(fmhistd1.cmtqty%): IF fmhistd1.cmtqty% = 0 THEN cmtqty$ = ""
			SELECT CASE fmhistd1.unit$
			CASE "EQ"
				PRINT #99, USING "    | \                       \          \\   &     &"; fmhistd1.desc$; fmhistd1.unit$; cmtqty$; fmhistd1.cmt$
			CASE "KG"
				PRINT #99, USING "    | \                       \ |####.## \\ | &     &"; fmhistd1.desc$; fmhistd1.qty!; fmhistd1.unit$; cmtqty$; fmhistd1.cmt$
			CASE "LT"
				PRINT #99, USING "    | \                       \ |####.## \\ | &     &"; fmhistd1.desc$; fmhistd1.qty!; fmhistd1.unit$; cmtqty$; fmhistd1.cmt$
			CASE ELSE
				IF MID$(fmhistd1.desc$, 1, 1) <= " " THEN
				PRINT #99, " "
				ELSE
				PRINT #99, USING "    | \                       \ |####.## \\ | &     &"; fmhistd1.desc$; fmhistd1.qty!; fmhistd1.unit$; cmtqty$; fmhistd1.cmt$
				END IF
			END SELECT


		END SELECT

		GET #34, , fmhistd1: hstrec% = hstrec% + 1
		LOOP

		PRINT #99,
		PRINT #99, TAB(20); "Viscosity "; visl!; " to "; vish!; u$
		IF STDOUT$ = "CON" THEN x$ = INPUT$(1)
		PRINT #99, CHR$(12)
		CLOSE #99

	shella$ = "COPY " + STDOUT$ + " LPT1"
	SHELL shella$

	shellb$ = "type " + STDOUT$ + " | more"
	'SHELL shellb$
END SUB

SUB printheaders (hstrec%, STDOUT$, ok%)

	lin% = 999
	hstrec% = 1
	n% = 0
	GET #34, hstrec%, fmhisth1
	DO WHILE NOT EOF(34)
		IF fmhisth1.seq% = 1 THEN
			n% = n% + 1
			a$ = "000" + MID$(STR$(fmhisth1.form%), 2)
			b$ = "00" + MID$(STR$(fmhisth1.rev%), 2)
			in$(n%) = RIGHT$(a$, 3) + fmhisth1.cost$ + RIGHT$(a$, 2)
			in%(n%) = hstrec%
			END IF
		IF hstrec% MOD 100 = 0 THEN
			CALL sndmsg("Loading records into sort. Record" + STR$(hstrec%))
			END IF
		GET #34, , fmhisth1: hstrec% = hstrec% + 1
		LOOP

	CALL sndmsg("Sorting...")
	CALL qsort(in$(), in%(), n%)
	CALL sndmsg("Printing...")

	OPEN STDOUT$ FOR OUTPUT AS #99
	WIDTH #99, 80

	ok% = 0
	lin% = 999
	FOR i% = 1 TO n%
		hstrec% = in%(i%)
		GET #34, hstrec%, fmhisth1
		IF fmhisth1.seq% = 1 THEN
			u$ = "pse.": IF fmhisth1.visl! >= 10 THEN u$ = "sec."

			visl! = fmhisth1.visl
			vish! = fmhisth1.vish
			type$ = "Water based": IF fmhisth1.type$ = "S" THEN type$ = "SOLVENT BASED"
			IF lin% > 50 THEN GOSUB heading
			SELECT CASE u$
			CASE "pse."
			PRINT #99, USING "###&-## & &,##  #####  #.# to #.# &"; fmhisth1.form%; fmhisth1.cost$; fmhisth1.rev%; fmhisth1.desc$; type$; fmhisth1.class%; fmhisth1.yld!; fmhisth1.visl!; fmhisth1.vish!; u$
			CASE "sec."
			PRINT #99, USING "###&-## & &,##  #####  ### to ### &"; fmhisth1.form%; fmhisth1.cost$; fmhisth1.rev%; fmhisth1.desc$; type$; fmhisth1.class%; fmhisth1.yld!; fmhisth1.visl!; fmhisth1.vish!; u$
			CASE ELSE
			END SELECT

			lin% = lin% + 1
			END IF
		NEXT

		CLOSE #99
		CALL sndmsg("")
EXIT SUB

heading:
	 IF pag% > 0 THEN PRINT #99, CHR$(12)
	 lin% = 0: pag% = pag% + 1
	 PRINT #99, CHR$(14); msmisc.cc$
	 PRINT #99, TAB(20); "H I S T O R Y    F I L E    I N D E X ";
	 PRINT #99, TAB(67); "DATE:"; MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
	 PRINT #99, STRING$(79, "=")
	 PRINT #99, "Formula Description               Base            Yield  Vis/L    Vis/H"
	 PRINT #99, STRING$(79, "-")

	'PRINT #99, CHR$(14); msmisc.cc$
	'PRINT #99, " #msHST01"; TAB(71); DATE1$
	'PRINT #99, TAB(15); CHR$(14); fmhisth1.desc$
	'PRINT #99, "ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿"
	'PRINT #99, USING "³Formula \  \!  Rev. ##  ³ Class \      \    ³                 Yield:##### Lt.³"; d$; fcost$; frev%; cldesc$; fyld
	'IF bno1 <> 0 THEN
	'PRINT #99, "ÃÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅÄÄÄÄÄÄÄÂÄÄÄÂÄÄÄÄÄÄÄÅÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ´"
	'PRINT #99, "³ COMPONENT              ³ LITRE ³HAZ³ KILO  ³CHECK³ INSTRUCTIONS             ³"
	'PRINT #99, "ÀÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÙ"
	'ELSE
	'PRINT #99, "ÃÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÂÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄ´"
	'PRINT #99, "³No. ³ COMPONENT                ³ Lt/Kg.³Ut³ INSTRUCTIONS              ³ Cost.³"
	'PRINT #99, "ÀÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÙ"
	'END IF

RETURN
END SUB

SUB qsort (in$(), in%(), n%) STATIC
'$INCLUDE: '\tpmanuf\src\qsort.bi'
END SUB

