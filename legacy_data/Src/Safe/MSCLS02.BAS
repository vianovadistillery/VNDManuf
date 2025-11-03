'/////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>         M S C L S 0 2       <<<<<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'.dc - Complete
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "MSMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	'$INCLUDE: '\tpmanuf\src\MSCLASS.INC'
	DIM cl$(99)

'>>>>>>>>>>  WRITE THE SCREEN IE BORDERS,HEADINGS,HELPLINE
cf1:
	GET #36, 1, msmisc
	CALL setup("DISPLAY CLASS FILE")
	COLOR 0, 3: LOCATE 25, 4:  PRINT "F1-Exit"; : COLOR 2, 0
'>>>>>>>>>>  WRITE THE DETAILS ON SCREEN
cf2:
	LOCATE 5, 2: COLOR 4
	PRINT " Seq  Class   Seq  Class   Seq  Class   Seq  Class   Seq  Class   Seq  Class"
	COLOR 2
	'**Allocating the data to record no
	s% = 1
	DO
	GET #29, , msclass: cl$(s%) = msclass.cldesc$
	s% = s% + 1
	LOOP WHILE s% < 100
	'**Printing the details onto the table
	s% = 0: i% = 1
	DO WHILE s% <> 99
	s% = s% + 1
	a$ = cl$(s%)
	IF i% = 18 THEN i% = 1
	IF s% < 18 THEN LOCATE i% + 5, 2: PRINT USING " ### \     \"; s%; a$;
	IF s% > 17 AND s% < 35 THEN LOCATE i% + 5, 15: PRINT USING " ### \     \"; s%; a$;
	IF s% > 34 AND s% < 52 THEN LOCATE i% + 5, 28: PRINT USING " ### \     \"; s%; a$;
	IF s% > 51 AND s% < 69 THEN LOCATE i% + 5, 41: PRINT USING " ### \     \"; s%; a$;
	IF s% > 68 AND s% < 86 THEN LOCATE i% + 5, 54: PRINT USING " ### \     \"; s%; a$;
	IF s% > 85 THEN LOCATE i% + 5, 67: PRINT USING " ### \      \"; s%; a$;
	i% = i% + 1
	LOOP
'>>>>>>>>>>  ENTER THE NEW DESCRIPTION FOR CLASS NUMBER
cf3:
	'**Get the class no. between 1 + 99
	newcl$ = "  "
	LOCATE 3, 15: PRINT SPACE$(55)
	LOCATE 3, 15: PRINT "Enter Class number to change..> ";
	CALL inpnew(newcl$, 2!, updwn%, "13,59" + alt$): GOSUB alt
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	b$ = "  ": LSET b$ = newcl$: b% = VAL(b$)
	IF b% < 1 OR b% > 99 THEN GOTO cf3
	'**Get the description
	des$ = "       "
	COLOR 2
	LOCATE 3, 15: PRINT SPACE$(55)
	LOCATE 3, 15: PRINT "Enter new description..> ";
	CALL inpnew(des$, 125!, updwn%, "13,59" + alt$): GOSUB alt
	'**Update the data file and the screen
	COLOR 2
	GET #29, b%, msclass
	LSET msclass.cldesc$ = des$
	PUT #29, b%, msclass
	IF b% < 18 THEN LOCATE b% + 5, 2: PRINT USING " ### \     \"; b%; des$;
	IF b% > 17 AND b% < 35 THEN LOCATE b% - 12, 15: PRINT USING " ### \     \"; b%; des$;
	IF b% > 34 AND b% < 52 THEN LOCATE b% - 29, 28: PRINT USING " ### \     \"; b%; des$;
	IF b% > 51 AND b% < 69 THEN LOCATE b% - 46, 41: PRINT USING " ### \     \"; b%; des$;
	IF b% > 68 AND b% < 86 THEN LOCATE b% - 63, 54: PRINT USING " ### \     \"; b%; des$;
	IF b% > 85 AND b% < 100 THEN LOCATE b% - 80, 67: PRINT USING " ### \      \"; b%; des$;
	GOTO cf3

SUB printing :
	IF s% < 18 THEN LOCATE i% + 5, 2: PRINT USING " ### \     \"; s%; a$;
	IF s% > 17 AND s% < 35 THEN LOCATE i% + 5, 15: PRINT USING " ### \     \"; s%; a$;
	IF s% > 34 AND s% < 52 THEN LOCATE i% + 5, 28: PRINT USING " ### \     \"; s%; a$;
	IF s% > 51 AND s% < 69 THEN LOCATE i% + 5, 41: PRINT USING " ### \     \"; s%; a$;
	IF s% > 68 AND s% < 86 THEN LOCATE i% + 5, 54: PRINT USING " ### \     \"; s%; a$;
	IF s% > 85 THEN LOCATE i% + 5, 67: PRINT USING " ### \      \"; s%; a$;
END SUB
