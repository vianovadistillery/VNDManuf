DECLARE SUB fmtoutput (a$, x$, o%, m%)
DECLARE SUB mls.iyj (y%, u%, mls%, u.oz%, ml.oz!)
DECLARE SUB codei (ain%, aout$)
DECLARE SUB decodei (ain$, aout%)
	'>>>>>>>>>>>>>>>>>> RTCOL03- PRINT Colour Formula File <<<<<<<<<<<<<<<<<<<<<<
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "ACMENU"
	'$INCLUDE: '\tpmanuf\src\colsyst.inc'
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	'>>>>>>>>>>>>                    KEY MAPS                   <<<<<<<<<<<<
	'>>>> KEY MAP 1
	'          KFLD       TDESC$    30A   1  Tint desciption.
	'          KFLD       CMSORT$    3A  31  Tint company number
	'          KFLD       TNO$       2I  33  Tint number
	'                                    35
	'//
	CONST max.rec.in.index% = 7000
	CONST debug% = 0
	CONST max.to.print% = 32000
	DIM tv$(5), tc$(5), tv%(5), tcx$(5), tvx%(5), tdolx(5)
	DIM ptv$(5), ptc$(5)
	maxsup% = 2000: maxcht% = 32000
	DIM k%(maxacc%), s$(maxacc%), h%(15)
	CALL setup(" TINT FORMULA PRINT ")
	COLOR 8, 3: LOCATE 25, 30: PRINT "F1 - exit.";
	COLOR 2, 0
	CLOSE
	''$INCLUDE: '\tpmanuf\src\COLCHTX1.INC'
	OPEN "colchtx1.DAT" FOR RANDOM SHARED AS #1 LEN = 38
	CLOSE
	OPEN "colcht.DAT" FOR RANDOM SHARED AS #1 LEN = 128
	OPEN "colbase.DAT" FOR RANDOM SHARED AS #5 LEN = 15
	OPEN "colcard.DAT" FOR RANDOM SHARED AS #6 LEN = 22
	IF debug% THEN
		OPEN "CON" FOR OUTPUT AS #99
		ELSE
		OPEN "LPT1" FOR OUTPUT AS #99
		END IF
	FIELD #1, 2 AS tno$, 2 AS tsuplr$, 2 AS tcno$, 1 AS tinex$, 2 AS tbase$, 4 AS TBPERC$, 30 AS tdesc$, 8 AS TSUPID$, 2 AS tc$(1), 2 AS tv$(1), 2 AS tc$(2), 2 AS tv$(2), 2 AS tc$(3), 2 AS tv$(3), 2 AS tc$(4), 2 AS tv$(4), 2 AS tc$(5), 2 AS tv$(5),  _
49 AS FILLER$, 8 AS tdate$
	FIELD #5, 1 AS BSCODE$, 12 AS bdesc$, 2 AS BPERC$
	FIELD #6, 22 AS CCDESC$
	indexf$ = "COLALLX1.DAT": keyl% = 35
	qk$ = SPACE$(keyl%)
	ch% = 2
	'Search for "standard" company
	FOR i% = 1 TO 20
		IF sno%(i%) = 1 THEN
			std.name$ = sname$(i%)
			std.sunpoz% = sunpoz%(i%)
			std.smlpoz = smlpoz(i%)
			EXIT FOR
			END IF
			NEXT
