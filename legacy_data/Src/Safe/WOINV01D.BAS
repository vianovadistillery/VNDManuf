DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB addtext (edit%)
DECLARE SUB additem (ln%)
DECLARE SUB addcust ()
DECLARE SUB ean13 (in$, dind%)
DECLARE SUB parse (hord%, opt%, cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, invmsg1$, invmsg2$)
DECLARE SUB dsply (sno%, norders%)
DECLARE SUB chglin (ln%, l%, d.elem%, updwn%)
DECLARE SUB prtWO (hord%, opt%, discovr!)
DECLARE SUB getname (tender$, updwn%)
DECLARE SUB addmessage (invmsg1$, invmsg2$, invmsg3$, invmsg4$)
DECLARE SUB update.order (hord%, updwn%)
DECLARE SUB add.bo.msg (updwn%)
DECLARE SUB accbrowse (rec%)
DECLARE SUB cf8 (l%, d.elem%, newdata$)
DECLARE SUB del.order (hord%, n%, clr%, autodel$, thissup$, norders%)
DECLARE SUB dsply.line (l%, d.elem%)
DECLARE SUB dsporders (dspstart%, norders%, custin$)
DECLARE SUB findnext (hord%, norders%, ok%)
DECLARE SUB findorders (thissup$, norders%, hord%)
DECLARE FUNCTION funclimit$ (climit!)
DECLARE SUB get.order.vs (hord%, updwn%)
DECLARE SUB init ()
DECLARE SUB limit.warn (s90!, s60!, s30!, scur!, climit!, updwn%, allow$)
DECLARE SUB linkedl (rrn%(), n%, firstrec%, ord%, chd%)
DECLARE SUB load.line (m%, ditem%, ordqty%, invqty%, Price!)
DECLARE SUB openpslip (opt%)
DECLARE SUB rightprice (Price!)
DECLARE SUB search.month (rec%, begyymd$)
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "DSMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CONST maxlines% = 1
	CONST debug% = 0' 'Prevents B/O,INV reducing qty
	CONST GST! = 10  '10%

	DIM SHARED C%(8), in$(maxlines%, 11), rrn%(maxlines%)
	DIM SHARED txt$(10)
	DIM SHARED orders%(1001)
	'---
	'Added to try to set up sub programs ---
	DIM SHARED mode$, beg$
	DIM SHARED TaxRate!, DiscRate!
	DIM SHARED startinvnum%, startcrtnum%
	DIM SHARED maxsup%, maxform%, maxrmat%, maxacc%, maxtypes%, maxcus%, maxord%
	DIM SHARED ext.has.changed%, rec50%, ctl%, cash%
	DIM SHARED vdisc!, Rate!, discovr!, climit!, ovrPrice!
	DIM SHARED tot.gst!, tot.ext!, tot.allup!
	DIM SHARED skipexit%
	DIM SHARED doc.type$, formtype$, sno%
	DIM SHARED tot.ord!, tot.ltact, tot.ltinv, tot.dollr, tot.items&
	DIM SHARED hord%
	DIM SHARED newsearch$
	DIM SHARED bysearch$
	DIM SHARED search.key$
	DIM SHARED tot.qty, tot.dtax, Tot.taxvol
	DIM SHARED tot.dg200%, tot.dg60%, tot.dg20%, tot.dg10%, tot.dg4%, tot.dg2%, tot.dg1%, tot.dg850%, tot.dg500%, tot.dg300%, tot.dg250%, tot.dglt!
	DIM SHARED extdisc!, inv.lt.printed!
	DIM SHARED tender$
	DIM SHARED invmsg1$, invmsg2$, invmsg3$, invmsg4$
	DIM SHARED qk$, keyl%, rep$
	DIM SHARED ean$
	keyl% = 20: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)

	DATA 2,7,10,13,18,56,63,72
	FOR i% = 1 TO 8: READ C%(i%): NEXT
	RESET
	typefields% = -1
	acstkf$ = "..."
	parm$ = ENVIRON$("PARM$")
	IF VAL(parm$) > 0 THEN pass.getcust% = -1: custin$ = parm$: updwn% = 13

	parm2$ = ENVIRON$("PARM2$")
	IF parm2$ = "PRE..." THEN acstkf$ = "PRE"

		'$INCLUDE: '\tpmanuf\src\whof.inc'
		'$INCLUDE: '\tpmanuf\src\cusx.inc'
		'$INCLUDE: '\tpmanuf\src\supx.inc'
		'$INCLUDE: '\tpmanuf\src\cus.inc'
		'$INCLUDE: '\tpmanuf\src\ACSTK.INC'
		'$INCLUDE: '\tpmanuf\src\ordhed.inc'
		'$INCLUDE: '\tpmanuf\src\orddet.inc'
		'$INCLUDE: '\tpmanuf\src\ordprt.inc'

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


	CALL parse(hord%, opt%, cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, invmsg1$, invmsg2$)
	'Clear all but the invnum and invnumrec%
	hord% = 0: opt% = 0: cash% = 0: tender$ = ""
	chginv# = 0: chginv.rrn% = 0
	thissup$ = "": norders% = 0
	invmsg1$ = "": invmsg2$ = ""


start:
	CALL setup("WORKORDER")
	IF acstkf$ = "PRE" THEN
		CALL box(1, 2, 80, 24, 13, 0, 2)
		CALL SNDMSG("")
		LOCATE 23, 2: COLOR 0, 13: PRINT SPACE$(29); "--PREVIOUS PRICES-- " + SPACE$(29): COLOR 2, 0
		END IF

	btm$ = " F1-Exit.  *-All orders    F6-Browse    F7-Rebuild    F9-Add Cust  F10-New order"
	COLOR 8, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0

getcust:
	LOCATE 2, 22
	COLOR 7, 0: PRINT "ÍÍµ";
	COLOR 2, 0: PRINT "Enter Customer......>"; custin$ + "     ";
	COLOR 7, 0: LOCATE 2, 51: PRINT "ÆÍÍÍÍÍ": COLOR 2, 0
	IF NOT pass.getcust% THEN
		LOCATE 2, 46
		CALL inpnew(custin$, 205!, updwn%, "13,59,64-65,67-68,72,80" + ALT$): GOSUB ALT
		IF MID$(custin$, 1, 1) = " " THEN custin$ = MID$(custin$, 2)
		custin$ = UCASE$(custin$)

		IF updwn% = 59 THEN : ENVIRON "PARM2$=......": CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
		IF updwn% = 65 THEN CLOSE : bpgm$ = "ASBLD02": CALL EXITPGM(bpgm$): CHAIN bpgm$
		END IF
	pass.getcust% = 0

	IF updwn% = 64 THEN
		npgm$ = "dsinv02d"
		CALL EXITPGM(npgm$)
		CLOSE
		CHAIN npgm$
	END IF
	IF updwn% = 13 THEN
			IF VAL(custin$) > 0 THEN
				sno% = VAL(custin$)
				IF sno% < 1 OR sno% > maxsup% THEN sno% = 1
				GET #43, sno%, CUS
				custin$ = cus.search$ + cus.stype$
			END IF
			keyin$ = custin$: chi% = 23
			CALL searchindex(keyin$, chi%, found%)
			IF custin$ = "*" THEN found% = -1
			IF found% THEN sno% = CVI(supx.wrrn$): CALL SNDMSG("")
			IF NOT found% THEN
				'>-Crude search (for new customers)
					sno% = 1
					GET #43, sno%, CUS
					DO WHILE NOT EOF(43)
						IF CVI(cus.sno) = sno% AND custin$ = cus.search$ + cus.stype$ THEN
							found% = -1
							EXIT DO
						END IF
					GET #43, , CUS: sno% = sno% + 1
					LOOP
			END IF


			IF NOT found% THEN
					msg$ = "          Customer not found.  Use the Up/Down arrows to locate."
					CALL SNDMSG(msg$)
					COLOR 14, 0: LOCATE 24, 4: PRINT msg$;
					sno% = CVI(supx.wrrn$): custin$ = supx.wcde$
					SOUND 250, 1
					END IF
			END IF

	IF updwn% = 67 THEN 'Add cust
			CALL addcust
			custin$ = cus.search$ + cus.stype$
			pass.getcust% = -1
			updwn% = 13
	END IF




	IF updwn% = 72 THEN 'Up arrow
		p% = LOC(chi%): p% = p% - 1: IF p% < 1 THEN p% = 1
		GET #chi%, p%, supx
		custin$ = supx.wcde$: updwn% = 13
		keyin$ = custin$: chi% = 23
		CALL searchindex(keyin$, chi%, found%)
		IF found% THEN sno% = CVI(supx.wrrn$)
		found% = 0
		END IF

	IF updwn% = 80 THEN 'Down arrow
		p% = LOC(chi%): p% = p% + 1
		GET #chi%, p%, supx
		custin$ = supx.wcde$: updwn% = 13
		keyin$ = custin$: chi% = 23
		CALL searchindex(keyin$, chi%, found%)
		IF found% THEN sno% = CVI(supx.wrrn$)
		found% = 0
		END IF


	IF sno% < 1 OR sno% > maxcus% THEN GOTO getcust
		CALL dsply(sno%, norders%)
		thissup$ = cus.search$ + cus.stype$
		IF custin$ = "*" THEN thissup$ = "*    "
		CALL findorders(thissup$, norders%, hord%)
		CALL dsply(sno%, norders%)
		dspstart% = 1
		CALL dsporders(dspstart%, norders%, custin$)
	clr% = 0
	DO UNTIL updwn% = 59
	IF clr% = 0 THEN in$ = ""
	IF clr% = 1 OR clr% = 3 THEN
		CALL setup("INVOICE/PICK SLIP")
		COLOR 8, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
		IF acstkf$ = "PRE" THEN
			CALL box(1, 2, 80, 24, 13, 0, 2)
			CALL SNDMSG("")
			LOCATE 23, 2: COLOR 0, 13: PRINT SPACE$(29); "--PREVIOUS PRICES-- " + SPACE$(29): COLOR 2, 0
			END IF

		CALL dsply(sno%, norders%)
		dspstart% = 1
		CALL dsporders(dspstart%, norders%, custin$)
		IF clr% = 3 THEN clr% = 0: EXIT DO
		clr% = 0
		END IF
	IF clr% = 2 THEN CALL box(2, 3, 79, 21, 7, 0, 0): clr% = 0
	IF emsg$ <> "" THEN COLOR 14, 0: LOCATE 21, 2: PRINT emsg$; CHR$(FNE): emsg$ = "": COLOR 2: updwn% = 59
	COLOR 2, 0
	IF NOT found% THEN GOTO getcust
