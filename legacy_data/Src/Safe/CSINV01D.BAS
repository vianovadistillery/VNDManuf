DECLARE SUB browse.idx (firstonscreen%, ch1%, ch2%)
DECLARE SUB supqtyconv (rec%, purconv)
DECLARE SUB invoiceentry (hord%, addate$, adnum$, status$, exitexit%)
DECLARE SUB receivedelivery (hord%, hdddate$, hdocket$, exitexit%)
DECLARE SUB upd.who (cha%, chw%, upd.audit%)
DECLARE SUB getdt (OSCurrency$, updwn%)
DECLARE SUB accbrowse (rec%)
DECLARE SUB add.bo.msg (updwn%)
DECLARE SUB add.up.order (tot.ltact!, tot.ord!, tot.ext!)
DECLARE SUB addmessage (invmsg1$, invmsg2$, invmsg3$, invmsg4$)
DECLARE SUB cf8 (L%, d.elem%, newdata$)
DECLARE SUB change.disc (discovr!)
DECLARE SUB chglin (ln%, L%, d.elem%, updwn%)
DECLARE SUB delOrder (hord%, n%, clr%, autodel$, thissup$, norders%)
DECLARE SUB dsply (sno%, norders%)
DECLARE SUB dsplyLine (L%, d.elem%)
DECLARE SUB dsporders (dspstart%, norders%, custin$)
DECLARE SUB ean13 (in$, dind%)
DECLARE SUB findnext (hord%, norders%, ok%)
DECLARE SUB findorders (thissup$, norders%, hord%)
DECLARE FUNCTION funclimit$ (climit!)
DECLARE SUB get.order.vs (hord%, updwn%)
DECLARE SUB getname (tender$, updwn%)
DECLARE SUB limit.warn (s90!, s60!, s30!, scur!, climit!, updwn%, allow$)
DECLARE SUB linkedl (rrn%(), n%, firstrec%, ord%, chd%)
DECLARE SUB loadLine (m%, il%, ditem%, ordqty%, invqty%, price!, unit!)

DECLARE SUB openpslip (opt%)
DECLARE SUB parse (hord%, opt%, cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, invmsg1$, invmsg2$)
DECLARE SUB prtinv (hord%, opt%, cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, OSCurrency$)
DECLARE SUB prtpslip (hord%, opt%, discovr!)
DECLARE SUB rightprice (price!)
DECLARE SUB search.month (rec%, begyymd$)
DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB setaudit (n%)
DECLARE SUB UpdateOrder (hord%, updwn%)

	'Added to try to set up sub programs ---
	COMMON SHARED C%(), in$(), rrn%()
	COMMON SHARED auditfile$(), orders%()

	COMMON SHARED mode$, beg$
	COMMON SHARED TaxRate!, DiscRate!
	COMMON SHARED maxsup%, maxform%, maxrmat%, maxacc%, maxtypes%, maxcus%, maxord%
	COMMON SHARED ext.has.changed%, rec50%, ctl%, cash%
	COMMON SHARED vdisc!, Rate!, discovr!, climit!, ovrPrice!
	COMMON SHARED tot.gst!, tot.ext!, tot.allup!
	COMMON SHARED skipexit%
	COMMON SHARED doc.type$, formtype$, sno%
	COMMON SHARED tot.ord!, tot.ltact, tot.ltinv, tot.dollr, tot.items&
	COMMON SHARED hord%
	COMMON SHARED newsearch$
	COMMON SHARED bysearch$
	COMMON SHARED search.key$
	COMMON SHARED tot.qty, Tot.taxvol
	COMMON SHARED tot.dg200%, tot.dg60%, tot.dg20%, tot.dg10%, tot.dg4%, tot.dg2%, tot.dg1%, tot.dg850%, tot.dg500%, tot.dg300%, tot.dg250%, tot.dglt!
	COMMON SHARED extdisc!, inv.lt.printed!
	COMMON SHARED tender$
	COMMON SHARED invmsg1$, invmsg2$, invmsg3$, invmsg4$
	COMMON SHARED qk$, keyl%, rep$
	COMMON SHARED naudit%, acstkf$
	COMMON SHARED ean$
	COMMON SHARED custin$
	COMMON SHARED nomatch%, unit!


'$INCLUDE: '.\SRC\pgmhead.inc'
	apgm$ = "CSMENU"
''$INCLUDE: '.\SRC\pgmerr.inc'
	CONST maxlines% = 45 '
	CONST GST! = 10  '10%

	DIM SHARED C%(8), in$(maxlines%, 17), rrn%(maxlines%)
	'1=qty%,2=size,3=unit,4=itm,5=desc,6=price,7=SOH,8=ext
	'9=tax flag,10=ordqty%,11=Invqty,12=BoFlag,13=save qty,14=Save item
	'15-unitprice, 16-OVERTYPE PRICE, 17-File Price

	DIM SHARED orders%(1001), auditfile$(15)

	keyl% = 24: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)

	DATA 2,7,10,13,18,56,63,72
	FOR i% = 1 TO 8: READ C%(i%): NEXT
	RESET
	typefields% = -1

'PD Comment - change to msrmat later
	acstkf$ = "..."
	parm$ = ENVIRON$("PARM$")
	IF VAL(parm$) > 0 THEN pass.getcust% = -1: custin$ = parm$: updwn% = 13

	parm2$ = ENVIRON$("PARM2$")
	IF parm2$ = "PRE..." THEN acstkf$ = "PRE"

		'$INCLUDE: '.\SRC\whof.inc'
		'$INCLUDE: '.\SRC\cusx.inc'
		'$INCLUDE: '.\SRC\supx.inc'
		'$INCLUDE: '.\SRC\sup.inc'
		'$INCLUDE: '.\SRC\MSRMAT.INC'
		'$INCLUDE: '.\SRC\ASAUDIT.INC'
		'$INCLUDE: '.\SRC\pordhed.inc'
		'$INCLUDE: '.\SRC\porddet.inc'
		'$INCLUDE: '.\SRC\pordprt.inc'


	SELECT CASE acstkf$
	CASE "PRE": CALL index("OPEN ", ind%, "msrmaty3.pre", 7, keyl%)
	CASE ELSE: CALL index("OPEN ", ind%, "msrmaty3.acf", 7, keyl%)
	END SELECT
		'$INCLUDE: '.\SRC\msmisc.inc'
		'$INCLUDE: '.\SRC\pickup.INC'
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxacc% = CVI(msmisc.max5$): maxtypes% = CVI(msmisc.max6$): maxcus% = CVI(msmisc.max7$)
	maxord% = 999
	chi% = 45

	CALL setaudit(naudit%)
	'cashonly$ = "M": auditname$ = auditfile$(naudit%)
	'GOSUB OPEN.AUDIT
	'CALL init
	'CLOSE # 8

start:
	CALL setup("PURCHASE ORDER/INVOICE")
	IF acstkf$ = "PRE" THEN
		CALL BOX(1, 2, 80, 24, 13, 0, 2)
		CALL SNDMSG("")
		LOCATE 23, 2: COLOR 0, 13: PRINT SPACE$(29); "--PREVIOUS PRICES-- " + SPACE$(29): COLOR 2, 0
	END IF

	btm$ = " F1-Exit.  *-All orders    F6-Browse    F7-Rebuild    F9-Counter   F10-New order"
	COLOR 8, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0

getcust:
	LOCATE 2, 22
	COLOR 7, 0: PRINT "ÍÍµ";
	COLOR 2, 0: PRINT "Enter Supplier......>"; custin$ + "     ";
	COLOR 7, 0: LOCATE 2, 51: PRINT "ÆÍÍÍÍÍ": COLOR 2, 0
	IF NOT pass.getcust% THEN
		LOCATE 2, 46
		CALL inpnew(custin$, 205!, updwn%, "13,59,64-65,68,72,80" + ALT$): GOSUB ALT
		IF MID$(custin$, 1, 1) = " " THEN custin$ = MID$(custin$, 2)
		custin$ = UCASE$(custin$)

		IF updwn% = 59 THEN : ENVIRON "PARM2$=......": CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
' PD - what is rebuild for sup?
		IF updwn% = 65 THEN CLOSE : bpgm$ = "ASBLD02": CALL EXITPGM(bpgm$): CHAIN bpgm$
		END IF
	pass.getcust% = 0

	IF updwn% = 64 THEN  'browse is a separate file?
		CALL browse.idx(p%, 45, 44)
		GET #chi%, p%, supx
		custin$ = supx.wcde$: updwn% = 13
		keyin$ = custin$: chi% = 45
		CALL searchindex(keyin$, chi%, found%)
		IF found% THEN sno% = CVI(supx.wrrn$)
		found% = 0
	END IF
	IF updwn% = 13 THEN
			IF VAL(custin$) > 0 THEN
				sno% = VAL(custin$)
				IF sno% < 1 OR sno% > maxsup% THEN sno% = 1
				GET #44, sno%, sup
				custin$ = sup.search$ + sup.stype$
				END IF
			keyin$ = custin$: chi% = 45
			CALL searchindex(keyin$, chi%, found%)
			IF custin$ = "*" THEN found% = -1
			IF found% THEN sno% = CVI(supx.wrrn$): CALL SNDMSG("")
			IF NOT found% THEN
					msg$ = "          Customer not found.  Use the Up/Down arrows to locate."
					CALL SNDMSG(msg$)
					COLOR 14, 0: LOCATE 24, 4: PRINT msg$;
					sno% = CVI(supx.wrrn$): custin$ = supx.wcde$
					SOUND 250, 1
					END IF
			END IF


	IF updwn% = 72 THEN 'Up arrow
		p% = LOC(chi%): p% = p% - 1: IF p% < 1 THEN p% = 1
		GET #chi%, p%, supx
		custin$ = supx.wcde$: updwn% = 13
		keyin$ = custin$: chi% = 45
		CALL searchindex(keyin$, chi%, found%)
		IF found% THEN sno% = CVI(supx.wrrn$)
		found% = 0
		END IF

	IF updwn% = 80 THEN 'Down arrow
		p% = LOC(chi%): p% = p% + 1
		GET #chi%, p%, supx
		custin$ = supx.wcde$: updwn% = 13
		keyin$ = custin$: chi% = 45
		CALL searchindex(keyin$, chi%, found%)
		IF found% THEN sno% = CVI(supx.wrrn$)
		found% = 0
		END IF


	IF sno% < 1 OR sno% > maxcus% THEN GOTO getcust
		CALL dsply(sno%, norders%)
		thissup$ = sup.search$ + sup.stype$
		IF custin$ = "*" THEN thissup$ = "*    "
		CALL findorders(thissup$, norders%, hord%)
		CALL dsply(sno%, norders%)
		dspstart% = 1
		CALL dsporders(dspstart%, norders%, custin$)
	clr% = 0
	DO UNTIL updwn% = 59
	IF clr% = 0 THEN in$ = ""
	IF clr% = 1 OR clr% = 3 THEN
		CALL setup("PURCHASE ORDERS/INVOICE")
		COLOR 8, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
		IF acstkf$ = "PRE" THEN
			CALL BOX(1, 2, 80, 24, 13, 0, 2)
			CALL SNDMSG("")
			LOCATE 23, 2: COLOR 0, 13: PRINT SPACE$(29); "--PREVIOUS PRICES-- " + SPACE$(29): COLOR 2, 0
		END IF

		CALL dsply(sno%, norders%)
		dspstart% = 1
		CALL dsporders(dspstart%, norders%, custin$)
		IF clr% = 3 THEN clr% = 0: EXIT DO
		clr% = 0
		END IF
	IF clr% = 2 THEN CALL BOX(2, 3, 79, 21, 7, 0, 0): clr% = 0
	IF emsg$ <> "" THEN COLOR 14, 0: LOCATE 21, 2: PRINT emsg$; CHR$(FNE): emsg$ = "": COLOR 2: updwn% = 59
	COLOR 2, 0
	IF NOT found% THEN GOTO getcust
