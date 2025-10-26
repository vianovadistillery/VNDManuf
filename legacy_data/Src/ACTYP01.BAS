'/////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>         A C T Y P 0 1       <<<<<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'.dc - Complete
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "ACMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\TYPES.INC'
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	 COLOR 2
	 CALL setup("UPDATE SUPPLIER TYPES FILE")
main:
	 COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : LOCATE 25, 71: PRINT CHR$(24); CHR$(25); "-Move";
	 COLOR 2, 0
	 GOSUB display
	 LOCATE 3, 25: PRINT "Enter number to view..>"
	 LOCATE 3, 49:
	 COLOR 2:
	 a$ = ""
	 CALL inpnew(a$, 2!, updwn%, "13,59" + ALT$): GOSUB ALT
	 IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	 b$ = "   ": LSET b$ = a$: b% = VAL(b$)
	 IF b% < 1 OR b% > 27 THEN
	COLOR 14:
	LOCATE 4, 27: PRINT "Supplier type not found"
	COLOR 2
	GOTO main
	 ELSE
	LOCATE 4, 27: PRINT CHR$(fne)
	 END IF
	 
	'***** edit/display details
	 rec = b%
	 GET #42, rec, types
	 LOCATE 21, 5: COLOR 6:
	 PRINT "Details for record:       Code:     Code desc: ";
	 COLOR 2
	 LOCATE 21, 24: PRINT rec;
	 LOCATE 21, 37: PRINT types.dftype$;
	 LOCATE 21, 52: PRINT types.dfdesc$;
tcode:          '***** Get code
	 LSET a$ = types.dftype$
	 LOCATE 21, 37:
	 CALL inpnew(a$, 101!, updwn%, "13,59,72,80")
	 IF updwn% = 59 THEN GOTO tsave
	 IF updwn% = 72 THEN GOTO tsave
	 IF updwn% = 80 THEN GOTO tdesc
	 '***** Check for duplications
	 ok = 1
	 FOR i% = 1 TO 27
	   GET #42, i%, types
	   IF types.dftype$ = a$ AND i% <> rec THEN ok = 0: i% = 999
	 NEXT
	 IF ok = 0 THEN
	COLOR 14:
	LOCATE 22, 5: PRINT "Type already used. Try again.":
	COLOR 2: GOTO tcode
	 END IF
	 LSET types.dftype$ = a$
	 PUT #42, rec, types
	 LOCATE 22, 5: PRINT CHR$(fne)
tdesc:          '***** Get Code description
	 GET #42, rec, types
	 a$ = types.dfdesc$
	 LOCATE 21, 52:
	 CALL inpnew(a$, 125!, updwn%, "13,59,72,80")
	 IF updwn% = 59 THEN GOTO tcode
	 IF updwn% = 72 THEN GOTO tcode
	 IF updwn% = 80 THEN GOTO tsave
	 LSET types.dfdesc$ = a$
tsave:          '***** save details
	 rec = b%
	 PUT #42, rec, types
	 LOCATE 21, 5: PRINT CHR$(fne)
	 GOTO main
display:        '***** Display all records
	 FOR i% = 1 TO 27
	GET #42, i%, types
	IF i% < 14 THEN
	   LOCATE i% + 4, 8:
	ELSE
	   LOCATE i% - 9, 47:
	END IF
	COLOR 12: PRINT USING "##   "; i%; :
	COLOR 2: PRINT types.dftype$; " "; types.dfdesc$; " ";
	 NEXT
	 LOCATE 19, 10: PRINT " 'A' Code on Supplier switches Margin fields on."
	 LOCATE 20, 10: PRINT " 'Z' Code on Customer switches Charge - to facility on."
	 RETURN

