DECLARE SUB accbrowseo (rec%)
DECLARE SUB accbrowse (rec%)
DECLARE SUB add.up.order (tot.ltact!, tot.ord!, tot.ext!)
DECLARE SUB alcbatch (gen$, rec57%, thisltr!, thisbatch$)
DECLARE SUB browse38 (browse38.result%, updwn%)
DECLARE SUB cf8 (L%, d.elem%, newdata$)
DECLARE SUB chglin (ln%, L%, d.elem%, updwn%)
DECLARE SUB copybatch (rec54&)
DECLARE SUB custombatch (rec54&, thisltr!, updwn%, auto%)
DECLARE SUB cvt.tnt (tnt$, tnt%, tntf$)
DECLARE SUB delOrder (hord%, n%, clr%, autodel$, thissup$, norders%)
DECLARE SUB doprint (rec&, thisbatch$, thisltr!, prt.batch%, prt.costs%, updwn%)
DECLARE SUB dsply (sno%, norders%)
DECLARE SUB dsplyLine (L%, d.elem%)
DECLARE SUB dsporders (dspstart%, norders%, custin$)
DECLARE SUB ean13 (in$, dind%)
DECLARE SUB findnext (hord%, norders%, ok%)
DECLARE SUB findorders (thissup$, norders%, hord%)
DECLARE SUB getform (opt%, form$, rec54&, updwn%)
DECLARE SUB height.in.tank (updwn%, seq%, Ltrs.in!, Height.from.btm!, Height.from.top!)
DECLARE SUB linkedl (rrn%(), n%, firstrec%, ord%, chd%)
DECLARE SUB loadLine (m%, il%, ditem%, ordqty%, invqty%, price!, rmc!)
DECLARE SUB mline ()
DECLARE SUB reallocate (rec57%, rec54&)
DECLARE SUB reprint (rec57%, rec54&)
DECLARE SUB ReturntoStock (form$, thisltr!)
DECLARE SUB rightprice (price!)
DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB setaudit (n%)
DECLARE SUB setchannel ()
DECLARE SUB UpdateOrder (hord%, updwn%)
DECLARE FUNCTION format$ (VALUE!, definition$)

	COMMON SHARED maxsup%, maxform%, maxrmat%, maxacc%, maxtypes, maxcus%, maxord%
	COMMON SHARED qk$, keyl%, rep$
	COMMON SHARED batchltr!, alprod%, hord%, batchsg!
	COMMON SHARED maxtnt%, msg$, maxtankrrn%
	COMMON SHARED ff!
	COMMON SHARED ch.hedx%, ch.hed%, ch.det%
	COMMON SHARED mode$, Modedesc$
	COMMON SHARED beg$, datereq$
	COMMON SHARED TaxRate!, DiscRate!
	COMMON SHARED ext.has.changed%, rec50%, ctl%, Cash%
	COMMON SHARED vdisc!, Rate!, discovr!, climit!, ovrPrice!
	COMMON SHARED tot.gst!, tot.ext!, tot.allup!
	COMMON SHARED skipexit%
	COMMON SHARED doc.type$, formtype$, sno%
	COMMON SHARED tot.ord!, tot.ltact, tot.ltinv, tot.dollr, tot.items&
	COMMON SHARED newsearch$
	COMMON SHARED bysearch$
	COMMON SHARED search.key$
	COMMON SHARED tot.qty, Tot.taxvol
	COMMON SHARED tot.dg200%, tot.dg60%, tot.dg20%, tot.dg10%, tot.dg4%, tot.dg2%, tot.dg1%, tot.dg850%, tot.dg500%, tot.dg300%, tot.dg250%, tot.dglt!
	COMMON SHARED extdisc!, inv.lt.printed!
	COMMON SHARED tender$
	COMMON SHARED invmsg1$, invmsg2$, invmsg3$, invmsg4$
	COMMON SHARED ean$, naudit%, acstkf$

	COMMON SHARED c%(), in$(), rrn%()
	COMMON SHARED tankrrn%()
	COMMON SHARED rm.tanksize!(), rm.tankltmm!() 'Size of the tank for every line
	COMMON SHARED orders%()
	COMMON SHARED auditfile$()

	CONST maxlines% = 45 '
	CONST GST! = 10  '10%
	CONST debug% = 0
	typefields% = -1
	maxtankrrn% = 5

	DIM SHARED tankrrn%(maxtankrrn%)
	DIM SHARED rm.tanksize!(38), rm.tankltmm!(38) 'Size of the tank for every line
	DIM SHARED orders%(1001)
	DIM SHARED auditfile$(15)
	DIM SHARED c%(8), in$(maxlines%, 16), rrn%(maxlines%)
	'1=qty%,2=size,3=unit,4=itm,5=desc,6=price,7=SOH,8=ext
	'9=tax flag,10=ordqty%,11=Invqty,12=BoFlag,13=save qty
	'14=Save item, 15=Overtyped price

	keyl% = 20: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)

	DATA 2,7,10,13,18,56,63,72
	FOR i% = 1 TO 8: READ c%(i%): NEXT
	

'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "DSMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
 

	
	acstkf$ = "..."
	parm$ = ENVIRON$("PARM$")
	IF VAL(parm$) > 0 THEN pass.getcust% = -1: custin$ = parm$: updwn% = 13
	parm2$ = ENVIRON$("PARM2$")
	IF parm2$ = "PRE..." THEN acstkf$ = "PRE"

		'$INCLUDE: '\tpmanuf\src\msrmat.INC'
		'$INCLUDE: '\tpmanuf\src\whof.inc'
		'$INCLUDE: '\tpmanuf\src\cusx.inc'
		'$INCLUDE: '\tpmanuf\src\supx.inc'
		'$INCLUDE: '\tpmanuf\src\cus.inc'
		'$INCLUDE: '\tpmanuf\src\ACSTK.INC'
		'$INCLUDE: '\tpmanuf\src\ASAUDIT.INC'
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
	'CALL setaudit(naudit%)
	parm$ = ENVIRON$("PARM$")
	IF parm$ = "/prt.." THEN
		ENVIRON "PARM$=......"
		after.prtinv% = -1
		CALL mline
	END IF

	
	'Clear all but the invnum and invnumrec%
	hord% = 0: opt% = 0: Cash% = 0: tender$ = ""
	chginv# = 0: chginv.rrn% = 0
	thissup$ = "": norders% = 0
	invmsg1$ = "": invmsg2$ = ""

