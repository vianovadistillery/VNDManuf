'///////////////////////////////////////////////////////////////////////
'>>>>> EXAMINE ORDER DETAIL FILES
'///////////////////////////////////////////////////////////////////////
	'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
	apgm$ = "DSINV01D"
	CONST pag.len% = 18
	file49$ = "ORDDET.ACF"
start:
	CLOSE
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\orddet.INC'
	CLOSE
	OPEN file49$ FOR RANDOM SHARED AS #49 LEN = 32

	CALL setup("LOOK AT ORDER DETAIL FILE  " + file49$)
	LOCATE 3, 2: COLOR 6
	PRINT "Count  Order#    Seq   RRN      Item#    Ord/qty"
	COLOR 2
	LOCATE 25, 1: COLOR 0, 3
	PRINT "F1-Return     F4-Copy ord*.new to ord*.acf    F5-Rebuild file    F10-Swap files";
	LOCATE 1, 1
	COLOR 2, 0
	y0% = 4
	rec.in.file% = LOF(49) / 32
	start.rec% = 1
	GET #49, 1, orddet
	LOCATE 2, 2: COLOR 7
	PRINT USING "µNull list,  First ##,###   |Last ##,###   |Records on file ##,###Æ"; orddet.drrn%; orddet.dseq%; rec.in.file%
	updwn% = 0
top.of.loop:
	IF start.rec% < 2 THEN start.rec% = 2
	IF start.rec% > rec.in.file% THEN start.rec% = 2
	rec% = start.rec%
	GET #49, rec%, orddet
	LOCATE y0%, 2: COLOR 2, 0
	lin% = 0
	DO WHILE NOT EOF(49) AND lin% < pag.len%
		IF lin% >= pag.len% THEN EXIT DO
		dordq% = CVI(orddet.dordq$)
		ditem% = CVI(orddet.ditem$)
		LOCATE , 2
		PRINT USING "####> |######|..|##|##,###|    ##,###|    ##,###"; rec%; orddet.dord%; orddet.dseq%; orddet.drrn%; ditem%; dordq%
		IF rec% = orddet.drrn% THEN LOCATE y0% + lin%, 2: COLOR 10, 0: PRINT "#####": COLOR 2, 0
		lin% = lin% + 1
		IF lin% = 1 THEN start.rec% = rec%
		GET #49, , orddet: rec% = rec% + 1
		LOOP
	'>-----------------------------------------------------------------------
	IF EOF(49) THEN
		FOR i% = lin% + 1 TO pag.len%: LOCATE , 2: PRINT SPACE$(78): NEXT
		END IF
	'>--
	LOCATE y0%, 2
	CALL inpnew(a$, 0!, updwn%, "13,59,62-63,68,73,81")
	SELECT CASE updwn%
	CASE 13: start.rec% = 1: GOTO top.of.loop
	CASE 59: GOTO endpgm
	CASE 62
		CLOSE
		LOCATE 5, 2
		SHELL "copy ord*.new ORD*.ACF"
		GOTO start
	CASE 63 'Rebuild detail file
		CLOSE
		bpgm$ = "asbld01"
		CALL exitpgm(bpgm$)
		CHAIN bpgm$
		GOTO endpgm
	CASE 68 'Swap files
		IF file49$ = "ORDDET.ACF" THEN
		   file49$ = "ORDDET.NEW"
		   ELSE
		   file49$ = "ORDDET.ACF"
		   END IF
		GOTO start
	CASE 73 'page up
		start.rec% = start.rec% - pag.len%
		GOTO top.of.loop
	CASE 81 'page down
		start.rec% = start.rec% + pag.len%
		IF start.rec% > rec.in.file% THEN start.rec% = start.rec% - pag.len%
		GOTO top.of.loop
	CASE ELSE
		GOTO top.of.loop
	END SELECT
endpgm:
	CLOSE
	CALL exitpgm(apgm$)
	CHAIN apgm$