amenu:
	COLOR 4, 0
	LOCATE 3, 30: PRINT " TINT FORMULA PRINT "
	LOCATE 4, 30: PRINT "===================="
	t$ = "1"
	COLOR 2, 0
	LOCATE 5, 20: PRINT "1...Report by name"
	LOCATE , 20: PRINT "2...Report using standard Mls/oz."
	LOCATE , 20: PRINT "3...Convert and report."
	LOCATE , 20: PRINT "8...Rebuild the index."
	LOCATE , 20: PRINT "9...Eject a page."
	'>>- Display all tint systems <<<
	n% = 0:
	FOR i% = 1 TO 20
		IF sno%(i%) > 0 THEN n% = n% + 1
		NEXT
	c% = n% / 3
	y0% = 10: x0% = 2
	y1% = y0% - 1
	x1% = x0%
	COLOR 6, 0
	FOR i% = 1 TO n%
		y1% = y1% + 1
		IF y1% > y0% + c% - 1 THEN y1% = y0%: x1% = x1% + 27
		LOCATE y1%, x1%: PRINT USING "### \                  \"; sno%(i%); sname$(i%)
		NEXT
	COLOR 2, 0
	LOCATE 15, 25: PRINT "Option..>"; CHR$(fnh);
	CALL inpnew(t$, 1!, updwn%, "59,13,80,9" + alt$): GOSUB alt
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	klist% = VAL(t$)
	SELECT CASE klist%
	CASE 1
		convert$ = "N"
		standard$ = "N"
		LOCATE 16, 20: PRINT "For supplier.....> "; CHR$(fnh);
		keyed.sup$ = "ALL"
		CALL inpnew(keyed.sup$, 103!, updwn%, "59-60,72,15,13" + alt$): GOSUB alt
		IF updwn% = 13 THEN GOSUB actprint
	CASE 2
		convert$ = "N"
		standard$ = "Y"
		LOCATE 16, 20: PRINT "For supplier.....> "; CHR$(fnh);
		keyed.sup$ = "ALL"
		CALL inpnew(keyed.sup$, 103!, updwn%, "59-60,72,15,13" + alt$): GOSUB alt
		IF updwn% = 13 THEN GOSUB actprint
	CASE 3
		convert$ = "Y"
		standard$ = "N"
		LOCATE 16, 20: PRINT "For supplier.....> "; CHR$(fnh);
		keyed.sup$ = "ALL"
		CALL inpnew(keyed.sup$, 103!, updwn%, "59-60,72,15,13" + alt$): GOSUB alt
		IF updwn% = 13 THEN GOSUB actprint
	CASE 8
		LOCATE 16, 20: PRINT "Rebuild the index..> "; CHR$(fnh); : bld$ = "N"
		CALL inpnew(bld$, 101!, updwn%, "59-60,72,15,13" + alt$): GOSUB alt
		IF updwn% = 13 AND bld$ = "Y" THEN GOSUB bldindex
	CASE 9
		PRINT #99, CHR$(12)
	CASE ELSE
	END SELECT
	GOTO amenu
'////////////////////////////////////////////////////////////////////////////
'>>>>> Build the index
'////////////////////////////////////////////////////////////////////////////
bldindex:
	KILL indexf$
	a$ = indexf$
	CALL index("OPEN ", ind%, a$, ch%, keyl%)
	rec% = 1
	GET #1, rec%
	'>>>-- Set the field sizes --<<<
	osuplr$ = tsuplr$: LSET osuplr$ = SPACE$(99)
	cmsort$ = "~~~"
	COLOR 2, 0
	LOCATE 18, 10: PRINT "Indexing...."
	printed% = 0
	DO WHILE NOT EOF(1) AND rec% <= max.rec.in.index%
	tno% = CVI(tno$)
	IF tdate$ > "19000101" AND tdate$ < "20991231" AND tno% = rec% THEN
		'>>>> Level break on supplier <<<<<
		'>>- Use the left four letters of the suppier name for sort -<<
		IF osuplr$ <> tsuplr$ THEN
			tsuplr% = CVI(tsuplr$)
			LSET cmsort$ = "~~~"
			FOR i% = 1 TO 20
				IF sno%(i%) = tsuplr% THEN
					LSET cmsort$ = MID$(STR$(sno%(i%)), 2)
					EXIT FOR
					END IF
				NEXT
			LSET osuplr$ = tsuplr$
			CALL codei(tsuplr%, idx.tsuplr$)
			END IF
		'>>> Detail time, Add the index record
		tno% = CVI(tno$)
		CALL codei(tno%, idx.tno$)
		LSET qk$ = tdesc$ + cmsort$ + idx.tno$
		LOCATE 18, 10: PRINT "Writing |"; tdesc$; "|"; cmsort$; "|"; tno%; "|"
		c$ = RIGHT$(qk$, 2)
		CALL decodei(c$, c%)
		LOCATE 19, 10: PRINT "Confirm |"; tdesc$; "|"; cmsort$; "|"; tno%; "|"
		CALL index("WRITE", ind%, qk$, ch%, keyl%)
		IF ind% <> 0 THEN SOUND 100, 2: xx$ = INPUT$(1)
		'>>> -
		END IF
		GET #1: rec% = rec% + 1
		LOOP
		CLOSE #ch%
