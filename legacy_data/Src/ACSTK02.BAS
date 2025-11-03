DECLARE SUB update.repack (updwn%)
DECLARE SUB accbrowse (rec%)
DECLARE SUB add.up.repack (tot.ltact!, tot.torepack!, tot.ltact.taxable!, tot.dtax!, tot.ext!)
DECLARE SUB cf8 (l%, s.elem%, newdata$)
DECLARE SUB chglin (ln%, l%, s.elem%, updwn%)
DECLARE SUB dsply.line (l%, s.elem%)
DECLARE FUNCTION funclimit$ (climit!)
DECLARE SUB init ()
DECLARE SUB load.line (m%, ditem%, ordqty%, invqty%, price!)
DECLARE SUB rightprice (price!)
DECLARE SUB setaudit (n%)

'////////////////////////////////////////////////////////////////////////
'////    S T O C K     R E P A C K
'////////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "ACMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CONST maxlines% = 15 '
	CONST debug% = 0' 'Prevents B/O,INV reducing qty
	CONST GST! = 10  '10%

	DIM SHARED c%(8), in$(maxlines%, 11), rrn%(maxlines%)
	DIM SHARED orders%(1001)
	'---
	'Added to try to set up sub programs ---
	DIM SHARED beg$
	DIM SHARED TaxRate!, DiscRate!
	DIM SHARED startinvnum%, startcrtnum%
	DIM SHARED maxsup%, maxform%, maxrmat%, maxacc%, maxtypes%, maxcus%, maxord%
	DIM SHARED ext.has.changed%, rec50%, ctl%
	DIM SHARED vdisc!, Rate!, discovr!, climit!, ovrPrice!
	DIM SHARED tot.gst!, tot.ext!, tot.allup!
	DIM SHARED skipexit%
	DIM SHARED doc.type$, formtype$, sno%
	DIM SHARED tot.torepack!, tot.ltact, tot.ltinv, tot.dollr, tot.items&
	DIM SHARED newsearch$
	DIM SHARED bysearch$
	DIM SHARED search.key$
	DIM SHARED tot.qty, tot.dtax, Tot.taxvol
	DIM SHARED tot.dg200%, tot.dg60%, tot.dg20%, tot.dg10%, tot.dg4%, tot.dg2%, tot.dg1%, tot.dg850%, tot.dg500%, tot.dg300%, tot.dg250%, tot.dglt!
	DIM SHARED extdisc!, inv.lt.printed!
	DIM SHARED tender$

	DIM SHARED qk$, keyl%, rep$
	DIM SHARED auditfile$(15), naudit%, acstkf$
	keyl% = 20: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)

	'--- Added to set up sub programs ---
	DATA 2,7,10,13,18,56,63,72
	FOR i% = 1 TO 8: READ c%(i%): NEXT
	RESET
	typefields% = -1
	acstkf$ = "..."
	parm$ = ENVIRON$("PARM$")
	parm2$ = ENVIRON$("PARM2$")
	IF parm2$ = "PRE..." THEN acstkf$ = "PRE"

	'$INCLUDE: '\tpmanuf\src\whof.inc'
	'$INCLUDE: '\tpmanuf\src\cusx.inc'
	'$INCLUDE: '\tpmanuf\src\supx.inc'
	'$INCLUDE: '\tpmanuf\src\cus.inc'
	'$INCLUDE: '\tpmanuf\src\ACSTK.INC'
	'$INCLUDE: '\tpmanuf\src\ASAUDIT.INC'
	'$INCLUDE: '\tpmanuf\src\ordhed.inc'
	'$INCLUDE: '\tpmanuf\src\orddet.inc'
	'$INCLUDE: '\tpmanuf\src\ordprt.inc'
	'$INCLUDE: '\tpmanuf\src\msrmat.inc'
	SELECT CASE acstkf$
	CASE "PRE": CALL index("OPEN ", ind%, "acstkx3.pre", 7, keyl%)
	CASE ELSE: CALL index("OPEN ", ind%, "acstkx3.acf", 7, keyl%)
	END SELECT
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	'$INCLUDE: '\tpmanuf\src\pickup.INC'
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxacc% = CVI(msmisc.max5$): maxtypes% = CVI(msmisc.max6$): maxcus% = CVI(msmisc.max7$)
	maxord% = 999

	CALL setaudit(naudit%)
	cashonly$ = "M": auditname$ = auditfile$(naudit%)
	GOSUB OPEN.AUDIT
	CALL init
	CLOSE #8



	'Clear all but the invnum and invnumrec%
	opt% = 0


start:
	CALL setup("S T O C K   R E P A C K")
	btm$ = " F1-Exit."
	COLOR 8, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0

'/////////////////////////////////////////////////////////
'>>>>> M A I N L I N E    O F    E D I T   S E C T I O N
'/////////////////////////////////////////////////////////
mline:

	'>> The supplier/Customer number


	GOSUB load.det
	l% = 1

det:
	GOSUB detail
	opt$ = " ": opt% = 0
exitmenu:

	IF tot.torepack > 0 OR tot.ltact > 0 THEN
		DO

		SELECT CASE skipexit%
		CASE -1: opt$ = "": updwn% = 60
		CASE ELSE
			CALL BOX(17, 4, 63, 14, 6, 9, 1)
			COLOR 3, 1
			LOCATE 5, 28: PRINT "  E X I T    M E N U "
			COLOR 6, 1
			LOCATE , 28: PRINT ""
			LOCATE , 28: PRINT "1....Exit without update."
			LOCATE , 28: PRINT "2....Exit and update."
			LOCATE , 28: PRINT "3....Return to repack."
			LOCATE , 28: PRINT ""
			LOCATE , 28: PRINT "Option...> "
			COLOR 6, 1
			LOCATE 13, 20: PRINT "F1-Exit without update.  F10-Update."
			LOCATE 11, 38: COLOR 2, 0
			CALL inpnew(opt$, 201!, updwn%, "13,59-60,62,68")
		END SELECT
		skipexit% = 0

		opt% = VAL(opt$)


		IF updwn% = 59 THEN opt% = 1
		IF updwn% = 68 THEN opt% = 2
		IF updwn% = 60 THEN opt% = 3


		LOOP UNTIL opt% >= 1 AND opt% <= 3
	END IF

	IF opt% = 3 THEN l% = l% - 1: GOTO det
	IF opt% = 2 THEN
		CALL update.repack(updwn%)
	END IF



