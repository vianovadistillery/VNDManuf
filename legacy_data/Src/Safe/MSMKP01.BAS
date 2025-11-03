'/////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>         M S M K P 0 1       <<<<<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'>>>>>>>>>> CHANGES
'>>>>>>>>>> 25/2/92 : ADDED INCLUDE HEADERS
'>>>>>>>>>> LJC     : FIXED HELP LINE ON SCREENS
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "MSMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	'$INCLUDE: '\tpmanuf\src\MSMKP.INC'
	CONST ln% = 8
	CONST lp% = 12
cf1:
	GET #36, 1, msmisc
	CALL setup("CHANGE MARKUP VALUES")
	COLOR 0, 3: LOCATE 25, 4: PRINT SPACE$(74);
	LOCATE 25, 4: PRINT "F1-Exit                           F9-Change Error Factor        F10-Change";
	COLOR 6, 0: LOCATE 6, lp% + 2: PRINT "Num.           Price List               Markup    Base"
	COLOR 7, 0: LOCATE 7, lp% + 2: PRINT "------------------------------------------------------"
	COLOR 2, 0
	LOCATE ln%, lp%: PRINT "   0...GATE COST"
	FOR i% = 1 TO 9
	GET #37, i%, msmkp
	mk = CVS(msmkp.mk$)
	mkon% = CVI(msmkp.mkon$)
	LOCATE ln% + i%, lp%: PRINT USING "####...&    ####.##      #"; i%; msmkp.mm$; mk * 100; mkon%
	NEXT
	COLOR 2: LOCATE 1, 1
	DO
	CALL inpnew(in$, 0!, updwn%, "59,67,68")
	LOOP UNTIL updwn% > 0
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	IF updwn% = 67 THEN GOSUB chgerrfactor
	IF updwn% = 68 THEN GOSUB chgmkup
	GOTO cf1
'///////////////////////////////////////////////////////////////////////
'///  CHANGE MARKUP VALUES
'///////////////////////////////////////////////////////////////////////
chgmkup:
	COLOR 0, 3: LOCATE 25, 4: PRINT SPACE$(74);
	LOCATE 25, 4: PRINT "F1-Exit         F2-Previous                                     F10-Change";
	FOR i% = 1 TO 9
	   GET #37, i%, msmkp
	   COLOR 2: LOCATE ln% + i%, lp% + 7
	   in$ = msmkp.mm$
	   CALL inpnew(in$, 130!, updwn%, "13,59,60")
	   IF updwn% = 59 THEN EXIT FOR
	   IF updwn% = 60 THEN i% = i% - 2: GOTO continue
	   LSET msmkp.mm$ = in$
	   LOCATE ln% + i%, lp% + 41
	   in$ = STR$(CVS(msmkp.mk$) * 100)
           CALL inpnew(in$, -5.2!, updwn%, "13,59,60")
	   IF updwn% = 59 THEN EXIT FOR
	   IF updwn% = 60 THEN i% = i% - 2: GOTO continue
	   LSET msmkp.mk$ = MKS$(VAL(in$) / 100)
	   LOCATE ln% + i%, lp% + 54
	   in$ = STR$(CVI(msmkp.mkon$))
	   in$ = MID$(in$, 2)
	   CALL inpnew(in$, 1!, updwn%, "13,59,60")
	   IF updwn% = 59 THEN EXIT FOR
	   IF updwn% = 60 THEN i% = i% - 2: GOTO continue
	   LSET msmkp.mkon$ = MKI$(VAL(in$))
	   PUT #37, i%, msmkp
continue:
	   IF i% < 0 THEN i% = 0
	 NEXT
	 RETURN
'///////////////////////////////////////////////////////////////////////
'/// 'Change the error factor for R.M.C
'///////////////////////////////////////////////////////////////////////
chgerrfactor:
	 CALL box(2, 3, 79, 20, 2, 0, 0)
	 COLOR 0, 3: LOCATE 25, 1: PRINT SPACE$(79);
	 COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit";
	'* Change error factor for R.M.C
	 COLOR 2, 0: LOCATE 11, 10
	 GET #37, 10, msmkp
	 ff = CVS(msmkp.mk$) * 100
	 LOCATE 10, 20: PRINT USING "Current error factor :#.##%"; ff
	 LOCATE 10, 42
	 in$ = STR$(ff)
         CALL inpnew(in$, 3.2!, updwn%, "13,59")
	 IF updwn% = 59 THEN RETURN
	 LSET msmkp.mk$ = MKS$(VAL(in$) / 100)
	 LSET msmkp.mkon$ = MKI$(0)
	 PUT #37, 10, msmkp
	 RETURN
