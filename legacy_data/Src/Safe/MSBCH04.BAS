'////////////////////////////////////////////////////////////////////////////
'>>>>> M S B C H 0 4 - Batch reporting.
'////////////////////////////////////////////////////////////////////////////
'.dc - Complete
	'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "msmenu"
	''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	'stdout$ = "CON"

	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\msmisc.INC'
	'$INCLUDE: '\tpmanuf\src\msclass.INC'
	'$INCLUDE: '\tpmanuf\src\msbatch.INC'
	'$INCLUDE: '\tpmanuf\src\msbatchh.INC'
	OPEN stdout$ FOR OUTPUT AS #99

	DIM SHARED form%(999), act(999), thy(999), d$(999), nform%
	DIM SHARED classid(100), CLASS(100), nclass%

	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxhist% = CVI(msmisc.max4$)
	start.mthyy$ = MID$(date1$, 4, 2) + MID$(date1$, 7, 2)
	end.mthyy$ = start.mthyy$
start:
	CALL setup("BATCH REPORTING")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : COLOR 2, 0
	LOCATE 7, 17: PRINT "1.. Print monthly batch listing"
	LOCATE 8, 17: PRINT "2.. Print monthly production by class."
	LOCATE 9, 17: PRINT "3.. Report on individual product"
	LOCATE 11, 17: PRINT "Selete Option..> "
	LOCATE 13, 17: PRINT "From Month.....>"; start.mthyy$
	LOCATE 14, 17: PRINT "To Month.......>"; end.mthyy$
	LOCATE 15, 17: PRINT "Enter from product number..>  "
	LOCATE 16, 17: PRINT "Enter to product number....>  "

