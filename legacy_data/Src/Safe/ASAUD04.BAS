DECLARE SUB searchindex (keyin$, chi%, found%)
'///////////////////////////////////////////////////////////////////////
'/////////////  ASAUD04 - AGED CREDITORS/DEBTORS REPORT
'///////////////////////////////////////////////////////////////////////
'.dc - Complete
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	pgm$ = "asaud01"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\asclobal.iNC'
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\CUSX.INC'
	'$INCLUDE: '\tpmanuf\src\CUS.INC'
	CONST pag.len% = 50
'>>>---------------------------------------------------<<<
'>>> NOTE: This program is for Suppliers and Customers
'>>>       Pass parm of  /CR or /DB
'>>>---------------------------------------------------<<<
	db.or.cr$ = "DB"
	db.or.cr$ = ENVIRON$("DB.OR.CR$")
	cr% = INSTR(COMMAND$, "/CR")
	'cr% = 1 '<<<-Swap to CR. System use cr% = 1
	IF cr% > 0 THEN db.or.cr$ = "CR"

	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$)
	maxsup% = CVI(msmisc.max7$)

	 IF db.or.cr$ = "CR" THEN
		cha% = 45: chb% = 44: maxsup% = maxsup%
		ELSE
		cha% = 23: chb% = 43: maxsup% = maxcus%
	 END IF

start:
	CALL setup("AGED CREDITORS/DEBTORS")
	CALL sndmsg(msg$)
	btm$ = "F1-Exit"
	COLOR 0, 3: LOCATE 25, 4: PRINT btm$; : COLOR 2, 0
	IF cha% = 45 THEN
		COLOR 4, 0: LOCATE 5, 25: PRINT "CREDITORS": COLOR 2, 0
		ELSE
		COLOR 4, 0: LOCATE 5, 25: PRINT "DEBTORS": COLOR 2, 0
		END IF
