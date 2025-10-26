'>>>>> M S B C H 0 5 - Required raw materials
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
'.dc - Complete
	pgm$ = "msbch02"

	CONST maxformseq& = 38
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\msrmat.inc'
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	'$INCLUDE: '\tpmanuf\src\msbatch.inc'
	'$INCLUDE: '\tpmanuf\src\forhed.inc'
	'$INCLUDE: '\tpmanuf\src\fordet.inc'
	'$INCLUDE: '\tpmanuf\src\tnthed.inc'
	'$INCLUDE: '\tpmanuf\src\tntdet.inc'
	'stdout$ = "shit.sht"

	CALL setup("REQUIRED RAW MATERIAL REPORT")
	COLOR 2
	GET #36, 1, msmisc
	maxrmat% = CVI(msmisc.max3$)
	DIM form$(700), rmqty!(maxrmat%)

	'>>>>>       Select unfinised batches
	LOCATE 10, 20: PRINT "Selecting unfinished batches...."; CHR$(FNE)
	n% = 0

	rec% = 1
	GET #57, rec%, batch
	DO WHILE NOT EOF(57)
	IF batch.ayld! = 0 THEN
		n% = n% + 1
		form$(n%) = batch.form$
		END IF
	GET #57, , batch: rec% = rec% + 1
	LOOP
	
	'<<<<<<<<- Process formulas
	LOCATE 10, 20: PRINT "Searching details of formula's.."
	FOR formidx% = 1 TO n%

		found% = 0
		rec% = 1
		GET #64, rec%, tnthed
		DO WHILE NOT EOF(64)
		IF tnthed.tnta$ = form$(formidx%) THEN found% = -1: EXIT DO
		GET #64, , tnthed: rec% = rec% + 1
		LOOP

	IF found% THEN
		LOCATE 11, 20: PRINT USING "Found...\   \&"; tnthed.tnta$; tnthed.desc$
		rec& = rec%
	 
		startrec& = rec& * maxformseq& - maxformseq& + 1
		FOR drec& = startrec& TO startrec& + maxformseq&
			GET #65, drec&, tntdet
			IF tntdet.qty! > 0 THEN rmqty!(tntdet.rmat%) = rmqty!(tntdet.rmat%) + tntdet.qty!
			NEXT

		END IF

	NEXT



	LOCATE 13, 20: PRINT "Printing report..."
	'>>>>> Print report
	OPEN stdout$ FOR OUTPUT AS #99
	lin% = 9999: pag% = 0
	FOR i% = 1 TO maxrmat%
	IF rmqty!(i%) > 0 THEN

		IF lin% > 45 THEN GOSUB HEADING
		GET #38, i%, msrmat
		ok% = -1
		IF msrmat.PurUnit$ = "EA" THEN ok% = 0
		IF msrmat.PurUnit$ = "EQ" THEN ok% = 0
		IF msrmat.PurUnit$ = "HR" THEN ok% = 0
		IF msrmat.PurUnit$ = "MN" THEN ok% = 0
		IF ok% THEN
			PRINT #99, USING "                       ####   &     ##### &"; i%; msrmat.desc1$; rmqty!(i%); msrmat.PurUnit$
			lin% = lin% + 1
			END IF

	END IF
	NEXT

	PRINT #99, CHR$(12)
	CLOSE

'   SHELL "type shit.sht"
'   END
	CALL exitpgm(pgm$)
	CHAIN pgm$
	END



HEADING:
	pag% = pag% + 1: lin% = 0
	IF pag% > 1 THEN PRINT #99, CHR$(12)
	PRINT #99, : PRINT #99, ; CHR$(14); cc$
	PRINT #99, "msbch05"; TAB(67); "Date: "; DATE1$
	PRINT #99, TAB(67); "Time: "; TIME$
	PRINT #99, ""
	PRINT #99, TAB(15); "R E Q U I R E D   M A T E R I A L S   L I S T I N G"
	PRINT #99, TAB(72); "page: "; pag%
	PRINT #99, STRING$(79, "=")
	PRINT #99, TAB(25); "NO.   DESCRIPTION        QUANTITY."
	PRINT #99, STRING$(79, "-")
RETURN

