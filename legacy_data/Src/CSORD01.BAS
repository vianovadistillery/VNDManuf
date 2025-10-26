DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB ql2fax (genfax%, sndfax%, viewfax%)
DECLARE SUB add.up.order (ok%)
DECLARE SUB quick.load (updwn%, lin%, Cont%)
DECLARE SUB browse38 (browse38.result%, updwn%)
DECLARE SUB det.entry (updwn%, lin%, in$)
DECLARE SUB browse.idx (firstonscreen%, ch1%, ch2%)
DECLARE SUB dsply (rec%, updwn%)
DECLARE SUB details (rec%, updwn%)
DECLARE SUB dsply.lines (dstart%, dend%)
'.dc - Complete
'////////////////////////////////////////////////////////////////////////////
'>>>>>   SUPPLIER ORDERS
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'NO TAX,confirmation on order??, FAX/ORDER/c


	'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "CSMENU"
	DB.OR.CR$ = "CR"
	''INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CLOSE
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	'$INCLUDE: '\tpmanuf\src\msrmat.inc'
	'$INCLUDE: '\tpmanuf\src\acstk.inc'
	'$INCLUDE: '\tpmanuf\src\csorder.inc'

	DIM SHARED maxsup%, maxrmat%, maxacc%
	DIM SHARED in$(18, 7), tot.ext!
	DIM SHARED fax(1 TO 50) AS STRING * 80

	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxacc% = CVI(msmisc.max5$)

	COLOR 2, 0
	acls% = -1
	 in$ = "21"'??
START:
	IF acls% THEN
		heading$ = "ENTER CREDITOR DETAILS"
		btm$ = "F1-Exit          F5-View Fax.     F6-Browse      F9-Details               ."
		CALL setup(heading$)
		acls% = 0
	END IF
	CALL sndmsg(msg$): msg$ = ""
	COLOR 0, 3: LOCATE 25, 4: PRINT btm$; : COLOR 2, 0
	updwn% = 0
	IF NOT pass% THEN
		COLOR 2, 0: in$ = ""
		LOCATE 3, 20: PRINT "Enter supplier code....> "
		LOCATE 3, 44
		CALL inpnew(in$, 105!, updwn%, "13,59,63-64,67" + ALT$): GOSUB ALT
				in$ = UCASE$(in$)
		END IF
	pass% = 0

	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	IF updwn% = 63 THEN
		CALL ql2fax(0, 0, -1)
		pass% = -1: acls% = -1
		GOTO START
		END IF
	IF updwn% = 64 THEN
		CALL browse.idx(first.on.screen%, 45, 44)
		in$ = STR$(first.on.screen%)
		rec% = VAL(in$)
		pass% = -1: acls% = -1
		GOTO START
		END IF
	IF updwn% = 67 THEN
		CALL details(rec%, updwn%)
		pass% = -1: acls% = -1
		END IF
	IF updwn% = 13 THEN
		p = VAL(in$)
		IF p = 0 THEN
			skey$ = in$: CALL searchindex(skey$, 45, ok%)
			p = CVI(supx.wrrn$)
			END IF
		rec% = p
		END IF

	CALL dsply(rec%, updnw%)
	GOTO START

SUB add.up.order (ok%)

	tot.ext! = 0
	FOR lin% = 1 TO 18
		Qty% = VAL(in$(lin%, 1))
		Price! = VAL(in$(lin%, 6))
		Tax! = VAL(in$(lin%, 7))
		ext! = Qty% * (Price! + Tax!)
		tot.ext! = tot.ext! + ext!
		NEXT

END SUB

SUB browse.idx (firstonscreen%, ch1%, ch2%) STATIC
'$INCLUDE: '\tpmanuf\src\browse01.bi'
END SUB

