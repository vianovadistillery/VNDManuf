'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'>>>>>>>>>>>>>>>>>>> ACMENU  -  ACCESSORY MENU <<<<<<<<<<<<<<<<<<<<<<<<<<
'////////////////////////////////////////////////////////////////////////
	'ACMENU.BAS
'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
	apgm$ = "MENUTP"
''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	GET #36, 1, msmisc
	cca$ = msmisc.cc$
	CLOSE
	CALL setup(cca$)
	CALL PRTBTM(" F1-Exit")
	COLOR 4, 0
	LOCATE 3, 22: PRINT "  A C C E S S O R Y    S Y S T E M  "
	LOCATE 4, 22: PRINT "===================================="
	COLOR 2: x = 27
	LOCATE , x: PRINT "1...Maintain Margins."
	LOCATE , x: PRINT "2...Supplier Types."
	LOCATE , x: PRINT "3...List Supplier Margins."
	'
	COLOR 4: LOCATE 11, 12: PRINT "ACCESSORY": COLOR 3
	'
	LOCATE , 5: PRINT "11..Maintain Accessory Stock."
	LOCATE , 5: PRINT "12..Accessory Price Lists."
	LOCATE , 5: PRINT "13..Accessory Stocktake System."
	LOCATE , 5: PRINT "14..Repack"
	LOCATE , 5: PRINT "15..Build/Rebuild Stock on Order."
	'
	COLOR 4: LOCATE 11, 52: PRINT "TINTING": COLOR 3
	'
	LOCATE , 45: PRINT "21..Maintain Tint Formulations."
	LOCATE , 45: PRINT "22..Print Formula Lists."
	LOCATE , 45: PRINT "23..Maintain Tint Bases."
	LOCATE , 45: PRINT "24..Maintain Colour Cards."
	LOCATE , 45: PRINT "25..Rebuild Colour Formulations"
	COLOR 2
	'
	'>>>>>>>>>>>>>>>>>>>>>>>>>> OPTIONS <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
	'
getopt:
	 '
	LOCATE 21, 27: PRINT "Option..> ";
	a$ = "": updwn% = 1: LOCATE 21, 36
	'
	CALL inpnew(a$, 102!, updwn%, "59,13" + alt$): GOSUB alt
	'
	b% = VAL(a$)
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	IF b% = 1 THEN achain$ = "acmgn01": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 2 THEN achain$ = "actyp01": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 3 THEN achain$ = "acrep04": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 11 THEN achain$ = "acstk01": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 12 THEN achain$ = "acrep01": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 13 THEN achain$ = "acrep02": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 14 THEN achain$ = "acstk02": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 15 THEN achain$ = "acstk03": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 21 THEN achain$ = "rtcol01": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 22 THEN achain$ = "rtcol03": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 23 THEN achain$ = "rtcol02": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 24 THEN achain$ = "rtcol04": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 25 THEN achain$ = "rtcol05": CALL exitpgm(achain$): CHAIN achain$
	'
GOTO getopt
	'
'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> END <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
