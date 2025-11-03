	 'M S U P D 0 9 - Set R/M activity flag.
	 '$INCLUDE: '\tpmanuf\src\pgmhead.INC'
'.dc - Complete
	apgm$ = "MSREP02"
''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	DIM r%(10000)
	CLOSE
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\msrmat.INC'
	'$INCLUDE: '\tpmanuf\src\tntdet.INC'
	'$INCLUDE: '\tpmanuf\src\fordet.INC'
	'$INCLUDE: '\tpmanuf\src\msmisc.INC'
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	doit$ = "Y": skip% = -1
	'* Set out screen
start:
	CALL setup("UPDATE ACTIVITY FLAG")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : COLOR 2, 0
	LOCATE 4, 25: PRINT "Checking Activity"

270
	IF NOT skip% THEN
		skip% = 0
		LOCATE 5, 25: PRINT "Continue.....(Y/N)..> "; CHR$(FNH);
		CALL inpnew(doit$, 101!, updwn%, "13,59" + ALT$): GOSUB ALT
		doit$ = UCASE$(doit$)
		IF updwn% = 59 THEN GOTO endpgm
	END IF
	IF doit$ = "N" THEN GOTO endpgm
	IF doit$ = "Y" THEN GOSUB do.update: doit$ = "N": GOTO endpgm
	GOTO start
endpgm:
CLOSE
CALL EXITPGM(apgm$): CHAIN apgm$
'////////////////////////////////////////////////////////////////////////////
'>>>> do UPDATE
'////////////////////////////////////////////////////////////////////////////
do.update:
	'>-Check formulations
	i% = 0: j% = 0
	rec65& = 1
	GET #65, rec65&, tntdet
	fk% = tntdet.rmat%
	DO WHILE NOT EOF(65)
		fk% = tntdet.rmat%
		IF fk% > 0 AND fk% < 10001 AND tntdet.tnt& = rec65& AND tntdet.cmt% >= 0 AND tntdet.cmt% <= 999 THEN
		r%(fk%) = r%(fk%) + 1
		END IF

		i& = i& + 1: j& = j& + 1
		IF j& = 1000 THEN LOCATE 10, 20: PRINT "Tested"; i&; "Records. (Formula)": j& = 0
		GET #65, , tntdet: rec65& = rec65& + 1

	LOOP

	'>-Check tints
	i& = 0: j& = 0
	rec55& = 1
	GET #55, rec55&, tntdet
	fk% = tntdet.rmat%
	DO WHILE NOT EOF(55)
		fk% = tntdet.rmat%
		IF fk% > 0 AND fk% < 10001 AND tntdet.tnt& = rec55& AND tntdet.cmt% >= 0 AND tntdet.cmt% <= 999 THEN
		r%(fk%) = r%(fk%) + 1
		END IF

		i& = i& + 1: j& = j& + 1
		IF j& = 1000 THEN LOCATE 11, 20: PRINT "Tested"; i&; "Records. (tints)": j& = 0
		GET #55, , tntdet: rec55& = rec55& + 1
	LOOP


	'-> Check all the other sets
	DIM c$(10)
	c$(1) = "BRIdet.asf"
	c$(2) = "hendet.asf"
	c$(3) = "hicdet.asf"
	c$(4) = "JOTdet.asf"
	c$(5) = "reddet.asf"
	c$(6) = "SICdet.asf"
	c$(7) = "WAGdet.asf"
	c$(8) = "WATdet.asf"

	FOR c% = 1 TO 8
		file$ = c$(c%)
		a$ = DIR$(file$)
		IF a$ > "" AND file$ > "" THEN
			LOCATE 11 + c%, 20: PRINT file$
			OPEN file$ FOR RANDOM SHARED AS #165 LEN = 32

			i& = 0: j& = 0
			GET #165, 1, tntdet
			fk% = tntdet.rmat%
			DO WHILE NOT EOF(165)
				fk% = tntdet.rmat%
				IF fk% > 0 AND fk% < 10001 AND tntdet.tnt& > 0 AND tntdet.cmt% >= 0 AND tntdet.cmt% <= 999 THEN r%(fk%) = r%(fk%) + 1
				i& = i& + 1: j& = j& + 1
				IF j& = 1000 THEN LOCATE 11 + c%, 20: PRINT "Tested"; i&; "Records. (" + c$(c%) + ")": j& = 0
				GET #165, , tntdet
				LOOP

			CLOSE #165
		END IF
	NEXT


	LOCATE 21, 20: PRINT "All formula details tested."
	'>>>>>>>- Update file -<<<<<<<<
	FOR i% = 1 TO maxrmat%
	IF i% MOD 100 = 0 THEN
		LOCATE 22, 20: PRINT USING "Updating Raw material #,###"; i%;
	END IF
	GET #38, i%, msrmat
	'- Active,Suspended or Redundant
	IF msrmat.active$ <> "M" THEN
		LSET msrmat.active$ = "S"
		IF r%(i%) > 0 THEN LSET msrmat.active$ = "A"
		PUT #38, i%, msrmat
		END IF
	NEXT

	x$ = INPUT$(1)

	'* End of update
RETURN