getordnum:
	IF updwn% <> 68 THEN

		LOCATE 24, 37
		COLOR 7, 0: PRINT "ÍÍµ";
		COLOR 2, 0: PRINT "Enter order number..>     ";
		COLOR 7, 0: PRINT "ÆÍ"; : COLOR 2, 0
		IF norders% > 33 THEN
			COLOR 7, 0: PRINT "ÍÍµ";
			COLOR 6, 0: PRINT "More " + CHR$(24) + CHR$(25);
			COLOR 7, 0: PRINT "ÆÍ"; : COLOR 2, 0
		END IF

		in$ = STR$(hord%): oldhord% = hord%
		IF hord% = 0 THEN in$ = ""
		LOCATE 24, 61
		CALL inpnew(in$, 205!, updwn%, "13,59-60,64,67-68,72,73,80,81" + ALT$): GOSUB ALT

		IF custin$ <> "*" AND cash% AND in$ = "0" THEN updwn% = 68' emulate F10
		IF VAL(in$) > 999 THEN in$ = MID$(in$, 1, 3)
		IF updwn% = 13 AND RTRIM$(in$) = "" THEN GOTO getordnum
		IF updwn% = 13 AND VAL(in$) = 0 THEN
			IF in$ = "0" THEN GOTO getordnum
			custin$ = in$
			pass.getcust% = -1
			GOTO getcust
			END IF
		END IF
	IF updwn% = 59 THEN pass.getcust% = 0: GOTO getcust
	IF updwn% = 60 THEN pass.getcust% = 0: GOTO getcust
	IF updwn% = 64 THEN pass.getcust% = -1: GOTO getcust
	IF updwn% = 72 THEN
		dspstart% = dspstart% - 1
		CALL dsporders(dspstart%, norders%, custin$)
		END IF
	IF updwn% = 73 THEN
		dspstart% = dspstart% - 11
		CALL dsporders(dspstart%, norders%, custin$)
		END IF
	IF updwn% = 81 THEN
		dspstart% = dspstart% + 11
		CALL dsporders(dspstart%, norders%, custin$)
		END IF
	IF updwn% = 80 THEN
		dspstart% = dspstart% + 1
		CALL dsporders(dspstart%, norders%, custin$)
		END IF

	IF updwn% = 13 AND custin$ = "*" THEN
		dspstart% = VAL(in$)
		CALL dsporders(dspstart%, norders%, custin$)
	END IF

	emsg$ = ""
	ok% = 0
	IF updwn% = 68 THEN ok% = -1
	hord% = VAL(in$)
	FOR i% = 1 TO norders%
		IF orders%(i%) = hord% THEN ok% = -1: EXIT FOR
	NEXT
	IF NOT ok% THEN
		hord% = orders%(1)
		GOTO getordnum
	END IF

	IF custin$ = "*" THEN updwn% = 13: GOTO getordnum

	SELECT CASE updwn%
	CASE 59
	CASE 68: 'F10-Find next unused order number
		CALL findnext(hord%, norders%, ok%)
		IF updwn% <> 59 AND emsg$ = "" THEN
			CALL limit.warn(s90!, s60!, s30!, scur!, climit!, updwn%, allow$)
			IF updwn% = 59 THEN sno% = 0: pass.getcust% = -1: GOTO getcust
			GOSUB mline
			END IF
	CASE 13: 'Edit the details
			CALL limit.warn(s90!, s60!, s30!, scur!, climit!, updwn%, allow$)
			IF updwn% = 59 THEN sno% = 0: pass.getcust% = -1: GOTO getcust
			GOSUB mline
	CASE ELSE
	END SELECT
	LOOP
	GOTO getcust

'--E D I T   S E C T I O N
mline:

	GOSUB load.det

det:
	mode$ = "ord"
	GOSUB detail
	opt$ = "2"
exitmenu:
	DO

	SELECT CASE skipexit%
	CASE -1: opt$ = "": updwn% = 60
	CASE ELSE
		CALL box(17, 4, 63, 11, 6, 9, 1)
		COLOR 3, 1
		LOCATE 5, 28: PRINT "  E X I T    M E N U "
		COLOR 6, 1
		LOCATE , 28: PRINT ""
		LOCATE , 28: PRINT "1....Exit without update."
		LOCATE , 28: PRINT "2....Print Work Order."
		COLOR 14
		LOCATE , 22: PRINT cond.red$
		COLOR 2
		LOCATE , 28: PRINT "Option...> "
		COLOR 6, 1
		LOCATE , 20: PRINT "F1-Save & Exit.  F2-Save & Cont. F4-Cancel."
		LOCATE 10, 38: COLOR 2, 0
		CALL inpnew(opt$, 201!, updwn%, "13,59-60,62,68")
	END SELECT
	skipexit% = 0

	opt% = VAL(opt$)

	IF updwn% = 13 AND opt% = 0 THEN updwn% = 59
	IF updwn% = 59 THEN opt% = 0
	IF updwn% = 60 THEN opt% = -1'F2 - Save & Cont
	IF updwn% = 62 THEN opt% = -2'F4 - Cancel the order

	LOOP UNTIL opt% >= -2 AND opt% <= 2

	sav% = 0
	doc.type$ = "TAX INVOICE"
	formtype$ = "*PRE.PRINTED.1"


	IF opt% = -2 THEN mode$ = "del": sav% = 0
	IF opt% = -1 THEN mode$ = "ord": sav% = -1
	IF opt% = 0 THEN mode$ = "ord": sav% = -1
	IF opt% = 1 THEN mode$ = "nil": sav% = 0
	IF opt% = 2 THEN mode$ = "ord": sav% = -1
	
	IF mode$ = "b/o" THEN CALL add.bo.msg(updwn%)

	IF sav% THEN
		CALL update.order(hord%, updwn%)
		IF updwn% = 60 THEN GOTO mline
	END IF

	'/// Print and exit or delete ///
	IF updwn% <> 59 THEN
		'- Supliers from 1 to MAXTYPES are for CASH ONLY
		IF mode$ = "inv" OR mode$ = "b/o" THEN
			END IF
		END IF

		IF mode$ = "b/o" THEN CALL prtWO(hord%, opt%, discovr!)
		IF mode$ = "ord" THEN CALL prtWO(hord%, opt%, discovr!)

		IF mode$ = "del" THEN
			autodel$ = "N"
			CALL del.order(hord%, n%, clr%, autodel$, thissup$, norders%)
			CALL findorders(thissup$, norders%, hord%)
			IF updwn% = 59 THEN GOTO det'Delete aborted
			GOTO mlend
		END IF


mlend:
	'- Change F1 to prevent the real mainline ending the program. <<
	updwn% = 13
	clr% = 3
RETURN


