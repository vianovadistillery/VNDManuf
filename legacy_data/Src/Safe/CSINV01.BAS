DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB calcusecost ()
DECLARE SUB IGArmat (rec%)
DECLARE SUB IGAAcc (rec%)
DECLARE SUB iga2 (rec%)
DECLARE SUB accbrowse (rec%)
DECLARE SUB iga ()
DECLARE SUB stockcalc (stock!)
'.dc - Complete
'////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>  C S I N V 0 1  - Supplier Stock Entry
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
DECLARE SUB browse.idx (first.on.screen%, ch1%, ch2%)
	'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	CONST vh% = 4
	CONST ne% = 18
	CONST maxddf% = 18
	RESET: apgm$ = "CSMENU"
	DB.OR.CR$ = "CR"
	DIM menu$(3)
	DIM SHARED s%(500), add(500), calc(500)
	DIM SHARED s2%(500), add2(500), calc2(500)
	DIM SHARED ddf%(maxddf%)

	''INCLUDE: '\tpmanuf\src\pgmerr.inc'
very.start:
	CLOSE
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	'$INCLUDE: '\tpmanuf\src\msrmat.inc'
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	'$INCLUDE: '\tpmanuf\src\acmgn.inc'
	'$INCLUDE: '\tpmanuf\src\acstk.inc'
	'$INCLUDE: '\tpmanuf\src\company.inc'
	keyl% = 20: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)
	CALL index("OPEN ", ind%, "acstkx3.acf", 7, keyl%)
	OPEN "c:\tpexe\acstk.WRK" FOR RANDOM AS #4 LEN = 16
	TYPE RcdFmtWrk1
		wrkrrn AS STRING * 2
		wrkqty AS STRING * 4
		END TYPE
	DIM SHARED wrk1 AS RcdFmtWrk1
'/////////////////////////////////////////////////////////////////////////////
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)

	COLOR 2, 0
300
	heading$ = "SUPPLIER INWARD GOODS"
 'btm$ = "F1-Exit   F5-Recost      F6-Browse       F8-Raw Materials   F9-Accessories  "
	btm$ = "F1-Exit   F5-Recost      F6-Browse                         F10-Enter Stock  "
	CALL setup(heading$)
	COLOR 7, 0: LOCATE 2, 18: PRINT "µ                              Æ"; : COLOR 2
370
	COLOR 0, 3: LOCATE 25, 4: PRINT btm$; : COLOR 2, 0
	updwn% = 0:
	IF NOT pass% THEN
		COLOR 2, 0: in$ = ""
		LOCATE 2, 20: PRINT "Enter supplier code....> "
		LOCATE 2, 44
		CALL inpnew(in$, 105!, updwn%, "13,59,63-64,66-68" + ALT$): GOSUB ALT
				in$ = UCASE$(in$)
	END IF
	pass% = 0

	IF updwn% = 59 THEN CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$

	IF updwn% = 63 THEN
		ENVIRON "PARM$=AUTOC."
		npgm$ = "MSUPD02D"
		CLOSE
		CALL EXITPGM(npgm$): CHAIN npgm$
	END IF

	IF updwn% = 64 THEN
		CALL browse.idx(first.on.screen%, 45, 44)
		in$ = STR$(first.on.screen%)
		pass% = -1
		GOTO 300
	END IF

	'IF updwn% = 66 THEN
	'  PCOPY 0, 1
	'  CALL IGARmat(rec%)
	'  PCOPY 1, 0
	'  GOTO 370
	'END IF
	'
	'IF updwn% = 67 THEN
	'  PCOPY 0, 1
	'  CALL IGAAcc(rec%)
	'  PCOPY 1, 0
	'  GOTO 370
	'END IF

	IF updwn% = 68 THEN
		PCOPY 0, 1
		IF sup.stype$ = "S" THEN
			CALL IGArmat(rec%)
		ELSE
			CALL IGAAcc(rec%)
		END IF
		PCOPY 1, 0
		GOTO 370
	END IF

	IF LEN(in$) = 0 THEN p = p + 1: GOTO 520
	p = VAL(in$)
	IF p > 0 THEN 520
	skey$ = in$: CALL searchindex(skey$, 45, ok%)
	p = CVI(supx.wrrn$)