SUB browse38 (browse38.result%, updwn%) STATIC
	maxrmat% = 9999
	 CALL setup("BROWSE FILE")
	 COLOR 6, 0
	 LOCATE 4, 2: PRINT "SEQ. DESCRIPTION.............. SUPL. GRP A S/G.. SUPPLY COST NOTES............";
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit       F6- Search again"; : LOCATE 25, 71: PRINT CHR$(24); CHR$(25); "-Move"; : COLOR 2, 0
	 COLOR 2, 0
	 len.of.browse% = 19
	'***** Correct position - SOH
	 IF p < 1 OR p > maxrmat% THEN p = 1
	 LOCATE 5, 2: s% = p - 1: X = p: f% = p: GOTO browse38.2540'* First time in list from saved number
2510
	IF f% < 1 OR f% > maxrmat% THEN f% = 1
	LOCATE 3, 2: PRINT "Current number.:"; f%;
	k% = 1
	LOCATE 3, 23: PRINT "Browse from number..> "; CHR$(FNH);
	z$ = ""
	CALL inpnew(z$, 204!, updwn%, "13,59-60,64,72,73,80,81")
browse38.2540:
		'>-- Search ----<
		startss% = 1: IF updwn% = 64 THEN startss% = last.found% + 1: z$ = last.search$
		z$ = UCASE$(z$)
		lenz% = LEN(z$)
		IF MID$(z$, 1, 1) >= "A" AND MID$(z$, 1, 1) <= "Z" THEN
		FOR j% = startss% TO 9999
			GET #38, j%, msrmat
			IF msrmat.no% = j% AND MID$(msrmat.search$, 1, lenz%) = z$ THEN
							last.found% = j%: last.search$ = z$
							z$ = STR$(j%)
							EXIT FOR
							updwn% = 13
							END IF
		NEXT
		END IF

	IF updwn% = 59 THEN skip$ = "Y": p = f%: p$ = MID$(STR$(p), 2): GOTO x.browse38
	LOCATE 3, 44
	IF updwn% = 72 THEN GOSUB 2840: GOTO 2530  '***** UP arrow
	IF updwn% = 73 THEN GOSUB 2820: GOTO 2530  '***** PGUP
	IF updwn% = 80 THEN X = f% + 1: GOTO 2530   '***** DN arrow
	IF updwn% = 81 THEN z$ = ""                '***** PGDN
	IF updwn% = 13 THEN
		IF LEN(z$) = 0 THEN X = X + 1: z$ = STR$(X)
		END IF
	IF LEN(z$) = 0 THEN X = s% + 1: GOTO 2530
	zz$ = "    ": LSET zz$ = z$: X = VAL(zz$)
2530 j% = -1: i% = 0
	 '
2630 j% = j% + 1
	 IF X + j% < 1 OR j% + X > maxrmat% THEN PRINT CHR$(FNE); : GOTO 2770
	 IF k% = 1 THEN
		GET #38, j% + X, msrmat: k% = 0
		ELSE
		GET #38, , msrmat
		END IF
	 IF msrmat.no% = 0 THEN 2630
	 LOCATE i% + 5, 2
	 PRINT USING "#### \                       \ \   \ ### \\#.### #####.###\ \\               \"; j% + X; msrmat.desc1$; msrmat.search$; msrmat.Group%; msrmat.active$; msrmat.Sg; msrmat.purcost; msrmat.PurUnit$; msrmat.notes$
2770 i% = i% + 1: s% = j% + X: IF i% = 1 THEN f% = j% + X
	 IF i% < len.of.browse% THEN 2630
	 'END IF
	 GOTO 2510
'//////////////////////////////////////////////////////////////////////
'>>>>> F I N D  F I R S T   R E C O R D   O F   R O L L B A C K
'//////////////////////////////////////////////////////////////////////
2820
	 X = f%: i% = 0
2840 X = X - 1
	 IF X < 1 THEN X = 1: GOTO 2890'BOF
	 GET #38, X, msrmat
	 IF msrmat.no = 0 THEN 2840
	 IF updwn% <> 72 OR updwn% <> 80 THEN
	i% = i% + 1: IF i% < len.of.browse% THEN 2840
	 END IF