'--L O A D   I N V O I C E   D E T A I L S
load.det:
	FOR l% = 1 TO maxlines%
		in$(l%, 1) = "0": in$(l%, 2) = "   ": in$(l%, 3) = "": in$(l%, 4) = "": in$(l%, 5) = "": in$(l%, 6) = "0"
		in$(l%, 7) = "0": in$(l%, 8) = "0": in$(l%, 9) = "N/": in$(l%, 10) = "0": in$(l%, 11) = "0"
	NEXT
	tot.ltact = 0      'Litres on order
	tot.ltinv = 0      'Litres invoiced
	tot.dollr = 0
	tot.items& = 0
	discovr! = 0'Discount override
	ovrPrice! = -9999
	invmsg1$ = ""'Clear out any old messages
	invmsg2$ = ""
	invmsg3$ = ""
	invmsg4$ = ""
	GET #48, hord%, ordhed
	invmsg1$ = ordhed.hnote1
	invmsg2$ = ordhed.hnote2
	
	hinvq = CVS(ordhed.hinvq$)

	nn% = -1: firstrec% = CVI(ordhed.hrrn$)
	CALL linkedl(rrn%(), nn%, firstrec%, hord%, 49)

	'-> Read throught the linked list of the details file
	dnext% = CVI(ordhed.hrrn$)
	l% = 0: m% = 0
	DO WHILE dnext% > 0
		GET #49, dnext%, orddet
		l% = l% + 1: IF l% > maxlines% THEN l% = maxlines%: EXIT DO
		ditem% = CVI(orddet.ditem$)
		ordqty% = CVI(orddet.dordq$)
		invqty% = CVI(orddet.dinvq$)
		Price! = CVS(orddet.dprice$)
		IF ordqty% > 0 THEN
			m% = m% + 1
			CALL load.line(m%, ditem%, ordqty%, invqty%, Price!)
		END IF
		'- Bottom of read equal loop
		dnext% = orddet.drrn%
	LOOP
	'Clear out items above loaded number.
	s% = m% + 1
	FOR m% = s% TO l%
		invqty% = 0
		ordqty% = 0
		ditem% = 0
		CALL load.line(m%, ditem%, ordqty%, invqty%, Price!)
	NEXT

RETURN

detail:
	CALL setup("W O R K    O R D E R    E N T R Y")
	btma$ = "F1-Save/Print  F5-Prices   F6-Browse   F8-Add Text   F9-Add Item  F10-Ref"
	COLOR 8, 3: LOCATE 25, 1: PRINT btma$;
	IF acstkf$ = "PRE" THEN
		CALL box(1, 2, 80, 24, 13, 0, 2)
		CALL SNDMSG("")
		LOCATE 23, 2: COLOR 0, 13: PRINT SPACE$(29); "--PREVIOUS PRICES-- " + SPACE$(29): COLOR 2, 0
	END IF

	d.elem% = 1'Start at element number 1.
	scrn.pag% = 1
	l% = 1
detail.a:
	IF updwn% = 73 THEN l% = d.elem%'page up
	IF updwn% = 81 THEN l% = d.elem%'page down
	e.elem% = d.elem% + 14
	IF e.elem% > maxlines% THEN e.elem% = maxlines%
	COLOR 7, 0: LOCATE 2, 2: PRINT "µ": LOCATE 2, 79: PRINT "Æ"
	COLOR 2, 0:
	LOCATE 2, 3: PRINT USING " Order:####"; hord%;
	a$ = "  " + LEFT$(cus.sname$, 20) + " " + LEFT$(cus.scont$, 20) + " " + cus.search$ + cus.stype$ + "  "
	COLOR 2
	PRINT a$
	COLOR 2

	LOCATE , 2: COLOR 6, 0: PRINT "Qty. Size   No.  Description                           Price  G.S.T   Value"

	COLOR 2
	LOCATE , 2: COLOR 2, 0: PRINT "ÄÄÄÄÂÄÄÄÄÄÂÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄ"
	LOCATE , 2: COLOR 10: PRINT USING "p #"; scrn.pag%: COLOR 2
	sav.l% = l%
	FOR l% = d.elem% TO e.elem%
		CALL dsply.line(l%, d.elem%)
		NEXT
	l% = sav.l%
	LOCATE , 2: COLOR 2, 0: PRINT "ÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄ"
	CALL addtext(0) 'Display mode only


	'--Get line entries
	updwn% = 0
	sav.scrn.pag% = scrn.pag%
	DO WHILE updwn% <> 59 AND sav.scrn.pag% = scrn.pag%
		ln% = (l% - d.elem%) MOD 15 + 1: ln% = ln% + 4
		CALL chglin(ln%, l%, d.elem%, updwn%)
		IF updwn% = 62 THEN EXIT DO   'F4 - Delete
		IF updwn% = 60 THEN l% = l% - 2'F2 - Back one line
		IF updwn% = 72 THEN l% = l% - 2'/\ - Back up one line
		IF updwn% = 73 THEN l% = l% - 16'Page up one screen
		IF updwn% = 81 THEN l% = l% + 16'Page down one screen

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
		CASE 31 TO 45: d.elem% = 31: scrn.pag% = 3
		CASE 16 TO 30: d.elem% = 16: scrn.pag% = 2
		CASE ELSE: d.elem% = 1: scrn.pag% = 1
		END SELECT
		IF l% > maxlines% THEN l% = maxlines%' Past end of data
		IF l% < 1 THEN l% = 1              ' Before start of data
		IF l% > d.elem% + 14 THEN l% = d.elem% + 15' Past end of screen
		IF l% < d.elem% THEN l% = d.elem%  ' Before start of screen
		LOOP
	IF sav.scrn.pag% <> scrn.pag% AND updwn% <> 59 THEN GOTO detail.a
RETURN

SUB accbrowse (rec%) STATIC
npgm$ = "dsinv04d"
CALL EXITPGM(npgm$)
SHELL npgm$
END SUB

SUB add.bo.msg (updwn%)
'Add item 2 "GOODS ON BACKORDER"
'or  "BACKORDER NOT REQUIRED" (Item 3)
ditem% = 2
IF cus.bo = "N" THEN ditem% = 3

ordqty% = 1
invqty% = 1
Price! = 0

m% = 0
found% = 0
FOR i% = 1 TO maxlines%
	IF VAL(in$(i%, 4)) = 0 THEN m% = i%: found% = -1: EXIT FOR
NEXT

IF found% THEN
	CALL load.line(m%, ditem%, ordqty%, invqty%, Price!)
END IF

END SUB

SUB addcust

name0:
			sno% = 1
			GET #43, sno%, CUS
			DO WHILE NOT EOF(43)
				IF CVI(cus.sno) <> sno% THEN
				PRINT cus.sname$
					EXIT DO
				END IF
			GET #43, , CUS: sno% = sno% + 1
			LOOP

			IF sno% > maxcus% THEN EXIT SUB

	'>>>>> Reals
	 LSET cus.s0$ = MKS$(0):     LSET cus.scur$ = MKS$(0)
	 LSET cus.s30$ = MKS$(0):    LSET cus.s60$ = MKS$(0)
	 LSET cus.s90$ = MKS$(0):    LSET cus.sterms$ = MKS$(0)
	 LSET cus.climit$ = MKS$(0)
	 LSET cus.sgl$ = MKS$(0)
	 LSET cus.opn$ = MKS$(0)
	 LSET cus.opn30$ = MKS$(0)
	 LSET cus.opn60$ = MKS$(0)
	 LSET cus.opn90$ = MKS$(0)
	 LSET cus.scur$ = MKS$(0)
	 LSET cus.s30$ = MKS$(0)
	 LSET cus.s60$ = MKS$(0)
	 LSET cus.s90$ = MKS$(0)

	 '>>>>> Integers
	 LSET cus.sno$ = MKI$(0):    LSET cus.daysmax$ = MKI$(0)
	 '>>>>> Strings
	 LSET cus.sname$ = SPACE$(99):   LSET cus.saddr$ = SPACE$(99)
	 LSET cus.spcode$ = SPACE$(99)'  LSET cus.sacode$ = SPACE$(99)
	 LSET cus.sphone$ = SPACE$(99):  LSET cus.sdate$ = SPACE$(99)
	 LSET cus.scont$ = SPACE$(99):   LSET cus.suburb$ = SPACE$(99)
	 LSET cus.spbox$ = SPACE$(99):   LSET cus.sdist$ = SPACE$(99)
	 LSET cus.sret$ = SPACE$(99):    LSET cus.spname$ = SPACE$(99)
	 LSET cus.spsub$ = SPACE$(99)
	 LSET cus.stype$ = SPACE$(99):   LSET cus.search$ = SPACE$(99)
	 'SET cus.sacode1$ = SPACE$(99):
	 LSET cus.sphone1$ = SPACE$(99)
	 LSET cus.account$ = SPACE$(99): LSET cus.taxe$ = SPACE$(99)
	 LSET cus.scont1$ = SPACE$(99):  LSET cus.scont2$ = SPACE$(99)
	 LSET cus.addocnum$ = SPACE$(99)
	 LSET cus.addate$ = SPACE$(99)
	 LSET cus.advalue$ = MKS$(0)
	 LSET cus.pstnCC$ = SPACE$(99)

		'
		cus.saddr2 = SPACE$(99)
		cus.state = SPACE$(99)
		cus.spboxsub = SPACE$(99)
		cus.email = SPACE$(99)
		cus.www = SPACE$(99)
		cus.scontTitle = SPACE$(99)
		cus.filler1 = SPACE$(200)

		cus.email = SPACE$(99)
		cus.www = SPACE$(99)
		FOR i% = 1 TO 6
			cus.ContactFirstName(6) = SPACE$(99)
			cus.ContactSurName(6) = SPACE$(99)
			cus.ContactTitle(6) = SPACE$(99)
			cus.ContactPhone(6) = SPACE$(99)
			cus.ContactMobile(6) = SPACE$(99)
			cus.ContactFax(6) = SPACE$(99)
			cus.Contactemail(6) = SPACE$(99)
		NEXT

			CALL dsply(sno%, norders%)

name1:
			a$ = cus.sname$
			LOCATE 3, 3: CALL inpnew(a$, 126!, updwn%, "13,59,60")
			LSET cus.sname$ = a$ + SPACE$(99)
			IF updwn% = 59 THEN GOTO xname
			IF updwn% = 60 THEN GOTO name0