x.bldmenu:
RETURN
'///////////////////////////////////////////////////////////////////////
'//// ACTUAL PRINT ROUTINE
'///////////////////////////////////////////////////////////////////////
actprint:
	a$ = indexf$
	CALL index("OPEN ", ind%, a$, ch%, keyl%)
	CALL index("FIRST", ind%, qk$, ch%, keyl%)
	lin% = 9999
	intext$ = "INT/EXT."
	'>> Get supplier name from keyed supplier<<
	FOR i% = 1 TO 20
		a% = VAL(keyed.sup$)
		IF a% = sno%(i%) THEN
			sname$ = sname$(i%)
			sunpoz% = sunpoz%(i%)
			smlpoz = smlpoz(i%)
			EXIT FOR
			END IF
		NEXT
	IF keyed.sup$ = "ALL" THEN
		sname$ = "ALL SUPPLIERS"
		sunpoz% = 0
		smlpoz = 0
		END IF
	rec% = 0
	DO WHILE ind% > 0 AND printed% < max.to.print%
		rec% = rec% + 1
		IF ind% < 1 OR ind% > maxcht% THEN ind% = 1
		GET #1, ind%
		tcno% = CVI(tcno$)
		'> Unpack the file
		ptdesc$ = tdesc$
		ptbase$ = tbase$
		ptinex$ = tinex$
		FOR i% = 1 TO 5: ptc$(i%) = tc$(i%): ptv$(i%) = tv$(i%): NEXT
		cmsort$ = MID$(qk$, 31, 3): cmsort% = VAL(cmsort$)
			tsuplr% = CVI(tsuplr$)
		'> If this list is for all suppliers the current mls/oz <<
		'> must get looked up for each record <<
		IF keyed.sup$ = "ALL" THEN
			FOR i% = 1 TO 20
				a% = CVI(tsuplr$)
				IF a% = sno%(i%) THEN
					sunpoz% = sunpoz%(i%)
					smlpoz = smlpoz(i%)
					EXIT FOR
					END IF
			NEXT
			END IF
		'// Print decisions ///
		ok% = 0
		IF keyed.sup$ = "ALL" THEN ok% = 1
		IF keyed.sup$ = cmsort$ THEN ok% = 1
		'// Print depending on previous decision ///
		IF ok% = 1 THEN
			IF lin% > 50 THEN GOSUB heading
							LSET intext$ = "Int/Ext."
			IF tinex$ = "I" THEN LSET intext$ = "Interior"
			IF tinex$ = "E" THEN LSET intext$ = "Exterior"
			tbase% = CVI(tbase$)
			IF tbase% < 1 OR tbase% > 99 THEN tbase% = 1
			GET #5, tbase%
			FOR j% = 1 TO 5: tv%(j%) = CVI(tv$(j%)): NEXT
			'??
			IF convert$ = "Y" THEN
				GOSUB convert
				tc$(1) = tcx$(1): tc$(2) = tcx$(2): tc$(3) = tcx$(3): tc$(4) = tcx$(4): tc$(5) = tcx$(5)
				tv%(1) = tvx%(1): tv%(2) = tvx%(2): tv%(3) = tvx%(3): tv%(4) = tvx%(4): tv%(5) = tvx%(5)
				END IF
			IF standard$ = "N" THEN
				CALL mls.iyj(a1%, a2%, tv%(1), sunpoz%, smlpoz)
				CALL mls.iyj(b1%, b2%, tv%(2), sunpoz%, smlpoz)
				CALL mls.iyj(c1%, c2%, tv%(3), sunpoz%, smlpoz)
				CALL mls.iyj(d1%, d2%, tv%(4), sunpoz%, smlpoz)
				CALL mls.iyj(e1%, e2%, tv%(5), sunpoz%, smlpoz)
				ELSE
				CALL mls.iyj(a1%, a2%, tv%(1), std.sunpoz%, std.smlpoz)
				CALL mls.iyj(b1%, b2%, tv%(2), std.sunpoz%, std.smlpoz)
				CALL mls.iyj(c1%, c2%, tv%(3), std.sunpoz%, std.smlpoz)
				CALL mls.iyj(d1%, d2%, tv%(4), std.sunpoz%, std.smlpoz)
				CALL mls.iyj(e1%, e2%, tv%(5), std.sunpoz%, std.smlpoz)
				END IF
			st$ = ""
			IF tv%(1) <> 0 THEN CALL fmtoutput(a$, tc$(1), a1%, a2%): st$ = st$ + a$
			IF tv%(2) <> 0 THEN CALL fmtoutput(a$, tc$(2), b1%, b2%): st$ = st$ + a$
			IF tv%(3) <> 0 THEN CALL fmtoutput(a$, tc$(3), c1%, c2%): st$ = st$ + a$
			IF tv%(4) <> 0 THEN CALL fmtoutput(a$, tc$(4), d1%, d2%): st$ = st$ + a$
			IF tv%(5) <> 0 THEN CALL fmtoutput(a$, tc$(5), e1%, e2%): st$ = st$ + a$
			'>>- Debug print area -<<
			IF debug% THEN
				PRINT #99, USING "! \                            \  \      \  \           \###! ## ####"; CHR$(15); tdesc$; intext$; colcard5.bdesc$; cmsort%; CHR$(18); tcno%; ind%
				lin% = lin% + 1
				printed% = printed% + 1
				END IF
			'>>- Real print area -<<
			IF NOT debug% THEN
			PRINT #99, USING "! \                            \  \      \  \           \###!\                                    \ ## ####"; CHR$(15); tdesc$; intext$; colcard5.bdesc$; cmsort%; CHR$(18); st$; tcno%; ind%
				lin% = lin% + 1
				printed% = printed% + 1
				END IF
			END IF
	CALL index("READ ", ind%, qk$, ch%, keyl%)
	LOOP
	IF rec% <> 0 THEN PRINT #99, CHR$(18); CHR$(12)
	CLOSE #2
