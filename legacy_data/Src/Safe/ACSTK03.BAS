DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB dsplywho (selitem%)
'///////////////////////////////////////////////////////////////////////
'///   BUILD/REPAIR Stock on Order to ACSTK
'///////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	acstkf$ = "ACF"
	apgm$ = "ACMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	keyl% = 20: qk$ = SPACE$(keyl%)
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\MSMISC.inc'
	'$INCLUDE: '\tpmanuf\src\ACSTK.inc'
	'$INCLUDE: '\tpmanuf\src\ORDHED.INC'
	'$INCLUDE: '\tpmanuf\src\ORDDET.INC'
	 GET #36, 1, msmisc
	 maxsup% = CVI(msmisc.max1$): maxacc% = CVI(msmisc.max5$)
'///////////////////////////////////////////////////////////////////////
'>>>>  M A I N L I N E
'///////////////////////////////////////////////////////////////////////
start:
	CALL setup("BUILD/REPAIR STOCK ON ORDER")
	LOCATE 25, 4: COLOR 0, 3: PRINT "F1-Exit";
	COLOR 2, 0
	LOCATE 10, 23: PRINT "1...Build/Repair Stock on order"
getopt:
	LOCATE 12, 23: PRINT "Option..> "; CHR$(fnh);
	CALL inpnew(OPT$, 1!, updwn%, "13,59" + alt$): GOSUB alt
	IF updwn% = 59 THEN CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
	OPT% = VAL(OPT$)
	IF OPT% < 1 OR OPT% > 1 THEN GOTO getopt

	'>>>-- Cont
	i% = 1
	GET #3, i%, acstk
	DO
		IF acstk.soo <> 0 THEN
			acstk.soo = 0
			PUT #3, i%, acstk
		END IF

		GET #3, , acstk: i% = i% + 1
	LOOP WHILE NOT EOF(3)

	i% = 1
	GET #49, i%, orddet
	DO
		dord% = orddet.dord%
		ditem% = CVI(orddet.ditem$)
		dordq% = CVI(orddet.dordq$)
		IF dord% > 0 AND (ditem% > 0 AND ditem% < maxacc%) THEN
			GET #3, ditem%, acstk
			acstk.soo = acstk.soo + dordq%
			PUT #3, ditem%, acstk
		END IF

		GET #49, , orddet: i% = i% + 1
		IF i% MOD 100 = 0 THEN LOCATE 18, 30: PRINT i%
	LOOP WHILE NOT EOF(49)
CLOSE


CALL EXITPGM(apgm$)
CHAIN apgm$