SUB accbrowseo (rec%) STATIC
'npgm$ = "dsinv04d"
'CALL EXITPGM(npgm$)
'SHELL npgm$
END SUB

SUB add.up.order (tot.ltact!, tot.ord!, tot.ext!) STATIC
add.up.order:
	'- Add up total litres and calc discount $
	tot.ltact = 0
	tot.ext = 0
	tot.items& = 0
	FOR i% = 1 TO maxlines%
		'- Add up litres order and actualy on order
		ltact = 0
		qty = VAL(in$(i%, 1))
		size! = VAL(in$(i%, 2))
		SELECT CASE UCASE$(in$(i%, 3))
			CASE "ML":
				ltact = qty! * VAL(in$(i%, 2)) / 1000
			CASE "LT":
				ltact = qty! * VAL(in$(i%, 2))
			CASE "LS":
				ltact = qty! * VAL(in$(i%, 2))
			CASE "GM":
				ltact = qty! * VAL(in$(i%, 2)) / 1000 / batchsg
			CASE "GS":
				ltact = qty! * VAL(in$(i%, 2)) / 1000 / batchsg
			CASE "KG":
				ltact = qty! * VAL(in$(i%, 2)) / batchsg
			CASE ELSE: ltact = 0
		END SELECT
			 ltact = ltact * VAL(in$(i%, 16))


		'IF in$(i%, 3) = "LS" THEN ltact = qty * size!
		'IF in$(i%, 3) = "LT" THEN ltact = qty * size!
		'IF in$(i%, 3) = "ML" THEN ltact = qty * size! / 1000

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
	IF CUS.stype$ = "W" THEN a = 0
	CALL ROUND(a, .5)
	vdisc! = 0: DiscRate! = 0
	SELECT CASE a'Total ordered + header volume adjustment
	CASE 100 TO 199: vdisc! = tot.ltact * .05: DiscRate! = .05
	CASE 200 TO 399: vdisc! = tot.ltact * .075: DiscRate! = .075
	CASE 400 TO 599: vdisc! = tot.ltact * .1: DiscRate! = .1
	CASE 600 TO 999: vdisc! = tot.ltact * .122: DiscRate! = .125
	CASE IS >= 1000: vdisc! = tot.ltact * .15: DiscRate! = .15
	CASE ELSE: vdisc! = 0: DiscRate! = 0
	END SELECT
	'no volume discount
	vdisc! = 0: DiscRate! = 0
'- Round the very bottom price for cash items
	IF Cash% AND 1 = 2 THEN
'Start a +10Cents and step back to -10Cents.
			tot.allup = tot.ext - vdisc!
			temptotal = tot.allup
			tot.gst! = temptotal * (TaxRate! / 100): CALL ROUND(tot.gst!, 2.5)
			tot.allup = temptotal + tot.gst!
			Cents! = tot.allup - FIX(tot.allup)
			Cents% = Cents! * 100
			IF Cents% MOD 5 = 0 THEN   'Until 5 Cent round
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
	LOCATE 21, 2: PRINT USING "                                           Litres in Batch            #,###.##"; batchltr!
	LOCATE 22, 2: PRINT USING "                                           Volume Allocated           #,###.##"; tot.ord!
																						LOCATE 23, 45: PRINT USING "Volume Unallocated         #,###.##"; batchltr! - tot.ord!
	COLOR 7, 0
	'LOCATE 24, 69: PRINT USING "�$$#####.##�"; tot.allup; : COLOR 2, 0
	'COLOR 10, 0:
	'LOCATE 24, 70: PRINT USING "$$#####.##"; tot.allup; : COLOR 2, 0
	COLOR 2, 0
	ext.has.changed% = 0
END SUB

SUB cf8 (L%, d.elem%, newdata$)
REDIM x20%(20)
'--EXTENSION
cf8:
	qty! = VAL(in$(L%, 1))
	size! = VAL(in$(L%, 2))
	price! = VAL(in$(L%, 6))
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
		ln% = (L% - d.elem%) MOD 15 + 1: ln% = ln% + 4
		LOCATE ln%, c%(4): PRINT USING "####"; spec%
		LOCATE ln%, c%(5): PRINT acstk.desc1$; " "; acstk.desc2$
		dkt$ = acstk.desc1$
		LOCATE ln%, c%(5)
		CALL inpnew(dkt$, 125!, updwn%, "13,60")
		LSET acstk.desc1$ = dkt$
		dkt$ = acstk.desc2$
		LOCATE ln%, c%(5) + 26
		CALL inpnew(dkt$, 110!, updwn%, "13,60")
		LSET acstk.desc2$ = dkt$
		LOCATE ln%, c%(5): PRINT acstk.desc1$; " "; acstk.desc2$
		in$(L%, 5) = acstk.desc1$ + " " + acstk.desc2$
		LOCATE ln%, c%(6)
		in$(L%, 6) = STR$(acstk.purcost!)
								CALL inpnew(in$(L%, 6), 5.2, updwn%, "13")
		price! = VAL(in$(L%, 6))
		TaxRate! = GST
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
		ctl% = 6
	END IF
	old.ext! = VAL(in$(L%, 8))
		SELECT CASE UCASE$(in$(L%, 3))
			CASE "ML":
				ext! = qty! * VAL(in$(L%, 2)) / 1000
			CASE "LT":
				ext! = qty! * VAL(in$(L%, 2))
			CASE "LS":
				ext! = qty! * VAL(in$(L%, 2))
			CASE "GM":
				ext! = qty! * VAL(in$(L%, 2)) / 1000 / batchsg
			CASE "GS":
				ext! = qty! * VAL(in$(L%, 2)) / 1000 / batchsg
			CASE "KG":
				ext! = qty! * VAL(in$(L%, 2)) / batchsg
			CASE ELSE: ltact = 0
		END SELECT
			 ext! = ext! * VAL(in$(L%, 16))
	 
	'ext! = qty! * price!
	in$(L%, 8) = STR$(ext!)
	IF old.ext! <> ext! THEN ext.has.changed% = -1