name2:
			a$ = cus.scont$
			LOCATE 3, 34: CALL inpnew(a$, 125!, updwn%, "13,59,60")
			LSET cus.scont$ = a$
			IF updwn% = 59 THEN GOTO xname
			IF updwn% = 60 THEN GOTO name1

name3:
			a$ = cus.sphone$
			LOCATE 3, 60: CALL inpnew(a$, 114!, updwn%, "13,59,60")
			LSET cus.sphone$ = a$ + SPACE$(99)
			IF updwn% = 59 THEN GOTO xname
			IF updwn% = 60 THEN GOTO name2

name4:
			a$ = cus.search$
			LOCATE 3, 74: CALL inpnew(a$, 104!, updwn%, "13,59,60")
			LSET cus.search$ = a$
			IF updwn% = 59 THEN GOTO xname
			IF updwn% = 60 THEN GOTO name3
			IF cus.search$ = "    " THEN GOTO name4
name5:
			a$ = cus.stype$
			LOCATE 3, 78: CALL inpnew(a$, 101!, updwn%, "13,59,60")
			LSET cus.stype$ = a$
			IF updwn% = 59 THEN GOTO xname
			IF updwn% = 60 THEN GOTO name4
			IF cus.stype$ = " " THEN GOTO name5
name6:
			a$ = cus.saddr$
			LOCATE 5, 3: CALL inpnew(a$, 120!, updwn%, "13,59,60")
			LSET cus.saddr$ = a$
			IF updwn% = 59 THEN GOTO xname
			IF updwn% = 60 THEN GOTO name5
name7:
			a$ = cus.suburb$
			LOCATE 6, 3: CALL inpnew(a$, 120!, updwn%, "13,59,60")
			LSET cus.suburb$ = a$
			IF updwn% = 59 THEN GOTO xname
			IF updwn% = 60 THEN GOTO name6

			cus.sno = MKI$(sno%)
			PUT #43, sno%, CUS

xname:

END SUB

SUB additem (ln%)
iname0:

			i% = 21
			GET #3, i%, acstk
			DO WHILE NOT EOF(43)
				IF acstk.no <> i% THEN
					EXIT DO
				END IF
			GET #3, , acstk: i% = i% + 1
			LOOP

			IF i% > maxacc% THEN EXIT SUB

iname1:
			a$ = acstk.desc1$
			LOCATE ln%, C%(5): CALL inpnew(a$, 125!, updwn%, "13,59,60")
			LSET acstk.desc1$ = a$
			IF updwn% = 59 THEN GOTO xiname
			IF updwn% = 60 THEN GOTO iname0

iname2:
			a$ = acstk.desc2$
			LOCATE ln%, C%(5) + 26: CALL inpnew(a$, 110!, updwn%, "13,59,60")
			LSET acstk.desc2$ = a$
			IF updwn% = 59 THEN GOTO xiname
			IF updwn% = 60 THEN GOTO iname1
iname3:
			a$ = ""
												LOCATE ln%, C%(6): CALL inpnew(a$, 5.2, updwn%, "13,59,60")
			acstk.counter = VAL(a$)
			acstk.contract = acstk.counter
			acstk.distributor = acstk.counter
			acstk.industrial = acstk.counter
			acstk.trade = acstk.counter
			acstk.wholesalecost = acstk.counter
			acstk.retail = acstk.counter

			IF updwn% = 59 THEN GOTO xiname
			IF updwn% = 60 THEN GOTO iname1


			l% = 1
			acstk.size = in$(l%, 2)
			acstk.no = i%
			PUT #3, i%, acstk

xiname:


END SUB

SUB addtext (edit%)

	filename$ = "WO" + RIGHT$("00000000" + MID$(STR$(hord%), 2), 5) + ".txt"
	f = FREEFILE

	FOR i% = 1 TO 10
		txt$(i%) = ""
	NEXT

	IF DIR$(filename$) > "" THEN
		i% = 0
		OPEN filename$ FOR INPUT AS #f


		i% = i% + 1
		LINE INPUT #f, txt$(i%)
		DO WHILE NOT EOF(f) AND i% < 10
			i% = i% + 1
			LINE INPUT #f, txt$(i%)
		LOOP

		CLOSE #f
	END IF

	CALL box(11, 7, 67, 20, 7, 0, 1)
	COLOR 6, 0: LOCATE 8, 13: PRINT "Comments....;": COLOR 2, 0
	FOR l% = 1 TO 10
		ln% = l% + 8
		LOCATE ln%, 12: PRINT txt$(l%)
	NEXT


	IF edit% THEN


		l% = 1
		DO
			IF l% > 10 THEN l% = 10
			IF l% < 1 THEN l% = 1
			ln% = l% + 8
												LOCATE ln%, 12: CALL inpnew(txt$(l%), 155!, updwn%, "13,59-60")
			IF updwn% = 59 THEN EXIT DO
			IF updwn% = 60 THEN l% = l% - 1
			IF updwn% = 13 THEN l% = l% + 1
		LOOP

	
		OPEN filename$ FOR OUTPUT AS #f
		FOR i% = 1 TO 10
			PRINT #f, txt$(i%)
		NEXT
		CLOSE #f
	END IF
		
END SUB

SUB cf8 (l%, d.elem%, newdata$)
REDIM x20%(20)
'--EXTENSION
cf8:
	qty! = VAL(in$(l%, 1))
	size! = VAL(in$(l%, 2))
	Price! = VAL(in$(l%, 6))
	tax! = VAL(in$(l%, 7))
	'>-- Stock items 1-20 are special reusable items
	IF VAL(in$(l%, 4)) = 1 AND ctl% = 4 THEN

		'Load an array of the first 20 stock units on order
		FOR i% = 1 TO 20: x20%(i%) = 0: NEXT:
		x20%(1) = -1: x20%(2) = -1: x20%(3) = -1'On backorder' ' order complete'
		i% = 1
		GET #49, i%, orddet
		DO WHILE i% < 10000 AND NOT EOF(49)
			IF orddet.dord% <> -1 THEN
				j% = CVI(orddet.ditem$)
				IF j% > 1 AND j% <= 20 THEN x20%(j%) = -1
			END IF
			GET #49, , orddet: i% = i% + 1
		LOOP

		FOR i% = 1 TO maxlines%
			j% = VAL(in$(i%, 4))
			IF j% > 1 AND j% <= 20 THEN x20%(j%) = -1
		NEXT

		spec% = 1
		FOR i% = 1 TO 20
			IF x20%(i%) = 0 THEN spec% = i%: EXIT FOR
		NEXT

		in$(l%, 4) = STR$(spec%)

		d.elem% = 1' this is hard coded
		ln% = (l% - d.elem%) MOD 15 + 1: ln% = ln% + 4'+4 Lines from the top of the screen
		LOCATE ln%, C%(4): PRINT USING "####"; spec%

		LOCATE ln%, C%(5): PRINT acstk.desc1$; " "; acstk.desc2$
		dkt$ = acstk.desc1$
		LOCATE ln%, C%(5)
		CALL inpnew(dkt$, 125!, updwn%, "13,60")
		LSET acstk.desc1$ = dkt$
		dkt$ = acstk.desc2$

		LOCATE ln%, C%(5) + 26
		CALL inpnew(dkt$, 110!, updwn%, "13,60")
		LSET acstk.desc2$ = dkt$
		LOCATE ln%, C%(5): PRINT acstk.desc1$; " "; acstk.desc2$
		in$(l%, 5) = acstk.desc1$ + " " + acstk.desc2$

		LOCATE ln%, C%(6)
		in$(l%, 6) = STR$(acstk.purcost!)
								CALL inpnew(in$(l%, 6), 5.2, updwn%, "13")
		Price! = VAL(in$(l%, 6))

		ctl% = 6
	END IF
	'-
	old.ext! = VAL(in$(l%, 8))
	ext! = qty! * (Price! + tax!)
	in$(l%, 8) = STR$(ext!)
	IF old.ext! <> ext! THEN ext.has.changed% = -1

END SUB

SUB chglin (ln%, l%, d.elem%, updwn%)
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

'--- Detail entry subroutines
	'-QTY