mlend:
	CLOSE
	CALL exitpgm(apgm$): CHAIN apgm$
	END

'/////////////////////////////////////////////////////////
'>>>>> CHANGE THE TOTAL INVOICE PRICE & CALC DISC
'/////////////////////////////////////////////////////////
change.price:
change.price0:
		LOCATE 24, 72
		TaxRate! = GST 'Use the constant
		in = (tot.ext - vdisc!) + ((tot.ext - vdisc!) * (TaxRate! / 100))
		CALL ROUND(in, 2.5)
		IF ovrPrice <> -9999 THEN in = ovrPrice

		in$ = STR$(in)
								CALL inpnew(in$, 7.2, updwn%, "13,59")
		in = VAL(in$)
		ovrPrice = in

		TaxRate! = GST 'Use the constant
		CALL add.up.repack(tot.ltact!, tot.torepack!, tot.ltact.taxable!, tot.dtax!, tot.ext!)
RETURN
'////////////////////////////////////////////////////////////
'/////  L O A D    D E T A I L S
'////////////////////////////////////////////////////////////
load.det:
	'>>>> Blank invoice arrays <<<<
	FOR l% = 1 TO maxlines%
		in$(l%, 1) = "0": in$(l%, 2) = "   ": in$(l%, 3) = "": in$(l%, 4) = "": in$(l%, 5) = "": in$(l%, 6) = "0"
		in$(l%, 7) = "0": in$(l%, 8) = "0": in$(l%, 9) = "N/": in$(l%, 10) = "0": in$(l%, 11) = "0"
	NEXT
	tot.ltact = 0      'Litres on order
	tot.ltinv = 0      'Litres invoiced
	tot.dollr = 0
	tot.items& = 0

	hinvq = CVS(ordhed.hinvq$)

	l% = maxlines%
	s% = m% + 1
	FOR m% = s% TO l%
		invqty% = 0
		ordqty% = 0
		ditem% = 0
		CALL load.line(m%, ditem%, ordqty%, invqty%, price!)
	NEXT

	TaxRate! = GST 'Use the constant
	CALL add.up.repack(tot.ltact!, tot.torepack!, tot.ltact.taxable!, tot.dtax!, tot.ext!)
RETURN
	'////////////////////////////////////////////////////////////
	'/////    D E T A I L S
	'////////////////////////////////////////////////////////////
detail:
	CALL setup("S T O C K   R E P A C K")
	btma$ = "F1-Save/Print.    F5-Prices     F6-Browse "
	COLOR 8, 3: LOCATE 25, 1: PRINT btma$;
	IF acstkf$ = "PRE" THEN
		CALL BOX(1, 2, 80, 24, 13, 0, 2)
		CALL SNDMSG("")
		LOCATE 23, 2: COLOR 0, 13: PRINT SPACE$(29); "--PREVIOUS PRICES-- " + SPACE$(29): COLOR 2, 0
		END IF

	'Reset the order to blanks
	TaxRate! = 0 'The GST is not relevent here because the order is empty
	CALL add.up.repack(tot.ltact!, tot.torepack!, tot.ltact.taxable!, tot.dtax!, tot.ext!)
	IF tot.exe! <> 0 THEN BEEP: CALL SNDMSG("Empty order has a dollar value!"): BEEP


	s.elem% = 1'Start at element number 1.
	scrn.pag% = 1
	IF l% < 1 OR l% > maxlines% THEN l% = 1