END SUB

SUB chglin (ln%, L%, d.elem%, updwn%)

	ctl% = 1: chg = 0: maxctl% = 7
	WHILE NOT ctl%
		'Edit
		IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
		ON ctl% GOSUB cf1, cf2, cf3, cf4, cf5, cf6, cf7
		' Pgm ctl processing
		ctl% = ctl% + 1
		'Mimick F1 if enter is pressed on a blank line
		IF updwn% = 13 AND VAL(in$(L%, 1)) = 0 AND VAL(in$(L%, 4)) = 0 THEN
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
	IF ext.has.changed% THEN
		TaxRate! = GST
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
	END IF
	LOCATE ln%, c%(1)
	in$ = in$(L%, 1)
	old.qty = VAL(in$(L%, 1))

	IF updwn% = 113 THEN 'The last one was scanned, get ready for another
		in$ = "1"
		updwn% = 13
	ELSE
		CALL inpnew(in$, 204!, updwn%, "13,27,59-60,62-65,68,72-73,80-81")
	END IF

	in$ = UCASE$(in$)
	IF updwn% = 27 THEN
		in$(L%, 1) = "0": in$(L%, 2) = "   ": in$(L%, 3) = "": in$(L%, 4) = "": in$(L%, 5) = "": in$(L%, 6) = "0"
		in$(L%, 7) = "0": in$(L%, 8) = "0": in$(L%, 9) = "N/": in$(L%, 10) = "0": in$(L%, 11) = "0": in$(L%, 12) = "N"
		CALL dsplyLine(L%, d.elem%)
		TaxRate! = GST
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
		GOTO cf1
	END IF

	IF updwn% = 63 THEN '-Instant price browse
		PCOPY 0, 1
		CALL BOX(4, 9, 77, 17, 3, 0, 1)
		i% = VAL(in$(L%, 4))
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
		COLOR 6, 0
					LOCATE 15, 5: PRINT "            ...RMC...   ..COGS...                                      "
		COLOR 2, 0
		LOCATE 16, 5: PRINT USING "            $#####.##   $#####.##                                     "; acstk.rmc; acstk.cogs



		CALL inpnew(a$, 0!, updwn%, "13,59,65")
		PCOPY 1, 0
		IF updwn% = 13 THEN
			GOTO cf1
		END IF
		IF updwn% = 59 THEN
			GOTO cf1
		END IF

	END IF
	IF updwn% = 64 THEN
		PCOPY 0, 1
		CALL accbrowseo(rec%)
		PCOPY 1, 0
		GOTO cf1
	END IF
	IF updwn% = 65 THEN ' overtype price
		CALL SNDMSG("F5-To reinstate price to original")
		LOCATE ln%, 56
		a$ = (in$(L%, 6))
		CALL inpnew(a$, 5.2, updwn%, "13,59,63")
		CALL SNDMSG("")
		IF updwn% = 13 THEN
			in$(L%, 6) = STR$(VAL(a$))
			in$(L%, 15) = "Y"
		END IF
		IF updwn% = 63 THEN
			'get original price
			IF VAL(in$(L%, 4)) > 0 AND VAL(in$(L%, 4)) < maxacc% THEN
				GET #3, VAL(in$(L%, 4)), acstk
				CALL rightprice(oprice!)
				in$(L%, 6) = STR$(oprice!)
				in$(L%, 15) = SPACE$(9)
			END IF
		END IF

		LOCATE ln%, 56: PRINT USING "####.##"; in$(L%, 6)
		CALL dsplyLine(L%, d.elem%)
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
	END IF
	IF updwn% = 68 THEN
		'CALL get.order.vs(hord%, updwn%)
	END IF

	'-
	IF VAL(in$) > 9300 THEN
		in$ = "1"
		SOUND 15000, 10
		SOUND 500, 3
	END IF


	in$(L%, 1) = in$
	newdata$ = "Y": CALL cf8(L%, ctl%, newdata$)
	newsearch$ = "Y"

	IF old.qty <> VAL(in$) THEN
		CALL dsplyLine(L%, d.elem%)
		TaxRate! = GST 'Use the constant
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
	END IF

RETURN
	'-SIZE
cf2: LOCATE ln%, c%(2)
	learn% = -1
	IF VAL(in$(L%, 4)) = 0 THEN check$ = "13,59,60,62,27" ELSE check$ = ""
	'CALL inpnew(in$(l%, 2), 103!, updwn%, check$)
	IF check$ > "" THEN
	btm$ = ""
	FOR i% = 1 TO 79: btm$ = btm$ + CHR$(SCREEN(25, i%)): NEXT
	btma$ = "F1-Save/Print.   Enter Size or Scan Barcode or F4-Remove Barcode Assigment"