cf1:
	LOCATE ln%, C%(1)
	in$ = in$(l%, 1)
	old.qty = VAL(in$(l%, 1))

	IF updwn% = 113 THEN 'The last one was scanned, get ready for another
		in$ = "1"
		updwn% = 13
	ELSE
		CALL inpnew(in$, 204!, updwn%, "13,27,59-60,62-64,66,68,72-73,80-81")
	END IF

	in$ = UCASE$(in$)
	IF updwn% = 27 THEN
		in$(l%, 1) = "0": in$(l%, 2) = "   ": in$(l%, 3) = "": in$(l%, 4) = "": in$(l%, 5) = "": in$(l%, 6) = "0"
		in$(l%, 7) = "0": in$(l%, 8) = "0": in$(l%, 9) = "N/": in$(l%, 10) = "0": in$(l%, 11) = "0"
		CALL dsply.line(l%, d.elem%)
		GOTO cf1
	END IF

	IF updwn% = 63 THEN '-Instant price browse
		PCOPY 0, 1
		CALL box(4, 9, 77, 15, 3, 0, 1)
		i% = VAL(in$(l%, 4))
		IF i% > 0 AND i% < maxacc% THEN
			GET #3, i%, acstk
		END IF
		COLOR 6, 0
		LOCATE 10, 5: PRINT USING "          Distributor   wholesale  Tax/Inc. ->&"; acstk.desc1$
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
	IF updwn% = 66 THEN 'edit text
		CALL addtext(-1)
		GOTO cf1
	END IF

	IF updwn% = 68 THEN
		CALL get.order.vs(hord%, updwn%)
		updwn% = 59: skipexit% = -1'Emualate. exit update and continue
	END IF

	'-
	IF VAL(in$) > 9300 THEN
		in$ = "1"
		SOUND 15000, 10
		SOUND 500, 3
	END IF


	in$(l%, 1) = in$
	newdata$ = "Y": CALL cf8(l%, ctl%, newdata$)
	newsearch$ = "Y"

	IF old.qty <> VAL(in$) THEN
		CALL dsply.line(l%, d.elem%)
	END IF

RETURN
	'-SIZE
cf2: LOCATE ln%, C%(2)
	learn% = -1
	IF VAL(in$(l%, 4)) = 0 THEN check$ = "13,59,60,62,27" ELSE check$ = ""
	'CALL inpnew(in$(l%, 2), 103!, updwn%, check$)
	IF check$ > "" THEN
	btm$ = ""
	FOR i% = 1 TO 79: btm$ = btm$ + CHR$(SCREEN(25, i%)): NEXT
	btma$ = "F1-Save/Print.   Enter Size or Scan Barcode or F4-Remove Barcode Assigment"

cf2UL:
		COLOR 8, 3: LOCATE 25, 1: PRINT btma$;
		LOCATE ln%, C%(2)
		CALL inpnew(in$(l%, 2), 113!, updwn%, check$)
		IF updwn% = 62 THEN
			learn% = 0
			CALL SNDMSG("Remove Barcode assignment.")
			GOTO cf2UL
		END IF

		CALL SNDMSG("")
		COLOR 8, 3: LOCATE 25, 1: PRINT btm$;
	END IF

	IF updwn% = 27 THEN
		in$(l%, 1) = "0": in$(l%, 2) = "   ": in$(l%, 3) = "": in$(l%, 4) = "": in$(l%, 5) = "": in$(l%, 6) = "0"
		in$(l%, 7) = "0": in$(l%, 8) = "0": in$(l%, 9) = "N/": in$(l%, 10) = "0": in$(l%, 11) = "0"
		CALL dsply.line(l%, d.elem%)
		updwn% = 60
	END IF

	IF VAL(in$(l%, 2)) > 9300 THEN
		ean$ = in$(l%, 2)
		CALL ean13(in$(l%, 2), ind%)
		IF ind% <= 0 THEN
			in$(l%, 2) = ""
			COLOR 13, 0
			LOCATE 3, 35: PRINT USING "\                \"; ean$
			COLOR 2, 0
			CALL SNDMSG("Barcode not found. Enter size & Search key to assign.")
			SOUND 1500, 10
			SOUND 300, 10
			GOTO cf2
		END IF

		'>F4 from then ean prompt removes it.
		IF NOT learn% THEN
			IF ind% > 0 AND ind% < maxacc% THEN
				GET #3, ind%, acstk
				acstk.ean13 = 0
				PUT #3, ind%, acstk
				CALL SNDMSG("Barcode assignment removed.")
			END IF
			updwn% = 13
			in$(l%, 2) = ""
			GOTO cf2
		END IF


		ditem% = ind%
		Price! = -1
		ordqty% = VAL(in$(l%, 1))
		invqty% = 0
		m% = l%
		CALL load.line(m%, ditem%, ordqty%, invqty%, Price!)
		CALL dsply.line(l%, d.elem%)
		updwn% = 113 'Says EAN assigned
	END IF


	in$(l%, 2) = UCASE$(in$(l%, 2))
	a$ = "   ": LSET a$ = in$(l%, 2): in$(l%, 2) = a$

	bysearch$ = "N"
	IF in$(l%, 2) <> "   " AND VAL(in$(l%, 4)) = 0 THEN bysearch$ = "Y"

RETURN
	'-UNITS
cf3: LOCATE ln%, C%(3)
	CALL inpnew(in$(l%, 3), 102!, updwn%, "")
RETURN
	'-STOCK NUMBER
cf4: LOCATE ln%, C%(4)
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
		Price! = -1
		ordqty% = VAL(in$(l%, 1))
		invqty% = 0
		m% = l%
		CALL load.line(m%, ditem%, ordqty%, invqty%, Price!)
		CALL dsply.line(l%, d.elem%)
	END IF
RETURN
	'-DESCRIPTION
cf5: LOCATE ln%, C%(5)
	IF bysearch$ = "N" THEN
		CALL inpnew(in$(l%, 5), 136!, updwn%, "")

	ELSE '/// Search away ///
		IF newsearch$ = "Y" THEN
			in$ = "": IF frombrowse% = -1 THEN in$ = acstk.search$: frombrowse% = 0
			CALL SNDMSG("Enter search key or F9 to add item.")

			CALL inpnew(in$, 118!, updwn%, "13,59,60,64,62,67")
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
			IF updwn% = 67 THEN 'Add item
				CALL additem(ln%)
				LSET qk$ = search.key$
				test1$ = MID$(qk$, 1, 1)
				search.dir$ = CHR$(13)
				ind% = acstk.no
				GOTO anext3

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
			LOCATE ln%, C%(4): PRINT USING "####"; ind%
			LOCATE ln%, C%(5): PRINT acstk.desc1$; " "; acstk.desc2$
			LOCATE ln%, C%(5)
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
			Price! = -1
			ordqty% = VAL(in$(l%, 1))
			invqty% = 0
			m% = l%
			CALL load.line(m%, ditem%, ordqty%, invqty%, Price!)
			CALL dsply.line(l%, d.elem%)
			'- Place the result of the search in the search key
			search.key$ = acstk.search$
			COLOR 13, 0
			LOCATE 3, 35: PRINT USING "\                \"; search.key$
			COLOR 2, 0

			'>-Learn
			IF ean$ > "" AND acstk.ean13 <> VAL(ean$) THEN
				IF ditem% > 0 AND ditem% < maxacc% THEN
					GET #3, ditem%, acstk
					IF acstk.ean13 > 0 THEN
						CALL SNDMSG("Stock already has a barcode. Reassign?..> ")
						SOUND 1000, 1
						LOCATE 24, 45
						a$ = "N"
						CALL inpnew(a$, 101!, updwn%, "59,13")
						IF updwn% = 59 THEN a$ = "N"
						IF UCASE$(a$) = "Y" THEN
							acstk.ean13 = 0
						ELSE
							CALL SNDMSG("")
						END IF
					END IF

					IF acstk.ean13 = 0 THEN
						acstk.ean13 = VAL(ean$)
						PUT #3, ditem%, acstk
						CALL SNDMSG("Barcode" + STR$(acstk.ean13) + " assigned.")
					END IF

				END IF
			END IF
			ean$ = ""
		END IF

xcf5:
RETURN
	'-PRICE
cf6: LOCATE ln%, C%(6)
				'CALL inpnew(in$(l%, 6), 5.2!, updwn%, "")
RETURN
	'-TAX
cf7:
RETURN
x.chglin:

END SUB

SUB del.order (hord%, n%, clr%, autodel$, thissup$, norders%)
del.order:
	IF autodel$ <> "Y" THEN
		COLOR 0, 7: LOCATE 25, 1: PRINT SPACE$(80);
		COLOR 0, 7: LOCATE 25, 20: PRINT "F1 - Exit.        F10 - Continue.";
		LOCATE 1, 1
		CALL inpnew(in$, 0!, updwn%, "59,68")
		IF updwn% = 59 THEN GOTO x.del.order
		END IF
	autodel$ = "N"

	'-Count the details
	FOR l% = 1 TO maxlines%
		IF VAL(in$(l%, 4)) <> 0 THEN n% = l%
	NEXT
	firstrec% = CVI(ordhed.hrrn$)
	CALL linkedl(rrn%(), 0, firstrec%, hord%, 49)

	'-Delete the HEADER file
	GET #48, hord%, ordhed
	LSET ordhed.hord$ = MKI$(0)
	LSET ordhed.hreford$ = SPACE$(99)
	LSET ordhed.hsup$ = "     "
	LSET ordhed.hrrn$ = MKI$(0)
	LSET ordhed.horgq$ = MKS$(0)
	LSET ordhed.hordq$ = MKS$(0)
	LSET ordhed.hinvq$ = MKS$(0)
	LSET ordhed.hdollar$ = MKS$(0)
	LSET ordhed.hitems$ = MKI$(0)
	LSET ordhed.hnote1$ = SPACE$(99)
	LSET ordhed.hnote2$ = SPACE$(99)
	PUT #48, hord%, ordhed
	hord% = 0

	'If a special item is used (stock # <20) delete it.
	FOR l% = 1 TO maxlines%
		i% = VAL(in$(l%, 4))
		IF i% >= 1 AND i% <= 20 THEN
			GET #3, i%, acstk
			acstk.no = 0
			acstk.desc1$ = ""
			acstk.desc2$ = ""
			PUT #3, i%, acstk
		END IF
	NEXT

	clr% = 1