detail.a:
	IF updwn% = 73 THEN l% = s.elem%'page up
	IF updwn% = 81 THEN l% = s.elem%'page down
	e.elem% = s.elem% + 14
	IF e.elem% > maxlines% THEN e.elem% = maxlines%

	'OLOR 7, 0: LOCATE 2, 2: PRINT "�": LOCATE 2, 79: PRINT "�":
	COLOR 2, 0

	LOCATE 3, 2: COLOR 6, 0: PRINT "Qty. Size   No.  Description                           Price  G.S.T   Value"

	COLOR 2
	LOCATE , 2: COLOR 2, 0: PRINT "컴컴쩡컴컴쩡컴컫컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴쩡컴컴컴쩡컴컴컴쩡컴컴컴컴"
	LOCATE , 2: COLOR 10: PRINT USING "p #"; scrn.pag%: COLOR 2
	sav.l% = l%
	FOR l% = s.elem% TO e.elem%
		CALL dsply.line(l%, s.elem%)
		NEXT
	l% = sav.l%
	LOCATE , 2: COLOR 2, 0: PRINT "컴컴좔컴컴좔컴컨컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴좔컴컴컴좔컴컴컴좔컴컴컴컴"


	LOCATE 6, 2: COLOR 2, 0: PRINT "컴컴좔컴컴좔컴컨컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴좔컴컴컴좔컴컴컴좔컴컴컴컴"
	LOCATE 7, 2: COLOR 6, 0: PRINT "Repack to.                                                                    "
	LOCATE 8, 2: COLOR 2, 0: PRINT "컴컴쩡컴컴쩡컴컫컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴쩡컴컴컴쩡컴컴컴쩡컴컴컴컴"
	'/////////////////////////////////////
	'>>>> Get line entries for the invoice
	'/////////////////////////////////////
	updwn% = 0
	sav.scrn.pag% = scrn.pag%
	DO WHILE updwn% <> 59 AND sav.scrn.pag% = scrn.pag%
		ln% = (l% - s.elem%) MOD 15 + 1: ln% = ln% + 4'+4 Lines from the top of the screen
		IF l% < 2 OR l% > 4 THEN
			CALL chglin(ln%, l%, s.elem%, updwn%)
		END IF
		IF updwn% = 62 THEN EXIT DO   'F4 - Delete
		IF updwn% = 60 THEN l% = l% - 2'F2 - Back one line
		IF updwn% = 72 THEN l% = l% - 2'/\ - Back up one line
		IF updwn% = 73 THEN l% = l% - 16'Page up one screen
		IF updwn% = 81 THEN l% = l% + 16'Page down one screen
		'>>> If the up arrow is hit on the first line jump to the
		'>>> next unused line
		IF updwn% = 72 AND l% = -1 THEN 'end- Find next unused line
				l% = maxlines% + 1
				DO UNTIL VAL(in$(l% - 1, 1)) <> 0
					l% = l% - 1
					IF l% = 1 THEN EXIT DO
					LOOP
				l% = l% - 1
				END IF
		l% = l% + 1
		IF l% > maxlines% THEN l% = maxlines%
		sav.scrn.pag% = scrn.pag%
		SELECT CASE l%
		CASE 31 TO 45: s.elem% = 31: scrn.pag% = 3
		CASE 16 TO 30: s.elem% = 16: scrn.pag% = 2
		CASE ELSE: s.elem% = 1: scrn.pag% = 1
		END SELECT
		IF l% > maxlines% THEN l% = maxlines%' Past end of data
		IF l% < 1 THEN l% = 1              ' Before start of data
		IF l% > s.elem% + 14 THEN l% = s.elem% + 15' Past end of screen
		IF l% < s.elem% THEN l% = s.elem%  ' Before start of screen
		LOOP
	IF sav.scrn.pag% <> scrn.pag% AND updwn% <> 59 THEN GOTO detail.a
RETURN

SUB accbrowse (rec%) STATIC
npgm$ = "dsinv04d"
CALL exitpgm(npgm$)
SHELL npgm$
END SUB

SUB add.up.repack (tot.ltact!, tot.torepack!, tot.ltact.taxable!, tot.dtax!, tot.ext!) STATIC
'/////////////////////////////////////////////////////////////////////////////
'>>>>> Add up the suple order
'/////////////////////////////////////////////////////////////////////////////
add.up.repack:
	'>>> Add up total litres and calc discount $ <<<
	tot.torepack = 0
	tot.toext! = 0

	tot.ltact = 0
	tot.ltact.taxable = 0
	tot.dtax = 0
	tot.ext = 0
	tot.items& = 0

	'To repack
	FOR i% = 1 TO 1
		ltact = 0
		qty = VAL(in$(i%, 1))
		size! = VAL(in$(i%, 2))
		IF in$(i%, 3) = "LT" THEN ltact = qty * size!
		IF in$(i%, 3) = "ML" THEN ltact = qty * size! / 1000
		tot.torepack = ltact
		wrktax = VAL(in$(i%, 7))
		CALL ROUND(wrktax, 2.5)
		wrktax = wrktax * qty
		tot.dtax = tot.dtax + wrktax
		IF wrktax > 0 THEN tot.ltact.taxable = tot.ltact.taxable + ltact
		ext! = VAL(in$(i%, 8))
		tot.ext = tot.ext + ext!
		tot.items& = tot.items& + qty
	NEXT
	tot.toext = tot.ext


	tot.ltact = 0
	tot.ltact.taxable = 0
	tot.dtax = 0
	tot.ext = 0
	tot.items& = 0


	'Add up only the repack portion
	FOR i% = 5 TO maxlines%
		'>>> Add up litres order and actualy on order <<<< in C F 8
		ltact = 0
		qty = VAL(in$(i%, 1))
		size! = VAL(in$(i%, 2))
		IF in$(i%, 3) = "LT" THEN ltact = qty * size!
		IF in$(i%, 3) = "ML" THEN ltact = qty * size! / 1000
		tot.ltact = tot.ltact + ltact
		wrktax = VAL(in$(i%, 7))
		CALL ROUND(wrktax, 2.5)
		wrktax = wrktax * qty
		tot.dtax = tot.dtax + wrktax
		IF wrktax > 0 THEN tot.ltact.taxable = tot.ltact.taxable + ltact
		ext! = VAL(in$(i%, 8))
		tot.ext = tot.ext + ext!
		tot.items& = tot.items& + qty
	NEXT



	'>>> Print out bottom line of the invoice <<<<
	tot.allup = tot.ext - tot.toext

	COLOR 2, 0
	LOCATE 21, 2: PRINT USING "Actual  :##,###                            Sub Total               $$######.##"; tot.torepack!; tot.ext
	LOCATE 22, 2: PRINT USING "Repacked:##,###                                                               "; tot.ltact
	LOCATE 23, 2: PRINT USING "         ##,###                                                               "; tot.ltact - tot.torepack

	COLOR 7, 0
	LOCATE 24, 69: PRINT USING "�$$#####.##�"; tot.allup; : COLOR 2, 0
	COLOR 10, 0:
	LOCATE 24, 70: PRINT USING "$$#####.##"; tot.allup; : COLOR 2, 0
	COLOR 2, 0

	ext.has.changed% = 0

END SUB

