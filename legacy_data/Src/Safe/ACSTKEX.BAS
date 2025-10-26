DECLARE SUB calcbulk (form$)
DECLARE SUB costing (rec%, form$)
DECLARE SUB export (rec%)
DECLARE SUB cvt.tnt (tnt$, tnt%, tntf$)
DECLARE SUB dsply (rec%, rec4cost%)
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
DECLARE SUB Recalc ()
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
	DIM SHARED formname$, formbulk
	DIM SHARED bulk, pkge, label, manu
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
	 
	COLOR 7, 0
	LOCATE 24, 1: PRINT "ศ"; STRING$(78, "อ"); "ผ";
	COLOR 0, 3
	LOCATE 25, 1: PRINT SPACE$(80);
	LOCATE 25, 1: PRINT "F1-Exit F2-U/Menu F3-Price F4-Del F6-Bwse F7-Mgn F8-Ins F9-Rep. F10-Chg. ";
	PRINT CHR$(24); CHR$(25); "-Move";
	COLOR 2, 0
480
	COLOR 7, 0: LOCATE 2, 23: PRINT "ต                              ฦอออออ": COLOR 2
	LOCATE 2, 25: PRINT "Control...> ";
	LOCATE 2, 45: PRINT "(*-Ext.)";
	p$ = ""
	


alast% = LOF(3) / LEN(acstk)
FOR rec% = 1 TO alast%
	CALL export(rec%)
	LOCATE 5, 20: PRINT rec%
NEXT

CLOSE
CALL EXITPGM(apgm$)

CHAIN apgm$

SUB accbrowse (rec%) STATIC
'$INCLUDE: '\tpmanuf\src\accbrow.bi'
END SUB

SUB addrec (rec%) STATIC
	'>>-- Add a record into the file
	 IF rec% < 1 OR rec% > maxacc% - 1 THEN RETURN
	 rec% = rec% + 1
	 savrec% = rec%: found% = 0
	 FOR i% = savrec% + 1 TO maxacc% - 1
		GET #3, i%, acstk
		IF acstk.no% <> i% THEN found% = i%: EXIT FOR
		NEXT
	 IF found% = 0 THEN CALL sndmsg("No unused records left in file."): GOTO X.addrec

	 FOR i% = found% TO savrec% + 1 STEP -1
		GET #3, i% - 1, acstk
		acstk.no% = i%
		PUT #3, i%, acstk
		SOUND 18000, 1
		NEXT
	 rec% = savrec%
	 GET #3, savrec%, acstk
	 CALL clrrcdfmt
	 PUT #3, savrec%, acstk

	 p$ = STR$(savrec%)
X.addrec:

END SUB

