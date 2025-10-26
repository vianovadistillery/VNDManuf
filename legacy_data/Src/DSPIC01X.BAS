DECLARE SUB qsort (r$(), k%(), n%)
   '>>>>>>>>>>>>>>>>> INDEX OVER pickup address FILE <<<<<<<<<<<<<<<<<<<<
'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
	apgm$ = "DSPIC01"
''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	OPEN "pickupx.who" FOR RANDOM AS #51 LEN = 7
	CLOSE
	KILL "pickupx.who"
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\pickup.INC'
	'$INCLUDE: '\tpmanuf\src\pickupX.INC'
	max% = 2500
	DIM k%(max%), r$(max%)
	CALL setup("INDEX CREATE FOR pickup FILE ")
	'*
	LOCATE 8, 20: PRINT "Index file create commencing....": LOCATE 1, 1
	FOR i% = 1 TO max%: k%(i%) = 0: r$(i%) = "~~~~": NEXT'* Set array to *hival
	'*
	LOCATE 10, 20: PRINT "Reading pickup file.....": LOCATE 1, 1
	rec% = 1: n% = 0
	GET #50, rec%, pickup
	DO WHILE NOT EOF(50)
		IF rec% = CVI(pickup.pno$) THEN
			n% = n% + 1
			k%(n%) = CVI(pickup.pno$)
			r$(n%) = LEFT$(pickup.pname1$, 14)
			END IF
		GET #50, , pickup: rec% = rec% + 1
		LOOP
	'*
	LOCATE 12, 20: PRINT "Sorting records now.......": LOCATE 1, 1
	CALL qsort(r$(), k%(), n%)
	LOCATE 14, 20: PRINT "Writing new file..........": LOCATE 1, 1
	FOR i% = 1 TO n%
		LSET pickupx.pxcde$ = r$(i%)
		LSET pickupx.pxrrn$ = MKI$(k%(i%))
		PUT #51, i%, pickupx
		LOCATE 16, 20: PRINT "Record...................."; i%: LOCATE 1, 1
		LOCATE 17, 20: PRINT "Code."; pickupx.pxcde$, "RRN."; CVI(pickupx.pxrrn$)
		NEXT
	CLOSE
	CALL exitpgm(apgm$)
	CHAIN apgm$
	END

SUB qsort (r$(), k%(), n%) STATIC
'>>>>> Quick-sort algorithmn
	DIM h%(15)
	ii% = 0
	h%(1) = 1
	FOR i% = 2 TO 15
	h%(i%) = 3 * h%(i% - 1) + 1: IF h%(i%) >= n% THEN 750
	NEXT i%
	n% = -1
	GOTO x.qsort
750 t% = i% - 2: IF t% < 1 THEN t% = 1
	FOR s% = t% TO 1 STEP -1
	h% = h%(s%)
	FOR j% = h% + 1 TO n%
	   r$ = r$(j%): k% = k%(j%)
	   FOR i% = j% - h% TO 1 STEP -h%
	   IF r$ >= r$(i%) THEN ii% = i%: i% = 0: GOTO 830
	   k%(i% + h%) = k%(i%): r$(i% + h%) = r$(i%)
830      NEXT'* I
	   IF ii% > 0 THEN i% = ii%: ii% = 0
	   k%(i% + h%) = k%: r$(i% + h%) = r$
	 NEXT'* J
	 NEXT'* S
x.qsort:
END SUB