'/////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>>>>> Get record and display <<<<<<<<<<<<<<<<<<<<<<<<<<<
'/////////////////////////////////////////////////////////////////////////////
520
	rec% = p
	IF rec% < 1 OR rec% > maxsup% THEN COLOR 14: LOCATE 4, 20: PRINT "Not found on file.": COLOR 2: GOTO 370
	GET #44, rec%, sup
	sno% = CVI(sup.sno$)
	scur = CVS(sup.scur$): s30 = CVS(sup.s30$): s60 = CVS(sup.s60$): s90 = CVS(sup.s90$)
	sdays% = CVI(sup.sdays$): climit = CVS(sup.climit$)
	sterms = CVS(sup.sterms$): daysmax% = CVI(sup.daysmax$)
	IF sno% = 0 THEN sno% = rec
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
	IF climit < 1 THEN upd1$ = "Trading terms"
	IF climit = 0 THEN upd1$ = "C.O.D        "
	IF climit > 0 THEN upd1$ = STR$(climit)
	COLOR 6
	LOCATE , X0: PRINT "Total        90+ Days     60 Days     30 Days      Current    C/Limit"
	COLOR 2
	LOCATE , 2: PRINT USING "###,###.##  ####,###.##   ###,###.##   ###,###.## #,###,###.##   \           \"; total; s90; s60; s30; scur; upd1$
	GOTO 370
'////////////////   BROWSE R/MAT FILE AND KEY NEW I.G.A'S   /////////////////
'////////////////////////////////////////////////////////////////////////////
upd.raw.mat:
	typeofload$ = "A": retry$ = "N"
	n% = 0
	COLOR 4, 3
	LOCATE 1, 25: PRINT "  RAW MATERIAL STOCK ENTRY   "
	btm$ = "F1-Exit    F5/F6-Backward/Forward   F8-Summary   F9-Active  F10-Suspended"
	COLOR 0, 3: LOCATE 25, 4: PRINT btm$; : COLOR 2, 0
'//////////////////   Search for raw mats for this supplier  ////////////////
upd.search:
	CALL BOX(25, 6, 55, 8, 7, 1, 2)
	LOCATE 7, 32: COLOR 10, 1: PRINT "  Searching... " + typeofload$: COLOR 2, 0
	i% = 0: GET #38, 1, msrmat
	WHILE NOT EOF(38)
		i% = i% + 1
		IF msrmat.search$ = sup.search$ + sup.stype$ THEN
		IF typeofload$ = UCASE$(msrmat.active$) OR typeofload$ = "All" THEN
			FOR j% = 1 TO n%
				IF s%(j%) = i% THEN j% = 32766
				NEXT
			IF j% < 32766 THEN n% = n% + 1: s%(n%) = i%: add(n%) = 0: calc(n%) = 0
			END IF
			END IF

		GET #38, , msrmat
		WEND
	IF n% = 0 AND retry$ = "N" THEN
		retry$ = "Y"
		IF typeofload$ = "A" THEN typeofload$ = "S" ELSE typeofload$ = "A"
		SOUND 1000, 1
		GOTO upd.search
		END IF
	s% = 1: oldi% = -1
'/////////////////////////////////////////////////////////////////////////////
'/////////////////////////////  Display a page  //////////////////////////////
'/////////////////////////////////////////////////////////////////////////////
	CALL setup(heading$)
	COLOR 7, 0
	COLOR 6, 0: LOCATE 3, 2
	PRINT "Seq. Description.             A   S.O.H.     Cost       Deal     I/G     Value"
	COLOR 2, 0
'>>>>>>>>>>>>>>>>>>>>>>>>>>> If nothing was found? <<<<<<<<<<<<<<<<<<<<<<<<<<<
	IF n% = 0 THEN
		COLOR 14, 0
		LOCATE 21, 2: PRINT "No stock items for this supplier. "
		COLOR 2, 0
		upd1$ = "A"
		DO
			LOCATE 21, 71
			CALL inpnew(upd1$, 101!, updwn%, "13,59,73,81,66-68")
						upd1$ = UCASE$(in$)
			LOOP UNTIL upd1$ = "A" OR upd1$ = "U"
		IF updwn% = 59 THEN upd1$ = "A"
		IF upd1$ = "A" THEN ESC% = 1'>- Escape and DO NOT update
		IF upd1$ = "U" THEN ESC% = 0'>- Escape and update -
		LOCATE 21, 2: PRINT SPACE$(78)
		GOTO x.upd.raw.mat
		END IF
