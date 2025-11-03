DECLARE SUB iyj.mls (Y%, u%, mls%, u.oz%, ml.oz!)
DECLARE SUB mls.iyj (Y%, u%, alpha$, mls%, u.oz%, ml.oz!)
DECLARE SUB browse.col (ret%, updwn%)
DECLARE SUB codei (ain%, aout$)
DECLARE SUB inpscreen (l!(), in$(), fmt!(), upd%(), allow$, fgnd%, bgnd%, f%)
	'>>>>>>>>>>>>>>>>>> RTCOL01 - Colour Formula File <<<<<<<<<<<<<<<<<<<<<<
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\colsyst.inc'
	apgm$ = "ACMENU"
	typefields% = -1
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	maxcht% = 9999: maxsup% = 1000
	CONST nf% = 7
	DIM TC$(5), tv%(5), tv$(5), tcx$(5), tvx%(5), tdolx(5)
	DIM l(nf%), in$(nf%), fmt(nf%), upd%(nf%)
	DIM A$(25)
	'Search for "standard" company
	FOR i% = 1 TO 20
		IF sno%(i%) = 1 THEN
			std.name$ = sname$(i%)
			std.sunpoz% = sunpoz%(i%)
			std.smlpoz = smlpoz(i%)
			EXIT FOR
			END IF
			NEXT
	btm$ = "F1-Exit.       F3-Insert.        F4-Delete.       F6-Browse        F9-Fast Add."
	hdg$ = "C O L O R   C H A R T   E N T R Y "
	CALL setup(hdg$)
	COLOR 0, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
	'$INCLUDE: '\tpmanuf\src\COLCHT.INC'
	'$INCLUDE: '\tpmanuf\src\COLBASE.INC'
	'$INCLUDE: '\tpmanuf\src\COLCARD.INC'
enter1:
	updwn% = 0
	WHILE updwn% <> 59
		COLOR 0, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
		LOCATE 4, 25: PRINT "Enter color number...> "; CHR$(FNH);
		A$ = ""
		CALL inpnew(A$, 105!, updwn%, "13,59,61-62,64,68" + alt$): GOSUB alt
		LOCATE 21, 2: PRINT sp78$
		IF updwn% = 13 THEN
			IF LEN(A$) = 0 THEN rec% = rec% + 1 ELSE rec% = VAL(A$)
			IF rec% < 1 OR rec% > maxcht% THEN
				COLOR 14: LOCATE 21, 2: PRINT USING "Chart number #### not valid."; rec%: COLOR 2
				updwn% = 0: rec% = 0
				END IF
			END IF
		IF updwn% = 61 THEN GOSUB insert.rec
		IF updwn% = 62 THEN GOSUB delet
		IF updwn% = 64 THEN GOSUB browse
		IF updwn% = 66 THEN GOSUB quote: updwn% = 13
		IF updwn% = 67 THEN GOSUB range
		IF updwn% = 68 THEN s% = 1: GOSUB change
		IF updwn% = 13 THEN GOSUB dsply
		WEND
	CLOSE :
	CALL exitpgm(apgm$)
	CHAIN apgm$
	'///////////////////////////////////////////////////////////////////////
	'/////  D I S P L A Y
	'///////////////////////////////////////////////////////////////////////