2890
x.browse38:
	browse38.result% = p

END SUB

SUB det.entry (updwn%, lin%, in$)
	c1% = 2: c2% = 6: c3% = 13: c4% = 18: c5% = 46: c6% = 62
cf1:
	in$(lin%, 1) = in$
	IF updwn% = -1 THEN GOTO cf7

cf2:
	LOCATE lin% + 4, c2%
	in$ = in$(lin%, 2)
	CALL inpnew(in$, 105!, updwn%, "13,59,72,80")
	in$(lin%, 2) = in$
	IF updwn% = 59 THEN GOTO cf7
	IF updwn% = 60 THEN GOTO cf1
cf3:
	LOCATE lin% + 4, c3%
	in$ = in$(lin%, 3)
	CALL inpnew(in$, 4!, updwn%, "13,59,64,72,80")
	IF updwn% = 64 THEN
		CALL browse38(browse38.result%, updwn%)
		in$ = STR$(browse38.result%): updwn% = 13
		END IF
	IF updwn% = 13 THEN
		SELECT CASE sup.stype$
		CASE "R"
			rec38% = VAL(in$)
			IF rec38% < 1 THEN rec38% = 1
			IF rec38% > maxrmat% THEN rec38% = 1
			GET #38, rec38%, msrmat
			in$(lin%, 4) = msrmat.desc1$
			in$(lin%, 5) = msrmat.notes$
			in$(lin%, 6) = STR$(msrmat.purcost!)
			in$ = STR$(msrmat.no%)
		CASE "A"
			rec3% = VAL(in$)
			IF rec3% < 1 THEN rec3% = 1
			IF rec3% > maxacc% THEN rec3% = 1
			GET #3, rec3%, acstk
			IF in$(lin%, 2) <= " " THEN in$(lin%, 2) = acstk.size$ + acstk.unit$
			in$(lin%, 4) = acstk.desc1$
			in$(lin%, 5) = acstk.desc2$
			in$(lin%, 6) = STR$(acstk.purcost!)
			in$ = STR$(acstk.no%)

		CASE ELSE
		END SELECT
		END IF

	in$(lin%, 3) = in$
	IF updwn% = 59 THEN GOTO cf7
	IF updwn% = 60 THEN GOTO cf2

cf4:
	LOCATE lin% + 4, c4%
	in$ = in$(lin%, 4)
	CALL inpnew(in$, 125!, updwn%, "13,59,72,80")
	in$(lin%, 4) = in$
	IF updwn% = 59 THEN GOTO cf7
	IF updwn% = 60 THEN GOTO cf3
cf5:
	LOCATE lin% + 4, c5%
	in$ = in$(lin%, 5)
        CALL inpnew(in$, 112!, updwn%, "13,59,72,80")
	in$(lin%, 5) = in$
	IF updwn% = 59 THEN GOTO cf7
	IF updwn% = 60 THEN GOTO cf4
cf6:
	LOCATE lin% + 4, c6%
	in$ = in$(lin%, 6)
        CALL inpnew(in$, 6.2!, updwn%, "13,59,72,80")
	in$(lin%, 6) = in$
	IF updwn% = 59 THEN GOTO cf7
	IF updwn% = 60 THEN GOTO cf5

cf7:
	oldext! = VAL(in$(lin%, 7))

	Qty% = VAL(in$(lin%, 1))
	Price! = VAL(in$(lin%, 6))
	ext! = Qty% * (Price! + Tax!)
	in$(lin%, 7) = STR$(ext!)

	tot.ext! = tot.ext! - oldext!
	tot.ext! = tot.ext! + ext!
	COLOR 7, 0
	LOCATE 24, 67: PRINT USING "µ$$##,###.##Æ"; tot.ext!
	COLOR 2, 0

	in$ = in$(lin%, 1)