getordnum:
	IF updwn% <> 68 THEN
		IF invnum# > 0 THEN
			LOCATE 24, 3: COLOR 7, 0: PRINT USING "µAudit/Inv:#,#### ########ÆÍ"; invnumrec%; invnum#; : COLOR 2, 0
		END IF

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
		IF custin$ <> "*" AND updwn% = 67 THEN cash% = -1: updwn% = 68
		IF VAL(in$) > 999 THEN in$ = MID$(in$, 1, 3)
		IF updwn% = 13 AND RTRIM$(in$) = "" THEN GOTO getordnum
		IF updwn% = 13 AND VAL(in$) = 0 THEN
			IF in$ = "0" THEN GOTO getordnum
			custin$ = UCASE$(in$)
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
	'mode$ = "ord"
	OSCurrency$ = "   "
	GOSUB detail '????
	opt$ = " "
	
	IF mode$ = "ord" THEN opt$ = "3"
	IF mode$ = "rec" THEN opt$ = "4"
	IF tot.ext = 0 THEN opt$ = "7"
exitmenu:
	DO

	SELECT CASE skipexit%
	CASE -1: opt$ = "": updwn% = 60
	CASE ELSE
		CALL BOX(17, 4, 63, 20, 6, 9, 1)
		COLOR 3, 1
		LOCATE 5, 28: PRINT "  E X I T    M E N U "
		COLOR 6, 1
		LOCATE 6, 28: PRINT ""
		LOCATE 7, 28: PRINT "1....Exit without update."
		IF mode$ <> "rec" THEN LOCATE 8, 28: PRINT "2....Print purchase order."
		IF mode$ <> "rec" THEN LOCATE 9, 28: PRINT "3....Receive goods and invoice. "
		IF mode$ = "rec" THEN LOCATE 10, 28: PRINT "4....Invoice received goods."
		'LOCATE 10, 28: PRINT "4....Invoice & backorder. "
		IF mode$ <> "rec" THEN LOCATE 11, 28: PRINT "5....Receive inward goods."
		IF mode$ <> "rec" THEN LOCATE 12, 28: PRINT "     and Invoice Later.   "
		LOCATE 13, 28: PRINT "6....Overtype price."
		IF tot.ext = 0 THEN LOCATE 14, 28: PRINT "7....Recieve toll goods"
		LOCATE 15, 28: PRINT "8....Enter message lines."
		IF mode$ <> "rec" THEN LOCATE 16, 28: PRINT "E....Import Sale. (Ex G.S.T.)"
		COLOR 14
		LOCATE 17, 22: PRINT cond.red$
		COLOR 2
		LOCATE 19, 28: PRINT "Option...> "
		COLOR 6, 1
		LOCATE 20, 20: PRINT "F1-Save & Exit.  F2-Save & Cont. F4-Cancel."
		LOCATE 19, 38: COLOR 2, 0
		CALL inpnew(opt$, 201!, updwn%, "13,59-60,62,68")
	END SELECT
	skipexit% = 0

	opt% = VAL(opt$)
	IF opt$ = "E" THEN opt% = 33
	IF opt$ = "e" THEN opt% = 33

	IF updwn% = 13 AND opt% = 0 THEN updwn% = 59
	IF updwn% = 59 AND mode$ = "ord" THEN opt% = 0
	IF updwn% = 59 AND mode$ = "rec" THEN opt% = 9
	IF updwn% = 60 THEN opt% = -1'F2 - Save & Cont
	IF updwn% = 62 THEN opt% = -2'F4 - Cancel the order


	LOOP UNTIL opt% >= -2 AND opt% <= 9 OR opt% = 33

	IF updwn% = 68 THEN GOSUB chgprev: GOTO exitmenu' F10 -Change invoice in audit file
	sav% = 0
	doc.type$ = "TAX INVOICE"
	formtype$ = "*PRE.PRINTED.1"


	IF opt% = -2 THEN mode$ = "del": sav% = 0
	IF opt% = -1 THEN mode$ = "ord": sav% = -1
	IF opt% = 0 THEN mode$ = "ord": sav% = -1
	IF opt% = 1 THEN mode$ = "nil ": sav% = 0
	IF opt% = 2 THEN mode$ = "ord": sav% = -1
	IF opt% = 3 THEN mode$ = "inv": sav% = -1
	IF opt% = 33 THEN mode$ = "inv": sav% = -1  'Inv No G.S.T.
	IF opt% = 4 THEN mode$ = "r-i": sav% = -1
	IF opt% = 5 THEN mode$ = "rec": sav% = -1:
	IF opt% = 6 THEN GOSUB change.price: GOTO exitmenu
	IF opt% = 7 THEN mode$ = "ing": sav% = -1:
	IF opt% = 9 THEN mode$ = "nil": sav% = -1

	GET #48, hord%, ordhed
	COLOR 6, 0:
	IF mode$ = "ord" AND ordhed.hreford$ = "            " THEN
		PCOPY 0, 1
		BEEP
		CALL get.order.vs(hord%, updwn%)
		PCOPY 1, 0
		GOTO exitmenu
	END IF
	IF mode$ = "ord" AND ordhed.htaxe$ = "        " THEN
		PCOPY 0, 1
		BEEP
		CALL get.order.vs(hord%, updwn%)
		PCOPY 1, 0
		GOTO exitmenu
	END IF
	
	IF opt% = 8 THEN
			CALL addmessage(invmsg1$, invmsg2$, invmsg3$, invmsg4$)
			GOTO exitmenu
	END IF
	'No need for our records
	'IF mode$ = "b/o" THEN CALL add.bo.msg(updwn%)

	IF opt% = 33 THEN  'Export Order (No GST)
		CALL getdt(OSCurrency$, updwn%)
		IF updwn% = 59 THEN GOTO exitmenu
		IF updwn% = 60 THEN GOTO exitmenu
		TaxRate! = 0
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
		TaxRate! = GST
	END IF

	IF sav% THEN
		CALL UpdateOrder(hord%, updwn%)
		IF updwn% = 60 THEN GOTO mline
	END IF

		'Enter invoice/delivery details - if canel here like receiving goods
		' Before updating order so can go back to mline if F1
		' after update so new items added to orders
		exitexit% = 0
		IF mode$ = "inv" OR mode$ = "r-i" OR mode$ = "b/o" THEN CALL invoiceentry(hord%, addate$, adnum$, status$, exitexit%)
		IF mode$ = "rec" OR mode$ = "ing" THEN CALL receivedelivery(hord%, hdddate$, hdocket$, exitexit%)
		IF exitexit% = -1 THEN
			exitexit% = 0
			GOTO exitmenu
		END IF


	'/// Print and exit or delete ///
		'- Only open the audit file when needed -<<
		cashonly$ = "M": auditname$ = auditfile$(naudit%)
		
		GOSUB OPEN.AUDIT '#8


		IF mode$ = "inv" THEN CALL prtinv(hord%, opt%, cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, OSCurrency$)
		IF mode$ = "b/o" THEN CALL prtinv(hord%, opt%, cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, OSCurrency$)

		

		CLOSE #8

		IF updwn% = 59 THEN
			ELSE
				IF mode$ = "b/o" THEN CALL prtpslip(hord%, opt%, discovr!)
				IF mode$ = "ord" THEN CALL prtpslip(hord%, opt%, discovr!)
		END IF
		
		'- Delete the order if it is fully invoiced

		anyDelDone% = 0

		IF NOT anyDelDone% THEN
		IF mode$ = "del" THEN
			autodel$ = "N"
			CALL delOrder(hord%, n%, clr%, autodel$, thissup$, norders%)
			anyDelDone% = -1
			CALL findorders(thissup$, norders%, hord%)
			IF updwn% = 59 THEN GOTO det'Delete aborted
			GOTO mlend
		END IF
		END IF

		
		IF NOT anyDelDone% THEN
		IF (mode$ = "inv") OR (status$ = "I" AND mode$ = "inv") OR mode$ = "ing" THEN
			autodel$ = "Y"
			CALL delOrder(hord%, n%, clr%, autodel$, thissup$, norders%)
			anyDelDone% = -1
			CALL findorders(thissup$, norders%, hord%)
		END IF
		END IF

		IF NOT anyDelDone% THEN
		IF mode$ = "inv" OR mode$ = "b/o" THEN
		IF sup.BO = "N" THEN
			autodel$ = "Y"
			CALL delOrder(hord%, n%, clr%, autodel$, thissup$, norders%)
			anyDelDone% = -1
			CALL findorders(thissup$, norders%, hord%)
		END IF
		END IF
		END IF