cf1:
	opt$ = "1"
	LOCATE 8, 30: PRINT "1..Outstanding"
	LOCATE 9, 30: PRINT "2..All"
	LOCATE 11, 30: PRINT "Enter option...>"; opt$
	LOCATE 11, 46: CALL inpnew(opt$, 1!, updwn%, "13,59" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN GOTO endpgm
	IF updwn% = 60 THEN GOTO cf1
	opt% = VAL(opt$)
	IF opt% < 1 OR opt% > 2 THEN GOTO cf1

cf2:
	mth$ = msmisc.DBmonth$
	IF cha% = 45 THEN mth$ = msmisc.CRmonth$
	'>- sub one from the sel month
	yy% = VAL(MID$(mth$, 3, 2))
	mm% = VAL(MID$(mth$, 1, 2))
	mm% = mm% - 1: IF mm% < 1 THEN mm% = 12: yy% = yy% - 1
	IF yy% > 99 THEN yy% = 0
	IF yy% < 0 OR yy% > 99 THEN yy% = 0
	IF mm% < 1 OR mm% > 12 THEN mm% = 0
	yy$ = RIGHT$("0" + MID$(STR$(yy%), 2, 2), 2)
	mm$ = RIGHT$("0" + MID$(STR$(mm%), 2, 2), 2)
	mth$ = mm$ + yy$

	LOCATE 11, 30: PRINT "Enter month...>"; mth$; "  (9999 for current)"
	LOCATE 11, 45: CALL inpnew(mth$, 104!, updwn%, "13,59" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN GOTO endpgm
	IF updwn% = 60 THEN GOTO cf1


	asclobal$ = "DBCL" + mth$ + ".ASF"
	IF cha% = 45 THEN asclobal$ = "CRCL" + mth$ + ".ASF"
	IF mth$ = "9999" THEN asclobal$ = "ASCURBAL.ASF"
	X$ = DIR$(asclobal$)
	IF X$ = "" THEN msg$ = "File " + asclobal$ + " not found!": GOTO start

	OPEN asclobal$ FOR RANDOM SHARED AS #60 LEN = LEN(clobal)
	'stdout$ = "CON": CLS '??
	OPEN stdout$ FOR OUTPUT AS #99
	WIDTH #99, 128
				  
	GOSUB do.list
	CLOSE #60
	CLOSE #99
	GOTO start
endpgm:
	CLOSE
	CALL exitpgm(pgm$)
	CHAIN pgm$
'///////////////////////////////////////////////////////////////////////
'////////  PRINT THE LIST
'///////////////////////////////////////////////////////////////////////
do.list:
	IF stdout$ = "CON" THEN CLS
	pag% = 0: lin% = 9999
	tot.o90! = 0
	tot.o60! = 0
	tot.o30! = 0
	tot.ocur! = 0

	rec% = 1
	GET #60, rec%, clobal
	DO WHILE NOT EOF(60)
		keyin$ = clobal.cust$
		CALL searchindex(keyin$, cha%, found%)
		recx% = 1
		recx% = LOC(cha%)
		GET #cha%, recx%, CUSX
		wrrn% = CVI(CUSX.wrrn$)
		sno% = CVI(CUSX.wrrn$)
		'IF sno% < 1 OR sno% > maxsup% THEN STOP: sno% = 1: SOUND 2400, 1
		GET #chb%, sno%, cus

		IF rec% MOD 10 = 0 AND stdout$ <> "CON" THEN
			LOCATE 20, 20: PRINT "Printing record number"; rec%; CUSX.wcde$; "  "
			END IF


		total# = clobal.o90! + clobal.o60! + clobal.o30! + clobal.ocur!  '???
		cusvalue! = CVS(cus.advalue$)
		ok% = -1
		IF sno% = 1 AND total# = 0 THEN ok% = 0
		IF opt% = 2 AND total# = 0 THEN ok% = 0
		IF ok% THEN
			IF lin% > pag.len% THEN GOSUB heading
			PRINT #99, USING "\   \ - \                            \ $$##,###.## $$##,###.## $$##,###.## $$##,###.## $$##,###.## \      \$$##,###.## \      \"; clobal.cust$; cus.sname$; clobal.ocur!; clobal.o30!; clobal.o60!; clobal.o90!; total#;  _
FNDYY$(cus.addate$); cusvalue!; cus.addocnum$
			lin% = lin% + 1
			 
			tot.o90! = tot.o90! + clobal.o90!
			tot.o60! = tot.o60! + clobal.o60!
			tot.o30! = tot.o30! + clobal.o30!
			tot.ocur! = tot.ocur! + clobal.ocur!
			END IF

		GET #60, , clobal: rec% = rec% + 1
		LOOP
	GOSUB end.of.report
x.dolist:
RETURN
'///////////////////////////////////////////////////////////////////////
'/////////////  G E N E R A L     H E A D I N G  ///////////////////////
'///////////////////////////////////////////////////////////////////////
heading:
	pag% = pag% + 1: lin% = 0
	IF pag% > 1 THEN PRINT #99, CHR$(12)
	'-----------------------------------------------------------------------
	PRINT #99, CHR$(15)
	'PRINT #99, USING "!        T R A D E P A I N T S   P T Y.   L T D."; CHR$(14)
	PRINT #99, USING "!   J A N G E R   P / L.  Trading as  T R A D E P A I N T S."; CHR$(14)
	PRINT #99, ""
	IF cha% = 45 THEN
	PRINT #99, "#ASAUD04                            Aged Creditors for the period ending "; mth$; "                                        "; date1$
	ELSE
	PRINT #99, "#ASAUD04                            Aged Debtors for the period ending "; mth$; "                                          "; date1$
	END IF

	PRINT #99, TAB(118); USING "Page ####"; pag%
	PRINT #99, "Code. - ..............................     Current      30days      60Days      90Days       Total *------ Last/payment -----*"
	PRINT #99, STRING$(127, "-")
RETURN
'///////////////////////////////////////////////////////////////////////
'/////////////  END OF REPORT
'///////////////////////////////////////////////////////////////////////
end.of.report:
	total# = tot.o90! + tot.o60! + tot.o30! + tot.ocur!
	IF total# <> 0 THEN
		perc.ocur! = tot.ocur! / total# * 100
		perc.o30! = tot.o30! / total# * 100
		perc.o60! = tot.o60! / total# * 100
		perc.o90! = tot.o90! / total# * 100
		perc.total# = perc.ocur! + perc.o30! + perc.o60! + perc.o90!
		ELSE
		perc.ocur! = 0
		perc.o30! = 0
		perc.o60! = 0
		perc.o90! = 0
		perc.total# = 0
		END IF

	PRINT #99, STRING$(127, "=")
	PRINT #99, USING "                                       $$##,###.## $$##,###.## $$##,###.## $$##,###.## $$##,###.##"; tot.ocur!; tot.o30!; tot.o60!; tot.o90!; total#
	PRINT #99, USING "                                            ###.##      ###.##      ###.##      ###.##      ###.##"; perc.ocur!; perc.o30!; perc.o60!; perc.o90!; perc.total!
	PRINT #99, "END OF REPORT"
	PRINT #99, CHR$(18);
	PRINT #99, CHR$(12);
	CLOSE #99
RETURN

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