RETURN
	'//////////////////////////////////////////////////////////////////////
	'//// HEADING
	'//////////////////////////////////////////////////////////////////////
heading:
	IF pag% > 0 THEN PRINT #99, CHR$(12)
	pag% = pag% + 1: lin% = 4
	fetch% = 0
	'/////  print acual heading
	PRINT #99, "#Rtcol03"; TAB(66); "Date:"; date1$
	PRINT #99, TAB(66); "Time:"; TIME$
	PRINT #99, CHR$(14); cc$
	PRINT #99, ""
	PRINT #99, "                    C O L O U R     F O R M U L A T I O N S "
	PRINT #99, TAB(73); "Page:"; pag%
	PRINT #99, USING "!           &!"; CHR$(14); colcard.sname$; CHR$(18)
	PRINT #99, "List by description"
	PRINT #99, STRING$(79, "=")
	PRINT #99, "Colour Name         I/E  Base     Tint Formulation                      CC  No."
	PRINT #99, STRING$(79, "-")
x.heading:
RETURN
'////////////////////////////////////////////////////////////////////////
'/////  C O N V E R T  TO STANDARD FORMULATIONS
'////////////////////////////////////////////////////////////////////////
convert:
	'>> e.g.
	'>> READ ZC%(N%),ZC$(N%),ZCMP%(N%),ZC2%(N%),ZCPCT(N%),PZDOL(N%)
	'>> DATA  01,  "mca  ",  001,  01,  100,  20.00
	tdollars = 0
	FOR n% = 1 TO 5
		FOR i% = 1 TO 200
			IF tc$(n%) = LEFT$(zc$(i%), 2) AND tsuplr% = zcmp%(i%) THEN EXIT FOR
			'PRINT"|"TC$(N%)"|"LEFT$(ZC$(I%),2)"|    "tsuplr%,zcmp%(i%)"    |"I%"|"
			NEXT
		IF i% > 200 THEN
			tcx$(n%) = "    "
			tvx%(n%) = 0
			tdolx(n%) = 0
			ELSE
			tcx$(n%) = zc$(zc2%(i%))
			tvx%(n%) = tv%(n%) * zcpct(i%) / 100
			tdolx(n%) = tv%(1) * pzdol(i%) / 20'**** This line here **** '??
			END IF
		tdollars = tdollars + tdolx(n%)
		NEXT