cf2UL:
		COLOR 8, 3: LOCATE 25, 1: PRINT btma$;
		LOCATE ln%, c%(2)
		CALL inpnew(in$(L%, 2), 113!, updwn%, check$)
		IF updwn% = 62 THEN
			learn% = 0
			CALL SNDMSG("Remove Barcode assignment.")
			GOTO cf2UL
		END IF

		CALL SNDMSG("")
		COLOR 8, 3: LOCATE 25, 1: PRINT btm$;
	END IF

	IF updwn% = 27 THEN
		in$(L%, 1) = "0": in$(L%, 2) = "   ": in$(L%, 3) = "": in$(L%, 4) = "": in$(L%, 5) = "": in$(L%, 6) = "0"
		in$(L%, 7) = "0": in$(L%, 8) = "0": in$(L%, 9) = "N/": in$(L%, 10) = "0": in$(L%, 11) = "0": in$(L%, 12) = "N"
		CALL dsplyLine(L%, d.elem%)
		updwn% = 60
	END IF

	IF VAL(in$(L%, 2)) > 9300 THEN
		ean$ = in$(L%, 2)
		CALL ean13(in$(L%, 2), ind%)
		IF ind% <= 0 THEN
			in$(L%, 2) = ""
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
			in$(L%, 2) = ""
			GOTO cf2
		END IF


		ditem% = ind%
		price! = -1
		ordqty% = VAL(in$(L%, 1))
		invqty% = 0
		m% = L%
		CALL loadLine(m%, 0, ditem%, ordqty%, invqty%, price!, rmc!)
		CALL dsplyLine(L%, d.elem%)
		updwn% = 113 'Says EAN assigned
	END IF


	in$(L%, 2) = UCASE$(in$(L%, 2))
	a$ = "   ": LSET a$ = in$(L%, 2): in$(L%, 2) = a$

	bysearch$ = "N"
	IF in$(L%, 2) <> "   " AND VAL(in$(L%, 4)) = 0 THEN bysearch$ = "Y"

RETURN
	'-UNITS
cf3: LOCATE ln%, c%(3)
	CALL inpnew(in$(L%, 3), 102!, updwn%, "")
RETURN
	'-STOCK NUMBER
cf4: LOCATE ln%, c%(4)
	oldrec% = VAL(in$(L%, 4))
	IF bysearch$ = "Y" OR VAL(in$(L%, 4)) <> 0 THEN
		inpctl$ = ""
	ELSE
		inpctl$ = "13,59,60,62,64"
	END IF

	IF frombrowse% THEN in$(L%, 4) = STR$(rec%): frombrowse% = 0
	CALL inpnew(in$(L%, 4), 4!, updwn%, inpctl$)
		IF updwn% = 64 THEN
			PCOPY 0, 1
			CALL accbrowseo(rec%)
			PCOPY 1, 0
			IF rec% < 1 OR rec% > maxacc% THEN rec% = 1
			in$(L%, 4) = "": updwn% = 0: frombrowse% = -1
			GOTO cf4
		END IF

	ditem% = VAL(in$(L%, 4))
	IF ditem% < 1 OR ditem% > maxacc% THEN ditem% = 0
	IF ditem% <> oldrec% OR ditem% = 0 THEN
		price! = -1
		ordqty% = VAL(in$(L%, 1))
		invqty% = 0
		m% = L%
		CALL loadLine(m%, 0, ditem%, ordqty%, invqty%, price!, rmc!)
		CALL dsplyLine(L%, d.elem%)
	END IF
RETURN
	'-DESCRIPTION
cf5: LOCATE ln%, c%(5)
	IF bysearch$ = "N" THEN
		CALL inpnew(in$(L%, 5), 136!, updwn%, "")

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
					CALL accbrowseo(rec%)
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
		test = VAL(in$(L%, 2))
		ii% = 0
		FOR i% = LEN(in$(L%, 2)) TO 1 STEP -1
			IF MID$(in$(L%, 2), i%, 1) = " " THEN ii% = ii% + 1
			IF MID$(in$(L%, 2), i%, 1) <> " " THEN EXIT FOR
			NEXT
		testa$ = STRING$(ii%, " ") + in$(L%, 2)
		testa$ = LEFT$(testa$, 3)

		test1$ = MID$(qk$, 1, 1)
		test1$ = MID$(qk$, 1, 1)
		count% = 0
anext3:
		IF MID$(qk$, 16, 3) = testa$ THEN
			test1$ = MID$(qk$, 1, 1)
			IF ind% > 0 AND ind% < maxacc% THEN GET #3, ind%, acstk
			LOCATE ln%, c%(4): PRINT USING "####"; ind%
			LOCATE ln%, c%(5): PRINT acstk.desc1$; " "; acstk.desc2$
			LOCATE ln%, c%(5)
			IF newsearch$ = "Y" THEN search.dir$ = CHR$(13)
			'// If its the last line leave it in Next/Previous mode on same line //
			IF newsearch$ = "Y" AND L% = maxlines% THEN search.dir$ = ""
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
			ordqty% = VAL(in$(L%, 1))
			invqty% = 0
			m% = L%
			CALL loadLine(m%, 0, ditem%, ordqty%, invqty%, price!, rmc!)
			CALL dsplyLine(L%, d.elem%)
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
cf6: LOCATE ln%, c%(6)
				'CALL inpnew(in$(l%, 6), 5.2!, updwn%, "")
RETURN
	'-TAX
cf7:
RETURN
x.chglin:
	
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
	PUT #48, hord%, ordhed
	hord% = 0

	'If a special item is used (stock # <20) delete it.
	FOR L% = 1 TO maxlines%
		i% = VAL(in$(L%, 4))
		IF i% >= 1 AND i% <= 20 THEN
			GET #3, i%, acstk
			acstk.no = 0
			acstk.desc1$ = ""
			acstk.desc2$ = ""
			PUT #3, i%, acstk
		END IF

		'-Update the stock file (remove previous)
		sooqty% = VAL(in$(L%, 13))
		svrrn% = VAL(in$(L%, 14))
		IF svrrn% >= 1 AND svrrn% <= maxacc% THEN
			GET #3, svrrn%, acstk
			acstk.soo = acstk.soo - sooqty%
			PUT #3, svrrn%, acstk
		END IF

	NEXT

	clr% = 1
x.delOrder:

END SUB

