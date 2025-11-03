'>>>>>>>>>>>>>>>>>> RTCOL05 - Update all colors
'.dc - Complete
	'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\colsyst.inc'
	apgm$ = "ACMENU"
	DIM TC$(5), tv%(5), tv$(5)
	'$INCLUDE: '\tpmanuf\src\colcht.inc'
	yorn$ = "Y"
start:
	btm$ = "                             F1-Exit."
	CALL setup("C O L O R   U P D A T E ")
	COLOR 8, 3: LOCATE 25, 5: PRINT btm$; : COLOR 2, 0
	LOCATE 5, 15: PRINT "This program rebuilds the color formulation file in"
	LOCATE 6, 15: PRINT "the ratio's of the Mls/Oz as listed in COLSYST.INC"
	DO
		LOCATE 8, 15: PRINT "Continue...> "; CHR$(FNH);
		CALL inpnew(yorn$, 101!, updwn%, "13,59" + ALT$): GOSUB ALT
				yorn$ = UCASE$(yorn$)
		IF updwn% = 59 THEN yorn$ = "N"
		LOOP UNTIL yorn$ = "Y" OR yorn$ = "N"
	IF yorn$ = "Y" THEN GOSUB do.upd: yorn$ = "N": GOTO start
	CLOSE
	CALL EXITPGM(apgm$)
	CHAIN apgm$
END
'////////////////////////////////////////////////////////////////////////////
'>>>>> DO update
'////////////////////////////////////////////////////////////////////////////
do.upd:
	rec% = 1
	GET #12, 1
	DO WHILE NOT EOF(12)
		tsuplr% = CVI(tsuplr$)
		FOR i% = 1 TO 5
			tv%(i%) = CVI(tv$(i%))
			NEXT
		FOR n% = 1 TO 20
			ok% = 0
			IF sno%(n%) = tsuplr% AND tsuplr% <> 0 THEN
				awas = smwas(n%)
				ais = smlpoz(n%)
				diff = awas - ais
				ok% = 1
				EXIT FOR
				END IF
			NEXT
		IF ok% = 1 THEN
			LOCATE 10, 10
			PRINT USING "#### & ###.## ###.##   ###.##"; rec%; tdesc$; awas; ais; diff
			LOCATE 12, 12
			FOR i% = 1 TO 5
				PRINT USING "#,### "; tv%(i%);
				NEXT
			PRINT
			FOR i% = 1 TO 5
				a! = tv%(i%)
				a! = a! / awas * ais
				tv%(i%) = a!
				LSET tv$(i%) = MKI$(a!)
				PUT #12, rec%
				NEXT
			PRINT
			LOCATE 14, 12
			FOR i% = 1 TO 5
				PRINT USING "#,### "; CVI(tv$(i%));
				NEXT
			PRINT
			END IF
		GET #12: rec% = rec% + 1
		LOOP
	CLOSE
END