SUB cf8 (l%, s.elem%, newdata$)
'/////////////////////////////////////////////////////////////////////////////
'>>>>> EXTENSION
'/////////////////////////////////////////////////////////////////////////////
cf8:
	qty! = VAL(in$(l%, 1))
	size! = VAL(in$(l%, 2))
	price! = VAL(in$(l%, 6))
	tax! = VAL(in$(l%, 7))
	'>-- Stock item (1) is a special case for re-keying sales dockets
	'    Get the docket number in adesc2,tax and price
	IF VAL(in$(l%, 4)) = 1 AND ctl% = 4 THEN
		s.elem% = 1' this is hard coded
		ln% = (l% - s.elem%) MOD 15 + 1: ln% = ln% + 4'+4 Lines from the top of the screen
		LOCATE ln%, c%(5): PRINT acstk.Desc1$; " "; acstk.Desc2$
		dkt$ = acstk.Desc1$
		LOCATE ln%, c%(5)
		CALL inpnew(dkt$, 125!, updwn%, "13,60")
		LSET acstk.Desc1$ = dkt$
		dkt$ = acstk.Desc2$

		LOCATE ln%, c%(5) + 26
		CALL inpnew(dkt$, 110!, updwn%, "13,60")
		LSET acstk.Desc2$ = dkt$
		LOCATE ln%, c%(5): PRINT acstk.Desc1$; " "; acstk.Desc2$
		in$(l%, 5) = acstk.Desc1$ + " " + acstk.Desc2$

		LOCATE ln%, c%(6)
		in$(l%, 6) = STR$(acstk.PurCost!)
								CALL inpnew(in$(l%, 6), 5.2, updwn%, "13")
		price! = VAL(in$(l%, 6))
		END IF
	'>---------------------------------------------------------------
	old.ext! = VAL(in$(l%, 8))
	ext! = qty! * (price! + tax!)
	in$(l%, 8) = STR$(ext!)
	IF old.ext! <> ext! THEN ext.has.changed% = -1

END SUB

SUB chglin (ln%, l%, s.elem%, updwn%)
'///////////////////////////////////////////////////////////////////////
'///// Change an invoice entry line
'///////////////////////////////////////////////////////////////////////
	ctl% = 1: chg = 0: maxctl% = 7
	WHILE NOT ctl%
		'Edit
		IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
		ON ctl% GOSUB cf1, cf2, cf3, cf4, cf5, cf6, cf7
		' Pgm ctl processing
		ctl% = ctl% + 1
		'Mimick F1 if enter is pressed on a blank line
		IF updwn% = 13 AND VAL(in$(l%, 1)) = 0 AND VAL(in$(l%, 4)) = 0 THEN
			ctl% = ctl% - 1'This stays there
			'UPDWN%=59  'This jumps out
			END IF
		IF updwn% = 60 THEN ctl% = ctl% - 2     'F2 - Back one
		IF updwn% = 72 THEN ctl% = -1           'Up Arrow
		IF updwn% = 80 THEN ctl% = -1           'Down Arrow
		IF updwn% = 73 THEN ctl% = -1           'Pg Up
		IF updwn% = 81 THEN ctl% = -1           'Pg Down
		IF updwn% = 60 AND ctl% = 0 THEN ctl% = -1'F2 at first
		IF updwn% = 59 THEN ctl% = -1           'F1 Save
		IF ctl% > maxctl% THEN ctl% = -1        'End of line
		WEND
GOTO x.chglin
'///////////////////////////////////////////////////////////////////////
'///// Detail entry subroutines
'///////////////////////////////////////////////////////////////////////
	'>>>>> QTY <<<<<<<
cf1:
	IF ext.has.changed% THEN
		TaxRate! = GST 'Use the constant
		CALL add.up.repack(tot.ltact!, tot.torepack!, tot.ltact.taxable!, tot.dtax!, tot.ext!)
		END IF
	LOCATE ln%, c%(1)
	in$ = in$(l%, 1)
	old.qty = VAL(in$(l%, 1))
	CALL inpnew(in$, 204!, updwn%, "13,27,59-60,62-64,68,72-73,80-81")
	in$ = UCASE$(in$)
	IF updwn% = 27 THEN
		in$(l%, 1) = "0": in$(l%, 2) = "   ": in$(l%, 3) = "": in$(l%, 4) = "": in$(l%, 5) = "": in$(l%, 6) = "0"
		in$(l%, 7) = "0": in$(l%, 8) = "0": in$(l%, 9) = "N/": in$(l%, 10) = "0": in$(l%, 11) = "0"
		CALL dsply.line(l%, s.elem%)
		TaxRate! = GST 'Use the constant
		CALL add.up.repack(tot.ltact!, tot.torepack!, tot.ltact.taxable!, tot.dtax!, tot.ext!)
		GOTO cf1
		END IF

	IF updwn% = 63 THEN '>> Instant browse of prices
		PCOPY 0, 1
		CALL BOX(4, 9, 77, 15, 3, 0, 1)
		i% = VAL(in$(l%, 4))
		IF i% > 0 AND i% < maxacc% THEN
			GET #3, i%, acstk
			END IF
		COLOR 6, 0
		LOCATE 10, 5: PRINT USING "          Distributor   wholesale  Tax/Inc. ->&"; acstk.Desc1$
		COLOR 2, 0
		LOCATE 11, 5: PRINT USING "Costs.......$#####.##   $#####.##     !     ->####  &"; acstk.distributor; acstk.wholesalecost; acstk.taxinc; acstk.no%; acstk.search$
		COLOR 6, 0
		LOCATE 12, 5: PRINT USING "\          \ Retail..    Counter.    Trade...    Contract    Industrial"; acstk.search$
		COLOR 2, 0
		LOCATE 14, 5: PRINT USING "Inv.........$#####.##   $#####.##   $#####.##   $#####.##   $#####.## "; acstk.retail; acstk.counter; acstk.trade; acstk.contract; acstk.industrial
		CALL inpnew(a$, 0!, updwn%, "13,59")
		PCOPY 1, 0
		GOTO cf1
		END IF
	IF updwn% = 64 THEN
		PCOPY 0, 1
		CALL accbrowse(rec%)
		PCOPY 1, 0
		GOTO cf1
		END IF

	in$(l%, 1) = in$
	newdata$ = "Y": CALL cf8(l%, ctl%, newdata$)
	newsearch$ = "Y"

	IF old.qty <> VAL(in$) THEN
		CALL dsply.line(l%, s.elem%)
		END IF