END SUB

SUB details (rec%, updwn%)
	btm$ = "F1-Return.     F6-Browse      F9-Quick load                                 ."
	COLOR 0, 3: LOCATE 25, 4: PRINT btm$; : COLOR 2, 0
	IF rec% < 1 OR rec% > maxsup% THEN GOTO x.detail
	

	dstart% = 1: dend% = 18

	CALL BOX(2, 3, 79, 22, 2, 0, 0)
	CALL dsply.lines(1, 18)
	CALL add.up.order(ok%)

	lin% = 1


detaila:
	IF lin% < 1 THEN lin% = 1
	IF lin% > 18 THEN lin% = 18
	LOCATE lin% + 4, 2
	in$ = in$(lin%, 1)
	was$ = in$
	CALL inpnew(in$, 3!, updwn%, "13,59,61-62,65,67,72,80")
	SELECT CASE updwn%
	CASE 59: GOTO exitmenu
	CASE 13:
			IF was$ <> in$ THEN
			CALL det.entry(updwn%, lin%, in$)
			END IF
			lin% = lin% + 1
	CASE 61: 'Insert a line
			IF VAL(in$(18, 1)) = 0 THEN
			FOR l% = 18 TO lin% + 1 STEP -1
				FOR c% = 1 TO 7
				in$(l%, c%) = in$(l% - 1, c%)
				NEXT
				NEXT
			FOR c% = 1 TO 7: in$(lin%, c%) = "": NEXT
			CALL add.up.order(ok%)
			END IF

	CASE 62: 'Delete a line
			FOR l% = lin% TO 18 - 1
				FOR c% = 1 TO 7
				in$(l%, c%) = in$(l% + 1, c%)
				NEXT
				NEXT
			FOR c% = 1 TO 7: in$(18, c%) = "": NEXT
			CALL add.up.order(ok%)
			updwn% = -1: in$ = in$(lin%, 1)
			CALL det.entry(updwn%, lin%, in$)

	CASE 64: CALL browse38(browse38.result%, updwn%)
	CASE 67: CALL quick.load(updwn%, lin%, Cont%)

	CASE 72: updwn% = -1: CALL det.entry(updwn%, lin%, in$)
			 lin% = lin% - 1
	CASE 80: updwn% = -1: CALL det.entry(updwn%, lin%, in$)
			 lin% = lin% + 1
	CASE ELSE
	END SELECT

	CALL dsply.lines(dstart%, dend%)
	GOTO detaila


exitmenu:
	opt% = 0
	DO
	CALL BOX(17, 5, 63, 19, 6, 9, 1)
	COLOR 4, 1
	LOCATE 6, 28: PRINT "  E X I T    M E N U "
	COLOR 7, 1
	LOCATE , 28: PRINT "1....Exit without update."
	LOCATE , 28: PRINT "2....Continue to enter details"
	LOCATE , 28: PRINT "3....Send fax order."
	COLOR 2
	LOCATE , 28: PRINT "Option...> "
	COLOR 6, 1
	LOCATE 18, 20: PRINT "F1-Save & Exit."
	LOCATE 17, 38: COLOR 2, 0
	CALL inpnew(opt$, 1!, updwn%, "13,59-60,62,68")
	opt% = VAL(opt$)
	IF updwn% = 13 AND opt% = 0 THEN updwn% = 59
	IF updwn% = 59 THEN opt% = 1
	IF updwn% = 60 THEN opt% = 2'F2 - Save & Cont
	LOOP UNTIL opt% <> 0

	IF opt% = 2 THEN
		CALL dsply.lines(1, 18)
		GOTO detaila
		END IF
	IF opt% = 3 THEN
		CALL ql2fax(-1, -1, -1)
		END IF

x.detail:
END SUB