mlend:
	'- Change F1 to prevent the real mainline ending the program. <<
	updwn% = 13
	clr% = 3
RETURN

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
		
		TaxRate! = GST
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
RETURN

'-Change a previous invoice
chgprev:
		cashonly$ = "M": auditname$ = auditfile$(naudit%)
		IF cash% THEN cashonly$ = "Y"

		GOSUB OPEN.AUDIT '#8
		PCOPY 0, 1
		CALL BOX(12, 17, 71, 21, 7, 0, 2)
		prev$ = STR$(chginv#)
chgprev1:
		LOCATE 18, 16: PRINT "Invoice or Credit.> "
		LOCATE 19, 16: PRINT "Reference.........> "
		LOCATE 20, 16: PRINT "Start period end..> "
chgprev1a:
		in$ = "I": IF doc.type$ = "TAX CREDIT " THEN in$ = "C"
		LOCATE 18, 35
		CALL inpnew(in$, 101!, updwn%, "13,59")
		IF updwn% = 59 THEN GOTO xchgprev
		in$ = UCASE$(in$)
		IF in$ <> "I" AND in$ <> "C" THEN GOTO chgprev1a
chgprev1b:
		LOCATE 19, 35
		CALL inpnew(prev$, 209!, updwn%, "13,59-60")
		IF updwn% = 59 THEN GOTO xchgprev
		IF updwn% = 60 THEN GOTO chgprev1a
chgprev1c:
		LOCATE 20, 35
		CALL inpnew(beg$, 104!, updwn%, "13,59-60")
		IF updwn% = 59 THEN GOTO xchgprev
		IF updwn% = 60 THEN GOTO chgprev1b
		begyymd$ = "yyyymmdd"
		MID$(begyymd$, 7, 2) = "00"
		MID$(begyymd$, 5, 2) = MID$(beg$, 1, 2)
		MID$(begyymd$, 3, 2) = MID$(beg$, 3, 2)
		MID$(begyymd$, 1, 2) = "19"
		IF MID$(begyymd$, 3, 2) < "73" THEN MID$(begyymd$, 1, 2) = "20"

		CALL search.month(rec%, begyymd$)
		IF in$ = "I" THEN doc.type$ = "TAX INVOICE"
		IF in$ = "C" THEN doc.type$ = "TAX CREDIT "
		chginv# = VAL(prev$): chginv.rrn% = 0

		'- Search the file to make sure is exists
		ok% = 0
		GET #8, rec%, Audit
		DO WHILE NOT EOF(8)

			IF Audit.adcust$ = sup.search$ + sup.stype$ THEN
			IF doc.type$ = "TAX INVOICE" AND Audit.adtype$ = "DI" THEN
				IF VAL(Audit.addocnum$) = chginv# THEN chginv.rrn% = rec%: ok% = -1: EXIT DO
				END IF
			IF doc.type$ = "TAX CREDIT " AND Audit.adtype$ = "DC" THEN
				IF VAL(Audit.addocnum$) = chginv# THEN chginv.rrn% = rec%: ok% = -1: EXIT DO
				END IF
			END IF

			GET #8, , Audit: rec% = rec% + 1
			IF Audit.adtype$ = "PE" THEN EXIT DO
			LOOP

		IF NOT ok% THEN
			COLOR 14, 0
			LOCATE 20, 41: PRINT "Not found in period."
			COLOR 2, 0
			chginv# = 0: chginv.rrn% = 0
			GOTO chgprev1
			END IF
xchgprev:
	IF updwn% = 59 THEN doc.type$ = "TAX INVOICE"
	PCOPY 1, 0
	IF chginv# > 0 THEN
		COLOR 13, 0: LOCATE 3, 35
		IF doc.type$ = "TAX INVOICE" THEN PRINT USING "REVISE Inv########"; chginv#
		IF doc.type$ = "TAX CREDIT " THEN PRINT USING "REVISE Crt########"; chginv#
		COLOR 2, 0

		COLOR 10, 0
		LOCATE 4, 2: PRINT USING "##### \   \ \      \  \\   \           \ \                   \       $$,###.##"; Audit.adrec%; Audit.adcust$; FNDYY$(Audit.addate$); Audit.adtype$; Audit.addocnum$; Audit.adtext$; Audit.advalue
		COLOR 2, 0
		IF Audit.advalue <> 0 THEN
			SOUND 500, 10
			COLOR 12, 0: LOCATE 4, 67: PRINT "ÄÄÄ>": COLOR 2, 0
			END IF
		GET #48, hord%, ordhed
		ordhed.hdate$ = Audit.addate$
		PUT #48, hord%, ordhed
		END IF

	CLOSE #8
RETURN
'--L O A D   I N V O I C E   D E T A I L S
load.det:
	FOR L% = 1 TO maxlines%
		in$(L%, 1) = "0": in$(L%, 2) = "   ": in$(L%, 3) = "": in$(L%, 4) = "": in$(L%, 5) = "": in$(L%, 6) = "0"
		in$(L%, 7) = "0": in$(L%, 8) = "0": in$(L%, 9) = "N/": in$(L%, 10) = "0": in$(L%, 11) = "0": in$(L%, 12) = "N"
		in$(L%, 13) = "0": in$(L%, 14) = "0": in$(L%, 15) = "": in$(L%, 16) = "": in$(L%, 17) = ""
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
	SELECT CASE ordhed.hstatus$
		CASE "B": mode$ = "b/o"
		CASE "I": mode$ = "ing"
		CASE "O": mode$ = "ord"
		CASE "R": mode$ = "rec"
		CASE ELSE: mode$ = "ord"
	END SELECT
	
	nn% = -1: firstrec% = CVI(ordhed.hrrn$)
	CALL linkedl(rrn%(), nn%, firstrec%, hord%, 49)

	'-> Read through the linked list of the details file
	dnext% = CVI(ordhed.hrrn$)
	L% = 0: m% = 0
	DO WHILE dnext% > 0
		GET #49, dnext%, orddet
		L% = L% + 1: IF L% > maxlines% THEN L% = maxlines%: EXIT DO
		ditem% = CVI(orddet.ditem$)
		ordqty% = CVI(orddet.dordq$)
		invqty% = CVI(orddet.dinvq$)
		price! = CVS(orddet.dprice$)
		unit! = CVS(MID$(orddet.dfiller$, 1, 4))
		CALL ROUND(unit!, 2.5)
		'Code to display received amount in the Qty column ???
		'IF mode$ = "rec" THEN ordqty% = invqty%
		IF ordqty% > 0 OR invqty% > 0 THEN
			m% = m% + 1
			CALL loadLine(m%, -1, ditem%, ordqty%, invqty%, price!, unit!)'initial load
		END IF
		'- Bottom of read equal loop
		dnext% = orddet.drrn%
	LOOP
	'Clear out items above loaded number.
	s% = m% + 1
	FOR m% = s% TO L%
		invqty% = 0
		ordqty% = 0
		ditem% = 0
		CALL loadLine(m%, -1, ditem%, ordqty%, invqty%, price!, unit!)
	NEXT

	TaxRate! = GST
	CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
RETURN

detail:
	CALL setup("O R D E R    E N T R Y")
	btma$ = "F1-Save/Print.   F5-Prices     F6-Browse "
	COLOR 8, 3: LOCATE 25, 1: PRINT btma$;
	IF acstkf$ = "PRE" THEN
		CALL BOX(1, 2, 80, 24, 13, 0, 2)
		CALL SNDMSG("")
		LOCATE 23, 2: COLOR 0, 13: PRINT SPACE$(29); "--PREVIOUS PRICES-- " + SPACE$(29): COLOR 2, 0
	END IF

	'Reset the order to blanks
	TaxRate! = GST
	CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
	IF tot.exe! <> 0 THEN BEEP: CALL SNDMSG("Empty order has a dollar value!"): BEEP

	d.elem% = 1'Start at element number 1.
	scrn.pag% = 1
	L% = 1
detail.a:
	IF updwn% = 73 THEN L% = d.elem%'page up
	IF updwn% = 81 THEN L% = d.elem%'page down
	e.elem% = d.elem% + 14
	IF e.elem% > maxlines% THEN e.elem% = maxlines%
	COLOR 7, 0: LOCATE 2, 2: PRINT "µ": LOCATE 2, 79: PRINT "Æ"
	COLOR 2, 0:
	LOCATE 2, 3: PRINT USING " Order:####"; hord%;
	a$ = "  " + LEFT$(sup.sname$, 20) + " " + LEFT$(sup.scont$, 20) + " " + sup.search$ + sup.stype$ + "  "
	COLOR 2
	PRINT a$
	COLOR 2

	LOCATE , 2: COLOR 6, 0: PRINT "Qty. Size   No.  Description                  Unit     Price  Revi'd   Value"

	COLOR 2
	LOCATE , 2: COLOR 2, 0: PRINT "ÄÄÄÄÂÄÄÄÄÄÂÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄ"
	LOCATE , 2: COLOR 10: PRINT USING "p #"; scrn.pag%: COLOR 2
	sav.l% = L%
	FOR L% = d.elem% TO e.elem%
		CALL dsplyLine(L%, d.elem%)
		NEXT
	L% = sav.l%
	LOCATE , 2: COLOR 2, 0: PRINT "ÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄ"

	COLOR 2
	LOCATE 21, 23: PRINT USING "D-Docket: \        \"; ordhed.hdocket$
	LOCATE 22, 23: PRINT USING "Del Date: \      \  "; FNDYY$(ordhed.hdddate$)

	LOCATE 23, 2: PRINT USING "PO Num.>\          \ Due date.>\        \"; ordhed.hreford$; FNDYY$(ordhed.htaxe$)

	'--Get line entries
	updwn% = 0
	sav.scrn.pag% = scrn.pag%
	DO WHILE updwn% <> 59 AND sav.scrn.pag% = scrn.pag%
		ln% = (L% - d.elem%) MOD 15 + 1: ln% = ln% + 4
		CALL chglin(ln%, L%, d.elem%, updwn%)
		IF updwn% = 62 THEN EXIT DO   'F4 - Delete
		IF updwn% = 60 THEN L% = L% - 2'F2 - Back one line
		IF updwn% = 72 THEN L% = L% - 2'/\ - Back up one line
		IF updwn% = 73 THEN L% = L% - 16'Page up one screen
		IF updwn% = 81 THEN L% = L% + 16'Page down one screen

		IF updwn% = 72 AND L% = -1 THEN 'end- Find next unused line
				L% = maxlines% + 1
				DO UNTIL VAL(in$(L% - 1, 1)) <> 0
					L% = L% - 1
					IF L% = 1 THEN EXIT DO
					LOOP
				L% = L% - 1
				END IF
		L% = L% + 1
		IF L% > maxlines% THEN L% = maxlines%
		sav.scrn.pag% = scrn.pag%
		SELECT CASE L%
		CASE 31 TO 45: d.elem% = 31: scrn.pag% = 3
		CASE 16 TO 30: d.elem% = 16: scrn.pag% = 2
		CASE ELSE: d.elem% = 1: scrn.pag% = 1
		END SELECT
		IF L% > maxlines% THEN L% = maxlines%' Past end of data
		IF L% < 1 THEN L% = 1              ' Before start of data
		IF L% > d.elem% + 14 THEN L% = d.elem% + 15' Past end of screen
		IF L% < d.elem% THEN L% = d.elem%  ' Before start of screen
		LOOP
	IF sav.scrn.pag% <> scrn.pag% AND updwn% <> 59 THEN GOTO detail.a
RETURN

SUB accbrowse (rec%) STATIC

	 CALL setup("  B R O W S E    F I L E")
	 btype$ = "cost"
	 cbtm$ = " No.Stock description.        Search    Size   Code   Pur.      Use.   S.O.H."
	 kbtm$ = " No.Stock description.                  Size  Distr. COGS    GPC   RMC    GPR "
	 dbtm$ = " No.Stock description.                  Size  Code  A D Barcode       Search  "
	 COLOR 6: LOCATE 3, 2: PRINT cbtm$
	 COLOR 0, 3: LOCATE 25, 1: PRINT SPACE$(80);
	 COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit   F3=Search     F5-Swap     F6-Search Duplicate Barcodes"; : LOCATE 25, 71: PRINT CHR$(24); CHR$(25); "-Move"; : COLOR 2, 0
	 maxpag% = 20
	 IF rec% < 1 OR rec% > maxacc% THEN rec% = 1
	 updwn% = 13: bpos$ = STR$(rec%)
	 xsearch$ = ""
	 showdup% = 0
	 skip$ = "Y"
	 REDIM bar#(maxacc%)
	 cleanbar% = 0

	 '>>>>> Get next REC%ord to browse from.
accBROWSE.A:
	LOCATE 2, 25
	COLOR 7: PRINT "¹ ";
	COLOR 2: PRINT "Start browse from..>      ";
	COLOR 7: PRINT "Ì": COLOR 2
	COLOR 2
	IF skip$ = "Y" THEN
		skip$ = "N"
	ELSE
		bpos$ = ""
		LOCATE 2, 47: CALL inpnew(bpos$, 205!, updwn%, "13,59,61,63-64,68,72,73,80,81")
	END IF

	IF updwn% = 61 THEN
		LOCATE 2, 25: PRINT "Search..>";
		CALL inpnew(xsearch$, 120!, updwn%, "13,59,61,63-64,72,73,80,81")
		bpos$ = "1"
		updwn% = 13
	END IF


	IF updwn% = 13 THEN
			IF VAL(bpos$) = 0 AND LEN(bpos$) > 0 THEN
				keyl% = 24: qk$ = SPACE$(keyl%)
				sa$ = bpos$
				sa$ = UCASE$(sa$): LSET qk$ = sa$
				CALL index("CHAIN", ind%, qk$, 7, keyl%)
				IF ind% < 0 AND qk$ < sa$ THEN CALL index("READ ", ind%, qk$, 7, keyl%)
				bpos$ = MID$(STR$(ind%), 2)
			END IF

			IF VAL(bpos$) = 0 THEN bpos$ = STR$(e%)
			rec% = VAL(bpos$)
			IF rec% < 1 OR rec% > maxacc% THEN rec% = 1
	END IF
	IF updwn% = 59 THEN rec% = s%: GOTO X.accbrowse
	IF updwn% = 63 THEN '***** Swap browse type
		COLOR 6: LOCATE 3, 2
		SELECT CASE btype$
		CASE "cost": btype$ = "key ": PRINT kbtm$
		CASE "key ": btype$ = "data": PRINT dbtm$
		CASE "data": btype$ = "cost": PRINT cbtm$
		END SELECT
		COLOR 2, 0
		rec% = s%
	END IF

	IF updwn% = 72 THEN 'UP arrow
		lin% = 1
		rec% = s%
		DO WHILE lin% > 0 AND rec% > 1
			rec% = rec% - 1
			GET #38, rec%, msrmat
			IF msrmat.no% = rec% THEN lin% = lin% - 1
			LOOP
	END IF
	IF updwn% = 80 THEN 'Down arrow
		rec% = s% + 1
		GET #38, rec%, msrmat
		DO WHILE msrmat.no <> rec% AND rec% < maxrmat%
			rec% = rec% + 1
			GET #38, rec%, msrmat
			LOOP

	END IF
	IF updwn% = 73 THEN 'pg up
		lin% = maxpag%
		rec% = s%
		DO WHILE lin% > 0 AND rec% > 1
			rec% = rec% - 1
			GET #38, rec%, msrmat
			IF msrmat.no% = rec% THEN lin% = lin% - 1
			LOOP
	END IF
	IF updwn% = 81 THEN 'pg dw
		rec% = e% + 1
	END IF


'///////////////////////////////////////////////////////////////////////////
'>>--- L I S T   A   P A G E
'///////////////////////////////////////////////////////////////////////////
	'Given rec% as the first record
	GET #38, rec%, msrmat
	lin% = 0: missed% = 0
	DO UNTIL lin% = maxpag% OR rec% > maxrmat%'OR missed% > 400

		'Selection
		ok% = -1
		IF msrmat.no% <> rec% THEN ok% = 0
		IF msrmat.search$ <> custin$ THEN ok% = 0
		IF btype$ = "key " AND UCASE$(msrmat.Active$) <> "A" THEN ok% = 0

		IF showdup% THEN
			ok% = 0
			IF msrmat.ean13 > 0 THEN
				FOR i% = 1 TO maxrmat%
					IF bar#(i%) = msrmat.ean13 AND i% <> rec% AND msrmat.ean13 > 0 THEN
						ok% = -1
						EXIT FOR
					END IF
				NEXT
			END IF
		END IF

		IF ok% AND xsearch$ > "" THEN
			ok0% = 0
			IF ok0% = 0 AND INSTR(LCASE$(msrmat.Desc1$), LCASE$(xsearch$)) > 0 THEN ok0% = -1
			IF ok0% = 0 AND INSTR(LCASE$(msrmat.Desc2$), LCASE$(xsearch$)) > 0 THEN ok0% = -1
			IF NOT ok0% THEN ok% = 0
		END IF


		IF ok% THEN prttype$ = btype$
		IF NOT ok% THEN prttype$ = "missed"
		bc$ = " ": IF msrmat.ean13 > 9300 THEN bc$ = CHR$(127)

		'force prttype
		IF prttype$ <> "missed" THEN prttype$ = "cost"
		SELECT CASE prttype$
		CASE "cost"
			LOCATE 4 + lin%, 2
			PRINT USING "####\                       \ \       \!####\\ \  \#####.## #####.##  ###,###"; msrmat.no%; msrmat.Desc1$; MID$(msrmat.searchs$, 1, 10); bc$; msrmat.supqty; msrmat.PurUnit$; msrmat.search$; msrmat.PurCost; msrmat.UseCost; msrmat. _
soh

			COLOR 3, 0
			LOCATE 4 + lin%, 2 + 47
			PRINT USING "\  \"; msrmat.search$
			LOCATE 4 + lin%, 2
			PRINT USING "####"; msrmat.no%
			COLOR 2, 0
			COLOR 10, 0: LOCATE 4 + lin%, 41: PRINT bc$; : COLOR 2, 0'BC

			lin% = lin% + 1
			IF lin% = 1 THEN s% = rec%
			e% = rec%
		CASE "key "

		CASE "missed"
			missed% = missed% + 1
		END SELECT

	bad% = 0

	GET #38, , msrmat: rec% = rec% + 1
	LOOP


	FOR i% = lin% + 1 TO maxpag%: LOCATE 3 + i%, 2: PRINT SPACE$(78): NEXT


	GOTO accBROWSE.A   '***** Get next REC%ord to browse from

X.accbrowse:

END SUB

SUB add.bo.msg (updwn%)
'Add item 2 "GOODS ON BACKORDER"
'or  "BACKORDER NOT REQUIRED" (Item 3)
ditem% = 2
IF sup.BO = "N" THEN ditem% = 3

ordqty% = 1
invqty% = 1
price! = 0

m% = 0
found% = 0
FOR i% = 1 TO maxlines%
	IF VAL(in$(i%, 4)) = 0 THEN m% = i%: found% = -1: EXIT FOR
NEXT

IF found% THEN
	CALL loadLine(m%, 0, ditem%, ordqty%, invqty%, price!, unit!)
END IF

END SUB

SUB add.up.order (tot.ltact!, tot.ord!, tot.ext!) STATIC

add.up.order:
	'- Add up total litres and calc discount $
	tot.ltact = 0
	tot.ext = 0
	tot.items& = 0
	tot.tax = 0
	FOR i% = 1 TO maxlines%
		'- Add up litres order and actualy on order
		ltact = 0
		qty = VAL(in$(i%, 1))
		size! = VAL(in$(i%, 2))
		IF in$(i%, 3) = "LT" THEN ltact = qty * size!
		IF in$(i%, 3) = "ML" THEN ltact = qty * size! / 1000
		IF in$(i%, 3) = "KL" THEN ltact = qty * size!
		tot.ltact = tot.ltact + ltact
		ext! = VAL(in$(i%, 8))
		tot.ext = tot.ext + ext!
		tot.items& = tot.items& + qty
	NEXT

	'- Set the total litres ever placed on this order
	tot.ord! = CVS(ordhed.horgq$)
	IF tot.ltact! > tot.ord! THEN tot.ord! = tot.ltact!
	IF discovr! <> 0 THEN tot.ord! = discovr!

	'- Calculate the volume discount
	a = tot.ord!
	IF sup.stype$ = "W" THEN a = 0
	CALL ROUND(a, .5)
	vdisc! = 0: DiscRate! = 0

	'- Round the very bottom price for cash items
	IF cash% AND 1 = 2 THEN

		'Start a +10Cents and step back to -10Cents.
			tot.allup = tot.ext - vdisc!
			temptotal = tot.allup
			tot.gst! = temptotal * (TaxRate! / 100): CALL ROUND(tot.gst!, 2.5)
			tot.allup = temptotal + tot.gst!
			
			cents! = tot.allup - FIX(tot.allup)
			cents% = cents! * 100
			
			IF cents% MOD 5 = 0 THEN   'Until 5 Cent round
			END IF
	END IF


	'- Print out bottom line of the invoice
	tot.allup = tot.ext - vdisc!
	temptotal = tot.allup
	tot.gst! = temptotal * (TaxRate! / 100): CALL ROUND(tot.gst!, 2.5)

	'>-- The price may be overwritten
	IF ovrPrice! <> -9999 THEN
		tot.allup! = ovrPrice!
		tot.gst! = tot.allup! / 11: CALL ROUND(tot.gst!, 2.5)
		temptotal = tot.allup! - tot.gst!
		vdisc! = tot.ext! - (tot.allup! - tot.gst!)
	END IF
	
	tot.allup = temptotal + tot.gst!
	COLOR 2, 0
	LOCATE 21, 2: PRINT USING "Ordered :###,###"; tot.ord!
	LOCATE 21, 45: PRINT USING "Sub Total               $$######.##"; tot.ext
	LOCATE 22, 2: PRINT USING "Actual  :###,###"; tot.ltact
	LOCATE 22, 45: PRINT USING "Volume discount          $$#####.##"; vdisc
	LOCATE 23, 45: PRINT USING "G.S.T                    $$#####.##"; tot.gst!
	
	COLOR 7, 0
	LOCATE 24, 69: PRINT USING "µ$$#####.##º"; tot.allup; : COLOR 2, 0
	COLOR 10, 0:
	LOCATE 24, 70: PRINT USING "$$#####.##"; tot.allup; : COLOR 2, 0
	COLOR 2, 0

	ext.has.changed% = 0

END SUB

SUB addmessage (invmsg1$, invmsg2$, invmsg3$, invmsg4$)
		PCOPY 0, 1
		CALL BOX(12, 16, 71, 19, 7, 0, 2)

		LOCATE 17, 16: PRINT "Message..>"; invmsg1$
		LOCATE , 16: PRINT "         >"; invmsg2$
cmsg1:
		LOCATE 17, 26: CALL inpnew(invmsg1$, 142!, updwn%, "13,59,60")
		IF updwn% = 59 THEN GOTO xmessage
		IF updwn% = 60 THEN GOTO xmessage
cmsg2:
		LOCATE 18, 26: CALL inpnew(invmsg2$, 142!, updwn%, "13,59,60")
		IF updwn% = 59 THEN GOTO xmessage
		IF updwn% = 60 THEN GOTO cmsg1
		GOTO xmessage
xmessage:
		PCOPY 1, 0

END SUB

SUB cf8 (L%, d.elem%, newdata$)
REDIM x20%(20)
'--EXTENSION
cf8:
	qty! = VAL(in$(L%, 1))
	size! = VAL(in$(L%, 2))
	price! = VAL(in$(L%, 6))
	received! = VAL(in$(L%, 11))
	'>-- Stock items 1-20 are special reusable items
	IF VAL(in$(L%, 4)) = 1 AND ctl% = 4 THEN

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

		in$(L%, 4) = STR$(spec%)

		d.elem% = 1' this is hard coded
		ln% = (L% - d.elem%) MOD 15 + 1: ln% = ln% + 4'+4 Lines from the top of the screen
		LOCATE ln%, C%(4): PRINT USING "####"; spec%

		LOCATE ln%, C%(5): PRINT msrmat.Desc1$; " "; msrmat.Desc2$
		dkt$ = msrmat.Desc1$
		LOCATE ln%, C%(5)
		CALL inpnew(dkt$, 125!, updwn%, "13,60")
		LSET msrmat.Desc1$ = dkt$
		dkt$ = msrmat.Desc2$

		LOCATE ln%, C%(5) + 26
		CALL inpnew(dkt$, 110!, updwn%, "13,60")
		LSET msrmat.Desc2$ = dkt$
		LOCATE ln%, C%(5): PRINT msrmat.Desc1$; " "; msrmat.Desc2$
		in$(L%, 5) = msrmat.Desc1$ + " " + msrmat.Desc2$

		LOCATE ln%, C%(6)
		in$(L%, 6) = STR$(msrmat.PurCost!)
								CALL inpnew(in$(L%, 6), 5.2, updwn%, "13")
		price! = VAL(in$(L%, 6))

		TaxRate! = GST
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)

		ctl% = 6
	END IF
	'-
	old.ext! = VAL(in$(L%, 8))
	ext! = (qty! + received!) * price!
	in$(L%, 8) = STR$(ext!)
	IF old.ext! <> ext! THEN ext.has.changed% = -1