RETURN
	'>>>>> SIZE <<<<<<<
cf2: LOCATE ln%, c%(2)
	IF VAL(in$(l%, 4)) = 0 THEN check$ = "13,59,60,62" ELSE check$ = ""
	CALL inpnew(in$(l%, 2), 103!, updwn%, check$)
	in$(l%, 2) = UCASE$(in$(l%, 2))
	a$ = "   ": LSET a$ = in$(l%, 2): in$(l%, 2) = a$
	'/////////////////////////////////////////////////////////
	'///// Set up search or non search mode              /////
	bysearch$ = "N"
	IF in$(l%, 2) <> "   " AND VAL(in$(l%, 4)) = 0 THEN bysearch$ = "Y"
	'/////////////////////////////////////////////////////////
RETURN
	'>>>>> UNITS <<<<<<<
cf3: LOCATE ln%, c%(3)
	CALL inpnew(in$(l%, 3), 102!, updwn%, "")
RETURN
	'>>>>> STOCK NUMBER <<<<<<<
cf4: LOCATE ln%, c%(4)
	oldrec% = VAL(in$(l%, 4))
	IF bysearch$ = "Y" OR VAL(in$(l%, 4)) <> 0 THEN
		inpctl$ = ""
		ELSE
		inpctl$ = "13,59,60,62,64"
		END IF

	IF frombrowse% THEN in$(l%, 4) = STR$(rec%): frombrowse% = 0
	CALL inpnew(in$(l%, 4), 4!, updwn%, inpctl$)
		IF updwn% = 64 THEN
			PCOPY 0, 1
			CALL accbrowse(rec%)
			PCOPY 1, 0
			IF rec% < 1 OR rec% > maxacc% THEN rec% = 1
			in$(l%, 4) = "": updwn% = 0: frombrowse% = -1
			GOTO cf4
			END IF

	ditem% = VAL(in$(l%, 4))
	IF ditem% < 1 OR ditem% > maxacc% THEN ditem% = 0
	IF ditem% <> oldrec% OR ditem% = 0 THEN
		price! = -1
		ordqty% = VAL(in$(l%, 1))
		invqty% = 0
		m% = l%
		CALL load.line(m%, ditem%, ordqty%, invqty%, price!)
		CALL dsply.line(l%, s.elem%)
		END IF
RETURN
	'>>>>> DESCRIPTION <<<<<<<
cf5: LOCATE ln%, c%(5)
	IF bysearch$ = "N" THEN
		CALL inpnew(in$(l%, 5), 136!, updwn%, "")

	ELSE '/// Search away ///
		IF newsearch$ = "Y" THEN
			in$ = "": IF frombrowse% = -1 THEN in$ = acstk.search$: frombrowse% = 0
			CALL inpnew(in$, 118!, updwn%, "13,59,60,64,62")
			IF LEN(in$) > 0 THEN
					in$ = UCASE$(in$)
					search.key$ = in$
					COLOR 13, 0
					LOCATE 3, 35: PRINT USING "\                \"; search.key$
					COLOR 2, 0
					END IF
			IF updwn% = 59 THEN GOTO xcf5
			IF updwn% = 60 THEN GOTO xcf5
			IF updwn% = 64 THEN
					PCOPY 0, 1
					CALL accbrowse(rec%)
					PCOPY 1, 0
					IF rec% < 1 OR rec% > maxacc% THEN rec% = 1
					GET #3, rec%, acstk
					frombrowse% = -1
					GOTO cf5
					END IF

			search.dir$ = "N"
			LSET qk$ = search.key$
			CALL index("CHAIN", ind%, qk$, 7, keyl%)
			IF ind% < 0 AND qk$ < search.key$ THEN CALL index("READ ", ind%, qk$, 7, keyl%)
			IF ind% < 0 THEN ind% = 0 - ind%
			END IF
		test = VAL(in$(l%, 2))
		ii% = 0
		FOR i% = LEN(in$(l%, 2)) TO 1 STEP -1
			IF MID$(in$(l%, 2), i%, 1) = " " THEN ii% = ii% + 1
			IF MID$(in$(l%, 2), i%, 1) <> " " THEN EXIT FOR
			NEXT
		testa$ = STRING$(ii%, " ") + in$(l%, 2)
		testa$ = LEFT$(testa$, 3)

		test1$ = MID$(qk$, 1, 1)
		test1$ = MID$(qk$, 1, 1)
		count% = 0