'////////////////////////////////////////////////////////////////////////////
GETDET:
	COLOR 0, 3: LOCATE 25, 15: PRINT SPACE$(61);
	COLOR 2, 0
	ESC% = 99
	WHILE ESC% = 99
		COLOR 2, 0
		IF s% < 1 THEN s% = 1
		IF s% > n% THEN s% = n%
		LOCATE vh%
		FOR i% = 0 TO ne%
			si% = s% + i%
			LOCATE , 2
			IF i% > n% OR s%(si%) < 1 OR s%(si%) > maxrmat% THEN
				PRINT SPACE$(78)
				ELSE
				GET #38, s%(si%), msrmat
				stock! = add(si%)
				CALL stockcalc(stock!)
				soh! = msrmat.soh + stock!

				PRINT USING "#### \                       \! ####.##\\ ####.##\\ #####.##\\####.## #####.##"; s%(si%); msrmat.desc1$; msrmat.active$; soh!; msrmat.UseUnit$; msrmat.purcost; msrmat.PurUnit$; msrmat.DealCost; msrmat.PurUnit$; add(si%); calc( _
si%);
				COLOR 3: LOCATE i% + vh%, 32: PRINT USING "!"; msrmat.active$: COLOR 2
				GOSUB hlight
				PRINT
				END IF
			NEXT


	GOSUB det.entry
	IF updwn% = 59 THEN
		CALL sndmsg(SPACE$(70))
		COLOR 14, 0
		LOCATE 24, 30: PRINT "All OK....> ";
		LOCATE 24, 45
		COLOR 2, 0
		upd1$ = "Y"
		CALL inpnew(upd1$, 101!, updwn%, "13,59,66-68,73,81")
				upd1$ = UCASE$(upd1$)
		IF upd1$ = "Y" THEN ESC% = 0     '>-- Escape and update --
		IF updwn% = 59 THEN ESC% = 1  '>-- Escape and DO NOT update -
		CALL sndmsg("")
		END IF
'/////////////////////////////  Command keys  ///////////////////////////////
	IF updwn% = 0 THEN s% = s% + 19
	IF updwn% = 72 THEN s% = s% - 19
	IF updwn% = 73 THEN s% = s% - 19
	IF updwn% = 81 THEN s% = s% + 19
	IF updwn% = 66 THEN GOSUB condense: GOTO GETDET
	IF updwn% = 67 THEN
		SELECT CASE typeofload$
		CASE "A":   typeofload$ = "All"   '>- Change the load type to suspended -
		CASE "All": typeofload$ = "S" '>- Change the load type to active
		CASE "S":   typeofload$ = "A"   '>-- Change the load type to active
		CASE ELSE:  typeofload$ = "A"
		END SELECT
		GOSUB condense
		GOTO upd.search
		END IF
	WEND
'/////////////////////////////////////////////////////////////////////////////
'////////////////////////// Edit before update ///////////////////////////////
'/////////////////////////////////////////////////////////////////////////////
x.upd.raw.mat:
	CALL setup(heading$)
RETURN
'////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>  ERROR ROUTINE 1  <<<<<<<<<<<<<<<<<<<<<<<<<<<
'////////////////////////////////////////////////////////////////////////////
ER1: COLOR 14, 0: LOCATE 21, 4: PRINT msg$: COLOR 2
	 RETURN
xer1: LOCATE 21, 2: PRINT SPACE$(78): COLOR 2
	 RETURN
'////////////////////////////////////////////////////////////////////////////
'////////////////////  Highligt changed line. ie. keyed I.G.A ///////////////
'////////////////////////////////////////////////////////////////////////////
hlight:
	IF add(s% + i%) > 0 THEN COLOR 10
	LOCATE i% + vh%, 72: PRINT USING "#####.##"; calc(si%);
	COLOR 2
RETURN
'////////////////////////////////////////////////////////////////////////////
'////////////////////////////  Detail entry subr  ///////////////////////////
'////////////////////////////////////////////////////////////////////////////
det.entry:
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit    F3-Change cost    F9-Toggle Act,All,Susp.    Pg Up/Down   " + CHR$(24); CHR$(25); "-move";
	COLOR 2, 0
	FOR i% = 0 TO ne%
	 IF oldi% <> -1 THEN
			i% = oldi%: oldi% = -1
			IF i% + s% > n% THEN i% = n% - s%
			END IF