END SUB

SUB change.disc (discovr!)
change.disc:
		LOCATE 21, 12
		in$ = STR$(discovr!)
		CALL inpnew(in$, 5!, updwn%, "13,59")
		discovr! = VAL(in$)
END SUB

SUB delOrder (hord%, n%, clr%, autodel$, thissup$, norders%)
delOrder:
	IF autodel$ <> "Y" THEN
		COLOR 0, 7: LOCATE 25, 1: PRINT SPACE$(80);
		COLOR 0, 7: LOCATE 25, 20: PRINT "F1 - Exit.        F10 - Continue.";
		LOCATE 1, 1
		CALL inpnew(in$, 0!, updwn%, "59,68")
		IF updwn% = 59 THEN GOTO x.delOrder
		END IF
	autodel$ = "N"

	'-Count the details
	FOR L% = 1 TO maxlines%
		IF VAL(in$(L%, 4)) <> 0 THEN n% = L%
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
	LSET ordhed.hdocket$ = SPACE$(10)
	LSET ordhed.hdddate$ = SPACE$(8)
	LSET ordhed.hstatus$ = SPACE$(1)
	PUT #48, hord%, ordhed
	hord% = 0

	'If a special item is used (stock # <20) delete it.
	FOR L% = 1 TO maxlines%
		i% = VAL(in$(L%, 4))
	'  IF i% >= 1 AND i% <= 20 THEN
	'    GET #38, i%, msrmat
	'    msrmat.no = 0
	'    msrmat.desc1$ = ""
	'    msrmat.desc2$ = ""
	'    PUT #38, i%, msrmat
	'  END IF
	'
		'-Update the stock file (remove previous)
		sooqty% = VAL(in$(L%, 13))
		svrrn% = VAL(in$(L%, 14))
		IF svrrn% >= 1 AND svrrn% <= maxacc% THEN
			GET #38, svrrn%, msrmat
			msrmat.soo = msrmat.soo - sooqty%
			PUT #38, svrrn%, msrmat
		END IF
	
	NEXT

	clr% = 1