dsply:
	IF rec% < 1 OR rec% > maxcht% THEN RETURN
	GET #12, rec%
	TNO% = CVI(TNO$)
	IF tdate$ = nul8$ OR tdate$ = sp8$ OR TNO% <> rec% THEN '.dc
							GOSUB zero
							CALL setup(hdg$)
							RETURN
							END IF
	TSUPLR% = CVI(TSUPLR$)
	IF TSUPLR% < 1 OR TSUPLR% > maxsup% THEN TSUPLR% = 1: LSET TSUPLR$ = MKI$(1)
	FOR i% = 1 TO 20
		IF TSUPLR% = sno%(i%) THEN
			sname$ = sname$(i%)
			sunpoz% = sunpoz%(i%)
			smlpoz = smlpoz(i%)
			END IF
		NEXT
	TCNO% = CVI(TCNO$)
	IF TCNO% < 1 OR TCNO% > 99 THEN TCNO% = 1: LSET TCNO$ = MKI$(1)
	GET #11, TCNO%, colcard
	TBASE% = CVI(TBASE$)
	IF TBASE% < 1 OR TBASE% > 99 THEN TBASE% = 1: LSET TBASE$ = MKI$(1)
	GET #10, TBASE%, colbase
	tv%(1) = CVI(tv$(1)): tv%(2) = CVI(tv$(2)): tv%(3) = CVI(tv$(3)): tv%(4) = CVI(tv$(4)): tv%(5) = CVI(tv$(5))
	inout$ = "Interior/Exterior."
		IF TINEX$ = "E" THEN inout$ = "Exterior."
		IF TINEX$ = "I" THEN inout$ = "Interior."
	IF tdate$ < "19000101" OR tdate$ > "20991231" THEN LSET tdate$ = sp8$
	COLOR 6, 0: LOCATE 6, 20: PRINT "GENERAL INFORMATION": COLOR 2, 0
	LOCATE , 20: PRINT USING "Color number...........:####"; rec%
	LOCATE , 20: PRINT USING "Supplier...............>### - \                        \"; TSUPLR%; sname$
	LOCATE , 20: PRINT USING "Colour card............>## - \                    \ "; TCNO%; colcard.ccdesc$
	LOCATE , 20: PRINT USING "Interior/Exterior......>!  - \                       \"; TINEX$; inout$
	LOCATE , 20: PRINT USING "Base...................>## - \         \"; TBASE%; colbase.bdesc$
	COLOR 6, 0
	LOCATE , 20: PRINT "COLOR DETAILS"
	COLOR 2, 0
	CALL mls.iyj(a1%, a2%, a1$, tv%(1), sunpoz%, smlpoz)
	CALL mls.iyj(b1%, b2%, a2$, tv%(2), sunpoz%, smlpoz)
	CALL mls.iyj(c1%, c2%, a3$, tv%(3), sunpoz%, smlpoz)
	CALL mls.iyj(d1%, d2%, a4$, tv%(4), sunpoz%, smlpoz)
	CALL mls.iyj(e1%, e2%, a5$, tv%(5), sunpoz%, smlpoz)
	CALL mls.iyj(sa1%, sa2%, s1$, tv%(1), std.sunpoz%, std.smlpoz)' 64 & 26.7
	CALL mls.iyj(sb1%, sb2%, s2$, tv%(2), std.sunpoz%, std.smlpoz)
	CALL mls.iyj(sc1%, sc2%, s3$, tv%(3), std.sunpoz%, std.smlpoz)
	CALL mls.iyj(sd1%, sd2%, s4$, tv%(4), std.sunpoz%, std.smlpoz)
	CALL mls.iyj(se1%, se2%, s5$, tv%(5), std.sunpoz%, std.smlpoz)
	'>> e.g.
	'>> READ ZC%(N%),ZC$(N%),ZCMP%(N%),ZC2%(N%),ZCPCT(N%),PZDOL(N%)
	'>> DATA  01,  "mca  ",  001,  01,  100,  20.00
	tdollars = 0
	FOR N% = 1 TO 5
		FOR i% = 1 TO 200
			IF TC$(N%) = LEFT$(zc$(i%), 2) AND TSUPLR% = zcmp%(i%) THEN EXIT FOR
			'PRINT"|"TC$(1)"|"LEFT$(ZC$(I%),2)"|"I%"|"
			NEXT
		IF i% > 200 THEN
			tcx$(N%) = "    "
			tvx%(N%) = 0
			tdolx(N%) = 0
			ELSE
			tcx$(N%) = zc$(zc2%(i%))
			tvx%(N%) = tv%(N%) * zcpct(i%) / 100
			tdolx(N%) = tv%(N%) * pzdol(i%) / 1000'**** This line here **** '??
			END IF
		tdollars = tdollars + tdolx(N%)
		NEXT
	CALL mls.iyj(sa1%, sa2%, x1$, tvx%(1), std.sunpoz%, std.smlpoz)' 64 & 26.7
	CALL mls.iyj(sb1%, sb2%, x2$, tvx%(2), std.sunpoz%, std.smlpoz)
	CALL mls.iyj(sc1%, sc2%, x3$, tvx%(3), std.sunpoz%, std.smlpoz)
	CALL mls.iyj(sd1%, sd2%, x4$, tvx%(4), std.sunpoz%, std.smlpoz)
	CALL mls.iyj(se1%, se2%, x5$, tvx%(5), std.sunpoz%, std.smlpoz)
	LOCATE , 20: PRINT USING "Suppliers ID number....>\        \ "; TSUPID$
	LOCATE , 20: PRINT USING "Color description......>\                            \ "; TDESC$
	COLOR 6
	LOCATE , 2: PRINT "  Tinter   Ml/10Lt   Formula...      Conversion.     Standard          Cost"
	COLOR 2
	IF tv%(1) > 0 THEN                  '0,000    CL 4y15...      CL 4y15....     MACL 4y15.... 1,234.56
	LOCATE , 2: PRINT USING "    1..>    #,###    \\ \      \     \\ \      \     \  \ \      \$$,###.##!"; tv%(1); TC$(1); a1$; TC$(1); s1$; tcx$(1); x1$; tdolx(1); CHR$(fne)
	ELSE
	LOCATE , 2: PRINT CHR$(fne)
	END IF
	IF tv%(2) > 0 THEN
	LOCATE , 2: PRINT USING "    2..>    #,###    \\ \      \     \\ \      \     \  \ \      \$$,###.##!"; tv%(2); TC$(2); a2$; TC$(2); s2$; tcx$(2); x2$; tdolx(2); CHR$(fne)
	ELSE
	LOCATE , 2: PRINT CHR$(fne)
	END IF
	IF tv%(3) > 0 THEN
	LOCATE , 2: PRINT USING "    3..>    #,###    \\ \      \     \\ \      \     \  \ \      \$$,###.##!"; tv%(3); TC$(3); a3$; TC$(3); s3$; tcx$(3); x3$; tdolx(3); CHR$(fne)
	ELSE
	LOCATE , 2: PRINT CHR$(fne)
	END IF
	IF tv%(4) > 0 THEN
	LOCATE , 2: PRINT USING "    4..>    #,###    \\ \      \     \\ \      \     \  \ \      \$$,###.##!"; tv%(4); TC$(4); a4$; TC$(4); s4$; tcx$(4); x4$; tdolx(4); CHR$(fne)
	ELSE
	LOCATE , 2: PRINT CHR$(fne)
	END IF
	IF tv%(5) > 0 THEN
	LOCATE , 2: PRINT USING "    5..>    #,###    \\ \      \     \\ \      \     \  \ \      \$$,###.##!"; tv%(5); TC$(5); a5$; TC$(5); s5$; tcx$(5); x5$; tdolx(5); CHR$(fne)
	ELSE
	LOCATE , 2: PRINT CHR$(fne)
	END IF
	'>>> Print the total cost for the tint
	IF tdollars > 0 THEN
	LOCATE , 67: PRINT USING "$$#,###.##"; tdollars
	ELSE
	LOCATE , 67: PRINT CHR$(fne)
	END IF
	LOCATE 3, 59: PRINT USING "Last update \       \"; FNDYY$(tdate$)