SUB dsply (rec%, updwn%)
	IF rec% < 1 OR rec% > maxsup% THEN msg$ = "Not found on file.": GOTO x.dsply

	GET #44, rec%, sup
	sno% = CVI(sup.sno$)
	scur = CVS(sup.scur$): s30 = CVS(sup.s30$): s60 = CVS(sup.s60$): s90 = CVS(sup.s90$)
	sdays% = CVI(sup.sdays$): climit = CVS(sup.climit$)
	sterms = CVS(sup.sterms$): daysmax% = CVI(sup.daysmax$)
	IF sno% = 0 THEN sno% = rec%
	X0 = 5: COLOR 2, 0
	LOCATE 4, X0: PRINT "File number.......:"; sno%; "  "; sup.search$
	LOCATE 4, X0 + 45: PRINT "Type.>"; sup.stype$
	LOCATE 5, X0: PRINT "         Name......:"; sup.sname$
	LOCATE , X0: PRINT "         Address...:"; sup.saddr$
	LOCATE , X0: PRINT "Suburb / Post code.:"; sup.suburb$; " "; sup.spcode$
	LOCATE , X0: PRINT "Contact............:"; sup.scont$
	LOCATE , X0: PRINT "Telephone .........:";
	LOCATE , X0 + 36: PRINT "(Bus.)........:";
	LOCATE , X0: PRINT "Trading terms......:"; daysmax%; " Days.";
	LOCATE , X0 + 35: PRINT sdays%; " Days for "; sterms; "% discount.";
	IF climit < 1 THEN a$ = "Trading terms"
	IF climit = 0 THEN a$ = "C.O.D        "
	IF climit > 0 THEN a$ = STR$(climit)
	COLOR 6
	LOCATE , X0: PRINT "Total        90+ Days     60 Days     30 Days      Current    C/Limit"
	COLOR 2
	LOCATE , 2: PRINT USING "###,###.##   ###,###.##   ###,###.##   ###,###.## #,###,###.##   \           \"; total; s90; s60; s30; scur; a$
x.dsply:
END SUB

SUB dsply.lines (dstart%, dend%) STATIC
	IF dstart% < 1 THEN dstart% = 1
	IF dend% > 18 THEN dend% = 18

	LOCATE 3, 2: COLOR 6, 0: PRINT "Qty. Size   No.  Description                                 Price   Value    "
	LOCATE 4, 2: COLOR 2, 0: PRINT "ÄÄÄÂÄÄÄÄÄÄÂÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄ"

	FOR lin% = dstart% TO dend%
			ln% = lin% + 4
			a% = VAL(in$(lin%, 1))
			b$ = in$(lin%, 2)
			c% = VAL(in$(lin%, 3))
			d$ = in$(lin%, 4)
			e$ = in$(lin%, 5)
			f! = VAL(in$(lin%, 6))
			g! = VAL(in$(lin%, 7))
			IF a% > 0 THEN
			LOCATE ln%, 2:  PRINT USING "###³\    \³####³\                         \ \             \³####.##³ #####.##"; a%; b$; c%; d$; e$; f!; g!
			ELSE
			LOCATE ln%, 2:  PRINT USING "   ³      ³    ³                                           ³       ³         !"; " "
			IF VAL(in$(lin%, 7)) <> 0 THEN LOCATE ln%, 70: PRINT VAL(in$(lin%, 7)): BEEP
			END IF
			NEXT

	COLOR 2, 0
END SUB

