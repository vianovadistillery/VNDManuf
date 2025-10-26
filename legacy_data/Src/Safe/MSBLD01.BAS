DECLARE SUB ReAssingOrdToDet (hord%)
DECLARE SUB linkedl (rrn%(), n%, firstrec%, ord%, chd%)
'** Reassign Order Numbers to linked list order detail file.

'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "DSREP03"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CONST maxlines% = 45
	typefields% = -1
	DIM SHARED rrn%(maxlines%)

	'$INCLUDE: '\tpmanuf\src\whof.inc'
	'$INCLUDE: '\tpmanuf\src\cusx.inc'
	'$INCLUDE: '\tpmanuf\src\supx.inc'
	'$INCLUDE: '\tpmanuf\src\cus.inc'
	'$INCLUDE: '\tpmanuf\src\ACSTK.INC'
	'$INCLUDE: '\tpmanuf\src\ordhed.inc'
	'$INCLUDE: '\tpmanuf\src\orddet.inc'
	'$INCLUDE: '\tpmanuf\src\ordprt.inc'

	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	'$INCLUDE: '\tpmanuf\src\pickup.INC'
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxacc% = CVI(msmisc.max5$): maxtypes% = CVI(msmisc.max6$): maxcus% = CVI(msmisc.max7$)
	maxord% = 999

start:
	CALL setup("ORDER DETAIL REBUILD")
	btm$ = " Wait..."
	COLOR 8, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0

	dnext% = 1
	GET #49, dnext%, orddet
	DO WHILE NOT EOF(49)
		orddet.dord% = 0
		PUT #49, dnext%, orddet
	GET #49, , orddet: dnext% = dnext% + 1
	LOOP


	FOR hord% = 1 TO maxord%
		CALL ReAssingOrdToDet(hord%)
	NEXT

	CLOSE
	CALL EXITPGM(apgm$)
	CHAIN apgm$
	END

SUB linkedl (rrn%(), n%, firstrec%, ord%, chd%) STATIC
'$INCLUDE: '\tpmanuf\src\linkedl.bi'
END SUB

SUB ReAssingOrdToDet (hord%)
	GET #48, hord%, ordhed
	hinvq = CVS(ordhed.hinvq$)

	nn% = -1: firstrec% = CVI(ordhed.hrrn$)
	CALL linkedl(rrn%(), nn%, firstrec%, hord%, 49)

	'-> Read throught the linked list of the details file
	dnext% = CVI(ordhed.hrrn$)
	l% = 0: m% = 0
	DO WHILE dnext% > 0
		GET #49, dnext%, orddet
		l% = l% + 1: IF l% > maxlines% THEN l% = maxlines%: EXIT DO
		ditem% = CVI(orddet.ditem$)
		ordqty% = CVI(orddet.dordq$)
		invqty% = CVI(orddet.dinvq$)
		Price! = CVS(orddet.dprice$)
		IF ordqty% > 0 THEN
			'RINT dnext%, ditem%, ordqty%, invqty%
			IF orddet.dord% <> CVI(ordhed.hord) THEN
				orddet.dord% = CVI(ordhed.hord)
				PUT #49, dnext%, orddet
			END IF
		END IF
		'- Bottom of read equal loop
		dnext% = orddet.drrn%
	LOOP

END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

