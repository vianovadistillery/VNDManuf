DECLARE SUB recalcall ()
DECLARE SUB calcbulk (form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)
DECLARE SUB costing (rec%, form$)
DECLARE SUB export (rec%)
DECLARE SUB cvt.tnt (tnt$, tnt%, tntf$)
DECLARE SUB dsply (rec%, rec4cost%, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!, form$)
DECLARE SUB getrec (rec%, rec4cost%)
DECLARE SUB round.long (in#, CUTOFF!)
DECLARE SUB trimfile (ok%)
DECLARE SUB accbrowse (rec%)
DECLARE SUB Recallmgn (skipask$, override.dots$)
DECLARE SUB globalrecalc ()
DECLARE SUB clrrcdfmt ()
DECLARE SUB addrec (rec%)
DECLARE SUB Do.delete (rec%)
DECLARE SUB browse (rec%)
DECLARE SUB dsplymargin ()
DECLARE SUB global.recalc ()
DECLARE SUB recalc ()
DECLARE SUB Sales ()
DECLARE FUNCTION perc! (code$)
DECLARE SUB searchindex (keyin$, chi%, found%)
'/////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>         A C S T K 0 1       <<<<<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'.dc - Complete
'$INCLUDE: '.\src\pgmhead.inc'
	apgm$ = "ACMENU"
	DB.OR.CR$ = "CR"
	keyl% = 20: qk$ = SPACE$(keyl%)
''$INCLUDE: '.\src\pgmerr.INC'
	typefields% = -1
	'$INCLUDE: '.\src\ACSTK.INC'
	CALL index("OPEN ", ind%, "acstkx3.acf", 7, keyl%)
	'$INCLUDE: '.\src\MSMISC.INC'
	'$INCLUDE: '.\src\whof.INC'
	'$INCLUDE: '.\src\supX.INC'
	'$INCLUDE: '.\src\sup.INC'
	'$INCLUDE: '.\src\ACMGN.INC'
	'$INCLUDE: '.\SRC\tnthed.INC'
	'$INCLUDE: '.\SRC\tnthedx.INC'
	'$INCLUDE: '.\SRC\forhed.INC'
	'$INCLUDE: '.\SRC\forhedx.INC'
	'$INCLUDE: '.\SRC\msrmat.INC'

	 'keyl% = 10: QK$ = SPACE$(keyl%)
	DIM SHARED xx#(8, 5)
	DIM SHARED sz$(100)
	DIM SHARED mc$(80), mm(80)
	DIM SHARED fl%, xl%, c1%, c2%, c3%, c4%, c5%
	DIM SHARED maxacc%, maxsup%
	DIM SHARED formname$, formbulk, formbulkkg
	DIM SHARED bulk!, pkge!, label!, lid!, pbox!, boxlbl!, manu!, pack%
	 sp40$ = SPACE$(40)
	 GET #36, 1, msmisc
	 maxsup% = CVI(msmisc.max1$): maxacc% = CVI(msmisc.max5$)
	 '>>>>> Array the margin file
	 GET #1, 1, acmgn: mm(1) = CVS(acmgn.margin$): mc$(1) = acmgn.mcode$
	 FOR i% = 2 TO 80: GET #1, , acmgn: mm(i%) = CVS(acmgn.margin$): mc$(i%) = acmgn.mcode$: NEXT
	 CLOSE #1
	 '>>>>> Array the size file
	 'GET #41, 1, sizes: sz$(1) = sizes.short$
	 'FOR i% = 2 TO 99: GET #41, , sizes: sz$(i%) = sizes.short$: NEXT
start:
main:
	 H1$ = "U P D A T E   P A I N T   S T O C K"
	 CALL setup(H1$)

'>>>>>            M A I N L I N E
	 DO
	COLOR 7, 0
	LOCATE 24, 1: PRINT "ศ"; STRING$(78, "อ"); "ผ";
	COLOR 0, 3
	LOCATE 25, 1: PRINT SPACE$(80);
	LOCATE 25, 1: PRINT "F1-Ext F2-U/Menu F3-Price F4-Del F5-Exp F6-Bws F7-Mgn F8-Ins F9-Rep. F10-Chg. ";
	'PRINT CHR$(24); CHR$(25); "-Move";
	COLOR 2, 0
480
	COLOR 7, 0: LOCATE 2, 23: PRINT "ต                              ฦอออออ": COLOR 2
	LOCATE 2, 25: PRINT "Control...> ";
	LOCATE 2, 45: PRINT "(*-Ext.)";
	p$ = ""
	LOCATE 2, 37:
	CALL inpnew(p$, 205!, updwn%, "13,27,59-60,61,62-68,72,80" + ALT$): GOSUB ALT
	p$ = UCASE$(p$)
	alpha% = 0
	FOR i% = 1 TO 5
		 A$ = MID$(p$, i%, 1)
		 IF A$ = " " THEN A$ = "1"
		 IF A$ = "" THEN A$ = "1"
		 IF A$ < "0" OR A$ > "9" THEN alpha% = -1
	NEXT
	ok% = 0
	IF p$ = "*" THEN ctl.p$ = "input": sa$ = "": GOSUB first.alpha.p: ok% = -1
	IF p$ = "N" THEN ctl.p$ = "read": GOSUB first.alpha.p: ok% = -1
	IF p$ = "P" THEN ctl.p$ = "readp": GOSUB first.alpha.p: ok% = -1
	IF ok% = 0 AND alpha% = -1 THEN ctl.p$ = "chain": sa$ = p$: GOSUB first.alpha.p
	IF updwn% = 59 THEN CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
	IF updwn% = 27 THEN GOSUB MULTUPD
	IF updwn% = 60 THEN CALL recalcall 'globalrecalc
	IF updwn% = 61 THEN
		IF acstk.no% <> rec% THEN
			ELSE
		CALL costing(rec%, acstk.form$)
		END IF
		p$ = STR$(p)
	END IF
	IF updwn% = 62 THEN CALL Do.delete(rec%): CALL setup(H1$)
	IF updwn% = 63 THEN CALL Sales
	IF updwn% = 64 THEN CALL accbrowse(rec%): CALL setup(H1$): p$ = STR$(rec%): CALL dsply(rec%, rec4cost%, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!, form$)
	IF updwn% = 65 THEN
		CALL dsplymargin              '***** Margin
		IF updwn% = 65 THEN CALL trimfile(ok%): GOTO start
	END IF
	IF updwn% = 66 THEN CALL addrec(rec%): p = rec%
	IF updwn% = 67 THEN GOSUB REPEAT
	IF updwn% = 68 THEN GOSUB CHANGE: p$ = STR$(p)
	IF updwn% = 72 THEN p = p - 1: p$ = STR$(p)        '***** UP arrow
	IF updwn% = 80 THEN p = p + 1: p$ = STR$(p)         '***** DN arrow
	'****** Process record
	oldp = p
	IF LEN(p$) > 0 THEN p = VAL(p$)
	IF p = 0 THEN p = oldp + 1
	IF p = rec% AND updwn% = 13 AND LEN(p$) = 0 THEN p = oldp + 1
	IF p < 1 OR p > maxacc% THEN COLOR 14: LOCATE 22, 2: PRINT "Stock number invalid"; : COLOR 2: GOTO 480
	rec% = p
	IF rec% < 1 OR rec% > maxacc% THEN COLOR 14: LOCATE 22, 2: PRINT "Stock number invalid"; : COLOR 2: GOTO 480
	CALL getrec(rec%, rec4cost%)
	CALL recalc
		CALL dsply(rec%, rec4cost%, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!, form$)
'>>>>> If the number is entered chain to the index to enable next/previous
	IF alpha% = 0 THEN
		 theno$ = MKI$(acstk.no%)
		 sfx$ = "  ": MID$(sfx$, 1, 1) = MID$(theno$, 2, 1): MID$(sfx$, 2, 1) = MID$(theno$, 1, 1)
		 sa$ = acstk.search$   ' + sup.SEARCH$ + sup.STYPE$ + acstk.SIZE$ + sfx$
		 FOR i% = 1 TO LEN(sa$) - 2
			IF MID$(sa$, i%, 1) = CHR$(0) THEN MID$(sa$, i%, 1) = " "
		 NEXT
		 LSET qk$ = sa$
		 GOSUB first.alpha.p
	END IF
	 LOOP
'////////////////////////////////////////////////////////////////////////////
'>>>>-  C H A N G E
'////////////////////////////////////////////////////////////////////////////
CHANGE:
	 IF rec% < 1 OR rec% > maxacc% THEN RETURN
	 OldRecalcflag$ = chgflg$ + acstk.salestaxcde$ + acstk.disccdeone$ + acstk.disccdetwo$ + acstk.distributorcde$ + acstk.retailcde$ + acstk.countercde$ + acstk.tradecde$ + acstk.contractcde$ + acstk.industrialcde$
	 acstk.no% = rec%
	bulk! = acstk.bulk!
	chgmenu% = 1
	ctl% = 1:  maxctl% = 33
	DO WHILE NOT ctl%  '***** Edit
		IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
		'***** Options
		ON ctl% GOSUB CF1, cf1a, CF2, CF3, CF4, CF5, CF6, CF7, cf7aa, Cf7A, CF7B, CF8, cf9, cf10, cf11, cf12, cf12a, CF13, CF14, cf15, cf16, cf17, cf18, cf19, cf20, CF21, CF22, CF23, CF24, CF25, CF26, CF27, cf28

		'IF RTRIM$(LTRIM$(acstk.suplr4stdcost$)) + RTRIM$(LTRIM$(acstk.search4stdcost)) > "" THEN
		'  IF ctl% = 10 AND updwn% = 13 THEN ctl% = 25
		'  IF ctl% = 29 AND updwn% = 60 THEN ctl% = 11
		'END IF
		IF ctl% = 13 AND updwn% = 13 AND acstk.distributorcde$ = "." THEN
			GOSUB CF14:
			IF updwn% = 60 THEN ctl% = ctl% + 1
			END IF

		IF ctl% = 17 AND updwn% = 13 AND acstk.retailcde$ = "." THEN
			GOSUB cf20:
			IF updwn% = 60 THEN ctl% = ctl% + 1
			END IF
		IF ctl% = 18 AND updwn% = 13 AND acstk.countercde$ = "." THEN
			GOSUB CF21: IF updwn% = 60 THEN ctl% = ctl% + 1
			END IF
		IF ctl% = 19 AND updwn% = 13 AND acstk.tradecde$ = "." THEN
			GOSUB CF22: IF updwn% = 60 THEN ctl% = ctl% + 1
			END IF
		IF ctl% = 20 AND updwn% = 13 AND acstk.contractcde$ = "." THEN
			GOSUB CF23: IF updwn% = 60 THEN ctl% = ctl% + 1
			END IF
		IF ctl% = 21 AND updwn% = 13 AND acstk.industrialcde$ = "." THEN
			GOSUB CF24: IF updwn% = 60 THEN ctl% = ctl% + 1
			END IF

		NewRecalcflag$ = chgflg$ + acstk.salestaxcde$ + acstk.disccdeone$ + acstk.disccdetwo$ + acstk.distributorcde$ + acstk.retailcde$ + acstk.countercde$ + acstk.tradecde$ + acstk.contractcde$ + acstk.industrialcde$ + acstk.wholesalecde$
		IF OldRecalcflag$ <> NewRecalcflag$ THEN
			chgflg$ = "N"
			NewRecalcflag$ = chgflg$ + acstk.salestaxcde$ + acstk.disccdeone$ + acstk.disccdetwo$ + acstk.distributorcde$ + acstk.retailcde$ + acstk.countercde$ + acstk.tradecde$ + acstk.contractcde$ + acstk.industrialcde$ + acstk.wholesalecde$
			OldRecalcflag$ = NewRecalcflag$
			CALL recalc
			CALL calcbulk(form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!) '??
			CALL dsply(rec%, rec4cost%, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!, form$)
		END IF

		ctl% = ctl% + 1      '***** Pgm ctl processing
		IF updwn% = 60 THEN ctl% = ctl% - 2
		IF ctl% > maxctl% THEN updwn% = 59
		IF updwn% = 59 THEN ctl% = -1
	LOOP

	CALL recalc
	wrkd$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
	LSET acstk.date$ = FNDY$(wrkd$)

	acstk.no% = rec%
	PUT #3, rec%, acstk
	CALL export(rec%)
RETURN
'////////////////////////////////////////////////////////////////////////////
'>>>>>   S E C O N D     C H A N G E     M E N U
'////////////////////////////////////////////////////////////////////////////
MULTUPD:
	 IF rec% < 1 OR rec% > maxacc% THEN GOTO X.MULTUPD
	 chgmenu% = 2
	 COLOR 15, 10
	 LOCATE 24, 1: PRINT SPACE$(80);
	 LOCATE 25, 1: PRINT SPACE$(80);
	 LOCATE 24, 1: PRINT " Esc)Search....  F2)Descrip..  F3)Supplier....  F4)Size line.   F5)Tax line...";
	 LOCATE 25, 1: PRINT "  F6)Cost......  F7)Margins..  F8)Invoice.....  F9)Activity..   F10)SOH.......";

	 COLOR 2, 0
	LOCATE 1, 1: CALL inpnew(A$, 0!, updwn%, "59-68,27")
	'***** - Get the company for the SOH & ACT FLAGS
	IF updwn% = 66 OR updwn% = 67 THEN
		oldupdwn% = updwn%
		comp% = 5 ' 5=All
		updwn% = oldupdwn%
		END IF

	 DO WHILE updwn% <> 59

		ctl% = 0: oldupdwn% = updwn%
		SELECT CASE updwn%
		CASE 27: '***** ESC - Descriptions
				ctl% = 1: maxctl% = 1
				WHILE NOT ctl%
				IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
				ON ctl% GOSUB CF1
				GOSUB pgmctl
				WEND

		CASE 60: '***** cmd 2 - Description
				ctl% = 1: maxctl% = 2
				WHILE NOT ctl%
				IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
				ON ctl% GOSUB CF2, CF3
				GOSUB pgmctl
				WEND
		 CASE 61: '*****cmd 3 - Supplier
				ctl% = 1: maxctl% = 1
				WHILE NOT ctl%
				IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
				automgn% = -1
				ON ctl% GOSUB CF4
				automgn% = 0
				GOSUB pgmctl
				WEND
		 CASE 62: '***** cmd 4 - Size line
				ctl% = 1: maxctl% = 4
				WHILE NOT ctl%
				IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
				ON ctl% GOSUB CF5, CF6, CF7, CF8
				GOSUB pgmctl
				WEND
		 CASE 63: '***** cmd 5 - Tax line
				ctl% = 1: maxctl% = 4
				WHILE NOT ctl%
				IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
				ON ctl% GOSUB cf9, cf10, cf11, cf12
				GOSUB pgmctl
				WEND
		 CASE 64: '***** cmd 6 - Cost price
				ctl% = 1: maxctl% = 1
				WHILE NOT ctl%
				IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
				ON ctl% GOSUB CF13
				GOSUB pgmctl
				WEND
		 CASE 65: '***** cmd 7 - Margins
				ctl% = 1: maxctl% = 5
				WHILE NOT ctl%
				IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
				ON ctl% GOSUB cf15, cf16, cf17, cf18, cf19
				GOSUB pgmctl
				WEND
		 CASE 66: '***** cmd 8 - Invoice
				ctl% = 1: maxctl% = 1
				IF comp% = 5 THEN maxctl% = 5
				WHILE NOT ctl%
				IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
				ON ctl% GOSUB cf20, CF21, CF22, CF23, CF24
				GOSUB pgmctl
				WEND
		 CASE 67: '***** cmd 9 - Activity
				ctl% = 1: maxctl% = 2
				IF comp% = 5 THEN maxctl% = 4
				WHILE NOT ctl%
				IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
				ON ctl% GOSUB CF25, CF26
				GOSUB pgmctl
				WEND
		 CASE 68: '***** cmd 10 - SOH
				ctl% = 1: maxctl% = 2
				WHILE NOT ctl%
				IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
				ON ctl% GOSUB CF27, cf28
				GOSUB pgmctl
				WEND
		CASE ELSE
		END SELECT


		CALL recalc
		wrkd$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
		LSET acstk.date$ = FNDY$(wrkd$)

		acstk.no% = rec%
		PUT #3, rec%, acstk
		CALL export(rec%)

	IF oldupdwn% <> 59 THEN          '*****Find next record
		rec% = rec% + 1
		DO WHILE rec% < maxacc%
			GET #3, rec%, acstk
			IF acstk.no% = rec% THEN EXIT DO
			rec% = rec% + 1
			LOOP
		END IF

	IF rec% < maxacc% THEN CALL dsply(rec%, rec4cost%, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!, form$)

	updwn% = oldupdwn%
	LOOP  'Looking for F1.

	 p$ = STR$(rec%): updwn% = 0

X.MULTUPD:
	 RETURN
'////////////////////////////////////////////////////////////////////////////
'>>>>>    L I S T   O F   C H A N G E   M O D U L E S
'////////////////////////////////////////////////////////////////////////////
CF1:    'Search
	LOCATE fl% - 1, 33
	CALL inpnew(acstk.search$, 110!, updwn%, "13,59,60")
RETURN
cf1a:   'EAN
	LOCATE fl% - 1, 47
	A$ = LTRIM$(STR$(acstk.ean13))
	CALL inpnew(A$, 113!, updwn%, "13,59,60")
	IF VAL(A$) > 9300 OR VAL(A$) = 0 THEN acstk.ean13 = VAL(A$)
RETURN

CF2:     'Desc1
	LOCATE fl%, c1% + 1
	: fl% = 4: xl% = 7:
	CALL inpnew(acstk.desc1$, 125!, updwn%, "13,59,60")
RETURN
CF3:    'Desc2
	LOCATE fl%, c1% + 27
	CALL inpnew(acstk.desc2$, 110!, updwn%, "13,59,60")
RETURN
CF4: '>>>>> S U P P L I E R    N U M B E R   <<<<<<<
	CALL sndmsg("Enter supplier number to recall margins")
	wrksuplr$ = acstk.suplr$
	LOCATE fl% + 1, c1% + 1: CALL inpnew(wrksuplr$, 105!, updwn%, "13,59,60")
	CALL sndmsg("")
	IF wrksuplr$ <> acstk.suplr$ THEN
		IF VAL(wrksuplr$) >= 1 AND VAL(wrksuplr$) <= maxsup% THEN
			sno% = VAL(wrksuplr$)
			GET #44, sno%, sup
			wrksuplr$ = sup.search$ + sup.stype$
			END IF

		CALL searchindex(wrksuplr$, 45, ok%)
		IF NOT ok% THEN CALL sndmsg("Supplier not found"): acstk.suplr$ = wrksuplr$: GOTO CF4Pass

		sno% = CVI(supx.wrrn$)
		IF sno% < 1 OR sno% > maxsup% THEN sno% = 1
		GET #44, sno%, sup

		acstk.suplr$ = wrksuplr$
		IF automgn% THEN
			CALL Recallmgn("Y", "Y")
			ELSE
			CALL Recallmgn("N", "Y")
			END IF
		CALL dsply(rec%, rec4cost%, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!, form$)
		END IF
CF4Pass:
	CALL sndmsg("")
RETURN
CF5: '>>>>> S I Z E  <<<<<<<
	 A$ = acstk.size$
	 LOCATE fl% + 2, c1% + 1: CALL inpnew(A$, 103!, updwn%, "13,59,60")
	 IF LEN(A$) > 0 THEN RSET acstk.size$ = A$
RETURN
CF6: '>>>>> U N I T S <<<<<<<
	 LOCATE fl% + 2, c1% + 15: CALL inpnew(acstk.unit$, 102!, updwn%, "13,59,60")
RETURN
CF7: '>>>>> P A C K <<<<<<<
	 apack% = acstk.pack: A$ = STR$(apack%): updwn% = 0
	 LOCATE fl% + 2, c1% + 27: CALL inpnew(A$, 3!, updwn%, "13,59,60")
	 acstk.pack% = VAL(A$)
RETURN
cf7aa: '>>>>> F R O M   F O R M U L A <<<<<<<
	 tnt$ = acstk.form$
	 LOCATE fl% + 3, c1% + 1: CALL inpnew(tnt$, 104!, updwn%, "13,59,60")
	 acstk.form$ = tnt$
	IF tnt$ = "000A" OR tnt$ = "    " THEN
		LOCATE 4, 72
		bulk$ = STR$(acstk.bulk!)
		CALL inpnew(bulk$, 6.2, updwn%, "13,59")
		IF updwn% = 59 THEN ctl% = -2: RETURN
		acstk.bulk! = VAL(bulk$)
		bulk! = VAL(bulk$)
	END IF
	CALL calcbulk(acstk.form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)
RETURN



	 CALL cvt.tnt(tnt$, tnt%, tntf$)
	 CALL calcbulk(tnt$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)

	 LOCATE fl% + 3, c1% + 5: PRINT USING " - \                              \"; tnthed.desc$
RETURN

Cf7A: '>>>>> suplr 4 std cost
	 LOCATE fl% + 4, c1% + 1: CALL inpnew(acstk.suplr4stdcost, 105!, updwn%, "13,59,60")

RETURN

CF7B: '>>>>> search 4 std cost
	 'LOCATE fl% + 4, c1% + 17: CALL inpnew(acstk.search4stdcost, 110!, updwn%, "13,59,60")
RETURN

CF8: '>>>>> T A X   I N C L U D E     (Y/N)  <<<<<<
'    CALL sndmsg("          Tax included Y=Yes, N=No")
'     A$ = acstk.taxinc$
'     IF A$ <> "N" AND A$ <> "Y" THEN A$ = "Y"
'     DO
'        LOCATE fl% + 3, c1% + 47: CALL inpnew(A$, 101!, updwn%, "13,59,60")
'        A$ = UCASE$(A$)
'        LOOP UNTIL A$ = "Y" OR A$ = "N"
'     LSET acstk.taxinc$ = A$
'    CALL sndmsg("")
RETURN
cf9: '>>>>> T A X   C O D E  <<<<<<
	LOCATE fl% + 5, c1% + 1
	 CALL inpnew(acstk.salestaxcde$, 101!, updwn%, "13,59,60,65")
		IF updwn% = 65 THEN CALL dsplymargin: GOTO cf9
RETURN
cf10: '>>>>> D I S T R I B U T O R  D I S C O U N T  C O D E  <<<<<<
	 LOCATE fl% + 8, c2%: CALL inpnew(acstk.distributorcde$, 101!, updwn%, "13,59,60,65")
	 IF updwn% = 65 THEN CALL dsplymargin: GOTO cf10

RETURN
cf11: '>>>>> C O N T R A C T   C O D E  - 1 <<<<<<<
	 LOCATE fl% + 8, c3%
	 CALL inpnew(acstk.disccdeone$, 101!, updwn%, "13,59,60,65")
	 IF updwn% = 65 THEN CALL dsplymargin: GOTO cf11
RETURN
cf12: '>>>>> C O N T R A C T   C O D E  - 2 <<<<<<<
	 LOCATE fl% + 8, c4%
	 CALL inpnew(acstk.disccdetwo$, 101!, updwn%, "13,59,60,65")
	 IF updwn% = 65 THEN CALL dsplymargin: GOTO cf12
RETURN
cf12a: '>>>>> wholesales code
	LOCATE fl% + 8, c5%
	CALL inpnew(acstk.wholesalecde$, 101!, updwn%, "13,59,60,65")
	IF updwn% = 65 THEN CALL dsplymargin: GOTO cf12a
RETURN

CF13: '>>>>> U N I T   C O S T  P R I C E <<<<<<<
	 A$ = STR$(acstk.purcost): updwn% = 0
	 LOCATE fl% + 9, c1%
				 CALL inpnew(A$, 7.2, updwn%, "13,59,60")
	 acstk.purcost = VAL(A$)

RETURN
CF14: '>>>>> D I S T R I B U T O R   P R I C E  <<<<<<
	 A$ = STR$(acstk.distributor): updwn% = 0
	 wrk! = acstk.distributor
	 LOCATE fl% + 9, c2%
				 CALL inpnew(A$, 7.2, updwn%, "13,59,60")
	 acstk.distributor = VAL(A$)
	 IF wrk! <> acstk.distributor THEN
	 acstk.distributorcde$ = "."
	 END IF
RETURN
cf15: '>> RETAIL CDE
	 LOCATE fl% + 14, c1%
	 CALL inpnew(acstk.retailcde$, 101!, updwn%, "13,59,60,65")
	 IF updwn% = 65 THEN CALL dsplymargin: GOTO cf15
RETURN
cf16: '>> COUNTER CDE
	 LOCATE fl% + 14, c2%
	 CALL inpnew(acstk.countercde$, 101!, updwn%, "13,59,60,65")
	 IF updwn% = 65 THEN CALL dsplymargin: GOTO cf16
RETURN
cf17: '>> TRADE CDE
7 LOCATE fl% + 14, c3%
	 CALL inpnew(acstk.tradecde$, 101!, updwn%, "13,59,60,65")
	 IF updwn% = 65 THEN CALL dsplymargin: GOTO cf17
RETURN
cf18: '>> CONTRACT CDE
	 LOCATE fl% + 14, c4%
	 CALL inpnew(acstk.contractcde$, 101!, updwn%, "13,59,60,65")
	 IF updwn% = 65 THEN CALL dsplymargin: GOTO cf18
RETURN
cf19: '>> INDUSTRIAL CDE
	 LOCATE fl% + 14, c5%
	 CALL inpnew(acstk.industrialcde$, 101!, updwn%, "13,59,60,65")
	 IF updwn% = 65 THEN CALL dsplymargin: GOTO cf19
RETURN
cf20: '>> RETAIL
	retail = acstk.retail
	counter = acstk.counter
	trade = acstk.trade
	contract = acstk.contract
	industial = acstk.industrial

	'>Std input
	IF acstk.suplr$ <> "ZZZZA" THEN
		A$ = STR$(acstk.retail)
								LOCATE fl% + 15, c1%: CALL inpnew(A$, 7.2, updwn%, "13,59,60")
		retail! = VAL(A$)
		IF updwn% = 59 THEN RETURN
		IF updwn% = 60 THEN GOTO cf19
		IF retail! <> acstk.retail THEN
			acstk.retail = retail!
			acstk.retailcde$ = "."
		END IF

	IF acstk.countercde$ <> "." THEN GOTO cf20x
	END IF

	LOCATE fl% + 18, 7: PRINT "Overkey....>"

cf20retail:
	IF acstk.retailcde$ = "." THEN
		A$ = STR$(acstk.retail)
		LOCATE fl% + 15, c1%: CALL inpnew(A$, 7.2, updwn%, "13,59,60")
		retail! = VAL(A$)
		IF updwn% = 59 THEN RETURN
		IF updwn% = 60 THEN GOTO cf20
	END IF

cf20counter:
	IF acstk.countercde$ = "." THEN
		A$ = STR$(acstk.counter)
		LOCATE fl% + 15, c2%: CALL inpnew(A$, 7.2, updwn%, "13,59,60")
		counter! = VAL(A$)
		IF updwn% = 59 THEN RETURN
		IF updwn% = 60 THEN GOTO cf20retail
	END IF

cf20trade:
	IF acstk.tradecde$ = "." THEN
		A$ = STR$(acstk.trade)
					LOCATE fl% + 15, c3%: CALL inpnew(A$, 7.2, updwn%, "13,59,60")
		trade! = VAL(A$)
		IF updwn% = 59 THEN RETURN
		IF updwn% = 60 THEN GOTO cf20counter
	END IF

cf20contract:
	IF acstk.contractcde$ = "." THEN
		A$ = STR$(acstk.contract)
		LOCATE fl% + 15, c4%: CALL inpnew(A$, 7.2, updwn%, "13,59,60")
		contract! = VAL(A$)
		IF updwn% = 59 THEN RETURN
		IF updwn% = 60 THEN GOTO cf20trade
	END IF

cf20industrial:
	IF acstk.industrialcde$ = "." THEN
		A$ = STR$(acstk.industrial)
		LOCATE fl% + 15, c5%: CALL inpnew(A$, 7.2, updwn%, "13,59,60")
		industrial! = VAL(A$)
		IF updwn% = 59 THEN RETURN
		IF updwn% = 60 THEN GOTO cf20contract
	END IF

cf20OK:
	A$ = "Y"
	LOCATE fl% + 18, c5% + 10: CALL inpnew(A$, 101!, updwn%, "13,59,60")
	IF updwn% = 60 THEN GOTO cf20industrial
	IF updwn% = 13 THEN ctl% = 28
	IF updwn% = 13 AND UCASE$(A$) = "Y" THEN
		acstk.retailcde$ = "."
		acstk.countercde$ = "."
		acstk.tradecde$ = "."
		acstk.contractcde$ = "."
		acstk.industrialcde$ = "."

		acstk.retail = retail
		acstk.counter = counter
		acstk.trade = trade
		acstk.contract = contract
		acstk.industrial = industrial

		chgflg$ = "Y"
	END IF

cf20x:
	'LOCATE fl% + 17, 7: PRINT CHR$(FNE);

RETURN
CF21: '>> counter

	wrk! = acstk.counter
	 A$ = STR$(wrk!): updwn% = 0
	 LOCATE fl% + 15, c2%
	 CALL inpnew(A$, 7.2, updwn%, "13,59,60")
	 A! = VAL(A$)
	 IF wrk! <> A! THEN
			 acstk.counter = A!
			 acstk.countercde$ = "."
			 chgflg$ = "Y"
			 END IF

RETURN
CF22: '>> trade
	 A$ = STR$(acstk.trade): updwn% = 0
	 LOCATE fl% + 15, c3%
	 CALL inpnew(A$, 7.2, updwn%, "13,59,60")
	 A! = VAL(A$)
	 IF acstk.trade <> A! THEN
			 acstk.trade = VAL(A$)
			 acstk.tradecde$ = "."
			 chgflg$ = "Y"
			 END IF
RETURN
CF23: '>> contract
	 A$ = STR$(acstk.contract): updwn% = 0
	 LOCATE fl% + 15, c4%
	 CALL inpnew(A$, 7.2, updwn%, "13,59,60")
	 A! = VAL(A$)
	 IF acstk.contract <> A! THEN
			 acstk.contract = VAL(A$)
			 acstk.contractcde$ = "."
			 chgflg$ = "Y"
			 END IF
RETURN

CF24: '>> industrial
	 A$ = STR$(acstk.industrial): updwn% = 0
	 LOCATE fl% + 15, c5%
	 CALL inpnew(A$, 7.2, updwn%, "13,59,60")
	 A! = VAL(A$)
	 IF acstk.industrial <> A! THEN
			 acstk.industrial = VAL(A$)
			 acstk.industrialcde$ = "."
			 chgflg$ = "Y"
			 END IF
RETURN

CF25: '>>DG FLAG
	CALL sndmsg("1=Water Based. 2=Solvent LFP.  3=Solvent HFP.  4=Inert.")
	LOCATE fl% + 19, c1% + 3
	CALL inpnew(acstk.dgflag$, 101!, updwn%, "13,59,60")
	CALL sndmsg("")
RETURN
CF26:
	 LOCATE fl% + 19, c2% + 4
	 CALL inpnew(acstk.active$, 101!, updwn%, "13,59,60")
RETURN
CF27:
	 A$ = STR$(acstk.soh): updwn% = 0
	 LOCATE fl% + 19, c3% + 1
	 CALL inpnew(A$, -5!, updwn%, "13,59,60")
	 IF VAL(A$) < 30000 AND VAL(A$) > -30000 THEN
	 acstk.soh = VAL(A$)
	 END IF
RETURN
cf28:
	 A$ = STR$(acstk.sold): updwn% = 0
	 LOCATE fl% + 19, c4%
	 CALL inpnew(A$, 5!, updwn%, "13,59,60")
	 IF VAL(A$) < 30000 AND VAL(A$) > -30000 THEN
	 acstk.sold = VAL(A$)
	 END IF
RETURN

'//////////////////////////////////////////////////////////////////////////////
'>>>>>  FIND THE FIRST RECORD WITH A
'//////////////////////////////////////////////////////////////////////////////
first.alpha.p:
	IF ctl.p$ = "input" THEN
	COLOR 7, 0: LOCATE 2, 23: PRINT "ต                                   ฦอออ": COLOR 2
	LOCATE 2, 25: PRINT "Control...>                     " + CHR$(24); CHR$(25)
	LOCATE 3, 2: PRINT CHR$(FNE)
	LOCATE 2, 36
	CALL inpnew(sa$, 120!, updwn%, "13,72,80,59")
	ctl.p$ = "chain"
	END IF
	IF ctl.p$ = "chain" THEN
		sa$ = UCASE$(sa$)
		LSET qk$ = sa$
		CALL index("CHAIN", ind%, qk$, 7, keyl%)
		IF ind% < 0 AND qk$ < sa$ THEN CALL index("READ ", ind%, qk$, 7, keyl%)
	END IF
	IF ctl.p$ = "read" THEN
		CALL index("READ ", ind%, qk$, 7, keyl%)
	END IF
	IF ctl.p$ = "readp" THEN
	CALL index("READP", ind%, qk$, 7, keyl%)
	END IF
'ANEXT2:
'     A$=MID$(QK$,01,10)'Product code
'     B$=MID$(QK$,11,05)'Supplr+type
'     C$=MID$(QK$,16,03)'Size
'     LOCATE 3,10:COLOR 12,0
'     PRINT USING "p/code|&|  supplier|&|   size|&|   rec.|####|";A$,B$,C$,IND%
'     COLOR 2,0
'
'     X$=INPUT$(1)
'     IF X$="n" THEN CALL INDEX("read ",IND%,QK$,7,KEYL%):GOTO ANEXT2
'     IF X$="p" THEN CALL INDEX("readp",IND%,QK$,7,KEYL%):GOTO ANEXT2
'     IF X$<>CHR$(13) THEN GOTO FIRST.ALPHA.P
	 p$ = STR$(ABS(ind%))
	 updwn% = 13
'    LOCATE 3,2:PRINT CHR$(FNE)
	 RETURN
pgmctl: '***** Pgm ctl processing
	 ctl% = ctl% + 1
	 IF updwn% = 59 THEN ctl% = -1: oldupdwn% = 59
	 IF updwn% = 60 THEN ctl% = ctl% - 2
	 IF ctl% > maxctl% THEN ctl% = -1
	 RETURN
'//////////////////////////////////////////////////////////////////////////
'>>>>>         REPEAT
'//////////////////////////////////////////////////////////////////////////
REPEAT:
'>>>>> Copy REC%ord to next available blank and zero some fields
	 IF rec% < 1 OR rec% > maxacc% THEN GOTO x.repeat
	 IF rec% <> acstk.no% THEN GOTO x.repeat

	 savrec% = rec%: found = 0
	 TOP% = maxacc%
	 IF savrec% = maxacc% THEN
			rec% = 1: GET #3, rec%, acstk
			IF acstk.no% = rec% THEN found = 1: rec% = 32766: TOP% = 0
	 END IF

	 DO WHILE rec% < TOP%
		rec% = rec% + 1
		GET #3, rec%, acstk
		IF acstk.no% <> rec% THEN found = rec%: rec% = 32766
		LOOP

	 IF found = 0 THEN COLOR 14: LOCATE 4, 20: PRINT "No unused records left in file.": COLOR 2: RETURN
	 GET #3, savrec%, acstk
	 rec% = found: p$ = STR$(rec%): cmd9 = 1
	 wrkd$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
	 LSET acstk.date$ = FNDY$(wrkd$)

	 acstk.no% = rec%
	 PUT #3, found, acstk
	 CALL dsply(rec%, rec4cost%, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!, form$)
	 CALL BOX(1, 2, 80, 23, 5, 0, -2)
	 COLOR 2, 0: LOCATE 22, 2: PRINT CHR$(FNE);
	 COLOR 0, 3: LOCATE 25, 1: PRINT SPACE$(80); : LOCATE 25, 4: PRINT "F1-Exit";
	 ctl% = 0: maxctl% = 2
	 WHILE NOT ctl%
		ctl% = ctl% + 1
		ON ctl% GOSUB CF5, CF13
		IF updwn% = 59 THEN ctl% = -1: oldupdwn% = 59
		IF updwn% = 60 AND ctl% = 2 THEN
			 ctla% = 2: maxctl% = 2
			 WHILE NOT ctla%
				ON ctla% GOSUB CF4, CF5
				IF updwn% = 59 THEN
				 ctla% = -1: ctl% = 4: oldupdwn% = 59
				ELSEIF updwn% = 60 THEN
				 ctla% = ctla% - 1: ctl% = 0
				ELSE
				 ctla% = ctla% + 1: ctl% = 1
				END IF
				IF ctla% < 1 OR ctla% > maxctl% THEN ctla% = -1
			 WEND
		ELSEIF updwn% = 60 THEN
			 ctl% = -1
		END IF
		IF ctl% > maxctl% THEN ctl% = -1
	 WEND

	wrkd$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
	LSET acstk.date$ = FNDY$(wrkd$)
	acstk.ean13 = 0


	acstk.no% = rec%
	PUT #3, found, acstk

	CALL BOX(1, 2, 80, 23, 7, 0, -2)
	p$ = STR$(rec%): updwn% = 0

x.repeat:
RETURN

SUB accbrowse (rec%) STATIC
'$INCLUDE: '\tpmanuf\src\accbrow.bi'
END SUB

SUB addrec (rec%) STATIC
	'>>-- Add a record into the file
	'>>-- Finds next empty record to use
	 IF rec% < 1 OR rec% > maxacc% - 1 THEN RETURN
	 'rec% = rec% + 1
	 savrec% = rec%: found% = 0
	 FOR i% = savrec% TO maxacc% - 1
		GET #3, i%, acstk
		IF acstk.no% <> i% THEN found% = i%: EXIT FOR
		NEXT
	 IF found% = 0 THEN CALL sndmsg("No unused records left in file."): GOTO X.addrec

	 'FOR i% = found% TO savrec% + 1 STEP -1
	 ' GET #3, i% - 1, acstk
	 ' acstk.no% = i%
	 ' PUT #3, i%, acstk
	 ' SOUND 18000, 1
	 ' NEXT
	 'rec% = savrec%
	 rec% = found%
	 GET #3, rec%, acstk
	 CALL clrrcdfmt
	 PUT #3, rec%, acstk

	 p$ = STR$(rec%)
X.addrec:

END SUB

SUB calcbulk (form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)
	IF VAL(MID$(form$, 1, 3)) > 0 THEN
		SELECT CASE UCASE$(acstk.unit$)
			CASE "ML":
				acstk.bulk = VAL(acstk.size$) * formbulk / 1000
			CASE "LT":
				acstk.bulk = VAL(acstk.size$) * formbulk
			CASE "LS":
				acstk.bulk = VAL(acstk.size$) * formbulk
			CASE "GM":
				acstk.bulk = VAL(acstk.size$) * formbulkkg / 1000
			CASE "GS":
				acstk.bulk = VAL(acstk.size$) * formbulkkg / 1000
			CASE "KG":
				acstk.bulk = VAL(acstk.size$) * formbulkkg
			CASE ELSE:
		END SELECT
	ELSE
		'acstk.bulk = 0
	END IF



		acstk.bulk = acstk.bulk * pack%


	'IF form$ = "000A" OR form$ = "    " THEN acstk.bulk = xx#(2, 1)

	acstk.rmc = acstk.bulk + pkge! + lid! + label! + pbox! + boxlbl!
	acstk.gpr = (1 - acstk.rmc / xx#(2, 2)) * 100
	acstk.cogs = acstk.bulk + pkge! + lid! + label! + pbox! + boxlbl! + manu!
	acstk.gpc = (1 - acstk.cogs / xx#(2, 2)) * 100
	 'Display values
	 LOCATE 5, 71: PRINT USING "$####.## "; pkge!
	 LOCATE 6, 71: PRINT USING "$####.## "; lid!
	 LOCATE 7, 71: PRINT USING "$####.## "; label!
	 LOCATE 8, 71: PRINT USING "$####.## "; pbox!
	 LOCATE 9, 71: PRINT USING "$####.## "; boxlbl!
	 LOCATE 10, 71: PRINT USING "$####.## "; manu!

	 LOCATE fl%, 71: PRINT USING "$####.## "; bulk!
	 LOCATE fl% + 5, 43: PRINT USING "###.##%$#,###.##"; acstk.gpc; acstk.cogs
	 LOCATE fl% + 6, 43: PRINT USING "###.##%$#,###.##"; acstk.gpr; acstk.rmc
	 COLOR 6
	 LOCATE fl% + 4, 43: PRINT "  Profit   Price"
	 COLOR 2
END SUB

SUB clrrcdfmt STATIC
		sp99$ = SPACE$(99)
		acstk.no% = 0
		acstk.search = sp99$
		acstk.suplr = sp99$
		acstk.search = sp99$
		acstk.desc1 = sp99$
		acstk.desc2 = sp99$
		acstk.suplr = sp99$
		acstk.size = sp99$
		acstk.unit = sp99$
		acstk.pack = 0
		acstk.dgflag = sp99$
		acstk.taxinc = sp99$
		acstk.salestaxcde = sp99$
		acstk.purcost = 0
		acstk.purtax = 0
		acstk.disccdeone = sp99$
		acstk.disccdetwo = sp99$
		acstk.wholesalecost = 0
		acstk.form$ = SPACE$(4)
		'acstk.wholesale-tax = 0
		acstk.retailcde = sp99$
		acstk.countercde = sp99$
		acstk.tradecde = sp99$
		acstk.contractcde = sp99$
		acstk.industrialcde = sp99$
		acstk.distributorcde = sp99$
		acstk.retail = 0
		acstk.counter = 0
		acstk.trade = 0
		acstk.contract = 0
		acstk.industrial = 0
		acstk.distributor = 0
		acstk.suplr4stdcost = SPACE$(5)
		acstk.search4stdcost = SPACE$(10)
		'acstk.retail-tax = 0
		'acstk.counter-tax = 0
		'acstk.trade-tax = 0
		'acstk.contract-tax = 0
		'acstk.industrial-tax = 0
		'acstk.distributor-tax = 0
		acstk.soh = 0
		acstk.sip = 0
		acstk.cogs = 0
		acstk.rmc = 0
		acstk.gpc = 0
		acstk.gpr = 0
		acstk.active = sp99$
		acstk.sold = 0
		acstk.date = sp99$
		acstk.ean13 = 0
		acstk.pkge% = 0
		acstk.label% = 0
		acstk.manu% = 0
		acstk.lid% = 0
		acstk.pbox% = 0
		acstk.boxlbl% = 0
END SUB

SUB costing (rec%, form$)
costing:
	 IF rec% < 1 OR rec% > maxacc% THEN GOTO x.costing
	 GET #3, rec%, acstk
	chgmenu% = 1
	ctl% = 1:  maxctl% = 6
	DO WHILE NOT ctl%  '***** Edit
		IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
		'***** Options
		ON ctl% GOSUB CC1, CC1b, CC2, CC2a, CC2b, CC3

		ctl% = ctl% + 1      '***** Pgm ctl processing
		IF updwn% = 60 THEN ctl% = ctl% - 2
		IF ctl% > maxctl% THEN updwn% = 59
		IF updwn% = 59 THEN ctl% = -1
		CALL calcbulk(acstk.form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)
	LOOP

	wrkd$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
	LSET acstk.date$ = FNDY$(wrkd$)

	PUT #3, rec%, acstk
	CALL export(rec%)
GOTO x.costing:

CC1: ' Packaging (Can)

	LOCATE 5, 66
	pkge$ = STR$(acstk.pkge%)
	CALL inpnew(pkge$, 104!, updwn%, "13,59")
	IF updwn% = 59 THEN ctl% = -2: RETURN
	pkge% = VAL(pkge$)
	IF pkge% = 0 THEN
		 acstk.pkge% = pkge%
		 pkge! = 0
		 LOCATE 5, 71: PRINT USING "$####.## "; pkge!
		 CALL calcbulk(acstk.form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)
		 RETURN
	END IF
	IF pkge% < 1 THEN GOTO CC1Pass
		LOCATE 5, 66: PRINT USING "####"; pkge%
	GET #38, pkge%, msrmat
	IF msrmat.cond$ = "Y" THEN
		acstk.pkge% = pkge%
		pkge! = msrmat.UseCost

		CALL sndmsg("")
	ELSE
CC1Pass:
		CALL sndmsg(" Selection is not marked as Packaging in Raw Material Index ")
		GOTO CC1
	END IF
	CALL calcbulk(acstk.form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)
RETURN

CC1b: ' Packaging2 (Lid)

	LOCATE 6, 66
	lid$ = STR$(acstk.lid%)
	CALL inpnew(lid$, 104!, updwn%, "13,59,60")
	IF updwn% = 59 THEN ctl% = -2: RETURN
	IF updwn% = 60 THEN RETURN
	lid% = VAL(lid$)
	IF lid% = 0 THEN
		 acstk.lid% = lid%
		 lid! = 0
		 LOCATE 6, 71: PRINT USING "$####.## "; lid!
		 CALL calcbulk(acstk.form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)
		 RETURN
	END IF
	IF lid% < 1 THEN GOTO CC1bPass
		LOCATE 6, 66: PRINT USING "####"; lid%
	GET #38, lid%, msrmat
	IF msrmat.cond$ = "Y" THEN
		acstk.lid% = lid%
		lid! = msrmat.UseCost

		CALL sndmsg("")
	ELSE
CC1bPass:
		CALL sndmsg(" Selection is not marked as Packaging in Raw Material Index ")
		GOTO CC1b
	END IF
	CALL calcbulk(acstk.form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)
RETURN

CC2: ' Label

	LOCATE 7, 66
	label$ = STR$(acstk.label%)
	CALL inpnew(label$, 104!, updwn%, "13,59,60")
	IF updwn% = 60 THEN RETURN
	label% = VAL(label$)
	IF label% = 0 THEN
		 acstk.label% = label%
		 label! = 0
		 CALL calcbulk(acstk.form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)
		 RETURN

	END IF

	IF label% < 1 THEN GOTO CC2Pass
		LOCATE 7, 66: PRINT USING "####"; label%
	GET #38, label%, msrmat
	IF msrmat.cond$ = "L" OR msrmat.cond$ = "Y" THEN
		acstk.label% = label%
		label! = msrmat.UseCost

		CALL sndmsg("")
	ELSE
CC2Pass:
		CALL sndmsg(" Selection is not marked as a Label in Raw Material Index ")
		GOTO CC2
	END IF
	CALL calcbulk(acstk.form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)
RETURN

CC2a: ' Box
	LOCATE 8, 66
	pbox$ = STR$(acstk.pbox%)
	CALL inpnew(pbox$, 104!, updwn%, "13,59,60")
	IF updwn% = 60 THEN RETURN
	pbox% = VAL(pbox$)
	IF pbox% = 0 THEN
		 acstk.pbox% = pbox%
		 pbox! = 0
		 LOCATE 7, 71: PRINT USING "$####.## "; pbox!
		 CALL calcbulk(acstk.form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)
		 RETURN
	END IF

	IF pbox% < 1 THEN GOTO CC2aPass
		LOCATE 8, 66: PRINT USING "####"; pbox%
	GET #38, pbox%, msrmat
	IF msrmat.cond$ = "Y" THEN
		acstk.pbox% = pbox%
		pbox! = msrmat.UseCost

		CALL sndmsg("")
	ELSE
CC2aPass:
		CALL sndmsg(" Selection is not marked as a Manufacturing Cost in Raw Material Index ")
		GOTO CC2a
	END IF
	CALL calcbulk(acstk.form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)
RETURN

CC2b: ' Box Label
	LOCATE 9, 66
	boxlbl$ = STR$(acstk.boxlbl%)
	CALL inpnew(boxlbl$, 104!, updwn%, "13,59,60")
	IF updwn% = 60 THEN RETURN
	boxlbl% = VAL(boxlbl$)
	IF boxlbl% = 0 THEN
		 acstk.boxlbl% = boxlbl%
		 boxlbl! = 0
		 LOCATE 7, 71: PRINT USING "$####.## "; boxlbl!
		 CALL calcbulk(acstk.form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)
		 RETURN
	END IF

	IF boxlbl% < 1 THEN GOTO CC2bPass
		LOCATE 9, 66: PRINT USING "####"; boxlbl%
	GET #38, boxlbl%, msrmat
	IF msrmat.cond$ = "Y" OR msrmat.cond$ = "L" THEN
		acstk.boxlbl% = boxlbl%
		boxlbl! = msrmat.UseCost

		CALL sndmsg("")
	ELSE
CC2bPass:
		CALL sndmsg(" Selection is not marked as a Manufacturing Cost in Raw Material Index ")
		GOTO CC2b
	END IF
	CALL calcbulk(acstk.form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)
RETURN


CC3: ' Manufacturing Cost
	LOCATE 10, 66
	manu$ = STR$(acstk.manu%)
	CALL inpnew(manu$, 104!, updwn%, "13,59,60")
	IF updwn% = 60 THEN RETURN
	manu% = VAL(manu$)
	IF manu% = 0 THEN
		 acstk.manu% = manu%
		 manu! = 0
		 LOCATE 10, 71: PRINT USING "$####.## "; manu!
		 CALL calcbulk(acstk.form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)
		 RETURN
	END IF

	IF manu% < 1 THEN GOTO CC3Pass
		LOCATE 10, 66: PRINT USING "####"; manu%
	GET #38, manu%, msrmat
	IF msrmat.cond$ = "M" OR msrmat.cond$ = "L" OR msrmat.cond$ = "Y" THEN
		acstk.manu% = manu%
		manu! = msrmat.UseCost

		CALL sndmsg("")
	ELSE
CC3Pass:
		CALL sndmsg(" Selection is not marked as a Manufacturing Cost in Raw Material Index ")
		GOTO CC3
	END IF
	CALL calcbulk(acstk.form$, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!)
RETURN

x.costing:
IF rec% > 0 THEN
	rec% = rec% - 1
ELSE
	rec% = 1
END IF
END SUB

SUB cvt.tnt (tnt$, tnt%, tntf$)
	tnt$ = UCASE$(tnt$)

	tnt$ = "    " + tnt$: tnt$ = RIGHT$(tnt$, 4)
	digit% = 4
	SELECT CASE MID$(tnt$, digit%, 1)
	CASE "A" TO "Z"
	'CASE "T"
	CASE "0" TO "9": tnt$ = tnt$ + "A": tnt$ = RIGHT$(tnt$, 4)
	CASE ELSE: MID$(tnt$, digit%, 1) = "A"
	END SELECT

	alpha% = 0
	alpha% = 0
	FOR digit% = 1 TO 3
	IF MID$(tnt$, digit%, 1) <> " " THEN
		IF MID$(tnt$, digit%, 1) < "0" OR MID$(tnt$, digit%, 1) > "9" THEN MID$(tnt$, digit%, 1) = " ": alpha% = -1
		END IF
	IF alpha% THEN MID$(tnt$, digit%, 1) = " "
	NEXT

	IF ch.hedx% = 53 THEN MID$(tnt$, 4, 1) = "T" ' Force tints

	tnt% = VAL(MID$(tnt$, 1, 3))
	tntf$ = RIGHT$(tnt$, 1)
	tnt$ = "000" + LTRIM$(STR$(tnt%)): tnt$ = RIGHT$(tnt$, 3) + tntf$

'get tnthedx to make rec%

			maxtnt% = 999

			GET #63, 1, tnthedx
				FOR i% = 1 TO 999
					IF tnt$ = tnthedx.tnta(i%) THEN rec% = tnthedx.rrn(i%): EXIT FOR

				NEXT
'get record
		IF rec% > 0 THEN GET #64, rec%, tnthed
		formbulk = tnthed.alccost!
		IF tnthed.alccost! = 0 THEN formbulk = tnthed.rawcost!
		formname$ = tnthed.desc$
		formbulkkg = formbulk / tnthed.sg
END SUB

SUB Do.delete (rec%) STATIC
	 IF rec% < 1 OR rec% > maxacc% THEN GOTO X.do.delete
	 CALL BOX(1, 2, 80, 24, 14, 0, -2)
	 COLOR 14: LOCATE 3, 28: PRINT "Deletion pending"
	 COLOR 0, 3: LOCATE 25, 1: PRINT SPACE$(80);
	 LOCATE 25, 4: PRINT "F1-Exit"; : LOCATE 25, 65: PRINT " F10-Continue"; : COLOR 2, 0
	 LOCATE 1, 1: CALL inpnew(X$, 0!, updwn%, "59,68")

	 IF updwn% = 68 THEN
		CALL clrrcdfmt
		PUT #3, rec%, acstk
		CALL export(rec%)
	 END IF

	 COLOR 2
	 CALL BOX(1, 2, 80, 23, 7, 0, -2)
	 LOCATE 4, 18: PRINT CHR$(FNE)
	 updwn% = 62

X.do.delete:
END SUB

SUB dsply (rec%, rec4cost%, bulk!, pkge!, lid!, label!, pbox!, boxlbl!, manu!, form$) STATIC
'////////////////////////////////////////////////////////////////////////////
'>>>>>    D I S P L A Y   A  R E C O R D
'////////////////////////////////////////////////////////////////////////////
	'***** List all fields
	COLOR 2, 0
	fl% = 4: xl% = 3:
	c1% = xl% + 13: c2% = xl% + 25: c3% = xl% + 37: c4% = xl% + 49: c5% = xl% + 61
	IF acstk.ean13 < 9300000000000# THEN acstk.ean13 = 0
	IF acstk.ean13 > 9399999000000# THEN acstk.ean13 = 0
	'pkge! = 0
	'label! = 0
	'lid! = 0
	'pbox! = 0
	'boxlbl! = 0
	'manu! = 0
	'pack% = 0
	IF acstk.pack% = 0 THEN
		pack% = 1
	ELSE
		pack% = acstk.pack%
	END IF
	bulk! = acstk.bulk
	form$ = acstk.form$

	LOCATE , , 0'Turn off cursor
	COLOR 6, 0
	LOCATE fl% - 1, 66: PRINT "Costing"
	LOCATE fl% + 4, 43: PRINT "  Profit   Price"
	COLOR 2, 0
	LOCATE fl% - 1
	rmsg$ = "": IF acstk.no% <> rec% THEN rmsg$ = "--"
		LOCATE , xl%: PRINT USING "Stock number> ####\\ Search..>\        \EAN>#############"; rec%; rmsg$; acstk.search$; acstk.ean13
		LOCATE , xl%: PRINT USING "Description.> \                       \-\         \       Bulk>     $####.## "; acstk.desc1$; acstk.desc2$; acstk.bulk
	IF acstk.no% = rec% THEN
		IF acstk.pkge% > 0 THEN
			GET #38, acstk.pkge%, msrmat
			pkge! = msrmat.UseCost * pack%
		ELSE
			pkge! = 0
		END IF

		LOCATE , xl%: PRINT USING "Supplier....> \   \ (####) \                            \ Pkge>####-$####.## "; acstk.suplr$; CVI(sup.sno$); sup.sname$; acstk.pkge%; pkge!
	ELSE
		LOCATE , xl%: PRINT USING "Supplier....> \   \ (####) \                            \ Pkge>####-$####.## "; " "; 0; " "; 0; 0
	END IF
		IF acstk.lid% > 0 THEN
			GET #38, acstk.lid%, msrmat
			lid! = msrmat.UseCost * pack%
		ELSE
			lid! = 0
		END IF

		LOCATE , xl%: PRINT USING "Size........> \ \  Unit...> \\ Pack...> ###               Lid.>####-$####.## "; acstk.size$; acstk.unit$; acstk.pack%; acstk.lid%; lid!

	'From forumla
	CALL cvt.tnt(acstk.form$, tnt%, tntf$)
		IF acstk.label% > 0 THEN
			GET #38, acstk.label%, msrmat
			label! = msrmat.UseCost * pack%
		ELSE
			label! = 0
		END IF
	IF acstk.form$ = "000A" THEN
		LOCATE , xl%: PRINT USING "From Formula> \  \ - \                                  \ Labl>####-$####.## "; "    "; "                              "; acstk.label%; label!
	ELSE
		LOCATE , xl%: PRINT USING "From Formula> \  \ - \                                  \ Labl>####-$####.## "; acstk.form$; formname$; acstk.label%; label!
	END IF
		IF acstk.pbox% > 0 THEN
			GET #38, acstk.pbox%, msrmat
			pbox! = msrmat.UseCost
		ELSE
			pbox! = 0
		END IF

		LOCATE , xl%: PRINT USING "Search Supl.>\    \  Search..>\         \                 Box.>####-$####.## "; acstk.suplr4stdcost$; acstk.search4stdcost$; acstk.pbox%; pbox!
		IF acstk.boxlbl% > 0 THEN
			GET #38, acstk.boxlbl%, msrmat
			boxlbl! = msrmat.UseCost
		ELSE
			boxlbl! = 0
		END IF
	 COLOR 6
	 LOCATE fl% + 4, 43: PRINT "  Profit   Price"
	 COLOR 2

		LOCATE , xl%: PRINT USING "GST Code....> ! GST Rate> ###.##%   COG>###.##%$#,###.##  BoxL>####-$####.## "; acstk.salestaxcde$; xx#(1, 1); acstk.gpc; acstk.cogs; acstk.boxlbl%; boxlbl!

		IF acstk.manu% > 0 THEN
			GET #38, acstk.manu%, msrmat
			manu! = msrmat.UseCost
			ELSE
			manu! = 0
		END IF

		LOCATE , xl%: PRINT USING "Last Updated>                       RMC>###.##%$#,###.##  Manu>####-$####.## "; acstk.gpr; acstk.rmc; acstk.manu%; manu!
	COLOR 3, 0
			LOCATE fl% + 6, xl% + 14: PRINT USING "\      \"; FNDYY$(acstk.date$)

	'pkge! = 0
	'label! = 0
	'lid! = 0
	'pbox! = 0
	'boxlbl! = 0
	'manu! = 0

	COLOR 6, 0
	LOCATE fl% + 7, xl%
	LOCATE , xl%:       PRINT "             Cost....    Distrib.    Disc 1..    Disc 2..    W/Sale.."
	LOCATE fl% + 13, xl%
	LOCATE , xl%:       PRINT "             Retail..    Counter.    Trade...    Contract    Industrial"
	COLOR 6, 0

	LOCATE fl% + 18, xl%:   PRINT "             DG/Flag.    Activity    S.O.H.      Sales.     S.O.O."
	COLOR 2, 0
	LOCATE , xl%: PRINT USING "                !            !     ###,###     ###,###    ###,### "; acstk.dgflag$; acstk.active$; acstk.soh%; acstk.sold%; acstk.soo%

	IF rec4cost% > 0 AND rec4cost% <= maxacc% THEN
		COLOR 10, 0
		LOCATE 5, 64: PRINT USING "From rec.:####"; rec4cost%
		COLOR 2, 0
	ELSE
		'LOCATE 5, 64: PRINT CHR$(FNE);
	END IF


	'>>- BDSPLY
	LOCATE fl% + 8, xl%
	'OCATE , xl%: PRINT USING "Margin......>! ###.##%  "; acstk.salestaxcde$; xx#(1, 1)
	LOCATE , xl%: PRINT USING "Margin......>            ! ###.##%   ! ###.##%   ! ###.##    ! ###.##%"; acstk.distributorcde$; xx#(1, 2); acstk.disccdeone$; 0 - xx#(1, 3); acstk.disccdetwo$; 0 - xx#(1, 4); acstk.wholesalecde$; 0 - xx#(1, 5)
	LOCATE , xl%: PRINT USING "Price.......$#####.##   $#####.##   $#####.##   $#####.##   $#####.##"; xx#(2, 1); xx#(2, 2); xx#(2, 3); xx#(2, 4); xx#(2, 5)
	LOCATE , xl%: PRINT USING "G.S.T.......$#####.##   $#####.##   $#####.##   $#####.##   $#####.##"; xx#(3, 1); xx#(3, 2); xx#(3, 3); xx#(3, 4); xx#(3, 5)
	LOCATE , xl%: PRINT USING "Inv.........$#####.##   $#####.##   $#####.##   $#####.##   $#####.##"; xx#(4, 1); xx#(4, 2); xx#(4, 3); xx#(4, 4); xx#(4, 5)

	LOCATE fl% + 14, xl%
	LOCATE , xl%: PRINT USING "Mrgn........ ! ###.##%   ! ###.##%   ! ###.##%   ! ###.##%   ! ###.##%"; acstk.retailcde$; xx#(5, 1); acstk.countercde$; 0 - xx#(5, 2); acstk.tradecde$; 0 - xx#(5, 3); acstk.contractcde$; 0 - xx#(5, 4); acstk. _
industrialcde$; 0 - xx#(5, 5)
	LOCATE , xl%: PRINT USING "Price.......$#####.##   $#####.##   $#####.##   $#####.##   $#####.## "; xx#(6, 1); xx#(6, 2); xx#(6, 3); xx#(6, 4); xx#(6, 5)
	LOCATE , xl%: PRINT USING "G.S.T.......$#####.##   $#####.##   $#####.##   $#####.##   $#####.## "; xx#(7, 1); xx#(7, 2); xx#(7, 3); xx#(7, 4); xx#(7, 5)
	LOCATE , xl%: PRINT USING "Inv.........$#####.##   $#####.##   $#####.##   $#####.##   $#####.## "; xx#(8, 1); xx#(8, 2); xx#(8, 3); xx#(8, 4); xx#(8, 5)

	IF acstk.no% <> rec% THEN
		y1% = fl% + 8: x1% = xl% + 14
		y2% = fl% + 8 + 4: : x2% = xl% + 70
		CALL BOX(x1%, y1%, x2%, y2%, 0, 0, 0)
		y1% = y1% + 6: x1% = xl% + 13
		y2% = y2% + 6: x2% = xl% + 70
		CALL BOX(x1%, y1%, x2%, y2%, 0, 0, 0)

		LOCATE fl% + 19, xl%: PRINT SPACE$(80 - xl%)
	END IF

	IF acstk.salestaxcde$ = "/" THEN
		COLOR 4, 0: LOCATE 23, 20: PRINT "There is NO G.S.T. on this item": COLOR 2, 0
	END IF

END SUB

SUB dsplymargin STATIC
	 PCOPY 0, 1
	 CALL setup("M A R G I N  S E A R C H")
	 LOCATE 3           '***** List the lot from the array
	 COLOR 6, 0
	 LOCATE 3, 2: PRINT "   Cde  Margin    Cde  Margin    Cde  Margin    Cde  Margin    Cde  Margin   ";
	 LOCATE 4, 2: PRINT " --------------------------------------------------------------------------- ";
	 COLOR 2, 0
	 FOR i% = 1 TO 16
	j% = i% + 16: k% = i% + 32: l% = i% + 48: m% = i% + 64
	LOCATE i% + 5, 2
	PRINT USING "    !   ###.##     !   ###.##     !   ###.##     !   ###.##     !   ###.##"; mc$(i%); mm(i%); mc$(j%); mm(j%); mc$(k%); mm(k%); mc$(l%); mm(l%); mc$(m%); mm(m%);
	IF i% = 1 THEN LOCATE 6, 9: PRINT "no margin";
	 NEXT
	 LOCATE 18, 65: PRINT " {  Future?"
	 LOCATE 19, 65: PRINT " |  Set price"
	 LOCATE 20, 65: PRINT " .  No recalc"

	 COLOR 7, 0
	 COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit";
	 LOCATE 22, 25:
	 CALL inpnew(X$, 0!, updwn%, "13,27,59-60,65")
	 COLOR 2, 0
	 PCOPY 1, 0

END SUB

SUB export (rec%)

GET #3, rec%, acstk

export:
	y$ = STR$(acstk.no%)
	MID$(y$, 1, 1) = "0"
	y$ = "00000000" + y$
	z$ = RIGHT$(y$, 7)

	OPEN ".\export\f" + z$ + ".stk" FOR OUTPUT AS #98

	aa = acstk.no%
	ab$ = acstk.search$
	ac$ = STR$(acstk.ean13)
	ad$ = acstk.desc1$
	ae$ = acstk.desc2$
	af$ = acstk.suplr$
	ag$ = acstk.size$
	ah$ = acstk.unit$
	ai$ = STR$(acstk.pack%)
	aj$ = ""
	ak$ = acstk.dgflag$
	al$ = acstk.form$
	am$ = ""
	an$ = acstk.active$

	'Finalcial Description
	ba$ = acstk.taxinc$
	bb$ = acstk.salestaxcde$
	bc$ = STR$(acstk.purcost)
	bd$ = STR$(acstk.purtax)
	be$ = STR$(acstk.wholesalecost)
	bf$ = acstk.disccdeone$
	bg$ = acstk.disccdetwo$

	bh$ = acstk.wholesalecde$
	bi$ = acstk.retailcde$
	bj$ = acstk.countercde$
	bk$ = acstk.tradecde$
	bl$ = acstk.contractcde$
	bm$ = acstk.industrialcde$
	bn$ = acstk.distributorcde$

	bo$ = STR$(acstk.retail)
	bp$ = STR$(acstk.counter)
	bq$ = STR$(acstk.trade)
	br$ = STR$(acstk.contract)
	bs$ = STR$(acstk.industrial)
	bt$ = STR$(acstk.distributor)

	bu$ = acstk.suplr4stdcost$
	bv$ = acstk.search4stdcost$

	'Stock holding
	ca$ = STR$(acstk.cogs)
	cb$ = STR$(acstk.gpc)
	cc$ = STR$(acstk.rmc)
	cd$ = STR$(acstk.gpr)
	ce$ = STR$(acstk.sip%)
	CF$ = STR$(acstk.soh%)
	cg$ = STR$(acstk.sohv)
	ch$ = STR$(acstk.soo%)
	ci$ = STR$(acstk.sold%)
	cj$ = acstk.date$

'detailed cogs
	da$ = STR$(acstk.bulk)
	DB$ = STR$(acstk.pkge%)
	dc$ = STR$(acstk.lid%)
	dd$ = STR$(acstk.label%)
	de$ = STR$(acstk.pbox%)
	df$ = STR$(acstk.boxlbl%)
	dg$ = STR$(acstk.manu%)
	dh$ = DATE$ + " " + TIME$
IF acstk.no% > 0 THEN
WRITE #98, "F", aa, ab$, ac$, ad$, ae$, af$, ag$, ah$, ai$, ak$, al$, an$, ba$, bb$, bc$, bd$, be$, bf$, bg$, bh$, bi$, bj$, bk$, bl$, bm$, bn$, bo$, bp$, bq$, br$, bs$, bt$, bu$, bv$, ca$, cb$, cc$, cd$, ce$, CF$, cg$, ch$, ci$, cj$, da$, DB$, dc$, _
 dd$, de$, df$, dg$, dh$
END IF
CLOSE #98


END SUB

SUB getrec (rec%, rec4cost%) STATIC
	qk$ = SPACE$(20): keyl% = 20
	GET #3, rec%, acstk
	rec4cost% = 0


	IF RTRIM$(acstk.suplr4stdcost$) > "" AND RTRIM$(acstk.search4stdcost$) > "" THEN
		suplr4stdcost$ = acstk.suplr4stdcost$
		search4stdcost$ = acstk.search4stdcost$
		size4stdcost$ = UCASE$(LTRIM$(RTRIM$(acstk.size$)))

		LSET qk$ = search4stdcost$
		ind% = 0
		CALL index("CHAIN", ind%, qk$, 7, keyl%)
		IF ind% < 0 AND qk$ < search4stdcost$ THEN
			CALL index("READ ", ind%, qk$, 7, keyl%)
		END IF

		IF ind% < 0 THEN ind% = 0 - ind%

		DO WHILE ind% > 0 AND ind% < maxacc%
			GET #3, ind%, acstk
			IF acstk.suplr$ = suplr4stdcost$ THEN
			IF acstk.search$ = search4stdcost$ THEN
			IF UCASE$(LTRIM$(RTRIM$(acstk.size$))) = size4stdcost$ THEN
				rec4cost% = ind%
				GET #3, rec4cost%, acstk4cost
				EXIT DO
			END IF
			END IF
			END IF

			CALL index("READ ", ind%, qk$, 7, keyl%)
		LOOP


		GET #3, rec%, acstk
		'>-Move the data from the cost record
		'------------------------------------
		acstk.retailcde$ = "."  'set don't calc
		acstk.retail = acstk4cost.retail
	END IF

	'>>- Lookup the supplier's name
	IF acstk.suplr$ <> supx.wcde$ THEN
		CALL searchindex(acstk.suplr$, 45, ok%)
		sno% = CVI(supx.wrrn$)
		GET #44, sno%, sup
	END IF

END SUB

SUB globalrecalc STATIC
'DELETED 23/01/2012 - PD
END SUB

FUNCTION perc (code$) STATIC
	 A% = ASC(code$) - 46: IF A% < 1 OR A% > 80 THEN A% = 1
	 pc! = mm(A%)
	 IF code$ = "." THEN pc! = 0
	 perc = pc!
END FUNCTION

'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
'บ    R O U N D   A   C A L C U L A T E D   P R I C E                    บ
'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
SUB priceround (in) STATIC
test = ABS(in): test = test * 100
test = INT(test)
test = test / 100
SELECT CASE test
CASE 0! TO .99: v = 10
CASE 1! TO 1.99: v = 10
CASE 2! TO 4.99: v = 10
CASE 5! TO 9.99: v = 10
CASE 10! TO 19.99: v = 10
CASE 20! TO 49.99: v = 10
CASE 50! TO 99.99: v = 20
CASE 100! TO 499.99: v = 50
CASE 500! TO 999.99: v = 100
CASE 1000! TO 4999.99: v = 500
CASE 5000! TO 9999.99: v = 1000
CASE 10000! TO 49999.99: v = 2000
CASE 50000! TO 99999.99: v = 5000
CASE ELSE: v = 5000
END SELECT
in = in / v
CALL ROUND(in, 2.0001)
in = in * v
CALL ROUND(in, 2.5)
END SUB

SUB recalc STATIC
'////////////////////////////////////////////////////////////////////////////
'*****  RECALC - Recalculate the main cost fields on the screen
'////////////////////////////////////////////////////////////////////////////
	 FOR X% = 1 TO 2
	'>>----------------<<
	'>>-- Hard coded --<<
	'>>----------------<<

	'>>----------------<<
	'>>-- First line --<<
	'>>----------------<<
	'Percentages
	xx#(1, 1) = perc(acstk.salestaxcde$)
	xx#(1, 2) = perc(acstk.distributorcde$)
	xx#(1, 3) = perc(acstk.disccdeone$)
	xx#(1, 4) = perc(acstk.disccdetwo$)
	xx#(1, 5) = perc(acstk.wholesalecde$)

	'>>----------------<<
	'>>-- Second line --<<
	'>>----------------<<
	xx#(2, 1) = acstk.purcost!

	'Distributor cost
	xx#(2, 2) = xx#(2, 1) * ((100 + xx#(1, 2)) / 100)

	'Discount price one
	xx#(2, 3) = xx#(2, 2) * ((100 - xx#(1, 3)) / 100)

	'Discount price two
	xx#(2, 4) = xx#(2, 2) * ((100 - xx#(1, 4)) / 100)

	'Wholesale
	xx#(2, 5) = xx#(2, 2) * ((100 - xx#(1, 5)) / 100)

	CALL round.long(xx#(2, 1), 2.5)
	CALL round.long(xx#(2, 2), 2.5)
	CALL round.long(xx#(2, 3), 2.5)
	CALL round.long(xx#(2, 4), 2.5)
	CALL round.long(xx#(2, 5), 2.5)


	'>>----------------<<
	'>>-- Third line --<<
	'>>----------------<<
	'>>-- Tax
	xx#(3, 1) = xx#(2, 1) * xx#(1, 1) / 100
	xx#(3, 2) = xx#(2, 2) * xx#(1, 1) / 100
	xx#(3, 3) = xx#(2, 3) * xx#(1, 1) / 100
	xx#(3, 4) = xx#(2, 4) * xx#(1, 1) / 100
	xx#(3, 5) = xx#(2, 5) * xx#(1, 1) / 100

	CALL round.long(xx#(3, 1), 2.5)
	CALL round.long(xx#(3, 2), 2.5)
	CALL round.long(xx#(3, 3), 2.5)
	CALL round.long(xx#(3, 4), 2.5)
	CALL round.long(xx#(3, 5), 2.5)

	'>>-----------------<<
	'>>-- Fourth line --<<
	'>>-----------------<<
	'>>- Gate cost
	xx#(4, 1) = xx#(2, 1) + xx#(3, 1)
	xx#(4, 2) = xx#(2, 2) + xx#(3, 2)
	xx#(4, 3) = xx#(2, 3) + xx#(3, 3)
	xx#(4, 4) = xx#(2, 4) + xx#(3, 4)
	xx#(4, 5) = xx#(2, 5) + xx#(3, 5)

	CALL round.long(xx#(4, 1), 2.5)
	CALL round.long(xx#(4, 2), 2.5)
	CALL round.long(xx#(4, 3), 2.5)
	CALL round.long(xx#(4, 4), 2.5)
	CALL round.long(xx#(4, 5), 2.5)

	'>>----------------<<
	'>>-- Fifth line --<<
	'>>----------------<<
	'>>- Percentages
	xx#(5, 1) = perc(acstk.retailcde$)
	xx#(5, 2) = perc(acstk.countercde$)
	xx#(5, 3) = perc(acstk.tradecde$)
	xx#(5, 4) = perc(acstk.contractcde$)
	xx#(5, 5) = perc(acstk.industrialcde$)

	'>>----------------<<
	'>>-- Sixth line --<<
	'>>----------------<<
	'Price
	xx#(6, 1) = xx#(2, 2) * (100 + xx#(5, 1)) / 100
	xx#(6, 2) = xx#(6, 1) * (100 - xx#(5, 2)) / 100
	xx#(6, 3) = xx#(6, 1) * (100 - xx#(5, 3)) / 100
	xx#(6, 4) = xx#(6, 1) * (100 - xx#(5, 4)) / 100
	xx#(6, 5) = xx#(6, 1) * (100 - xx#(5, 5)) / 100


	'>--------------------<
	'>--Manual overkey
	'>--------------------<
	IF acstk.retailcde$ = "." THEN
		xx#(6, 1) = acstk.retail
		xx#(6, 2) = xx#(6, 1) * (100 - xx#(5, 2)) / 100
		xx#(6, 3) = xx#(6, 1) * (100 - xx#(5, 3)) / 100
		xx#(6, 4) = xx#(6, 1) * (100 - xx#(5, 4)) / 100
		xx#(6, 5) = xx#(6, 1) * (100 - xx#(5, 5)) / 100
	END IF
	IF acstk.countercde$ = "." THEN
		xx#(6, 2) = acstk.counter
		xx#(6, 3) = xx#(6, 1) * (100 - xx#(5, 3)) / 100
		xx#(6, 4) = xx#(6, 1) * (100 - xx#(5, 4)) / 100
		xx#(6, 5) = xx#(6, 1) * (100 - xx#(5, 5)) / 100
	END IF
	IF acstk.tradecde$ = "." THEN
		xx#(6, 3) = acstk.trade
		xx#(6, 4) = xx#(6, 1) * (100 - xx#(5, 4)) / 100
		xx#(6, 5) = xx#(6, 1) * (100 - xx#(5, 5)) / 100
	END IF
	IF acstk.contractcde$ = "." THEN
		xx#(6, 4) = acstk.contract
		xx#(6, 5) = xx#(6, 1) * (100 - xx#(5, 5)) / 100
	END IF
	IF acstk.industrialcde$ = "." OR acstk.industrialcde$ = "." THEN
		xx#(6, 5) = acstk.industrial
	END IF

	CALL round.long(xx#(6, 1), 2.5)
'   CALL round.long(xx#(6, 2), 2.5)
'   CALL round.long(xx#(6, 3), 2.5)
'   CALL round.long(xx#(6, 4), 2.5)
'   CALL round.long(xx#(6, 5), 2.5)


	'>>------------------<<
	'>>-- Seventh line --<<
	'>>------------------<<
	'Tax
	xx#(7, 1) = xx#(6, 1) * xx#(1, 1) / 100
	xx#(7, 2) = xx#(6, 2) * xx#(1, 1) / 100
	xx#(7, 3) = xx#(6, 3) * xx#(1, 1) / 100
	xx#(7, 4) = xx#(6, 4) * xx#(1, 1) / 100
	xx#(7, 5) = xx#(6, 5) * xx#(1, 1) / 100

	CALL round.long(xx#(7, 1), 2.5)
	CALL round.long(xx#(7, 2), 2.5)
	CALL round.long(xx#(7, 3), 2.5)
	CALL round.long(xx#(7, 4), 2.5)
	CALL round.long(xx#(7, 5), 2.5)

	'>>-----------------<<
	'>>-- Eighth line --<<
	'>>-----------------<<
	'Invoice $
	xx#(8, 1) = xx#(6, 1) + xx#(7, 1)
	xx#(8, 2) = xx#(6, 2) + xx#(7, 2)
	xx#(8, 3) = xx#(6, 3) + xx#(7, 3)
	xx#(8, 4) = xx#(6, 4) + xx#(7, 4)
	xx#(8, 5) = xx#(6, 5) + xx#(7, 5)

	CALL round.long(xx#(8, 1), 2.5)
	CALL round.long(xx#(8, 2), 2.5)
	CALL round.long(xx#(8, 3), 2.5)
	CALL round.long(xx#(8, 4), 2.5)
	CALL round.long(xx#(8, 5), 2.5)

	'>>------------------------------<<
	'>>-- Move results to the file --<<
	'>>------------------------------<<

	'acstk.distributor-tax = xx#(3, 2)
		 acstk.distributor = xx#(2, 2)

	'acstk.wholesale-tax = xx#(3, 5)
	 acstk.wholesalecost = xx#(2, 5)

	'acstk.retail-tax = xx#(7, 1)
	'acstk.counter-tax = xx#(7, 2)
	'acstk.trade-tax = xx#(7, 3)
	'acstk.contract-tax = xx#(7, 4)
	'acstk.industrial-tax = xx#(7, 5)

			acstk.retail = xx#(6, 1)
			 acstk.counter = xx#(6, 2)
			 acstk.trade = xx#(6, 3)
			acstk.contract = xx#(6, 4)
		acstk.industrial = xx#(6, 5)
NEXT

END SUB

SUB recalcall
PCOPY 0, 1

	CALL setup("R E C A L C   A L L  R E C O R D S")
A$ = "Y"
recalcall0:
	LOCATE 10, 10: PRINT "Recalc all records...............>       "
	LOCATE 10, 44
		CALL inpnew(A$, 101!, updwn%, "13,59")
	A$ = UCASE$(A$)
	IF updwn% = 59 THEN GOTO x.recalcall
	IF A$ = "N" THEN GOTO x.recalcall
	IF A$ = "Y" THEN GOTO recalcall1
GOTO recalcall0
recalcall1:
FOR i% = 1 TO LOF(3) / LEN(acstk)
GET #3, i%, acstk

IF acstk.no% = i% THEN
		bulk! = 0
		label! = 0
		pkge! = 0
		lid! = 0
		pbox! = 0
		boxlbl! = 0
		manu! = 0

		LOCATE 12, 20: PRINT STR$(i%) + " " + acstk.desc1$ + " " + acstk.desc2$
'Get costs of pkge/label/manu/bulk/recalculate
	IF acstk.pkge% > 0 THEN
			GET #38, acstk.pkge%, msrmat
			pkge = msrmat.UseCost
	END IF
	IF acstk.label% > 0 THEN
			GET #38, acstk.label%, msrmat
			label = msrmat.UseCost
	END IF
	IF acstk.manu% > 0 THEN
			GET #38, acstk.manu%, msrmat
			manu = msrmat.UseCost
	END IF

	'From forumla

	IF VAL(MID$(acstk.form$, 1, 3)) > 0 THEN
		CALL cvt.tnt(acstk.form$, tnt%, tntf$)
		SELECT CASE VAL(acstk.size$)
			CASE 250:
			IF acstk.unit = "ML" THEN acstk.bulk = .25 * formbulk
			CASE 500:
				IF acstk.unit = "ML" THEN acstk.bulk = .5 * formbulk
			CASE 1:
				IF acstk.unit = "LT" THEN acstk.bulk = formbulk
			CASE 2:
				IF acstk.unit = "LT" THEN acstk.bulk = 2 * formbulk
			CASE 4:
				IF acstk.unit = "LT" THEN acstk.bulk = 4 * formbulk
			CASE 10:
				IF acstk.unit = "LT" THEN acstk.bulk = 10 * formbulk
			CASE 15:
				IF acstk.unit = "LT" THEN acstk.bulk = 15 * formbulk
			CASE 20:
				IF acstk.unit = "LT" THEN acstk.bulk = 20 * formbulk
			CASE ELSE:
		END SELECT
	ELSE
		acstk.bulk = 0
	END IF

	IF acstk.form$ = "000A" OR acstk.form$ = "    " THEN acstk.bulk = acstk.purcost!

	acstk.rmc = acstk.bulk + pkge + label
	acstk.cogs = acstk.bulk + pkge + label + manu
	IF acstk.distributor > 0 THEN
		acstk.gpr = (1 - acstk.rmc / acstk.distributor) * 100
		acstk.gpc = (1 - acstk.cogs / acstk.distributor) * 100
	ELSE
		acstk.gpr = 0
		acstk.gpc = 0
	END IF

	'LOCATE 13, 20: PRINT acstk.desc1$ + " " + acstk.desc2$

PUT #3, i%, acstk


	y$ = STR$(acstk.no%)
	MID$(y$, 1, 1) = "0"
	y$ = "00000000" + y$
	z$ = RIGHT$(y$, 7)

	OPEN ".\export\f" + z$ + ".stk" FOR OUTPUT AS #98

	aa = acstk.no%
	ab$ = acstk.search$
	ac$ = STR$(acstk.ean13)
	ad$ = acstk.desc1$
	ae$ = acstk.desc2$
	af$ = acstk.suplr$
	ag$ = acstk.size$
	ah$ = acstk.unit$
	ai$ = STR$(acstk.pack%)
	aj$ = ""
	ak$ = acstk.dgflag$
	al$ = acstk.form$
	am$ = ""
	an$ = acstk.active$

	'Finalcial Description
	ba$ = acstk.taxinc$
	bb$ = acstk.salestaxcde$
	bc$ = STR$(acstk.purcost)
	bd$ = STR$(acstk.purtax)
	be$ = STR$(acstk.wholesalecost)
	bf$ = acstk.disccdeone$
	bg$ = acstk.disccdetwo$

	bh$ = acstk.wholesalecde$
	bi$ = acstk.retailcde$
	bj$ = acstk.countercde$
	bk$ = acstk.tradecde$
	bl$ = acstk.contractcde$
	bm$ = acstk.industrialcde$
	bn$ = acstk.distributorcde$

	bo$ = STR$(acstk.retail)
	bp$ = STR$(acstk.counter)
	bq$ = STR$(acstk.trade)
	br$ = STR$(acstk.contract)
	bs$ = STR$(acstk.industrial)
	bt$ = STR$(acstk.distributor)

	bu$ = acstk.suplr4stdcost$
	bv$ = acstk.search4stdcost$

	'Stock holding
	ca$ = STR$(acstk.cogs)
	cb$ = STR$(acstk.gpc)
	cc$ = STR$(acstk.rmc)
	cd$ = STR$(acstk.gpr)
	ce$ = STR$(acstk.sip%)
	CF$ = STR$(acstk.soh%)
	cg$ = STR$(acstk.sohv)
	ch$ = STR$(acstk.soo%)
	ci$ = STR$(acstk.sold%)
	cj$ = acstk.date$

'detailed cogs
	da$ = STR$(acstk.bulk)
	DB$ = STR$(acstk.pkge%)
	dc$ = STR$(acstk.label%)
	dd$ = STR$(acstk.manu%)
	de$ = DATE$ + " " + TIME$

WRITE #98, "F", aa, ab$, ac$, ad$, ae$, af$, ag$, ah$, ai$, ak$, al$, an$, ba$, bb$, bc$, bd$, be$, bf$, bg$, bh$, bi$, bj$, bk$, bl$, bm$, bn$, bo$, bp$, bq$, br$, bs$, bt$, bu$, bv$, ca$, cb$, cc$, cd$, ce$, CF$, cg$, ch$, ci$, cj$, da$, DB$, dc$, _
 dd$, de$

CLOSE #98
END IF
NEXT
x.recalcall:
PCOPY 1, 0
END SUB

SUB Recallmgn (skipask$, override.dots$) STATIC
		A$ = "N"
		IF skipask$ = "Y" THEN A$ = "Y"
		DO
			IF skipask$ <> "Y" THEN
				COLOR 14: LOCATE 23, 3: PRINT "Recall margins..> ":  COLOR 2
				LOCATE 23, 20: CALL inpnew(A$, 101!, updwn%, "13,59")
				END IF
			A$ = UCASE$(A$)
			IF updwn% = 59 THEN A$ = "N"
			LOOP UNTIL A$ = "Y" OR A$ = "N"
		COLOR 2, 0: LOCATE 23, 2: PRINT SPACE$(40);

		wrk.sret$ = sup.sret$
		wrk.sdist$ = sup.sdist$
		wrk.scont1$ = sup.scont1$
		wrk.scont2$ = sup.scont2$
		wrk.countercde$ = sup.countercde$
		wrk.tradecde$ = sup.tradecde$
		wrk.contractcde$ = sup.contractcde$
		wrk.industrialcde$ = sup.industrialcde$
		wrk.wholesalecde$ = sup.wholesalecde$

		IF override.dots$ = "N" THEN
			IF acstk.retailcde$ = "." THEN wrk.sret$ = "."
			IF acstk.distributorcde$ = "." THEN wrk.sdist$ = "."
			IF acstk.disccdeone$ = "." THEN wrk.scont1$ = "."
			IF acstk.disccdetwo$ = "." THEN wrk.scont2$ = "."
			IF acstk.countercde$ = "." THEN wrk.countercde$ = "."
			IF acstk.tradecde$ = "." THEN wrk.tradecde$ = "."
			IF acstk.contractcde$ = "." THEN wrk.contractcde$ = "."
			IF acstk.industrialcde$ = "." THEN wrk.industrialcde$ = "."
			IF acstk.wholesalecde$ = "." THEN wrk.wholesalecde$ = "."
			END IF


		IF A$ = "Y" THEN
			acstk.distributorcde$ = wrk.sdist$
			acstk.disccdeone$ = wrk.scont1$
			acstk.disccdetwo$ = wrk.scont2$
			acstk.wholesalecde$ = wrk.wholesalecde$

			acstk.retailcde$ = wrk.sret$
			acstk.countercde$ = wrk.countercde$
			acstk.tradecde$ = wrk.tradecde$
			acstk.contractcde$ = wrk.contractcde$
			acstk.industrialcde$ = wrk.industrialcde$

			END IF

END SUB

SUB round.long (in#, CUTOFF)

neg% = 1: IF in# < 0 THEN neg% = -1: in# = 0 - in#
IF CUTOFF < 0 THEN CUTOFF = 0 - CUTOFF
IF CUTOFF > 9 THEN CUTOFF = 9.5
dp% = FIX(CUTOFF)
OFFSET = 10 ^ dp%
in# = in# * OFFSET
CUT# = CUTOFF - FIX(CUTOFF)
test! = in# - FIX(in#)
IF test! >= CUT# THEN in# = in# + 1
in# = FIX(in#)
in# = in# / OFFSET
in# = in# * neg%
EXIT SUB

END SUB

SUB Sales
PCOPY 0, 1

	 CALL setup("E X P O R T   S A L E S   I N F O")
	 LOCATE 3
	 COLOR 6, 0
	 LOCATE 3, 2: PRINT "   No.   Description                              Sold ";
	 LOCATE 4, 2: PRINT " ------------------------------------------------------";
	 COLOR 7, 0
	 COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit";
	 COLOR 2, 0
	 LOCATE 17, 14: PRINT "Zero Sales>"
	 LOCATE 18, 14: PRINT "Proceed...>"


	 LOCATE 17, 25:
	 X$ = "N"
	 zerosales% = 0
z.sales:
	 CALL inpnew(X$, 101!, updwn%, "13,59")
		IF updwn% = 59 THEN GOTO x.sales
		IF updwn% = 13 THEN
			IF UCASE$(X$) = "Y" THEN zerosales% = -1
			IF UCASE$(X$) = "N" THEN zerosales% = 0
			GOTO c.sales
		END IF
GOTO z.sales

c.sales:
	 LOCATE 18, 25:
	 X$ = "Y"
s.sales:
	 CALL inpnew(X$, 101!, updwn%, "13,59,60")
	 COLOR 2, 0
		IF updwn% = 59 THEN GOTO x.sales
		IF updwn% = 13 THEN
			IF UCASE$(X$) = "Y" THEN GOTO p.sales
			IF UCASE$(X$) = "N" THEN GOTO x.sales
		END IF
GOTO s.sales

p.sales:

OPEN ".\sales.txt" FOR OUTPUT AS #98
WRITE #98, "No.", "Description", "Colour", "Size", "Unit", "Distributor", "RMC", "SOH", "Sales"

FOR rec% = 1 TO 3500

LOCATE 10, 30: PRINT rec%
GET #3, rec%, acstk

IF acstk.no% > 0 THEN
	'Export info
	A$ = STR$(acstk.no%)
	b$ = acstk.desc1$
	c$ = acstk.desc2$
	d$ = acstk.size$
	e$ = acstk.unit$
	f$ = STR$(acstk.distributor)
	g$ = STR$(acstk.rmc)
	h$ = STR$(acstk.soh%)
	i$ = STR$(acstk.sold%)

	WRITE #98, A$, b$, c$, d$, e$, f$, g$, h$, i$
	 COLOR 2, 0
	 LOCATE 5, 2: PRINT USING " #### \                       \\         \ ##,###"; acstk.no%; acstk.desc1$; acstk.desc2$; acstk.sold%;

	'reset sold to zero
	IF zerosales% = -1 THEN
		acstk.sold% = 0
		PUT #3, rec%, acstk
	END IF

END IF

NEXT

CLOSE #98
x.sales:
PCOPY 1, 0
END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
'>>>>> Lookup index file. Passed skey$. Returns SKEY, 0 if not found. <<<<<
'>>>>> SKEY1, one after insertion place                               <<<<<
	keyin$ = UCASE$(keyin$)
	found% = 0
	max% = LOF(chi%) / 5
	s% = 0: e% = max%

SEARCHAGAIN:
	p% = (e% - s%) / 2 + s%
	IF p% = 0 THEN GOTO X.SEARCHINDEX
	GET #chi%, p%, supx
	IF CVI(supx.wrrn$) = 0 THEN LSET supx.wcde$ = STRING$(99, CHR$(255))
	IF supx.wcde$ = keyin$ THEN found% = -1: GOTO X.SEARCHINDEX
	IF supx.wcde$ < keyin$ AND s% <> p% THEN s% = p%: GOTO SEARCHAGAIN
	IF supx.wcde$ > keyin$ AND e% <> p% THEN e% = p%: GOTO SEARCHAGAIN

X.SEARCHINDEX:
END SUB

SUB trimfile (ok%)
	'Search for the last active record
	lastactive% = 0
	rec3% = 1
	GET #3, rec3%, acstk
	DO WHILE NOT EOF(3) AND rec3% < 32000
	IF acstk.no = rec3% THEN lastactive% = rec3%
	IF rec3% MOD 100 = 0 THEN CALL sndmsg("Searching Record" + STR$(rec3%))
	GET #3, , acstk: rec3% = rec3% + 1
	LOOP
	CALL sndmsg("Last active Record" + STR$(lastactive%))


	OPEN "c:\tpexe\acstk.wrk" FOR RANDOM AS #99 LEN = LEN(acstk)
	rec3% = 1
	GET #3, rec3%, acstk
	DO WHILE NOT EOF(3) AND rec3% <= lastactive%
	IF acstk.no <> rec3% THEN
		acstk.no = 0
		acstk.search = SPACE$(99)
		acstk.desc1 = SPACE$(99)
		acstk.desc2 = SPACE$(99)
		acstk.suplr = SPACE$(99)
		acstk.size = SPACE$(99)
		acstk.unit = SPACE$(99)
		acstk.pack = 0
		acstk.dgflag = SPACE$(99)
		acstk.taxinc = SPACE$(99)
		acstk.salestaxcde = SPACE$(99)
		acstk.purcost = 0
		acstk.purtax = 0
		acstk.disccdeone = SPACE$(99)
		acstk.disccdetwo = SPACE$(99)
		acstk.wholesalecost = 0
		'acstk.wholesale-tax = 0
		acstk.retailcde = SPACE$(99)
		acstk.countercde = SPACE$(99)
		acstk.tradecde = SPACE$(99)
		acstk.contractcde = SPACE$(99)
		acstk.industrialcde = SPACE$(99)
		acstk.distributorcde = SPACE$(99)
		acstk.retail = 0
		acstk.counter = 0
		acstk.trade = 0
		acstk.contract = 0
		acstk.industrial = 0
		acstk.distributor = 0
		acstk.suplr4stdcost = SPACE$(5)
		acstk.search4stdcost = SPACE$(10)

		'acstk.retail-tax = 0
		'acstk.counter-tax = 0
		'acstk.trade-tax = 0
		'acstk.contract-tax = 0
		'acstk.industrial-tax = 0
		'acstk.distributor-tax = 0
		acstk.soh = 0
		acstk.active = SPACE$(99)
		acstk.sold = 0
		acstk.date = SPACE$(99)
		acstk.wholesalecde = SPACE$(99)
		acstk.filler = SPACE$(99)
		END IF

	PUT #99, rec3%, acstk

	IF rec3% MOD 100 = 0 THEN CALL sndmsg("Writing Record" + STR$(rec3%))
	GET #3, , acstk: rec3% = rec3% + 1
	LOOP

	CLOSE #3
	CLOSE #99

	SHELL "COPY c:tpexe\acstk.wrk \tpmanuf\acstk.acf"
	KILL "c:\tpexe\acstk.WRK"

	OPEN "acstk.acf" FOR RANDOM AS #3 LEN = LEN(acstk)

END SUB