x.delOrder:

END SUB

SUB dsply (sno%, norders%) STATIC
dsply:
	IF sno% < 1 OR sno% > maxcus% THEN GOTO x.dsply
	GET #44, sno%, sup
	scur = CVS(sup.scur$): s30 = CVS(sup.s30$): s60 = CVS(sup.s60$): s90 = CVS(sup.s90$)
	sdays% = CVI(sup.sdays$): climit = CVS(sup.climit$)
	sterms = CVS(sup.sterms$): daysmax% = CVI(sup.daysmax$)
	rec50% = VAL(sup.spname$)
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
	LOCATE 3, 3: PRINT USING "& & & &&"; LEFT$(sup.sname$, 30); LEFT$(sup.scont$, 25); LEFT$(sup.sphone$, 13); sup.search$; sup.stype$
	COLOR 7: LOCATE 4, 2: PRINT "ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ": COLOR 2
	LOCATE 5, 2: PRINT USING " \                                  \  Deliver:\                            \"; sup.saddr$; PICKUP.pname1$
	LOCATE 6, 2: PRINT USING " \                                  \          \                            \"; sup.saddr2$; PICKUP.pname2$
	LOCATE 7, 2: PRINT USING " \                  \           \   \          \                            \"; sup.suburb$; sup.spcode$; PICKUP.pname3$
	COLOR 6, 0
	LOCATE 5, 41: PRINT "Deliver:"
	COLOR 2, 0
	
	COLOR 6
	SELECT CASE daysmax%
	CASE 1: LOCATE 8, X0%: PRINT USING "Terms:## day for ##% discount. "; daysmax%; sterms
	CASE ELSE: LOCATE 8, X0%: PRINT USING "Terms:## days for ##% discount."; daysmax%; sterms
	END SELECT

	COLOR 10, 0: LOCATE 8, 49
	IF sup.BO$ = "Y" THEN
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
	CALL BOX(2, 12, 79, 23, 7, 0, 0)
	LOCATE 11, 25: PRINT "Orders found for this supplier"
	COLOR 6, 0
	IF norders% < 10 THEN
	LOCATE , 3: PRINT "Num. Type Ord.. Inv..  Order    Dollars. Date....  Order Reference Due Date"
	ELSE
	 LOCATE , 2: PRINT "Num Date. Cust. Ref...... Num Date. Cust. Ref...... Num Date. Cust. Ref......"
	END IF

	COLOR 2, 0

	'- Set cash sale mode
	cash% = 0
' PD Comment out
'  IF sup.search = "CASH" THEN cash% = -1

x.dsply:

END SUB