x.del.order:

END SUB

SUB dsply (sno%, norders%) STATIC
dsply:
	IF sno% < 1 OR sno% > maxcus% THEN GOTO x.dsply
	GET #43, sno%, CUS
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
	COLOR 7: LOCATE 4, 2: PRINT "ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ": COLOR 2
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

	COLOR 10, 0: LOCATE 8, 49
	IF cus.bo$ = "Y" THEN
		PRINT "Backorders Required": COLOR 2, 0
	ELSE
		PRINT "Backorder Not Required"
	END IF

	COLOR 6
	LOCATE , X0%: PRINT "90 Days.     60 Days.     30 Days.     Current.       Total.     C/Limit."
	COLOR 2
	LOCATE , 2: PRINT USING " ###,###.##   ###,###.##   ###,###.##   ###,###.## #,###,###.## "; s90; s60; s30; scur; s90 + s60 + s30 + scur

	IF climit! < 1 THEN COLOR 14
	LOCATE 10, 67: PRINT funclimit(climit!)
	COLOR 2

	COLOR 7: LOCATE , 2: PRINT "ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ": COLOR 2
	CALL box(2, 12, 79, 23, 7, 0, 0)
	LOCATE 11, 25: PRINT "Orders found for this customer"
	COLOR 6, 0
	IF norders% < 10 THEN
	LOCATE , 3: PRINT "Num. Type Ord.. Inv..  Order    Dollars. Date....  Order Ref... Due........"
	ELSE
	 LOCATE , 2: PRINT "Num Date. Cust. Ref...... Num Date. Cust. Ref...... Num Date. Cust. Ref......"
	END IF

	COLOR 2, 0

	'- Set cash sale mode
	cash% = 0
	IF cus.search = "CASH" THEN cash% = -1

x.dsply:

END SUB

SUB dsply.line (l%, d.elem%) STATIC
		ln% = (l% - d.elem%) MOD 15 + 1: ln% = ln% + 4'+4 Lines from the top of the screen
		COLOR 2, 0
		qty% = VAL(in$(l%, 1))
		IF qty% < 1 OR qty% > 9999 THEN
			LOCATE ln%, 2
			PRINT "    ³     ³    ³                                    ³       ³       ³         "
			ELSE
			qty% = VAL(in$(l%, 1))
			LSET acstk.size$ = in$(l%, 2)
			LSET acstk.unit$ = in$(l%, 3)
			ano% = VAL(in$(l%, 4))
			LSET acstk.desc1$ = in$(l%, 5)
			LSET acstk.desc2$ = MID$(in$(l%, 5), LEN(acstk.desc1$) + 2, 10)
			newdata$ = "N": CALL cf8(l%, d.elem%, newdata$)
			Price! = VAL(in$(l%, 6))
			tax! = VAL(in$(l%, 7))
			ext! = VAL(in$(l%, 8))
			'- Condition red
			IF ext! <= .01 AND qty% > 0 AND ano% > 0 THEN
				COLOR 4
				SOUND 250, 10
				cond.red$ = "There are zero values on the invoice"
				ELSE
				cond.red$ = ""
				END IF
			a$ = "³" + acstk.size$ + acstk.unit$ + "³"
			b$ = "³" + acstk.desc1$ + " " + acstk.desc2$ + "³"
			C$ = "³"
			LOCATE ln%, 2: PRINT USING "####"; qty%
			LOCATE ln%, 6: PRINT a$;
			LOCATE ln%, 13: PRINT USING "####"; ano%
			LOCATE ln%, 17: PRINT b$;
			LOCATE ln%, 55: PRINT USING "####.##"; Price!;
			LOCATE ln%, 62: PRINT C$;
			IF tax! <> 0 THEN
			LOCATE ln%, 63: PRINT USING "####.##"; tax!;
			ELSE
			LOCATE ln%, 63: PRINT USING "\     \"; SPACE$(7);
			END IF
			COLOR 2
			LOCATE ln%, 70: PRINT C$;
			LOCATE ln%, 71: PRINT USING "######.##"; ext!
			END IF

END SUB

SUB dsporders (dspstart%, norders%, custin$) STATIC
	IF dspstart% > norders% - 10 THEN dspstart% = norders% - 10
	IF dspstart% < 1 THEN dspstart% = 1

	X% = 2
	y% = 12

	FOR i% = dspstart% TO dspstart% + 32
		IF y% > 22 THEN
			X% = X% + 26
			y% = 12
			END IF
		y% = y% + 1
		LOCATE y%, X%
		IF norders% > 10 THEN
		PRINT "                         ";
		END IF

	IF i% <= norders% THEN
		GET #48, orders%(i%), ordhed
		a$ = "B/o."
		a$ = "Ord."
		IF custin$ = "*" THEN a$ = " <" + ordhed.hsup$ + ">"
		a = CVS(ordhed.horgq$)
		IF discovr! <> 0 THEN a = discovr!
		LOCATE y%, X%
		IF norders% < 10 THEN
		PRINT USING "### \   \ ###### ##### ######$$#######.## \      \  \          \ \        \"; CVI(ordhed.hord$); a$; a; CVS(ordhed.hinvq$); CVS(ordhed.hordq$); CVS(ordhed.hdollar$); FNDYY$(ordhed.hdate$); ordhed.hreford$; ordhed.htaxe$
		ELSE

		PRINT USING "### \   \ \   \ \        \"; CVI(ordhed.hord$); FNDYY$(ordhed.hdate$); ordhed.hsup$; ordhed.htaxe$
		END IF

		END IF
		NEXT


END SUB

SUB ean13 (in$, dind%)
	thsEan# = VAL(in$)
	found% = 0

	dind% = 1
	GET #3, dind%, acstk
	DO WHILE NOT EOF(3) AND dind% <= maxacc%
		IF acstk.ean13 = thsEan# THEN
			found% = -1
			EXIT DO
		END IF
		GET #3, , acstk: dind% = dind% + 1
	LOOP

	IF NOT found% THEN
		dind% = 0
	END IF

END SUB

SUB findnext (hord%, norders%, ok%) STATIC
findnext:
	IF norders% > 1001 THEN
		emsg$ = "Their are already EIGHT orders open for this customer."
		END IF
	IF hord% < 1 OR hord% > maxord% THEN hord% = 1
	oldhord% = hord%
	top% = 0
	GET #48, hord%, ordhed
	DO WHILE CVI(ordhed.hord$) = hord% AND emsg$ = ""
		IF top% AND hord% = oldhord% THEN emsg$ = "No unused orders could be found. Delete old orders before continuing.": EXIT DO
		IF hord% >= maxord% THEN hord% = 0: top% = -1
		hord% = hord% + 1
		GET #48, hord%, ordhed
		LOOP
	IF emsg$ = "" THEN
		'- Grab the record first up.
		LOCK #48, hord%
		GET #48, hord%, ordhed
		IF CVI(ordhed.hord$) = hord% THEN
			UNLOCK #48, hord%
			GOTO x.findnext
			END IF
		LSET ordhed.hord$ = MKI$(hord%)
		PUT #48, hord%, ordhed
		UNLOCK #48, hord%

		LSET ordhed.hdate$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
		LSET ordhed.htaxe$ = cus.taxe$
		LSET ordhed.hreford$ = SPACE$(99)
		LSET ordhed.hsup$ = "     "
		LSET ordhed.hrrn$ = MKI$(0)
		LSET ordhed.horgq$ = MKS$(0)
		LSET ordhed.hordq$ = MKS$(0)
		LSET ordhed.hinvq$ = MKS$(0)
		LSET ordhed.hdollar$ = MKS$(0)
		LSET ordhed.hitems$ = MKI$(0)
		LSET ordhed.hitems$ = MKI$(0)
		LSET ordhed.linvnum$ = SPACE$(99)
		PUT #48, hord%, ordhed

		'- Clear out the detail arrays
		'- Set order/pickslip mode
		mode$ = "ord"
		norders% = norders% + 1
		orders%(norders%) = hord%
		PUT #48, hord%, ordhed
		END IF

x.findnext:
	IF updwn% = 59 THEN
		LSET ordhed.hord$ = MKI$(0)
		PUT #48, hord%, ordhed
		END IF

END SUB

SUB findorders (thissup$, norders%, hord%)
	FOR i% = 1 TO 1001: orders%(i%) = 0: NEXT
	norders% = 0
	hord% = 1
	GET #48, hord%, ordhed
	DO WHILE NOT EOF(48)
		IF thissup$ = "ZZZZZ" THEN
			skey$ = "     ": LSET skey$ = ordhed.hsup$
			keyin$ = skey$: chi% = 23
			CALL searchindex(keyin$, chi%, found%)
			IF NOT found% THEN ordhed.hsup$ = thissup$
			END IF
		IF thissup$ = "*    " AND ordhed.hsup$ > "      " THEN
			ordhed.hsup$ = thissup$
			END IF
		IF CVI(ordhed.hord$) = hord% AND ordhed.hsup$ = thissup$ THEN
			norders% = norders% + 1
			IF norders% < 1001 THEN
				orders%(norders%) = hord%
				END IF
			END IF

		GET #48, , ordhed: hord% = hord% + 1
		IF hord% > 5001 THEN EXIT DO
		LOOP

	hord% = orders%(norders%)
	IF thissup$ = "*    " THEN hord% = 0

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