SUB ql2fax (genfax%, sndfax%, viewfax%)

	chka$ = DIR$("\UTIL\QL2FAX\CONVERT.EXE")
	chkb$ = DIR$("\UTILS\QL2FAX\CONVERT.EXE")
	IF chka$ > "" THEN faxpath$ = "\UTIL\QL2FAX\"
	IF chkb$ > "" THEN faxpath$ = "\UTILS\QL2FAX\"
	faxfile$ = faxpath$ + "OUTBOUND\FAX.TXT"

	IF genfax% THEN
	'>> Get last order number from history log
	csorderlast% = LOF(69) / 87
	IF csorderlast% > 0 THEN
		GET #69, csorderlast%, csorder
		lastorder% = VAL(csorder.no$)
		ELSE
		lastorder% = 0
		END IF

	order% = lastorder% + 1

	OPEN faxfile$ FOR OUTPUT AS #93
	PRINT #93, ".FILE=" + faxpath$ + "OUTBOUND\JPLOGO.QFX"
	PRINT #93, "Order: " + STR$(order%)
	PRINT #93, ""
	PRINT #93, sup.sname$
	PRINT #93, sup.saddr$
	PRINT #93, sup.suburb$; " "; sup.spcode$
	PRINT #93, ""
	PRINT #93, "Qty. Size   No.  Description                           Price     Tax    Value"
	PRINT #93, "ÄÄÄÂÄÄÄÄÄÄÂÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄ"
	FOR lin% = 1 TO 18
			ln% = lin% + 4
			a% = VAL(in$(lin%, 1))
			b$ = in$(lin%, 2)
			c% = VAL(in$(lin%, 3))
			d$ = in$(lin%, 4)
			e$ = in$(lin%, 5)
			f! = VAL(in$(lin%, 6))
			g! = VAL(in$(lin%, 7))
			IF a% > 0 THEN
				PRINT #93, USING "###³\    \³####³\                                   \³####.##³ ###.##³#####.##"; a%; b$; c%; d$; e!; f!; g!
			ELSE
				PRINT #93, USING "   ³      ³    ³                                     ³       ³       ³       !"; " "
			END IF
			NEXT
	PRINT #93, "ÄÄÄÁÄÄÄÄÄÄÁÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄ"


	PRINT #93, USING "                                                                   $$##,###.##"; tot.ext!
	PRINT #93, ""
	PRINT #93, ".FILE=" + faxpath$ + "OUTBOUND\JPSIG.QFX"
	CLOSE #93
	END IF

	IF sndfax% THEN

		OPEN "SNDFAX.DAT" FOR RANDOM AS #2
		FIELD #2, 10 AS fax.file$, 20 AS fax.phone$, 10 AS fax.retpgm$
		LSET fax.file$ = "FAX.QFX"
		LSET fax.phone$ = "42000000"
		LSET fax.retpgm$ = "CSORD01"
		PUT #2, 1
		CLOSE #2

		'>>- Copy fax to history log -<<
		OPEN faxfile$ FOR INPUT AS #93
		INPUT #93, a$
		DO WHILE NOT EOF(93)
			wrk5$ = "00000" + MID$(STR$(order%), 2)
			csorder.no$ = RIGHT$(wrk5$, 5)
			csorder.bar$ = "|"
			csorder.text$ = a$
			csorder.cr$ = CHR$(13)
			PUT #69, , csorder

			INPUT #93, a$
			LOOP

			wrk5$ = "00000" + MID$(STR$(order%), 2)
			csorder.no$ = RIGHT$(wrk5$, 5)
			csorder.bar$ = "|"
			csorder.text$ = a$
			csorder.cr$ = CHR$(13)
			PUT #69, , csorder

			CLOSE #93

		shella$ = "CD " + MID$(faxpath$, 1, LEN(faxpath$) - 1)
		shellb$ = "CONVERT " + faxfile$ + " /C"
		shellc$ = "CD " + CURDIR$

		PCOPY 0, 1
		CLS
		PRINT shella$
		PRINT shellb$
		PRINT shellc$

		SHELL shella$
		SHELL shellb$
		SHELL shellc$
		PCOPY 1, 0

		'?? npgm$ = "SNDFAX": CALL exitpgm(npgm$): CLOSE : CHAIN npgm$
		END IF

	IF viewfax% THEN
		shella$ = faxpath$ + "VIEWFAX " + faxfile$
		X% = INSTR(shella$, ".TXT")
		IF X% > 0 THEN MID$(shella$, X%, 4) = ".QFX"
		OPEN "vf.bat" FOR OUTPUT AS #98
		PRINT #98, shella$
		CLOSE #98
		PRINT shella$

		SHELL shella$


		END IF

		SLEEP 10

