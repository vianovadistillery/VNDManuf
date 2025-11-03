'------------------------------------------------------------------------
'>>>>>>>>>>>>>>>>>>> ACREP04 -  MASTER MARGIN LIST <<<<<<<<<<<<<<<<<<<<<<
'------------------------------------------------------------------------
'.dc - Complete
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "ACMENU"
	DB.OR.CR$ = "CR"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	DIM mm(80)
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\supx.inc'
	'$INCLUDE: '\tpmanuf\src\sup.inc'
	'$INCLUDE: '\tpmanuf\src\acmgn.inc'
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	OPEN stdout$ FOR OUTPUT AS #99

	 GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	'>>>>> Array the margin file
	GET #1, 1, acmgn: mm(1) = CVS(acmgn.margin$)
	FOR i% = 2 TO 80: GET #1, , acmgn: mm(i%) = CVS(acmgn.margin$): NEXT
	CLOSE #1
	'////////////////////////////////////////////////////////////////////////
	CALL setup("M A S T E R   M A R G I N   L I S T")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : COLOR 2, 0
	in$ = "Y"
yorn:
	COLOR 2, 0: LOCATE 10, 30: PRINT "Continue (Y/N)..> "; CHR$(fnh);
	CALL inpnew(in$, 101!, updwn%, "59,13" + alt$): GOSUB alt
	IF updwn% = 59 THEN in$ = "N"
	IF in$ = "y" THEN in$ = "Y"
	IF in$ = "n" THEN in$ = "N"
	IF in$ <> "Y" AND in$ <> "N" THEN GOTO yorn
	IF in$ = "N" THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	'///////////////////////////////////////////////////////////////////////////
	'///   GO
	'///////////////////////////////////////////////////////////////////////////
	pag = 0: lin% = 9999
	FOR i% = 1 TO maxsup%
		GET #45, i%, supx
		IF supx.wcde$ = "~~~~" THEN EXIT FOR
		GOSUB prtrec'files print
		LOCATE 20, 25: PRINT "Printing record "; i%; sup.sname$; CHR$(fne)
		NEXT
	PRINT #99, CHR$(12);
	CLOSE
	CALL exitpgm(apgm$)
	CHAIN apgm$
	'///////////////////////////////////////////////////////////////////////////
	'///   PRINT A RECORD
	'///////////////////////////////////////////////////////////////////////////
prtrec:
	IF lin% > 45 THEN GOSUB heading
	wrrn% = CVI(supx.wrrn$)
	IF wrrn% < 1 OR wrrn% > maxsup% THEN GOTO xprtrec
	GET #44, wrrn%, sup'get from master file
	a2% = ASC(sup.scont1$) - 46: IF a2% < 1 OR a2% > 80 THEN a2% = 1
	a3% = ASC(sup.scont2$) - 46: IF a3% < 1 OR a3% > 80 THEN a3% = 1
	a11% = ASC(sup.sret$) - 46: IF a11% < 1 OR a11% > 80 THEN a11% = 1
	a13% = ASC(sup.sdist$) - 46: IF a13% < 1 OR a13% > 80 THEN a13% = 1
	pc2 = mm(a2%): pc3 = mm(a3%)
	pc11 = mm(a11%): pc13 = mm(a13%)
	'>>>>  Print
	IF sup.sret$ <> " " THEN
		PRINT #99, USING "#### &  !###.##%   !###.##%   !###.##%   !###.##% "; CVI(sup.sno$); sup.sname$; sup.sret$; pc11; sup.sdist$; pc13; sup.scont1$; pc2; sup.scont2$; pc3
		lin% = lin% + 1
		END IF
xprtrec:
	RETURN
	'///////////////////////////////////////////////////////////////////////
	'///   HEADING
	'///////////////////////////////////////////////////////////////////////
heading:
	IF pag > 0 THEN PRINT #99, CHR$(12);
	pag = pag + 1: lin% = 0
	col$ = "Code Supplier Name.                    Retail     Distr.    Contr 1    Contr 2"
	'    "#### \                            \  !###.##%   !###.##%   !###.##%   !###.##% ";CVI(sup.SNO$),SNAME$,SRET$,PC11,SDIST$,PC13,SCONT1$,PC2,SCONT2$,PC3
	PRINT #99, "#mslbl01"; TAB(66); "Date:"; date1$
	PRINT #99, TAB(66); "Time:"; TIME$
	PRINT #99, ""
	PRINT #99, CHR$(14); msmisc.cc$
	PRINT #99, ""
	PRINT #99, "        M A S T E R   M A R G I N    L I S T"
	PRINT #99, a$; TAB(73); "Page:"; pag
	PRINT #99, STRING$(79, "=")
	PRINT #99, col$
	RETURN