RETURN
'///////////////////////////////////////////////////////////////////////
'/////  C H A N G E
'///////////////////////////////////////////////////////////////////////
change:
	IF rec% < 1 OR rec% > maxcht% THEN RETURN
	IF tdate$ = nul8$ OR tdate$ = sp8$ OR TNO% <> rec% THEN
			LSET TNO$ = MKI$(rec%)
			LSET tdate$ = FNDY$(date1$)
			PUT #12, rec%
			GOSUB dsply
			END IF
	IF NOT loaded% THEN GOSUB loadit
	in$(1) = MID$(STR$(CVI(TSUPLR$)), 2)
	in$(2) = MID$(STR$(CVI(TCNO$)), 2)
	in$(3) = TINEX$
	in$(4) = STR$(CVI(TBASE$))
	in$(5) = STR$(CVI(TSUPLR$))
	in$(5) = TSUPID$
	in$(6) = TDESC$
	GOSUB crtstring
	in$(7) = A$
	LOCATE 15, 2: PRINT CHR$(fne)
	LOCATE 15, 20: PRINT "Tint formula...........>"
inpchange:
	CALL inpscreen(l(), in$(), fmt(), upd%(), "13,59", 2, 0, s%)
	LSET TNO$ = MKI$(rec%)
	LSET TSUPLR$ = MKI$(VAL(in$(1)))
	LSET TCNO$ = MKI$(VAL(in$(2)))
	LSET TINEX$ = in$(3)
	LSET TBASE$ = MKI$(VAL(in$(4)))
	LSET TSUPID$ = in$(5)
	LSET TDESC$ = in$(6)
	w$ = in$(7)
	GOSUB decodestring '>>>>> Decode the keyed string
	GOSUB doedit
	IF cerror% = -1 THEN GOTO inpchange
	IF epos% > 0 THEN
			COLOR 2: LOCATE 16, 44: PRINT "1...+....10....+....20....+....30"
			COLOR 14: LOCATE 16, 44 + epos%: PRINT "x": COLOR 2
			COLOR 14: LOCATE 21, 2: PRINT "Error position"; epos%; CHR$(fne): COLOR 2
			s% = 7
			GOTO inpchange
			END IF
	IF cerror% = 1 THEN 'update
		LSET tdate$ = FNDY$(date1$)
		PUT #12, rec%
		updwn% = 13
		END IF
	LOCATE 15, 20: PRINT CHR$(fne)
RETURN
	'///////////////////////////////////////////////////////////////////////
	'/////  C H A N G E    A     R A N G E    O F    R E C O R D S  :  Cmd:9
	'///////////////////////////////////////////////////////////////////////
range:
	IF rec% < 1 OR rec% > maxcht% - 1 THEN RETURN
	GOSUB doedit
	IF cerror% = -1 THEN RETURN
	IF epos% > 0 THEN RETURN
	'Continue
	srec% = rec%
	'Find next available record
	FOR i% = srec% + 1 TO maxcht%
		GET #12, i%
		TNO% = CVI(TNO$)
		IF tdate$ = nul8$ OR tdate$ = sp8$ OR TNO% <> i% THEN EXIT FOR
		NEXT
	IF i% > maxcht% THEN RETURN
	rec% = i%
	GET #12, srec%
	LSET TNO$ = MKI$(rec%)
	PUT #12, rec%
	GOSUB dsply
	s% = 4
	GOSUB change
	RETURN
'///////////////////////////////////////////////////////////////////////
'/////  Q U O T E
'///////////////////////////////////////////////////////////////////////
quote:
	CALL setup(hdg$)
	'>>- Display all tint systems <<<
	N% = 0:
	FOR i% = 1 TO 20
		IF sno%(i%) > 0 THEN N% = N% + 1
		NEXT
	C% = N% / 3
	y0% = 8: x0% = 2'**********
	y1% = y0% - 1
	x1% = x0%
	COLOR 6, 0
	FOR i% = 1 TO N%
		y1% = y1% + 1
		IF y1% > y0% + C% - 1 THEN y1% = y0%: x1% = x1% + 27
		LOCATE y1%, x1%: PRINT USING "### \                  \"; sno%(i%); sname$(i%)
		NEXT
	COLOR 2, 0