SUB dsply (sno%, norders%) STATIC
dsply:
	IF sno% < 1 OR sno% > maxcus% THEN GOTO x.dsply
	GET #43, sno%, CUS
	scur = CVS(CUS.scur$): s30 = CVS(CUS.s30$): s60 = CVS(CUS.s60$): s90 = CVS(CUS.s90$)
	sdays% = CVI(CUS.sdays$): climit = CVS(CUS.climit$)
	sterms = CVS(CUS.sterms$): daysmax% = CVI(CUS.daysmax$)
	rec50% = VAL(CUS.spname$)
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
	LOCATE 3, 3: PRINT USING "& & & &&"; LEFT$(CUS.sname$, 30); LEFT$(CUS.scont$, 25); LEFT$(CUS.sphone$, 13); CUS.search$; CUS.stype$
	COLOR 7: LOCATE 4, 2: PRINT "컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴": COLOR 2
	LOCATE 5, 2: PRINT USING " \                                  \  Deliver:\                            \"; CUS.saddr$; PICKUP.pname1$
	LOCATE 6, 2: PRINT USING " \                                  \          \                            \"; CUS.saddr2$; PICKUP.pname2$
	LOCATE 7, 2: PRINT USING " \                  \           \   \          \                            \"; CUS.suburb$; CUS.spcode$; PICKUP.pname3$
	COLOR 6, 0
	LOCATE 5, 41: PRINT "Deliver:"
	COLOR 2, 0
	
	COLOR 6
	SELECT CASE daysmax%
	CASE 1: LOCATE 8, X0%: PRINT USING "Terms:## day for ##% discount. "; daysmax%; sterms
	CASE ELSE: LOCATE 8, X0%: PRINT USING "Terms:## days for ##% discount."; daysmax%; sterms
	END SELECT

	COLOR 10, 0: LOCATE 8, 49
	IF CUS.BO$ = "Y" THEN
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

	COLOR 7: LOCATE , 2: PRINT "컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴": COLOR 2
	CALL BOX(2, 12, 79, 23, 7, 0, 0)
	LOCATE 11, 25: PRINT "Orders found for this customer"
	COLOR 6, 0
	IF norders% < 10 THEN
	LOCATE , 3: PRINT "Num. Type Ord.. Inv..  Order    Dollars. Date....  Order Ref... Due........"
	ELSE
	 LOCATE , 2: PRINT "Num Date. Cust. Ref...... Num Date. Cust. Ref...... Num Date. Cust. Ref......"
	END IF

	COLOR 2, 0

	'- Set cash sale mode
	Cash% = 0
	IF CUS.search = "CASH" THEN Cash% = -1

x.dsply:

END SUB

SUB dsplyLine (L%, d.elem%) STATIC
		ln% = (L% - d.elem%) MOD 15 + 1: ln% = ln% + 4'+4 Lines from the top of the screen
		COLOR 2, 0
		qty% = VAL(in$(L%, 1))
		IF qty% < 1 OR qty% > 9999 THEN
			LOCATE ln%, 2
			PRINT "    �     �    �                                    �       �       �         "
		ELSE
			qty% = VAL(in$(L%, 1))
			LSET acstk.size$ = in$(L%, 2)
			LSET acstk.unit$ = in$(L%, 3)
			ano% = VAL(in$(L%, 4))
			LSET acstk.desc1$ = in$(L%, 5)
			LSET acstk.desc2$ = MID$(in$(L%, 5), LEN(acstk.desc1$) + 2, 10)
			newdata$ = "N": CALL cf8(L%, d.elem%, newdata$)
			price! = acstk.soo%   'VAL(in$(L%, 2))


			soh% = VAL(in$(L%, 7))
			ext! = VAL(in$(L%, 8))' ???

			SELECT CASE acstk.unit$
				CASE "ML": ext! = ext! / 1000
				CASE ELSE
			END SELECT

			'- On BO
			IF in$(L%, 12) = "Y" THEN
				COLOR 10
			END IF
			IF MID$(in$(L%, 15), 1, 1) = "Y" THEN
				COLOR 14
			END IF

			'- Condition red
			IF ext! <= .01 AND qty% > 0 AND ano% > 0 THEN
				COLOR 4
				SOUND 250, 10
				cond.red$ = "There are zero values on the invoice"
			ELSE
				cond.red$ = ""
			END IF
			a$ = "�" + acstk.size$ + acstk.unit$ + "�"
			b$ = "�" + acstk.desc1$ + " " + acstk.desc2$ + "�"
			c$ = "�"
			LOCATE ln%, 2: PRINT USING "####"; qty%
			LOCATE ln%, 6: PRINT a$;
			LOCATE ln%, 13: PRINT USING "####"; ano%
			LOCATE ln%, 17: PRINT b$;
			LOCATE ln%, 55: PRINT USING "####.##"; price!;
			LOCATE ln%, 62: PRINT c$;
			IF soh% <> 0 THEN
			LOCATE ln%, 63: PRINT USING " #####"; soh%;
			ELSE
			LOCATE ln%, 63: PRINT USING "\     \"; SPACE$(7);
			END IF
			COLOR 2
			LOCATE ln%, 70: PRINT c$;
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

		PRINT USING "### \   \ \   \ \        \"; CVI(ordhed.hord$); FNDYY$(ordhed.hdate$); ordhed.hsup$; ordhed.hreford$
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
		LSET ordhed.htaxe$ = CUS.taxe$
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

SUB linkedl (rrn%(), n%, firstrec%, ord%, chd%) STATIC
'$INCLUDE: '\tpmanuf\src\linkedl.bi'
END SUB

