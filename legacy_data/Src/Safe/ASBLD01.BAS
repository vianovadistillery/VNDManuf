DECLARE SUB fixbadrecords (ok%)
DECLARE SUB rebuild (ok%)
DECLARE SUB cleanup (ok%)
DECLARE SUB findorders (ok%)
'////////////////////////////////////////////////////////////////////////
'////    Rebuld the order files
'////////////////////////////////////////////////////////////////////////
	CONST maxord% = 1000
	CONST maxitem% = 32000
	CONST maxdet% = 11000
	CONST top.lin% = 6
	CONST btm.lin% = 18
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	pgm$ = "ASBLD02"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	OPEN "ordhed.new" FOR OUTPUT AS #58 LEN = 128
	OPEN "orddet.new" FOR OUTPUT AS #59 LEN = 32
	CLOSE

	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\ordhed.inc'
	'$INCLUDE: '\tpmanuf\src\orddet.inc'
	'$INCLUDE: '\tpmanuf\src\acstk.inc'

	OPEN "ordhed.new" FOR RANDOM AS #58 LEN = 256
	OPEN "orddet.new" FOR RANDOM AS #59 LEN = 32
	DIM SHARED orders%(maxord%)
start:
	CALL setup("CHECKING ORDER FILE")
	btm$ = " F1-Return.  "
	hed$ = "Head/ord.  Order  Seq. RRN   Item Desc...................   Price    On Order"
	COLOR 8, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
	COLOR 6, 0: LOCATE 3, 2: PRINT hed$: COLOR 2, 0
	CALL findorders(ok%)
	CALL fixbadrecords(ok%)
	CALL rebuild(ok%)
	CLOSE
	CALL exitpgm(pgm$)
	CHAIN pgm$

SUB findorders (ok%)
'/////////////////////////////////////////////////////
'>>>>>  FIND ORDERS WITH THE SAME CUSTOMER NUMBER
'/////////////////////////////////////////////////////
findorders:
	FOR I% = 1 TO maxord%
		orders%(I%) = 0
	NEXT
	hord% = 1
	GET #48, hord%, ordhed
	DO WHILE NOT EOF(48)
		IF CVI(ordhed.hord$) = hord% THEN
			orders%(hord%) = hord%
		END IF
		GET #48, , ordhed: hord% = hord% + 1
	LOOP

END SUB

SUB fixbadrecords (ok%)
'/////////////////////////////////////////////////////
'>>>>>  CLEAN UP DETAIL RECORDS
'/////////////////////////////////////////////////////
cleanup:
	tot.cnt% = 0
	err.cnt% = 0
	REC% = 1
	GET #49, REC%, orddet
	LOCATE , 2
	PRINT USING "  ##,###   ####   ####"; orddet.dord%; orddet.dseq%; orddet.drrn%
	REC% = 2
	GET #49, REC%, orddet
	DO WHILE NOT EOF(49)
		IF orddet.dord% = -1 THEN orddet.dord% = 0
		dord% = orddet.dord%
		IF orders%(dord%) <> dord% AND dord% <> 0 THEN
		IF CVI(orddet.dordq$) > 0 THEN
			ano% = CVI(orddet.ditem$)
			IF ano% < 1 OR ano% > maxitem% THEN ano% = 1
			GET #3, ano%, acstk
			err.cnt% = err.cnt% + 1
			yloc% = err.cnt% MOD 17
			LOCATE yloc% + 4, 2
			PRINT USING "    ####   ####   ## ##,###  #### \                      \ $$####.##    ###"; orders%(dord%); orddet.dord%; orddet.dseq%; orddet.drrn%; CVI(orddet.ditem$); ADESC$; CVS(orddet.dprice$); CVI(orddet.dordq$)
			END IF
			IF orddet.dord% <> 0 OR orddet.drrn% <> 0 THEN
				LSET dord$ = MKI$(0)
				LSET drrn$ = MKI$(0)
				PUT #49, REC%
				END IF
			END IF
		tot.cnt% = tot.cnt% + 1
		GET #49, , orddet: REC% = REC% + 1
		LOOP
		LOCATE 21, 2: COLOR 14, 0
		PRINT USING "Total record ##,### Records in error ##,###"; tot.cnt%; err.cnt%
		COLOR 2, 0
	'        x$ = INPUT$(1)

END SUB

SUB rebuild (ok%)
'/////////////////////////////////////////////////////
'>>>>>  REBUILD THE DETAIL FILE
'/////////////////////////////////////////////////////
rebuild:
	'The first record is a header.
	'DRRN points to the start of the nul linked list. (deleted records)
	'DSEQ points to the end of the nul linked list.
	orddet.dord% = 32767
	orddet.dseq% = 0
	orddet.drrn% = 0
	LSET orddet.ditem$ = MKI$(0)
	LSET orddet.dprice$ = MKS$(0)
	LSET orddet.dordq$ = MKI$(0)
	LSET orddet.dinvq$ = MKI$(0)
	LSET orddet.dtax$ = MKS$(0)
	LSET orddet.dlinvq$ = MKI$(0)
	nxt.rec% = 1
	PUT #59, nxt.rec%, orddet
	nxt.rec% = nxt.rec% + 1
	lin% = top.lin% - 1
	hord% = 1
	GET #48, hord%, ordhed
	DO WHILE NOT EOF(48)
		IF CVI(ordhed.hord$) = hord% THEN
			drrn% = CVI(ordhed.hrrn$)
			IF drrn% > 0 AND drrn% < maxdet% THEN
				GET #49, drrn%, orddet
				LOCATE 4, 2: PRINT USING "Rebuilding order ##### Search|&|"; hord%; ordhed.hsup$
				LOCATE 5, 2: PRINT "rcd.  Order    Seq    RRN    ITEM#"
				lin% = top.lin% - 1
				ELSE
				drrn% = 0
				END IF
		first.det% = 0
		seq% = 0
		DO WHILE drrn% <> 0
				IF drrn% = orddet.drrn% THEN orddet.drrn% = 0 '??
				drrn% = orddet.drrn%

				IF orddet.dord% <> hord% THEN : errcnt% = errcnt% + 1: SOUND 50, 1
				orddet.dord% = hord%
				seq% = seq% + 1
				orddet.dseq% = seq%
				IF orddet.drrn% = 0 THEN
					orddet.drrn% = 0
					ELSE
					orddet.drrn% = nxt.rec% + 1
					END IF
				IF first.det% = 0 THEN first.det% = nxt.rec%
				lin% = lin% + 1: IF lin% > btm.lin% THEN lin% = top.lin%
				LOCATE lin%, 2
				PRINT USING "###   ##,### ##,### ##,###  ##,###"; nxt.rec%; orddet.dord%; orddet.dseq%; orddet.drrn%; CVI(orddet.ditem$)
				PUT #59, nxt.rec%, orddet
				nxt.rec% = nxt.rec% + 1
				IF drrn% > 0 AND drrn% < maxdet% THEN
					GET #49, drrn%, orddet
					END IF
			LOOP
		'>> Write new header <<
		GET #48, hord%, ordhed
		LSET ordhed.hrrn$ = MKI$(first.det%)
		PUT #58, hord%, ordhed
		END IF
		FOR I% = lin% + 1 TO btm.lin%
			LOCATE I%, 2
			PRINT SPACE$(78)
			NEXT
		x$ = INKEY$
		'$ = INPUT$(1)
		GET #48, , ordhed: hord% = hord% + 1
		LOOP
LOCATE 22, 2: COLOR 14: PRINT USING "##,### errors found"; errcnt%: COLOR 2
SLEEP 1

END SUB