END SUB

SUB quick.load (updwn%, lin%, Cont%) STATIC
	lin.sav% = lin%
	thissup$ = sup.search$ + sup.stype$

	SELECT CASE sup.stype$
	CASE "A"
	IF NOT Cont% THEN rec3% = 1
	IF rec3% < 1 OR rec3% > maxacc% THEN rec3% = 1

	GET #3, rec3%, acstk
	DO WHILE NOT EOF(3)
		IF acstk.no% = rec3% THEN
		IF acstk.suplr$ = thissup$ THEN
			in$(lin%, 1) = "1"
			in$(lin%, 2) = acstk.size$ + acstk.unit$
			in$(lin%, 3) = STR$(acstk.no%)
			in$(lin%, 4) = acstk.desc1$
			in$(lin%, 5) = acstk.desc2$
			in$(lin%, 6) = STR$(acstk.purcost!)
			updwn% = -1
			CALL det.entry(updwn%, lin%, "1")
			CALL dsply.lines(lin%, lin%)
			lin% = lin% + 1
			IF lin% > 18 THEN Cont% = -1: EXIT DO
			END IF
			END IF

		'>> - Wheel on screen
		IF rec3% MOD 100 = 0 THEN
			chr% = chr% + 1: IF chr% > 4 THEN chr% = 1
			chrlist$ = "|/-\": char$ = MID$(chrlist$, chr% + 1, 1)
			LOCATE 22, 78: PRINT char$
			END IF

		GET #3, , acstk: rec3% = rec3% + 1
		LOOP

	CASE ELSE
	IF NOT Cont% THEN rec38% = 1
	IF rec38% < 1 OR rec38% > maxrmat% THEN rec38% = 1

	GET #38, rec38%, msrmat
	DO WHILE NOT EOF(38)
		IF msrmat.no% = rec38% THEN
		IF msrmat.search$ = thissup$ THEN
			in$(lin%, 1) = "1"
			in$(lin%, 2) = msrmat.PurUnit$
			in$(lin%, 3) = STR$(msrmat.no%)
			in$(lin%, 4) = msrmat.desc1$
			cost! = msrmat.purcost!
			IF msrmat.DealCost! > 0 AND msrmat.DealCost! < cost! THEN cost! = msrmat.DealCost!
			in$(lin%, 6) = STR$(cost!)
			in$(lin%, 7) = STR$(0)
			updwn% = -1
			CALL det.entry(updwn%, lin%, "1")
			CALL dsply.lines(lin%, lin%)
			lin% = lin% + 1
			IF lin% > 18 THEN Cont% = -1: EXIT DO
			END IF
			END IF
		GET #38, , msrmat: rec38% = rec38% + 1
		LOOP
	END SELECT

	lin% = lin.sav%
END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
'>>>>> Lookup index file. Passed skey$. Returns SKEY, 0 if not found. <<<<<
'>>>>> SKEY1, one after insertion place                               <<<<<
	keyin$ = UCASE$(keyin$)
	found% = 0
	max% = LOF(chi%) / 5
	s% = 0: e% = max%

searchagain:
	p% = (e% - s%) / 2 + s%
	IF p% = 0 THEN GOTO X.SEARCHINDEX
	GET #chi%, p%, supx
	IF CVI(supx.wrrn$) = 0 THEN LSET supx.wcde$ = STRING$(99, CHR$(255))
	IF supx.wcde$ = keyin$ THEN found% = -1: GOTO X.SEARCHINDEX
	IF supx.wcde$ < keyin$ AND s% <> p% THEN s% = p%: GOTO searchagain
	IF supx.wcde$ > keyin$ AND e% <> p% THEN e% = p%: GOTO searchagain

X.SEARCHINDEX:
END SUB