SUB loadLine (m%, il%, ditem%, ordqty%, invqty%, price!, rmc!)
loadLine:
		'- lokup the details
		IF ditem% > 0 AND ditem% < maxacc% THEN
			GET #3, ditem%, acstk
			ano% = acstk.no%
		ELSE
			ano% = 0
			price! = 0
			LSET acstk.size$ = in$(m%, 2)
			LSET acstk.unit$ = SPACE$(99)
			LSET acstk.desc1$ = SPACE$(99)
			LSET acstk.desc2$ = SPACE$(99)
			LSET acstk.taxinc$ = SPACE$(99)
		END IF
	'//// Determine which price to use ////
	IF price! THEN
		IF ditem% <> 1 THEN
			IF MID$(otprice$, 1, 1) = "Y" THEN
			ELSE
				CALL rightprice(price!)
			END IF
		END IF
	END IF
		'- Add up litres order and actualy on order
		ltact = 0
		size! = VAL(acstk.size$)
		SELECT CASE UCASE$(acstk.unit$)
			CASE "ML":
				ltact = qty! * size! / 1000
			CASE "LT":
				ltact = qty! * size!
			CASE "LS":
				ltact = qty! * size!
			CASE "GM":
				ltact = qty! * size! / 1000 / batchsg
			CASE "GS":
				ltact = qty! * size! / 1000 / batchsg
			CASE "KG":
				ltact = qty! * size! / batchsg
			CASE ELSE: ltact = 0
		END SELECT
			 ltact = ltact * acstk.pack%

		'IF acstk.unit$ = "LS" THEN ltact = ordqty% * size!
		'IF acstk.unit$ = "LT" THEN ltact = ordqty% * size!
		'IF acstk.unit$ = "ML" THEN ltact = ordqty% * size! / 1000
		in$(m%, 1) = STR$(ordqty%)
		in$(m%, 2) = acstk.size$
		in$(m%, 3) = acstk.unit$
		in$(m%, 4) = STR$(ano%)
		in$(m%, 5) = acstk.desc1$ + " " + acstk.desc2$
		in$(m%, 6) = STR$(price!)' Price is set only the first time in since it cannot change
		in$(m%, 7) = STR$(acstk.soh%)
		in$(m%, 8) = STR$(0)
		newdata$ = "Y": CALL cf8(m%, d.elem%, newdata$)
		in$(m%, 9) = acstk.taxinc$
		in$(m%, 10) = STR$(ordqty%)
		in$(m%, 11) = STR$(invqty%)
		IF orddet.dBo$ < " " OR orddet.dBo$ > "~" THEN orddet.dBo$ = "N" 'jic
		in$(m%, 12) = orddet.dBo$
		IF il% THEN
			in$(m%, 13) = STR$(ordqty%)
			in$(m%, 14) = STR$(ano%)
		END IF
		in$(m%, 15) = otprice$
		in$(m%, 16) = STR$(acstk.pack%)
END SUB

SUB mline

	c%(1) = 2
	c%(2) = 7
	c%(3) = 10
	c%(4) = 13
	c%(5) = 18
	c%(6) = 56
	c%(7) = 63
	c%(8) = 72
	
s.mline:
CLOSE #3
CLOSE #48
CLOSE #49
OPEN "acstk.acf" FOR RANDOM SHARED AS #3 LEN = 256
OPEN "igahed.acf" FOR RANDOM SHARED AS #48 LEN = 320
OPEN "igadet.acf" FOR RANDOM SHARED AS #49 LEN = 32

	custin$ = "ZSTOA"

getcust:
		custin$ = "ZSTOA"
		GOSUB mline

'--E D I T   S E C T I O N
mline:
GOSUB load.det
aRETURN:
GOSUB detail

exitmenu:
	DO

	SELECT CASE skipexit%
	CASE -1: opt$ = "": updwn% = 60
	CASE ELSE
		CALL BOX(17, 4, 63, 20, 6, 9, 1)
		COLOR 3, 1
		LOCATE 5, 28: PRINT "  E X I T    M E N U "
		COLOR 6, 1
		LOCATE , 28: PRINT ""
		LOCATE , 28: PRINT ""
		LOCATE , 28: PRINT ""
		LOCATE , 28: PRINT ""
		LOCATE , 28: PRINT ""
		LOCATE , 28: PRINT ""
		LOCATE , 28: PRINT ""
		LOCATE , 28: PRINT ""
		LOCATE , 28: PRINT ""
		LOCATE , 28: PRINT ""
		LOCATE , 28: PRINT ""
		LOCATE , 28: PRINT ""
		COLOR 14
		LOCATE , 22: PRINT cond.red$
		COLOR 2
		LOCATE , 28: PRINT "Option...> "
		COLOR 6, 1
		LOCATE , 20: PRINT "F1-Batch. F4-Return."
		LOCATE 19, 38: COLOR 2, 0
		CALL inpnew(opt$, 201!, updwn%, "13,59-60,62")
	END SELECT
	skipexit% = 0

	opt% = VAL(opt$)

	IF updwn% = 13 AND opt% = 0 THEN updwn% = 62
	IF updwn% = 59 THEN opt% = -1
	IF updwn% = 60 THEN opt% = -1'F2 - Save & Cont
	IF updwn% = 62 THEN opt% = -2'F4 - Return

	LOOP UNTIL opt% >= -2 AND opt% <= -1


	sav% = 0
	doc.type$ = "TAX INVOICE"
	formtype$ = "*PRE.PRINTED.1"

	IF opt% = -2 THEN GOTO aRETURN
	IF opt% = -1 THEN mode$ = "ord": sav% = -1
	'IF opt% = 0 THEN mode$ = "ord": sav% = -1
	'IF opt% = 1 THEN mode$ = "nil": sav% = 0
	'IF opt% = 2 THEN mode$ = "ord": sav% = -1
	'IF opt% = 3 THEN mode$ = "inv": sav% = -1
	'IF opt% = 4 THEN mode$ = "b/o": sav% = -1

	IF sav% THEN
		CALL UpdateOrder(hord%, updwn%)
		IF updwn% = 60 THEN GOTO mline
	END IF

	'/// Print and exit or delete ///

		'- Only open the audit file when needed -<<
		cashonly$ = "M"


		'GOSUB OPEN.AUDIT '#8

		'IF mode$ = "inv" THEN CALL prtstk

		CLOSE #8