SUB dsplyLine (L%, d.elem%) STATIC
		ln% = (L% - d.elem%) MOD 15 + 1: ln% = ln% + 4'+4 Lines from the top of the screen
		COLOR 2, 0
		qty% = VAL(in$(L%, 1))
		IF qty% < 1 AND VAL(in$(L%, 11)) < 1 OR qty% > 9999 THEN
			LOCATE ln%, 2
			PRINT "    ³     ³    ³                            ³       ³       ³       ³         "
		ELSE
			qty% = VAL(in$(L%, 1))
			msrmat.supqty! = VAL(in$(L%, 2))
			LSET msrmat.SupUnit$ = in$(L%, 3)
			ano% = VAL(in$(L%, 4))
			
			LSET msrmat.Desc1$ = in$(L%, 5)
			LSET msrmat.Desc2$ = MID$(in$(L%, 5), LEN(msrmat.Desc1$) + 2, 10)
			newdata$ = "N": CALL cf8(L%, d.elem%, newdata$)
			unit! = VAL(in$(L%, 16))
			price! = VAL(in$(L%, 6))
			'soh is not received "invqty"
			soh = VAL(in$(L%, 11)) ' not 7
			ext! = VAL(in$(L%, 8))

			'- On BO
			IF in$(L%, 12) = "Y" THEN
				COLOR 10
			END IF
			'- Condition red
			IF ext! <= .01 AND qty% > 0 AND ano% > 0 THEN
				COLOR 4
				'SOUND 250, 10
				cond.red$ = "There are zero values on the invoice"
			ELSE
				cond.red$ = ""
			END IF
			purqtydsply$ = ""
			
			SELECT CASE LEN(LTRIM$(RTRIM$(STR$(msrmat.supqty!))))
				CASE 1: a$ = "³  " + LTRIM$(RTRIM$(STR$(msrmat.supqty!))) + msrmat.SupUnit$ + "³"
				CASE 2: a$ = "³ " + LTRIM$(RTRIM$(STR$(msrmat.supqty!))) + msrmat.SupUnit$ + "³"
				CASE 3: a$ = "³" + LTRIM$(RTRIM$(STR$(msrmat.supqty!))) + msrmat.SupUnit$ + "³"
				CASE 4: a$ = "³" + LTRIM$(RTRIM$(STR$(msrmat.supqty!))) + MID$(msrmat.SupUnit$, 1, 1) + "³"
				CASE 5: a$ = "" + LTRIM$(RTRIM$(STR$(msrmat.supqty!))) + msrmat.SupUnit$ + ""
				CASE 6: a$ = "³" + LTRIM$(RTRIM$(STR$(msrmat.supqty!))) + MID$(msrmat.SupUnit$, 1, 1) + ""
				CASE 7: a$ = "" + LTRIM$(RTRIM$(STR$(msrmat.supqty!))) + "" + ""
			END SELECT

			'a$ = "³" + purqtydsply$ + msrmat.SupUnit$ + "³"
			B$ = "³" + msrmat.Desc1$ + "   " + "³"
			C$ = "³"
			'IF ditem% > 0 AND ditem% < maxacc% THEN
			testa = 0
			testb = 0
			testa = VAL(in$(L%, 16))
			CALL ROUND(testa, 2.5)
			CALL ROUND(VAL(in$(L%, 17)), 2.5)
			testb = (testa - VAL(in$(L%, 17)))
			CALL ROUND(testb, 2.5)
			IF testa > 0 AND testb <> 0 THEN
				COLOR 14
			ELSE
				COLOR 2
				END IF
			
			'END IF
			LOCATE ln%, 2: PRINT USING "####"; qty%
			LOCATE ln%, 6: PRINT a$;
			LOCATE ln%, 13: PRINT USING "####"; ano%
			LOCATE ln%, 17: PRINT B$;
			LOCATE ln%, 47: PRINT USING "####.##"; unit!;
			LOCATE ln%, 54: PRINT C$;
			IF price! < 9999.99 THEN
				LOCATE ln%, 55: PRINT USING "####.##"; price!;
			ELSE
				LOCATE ln%, 55: PRINT USING "#####.#"; price!;
			END IF
			LOCATE ln%, 62: PRINT C$;
			IF soh <> 0 THEN
			LOCATE ln%, 63: PRINT USING "###,###"; soh;
			ELSE
			LOCATE ln%, 63: PRINT USING "\     \"; SPACE$(7);
			END IF
			COLOR 2
			
			IF testa > 0 AND testb <> 0 THEN
				COLOR 14
			ELSE
				COLOR 2
			END IF
			LOCATE ln%, 70: PRINT C$;
			LOCATE ln%, 71: PRINT USING "######.##"; ext!
		END IF
		'put green lines in
		COLOR 2
		LOCATE ln%, 6: PRINT "³"
		LOCATE ln%, 12: PRINT "³"
		LOCATE ln%, 17: PRINT "³"
		LOCATE ln%, 46: PRINT "³"
		LOCATE ln%, 54: PRINT "³"
		LOCATE ln%, 62: PRINT "³"
		LOCATE ln%, 70: PRINT "³"

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
		SELECT CASE ordhed.hstatus$
			CASE "B": a$ = "B/o."
			CASE "I": a$ = "TollR"
			CASE "O": a$ = "Ord."
			CASE "R": a$ = "Recvd"
		END SELECT
		IF custin$ = "*" THEN a$ = " <" + ordhed.hsup$ + ">"
		a = CVS(ordhed.horgq$)
		IF discovr! <> 0 THEN a = discovr!
		LOCATE y%, X%
		IF norders% < 10 THEN
		PRINT USING "### \   \ ###### ##### ######$$#######.## \      \  \             \ \      \"; CVI(ordhed.hord$); a$; a; CVS(ordhed.hinvq$); CVS(ordhed.hordq$); CVS(ordhed.hdollar$); FNDYY$(ordhed.hdate$); ordhed.hreford$; FNDYY$(ordhed.htaxe$)
		ELSE

		PRINT USING "### \   \ \   \ \      \"; CVI(ordhed.hord$); FNDYY$(ordhed.hdate$); ordhed.hsup$; FNDYY$(ordhed.htaxe$)
		END IF

		END IF
		NEXT


END SUB

SUB ean13 (in$, dind%)
	thsEan# = VAL(in$)
	found% = 0

	dind% = 1
	GET #38, dind%, msrmat
	DO WHILE NOT EOF(3) AND dind% <= maxacc%
		IF acstk.ean13 = thsEan# THEN
			found% = -1
			EXIT DO
		END IF
		GET #38, , msrmat: dind% = dind% + 1
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
		'LSET ordhed.htaxe$ = sup.taxe$
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
		LSET ordhed.hdocket$ = SPACE$(10)
		LSET ordhed.hstatus$ = SPACE$(1)

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
			keyin$ = skey$: chi% = 45
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

TX1:
		a$ = ordhed.hreford$
		LOCATE 23, 10: CALL inpnew(a$, 112!, updwn%, "13,59-60")
		IF updwn% = 59 THEN GOTO x.get.order.vs
		IF updwn% = 60 THEN GOTO x.get.order.vs
		LSET ordhed.hreford$ = a$
TX2:
		 a$ = FNDYY$(ordhed.htaxe$)
		 IF MID$(a$, 1, 8) = "  /  /  " THEN
			a$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
		 END IF
		 LOCATE 23, 33: CALL inpnew(a$, 100!, updwn%, "13,59-60")
		 LSET ordhed.htaxe$ = FNDY$(a$)
		 IF updwn% = 59 THEN GOTO x.get.order.vs
		 IF updwn% = 60 THEN GOTO TX1
x.get.order.vs:
		PUT #48, hord%, ordhed
END SUB

SUB getdt (OSCurrency$, updwn%)
getdt.name:
		REDIM osd$(5)
		osd$(1) = "USD"
		osd$(2) = "PPS"
		osd$(3) = "SID"
		osd$(4) = "yyy"
		osd$(5) = "zzz"
		PCOPY 0, 1
		COLOR 2, 0
		CALL BOX(28, 9, 52, 16, 7, 0, 2)
		LOCATE 10, 30: PRINT "OS Currency.> "
		FOR i% = 1 TO 5
		LOCATE , 30: PRINT USING "## &"; i%; osd$(i%)
		NEXT

getdt.tender:
		OSCurrency$ = ""
		LOCATE 10, 43: CALL inpnew(OSCurrency$, 101!, updwn%, "13,59")
		IF updwn% = 59 THEN GOTO getdt.xname


		IF INSTR("1,2,3,4,5,", OSCurrency$ + ",") <= 0 THEN GOTO getdt.tender
		OSCurrency$ = osd$(VAL(OSCurrency$))

getdt.xname:
		PCOPY 1, 0

END SUB

SUB getname (tender$, updwn%)
get.name:
		PCOPY 0, 1
		CALL BOX(24, 9, 52, 16, 7, 0, 2)
		LOCATE 10, 28: PRINT "Tender.>?"
		LOCATE 11, 28: PRINT "        1.Cash"
		LOCATE 12, 28: PRINT "        2.Cheque"
		LOCATE 13, 28: PRINT "        3.Credit card"
		LOCATE 14, 28: PRINT "        4.Counter"
		LOCATE 15, 28: PRINT "        9.Type Desc"


tender:
		tender$ = "?"
								LOCATE 10, 36: CALL inpnew(tender$, 101!, updwn%, "13,59")
		IF updwn% = 59 THEN GOTO xname

		'- Sname
		IF tender$ = "9" THEN
			CALL BOX(3, 17, 78, 21, 7, 0, 2)
			LOCATE 18, 5: PRINT USING "Name...>\                        \"; LEFT$(sup.sname$, 30)
			LOCATE , 5: PRINT USING "Address..>\                  \"; sup.saddr$
			LOCATE , 5: PRINT USING "Suburb...>\                  \"; sup.suburb$
tender1:
			a$ = sup.sname$
			LOCATE 18, 13: CALL inpnew(a$, 126!, updwn%, "13,59,60")
			LSET sup.sname$ = a$
			IF updwn% = 59 THEN GOTO xname
			IF updwn% = 60 THEN GOTO tender
tender2:
			a$ = sup.saddr$
			LOCATE 19, 15: CALL inpnew(a$, 120!, updwn%, "13,59,60")
			LSET sup.saddr$ = a$
			IF updwn% = 59 THEN GOTO xname
			IF updwn% = 60 THEN GOTO tender1
Tender3:
			a$ = sup.suburb$
			LOCATE 20, 15: CALL inpnew(a$, 120!, updwn%, "13,59,60")
			LSET sup.suburb$ = a$
			IF updwn% = 59 THEN GOTO xname
			IF updwn% = 60 THEN GOTO tender2


			GOTO tender
			END IF

		IF INSTR("1,2,3,4,5,9,?,", tender$ + ",") <= 0 THEN GOTO tender