anext3:
		IF MID$(qk$, 16, 3) = testa$ THEN
			test1$ = MID$(qk$, 1, 1)
			IF ind% > 0 AND ind% < maxacc% THEN GET #3, ind%, acstk
			LOCATE ln%, c%(4): PRINT USING "####"; ind%
			LOCATE ln%, c%(5): PRINT acstk.Desc1$; " "; acstk.Desc2$
			LOCATE ln%, c%(5)
			IF newsearch$ = "Y" THEN search.dir$ = CHR$(13)
			'// If its the last line leave it in Next/Previous mode on same line //
			IF newsearch$ = "Y" AND l% = maxlines% THEN search.dir$ = ""
			IF newsearch$ = "N" THEN SOUND 1000, 5: search.dir$ = CHR$(13)
			newsearch$ = "N"
			search.dir$ = UCASE$(search.dir$)
			'CALL INPNEW(  0.0,UPDWN%,"13,p,n")
			END IF
		'// If the first letter in the index changes cancel then search //
		IF test1$ <> MID$(qk$, 1, 1) THEN 'Size not found. Go back to size .
				updwn% = 60
				GOTO xcf5
				END IF
		IF search.dir$ = "N" THEN
				CALL index("READ ", ind%, qk$, 7, keyl%)
				count% = count% + 1: IF count% < 3000 THEN GOTO anext3
				END IF
		IF search.dir$ = "P" THEN
				CALL index("READP", ind%, qk$, 7, keyl%)
				GOTO anext3
				END IF
		IF search.dir$ <> CHR$(13) THEN GOTO cf5'AGAIN
		'// Load details of new record into array ///
			ditem% = ind%
			price! = -1
			ordqty% = VAL(in$(l%, 1))
			invqty% = 0
			m% = l%
			CALL load.line(m%, ditem%, ordqty%, invqty%, price!)
			CALL dsply.line(l%, s.elem%)
			'>>> Place the result of the search in the search key <<<
			search.key$ = acstk.search$
			COLOR 13, 0
			LOCATE 3, 35: PRINT USING "\                \"; search.key$
			COLOR 2, 0
		END IF
xcf5:
RETURN
	'>>>>> PRICE <<<<<<<
cf6: LOCATE ln%, c%(6)
				'CALL inpnew(in$(l%, 6), 5.2!, updwn%, "")
RETURN
	'>>>>> TAX <<<<<<< Calulated in the extention routine
cf7:
RETURN
x.chglin:

END SUB

SUB dsply (sno%, norders%) STATIC
'/////////////////////////////////////////////////////
'>>>>> Get record and display
'/////////////////////////////////////////////////////
dsply:
	IF sno% < 1 OR sno% > maxcus% THEN GOTO x.dsply
	GET #43, sno%, cus
	scur = CVS(cus.scur$): s30 = CVS(cus.s30$): s60 = CVS(cus.s60$): s90 = CVS(cus.s90$)
	sdays% = CVI(cus.sdays$): climit = CVS(cus.climit$)
	sterms = CVS(cus.sterms$): daysmax% = CVI(cus.daysmax$)
	rec50% = VAL(cus.spname$)
	IF rec50% > 0 AND rec50% < 999 THEN
		GET #50, rec50%, PICKUP
		ELSE
		LSET PICKUP.pname1$ = SPACE$(99)
		LSET PICKUP.pname2$ = SPACE$(99)
		LSET PICKUP.pname3$ = SPACE$(99)
		LSET PICKUP.pname4$ = SPACE$(99)
		END IF
	X0% = 5
	COLOR 2, 0
	LOCATE 3, 3: PRINT USING "& & & &&"; LEFT$(cus.sname$, 30); LEFT$(cus.scont$, 25); LEFT$(cus.sphone$, 13); cus.search$; cus.stype$
	COLOR 7: LOCATE 4, 2: PRINT "컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴": COLOR 2
	LOCATE 5, 2: PRINT USING " \                                  \  Deliver:\                            \"; cus.saddr$; PICKUP.pname1$
	LOCATE 6, 2: PRINT USING " \                                  \          \                            \"; cus.saddr2$; PICKUP.pname2$
	LOCATE 7, 2: PRINT USING " \                  \           \   \          \                            \"; cus.suburb$; cus.spcode$; PICKUP.pname3$
	COLOR 6, 0
	LOCATE 5, 41: PRINT "Deliver:"
	COLOR 2, 0

	COLOR 6
	SELECT CASE daysmax%
	CASE 1: LOCATE 8, X0%: PRINT USING "Terms:## day for ##% discount. "; daysmax%; sterms
	CASE ELSE: LOCATE 8, X0%: PRINT USING "Terms:## days for ##% discount."; daysmax%; sterms
	END SELECT

	COLOR 6
	LOCATE , X0%: PRINT "90 Days.     60 Days.     30 Days.     Current.       Total.     C/Limit."
	COLOR 2
	LOCATE , 2: PRINT USING " ###,###.##   ###,###.##   ###,###.##   ###,###.## #,###,###.## "; s90; s60; s30; scur; s90 + s60 + s30 + scur

	IF climit! < 1 THEN COLOR 14
	LOCATE 10, 67: PRINT funclimit(climit!)
	COLOR 2

	COLOR 7: LOCATE , 2: PRINT "컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴": COLOR 2
	CALL BOX(2, 12, 79, 23, 7, 0, 0)
	LOCATE 11, 25: PRINT "Orders found for this customer"
	COLOR 6, 0
	IF norders% < 10 THEN
	LOCATE , 3: PRINT "Num. Type Ord.. Inv..  Order    Dollars. Date....  Order Ref... Due........" 'ajd2
	ELSE
	 LOCATE , 2: PRINT "Num Date. Cust. Ref...... Num Date. Cust. Ref...... Num Date. Cust. Ref......" 'ajd2
	END IF

	COLOR 2, 0

x.dsply:

END SUB

