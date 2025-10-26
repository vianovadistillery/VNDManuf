DECLARE SUB browse.idx (firstonscreen%, ch1%, ch2%)
DECLARE SUB cf8 (l%, s.elem%, newdata$)
DECLARE SUB findorders (thissup$, norders%, hord%)
DECLARE FUNCTION funclimit$ (climit!)
DECLARE SUB linkedl (rrn%(), n%, firstrec%, ord%, chd%)
DECLARE SUB rightprice (price!, tax!)
'////////////////////////////////////////////////////////////////////////
'////    F U L L     D E B T O R S    I N V O I C I N G
'////////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "DSMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CLOSE
	typefields% = -1

	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\cusx.inc'
	'$INCLUDE: '\tpmanuf\src\supx.inc'
	'$INCLUDE: '\tpmanuf\src\whox.inc'
	'$INCLUDE: '\tpmanuf\src\cus.inc'
	CALL browse.idx(s%, 23, 43)
	ENVIRON "PARM$=" + STR$(s%)
	npgm$ = "DSINV01D"
	CALL EXITPGM(npgm$)
	CLOSE
	CHAIN npgm$

SUB browse.idx (firstonscreen%, ch1%, ch2%) STATIC
'$INCLUDE: '\tpmanuf\src\browse01.bi'
END SUB