2300 IF i% < 0 THEN i% = 0
	si% = s% + i%
	rec% = s%(si%)
	 IF i% > n% OR rec% < 1 OR rec% > maxrmat% THEN 2400
	 GET #38, rec%, msrmat
	updwn% = 0
		LOCATE i% + vh%, 64: updwn% = 1
		in$ = STR$(add(si%))
								CALL inpnew(in$, 6.2, updwn%, "13,59,60-61,73,81,66-68,72,80")
	IF updwn% = 59 THEN i% = 999: GOTO 2400
	IF updwn% = 61 THEN '>- Update cost on file --
		LOCATE i% + vh%, 43: updwn% = 1
		in$ = STR$(msrmat.purcost)
								CALL inpnew(in$, 7.2, updwn%, "13,59")
		IF updwn% <> 59 THEN
			in = VAL(in$)
			msrmat.purcost = in
			PUT #38, rec%, msrmat
			END IF
		LOCATE i% + vh%, 54: updwn% = 1
		in$ = STR$(msrmat.DealCost)
								CALL inpnew(in$, 7.2, updwn%, "13,59")
		IF updwn% <> 59 THEN
			in = VAL(in$)
			msrmat.DealCost = in
			PUT #38, rec%, msrmat
			END IF
		i% = i% - 1
		GOTO 2400
		END IF

	add(si%) = VAL(in$)
	calc(si%) = add(si%) * msrmat.purcost
	LOCATE i% + vh%, 64: PRINT USING "####.##"; add(i% + s%);
	stock! = add(si%)
	CALL stockcalc(stock!)
	LOCATE i% + vh%, 32: PRINT USING "######.##"; msrmat.soh + stock!
	GOSUB hlight    '>- Highlight keyed line --
	 msrmat.soh = total

	cnt% = 0: dollar! = 0
	FOR j% = 1 TO n%: IF calc(j%) <> 0 THEN cnt% = cnt% + 1: dollar! = dollar! + calc(j%)
		NEXT
	COLOR 7
	LOCATE 24, 71: PRINT USING "µ\      \º"; " ";
	LOCATE 24, 71: PRINT USING "######.##"; dollar!;

	IF updwn% = 13 OR updwn% = 80 THEN updwn% = 0
	IF updwn% = 73 THEN EXIT FOR
	IF updwn% = 81 THEN EXIT FOR
	IF updwn% = 60 THEN updwn% = 72
	IF updwn% = 67 THEN EXIT FOR
	IF updwn% = 68 THEN EXIT FOR
	IF updwn% = 72 THEN
		i% = i% - 2
		IF i% < -1 THEN oldi% = 18: i% = 999
		END IF
	'IF updwn% > 0 THEN i% = 999
2400
	NEXT
RETURN
'/////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>   HOLD SELETED ITEMS IN THE SCREEN ARRAYS  <<<<<<<<<<<<<<<<<<<<<
'/////////////////////////////////////////////////////////////////////////////
condense:
	n1% = n%: n% = 0
	FOR i% = 1 TO n1%
		IF add(i%) <> 0 THEN
			n% = n% + 1
			s2%(n%) = s%(i%)
			add2(n%) = add(i%)
			calc2(n%) = calc(i%)
			END IF
		NEXT
'>>>>>>>>>>>>>>>>>>>>>  Copy data back to live arrays  <<<<<<<<<<<<<<<<<<<<<<
	FOR i% = 1 TO n%
			s%(i%) = s2%(i%)
			add(i%) = add2(i%)
			calc(i%) = calc2(i%)
			NEXT
'>>>>>>>>>>>>>>>>>>>>>  Clear remaining part of array  <<<<<<<<<<<<<<<<<<<<<<
	FOR i% = n% + 1 TO n1%: s%(i%) = 0: add(i%) = 0: calc(i%) = 0: NEXT
	RETURN

SUB accbrowse (rec%) STATIC
'$INCLUDE: '\tpmanuf\src\accbrow.bi'
END SUB

SUB browse.idx (firstonscreen%, ch1%, ch2%) STATIC
'$INCLUDE: '\tpmanuf\src\browse01.bi'
END SUB

SUB calcusecost
'$INCLUDE: '\tpmanuf\src\IGACalc.bi'
END SUB

SUB IGAAcc (rec%)
maxacc% = 2000
'$INCLUDE: '\tpmanuf\src\IGAACC.bi'
END SUB

SUB IGArmat (rec%)
maxrmat% = 2000
'$INCLUDE: '\tpmanuf\src\IGARMAT.bi'
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

'* Calculate form. amount from SG & cost price
SUB stockcalc (stock!) STATIC
	'////////////////////////////////////////////////////////
	'>>>>> THE CALCULATION OF THE STOCK UPDATE FIGURE
	'////////////////////////////////////////////////////////
	 ab$ = msrmat.PurUnit$ + "-" + msrmat.UseUnit$
	 sgwork = msrmat.Sg
	 IF sgwork < .0001 THEN sgwork = 1
	 SELECT CASE ab$
	 CASE "KG-LT": msrmat.UseCost = msrmat.purcost * sgwork: stock! = stock! / sgwork
	 CASE "LT-KG": msrmat.UseCost = msrmat.purcost / sgwork: stock! = stock! * sgwork
	 CASE "/M-EA": msrmat.UseCost = msrmat.purcost / 1000: stock! = stock! * 1000
	 CASE "/H-EA": msrmat.UseCost = msrmat.purcost / 100: stock! = stock! * 100
	 CASE "MT-KG": msrmat.UseCost = msrmat.purcost / 1000: stock! = stock! * 1000
	 CASE "MT-LT": msrmat.UseCost = msrmat.purcost * sgwork / 1000: stock! = stock! / 1000
	 CASE ELSE: msrmat.UseCost = msrmat.purcost: stock! = stock!
	 END SELECT

	 CALL ROUND(msrmat.UseCost, 2.5)

END SUB