SUB dsply.line (l%, s.elem%) STATIC
'/////////////////////////////////////////////////////////////////
'/////  D I S P L A Y   A  S I N G L E   L I N E   O F   D A T A
'////////////////////////////////////////////////////////////////
		ln% = (l% - s.elem%) MOD 15 + 1: ln% = ln% + 4'+4 Lines from the top of the screen
		COLOR 2, 0
		qty% = VAL(in$(l%, 1))
		IF qty% < 1 OR qty% > 9999 THEN
			LOCATE ln%, 2
			PRINT "    �     �    �                                    �       �       �         "
			ELSE
			qty% = VAL(in$(l%, 1))
			LSET acstk.size$ = in$(l%, 2)
			LSET acstk.unit$ = in$(l%, 3)
			ano% = VAL(in$(l%, 4))
			LSET acstk.Desc1$ = in$(l%, 5)
			LSET acstk.Desc2$ = MID$(in$(l%, 5), LEN(acstk.Desc1$) + 2, 10)
			newdata$ = "N": CALL cf8(l%, s.elem%, newdata$)
			price! = VAL(in$(l%, 6))
			tax! = VAL(in$(l%, 7))
			ext! = VAL(in$(l%, 8))
			'>>> Condition red <<<
			IF ext! <= .01 AND qty% > 0 AND ano% > 0 THEN
				COLOR 4
				SOUND 250, 10
				cond.red$ = "There are zero values on the invoice"
				ELSE
				cond.red$ = ""
				END IF
			a$ = "�" + acstk.size$ + acstk.unit$ + "�"
			b$ = "�" + acstk.Desc1$ + " " + acstk.Desc2$ + "�"
			c$ = "�"
			LOCATE ln%, 2: PRINT USING "####"; qty%
			LOCATE ln%, 6: PRINT a$;
			LOCATE ln%, 13: PRINT USING "####"; ano%
			LOCATE ln%, 17: PRINT b$;
			LOCATE ln%, 55: PRINT USING "####.##"; price!;
			LOCATE ln%, 62: PRINT c$;
			IF tax! <> 0 THEN
			LOCATE ln%, 63: PRINT USING "####.##"; tax!;
			ELSE
			LOCATE ln%, 63: PRINT USING "\     \"; SPACE$(7);
			END IF
			COLOR 2
			LOCATE ln%, 70: PRINT c$;
			LOCATE ln%, 71: PRINT USING "######.##"; ext!
			END IF


END SUB

FUNCTION funclimit$ (climit!)
	wrk$ = "             "
	climit$ = STR$(climit!)
	LSET wrk$ = climit$
	IF climit! = 0 THEN wrk$ = "C.O.D. ONLY  "
	IF climit! = -1 THEN wrk$ = "Invoice value"
	IF climit! = -2 THEN wrk$ = "Invoice plus "
	IF climit! = -3 THEN wrk$ = "Bank Cheque  "
	IF climit! = -4 THEN wrk$ = "Counter Sales"
	IF climit! < -25 THEN wrk$ = "Installment.$"
	IF climit! <= -5 AND climit! >= -25 THEN wrk$ = "Installment.%"
	funclimit$ = wrk$
END FUNCTION

SUB init
'///////////////////////////////////////////////////////////////////////
'///// Setup things
'///////////////////////////////////////////////////////////////////////
init:
	startinvnum% = 1
	startcrtnum% = 1
	beg$ = "yymm"

	GET #8, 1, audit
	adnxtpe% = CVI(MID$(audit.adsname$, 1, 2))
	adprepe% = CVI(MID$(audit.adsname$, 3, 2))
	adlstpe% = CVI(MID$(audit.adsname$, 5, 2))
	IF adlstpe% > 1 AND adlstpe% < adlast% THEN
		startinvnum% = adlstpe%
		startcrtnum% = adlstpe%
		END IF

	beg$ = "mmyy"
	IF adlstpe% > 0 AND adlstpe% <= adlast% THEN
		GET #8, adlstpe%, audit
		beg$ = "mmyy"
		MID$(beg$, 1, 2) = MID$(FNDYY$(audit.addate$), 4, 2)
		MID$(beg$, 3, 2) = MID$(FNDYY$(audit.addate$), 7, 2)
		END IF


END SUB

SUB linkedl (rrn%(), n%, firstrec%, ord%, chd%) STATIC
'$INCLUDE: '\tpmanuf\src\linkedl.bi'
END SUB

SUB load.line (m%, ditem%, ordqty%, invqty%, price!)
'/////////////////////////////////////////////////////////////////
'/////  L O A D   A  S I N G L E   L I N E   O F   D A T A
'/////////////////////////////////////////////////////////////////
load.line:
		'>>> lokup the details
		IF ditem% > 0 AND ditem% < maxacc% THEN
			GET #3, ditem%, acstk
			ano% = acstk.no%
			ELSE
			ano% = 0
			price! = 0
			LSET acstk.size$ = in$(m%, 2)
			LSET acstk.unit$ = SPACE$(99)
			LSET acstk.Desc1$ = SPACE$(99)
			LSET acstk.Desc2$ = SPACE$(99)
			LSET acstk.taxinc$ = SPACE$(99)
			END IF
	'//// Determine which price to use ////
	IF price! THEN
		IF ditem% <> 1 THEN
			CALL rightprice(price!)
			END IF

'        '>- To use the VS number an order number must also be supplied
'        IF MID$(ordhed.hreford$, 1, 2) > "  " THEN
'        IF MID$(ordhed.htaxe$, 1, 2) > "  " THEN
'                tax! = 0
'                END IF
'                END IF

		END IF
		'>>> Add up litres order and actualy on order <<<<
		ltact = 0
		size! = VAL(acstk.size$)
		IF acstk.unit$ = "LT" THEN ltact = ordqty% * size!
		IF acstk.unit$ = "ML" THEN ltact = ordqty% * size! / 1000
		in$(m%, 1) = STR$(ordqty%)
		in$(m%, 2) = acstk.size$
		in$(m%, 3) = acstk.unit$
		in$(m%, 4) = STR$(ano%)
		in$(m%, 5) = acstk.Desc1$ + " " + acstk.Desc2$
		in$(m%, 6) = STR$(price!)' Price is set only the first time in since it cannot change
		in$(m%, 7) = STR$(tax!)
		in$(m%, 8) = STR$(0)
		newdata$ = "Y": CALL cf8(l%, s.elem%, newdata$)
		in$(m%, 9) = acstk.taxinc$
		in$(m%, 10) = STR$(ordqty%)
		in$(m%, 11) = STR$(invqty%)