cf1:
        LOCATE 11, 33: CALL INPNEW(opt$, 101!, updwn%, "13,59" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN GOTO ENDPGM

cf2:
        LOCATE 13, 33: CALL INPNEW(start.mthyy$, 104!, updwn%, "13,59-60" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN GOTO ENDPGM
	IF updwn% = 60 THEN GOTO cf1

Cf3:
        LOCATE 14, 33: CALL INPNEW(end.mthyy$, 104!, updwn%, "13,59-60" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN GOTO ENDPGM
	IF updwn% = 60 THEN GOTO cf2

	IF opt$ <> "3" THEN GOTO cf99
Cf4:
	LOCATE 15, 45: CALL INPNEW(from.prod$, 103!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO ENDPGM
	IF updwn% = 60 THEN GOTO Cf3
	to.prod$ = from.prod$
cf5:
	LOCATE 16, 45: CALL INPNEW(to.prod$, 103!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO ENDPGM
	IF updwn% = 60 THEN GOTO Cf4

cf99:


	start.rec% = 1
	'start.rec% = 7700
	startyymd$ = "19" + MID$(start.mthyy$, 3, 2) + MID$(start.mthyy$, 1, 2) + "00"
	endyymd$ = "19" + MID$(end.mthyy$, 3, 2) + MID$(end.mthyy$, 1, 2) + "99"
	IF MID$(startyymd$, 3, 2) < "73" THEN MID$(startyymd$, 1, 2) = "20"
	IF MID$(endyymd$, 3, 2) < "73" THEN MID$(endyymd$, 1, 2) = "20"
	from.prod% = VAL(from.prod$)
	to.prod% = VAL(to.prod$)
	IF to.prod$ = "" THEN to.prod% = 32767


	SELECT CASE opt$
	CASE "1": GOSUB BATCH.REP
	CASE "2": GOSUB CLASS.REP
	CASE "3": GOSUB PRODUCT.REP
	CASE ELSE
	END SELECT

	IF stdout$ = "CON" AND updwn% <> 59 THEN SLEEP 10
	GOTO start

ENDPGM:
	CLOSE
	CALL exitpgm(apgm$)
	CHAIN apgm$
	END
'////////////////////////////////////////////////////////////////////////////
'>>>>>  BATCH REPORT - Period by product
'////////////////////////////////////////////////////////////////////////////
BATCH.REP:
	'* First heading
	pag% = 0: lin% = 9999
	rec% = start.rec%
	GET #26, rec%, batchh
	DO WHILE NOT EOF(26)

	'* Decode the file
	bno% = batchh.bno: bfno% = VAL(MID$(batchh.form, 1, 3)): brev% = batchh.revision
	bclass% = batchh.CLASS: byld% = batchh.yld: bayld% = batchh.ayld
	bvisl = 0: bvish = 0: bavis = 0

	ok% = -1
	IF bfno% < 1 OR bfno% > 10000 THEN ok% = 0
	IF batchh.date$ < startyymd$ THEN ok% = 0 '.dc
	IF batchh.date$ > endyymd$ THEN ok% = 0   'dc

	IF bclass% < 1 OR bclass% > 99 THEN bclass% = 1
	GET #29, bclass%, msclass

	u$ = "pse": IF btype$ = "S" OR btype$ = "s" THEN u$ = "sec"
	'* Convert brev to string form
	r1$ = STR$(brev%): r% = LEN(r1$): r1$ = RIGHT$(r1$, r% - 1): r1$ = RIGHT$("00" + r1$, 2)
	'* Convert bfno to string form
	r2$ = STR$(bfno%): r% = LEN(r2$): r2$ = RIGHT$(r2$, r% - 1): r2$ = RIGHT$("000" + r2$, 3)
	'* Calculate % diff between expected and actual
	percnt = (bayld% - byld%) / (byld% + .000001)
	percnt = percnt * 100

	IF ok% THEN
		lin% = lin% + 1
		IF lin% > 50 THEN GOSUB HEADING
		PRINT #99, USING "#### \ \!-\\ \                       \ \     \\      \ ### \ \ #### #### ###.##"; bno%; r2$; MID$(batchh.form$, 4, 1); r1$; batchh.name$; msclass.cldesc$; FNDYY$(batchh.date$); bavis; u$; byld%; bayld%; percnt
		END IF


	IF rec% MOD 100 = 0 THEN
		LOCATE 22, 17: PRINT USING "Record ##### Mth &"; rec%; FNDYY$(batchh.date$)
		x$ = INKEY$
		IF x$ = CHR$(0) + CHR$(59) THEN updwn% = 59: EXIT DO
		END IF

	GET #26, , batchh: rec% = rec% + 1
	LOOP


	 IF pag > 0 THEN PRINT #99, CHR$(12)
RETURN

'/////////////////////////////////////////////////////////////////////////////
'>>>>>  H E A D I N G
'/////////////////////////////////////////////////////////////////////////////
HEADING:
IF stdout$ = "CON" THEN CLS
	 pag% = pag% + 1: lin% = 0
	 IF pag% > 1 THEN PRINT #99, CHR$(12)
	 PRINT #99,
	 PRINT #99, CHR$(14); cc$
	 PRINT #99, "msbch02"; TAB(66); "Date: "; date1$
	 PRINT #99, TAB(66); "Time: "; TIME$
	 PRINT #99,
	 PRINT #99, TAB(15); "M O N T H L Y   B A T C H  L I S T I N G  : "; start.mthyy$
	 PRINT #99,
	 PRINT #99, TAB(66); "page: "; pag%
	 PRINT #99, STRING$(79, "=")
	 PRINT #99, "Batch                                                           Exp  Act   %  "
	 PRINT #99, " No. Formula  Dsecription               Class   Update  Viscos. Yld  Yld  Diff"
	 PRINT #99, STRING$(79, "-")
RETURN

'////////////////////////////////////////////////////////////////////////////
'>>>>>   C L A S S   P R O C E S S I N G
'////////////////////////////////////////////////////////////////////////////
CLASS.REP:
	FOR i% = 1 TO 100: classid(i%) = 0: CLASS(i%) = 0: NEXT: nclass% = 0

	rec% = start.rec%
	GET #26, rec%, batchh
	DO WHILE NOT EOF(26)

	'* Decode the file
	bno% = batchh.bno: bfno% = VAL(MID$(batchh.form, 1, 3)): brev% = batchh.revision
	bclass% = batchh.CLASS: byld% = batchh.yld: bayld% = batchh.ayld
	bvisl = 0: bvish = 0: bavis = 0

	ok% = -1
	IF bfno% < 1 OR bfno% > 10000 THEN ok% = 0
	IF batchh.date$ < startyymd$ THEN ok% = 0 '.dc
	IF batchh.date$ > endyymd$ THEN ok% = 0   'dc


	IF ok% THEN
		bclass = batchh.CLASS
		found% = 0
		FOR i% = 1 TO nclass%
			IF classid(i%) = bclass THEN found% = -1: EXIT FOR
			NEXT
		IF NOT found% THEN nclass% = nclass% + 1: i% = nclass%
		classid(i%) = bclass
		CLASS(i%) = CLASS(i%) + 0
		END IF


	IF rec% MOD 100 = 0 THEN
		LOCATE 22, 17: PRINT USING "Record ##### Mth &"; rec%; FNDYY$(batchh.date$)
		x$ = INKEY$
		IF x$ = CHR$(0) + CHR$(59) THEN updwn% = 59: EXIT DO
		END IF

	GET #26, , batchh: rec% = rec% + 1
	LOOP


	 '* Now print it
	 pag% = 0: lin% = 9999
	 FOR i% = 1 TO nclass%
		IF lin% > 45 THEN GOSUB CLASSHEADING

		PRINT #99, USING "####   #####.##    #####.###"; i%; classid(i%); CLASS(i%)
		NEXT
	IF pag% > 0 THEN PRINT #99, CHR$(12)
RETURN
'/////////////////////////////////////////////////////////////////////////////
'>>>  Class heading
'/////////////////////////////////////////////////////////////////////////////
CLASSHEADING:
	IF stdout$ = "CON" THEN CLS
	pag% = pag% + 1: lin% = 0
	IF pag% > 1 THEN PRINT #99, CHR$(12)
	PRINT #99, : PRINT #99, ; CHR$(14); cc$
	PRINT #99, "#msbch02"; TAB(66); "Date: "; date1$
	PRINT #99, TAB(67); "Time: "; TIME$
	PRINT #99,
	PRINT #99, TAB(5); "M O N T H L Y   P R O D U C T I O N   B Y   C L A S S : "; start.mthyy$
	PRINT #99,
	PRINT #99, TAB(66); "page: "; pag%
	PRINT #99, STRING$(79, "=")
	PRINT #99, "  No  CLASS                      LITRES"
	PRINT #99, STRING$(79, "-")
RETURN
'/////////////////////////////////////////////////////////////////////////////
'>>>>>  R E P O R T -  Individual product
'/////////////////////////////////////////////////////////////////////////////
PRODUCT.REP:
	FOR i% = 1 TO 999: form%(i%) = 0: act(i%) = 0: thy(i%) = 0: d$(i%) = "": NEXT:
	nform% = 0

	rec% = start.rec%
	GET #26, rec%, batchh
	DO WHILE NOT EOF(26)

	'* Decode the file
	bno% = batchh.bno: bfno% = VAL(MID$(batchh.form, 1, 3)): brev% = batchh.revision
	bclass% = batchh.CLASS: byld% = batchh.yld: bayld% = batchh.ayld
	bvisl = 0: bvish = 0: bavis = 0

	ok% = -1
	IF bfno% < 1 OR bfno% > 10000 THEN ok% = 0
	IF bfno% < from.prod% THEN ok% = 0
	IF bfno% > to.prod% THEN ok% = 0
	IF batchh.date$ < startyymd$ THEN ok% = 0 '.dc
	IF batchh.date$ > endyymd$ THEN ok% = 0   'dc


	IF ok% THEN
		found% = 0
		FOR i% = 1 TO nform%
			IF form%(i%) = bfno% THEN found% = -1: EXIT FOR
			NEXT
		IF NOT found% THEN nform% = nform% + 1: i% = nform%
		form%(i%) = bfno%
		act(i%) = act(i%) + bayld%
		thy(i%) = thy(i%) + byld%
		d$(i%) = batchh.name$
		END IF


	IF rec% MOD 100 = 0 THEN
		LOCATE 22, 17: PRINT USING "Record ##### Mth &"; rec%; FNDYY$(batchh.date$)
		x$ = INKEY$
		IF x$ = CHR$(0) + CHR$(59) THEN updwn% = 59: EXIT DO
		END IF

	GET #26, , batchh: rec% = rec% + 1
	LOOP


	 '* Now print it
	 pag% = 0: lin% = 9999
	 FOR i% = 1 TO nform%
		percnt = (thy(i%) - act(i%)) / (thy(i%) + .000001)
		percnt = percnt * 100
		lin% = lin% + 1
		IF lin% > 50 THEN GOSUB PRODHEADING
		PRINT #99, USING "###  \                        \   ###,###     ###,###    ##.##"; form%(i%); d$(i%); act(i%); thy(i%); percnt
		tot.byld% = tot.byld% + thy(i%)
		tot.bayld% = tot.bayld% + act(i%)
		NEXT

	IF pag% > 0 THEN PRINT #99, CHR$(12)

RETURN

'/////////////////////////////////////////////////////////////////////////////
'>>>>>  H E A D I N G
'/////////////////////////////////////////////////////////////////////////////
PRODHEADING:
	IF stdout$ = "CON" THEN CLS
	pag% = pag% + 1: lin% = 0
	IF pag% > 1 THEN PRINT #99, CHR$(12)

	 PRINT #99, : PRINT #99, ; CHR$(14); cc$
	 PRINT #99, "#msrep04"; TAB(66); "Date: "; date1$
	 PRINT #99, TAB(66); "Time: "; TIME$
	 PRINT #99, TAB(12); USING "REPORT FOR PRODUCT from  ###  to ### "; from.prod%; to.prod%
	 PRINT #99, TAB(11); "-------------------------------------------"
	 PRINT #99, TAB(66); "page: "; pag%
	 PRINT #99, STRING$(79, "=")
	 PRINT #99, "Batch                                                           Exp  Act   %  "
	 PRINT #99, USING "No.  Formula  Description         Exp.Yld     Act.Yld   % Diff  !"; ""
	 PRINT #99, STRING$(79, "-")
RETURN