quote1:
	GOSUB doedit
	COLOR 6, 0
	LOCATE 5, 20: PRINT "GENERAL INFORMATION": COLOR 2, 0
	LOCATE 7, 20: PRINT USING "Supplier...............>### - \                        \"; TSUPLR%; sname$
	IF cerror% = 1 THEN GOTO quote2'First time in skip supplier (If valid?)
	A$ = MID$(STR$(TSUPLR%), 2)
	LOCATE 7, 44
	CALL inpnew(A$, 103!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.quote
	IF updwn% = 60 THEN GOTO x.quote
	LSET TSUPLR$ = MKI$(VAL(A$))
	TSUPLR% = CVI(TSUPLR$)
	GOTO quote1
quote2:
	LOCATE 14, 20: PRINT "Tint formula...........>";
	CALL inpnew(w$, 120!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.quote
	IF updwn% = 60 THEN LSET TSUPLR$ = MKI$(0): GOTO quote1
	GOSUB decodestring '>>>>> Decode the keyed string
	GOSUB doedit
	IF epos% > 0 THEN
			COLOR 2: LOCATE 15, 44: PRINT "1...+....10....+....20....+....30"
			COLOR 14: LOCATE 15, 44 + epos%: PRINT "x": COLOR 2
			COLOR 14: LOCATE 21, 2: PRINT "Error position"; epos%; CHR$(fne): COLOR 2
			s% = 7
			GOTO quote2
			END IF
	LOCATE 14, 20: PRINT CHR$(fne)
	CALL mls.iyj(a1%, a2%, a1$, tv%(1), sunpoz%, smlpoz)
	CALL mls.iyj(b1%, b2%, a2$, tv%(2), sunpoz%, smlpoz)
	CALL mls.iyj(c1%, c2%, a3$, tv%(3), sunpoz%, smlpoz)
	CALL mls.iyj(d1%, d2%, a4$, tv%(4), sunpoz%, smlpoz)
	CALL mls.iyj(e1%, e2%, a5$, tv%(5), sunpoz%, smlpoz)
	CALL mls.iyj(sa1%, sa2%, s1$, tv%(1), std.sunpoz%, std.smlpoz)' 64 & 26.7
	CALL mls.iyj(sb1%, sb2%, s2$, tv%(2), std.sunpoz%, std.smlpoz)
	CALL mls.iyj(sc1%, sc2%, s3$, tv%(3), std.sunpoz%, std.smlpoz)
	CALL mls.iyj(sd1%, sd2%, s4$, tv%(4), std.sunpoz%, std.smlpoz)
	CALL mls.iyj(se1%, se2%, s5$, tv%(5), std.sunpoz%, std.smlpoz)
	IF tv%(1) > 0 THEN
	LOCATE , 20: PRINT USING "Tint number 1.(#,###)..>\\ \          \     \\ \          \!"; tv%(1); TC$(1); a1$; TC$(1); s1$; CHR$(fne)
	ELSE
	LOCATE , 20: PRINT CHR$(fne)
	END IF
	IF tv%(2) > 0 THEN
	LOCATE , 20: PRINT USING "Tint number 2.(#,###)..>\\ \          \     \\ \          \!"; tv%(2); TC$(2); a2$; TC$(2); s2$; CHR$(fne)
	ELSE
	LOCATE , 20: PRINT CHR$(fne)
	END IF
	IF tv%(3) > 0 THEN
	LOCATE , 20: PRINT USING "Tint number 3.(#,###)..>\\ \          \     \\ \          \!"; tv%(3); TC$(3); a3$; TC$(3); s3$; CHR$(fne)
	ELSE
	LOCATE , 20: PRINT CHR$(fne)
	END IF
	IF tv%(4) > 0 THEN
	LOCATE , 20: PRINT USING "Tint number 4.(#,###)..>\\ \          \     \\ \          \!"; tv%(4); TC$(4); a4$; TC$(4); s4$; CHR$(fne)
	ELSE
	LOCATE , 20: PRINT CHR$(fne)
	END IF
	IF tv%(5) > 0 THEN
	LOCATE , 20: PRINT USING "Tint number 5.(#,###)..>\\ \          \     \\ \          \!"; tv%(5); TC$(5); a5$; TC$(5); s5$; CHR$(fne)
	ELSE
	LOCATE , 20: PRINT CHR$(fne)
	END IF
	A$ = ""'
	LOCATE 21, 20: PRINT "Hit ENTER to Continue."
	CALL inpnew(A$, 0!, updwn%, "ALL")
x.quote:
	CALL setup(hdg$)
RETURN
	'///////////////////////////////////////////////////////////////////////
	'/////    D E C O D E   A L P H A   S T R I N G
	'///////////////////////////////////////////////////////////////////////
decodestring:
	'>>>>> Decode the keyed string
	epos% = 0'Error position (if any)
	'- - - - - - - - - - - - - - - - - - - - - - - -
	'>>>>> FIRST BREAK IT UP INTO FIVE TINTS
	'- - - - - - - - - - - - - - - - - - - - - - - -
	A% = 1: FOR i% = 1 TO 5: A$(i%) = "": NEXT
	i$ = " ": prev$ = i$: ok% = 0: cnt% = 0
	FOR i% = 1 TO LEN(w$)
		LSET prev$ = i$: i$ = MID$(w$, i%, 1)
		IF i$ >= "0" AND i$ <= "9" THEN A$(A%) = A$(A%) + i$: ok% = -1: GOTO nxt
		IF i$ = "Y" AND ok% = 0 THEN GOTO nxt
		IF i$ = "y" AND ok% = 0 THEN GOTO nxt
		IF i$ >= "A" AND i$ <= "Z" THEN A$(A%) = A$(A%) + i$: ok% = -1: GOTO nxt
		IF i$ >= "a" AND i$ <= "z" THEN A$(A%) = A$(A%) + CHR$(ASC(i$) - 32): ok% = -1: GOTO nxt
		IF ok% THEN
			IF prev$ >= "0" AND prev$ <= "9" THEN A% = A% + 1
			IF prev$ = "Y" OR prev$ = "y" THEN A% = A% + 1
			ok% = 0: cnt% = 0
			END IF
nxt:           'CNT%=CNT%+1:IF CNT%>3 THEN A%=A%+1:OK%=0
	NEXT
	'- - - - - - - - - - - - - - - - - - - - - - - -
	'>>>> Now break each tint into colour and mls
	'- - - - - - - - - - - - - - - - - - - - - - - -
	FOR A% = 1 TO 5
	A$(A%) = A$(A%) + " "
	' Alpha code
	w$ = "": l% = LEN(A$(A%))
	i% = 1: i1% = 0: i$ = MID$(A$(A%), i%, 1)
	WHILE i$ >= "A" AND i$ <= "Z" AND i$ <> "Y" AND i% < l%
		w$ = w$ + i$
		i1% = i1% + 1: IF i1% > 2 THEN epos% = i%'Error if code longer than 2
		i% = i% + 1: i$ = MID$(A$(A%), i%, 1)
		WEND
	LSET TC$(A%) = w$
	' Number of ounces (Y's)
	w$ = "": w1$ = "": i1% = 0
	IF i$ = "Y" THEN w$ = "1"
	WHILE i$ >= "0" AND i$ <= "9" AND i% < l%
		w$ = w$ + i$
		i1% = i1% + 1: IF i1% > 2 THEN epos% = i%'Error if code longer than 2
		i% = i% + 1: i$ = MID$(A$(A%), i%, 1)
		WEND
	IF i% >= l% THEN w1$ = w$: w$ = "0"
	a1% = VAL(w$)
	' The next letter must be a Y
	i1% = 0
	WHILE i$ >= "A" AND i$ <= "Z" AND i% < l%
	IF i$ <> "Y" THEN epos = i%
		i1% = i1% + 1: IF i1% > 1 THEN epos% = i%'Error if "y" longer than 1
		i% = i% + 1: i$ = MID$(A$(A%), i%, 1)
		WEND
	' Number of Mls
	i1% = 0
	WHILE i$ >= "0" AND i$ <= "9" AND i% < l% + 1
		w1$ = w1$ + i$
		i1% = i1% + 1: IF i1% > 2 THEN epos% = i%'Error if code longer than 2
		i% = i% + 1: i$ = MID$(A$(A%), i%, 1)
		WEND
	a2% = VAL(w1$)
	'  Convert to Y's units to total mls
	IF a1% < 99 AND a2% < 99 THEN
		CALL iyj.mls(a1%, a2%, tv%(A%), sunpoz%, smlpoz)
		LSET tv$(A%) = MKI$(tv%(A%))
		END IF
	NEXT
RETURN
	'///////////////////////////////////////////////////////////////////////
	'/////    C R E A T E   A   A L P H A   S T R I N G
	'///////////////////////////////////////////////////////////////////////
crtstring:
	CALL mls.iyj(a1%, a2%, a1$, tv%(1), sunpoz%, smlpoz)
	CALL mls.iyj(b1%, b2%, a2$, tv%(2), sunpoz%, smlpoz)
	CALL mls.iyj(c1%, c2%, a3$, tv%(3), sunpoz%, smlpoz)
	CALL mls.iyj(d1%, d2%, a4$, tv%(4), sunpoz%, smlpoz)
	CALL mls.iyj(e1%, e2%, a5$, tv%(5), sunpoz%, smlpoz)
	A$ = ""
	A$ = A$ + TC$(1) + a1$
	A$ = A$ + TC$(2) + a2$
	A$ = A$ + TC$(3) + a3$
	A$ = A$ + TC$(4) + a4$
	A$ = A$ + TC$(5) + a5$
	IF MID$(A$, 1, 1) = " " THEN A$ = MID$(A$, 2)
RETURN
	'///////////////////////////////////////////////////////////////////////
	'/////  E D I T   S C R E E N
	'///////////////////////////////////////////////////////////////////////
doedit:
	cerror% = 1' 0-NO CHANGE,-1 CHANGE IN ERROR,1 = UPDATE RECORD
	'>> check supplier
	LOCATE 21, 2: PRINT sp78$'Clear error line
	TSUPLR% = CVI(TSUPLR$)
	IF TSUPLR% < 1 OR TSUPLR% > maxsup% THEN cerror% = -1: er$ = "Supplier number out of range.": s% = 1: GOTO xdoedit
	FOR i% = 1 TO 20
		IF TSUPLR% = sno%(i%) THEN
				sname$ = sname$(i%)
			sunpoz% = sunpoz%(i%)
			smlpoz = smlpoz(i%)
			EXIT FOR
			END IF
		NEXT
	IF sno%(i%) = 0 THEN cerror% = -1: er$ = "Supplier number not valid.": s% = 1: GOTO xdoedit
	'>> check tint codes are all capital
	FOR i% = 1 TO 5
		l$ = MID$(TC$(i%), 1, 1): R$ = MID$(TC$(i%), 2, 1)
		IF l$ >= "a" AND l$ <= "z" THEN l$ = CHR$(ASC(l$) - 32)
		IF R$ >= "a" AND R$ <= "z" THEN R$ = CHR$(ASC(R$) - 32)
		IF R$ = " " AND l$ <> " " THEN C$ = R$ + l$ ELSE C$ = l$ + R$
		LSET TC$(i%) = C$
		NEXT
xdoedit:
	IF cerror% THEN LOCATE 21, 2: COLOR 14, 0: PRINT er$: COLOR 2, 0: er$ = ""
	RETURN
	'///////////////////////////////////////////////////////////////////////
	'/////   I N S E R T    A    R E C O R D                          CMD:8
	'///////////////////////////////////////////////////////////////////////
insert.rec:
	IF rec% < 1 OR rec% > maxcht% - 1 THEN RETURN
	srec% = rec%
	'Find next available record
	FOR i% = srec% + 1 TO maxcht%
		GET #12, i%
		TNO% = CVI(TNO$)
		IF tdate$ = nul8$ OR tdate$ = sp8$ OR TNO% <> i% THEN EXIT FOR
		NEXT
	IF i% > maxcht% THEN RETURN
	rec% = i%
	'Move everything down
	FOR i% = rec% TO srec% + 1 STEP -1
		GET #12, i% - 1
		LSET TNO$ = MKI$(i%)
		PUT #12, i%
		NEXT
	rec% = srec%
	GOSUB dsply
	s% = 4
	GOSUB change
RETURN
	'///////////////////////////////////////////////////////////////////////
	'/////   D E L E T E                                              CMD:4
	'///////////////////////////////////////////////////////////////////////
delet:
	IF rec% < 1 OR rec% > maxcht% THEN RETURN
	IF tdate$ = nul8$ OR tdate$ = sp8$ OR CVI(TNO$) <> rec% THEN RETURN
	LOCATE 5, 25: COLOR 14: PRINT "D E L E T I O N   P E N D I N G": COLOR 2
	COLOR 8, 3: LOCATE 25, 2: PRINT sp78$;
	COLOR 8, 3: LOCATE 25, 30: PRINT "F1 - Abort.       F10 - Continue."; : COLOR 2, 0
	LOCATE 1, 1: A$ = " ": CALL inpnew(A$, 101!, updwn%, "59,68")
	LOCATE 5, 2: COLOR 2, 0: PRINT sp78$
	IF updwn% <> 68 THEN updwn% = 0: RETURN
	LSET TNO$ = MKI$(0)
	LSET TSUPLR$ = MKI$(0)
	LSET TCNO$ = MKI$(0)
	LSET TINEX$ = sp78$
	LSET TBASE$ = MKI$(0)
	LSET TBPERC$ = MKS$(0)
	LSET TDESC$ = sp78$
	LSET TSUPID$ = sp78$
	FOR i% = 1 TO 5
		LSET TC$(i%) = "  "
		LSET tv$(i%) = MKI$(0)
		NEXT
	LSET tdate$ = sp8$
	PUT #12, rec%
	GOSUB dsply
	updwn% = 0
	RETURN
	'///////////////////////////////////////////////////////////////////////
	'/////  B R O W S E
	'///////////////////////////////////////////////////////////////////////
browse:
	CALL setup("BROWSE COLOUR NUMBER")
	COLOR 0, 3: LOCATE 25, 1: PRINT " F1-Return                         Page up/down          F3-Swap ";
	COLOR 6, 0: LOCATE 3, 2: PRINT " Num *-----Colour description-----*  *-Code-*  CC I/E    Base        Supplier"
	COLOR 2, 0
	GOSUB onescreen
	WHILE updwn% <> 59
	COLOR 7, 0: LOCATE 2, 25: PRINT CHR$(185); " ";
	COLOR 2, 0: PRINT "Start browse from..>     ";
	COLOR 7, 0: PRINT " "; CHR$(204);
	COLOR 2, 0: LOCATE 2, 47: A$ = ""
	CALL inpnew(A$, 105!, updwn%, "13,59,61,73,81" + alt$): GOSUB alt
	IF updwn% = 13 OR updwn% = 81 THEN
		updwn% = 64
		IF LEN(A$) = 0 THEN rec% = lrec% ELSE rec% = VAL(A$)
		IF rec% < 1 OR rec% > maxcht% THEN
			COLOR 14: LOCATE 21, 2: PRINT USING "Colour number #### not valid."; rec%: COLOR 2
			updwn% = 0: rec% = 0
			END IF
		END IF
	IF updwn% = 73 THEN
		updwn% = 64
		IF LEN(A$) = 0 THEN rec% = lrec% - (mpage% * 2) + 2 ELSE rec% = VAL(A$)
		IF rec% < 1 OR rec% > maxcht% THEN rec% = 1
		END IF
	IF updwn% = 64 THEN GOSUB onescreen
	IF updwn% = 61 THEN CALL browse.col(ret%, updwn%)
	WEND
	IF updwn% = 59 THEN updwn% = 13
	CALL setup(hdg$)
	RETURN
	'>>--- LOAD ONE SCREEN
onescreen:
	thispage% = 0: misses% = 0: first% = -1: mpage% = 20
	LOCATE 4, 2
	IF rec% < 1 OR rec% > maxcht% THEN rec% = 1
	lrec% = rec%: GET #12, rec%
	WHILE thispage% < mpage% AND NOT EOF(12) AND misses < 50
		IF first% THEN GET #12, rec%: first% = 0 ELSE GET #12: lrec% = lrec% + 1
		LOCATE , 2
		TNO% = CVI(TNO$): obase$ = "  ": TCNO% = CVI(TCNO$)
		IF lrec% = TNO% AND tdate$ <> nul8$ AND tdate$ <> sp8$ THEN
			TSUPLR% = CVI(TSUPLR$): IF TSUPLR% < 1 OR TSUPLR% > maxsup% THEN TSUPLR% = 0
			IF TBASE$ <> obase$ THEN
				TBASE% = CVI(TBASE$): IF TBASE% < 1 OR TBASE% > 99 THEN TBASE% = 1
				IF TBASE% <> obase% THEN GET #10, TBASE%, colbase
				LSET obase$ = TBASE$: obase% = TBASE%
				END IF
			ix$ = "I/E"
			IF TINEX$ = "E" THEN ix$ = "EXT"
			IF TINEX$ = "I" THEN ix$ = "INT"
			PRINT USING "#### &  &  ## \  \  &    ####"; TNO%; TDESC$; TSUPID$; TCNO%; ix$; colbase.bdesc$; TSUPLR%
			thispage% = thispage% + 1
			ELSE
			misses% = misses% + 1
			END IF
		WEND
		IF misses% > 50 THEN
			IF thispage% < mpage% THEN COLOR 14: LOCATE 21, 2: PRINT "More than 50 records searched with no hits."; CHR$(fne): COLOR 2, 0
			FOR i% = thispage% TO mpage% - 1: LOCATE , 2: PRINT sp78$: NEXT
			END IF
		IF EOF(12) THEN FOR i% = thispage% TO mpage% - 1: LOCATE , 2: PRINT sp78$: NEXT
	RETURN
	'///////////////////////////////////////////////////////////////////////
	'/////  Z E R O ALL FIELDS
	'///////////////////////////////////////////////////////////////////////
zero:
	LSET TNO$ = MKI$(0)
	LSET TSUPLR$ = MKI$(0)
	LSET TCNO$ = MKI$(0)
	LSET TINEX$ = SPACE$(99)
	LSET TBASE$ = MKI$(0)
	LSET TSUPID$ = SPACE$(99)
	LSET TDESC$ = SPACE$(99)
	FOR i% = 1 TO 5
		 LSET TC$(i%) = SPACE$(99)
		 LSET tv$(i%) = MKI$(0)
		 NEXT
	LSET tdate$ = SPACE$(99)
	RETURN
	'///////////////////////////////////////////////////////////////////////
	'/////  L O A D    F I E L D   L O C A T I O N S
	'///////////////////////////////////////////////////////////////////////
loadit:
	'Description fields
	DATA 08.44, 103.0, 1
	DATA  9.44, 102.0, 1
	DATA 10.44, 101.0, 1
	DATA 11.44, 102.0, 1
	'Second description fields
	DATA 13.44, 110.0, 1
	DATA 14.44, 130.0, 1
	'Tint field
	DATA 15.44, 130.0, 1
	RESTORE loadit
	FOR x% = 1 TO nf%: READ l(x%), fmt(x%), upd%(x%): in$(x%) = "": NEXT
	loaded% = -1
	RETURN

SUB browse.col (ret%, updwn%) STATIC
	max.pag% = 50
	max.pag.len% = 20
	REDIM top.of.pag%(max.pag%): pag% = 0
	REDIM tv$(5), TC$(5)
	CALL setup("BROWSE BY COLOR DESCRIPTION")
	COLOR 0, 3: LOCATE 25, 1: PRINT " F1-Return                         Page up/down               F3-Swap";
	COLOR 6, 0: LOCATE 3, 4: PRINT "Num.  Colour Name                   Base.            Manufacturer.          "
	COLOR 2, 0
	FIELD #12, 2 AS TNO$, 2 AS TSUPLR$, 2 AS TCNO$, 1 AS TINEX$, 2 AS TBASE$, 4 AS TBPERC$, 30 AS TDESC$, 8 AS TSUPID$, 2 AS TC$(1), 2 AS tv$(1), 2 AS TC$(2), 2 AS tv$(2), 2 AS TC$(3), 2 AS tv$(3), 2 AS TC$(4), 2 AS tv$(4), 2 AS TC$(5), 2 AS tv$(5) _
, 49 AS filler$, 8 AS tdate$
	indexf$ = "COLALLX1.DAT": keyl% = 35
	qk$ = SPACE$(keyl%)
	ch.ind% = 2
	CALL index("OPEN ", ind%, indexf$, ch.ind%, keyl%)
	CALL index("FIRST", ind%, qk$, ch.ind%, keyl%)
atop:
	col$ = old.col$
	COLOR 7, 0: LOCATE 2, 25: PRINT "น ";
	COLOR 2, 0: PRINT "Start browse from..>     ";
	COLOR 7, 0: PRINT "ฬ"
	COLOR 2, 0: LOCATE 2, 26: PRINT "Enter Colour...>";
	CALL inpnew(col$, 110!, updwn%, "13,59,61,73,81")

	IF updwn% = 59 THEN GOTO x.browse.col
	IF updwn% = 61 THEN GOTO x.browse.col
		col$ = UCASE$(col$)
	'>> New search starts with a change of description <<
	SELECT CASE updwn%
	CASE 13, 81:  '>-Enter & page down
		'>>- Start of a new search
		IF old.col$ <> col$ THEN
			FOR i% = 1 TO max.pag%: top.of.pag%(i%) = 0: NEXT: pag% = 0
			old.col$ = col$
			IF VAL(col$) > 0 THEN
				ind% = VAL(col$)
				ELSE
				LSET qk$ = col$
				CALL index("CHAIN", ind%, qk$, ch.ind%, keyl%)
				IF ind% < 0 AND LEFT$(qk$, LEN(col$)) < col$ THEN
					CALL index("READ ", ind%, qk$, ch.ind%, keyl%)
					END IF
				IF ind% < 0 THEN ind% = 0 - ind%
				END IF
			pag% = pag% + 1: IF pag% > max.pag% THEN pag% = max.pag%
			'>>- Next page in this search
			ELSE
			pag% = pag% + 1: IF pag% > max.pag% THEN pag% = max.pag%
			END IF
	CASE 73: '>-Page Up
			pag% = pag% - 1
			IF pag% < 1 THEN pag% = 1
			ind% = top.of.pag%(pag%)
	CASE ELSE
	END SELECT
'>>--------------------------------
	'>> List the page?
	'>>-Note: This chain uses the full key
	'>>
	IF ind% >= 1 AND ind% <= 7000 THEN
		GET #12, ind%
		cmsort$ = MID$(STR$(CVI(TSUPLR$)), 2)
		TNO% = CVI(TNO$): CALL codei(TNO%, idx.tno$)
		LSET qk$ = TDESC$ + cmsort$ + idx.tno$
		CALL index("CHAIN", ind%, qk$, ch.ind%, keyl%)
		IF ind% < 0 THEN ind% = 0 - ind%
		END IF
'>>--------------------------------
	lin% = 0
	LOCATE 4, 1
	DO WHILE ind% > 0 AND lin% < max.pag.len%
		IF ind% < 1 OR ind% > 7000 THEN ind% = 1
		IF lin% = 0 THEN top.of.pag%(pag%) = ind%
		GET #12, ind%
		TCNO% = CVI(TCNO$)
		TSUPLR% = CVI(TSUPLR$)
		TBASE% = CVI(TBASE$)
		IF TSUPLR% = 1 THEN xx$ = "TRADEPAINTS   "
		IF TSUPLR% = 146 THEN xx$ = "LAPORTE       "
		IF TSUPLR% = 203 THEN xx$ = "BERGER-BRITISH"
		IF TSUPLR% = 204 THEN xx$ = "BRISTOL       "
		IF TSUPLR% = 206 THEN xx$ = "BRITISH -OLD  "
		IF TSUPLR% = 232 THEN xx$ = "HAYMES        "
		IF TSUPLR% = 278 THEN xx$ = "TAUBMANS      "
		IF TSUPLR% = 290 THEN xx$ = "WATTYL        "
		IF TSUPLR% = 844 THEN xx$ = "INDUSTRIAL    "
		IF TSUPLR% = 999 THEN xx$ = "DULUX         "
					'ELSE XX$ = "unknown       "
		LOCATE , 2
		PRINT USING "##,### \                            \  ##              \             \   (###)"; ind%; TDESC$; TCNO%; xx$; TSUPLR%
		lin% = lin% + 1
		CALL index("READ ", ind%, qk$, ch.ind%, keyl%)
		LOOP
GOTO atop
x.browse.col:
	ret% = top.of.pag%(pag%)
	IF updwn% = 59 AND old.col$ <> col$ THEN
			IF VAL(col$) >= 1 AND VAL(col$) <= 7000 THEN ret% = VAL(col$)
			END IF
	CLOSE #ch.ind%
EXIT SUB
END SUB

SUB codei (ain%, aout$) STATIC
	sfx$ = MKI$(ain%)
	aout$ = "  "
	MID$(aout$, 1, 1) = MID$(sfx$, 2, 1)
	MID$(aout$, 2, 1) = MID$(sfx$, 1, 1)
	END SUB

'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
'บ                    S C R E E N  I N P U T                             บ
'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
'     LOCATION
'     INPUT
'     FMT
'     UPD
'     ALLOW$
SUB inpscreen (l(), in$(), fmt(), upd%(), allow$, fgnd%, bgnd%, f%) STATIC
	limit% = UBOUND(l, 1)
	REDIM x%(limit%), Y%(limit%), online%(24)
	FOR i% = 1 TO limit%: x%(i%) = FIX(l(i%)): Y%(i%) = (l(i%) - x%(i%)) * 100
		online%(x%(i%)) = online%(x%(i%)) + 1
		x% = x%(i%): Y% = Y%(i%)
		LOCATE x%, Y%
		x = SCREEN(x%, Y%, 1): of% = (x MOD 16): ob% = (((x - of%) / 16) MOD 128)'Set prev color
		IF x > 127 THEN of% = of% + 16: ob% = ob% + 16
		IF of% = 7 AND ob% = 0 THEN of% = fgnd%: ob% = bgnd%
		COLOR of%, ob%: PRINT " ": LOCATE x%(i%), Y%(i%)
		updwn% = upd%(i%)
		CALL inpnew(in$(i%), fmt(i%), updwn%, "")'Display only.
		NEXT
	finish% = 0: wrap% = 0
	WHILE NOT finish%
		x% = x%(f%): Y% = Y%(f%)
		LOCATE x%, Y%
		updwn% = upd%(f%)
		A$ = allow$ + ",13,09,15,72,80,60"
		CALL inpnew(in$(f%), fmt(f%), updwn%, A$)
		IF updwn% = 60 THEN updwn% = 15
		IF updwn% = 9 THEN
						  GOSUB findfwd
		ELSEIF updwn% = 13 THEN GOSUB findfwd: IF wrap% THEN finish% = -1
		ELSEIF updwn% = 15 THEN GOSUB findbwd
		ELSEIF updwn% = 60 THEN GOSUB findbwd
		ELSEIF updwn% = 72 THEN 'Find directly above
			x% = x% - 1: IF x% < 1 THEN x% = 24
			Y% = Y% + 1: IF Y% > 80 THEN Y% = 1
			GOSUB findbwd
		ELSEIF updwn% = 80 THEN 'Find directly underneath
			x% = x% + 1: IF x% > 24 THEN x% = 1
			Y% = Y% - 1: IF Y% < 1 THEN Y% = 80
			GOSUB findfwd
		ELSE CALL KCHECK(updwn%, allow$): IF updwn% > 0 THEN finish% = -1
		END IF
		WEND
EXIT SUB
'//////////////////////////////////////
'/////// SUBROUTINE FIND FORWARD //////
'//////////////////////////////////////
findfwd:
			found% = 0: x% = x% - 1: Y% = Y% + 1: IF Y% > 80 THEN Y% = 0
			WHILE found% = 0
				x% = x% + 1: IF x% > 24 THEN x% = 1: wrap% = -1
				IF online%(x%) > 0 THEN
				FOR j% = Y% TO 80
					FOR i% = 1 TO limit%
						IF Y%(i%) = j% AND x%(i%) = x% THEN found% = i%: i% = 32766: j% = 32766
						NEXT
					NEXT
					Y% = 0
					END IF
			  WEND
			f% = found%
RETURN
'//////////////////////////////////////
'////// SUBROUTINE FIND BACKWARD //////
'//////////////////////////////////////
findbwd:
			found% = 0: x% = x% + 1: Y% = Y% - 1: IF Y% < 1 THEN Y% = 81
			WHILE found% = 0
				x% = x% - 1: IF x% < 1 THEN x% = 24
				IF online%(x%) > 0 THEN
				FOR j% = Y% TO 1 STEP -1
					FOR i% = 1 TO limit%
						IF Y%(i%) = j% AND x%(i%) = x% THEN found% = i%: i% = 32766: j% = -32766
						NEXT
					NEXT
					Y% = 81
					END IF
			  WEND
			f% = found%
RETURN
END SUB

	'///////////////////////////////////////////////////////////////////////
	'/////  C O N V E R T    xYz TO Mls per 10 litres.
	'///////////////////////////////////////////////////////////////////////
SUB iyj.mls (Y%, u%, mls%, u.oz%, ml.oz) STATIC
IF u.oz% <> 0 THEN
	mls% = ((Y% * u.oz% + u%) * ml.oz / u.oz%) * 2.5
	END IF
END SUB

	'///////////////////////////////////////////////////////////////////////
	'/////  C O N V E R T    Mls per 10 litres TO iYj
	'///////////////////////////////////////////////////////////////////////
SUB mls.iyj (Y%, u%, alpha$, mls%, u.oz%, ml.oz) STATIC
	IF ml.oz <> 0 THEN
		ounces = mls% / (2.5 * ml.oz)
		u% = (ounces - INT(ounces)) * u.oz%
		Y% = INT(ounces)
		IF u% = u.oz% THEN u% = 0: Y% = Y% + 1
		END IF
	'>> Now create the string for us humans <<
	alpha$ = ""
	IF Y% > 1 THEN alpha$ = MID$(STR$(Y%), 2) + "Y"
	IF Y% = 1 THEN alpha$ = "Y"
	IF u% > 0 THEN alpha$ = alpha$ + MID$(STR$(u%), 2)
END SUB