END SUB

SUB retail.round (price!, round.type$) STATIC
SELECT CASE round.type$
CASE "5 Cents"
	work# = price! * 1: dollars% = FIX(work#)
	work# = (price! - dollars%) * 10: tens% = FIX(work#)
	work# = (price! - dollars% - (tens% / 10)) * 100: digit% = work#
	SELECT CASE digit%
	CASE 0 TO 2: digit% = 0
	CASE 3 TO 5: digit% = 5
	CASE 6 TO 7: digit% = 5
	CASE 8 TO 9: digit% = 10
	CASE -2 TO 0: digit% = 0
	CASE -5 TO -3: digit% = -5
	CASE -7 TO -6: digit% = -5
	CASE -9 TO -8: digit% = -10
	END SELECT
	price! = dollars% + tens% / 10 + digit% / 100
CASE ELSE
END SELECT
END SUB

SUB rightprice (price!) STATIC
'///////////////////////////////////////////
'//// Determine which price to use ////
'///////////////////////////////////////////

	SELECT CASE cus.stype$
	CASE "A": 'Factory Price
				price! = acstk.counter
	CASE "C": 'Contractor Price
				price! = acstk.contract
	CASE "D": 'Distributor Price
				price! = acstk.distributor
	CASE "G": 'Group Price
				price! = acstk.distributor
	CASE "H": 'Hardware Price
				price! = acstk.distributor
	CASE "I": 'Industrial Price
				price! = acstk.industrial
	CASE "M": 'Mitre Ten Price
				price! = acstk.distributor
	CASE "P": 'Painter Price
				price! = acstk.industrial
	CASE "S": 'Special Price
				price! = acstk.trade
	CASE "T": 'Trade Price
				price! = acstk.trade
	CASE "W": 'Best Possible Price
				price! = acstk.wholesalecost
	CASE "Y": 'Group Office Price
				price! = acstk.distributor
	CASE "Z": 'Group store price
				price! = acstk.distributor

	CASE ELSE: 'All Other Codes Are Retail Price
				price! = acstk.retail
	END SELECT

x.rightprice:

END SUB

SUB search.month (rec%, begyymd$)
'//////////////////////////////////////////////////////
'>>>>> SEARCH THE MONTH BY SKIPPING OVER "pe" RECORDS
'//////////////////////////////////////////////////////
search.month:
	adlast% = LOF(8) / 92
	rec% = 1
	GET #8, rec%, audit
	'>>> Use the period end records to jump old months <<<
	DO WHILE audit.addate < begyymd$
		adnxtpe% = CVI(MID$(audit.adsname$, 1, 2))
		adprepe% = CVI(MID$(audit.adsname$, 3, 2))
		adlstpe% = CVI(MID$(audit.adsname$, 5, 2))
		IF adnxtpe% < 1 OR adlstpe% > adlast% THEN EXIT DO
		rec% = adnxtpe%
		GET #8, rec%, audit
		LOOP

END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

SUB setaudit (n%)
'$INCLUDE: '\tpmanuf\src\setaudit.bi'
END SUB

'////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>  UPDATE THE SUPPLIER FILE <<<<<<<<<<<<<<<<<<<<<<
'////////////////////////////////////////////////////////////////////////////
SUB upd.who (chaudit%, chcus%, upd%) STATIC
'$INCLUDE: '\tpmanuf\src\updwho.bi'
END SUB

SUB update.repack (updwn%)
'//////////////////////////////////////////////////////////////////////
'/////   U P D A T E    T H E     O R D E R     F I L E S
'//////////////////////////////////////////////////////////////////////
update.order:
	FOR l% = 1 TO maxlines%
		keyed% = VAL(in$(l%, 1))
		IF l% = 1 THEN
			keyed% = 0 - keyed% 'Reverse the sign iof the first line
		END IF
		'>>>  Update the stock file <<<
		IF keyed% <> 0 THEN
			ditem% = VAL(in$(l%, 4))
			IF ditem% < 1 OR ditem% > maxacc% THEN
				IF ditem% <> 0 THEN SOUND 50, 1'Error
			ELSE
				GET #3, ditem%, acstk
				asoh1 = acstk.soh
				asoh1 = asoh1 + keyed%' Last invoice qty
				acstk.soh = asoh1
				PUT #3, ditem%, acstk
				'IF ditem% = 1 THEN
				'    GET #3, ditem%, acstk
				'    LSET acstk.desc1$ = in$(l%, 5)
				'    LSET acstk.desc2$ = MID$(in$(l%, 5), 27, 10)
				'    acstk.purcost! = VAL(in$(l%, 6))
				'    PUT #3, ditem%, acstk
				'END IF
			 IF l% = 1 THEN
			 ELSE
			 '?? Reduce Can/Label/Manu?
				 IF acstk.pkge% > 0 THEN
					 GET #38, acstk.pkge%, msrmat
					 msrmat.soh! = msrmat.soh! - keyed%
					 msrmat.used! = msrmat.used! + keyed%
					 PUT #38, acstk.pkge%, msrmat
				 END IF
				 IF acstk.label% > 0 THEN
					 GET #38, acstk.label%, msrmat
					 msrmat.soh! = msrmat.soh! - keyed%
					 msrmat.used! = msrmat.used! + keyed%
					 PUT #38, acstk.label%, msrmat
					END IF
					IF acstk.manu% > 0 THEN
					 GET #38, acstk.manu%, msrmat
						msrmat.used! = msrmat.used! + keyed%
						PUT #38, acstk.manu%, msrmat
					END IF
				END IF
			END IF
		END IF
		'>>> End of updating the stock file <<<
	NEXT

END SUB