xname:
		PCOPY 1, 0
END SUB

SUB limit.warn (s90!, s60!, s30!, scur!, climit!, updwn%, allow$) STATIC


x.limit.warn:
END SUB

SUB loadLine (m%, il%, ditem%, ordqty%, invqty%, price!, unit!)
nomatch% = 0
loadLine:
		'- lookup the details
		IF ditem% > 0 AND ditem% < maxacc% THEN
			GET #38, ditem%, msrmat
			ano% = msrmat.no%
			IF NOT msrmat.search$ = custin$ THEN
				ditem% = 0
				nomatch% = -1
				GOTO loadLine'??
			END IF
		ELSE
			ano% = 0
			price! = 0

			msrmat.supqty! = VAL(in$(m%, 2))
			LSET msrmat.PurUnit$ = SPACE$(99)
			LSET msrmat.Desc1$ = SPACE$(99)
			LSET msrmat.Desc2$ = SPACE$(99)
			LSET taxinc$ = SPACE$(99)
		END IF
	'//// Determine which price to use ////
	'Unit price from flie or order detail
	IF ditem% > 0 AND ditem% < maxacc% THEN

	IF unit! = 0 THEN unit! = msrmat.PurCost
	CALL ROUND(unit!, 2.5)
	in$(m%, 16) = STR$(unit!)
	END IF

	IF price! THEN
		IF ditem% <> 1 THEN
			CALL rightprice(price!)
			IF VAL(in$(m%, 16)) <> 0 THEN
				price! = price! / msrmat.PurCost * VAL(in$(m%, 16))
			ELSE
				price! = 0
			END IF
		END IF
	END IF
		'- Add up litres order and actualy on order
		ltact = 0
		size! = msrmat.supqty!
		IF msrmat.SupUnit$ = "LT" THEN ltact = ordqty% * size!
		IF msrmat.SupUnit$ = "ML" THEN ltact = ordqty% * size! / 1000
		IF msrmat.SupUnit$ = "KL" THEN ltact = ordqty% * size! * 1000
		in$(m%, 1) = STR$(ordqty%)
		in$(m%, 2) = STR$(msrmat.supqty!)
		in$(m%, 3) = msrmat.SupUnit$
		in$(m%, 4) = STR$(ano%)
		in$(m%, 5) = msrmat.Desc1$ + " " + masrmat.desc2$
		
		in$(m%, 6) = STR$(price!)' Price is set only the first time in since it cannot change
		IF ditem% <> 1 THEN rightsoh! = msrmat.soh
		in$(m%, 7) = STR$(rightsoh!)
		in$(m%, 8) = STR$(0)
		newdata$ = "Y": CALL cf8(m%, d.elem%, newdata$)
		in$(m%, 9) = "Y" ' acstk.taxinc$
		in$(m%, 10) = STR$(ordqty%)
		in$(m%, 11) = STR$(invqty%)
		IF orddet.dBo$ < " " OR orddet.dBo$ > "~" THEN orddet.dBo$ = "N" 'jic
		in$(m%, 12) = orddet.dBo$
		IF il% THEN
			in$(m%, 13) = STR$(ordqty%)
			in$(m%, 14) = STR$(ano%)
		END IF
			in$(m%, 17) = STR$(msrmat.PurCost)

END SUB

SUB openpslip (opt%) STATIC
ON LOCAL ERROR RESUME NEXT

IF opt% = 2 OR opt% = 10 THEN
	CLOSE #99
	OPEN "\export\po.prn" FOR OUTPUT SHARED AS #99
	END IF

IF opt% <> 2 AND opt% <> 10 THEN
	ok% = 0
	DO WHILE ok% = 0
		ERR = 0
		CLOSE #99
		OPEN "PO.PIC" FOR APPEND AS #99
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

GET #44, sno%, sup
scur = CVS(sup.scur$): s30 = CVS(sup.s30$): s60 = CVS(sup.s60$): s90 = CVS(sup.s90$)
sdays% = CVI(sup.sdays$): climit = CVS(sup.climit$)
sterms = CVS(sup.sterms$): daysmax% = CVI(sup.daysmax$)
rec50% = VAL(sup.spname$)
IF rec50% > 0 AND rec50% < 999 THEN
	GET #50, rec50%, PICKUP
	ELSE
	LSET PICKUP.pname1$ = SPACE$(99)
	LSET PICKUP.pname2$ = SPACE$(99)
	LSET PICKUP.pname3$ = SPACE$(99)
	LSET PICKUP.pname4$ = SPACE$(99)
	END IF

END SUB

SUB prtpslip (hord%, opt%, discovr!)
	IF hord% = 0 THEN GOTO x.prtpslip
	GET #48, hord%, ordhed
	hordq = CVS(ordhed.hordq$)

	CLOSE #99
	IF RTRIM$(ordhed.hreford$) = "" THEN ordhed.hreford$ = MID$(DATE$, 4, 2) + MID$(DATE$, 1, 2) + sup.search$
	
	OPEN ".\export\" + MID$(ordhed.hreford$, 1, 8) + ".po" FOR OUTPUT SHARED AS #99

	WRITE #99, "CI-ID", "Creditor Invoice"
	WRITE #99, "BLANK", "sup.sname$", "sup.search$", "sup.stype$", "sup.sno", "sup.saddr$", "sup.saddr2$", "sup.suburb$", "sup.spcode$", "pickup.pname1$", "pickup.pname2$", "pickup.pname3$", "pickup.pname4$"
	WRITE #99, "CIHED", RTRIM$(sup.sname$), RTRIM$(sup.search$), RTRIM$(sup.stype$), sup.sno, RTRIM$(sup.saddr$), RTRIM$(sup.saddr2$), RTRIM$(sup.suburb$), RTRIM$(sup.spcode$), RTRIM$(PICKUP.pname1$), RTRIM$(PICKUP.pname2$), RTRIM$(PICKUP.pname3$),  _
RTRIM$(PICKUP.pname4$)'??

	WRITE #99, "BLANK", "PONum", "InvNo", "FNDYY$(ordhed.hdate$)", "ordhed.htaxe$", "DATE$", "GL", "ContName", "Fax"
	WRITE #99, "CIINF", RTRIM$(ordhed.hreford$), addocnum$, FNDYY$(ordhed.hdate$), FNDYY$(ordhed.htaxe$), MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2), CVS(sup.sgl$), sup.scont$, sup.sphone1$

	WRITE #99, "BLANK", "dordq%", "PURQTY", "supunit$", "ditem%", "desc1$", "desc2$", "dprice", "dtax", "ext!", "purcost", "purunit", "usecost", "unseunit", "gl"
	'-> Read throught the linked list of the details file
	dnext% = CVI(ordhed.hrrn$)
	L% = 0
	tot.ext! = 0
	DO WHILE dnext% > 0
		GET #49, dnext%, orddet
		L% = L% + 1
		'- Decode the detail file
		dord% = orddet.dord%
		ditem% = CVI(orddet.ditem$)
		dordq% = CVI(orddet.dordq$)
		dprice = CVS(orddet.dprice$)
			
			dtax = CVS(orddet.dtax$)
			

		IF ditem% < 1 OR ditem% > maxacc% OR dordq% = 0 THEN
		ELSE
			GET #38, ditem%, msrmat
			dordq% = CVI(orddet.dordq$)
			size! = msrmat.purqty
			ext! = dprice! * dordq%
			tot.ext = tot.ext + ext!

WriteExternal:
			WRITE #99, "CIDET", dordq%, msrmat.supqty!, msrmat.SupUnit$, ditem%, msrmat.Desc1$, msrmat.Desc2$, dprice, dtax, ext!, msrmat.PurCost, msrmat.PurUnit$, msrmat.UseCost, msrmat.UseUnit$, msrmat.Osoh


			END IF
		'- Bottom of read equal loop
		dnext% = orddet.drrn%
		LOOP

	WRITE #99, "BLANK", "invmsg1$", "invmsg2$", "invmsg3$", "invmsg4$"
	WRITE #99, "CIMSG", invmsg1$, invmsg2$, invmsg3$, invmsg4$

	WRITE #99, "BLANK", "tot.ltinv", "tot.ord", "Rate!", "tot.ext", "advalue"
	WRITE #99, "CITOT", tot.ltinv, tot.ord, Rate!, tot.ext, tot.gst

	CLOSE #99
	'IF opt% = 2 OR opt% = 10 THEN
	'  shella$ = "printpo"
	'  LOCATE 22, 2
	'  SHELL shella$
	'END IF
x.prtpslip:



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

					
	 '* Calculate supply cost from SG & cost price
	ab$ = msrmat.SupUnit$ + "-" + msrmat.PurUnit$
	SELECT CASE ab$
	CASE "KG-LT": price! = msrmat.PurCost * msrmat.Sg
	CASE "KG-ML": price! = msrmat.PurCost * msrmat.Sg / 1000
	CASE "LT-KG"
				IF msrmat.Sg <> 0 THEN price! = msrmat.PurCost / msrmat.Sg
				IF msrmat.Sg = 0 THEN price! = msrmat.PurCost
	CASE "LT-GM"
				IF msrmat.Sg <> 0 THEN price! = msrmat.PurCost / msrmat.Sg * 1000
				IF msrmat.Sg = 0 THEN price! = msrmat.PurCost / 1000
	CASE "/M-EA": price! = msrmat.PurCost / 1000
	CASE "/H-EA": price! = msrmat.PurCost / 100
	CASE "MT-KG": price! = msrmat.PurCost / 1000
	CASE "MT-GM": price! = msrmat.PurCost / 1000 / 1000
	CASE "MT-LT": price! = msrmat.PurCost * msrmat.Sg / 1000
	CASE "MT-ML": price! = msrmat.PurCost * msrmat.Sg / 1000000
	CASE "LT-OZ": price! = msrmat.PurCost / 28.413
	CASE "LT-UT": price! = msrmat.PurCost / 28.413 / 64
	CASE "LT-ML": price! = msrmat.PurCost / 1000
	CASE "KG-GM": price! = msrmat.PurCost / 1000
	CASE "GM-LT": price! = msrmat.PurCost * msrmat.Sg / 1000
	CASE "ML-LT": price! = msrmat.PurCost * 1000
	CASE "KL-LT": price! = msrmat.PurCost * 1000
	CASE "TK": price! = msrmat.PurCost
	CASE ELSE: price! = msrmat.PurCost
	END SELECT
	price! = price! * msrmat.supqty!
	'* Round to 2 decimal plmsrmat.activees UP ie 3.0001 = 3.01
	CALL ROUND(price!, 2.5)