RETURN

SUB codei (ain%, aout$) STATIC
	sfx$ = MKI$(ain%)
	aout$ = "  "
	MID$(aout$, 1, 1) = MID$(sfx$, 2, 1)
	MID$(aout$, 2, 1) = MID$(sfx$, 1, 1)
	END SUB

SUB decodei (ain$, aout%) STATIC
	sfx$ = "  ": ain1$ = sfx$: LSET ain1$ = ain$
	MID$(sfx$, 1, 1) = MID$(ain1$, 2, 1)
	MID$(sfx$, 2, 1) = MID$(ain1$, 1, 1)
	aout% = CVI(sfx$)
	END SUB

	'////////////////////////////////////////////////////////////////////////
	'/////  Format letter,ounces,mls in printable format
	'////////////////////////////////////////////////////////////////////////
	' A$=Result
	' X$=Tinter code from a single part of the formula. eg. "aa 4y16" X$="aa"
	' O%=Number of ounces
	' M%=Remaining number of mls
SUB fmtoutput (a$, x$, o%, m%) STATIC
	a$ = x$
	IF o% > 1 THEN
		a$ = a$ + MID$(STR$(o%), 2)
		END IF
	IF o% > 0 THEN
		a$ = a$ + "Y"
		END IF
	IF m% > 1 OR (o% = 0 AND m% > 0) THEN
		a$ = a$ + MID$(STR$(m%), 2)
		END IF
	a$ = LEFT$(a$ + "        ", 8)
END SUB

	'////////////////////////////////////////////////////////////////////////
	'/////  C O N V E R T    xYz TO Mls per 10 litres.
	'////////////////////////////////////////////////////////////////////////
SUB iyj.mls (y%, u%, mls%, u.oz%, ml.oz) STATIC
IF u.oz% <> 0 THEN
	mls% = ((y% * u.oz% + u%) * ml.oz / u.oz%) * 2.5
	END IF
END SUB

	'////////////////////////////////////////////////////////////////////////
	'/////  C O N V E R T    Mls per 10 litres TO iYj
	'////////////////////////////////////////////////////////////////////////
SUB mls.iyj (y%, u%, mls%, u.oz%, ml.oz) STATIC
IF ml.oz <> 0 THEN
	ounces = mls% / (2.5 * ml.oz)
	u% = (ounces - INT(ounces)) * u.oz%
	y% = INT(ounces)
	IF u% = u.oz% THEN u% = 0: y% = y% + 1
	END IF
END SUB