SUB get.order.vs (hord%, updwn%)
		GET #48, hord%, ordhed
		'- Get the tax exempt number and the tax order number
		LOCATE 21, 2: PRINT SPACE$(78)
		LOCATE 22, 2: PRINT SPACE$(78)
		LOCATE 21, 10: PRINT USING "Order number..>\          \   Due date ot note...>\          \"; ordhed.hreford$; ordhed.htaxe$
TX1:
		a$ = ordhed.hreford$
		LOCATE 22, 10: COLOR 10, 0: PRINT "Blanket orders must start B01-B12. (Number denotes month)": COLOR 2, 0
		LOCATE 21, 25: CALL inpnew(a$, 112!, updwn%, "13,59-60")
		LOCATE 22, 10: COLOR 6, 0: PRINT "                                                          ": COLOR 2, 0
		IF updwn% = 59 THEN GOTO x.get.order.vs
		IF updwn% = 60 THEN GOTO x.get.order.vs
		LSET ordhed.hreford$ = a$
		IF ordhed.hreford$ = SPACE$(12) THEN
			LSET ordhed.hreford$ = "    " + MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
			LSET ordhed.htaxe$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
			GOTO TX1
			GOTO x.get.order.vs
			END IF
		'//// Get the tax exempt numnber ////
TX2:
		 a$ = ordhed.htaxe$
		 LOCATE 21, 60: CALL inpnew(a$, 112!, updwn%, "13,59-60")

		 LSET ordhed.htaxe$ = a$ + SPACE$(99)
		 IF updwn% = 59 THEN GOTO x.get.order.vs
		 IF updwn% = 60 THEN GOTO TX1
x.get.order.vs:
		PUT #48, hord%, ordhed

END SUB

SUB limit.warn (s90!, s60!, s30!, scur!, climit!, updwn%, allow$) STATIC

	IF cash% THEN GOTO x.limit.warn

	warn1$ = "1 >- Customer is on cash only supply basis  (C.O.D.)": warn1% = 0
	warn2$ = "2 >- Customer is over their limit.                   ": warn2% = 0
	warn3$ = "3 >- Customer has outstanding debt over 30 days      ": warn3% = 0
	warn4$ = "4 >- Customer has outstanding debt over 60 days      ": warn4% = 0
	warn5$ = "5 >- Do Not sell anything on credit to this customer ": warn5% = 0
	warn6$ = "6 >- Customer has monthly installment agreement of ": warn6% = 0

	stotal! = s90! + s60! + s30! + scur!

	warn% = 0
	IF climit! = 0 THEN warn1% = -1: warn% = -1
	IF stotal! > climit! THEN warn2% = -1: warn% = -1
	IF s60! > 0 THEN warn3% = -1: warn% = -1
	IF s90! > 0 THEN warn4% = -1: warn% = -1
	IF climit = -3 THEN warn5% = -1: warn% = -1
	IF climit < -5 THEN warn6% = -1: warn% = -1

	IF climit <= -5 AND climit >= -25 THEN warn6$ = warn6$ + "Inv. + %" + STR$(0 - climit!)
	IF climit < -26 THEN warn6$ = warn6$ + "$" + STR$(0 - climit!)


	IF warn% THEN
		CALL box(3, 12, 78, 21, 0, 4, 1)
		COLOR 0, 4: LOCATE 21, 21: PRINT " F1 - Return     ENTER - to continue "
		IF warn1% THEN LOCATE 13, 11: COLOR 10: PRINT warn1$
		IF warn2% THEN LOCATE 14, 11: COLOR 11: PRINT warn2$
		IF warn3% THEN LOCATE 15, 11: COLOR 12: PRINT warn3$
		IF warn4% THEN LOCATE 16, 11: COLOR 13: PRINT warn4$
		IF warn5% THEN LOCATE 17, 11: COLOR 14: PRINT warn5$
		IF warn6% THEN LOCATE 18, 11: COLOR 15: PRINT warn6$
								CALL inpnew(a$, 0!, updwn%, "59,13")
		END IF

x.limit.warn:
END SUB

SUB linkedl (rrn%(), n%, firstrec%, ord%, chd%) STATIC
'$INCLUDE: '\tpmanuf\src\linkedl.bi'
END SUB

SUB load.line (m%, ditem%, ordqty%, invqty%, Price!)
load.line:
		'- lokup the details
		IF ditem% > 0 AND ditem% < maxacc% THEN
			GET #3, ditem%, acstk
			ano% = acstk.no%
			ELSE
			ano% = 0
			Price! = 0
			LSET acstk.size$ = in$(m%, 2)
			LSET acstk.unit$ = SPACE$(99)
			LSET acstk.desc1$ = SPACE$(99)
			LSET acstk.desc2$ = SPACE$(99)
			LSET acstk.taxinc$ = SPACE$(99)
			END IF
	'//// Determine which price to use ////
	IF Price! THEN
		IF ditem% <> 1 THEN
			CALL rightprice(Price!)
			tax! = Price! * (TaxRate! / 100): CALL ROUND(tax!, 2.5)
		END IF
	END IF
		'- Add up litres order and actualy on order
		ltact = 0
		size! = VAL(acstk.size$)
		IF acstk.unit$ = "LT" THEN ltact = ordqty% * size!
		IF acstk.unit$ = "ML" THEN ltact = ordqty% * size! / 1000
		in$(m%, 1) = STR$(ordqty%)
		in$(m%, 2) = acstk.size$
		in$(m%, 3) = acstk.unit$
		in$(m%, 4) = STR$(ano%)
		in$(m%, 5) = acstk.desc1$ + " " + acstk.desc2$
		in$(m%, 6) = STR$(Price!)' Price is set only the first time in since it cannot change
		in$(m%, 7) = STR$(tax!)
		in$(m%, 8) = STR$(0)
		'newdata$ = "Y": CALL cf8(l%, d.elem%, newdata$)
		newdata$ = "Y": CALL cf8(m%, d.elem%, newdata$)
		in$(m%, 9) = acstk.taxinc$
		in$(m%, 10) = STR$(ordqty%)
		in$(m%, 11) = STR$(invqty%)

END SUB

SUB openpslip (opt%) STATIC
ON LOCAL ERROR RESUME NEXT

IF opt% = 2 OR opt% = 10 THEN
	CLOSE #99
	OPEN "c:\tpexe\pslip.prn" FOR OUTPUT SHARED AS #99
	END IF

IF opt% <> 2 AND opt% <> 10 THEN
	ok% = 0
	DO WHILE ok% = 0
		CLOSE #99
		OPEN "PSLIP.PIC" FOR APPEND AS #99
		IF ERR = 0 THEN ok% = -1
		IF ERR <> 0 THEN
			CALL SNDMSG("Waiting...")
			SLEEP 5
			CALL SNDMSG("")
			END IF
		LOOP
	END IF

END SUB

SUB parse (hord%, opt%, cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, invmsg1$, invmsg2$)
ON ERROR RESUME NEXT

	rrn78% = 1
	GET #78, rrn78%, ordprt
	hord% = ordprt.hord
	opt% = ordprt.hopt
	cash% = ordprt.hcash
	chginv# = ordprt.hchginv
	chginv.rrn% = ordprt.hchginvrrn
	invnum# = ordprt.hinvnum
	invnumrec% = ordprt.hinvnumrec
	thissup$ = ordprt.hthissup
	norders% = ordprt.hnorders
	TaxRate! = ordprt.hTaxRate
	DiscRate! = ordprt.hDiscRate
	invmsg1$ = ordprt.hnote1
	invmsg2$ = ordprt.hnote2
	
	'Shared
	mode$ = ordprt.hMode
	sno% = ordprt.gsno
	tax.in$ = ordprt.gtaxin
	tender$ = ordprt.gtender
	doc.type$ = ordprt.gdoctype$
	formtype$ = ordprt.gformtype$

GET #48, hord%, ordhed

GET #43, sno%, CUS
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

END SUB