after.prtinv:

		'- Delete the order if it is fully invoiced
		Blanket.order% = -1
		IF MID$(ordhed.hreford$, 1, 1) <> "B" THEN Blanket.order% = 0
		IF MID$(ordhed.hreford$, 2, 2) < "01" THEN Blanket.order% = 0
		IF MID$(ordhed.hreford$, 2, 2) > "12" THEN Blanket.order% = 0

		anyDelDone% = 0

		IF NOT anyDelDone% THEN
		IF mode$ = "del" THEN
			autodel$ = "N"
			CALL delOrder(hord%, n%, clr%, autodel$, thissup$, norders%)
			anyDelDone% = -1
			CALL findorders(thissup$, norders%, hord%)
			'IF updwn% = 59 THEN GOTO det 'Delete aborted
			GOTO mlend
		END IF
		END IF


		IF NOT anyDelDone% THEN
		IF NOT Blanket.order% THEN
		IF tot.items& = 0 OR (Cash% AND mode$ = "inv") OR (Cash% AND mode$ = "b/o") THEN
			autodel$ = "Y"
			CALL delOrder(hord%, n%, clr%, autodel$, thissup$, norders%)
			anyDelDone% = -1
			CALL findorders(thissup$, norders%, hord%)
		END IF
		END IF
		END IF

		IF NOT anyDelDone% THEN
		IF mode$ = "inv" OR mode$ = "b/o" THEN
		IF CUS.BO = "N" THEN
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
GOTO igacc02.x

'--L O A D   I N V O I C E   D E T A I L S ???
load.det:
	FOR L% = 1 TO maxlines%
		in$(L%, 1) = "0": in$(L%, 2) = "   ": in$(L%, 3) = "": in$(L%, 4) = "": in$(L%, 5) = "": in$(L%, 6) = "0"
		in$(L%, 7) = "0": in$(L%, 8) = "0": in$(L%, 9) = "N/": in$(L%, 10) = "0": in$(L%, 11) = "0": in$(L%, 12) = "N"
		in$(L%, 13) = "0": in$(L%, 14) = "0": in$(L%, 15) = "": in$(L%, 16) = ""
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
	CALL findnext(hord%, norders%, ok%) ', add1$, add2$, add3$, add4$
	GET #48, hord%, ordhed
	invmsg1$ = ordhed.hnote1
	invmsg2$ = ordhed.hnote2

	hinvq = CVS(ordhed.hinvq$)

	nn% = -1: firstrec% = CVI(ordhed.hrrn$)
	CALL linkedl(rrn%(), nn%, firstrec%, hord%, 49)

	'-> Read throught the linked list of the details file
	dnext% = CVI(ordhed.hrrn$)
	L% = 0: m% = 0
	DO WHILE dnext% > 0
		GET #49, dnext%, orddet
		L% = L% + 1: IF L% > maxlines% THEN L% = maxlines%: EXIT DO
		ditem% = CVI(orddet.ditem$)
		ordqty% = CVI(orddet.dordq$)
		invqty% = CVI(orddet.dinvq$)
		price! = CVS(orddet.dprice$)
		rmc! = CVS(orddet.dtax$)
		IF ordqty% > 0 THEN
			m% = m% + 1
			CALL loadLine(m%, -1, ditem%, ordqty%, invqty%, price!, rmc!)'initial load
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
		CALL loadLine(m%, -1, ditem%, ordqty%, invqty%, price!, rmc!)
	NEXT

	TaxRate! = GST
	CALL add.up.order(tot.ltact!, tot.ord!, tot.weight!)
RETURN

detail:
	CALL setup("S T O C K    E N T R Y")
	btma$ = "F1-Save/Enter.    F6-Browse  "
	COLOR 8, 3: LOCATE 25, 1: PRINT btma$;

	CALL add.up.order(tot.ltact!, tot.ord!, tot.weight!)
	IF tot.exe! <> 0 THEN BEEP: CALL SNDMSG("Empty order has a dollar value!"): BEEP

	d.elem% = 1'Start at element number 1.
	scrn.pag% = 1
	L% = 1
detail.a:
	IF updwn% = 73 THEN L% = d.elem%'page up
	IF updwn% = 81 THEN L% = d.elem%'page down
	e.elem% = d.elem% + 14
	IF e.elem% > maxlines% THEN e.elem% = maxlines%
	COLOR 7, 0: LOCATE 2, 2: PRINT "�": LOCATE 2, 79: PRINT "�"
	COLOR 2, 0:
	LOCATE 2, 3: PRINT USING " Order:####"; hord%;
	a$ = "  " + LEFT$(CUS.sname$, 20) + " " + LEFT$(CUS.scont$, 20) + " " + CUS.search$ + CUS.stype$ + "  "
	COLOR 2
	PRINT a$
	COLOR 2

	LOCATE , 2: COLOR 6, 0: PRINT "Qty. Size   No.  Description                          S.O.O.  S.O.H.  Sum(LT) "


	COLOR 2
	LOCATE , 2: COLOR 2, 0: PRINT "컴컴쩡컴컴쩡컴컫컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴쩡컴컴컴쩡컴컴컴쩡컴컴컴컴"
	LOCATE , 2: COLOR 10: PRINT USING "p #"; scrn.pag%: COLOR 2
	sav.l% = L%
	FOR L% = d.elem% TO e.elem%
		CALL dsplyLine(L%, d.elem%)
		NEXT
	L% = sav.l%
	LOCATE , 2: COLOR 2, 0: PRINT "컴컴좔컴컴좔컴컨컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴컴좔컴컴컴좔컴컴컴좔컴컴컴컴"

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

igacc02.x:
	CLOSE #3
	CLOSE #43
	CLOSE #49
 

END SUB

SUB rightprice (price!) STATIC
	SELECT CASE CUS.stype$
	CASE "A": 'Factory Price
				price! = acstk.counter
	CASE "C": 'Contractor Price
				price! = acstk.contract
	CASE "D": 'Distributor Price
				price! = acstk.distributor * (1 + CUS.slevel / 100)
	CASE "G": 'Group Price
				price! = acstk.distributor * (1 + CUS.slevel / 100)
	CASE "H": 'Hardware Price
				price! = acstk.distributor * (1 + CUS.slevel / 100)
	CASE "I": 'Industrial Price
				price! = acstk.industrial
	CASE "M": 'Mitre Ten Price
				price! = acstk.distributor * (1 + CUS.slevel / 100)
	CASE "P": 'Painter Price
				price! = acstk.industrial
	CASE "S": 'Special Price
				price! = acstk.trade
	CASE "T": 'Trade Price
				price! = acstk.trade
	CASE "W": 'Best Possible Price
				price! = acstk.wholesalecost
	CASE "Y": 'Group Office Price
				price! = acstk.distributor * (1 + CUS.slevel / 100)
	CASE "Z": 'Group store price
				price! = acstk.distributor * (1 + CUS.slevel / 100)

	CASE ELSE: 'All Other Codes Are Retail Price
				price! = acstk.retail
	END SELECT