SUB calcbulk (form$)
	IF VAL(MID$(form$, 1, 3)) > 0 THEN
		SELECT CASE VAL(acstk.size$)
			CASE 250:
			IF acstk.unit = "ML" THEN acstk.bulk = .25 * formbulk
			CASE 500:
				IF acstk.unit = "ML" THEN acstk.bulk = .5 * formbulk
			CASE 1:
				IF acstk.unit = "LS" THEN acstk.bulk = formbulk
			CASE 2:
				IF acstk.unit = "LS" THEN acstk.bulk = 2 * formbulk
			CASE 4:
				IF acstk.unit = "LS" THEN acstk.bulk = 4 * formbulk
			CASE 10:
				IF acstk.unit = "LS" THEN acstk.bulk = 10 * formbulk
			CASE 15:
				IF acstk.unit = "LS" THEN acstk.bulk = 15 * formbulk
			CASE 20:
				IF acstk.unit = "LS" THEN acstk.bulk = 20 * formbulk
			CASE ELSE:
		END SELECT
	ELSE
		acstk.bulk = 0
	END IF

	acstk.rmc = acstk.bulk + pkge + label
	acstk.gpr = (1 - acstk.rmc / xx#(2, 2)) * 100
	acstk.cogs = acstk.bulk + pkge + label + manu
	acstk.gpc = (1 - acstk.cogs / xx#(2, 2)) * 100
	 'Display values
	 LOCATE 5, 71: PRINT USING "$####.##"; pkge
	 LOCATE 6, 71: PRINT USING "$####.##"; label
	 LOCATE 7, 71: PRINT USING "$####.##"; manu
	 LOCATE fl%, 71: PRINT USING "$####.##"; acstk.bulk
	 LOCATE fl% + 5, 60: PRINT USING "###.##%   $#,###.##"; acstk.gpc; acstk.cogs
	 LOCATE fl% + 6, 60: PRINT USING "###.##%   $#,###.##"; acstk.gpr; acstk.rmc

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

END SUB

SUB costing (rec%, form$)
costing:
	 IF rec% < 1 OR rec% > maxacc% THEN GOTO x.costing
	 GET #3, rec%, acstk
	chgmenu% = 1
	ctl% = 1:  maxctl% = 3
	DO WHILE NOT ctl%  '***** Edit
		IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
		'***** Options
		ON ctl% GOSUB CC1, CC2, CC3

		ctl% = ctl% + 1      '***** Pgm ctl processing
		IF updwn% = 60 THEN ctl% = ctl% - 2
		IF ctl% > maxctl% THEN updwn% = 59
		IF updwn% = 59 THEN ctl% = -1
		CALL calcbulk(acstk.form$)
	LOOP

	wrkd$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
	LSET acstk.date$ = FNDY$(wrkd$)
	
	PUT #3, rec%, acstk
	CALL export(rec%)
GOTO x.costing:

CC1: ' Packaging

	LOCATE 5, 66
	pkge$ = STR$(acstk.pkge%)
	CALL inpnew(pkge$, 104!, updwn%, "13,59")
	IF updwn% = 59 THEN ctl% = -2: RETURN
	pkge% = VAL(pkge$)
	IF pkge% = 0 THEN
		 acstk.pkge% = pkge%
		 pkge = 0
		 LOCATE 5, 71: PRINT USING "$####.##"; pkge
		 RETURN
	END IF
	IF pkge% < 1 THEN GOTO CC1Pass
		LOCATE 5, 66: PRINT USING "####"; pkge%
	GET #38, pkge%, msrmat
	IF msrmat.cond$ = "Y" THEN
		acstk.pkge% = pkge%
		pkge = msrmat.usecost
	
		CALL sndmsg("")
	ELSE
CC1Pass:
		CALL sndmsg(" Selection is not marked as Packaging in Raw Material Index ")
		GOTO CC1
	END IF
RETURN

CC2: ' Label

	LOCATE 6, 66
	label$ = STR$(acstk.label%)
	CALL inpnew(label$, 104!, updwn%, "13,59,60")
	IF updwn% = 60 THEN RETURN
	label% = VAL(label$)
	IF label% = 0 THEN
		 acstk.label% = label%
		 label = 0
 
		 RETURN
	END IF

	IF label% < 1 THEN GOTO CC2Pass
		LOCATE 6, 66: PRINT USING "####"; label%
	GET #38, label%, msrmat
	IF msrmat.cond$ = "L" THEN
		acstk.label% = label%
		label = msrmat.usecost

		CALL sndmsg("")
	ELSE
CC2Pass:
		CALL sndmsg(" Selection is not marked as a Label in Raw Material Index ")
		GOTO CC2
	END IF
RETURN

CC3: ' Manufacturing Cost
	LOCATE 7, 66
	manu$ = STR$(acstk.manu%)
	CALL inpnew(manu$, 104!, updwn%, "13,59,60")
	IF updwn% = 60 THEN RETURN
	manu% = VAL(manu$)
	IF manu% = 0 THEN
		 acstk.manu% = manu%
		 manu = 0
		 LOCATE 7, 71: PRINT USING "$####.##"; manu
		 RETURN
	END IF

	IF label% < 1 THEN GOTO CC3Pass
		LOCATE 7, 66: PRINT USING "####"; manu%
	GET #38, manu%, msrmat
	IF msrmat.cond$ = "M" THEN
		acstk.manu% = manu%
		manu = msrmat.usecost
	
		CALL sndmsg("")
	ELSE
CC3Pass:
		CALL sndmsg(" Selection is not marked as a Manufacturing Cost in Raw Material Index ")
		GOTO CC3
	END IF
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
	CASE "A" TO "F"
	CASE "T"
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
		formbulk = tnthed.rawcost!
		formname$ = tnthed.desc$
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

SUB dsply (rec%, rec4cost%) STATIC
'////////////////////////////////////////////////////////////////////////////
'>>>>>    D I S P L A Y   A  R E C O R D
'////////////////////////////////////////////////////////////////////////////
	'***** List all fields
	COLOR 2, 0
	fl% = 4: xl% = 3:
	c1% = xl% + 13: c2% = xl% + 25: c3% = xl% + 37: c4% = xl% + 49: c5% = xl% + 61
	IF acstk.ean13 < 9300000000000# THEN acstk.ean13 = 0
	IF acstk.ean13 > 9399999000000# THEN acstk.ean13 = 0
	pkge = 0
	label = 0
	manu = 0

	LOCATE , , 0'Turn off cursor
	COLOR 6, 0
	LOCATE fl% - 1, 66: PRINT "Costing"
	LOCATE fl% + 4, 50: PRINT "Basis      Profit     Price"
	COLOR 2, 0
	LOCATE fl% - 1
	rmsg$ = "": IF acstk.no% <> rec% THEN rmsg$ = "--"
		LOCATE , xl%: PRINT USING "Stock number> ####\\ Search..>\        \EAN>#############"; rec%; rmsg$; acstk.search$; acstk.ean13
		LOCATE , xl%: PRINT USING "Description.> \                       \-\         \       Bulk>     $####.##"; acstk.desc1$; acstk.desc2$; acstk.bulk
	IF acstk.no% = rec% THEN
		IF acstk.pkge% > 0 THEN
			GET #38, acstk.pkge%, msrmat
			pkge = msrmat.usecost
		END IF
		LOCATE , xl%: PRINT USING "Supplier....> \   \ (####) \                            \ Pkge>####-$####.##"; acstk.suplr$; CVI(sup.sno$); sup.sname$; acstk.pkge%; pkge
	ELSE
		LOCATE , xl%: PRINT USING "Supplier....> \   \ (####) \                            \ Pkge>####-$####.##"; " "; 0; " "; 0; 0
	END IF
		IF acstk.label% > 0 THEN
			GET #38, acstk.label%, msrmat
			label = msrmat.usecost
		END IF
		LOCATE , xl%: PRINT USING "Size........> \ \  Unit...> \\ Pack...> ###               Labl>####-$####.##"; acstk.size$; acstk.unit$; acstk.pack%; acstk.label%; label

	'From forumla
	CALL cvt.tnt(acstk.form$, tnt%, tntf$)
		IF acstk.manu% > 0 THEN
			GET #38, acstk.manu%, msrmat
			manu = msrmat.usecost
		END IF
	IF acstk.form$ = "000A" THEN
		LOCATE , xl%: PRINT USING "From Formula> \  \ - \                                  \ Manu>####-$####.##"; "    "; "                              "; acstk.manu%; manu
	ELSE
		LOCATE , xl%: PRINT USING "From Formula> \  \ - \                                  \ Manu>####-$####.##"; acstk.form$; formname$; acstk.manu%; manu
	END IF
		LOCATE , xl%: PRINT USING "Search Supl.>\    \  Search..>\         \"; acstk.suplr4stdcost$; acstk.search4stdcost$
		LOCATE , xl%: PRINT USING "GST Code....> !      GST Rate> ###.##%         COGS...>  ###.##%   $#,###.##"; acstk.salestaxcde$; xx#(1, 1); acstk.gpc; acstk.cogs
		LOCATE , xl%: PRINT USING "Last Updated>                                  RMC....>  ###.##%   $#,###.##"; acstk.gpr; acstk.rmc
	COLOR 3, 0
			LOCATE fl% + 6, xl% + 14: PRINT USING "\      \"; FNDYY$(acstk.date$)
	pkge = label = manu = 0
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

IF acstk.no% > 0 THEN
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

	da$ = STR$(acstk.bulk)
	DB$ = STR$(acstk.pkge%)
	dc$ = STR$(acstk.lid%)
	dd$ = STR$(acstk.label%)
	de$ = STR$(acstk.pbox%)
	df$ = STR$(acstk.boxlbl%)
	dg$ = STR$(acstk.manu%)
	dh$ = DATE$ + " " + TIME$

WRITE #98, "F", aa, ab$, ac$, ad$, ae$, af$, ag$, ah$, ai$, ak$, al$, an$, ba$, bb$, bc$, bd$, be$, bf$, bg$, bh$, bi$, bj$, bk$, bl$, bm$, bn$, bo$, bp$, bq$, br$, bs$, bt$, bu$, bv$, ca$, cb$, cc$, cd$, ce$, CF$, cg$, ch$, ci$, cj$, da$, DB$, dc$, _
 dd$, de$, df$, dg$, dh$


CLOSE #98
END IF

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
	CALL setup("R E C A L C   A L L  R E C O R D S")

	supa$ = "*ALL"
global.recalc0:
	LOCATE 10, 10: PRINT "Recalc all records for supplier..>       "
	LOCATE 15, 10: PRINT "Recall supplier margins...>N"
	LOCATE 17, 10: PRINT "Override manually keyed margins...>N"
	LOCATE 19, 10: PRINT "Change tax from..>    to...> "
	LOCATE 10, 44
				CALL inpnew(supa$, 105!, updwn%, "13,59")
	supa$ = UCASE$(supa$)
	IF updwn% = 59 THEN GOTO X.global.recalc

	LOCATE 12, 10: PRINT "                                    "
	IF supa$ <> "*ALL" THEN
		CALL searchindex(supa$, 45, found%)
		IF NOT found% THEN GOTO global.recalc0
		END IF

	sno% = CVI(supx.wrrn$)
	IF sno% < 1 OR sno% > maxsup% THEN sno% = 1
	GET #44, sno%, sup
	IF supa$ = "*ALL" THEN sup.search$ = "*ALL": sup.sname$ = "All Suppliers"
	LOCATE 12, 10: PRINT USING "& - &"; sup.search$; sup.sname$

cfm2:
	Recall$ = "N"
	LOCATE 15, 37
				CALL inpnew(Recall$, 101!, updwn%, "13,59-60")
	Recall$ = UCASE$(Recall$)
	IF updwn% = 59 THEN GOTO X.global.recalc
	IF updwn% = 60 THEN GOTO global.recalc0
cfm3:
	override.dots$ = "N"
	LOCATE 17, 45
				CALL inpnew(override.dots$, 101!, updwn%, "13,59-60")
	override.dots$ = UCASE$(override.dots$)
	IF updwn% = 59 THEN GOTO X.global.recalc
	IF updwn% = 60 THEN GOTO cfm2

cfm4:
	LOCATE 19, 28
				CALL inpnew(override.fromtax$, 101!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO X.global.recalc
	IF updwn% = 60 THEN GOTO cfm3
cfm5:
	LOCATE 19, 38
				CALL inpnew(override.totax$, 101!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO X.global.recalc
	IF updwn% = 60 THEN GOTO cfm4


	rec% = 1
	count% = 0
	oldsup$ = "~~~~~"
	GET #3, rec%, acstk

	DO WHILE NOT EOF(3)
		ok% = -1
		IF acstk.no% <> rec% THEN ok% = 0
		IF supa$ <> "*ALL" AND supa$ <> acstk.suplr$ THEN ok% = 0

		'>> L1 Sup
		supa$ = acstk.suplr$
		IF supa$ <> oldsup$ THEN
			CALL searchindex(supa$, 45, found%)
			sno% = CVI(supx.wrrn$)
			IF NOT found% THEN sno% = 1
			IF sno% < 1 OR sno% > maxsup% THEN sno% = 1
			GET #44, sno%, sup
			LOCATE 13, 10: PRINT USING "& - &"; sup.search$; sup.sname$
			oldsup$ = supa$
			END IF

		'>>- Recall margins
		IF ok% THEN
			IF Recall$ = "Y" THEN
			CALL Recallmgn("Y", override.dots$)
			END IF

		IF override.fromtax$ <> override.totax$ THEN
			IF acstk.salestaxcde$ = override.fromtax$ THEN acstk.salestaxcde$ = override.totax$
			END IF

			CALL Recalc
			PUT #3, rec%, acstk
			CALL export(rec%)
			count% = count% + 1
		END IF

		IF ok% THEN
		IF rec% MOD 20 = 0 THEN CALL sndmsg("Record" + STR$(rec%))
		ELSE
		IF rec% MOD 100 = 0 THEN CALL sndmsg("Record" + STR$(rec%))
		END IF

		GET #3, , acstk: rec% = rec% + 1
		LOOP

		CALL sndmsg(STR$(count%) + " records for " + supa$ + " Complete")
		GOTO global.recalc0
X.global.recalc:
		CALL sndmsg("")

END SUB

FUNCTION perc (code$) STATIC
	 a% = ASC(code$) - 46: IF a% < 1 OR a% > 80 THEN a% = 1
	 pc! = mm(a%)
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

SUB Recalc STATIC
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

SUB Recallmgn (skipask$, override.dots$) STATIC
		a$ = "N"
		IF skipask$ = "Y" THEN a$ = "Y"
		DO
			IF skipask$ <> "Y" THEN
				COLOR 14: LOCATE 23, 3: PRINT "Recall margins..> ":  COLOR 2
				LOCATE 23, 20: CALL inpnew(a$, 101!, updwn%, "13,59")
				END IF
			a$ = UCASE$(a$)
			IF updwn% = 59 THEN a$ = "N"
			LOOP UNTIL a$ = "Y" OR a$ = "N"
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


		IF a$ = "Y" THEN
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

SUB searchindex (keyin$, chi%, found%) STATIC
'>>>>> Lookup index file. Passed skey$. Returns SKEY, 0 if not found. <<<<<
'>>>>> SKEY1, one after insertion place                               <<<<<
	keyin$ = UCASE$(keyin$)
	found% = 0
	max% = LOF(chi%) / 5
	s% = 0: E% = max%

SEARCHAGAIN:
	p% = (E% - s%) / 2 + s%
	IF p% = 0 THEN GOTO X.SEARCHINDEX
	GET #chi%, p%, supx
	IF CVI(supx.wrrn$) = 0 THEN LSET supx.wcde$ = STRING$(99, CHR$(255))
	IF supx.wcde$ = keyin$ THEN found% = -1: GOTO X.SEARCHINDEX
	IF supx.wcde$ < keyin$ AND s% <> p% THEN s% = p%: GOTO SEARCHAGAIN
	IF supx.wcde$ > keyin$ AND E% <> p% THEN E% = p%: GOTO SEARCHAGAIN

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