SUB prtWO (hord%, opt%, discovr!)
	IF hord% = 0 THEN GOTO x.prtWO
	GET #48, hord%, ordhed
	hordq = CVS(ordhed.hordq$)
	disc.qty = tot.ord
	CALL openpslip(opt%)
	pag = 1: lin = 0
	IF pag > 1 THEN PRINT #99, CHR$(12);
	'/////  print actual heading
		PRINT #99, USING "&&"; CHR$(14); msmisc.cc$
		PRINT #99, USING "ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ!"; "¿"
		PRINT #99, USING "³                                                                             !"; "³"
		PRINT #99, USING "³                          W O R K   O R D E R                \       \ \    \³"; MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2); MID$(TIME$, 1, 5)
		PRINT #99, USING "³                                                                             !"; "³"
		PRINT #99, USING "³ Name....: \                                 \ \                \            ³"; cus.sname$; cus.sphone$
		PRINT #99, USING "³ Address.: \                                 \ \                   \         ³"; cus.saddr$; cus.suburb$
		PRINT #99, USING "ÃÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ!"; "´"
		PRINT #99, USING "³ P/Slip ³ Account No. ³ O/Date    ³ Order No.     ³ Litres  ³ Due Date.....  !"; "³"
		PRINT #99, USING "³  ####  ³ \   \ - ### ³ \       \ ³ \           \ ³         ³ \           \  ³"; hord%; cus.search$ + cus.stype$; sno%; FNDYY$(ordhed.hdate$); ordhed.hreford$; ordhed.htaxe$ + ""
		PRINT #99, USING "ÃÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ!"; "´"
		PRINT #99, USING "³ No.   Description                            Size           Qty             !"; "³"
		PRINT #99, USING "ÃÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ!"; "³"
	'-> Read throught the linked list of the details file
	dnext% = CVI(ordhed.hrrn$)
	l% = 0
	DO WHILE dnext% > 0
		GET #49, dnext%, orddet
		l% = l% + 1
		'- Decode the detail file
		dord% = orddet.dord%
		ditem% = CVI(orddet.ditem$)
		dordq% = CVI(orddet.dordq$)
		IF ditem% < 1 OR ditem% > maxacc% OR dordq% = 0 THEN
		ELSE
			GET #3, ditem%, acstk
			dinvq% = CVI(orddet.dinvq$)
			PRINT #99, USING "³####  \                       \ \        \   \ \ \\         ###              ³"; ditem%; acstk.desc1$; acstk.desc2$; acstk.size$; acstk.unit$; dordq%
		END IF
		'- Bottom of read equal loop
		dnext% = orddet.drrn%
		LOOP
		PRINT #99, "ÀÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÙ"
		PRINT #99,
		PRINT #99,

		FOR i% = 1 TO 10
		PRINT #99, txt$(i%)
		NEXT

		FOR i% = l% TO 20
		PRINT #99,
		NEXT

		PRINT #99, "ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿"
		PRINT #99, "³ Required by                      ³ Batch No.                                ³"
		PRINT #99, "ÀÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÙ"
	PRINT #99, CHR$(18); CHR$(12);
	CLOSE #99

	IF opt% = 2 OR opt% = 10 THEN
	LOCATE 23, 2
	shella$ = "copy c:\tpexe\pslip.prn LPT1"
	SHELL shella$
	END IF

x.prtWO:

END SUB

SUB retail.round (Price!, round.type$) STATIC
SELECT CASE round.type$
CASE "5 Cents"
	work# = Price! * 1: dollars% = FIX(work#)
	work# = (Price! - dollars%) * 10: tens% = FIX(work#)
	work# = (Price! - dollars% - (tens% / 10)) * 100: digit% = work#
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
	Price! = dollars% + tens% / 10 + digit% / 100
CASE ELSE
END SELECT
END SUB

SUB rightprice (Price!) STATIC
	SELECT CASE cus.stype$
	CASE "A": 'Factory Price
				Price! = acstk.counter
	CASE "C": 'Contractor Price
				Price! = acstk.contract
	CASE "D": 'Distributor Price
				Price! = acstk.distributor
	CASE "G": 'Group Price
				Price! = acstk.distributor
	CASE "H": 'Hardware Price
				Price! = acstk.distributor
	CASE "I": 'Industrial Price
				Price! = acstk.industrial
	CASE "M": 'Mitre Ten Price
				Price! = acstk.distributor
	CASE "P": 'Painter Price
				Price! = acstk.industrial
	CASE "S": 'Special Price
				Price! = acstk.trade
	CASE "T": 'Trade Price
				Price! = acstk.trade
	CASE "W": 'Best Possible Price
				Price! = acstk.wholesalecost
	CASE "Y": 'Group Office Price
				Price! = acstk.distributor
	CASE "Z": 'Group store price
				Price! = acstk.distributor

	CASE ELSE: 'All Other Codes Are Retail Price
				Price! = acstk.retail
	END SELECT

x.rightprice:

END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

SUB update.order (hord%, updwn%)
update.order:
	'-First ensure all the details records have been allocated a rrn
	FOR l% = 1 TO maxlines%
		IF VAL(in$(l%, 4)) <> 0 THEN n% = l%
	NEXT
	nn% = n%: firstrec% = CVI(ordhed.hrrn$)
	CALL linkedl(rrn%(), nn%, firstrec%, hord%, 49)
	'-Update the order file before printing the picking slip
	tot.ltact = 0      'Litres on order
	tot.ltinv = 0      'Litres invoiced
	tot.dollr = 0
	tot.items& = 0
	FOR l% = 1 TO nn%
		keyed% = VAL(in$(l%, 1))
		ordqty% = VAL(in$(l%, 10))
		invqty% = VAL(in$(l%, 11))
		IF mode$ = "inv" THEN
			invqty% = keyed%
			ordqty% = 0
			dlinvq% = keyed%
		END IF
		IF mode$ = "ord" THEN
			invqty% = 0
			ordqty% = keyed%
			dlinvq% = CVI(orddet.dlinvq$)
		END IF
		IF mode$ = "b/o" THEN
			invqty% = keyed%
			ordqty% = ordqty% - keyed%
			IF ordqty% < 0 THEN ordqty% = 0
			dlinvq% = keyed%
		END IF
		IF debug% AND (mode$ = "inv" OR mode$ = "b/o") THEN
			ordqty% = VAL(in$(l%, 10))
			IF keyed% > ordqty% THEN
				ordqty% = keyed%
		END IF
		END IF
		'-Add up litres order and actualy on order
		ltact = 0: ltinv = 0
		size! = VAL(in$(l%, 2))
		IF in$(l%, 3) = "LT" THEN ltact = ordqty% * size!
		IF in$(l%, 3) = "ML" THEN ltact = ordqty% * size! / 1000
		tot.ltact = tot.ltact + ltact
		IF in$(l%, 3) = "LT" THEN ltinv = invqty% * size!
		IF in$(l%, 3) = "ML" THEN ltinv = invqty% * size! / 1000
		dprice = VAL(in$(l%, 6))
		tot.ltinv = tot.ltinv + ltinv
		tot.dollr = tot.dollr + (dprice * ordqty%)
		tot.items& = tot.items& + ordqty%
		IF ordqty% < 0 THEN ordqty% = 0
		GET #49, rrn%(l%), orddet
		LSET orddet.dinvq$ = MKI$(invqty%)
		LSET orddet.dordq$ = MKI$(ordqty%)
		LSET orddet.dlinvq$ = MKI$(dlinvq%)
		LSET orddet.ditem$ = MKI$(VAL(in$(l%, 4)))
		LSET orddet.dprice$ = MKS$(VAL(in$(l%, 6)))
		LSET orddet.dtax$ = MKS$(VAL(in$(l%, 7)))
		PUT #49, rrn%(l%), orddet: SOUND 20000, 1
		'-Update the stock file
			ditem% = CVI(orddet.ditem$)
			IF ditem% < 1 OR ditem% > maxacc% THEN
				IF ditem% <> 0 THEN SOUND 50, 1
			ELSE
				GET #3, ditem%, acstk
				asoh1 = acstk.soh
				asold1 = acstk.sold
				asoh1 = asoh1 - dlinvq%' Last invoice qty
				asoldt = asold1 + dlinvq%
				IF asoldt < 32000 AND asoldt > -32000 THEN asold1 = asoldt
				acstk.soh = asoh1
				acstk.sold = asold1
				PUT #3, ditem%, acstk

				IF in$(l%, 2) = "***" THEN 'special items
					GET #3, ditem%, acstk
					IF acstk.no <> ditem% OR ditem <= 20 THEN
						acstk.no = ditem%
						acstk.desc1$ = in$(l%, 5)
						acstk.desc2$ = MID$(in$(l%, 5), 27, 10)

						acstk.counter = CVS(orddet.dprice$)
						acstk.contract = acstk.counter
						acstk.distributor = acstk.counter
						acstk.industrial = acstk.counter
						acstk.trade = acstk.counter
						acstk.wholesalecost = acstk.counter
						acstk.retail = acstk.counter
						PUT #3, ditem%, acstk
					END IF
				END IF
				END IF
		'-End of updating the stock file
		NEXT

	GET #48, hord%, ordhed
	hinvq = CVS(ordhed.hinvq$)
	LSET ordhed.hord$ = MKI$(hord%)
	LSET ordhed.hsup$ = cus.search$ + cus.stype$

	LSET ordhed.hrrn$ = MKI$(rrn%(1))
	LSET ordhed.horgq$ = MKS$(tot.ord!)
	LSET ordhed.hordq$ = MKS$(tot.ltact)
	LSET ordhed.hinvq$ = MKS$(tot.ltinv)
	LSET ordhed.hdollar$ = MKS$(tot.dollr)
	IF tot.items& < 32000 THEN wrkitems% = tot.items& ELSE wrkitems% = 32000
	LSET ordhed.hitems$ = MKI$(wrk.items%)
	LSET ordhed.ldisc$ = MKS$(vdisc)
	ordhed.hnote1 = invmsg1$
	ordhed.hnote2 = invmsg2$

	PUT #48, hord%, ordhed

END SUB