x.rightprice:

END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

SUB UpdateOrder (hord%, updwn%)
UpdateOrder:
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

		IF mode$ = "inv" THEN
			invqty% = keyed%
			ordqty% = 0
			dlinvq% = keyed%
			BoFlag$ = "N"
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
		IF ordqty% < 0 THEN ordqty% = 0

		GET #49, rrn%(L%), orddet
		LSET orddet.dinvq$ = MKI$(invqty%)
		LSET orddet.dordq$ = MKI$(ordqty%)
		LSET orddet.dlinvq$ = MKI$(dlinvq%)
		LSET orddet.ditem$ = MKI$(VAL(in$(L%, 4)))
		LSET orddet.dprice$ = MKS$(VAL(in$(L%, 6)))
		LSET orddet.dtax$ = MKS$(VAL(in$(L%, 16)))
		LSET orddet.dBo$ = BoFlag$
		LSET orddet.dfiller$ = in$(L%, 15)
		PUT #49, rrn%(L%), orddet: SOUND 20000, 1

		'-Update the stock file (remove previous)
		IF svrrn% >= 1 AND svrrn% <= maxacc% THEN
			GET #3, svrrn%, acstk
			acstk.sip% = acstk.sip% - sooqty%
			pack% = acstk.pack%
			IF pack% = 0 THEN pack% = 1
			PUT #3, svrrn%, acstk
			IF acstk.pkge% > 0 THEN
				GET #38, acstk.pkge%, msrmat
				msrmat.sip! = msrmat.sip! - sooqty% * pack%
				PUT #38, acstk.pkge%, msrmat
			END IF
			IF acstk.lid% > 0 THEN
				GET #38, acstk.lid%, msrmat
				msrmat.sip! = msrmat.sip! - sooqty% * pack%
				PUT #38, acstk.lid%, msrmat
			END IF
			IF acstk.label% > 0 THEN
				GET #38, acstk.label%, msrmat
				msrmat.sip! = msrmat.sip! - sooqty% * pack%
				PUT #38, acstk.label%, msrmat
			END IF
			IF acstk.pbox% > 0 THEN
				GET #38, acstk.pbox%, msrmat
				msrmat.sip! = msrmat.sip! - sooqty%
				PUT #38, acstk.pbox%, msrmat
			END IF
			IF acstk.boxlbl% > 0 THEN
				GET #38, acstk.boxlbl%, msrmat
				msrmat.sip! = msrmat.sip! - sooqty%
				PUT #38, acstk.boxlbl%, msrmat
			END IF
			IF acstk.manu% > 0 THEN
				GET #38, acstk.manu%, msrmat
				msrmat.sip! = msrmat.sip! - sooqty%
				PUT #38, acstk.manu%, msrmat
			END IF

		END IF

		'-Update the stock file
		ditem% = CVI(orddet.ditem$)
		IF ditem% < 1 OR ditem% > maxacc% THEN
			IF ditem% <> 0 THEN SOUND 50, 1
		ELSE
			GET #3, ditem%, acstk

			acstk.sip% = acstk.sip% + ordqty%
			pack% = acstk.pack%
			IF pack% = 0 THEN pack% = 1
			PUT #3, ditem%, acstk

			IF acstk.pkge% > 0 THEN
				GET #38, acstk.pkge%, msrmat
				msrmat.sip! = msrmat.sip! + ordqty% * pack%
				PUT #38, acstk.pkge%, msrmat
			END IF
			IF acstk.lid% > 0 THEN
				GET #38, acstk.lid%, msrmat
				msrmat.sip! = msrmat.sip! + ordqty% * pack%
				PUT #38, acstk.lid%, msrmat
			END IF
			IF acstk.label% > 0 THEN
				GET #38, acstk.label%, msrmat
				msrmat.sip! = msrmat.sip! + ordqty% * pack%
				PUT #38, acstk.label%, msrmat
			END IF
			IF acstk.pbox% > 0 THEN
				GET #38, acstk.pbox%, msrmat
				msrmat.sip! = msrmat.sip! + ordqty%
				PUT #38, acstk.pbox%, msrmat
			END IF
			IF acstk.boxlbl% > 0 THEN
				GET #38, acstk.boxlbl%, msrmat
				msrmat.sip! = msrmat.sip! + ordqty%
				PUT #38, acstk.boxlbl%, msrmat
			END IF
			IF acstk.manu% > 0 THEN
				GET #38, acstk.manu%, msrmat
				msrmat.sip! = msrmat.sip! + ordqty%
				PUT #38, acstk.manu%, msrmat
			END IF

			IF in$(L%, 2) = "***" THEN 'special items
				GET #3, ditem%, acstk
				IF acstk.no <> ditem% OR ditem <= 20 THEN
					acstk.no = ditem%
					acstk.desc1$ = in$(L%, 5)
					acstk.desc2$ = MID$(in$(L%, 5), 27, 10)

					acstk.counter = CVS(orddet.dprice$)
					acstk.contract = acstk.counter
					acstk.distributor = acstk.counter
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

		'tmp$ = tmp$ + " AF rrn/qty =" + STR$(ditem%) + "/" + STR$(ordqty%)
		'CALL sndmsg(tmp$): X$ = INPUT$(1)

	NEXT

	GET #48, hord%, ordhed
	hinvq = CVS(ordhed.hinvq$)
	LSET ordhed.hord$ = MKI$(hord%)
	LSET ordhed.hsup$ = CUS.search$ + CUS.stype$

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