END SUB

SUB search.month (rec%, begyymd$)
search.month:
	adlast% = LOF(8) / 384
	rec% = 1
	GET #8, rec%, Audit
	'-Use the period end records to jump old months
	DO WHILE Audit.addate < begyymd$
		adnxtpe% = CVI(MID$(Audit.adsname$, 1, 2))
		adprepe% = CVI(MID$(Audit.adsname$, 3, 2))
		adlstpe% = CVI(MID$(Audit.adsname$, 5, 2))
		IF adnxtpe% < 1 OR adlstpe% > adlast% THEN EXIT DO
		rec% = adnxtpe%
		GET #8, rec%, Audit
	LOOP

END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
'$INCLUDE: '.\SRC\searchx.bi'
END SUB

SUB setaudit (n%)
'$INCLUDE: '.\SRC\setaudit.bi'
END SUB

SUB UpdateOrder (hord%, updwn%)
UpdateOrder:
	GET #48, hord%, ordhed
	IF mode$ = "rec" OR mode$ = "ing" THEN
	'>>>---- Open an invoice copy file if recording the stock to file
		IF RTRIM$(ordhed.hreford$) = "" THEN ordhed.hreford$ = MID$(DATE$, 4, 2) + MID$(DATE$, 1, 2) + sup.search$
		ext$ = ".\export\" + MID$(ordhed.hreford$, 1, 8) + ".DD"
		CLOSE #97
		OPEN ext$ FOR OUTPUT AS #97
			WRITE #97, "DD-ID", "Delivery Docket info"
			WRITE #97, "BLANK", "sup.sname$", "sup.search$", "sup.stype$", "sup.sno", "sup.saddr$", "sup.saddr2$", "sup.suburb$", "sup.spcode$", "pickup.pname1$", "pickup.pname2$", "pickup.pname3$", "pickup.pname4$"
			WRITE #97, "DDHED", RTRIM$(sup.sname$), RTRIM$(sup.search$), RTRIM$(sup.stype$), sup.sno, RTRIM$(sup.saddr$), RTRIM$(sup.saddr2$), RTRIM$(sup.suburb$), RTRIM$(sup.spcode$), RTRIM$(PICKUP.pname1$), RTRIM$(PICKUP.pname2$), RTRIM$(PICKUP.pname3$) _
, RTRIM$(PICKUP.pname4$)'??

			WRITE #97, "BLANK", "PONum", "InvNo", "FNDYY$(ordhed.hdate$)", "ordhed.htaxe$", "DATE$", "GL", "contact", "phonenum", "dd-date", "ddocketnum"
			WRITE #97, "DDINF", RTRIM$(ordhed.hreford$), addocnum$, FNDYY$(ordhed.hdate$), FNDYY$(ordhed.htaxe$), MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2), CVS(sup.sgl$), sup.scont$, sup.sphone1$, ordhed.hdddate$, ordhed. _
hdocket$

			WRITE #97, "BLANK", "dordq%", "PURQTY", "supunit$", "ditem%", "desc1$", "desc2$", "dprice", "dtax", "ext!", "purcost", "purunit", "usecost", "unseunit", "gl", "useqty"

	END IF

	'-First ensure all the details records have been allocated a rrn
	FOR L% = 1 TO maxlines%
		IF VAL(in$(L%, 4)) <> 0 OR VAL(in$(L%, 14)) <> 0 THEN n% = L%
	NEXT
	nn% = n%: firstrec% = CVI(ordhed.hrrn$)
	CALL linkedl(rrn%(), nn%, firstrec%, hord%, 49)
	'-Update the order file before printing the picking slip
	tot.ltact = 0      'Litres on order
	tot.ltinv = 0      'Litres invoiced
	tot.dollr = 0
	tot.items& = 0
	FOR L% = 1 TO nn%
		keyed% = VAL(in$(L%, 1))
		ordqty% = VAL(in$(L%, 10))
		invqty% = VAL(in$(L%, 11))
		sooqty% = VAL(in$(L%, 13))
		svrrn% = VAL(in$(L%, 14))
		BoFlag$ = in$(L%, 12)
		'tmp$ = "Line =" + STR$(l%) + " B4 rrn/qty =" + STR$(svrrn%) + "/" + STR$(sooqty%)
'pd inclusion to try get dlinq% working.
GET #49, rrn%(L%), orddet

		IF mode$ = "inv" OR mode$ = "rec" OR mode$ = "ing" OR mode$ = "nil" THEN
			invqty% = keyed%
			ordqty% = 0
			dlinvq% = keyed%
			BoFlag$ = "N"
			sooqty% = 0
		END IF
		IF mode$ = "ord" THEN
			invqty% = 0
			ordqty% = keyed%
			dlinvq% = CVI(orddet.dlinvq$) '
		END IF
		IF mode$ = "b/o" THEN
			invqty% = keyed%
			ordqty% = ordqty% - keyed%
			IF ordqty% < 0 THEN ordqty% = 0
			dlinvq% = keyed%
			BoFlag$ = "N": IF ordqty% > 0 THEN BoFlag$ = "Y"
		END IF
		'-Add up litres order and actualy on order
		ltact = 0: ltinv = 0
		size! = VAL(in$(L%, 2))
		IF in$(L%, 3) = "LT" THEN ltact = ordqty% * size!
		IF in$(L%, 3) = "ML" THEN ltact = ordqty% * size! / 1000
		tot.ltact = tot.ltact + ltact
		IF in$(L%, 3) = "LT" THEN ltinv = invqty% * size!
		IF in$(L%, 3) = "ML" THEN ltinv = invqty% * size! / 1000
		dprice = VAL(in$(L%, 6))
		tot.ltinv = tot.ltinv + ltinv
		tot.dollr = tot.dollr + (dprice * ordqty%)
		tot.items& = tot.items& + ordqty%
		IF mode$ = "rec" OR mode$ = "nil" THEN
			tot.dollr = tot.dollr + (dprice * invqty%)
			tot.items& = tot.items& + invqty%
		END IF
		IF ordqty% < 0 THEN ordqty% = 0

		GET #49, rrn%(L%), orddet
		LSET orddet.dinvq$ = MKI$(invqty%)
		LSET orddet.dordq$ = MKI$(ordqty%)
		LSET orddet.dlinvq$ = MKI$(dlinvq%)
		LSET orddet.ditem$ = MKI$(VAL(in$(L%, 4)))
			test = 0
			test = VAL(in$(L%, 6))
			CALL ROUND(test, 2.5)
		LSET orddet.dprice$ = MKS$(test)
		LSET orddet.dtax$ = MKS$(0)
		LSET orddet.dBo$ = BoFlag$
		IF VAL(in$(L%, 16)) > 0 THEN
			test = 0
			test = VAL(in$(L%, 16))
			CALL ROUND(test, 2.5)
			LSET orddet.dfiller$ = MKS$(test)'????
		ELSE
		orddet.dfiller$ = SPACE$(9)
		END IF
		PUT #49, rrn%(L%), orddet: SOUND 20000, 1

		'-Update the stock file (remove previous)


	 
	
	
		'stop changing stock file if mode nil
		IF mode$ <> "nil" THEN

		IF svrrn% >= 1 AND svrrn% <= maxacc% THEN
			GET #38, svrrn%, msrmat
			CALL supqtyconv(svrrn%, purconv)
			msrmat.soo = msrmat.soo - sooqty% * purconv
			PUT #38, svrrn%, msrmat
		END IF

		'-Update the stock file
		ditem% = CVI(orddet.ditem$)
		IF ditem% < 1 OR ditem% > maxacc% THEN
			'IF ditem% <> 0 THEN SOUND 50, 1
		ELSE
			GET #38, ditem%, msrmat
			CALL supqtyconv(ditem%, purconv)

			asoh1 = msrmat.soh
			'asold1 = acstk.sold
			'asohv = msrmat.sohv
			asoh1 = asoh1 + invqty% * purconv
			asohv = asohv + (invqty%) * purconv * msrmat.PurCost

			msrmat.soo = msrmat.soo + ordqty% * purconv
			'msrmat.sohv = asohv
			msrmat.soh = asoh1
			'msrmat.UseCost = msrmat.sohv / abs(msrmat.soh)
			
			END IF

			IF mode$ = "rec" OR mode$ = "ing" THEN
				'write item record of delivery
				WRITE #97, "DDDET", dlinvq%, msrmat.supqty!, msrmat.SupUnit$, ditem%, msrmat.Desc1$, msrmat.Desc2$, dprice, dtax, ext!, msrmat.PurCost, msrmat.PurUnit$, msrmat.UseCost, msrmat.UseUnit$, msrmat.Osoh, invqty% * purconv
				msrmat.lastpur$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
			END IF


			PUT #38, ditem%, msrmat

		END IF
		'-End of updating the stock file

		'tmp$ = tmp$ + " AF rrn/qty =" + STR$(ditem%) + "/" + STR$(ordqty%)
		'CALL sndmsg(tmp$): X$ = INPUT$(1)

	NEXT

	GET #48, hord%, ordhed
	hinvq = CVS(ordhed.hinvq$)
	LSET ordhed.hord$ = MKI$(hord%)
	LSET ordhed.hsup$ = sup.search$ + sup.stype$

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
	SELECT CASE mode$
		CASE "rec": ordhed.hstatus$ = "R"
		CASE "b/o": ordhed.hstatus$ = "B"
		CASE "ord": ordhed.hstatus$ = "O"
		CASE "inv": ordhed.hstatus$ = "I"
		CASE "nil": ordhed.hstatus$ = "R"
		CASE ELSE: ordhed.hstatus$ = "O"
	END SELECT
	
	PUT #48, hord%, ordhed
	IF mode$ = "nil" THEN mode$ = "rec"
	CLOSE #97
END SUB

