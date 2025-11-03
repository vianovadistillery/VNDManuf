DECLARE SUB prtinv (hord%, opt%, Cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%)
DECLARE SUB init ()
DECLARE SUB setaudit (n%)
DECLARE SUB parse (hord%, opt%, Cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, invprt1$, invprt2$, NameOverTyped$, AddrOvertyped$, Suburbovertyped$)
DECLARE SUB upd.who (chaudit%, chcus%, upd%)
'>>>>>>>>>>>>>>>> CHANGES MARKED AJD - 30/09/01 <<<<<<<<<<<<<<<<<<<
'1  G.S.T. CAN BE ELIMINATED USING A SMALL CHANGE - David can you
'   organise this one - It's beyond me - ajd1
'2  VS-NUMBER FIELD NOW USED FOR DUE DATE ON ORDER/PICK SLIP -ajd2
'3  Cosmetic changes to the list of orders on screen using * on the
'   order input screen to show due date (old V.S.field.) and customer. - ajd2
'-----------------------------------------------------------

'////////////////////////////////////////////////////////////////////////
'////    F U L L     D E B T O R S    I N V O I C E I N G
'////////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "DSMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CONST maxlines% = 45
	CONST debug% = 0   'Disable updating the WHO file.
	invnum# = 0

	 ' DIM SHARED orders%(100)
	'--- Added to try to set up sub programs ---
	DIM SHARED tot.invext!, tot.invord!
	DIM SHARED TaxRate!, DiscRate!
	'---
	DIM SHARED mode$, beg$
	DIM SHARED startinvnum%, startcrtnum%
	DIM SHARED maxsup%, maxform%, maxrmat%, maxacc%, maxtypes%, maxcus%, maxord%
	DIM SHARED ext.has.changed%, rec50%, ctl%, Cash%
	DIM SHARED vdisc!, Rate!, discovr!, climit!
	DIM SHARED Taxable AS CURRENCY
	DIM SHARED advalue AS CURRENCY
	DIM SHARED skipexit%
	DIM SHARED doc.type$, formtype$, sno%
	DIM SHARED tot.ord!, tot.ltact, tot.ltinv, tot.dollr, tot.items&
	DIM SHARED hord%
	DIM SHARED newsearch$
	DIM SHARED bysearch$
	DIM SHARED search.key$
	DIM SHARED tot.qty, Tot.taxvol
	DIM SHARED tot.dg200%, tot.dg60%, tot.dg20%, tot.dg10%, tot.dg4%, tot.dg2%, tot.dg1%, tot.dg850%, tot.dg500%, tot.dg300%, tot.dg250%, tot.dglt!
	DIM SHARED Discofftax!, extdisc!, inv.lt.printed!
	DIM SHARED Tender$, tax.in$
	DIM SHARED invmsg1$, invmsg2$, invmsg3$, invmsg4$
	DIM SHARED qk$, keyl%, rep$
	DIM SHARED auditfile$(15), naudit%, acstkf$
	keyl% = 20: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)

	'--- Added to try to set up sub programs ---
	DIM c%(8)
	DATA 2,7,10,13,18,56,63,72
	FOR i% = 1 TO 8: READ c%(i%): NEXT
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

	CALL setaudit(naudit%)
	cashonly$ = "M": auditname$ = auditfile$(naudit%)
	GOSUB OPEN.AUDIT
	CALL init
	CLOSE #8

	CALL parse(hord%, opt%, Cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, invmsg1$, invmsg2$, NameOverTyped$, AddressOverTyped$, Suburbovertyped$)

	'>>- Only open the audit file when needed -<<
	cashonly$ = "M": auditname$ = auditfile$(naudit%)
	IF opt% = 5 THEN cashonly$ = "Y"
	IF opt% = 9 AND Cash% THEN cashonly$ = "Y"
	GOSUB OPEN.AUDIT '#8
	CALL prtinv(hord%, opt%, Cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%)
	CLOSE #8

	rrn78% = 1
	GET #78, rrn78%, ordprt
	ordprt.hinvnum = invnum#
	ordprt.hinvnumrec = invnumrec%
	PUT #78, rrn78%, ordprt

	npgm$ = "DSINV01D"

	CALL EXITPGM(npgm$)
	ENVIRON "PARM$=/prt.."

	CHAIN npgm$
	END

SUB init
'///////////////////////////////////////////////////////////////////////
'///// Setup things
'///////////////////////////////////////////////////////////////////////
init:
	startinvnum% = 1
	startcrtnum% = 1
	beg$ = "yymm"
	mode$ = "ord"

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

SUB parse (hord%, opt%, Cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, invprt1$, invprt2$, NameOverTyped$, AddrOvertyped$, Suburbovertyped$)

	rrn78% = 1
	GET #78, rrn78%, ordprt
	hord% = ordprt.hord
	opt% = ordprt.hopt
	Cash% = ordprt.hcash
	chginv# = ordprt.hchginv
	chginv.rrn% = ordprt.hchginvrrn
	invnum# = ordprt.hinvnum
	invnumrec% = ordprt.hinvnumrec
	thissup$ = ordprt.hthissup
	norders% = ordprt.hnorders
	TaxRate! = ordprt.hTaxRate
	DiscRate! = ordprt.hDiscRate
	invprt1$ = ordprt.hnote1
	invprt2$ = ordprt.hnote2
	NameOverTyped$ = ordprt.hNameOvertyped
	AddrOvertyped$ = ordprt.hAddrOvertyped
	Suburbovertyped$ = ordprt.hSuburbOvertyped

	'Shared
	sno% = ordprt.gsno
	tax.in$ = ordprt.gtaxin
	Tender$ = ordprt.gtender
	doc.type$ = ordprt.gdoctype$
	formtype$ = ordprt.gformtype$

GET #48, hord%, ordhed

GET #43, sno%, cus
scur = CVS(cus.scur$): s30 = CVS(cus.s30$): s60 = CVS(cus.s60$): s90 = CVS(cus.s90$)
sdays% = CVI(cus.sdays$): climit = CVS(cus.climit$)
sterms = CVS(cus.sterms$): daysmax% = CVI(cus.daysmax$)

IF NameOverTyped$ > "" THEN
	cus.sname = NameOverTyped$
	cus.saddr = AddrOvertyped$
	cus.suburb = Suburbovertyped$
END IF

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

SUB prtinv (hord%, opt%, Cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%)
'////////////////////////////////////////////////////////////
'/////    P R I N T   I N V O I C E
'////////////////////////////////////////////////////////////
prtinv:
	'>>> Find highest document number of the same type <<<
	invnum# = 0
	'/// Find the end of the audit file
	adlast% = LOF(8) / 92
	startinvnum% = adlast%
	IF chginv# > 0 THEN startinvnum% = chginv.rrn%
	IF startinvnum% >= 1 THEN
		GET #8, startinvnum%, audit
		invnum# = VAL(audit.addocnum$)
		invnumrec% = adlast%
	END IF
		'           12345678901
	IF doc.type$ = "TAX INVOICE" THEN test$ = "DI"
	IF doc.type$ = "TAX CREDIT " THEN test$ = "DC"
	DO UNTIL audit.adtype$ = test$
		startinvnum% = startinvnum% - 1
		IF startinvnum% < 1 THEN startinvnum% = 1
		GET #8, startinvnum%, audit
		invnum# = VAL(audit.addocnum$)
		invnumrec% = adlast%
		IF startinvnum% <= 1 THEN EXIT DO
	LOOP
	IF startinvnum% = 1 AND audit.adtype$ <> test$ THEN
		invnum# = 0
	END IF
	upd.audit% = -1

	'>- Use the last invoice number
	IF Tender$ = "?" THEN invnum# = invnum# - 1
	'>>>>>>>> This section backs out the value on the audit file <<<<<<<<
	IF chginv# > 0 THEN
		GET #8, chginv.rrn%, audit
		invnum# = chginv# - 1
		upd.audit% = chginv.rrn%
		chginv# = 0: chginv.rrn% = 0'To prevent it happening next update!
		'>>> BACK OUT THE OLD AUDIT RECORD <<<
		cha% = 8'Channel of audit file
		chw% = 43'Channel of cus file
		gst! = audit.adtax!
		advalue = audit.advalue
		advalue = 0 - advalue
		adtax! = 0 - adtax!
		LSET audit.adsname$ = cus.sname$
		LSET audit.adcust$ = cus.search$ + cus.stype$
		audit.adtax! = gst!
		audit.advalue = advalue
		IF NOT Cash% THEN GET #chw%, sno%
		IF NOT debug% THEN CALL upd.who(cha%, chw%, upd.audit%)
	END IF
	'>>>> Set up statics for raw material entry
	LSET audit.adsname$ = cus.sname$
	LSET audit.addate$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
	IF doc.type$ = "TAX INVOICE" THEN
		LSET audit.adtype$ = "DI"
		LSET audit.adtext$ = "STANDARD INVOICE."
		IF Cash% THEN
			SELECT CASE Tender$
			CASE "1", "?": LSET audit.adtext$ = "Cash  "
			CASE "2": LSET audit.adtext$ = "Cheque"
			CASE "3": LSET audit.adtext$ = "Card  "
			CASE "4": LSET audit.adtext$ = "Counter  "
			CASE ELSE
			END SELECT
			END IF
		ELSE
			LSET audit.adtype$ = "DC"
			LSET audit.adtext$ = "CREDIT RETURN."
			IF Cash% THEN LSET audit.adtext$ = "Cash Credit.    "
		END IF

	 IF Tender$ = "4" THEN audit.adtype$ = "XX"

	 LSET audit.adcust$ = cus.search$ + cus.stype$
	 LSET audit.addate$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
	 audit.advalue = 0 'set Later
	 audit.adglacc! = 170!
	 LSET audit.adpaid$ = " "
	'>- The invoice for an order uses the detail rrn off the header file
	'>  2nd and subsequent invoices use the next rrn off the detail file.
	start.det.rec% = CVI(ordhed.hrrn$)
	inv.lt.printed = 0
	inv.lt.to.print = lt.inv

	tot.invext! = 0
	tot.invord! = 0  'Ordered litres
	invnum# = invnum# + 1
	invnum$ = MID$(STR$(invnum#), 2)
	LSET audit.addocnum$ = invnum$

	'>>>---- Open an invoice copy file
	a$ = STR$(invnum#)
	MID$(a$, 1, 1) = "0"
	a$ = "00000000" + a$
	b$ = RIGHT$(a$, 8)
	IF doc.type$ = "TAX INVOICE" THEN
		ext$ = ".\export\" + RIGHT$(a$, 8) + ".RDI"
		b$ = ".\invoices\" + b$ + ".INS"
		IF Tender$ = "?" THEN MID$(b$, LEN(b$) - 3, 4) = ".$$$"
		ELSE
		ext$ = ".\export\" + RIGHT$(a$, 8) + ".RDC"
		b$ = ".\invoices\" + b$ + ".CRS"
		END IF
	OPEN b$ FOR OUTPUT AS #98
	OPEN ext$ FOR OUTPUT AS #97

	tot.qty = 0
	tot.ext = 0
	tot.ltinv = 0
	Tot.taxvol = 0
	tot.dg200% = 0
	tot.dg60% = 0
	tot.dg20% = 0
	tot.dg10% = 0
	tot.dg4% = 0
	tot.dg2% = 0
	tot.dg1% = 0
	tot.dg850% = 0
	tot.dg500% = 0
	tot.dg300% = 0
	tot.dg250% = 0
	tot.dglt! = 0

	'//// Update the last invoice number for this order ////
	GET #48, hord%, ordhed
	RSET ordhed.linvnum$ = audit.addocnum$
	PUT #48, hord%, ordhed
	ldisc = CVS(ordhed.ldisc$)
	hinvq = CVS(ordhed.hinvq$)
	hordq = CVS(ordhed.hordq$)

	IF formtype$ = "*PRE.PRINTED.2" THEN
		'-Reverse Lines for tear off (Cash sale only)
		FOR i% = 1 TO 4 ' 4/6/2012 - was 9 for NEC pinwriter
			PRINT #98, CHR$(28); CHR$(82)  'Set reverse LF
		NEXT
		'PRINT #98, CHR$(27); "j"; CHR$(15); '>> Half a line jump
		PRINT #98, CHR$(28); CHR$(70);  'Reset forward LF
	END IF

Nextpage:
	more.on.pickslip% = 0

	IF formtype$ = "*PRE.PRINTED.1" THEN GOSUB actual.print.1
	IF formtype$ = "*PRE.PRINTED.2" THEN GOSUB actual.print.2


	'>- If there is more than a page on an order go and pick the details
	'>- up. Remember the rrn from the detail file.
	IF more.on.pickslip% THEN
		start.det.rec% = orddet.drrn%
		GOTO Nextpage
	END IF

	CLOSE #97
	CLOSE #98
	x! = FRE(-1): x! = FRE(-1)
	IF x! > 65000 AND Tender$ <> "?" THEN
		SHELL shella$
	END IF

	'////////////////////////////////////////////////////////////
	'>>>>>>>>>>>> Write to audit file record <<<<<<<<<<<<<<<<<<<<
	'////////////////////////////////////////////////////////////
	cha% = 8'Channel of audit file
	chw% = 43'Channel of cus file
	audit.advalue = advalue
	audit.adtax! = adtax
	GET #chw%, sno%, cus
	IF NOT debug% THEN CALL upd.who(cha%, chw%, upd.audit%)
	'>>- Only open the audit file when needed -<<


GOTO x.prtinv
'////////////////////////////////////////////////////////////
'/////    T H E   F I R S T  F O R M   T Y P E - INVOICE
'////////////////////////////////////////////////////////////
actual.print.1:
	'-- Print control
	heavy$ = CHR$(14) + CHR$(27) + "E"
	rheavy$ = CHR$(20) + CHR$(27) + "F"
	wide$ = CHR$(27) + "W1"
	rwide$ = CHR$(27) + "W0"

 ''/// Set page length to 51 lines (8 1/2 inches ///
	''/// This treats the current position as the top of page ///
	PRINT #98, CHR$(27); "C"; CHR$(51);
	PRINT #98, CHR$(27); "j"; CHR$(15); '>> Half a line jump

	'>- 4 prints at the top.
	PRINT #98, ""
	PRINT #98, ""
	PRINT #98, ""
	PRINT #98, ""

	'>-These were here before.
	PRINT #98, ""
	PRINT #98, " "
	PRINT #98, CHR$(15)'Condensed print
	IF doc.type$ = "TAX INVOICE" THEN
		 PRINT #98, "  Invoiced to:                                                              Delivery:"
	ELSE
		PRINT #98, "  Credited to:                                                              Delivery:"
	END IF
	PRINT #98, ""
'Export record
	WRITE #97, "DI-ID", "Debtor Invoice"
	WRITE #97, "BLANK", "cus.sname$, cus.search$, cus.stype$, cvi(cus.sno), cus.saddr$, cus.saddr2$, cus.suburb$, cus.spcode$, pickup.pname1$, pickup.pname2$, pickup.pname3$, pickup.pname4$"
	WRITE #97, "DIHED", RTRIM$(cus.sname$), RTRIM$(cus.search$), RTRIM$(cus.stype$), CVI(cus.sno), RTRIM$(cus.saddr$), RTRIM$(cus.saddr2$), RTRIM$(cus.suburb$), RTRIM$(cus.spcode$), RTRIM$(PICKUP.pname1$), RTRIM$(PICKUP.pname2$), RTRIM$(PICKUP.pname3$ _
), RTRIM$(PICKUP.pname4$)
	WRITE #97, "BLANK", "ordhed.hreford$, ordhed.linvnum$, FNDYY$(ordhed.hdate$), ordhed.htaxe$, DATE$, GL, Contact, phone, PICKUP.pname1$, PICKUP.pname2$,PICKUP.pname3$, PICKUP.pname4$"
	p1$ = RTRIM$(PICKUP.pname1$)
	p2$ = RTRIM$(PICKUP.pname2$)
	p3$ = RTRIM$(PICKUP.pname3$)
	p4$ = RTRIM$(PICKUP.pname4$)
	cphone$ = cus.sphone1$
	WRITE #97, "DIINF", RTRIM$(ordhed.hreford$), ordhed.linvnum$, FNDYY$(ordhed.hdate$), FNDYY$(MID$(ordhed.htaxe$, 1, 9)), MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2), CVS(cus.sgl$), cus.scont$, cphone$, p1$, p2$, p3$, p4$

	PRINT #98, USING "  &\                            \&               \                            \     "; wide$; cus.sname$; rwide$; PICKUP.pname1$
	PRINT #98, USING "  &\                            \&               \                            \     "; wide$; cus.saddr$; rwide$; PICKUP.pname2$
	PRINT #98, USING "  &\                            \&               \                            \     "; wide$; cus.saddr2$; rwide$; PICKUP.pname3$
	PRINT #98, USING "  &\                    \    \  \&               \                            \              "; wide$; cus.suburb$; cus.spcode$; rwide$; PICKUP.pname4$
	PRINT #98, ""
	PRINT #98, " "
	PRINT #98, USING "                                                                                                                   \       \  "; ordhed.linvnum$
	PRINT #98, USING "!                                          !!!\         \!!!"; CHR$(18); CHR$(14); CHR$(27); "E"; doc.type$; CHR$(15); CHR$(27); "F"

	PRINT #98, USING "  \    \ - ###     \       \     \           \    \           \               A.B.N. - 52 106 096 655               \       \ "; cus.search$ + cus.stype$; sno%; FNDYY$(ordhed.hdate$); ordhed.hreford$; ordhed.htaxe$; MID$(DATE$, 4 _
, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
	PRINT #98, " "
	PRINT #98, " "
	PRINT #98, " "
	'>>>> Read throught the linked list of the details file <<<<
	dnext% = start.det.rec%
	l% = 0: lin% = 0
	DO WHILE dnext% > 0 AND lin% < 19
		GET #49, dnext%, orddet
		l% = l% + 1
		'>>> Decode the detail file <<<
		dord% = orddet.dord%
		ditem% = CVI(orddet.ditem$)
		dlinvq% = CVI(orddet.dlinvq$)
		IF ditem% < 1 OR ditem% > maxacc% OR dlinvq% = 0 THEN
			'PRINT#98,      "                                                                                                                              "
		ELSE
			lin% = lin% + 1
			GET #3, ditem%, acstk
			dprice = CVS(orddet.dprice$)
			dordq% = CVI(orddet.dordq$)
			dinvq% = CVI(orddet.dinvq$)
			size! = VAL(acstk.size$)
			dtax = CVS(orddet.dtax$)
			ext! = (dprice + dtax) * dlinvq%
			tot.ext = tot.ext + ext!
			SELECT CASE acstk.unit$
			CASE "LT": ltinv! = dlinvq% * size!
			CASE "ML": ltinv! = dlinvq% * size! / 1000
			CASE ELSE: ltinv! = 0
			END SELECT

			'>>
			SELECT CASE acstk.unit$
			CASE "LT": ltinv.real! = dlinvq% * size!
			CASE "LS": ltinv.real! = dlinvq% * size!
			CASE "ML": ltinv.real! = dlinvq% * size! / 1000
			CASE "MS": ltinv.real! = dlinvq% * size! / 1000
			CASE ELSE: ltinv.real! = 0
			END SELECT

			tot.ltinv = tot.ltinv + ltinv
			IF dtax > 0 THEN
				Tot.taxvol = Tot.taxvol + ltinv'wHAT
				END IF
			IF acstk.dgflag$ = "3" THEN
				tot.dglt! = tot.dglt! + ltinv.real!
				SELECT CASE size!
				CASE 200: tot.dg200% = tot.dg200% + dlinvq%
				CASE 60: tot.dg60% = tot.dg60% + dlinvq%
				CASE 20: tot.dg20% = tot.dg20% + dlinvq%
				CASE 10: tot.dg10% = tot.dg10% + dlinvq%
				CASE 4: tot.dg4% = tot.dg4% + dlinvq%
				CASE 2: tot.dg2% = tot.dg2% + dlinvq%
				CASE 1: tot.dg1% = tot.dg1% + dlinvq%
				CASE 850: tot.dg850% = tot.dg850% + dlinvq%
				CASE 500: tot.dg500% = tot.dg500% + dlinvq%
				CASE 300: tot.dg300% = tot.dg300% + dlinvq%
				CASE 250: tot.dg250% = tot.dg250% + dlinvq%
				CASE ELSE: tot.dglt! = tot.dglt! - ltinv.real!
				END SELECT
				END IF
			IF dtax = 0 THEN
			PRINT #98, USING "####    \  \\ \   ####     \                             \ \        \                      ####.##               $$##,###.##  "; dlinvq%; acstk.size$; acstk.unit$; ditem%; acstk.desc1$; acstk.desc2$; dprice; ext!
			ELSE
			PRINT #98, USING "####    \  \\ \   ####     \                             \ \        \                      ####.##    #####.##   $$##,###.##  "; dlinvq%; acstk.size$; acstk.unit$; ditem%; acstk.desc1$; acstk.desc2$; dprice; dtax; ext!
			END IF
			tot.invext! = tot.invext! + ext!
			tot.invord! = tot.invord! + ltinv
			inv.lt.printed = inv.lt.printed + ltinv

			GOSUB writeexternal

			END IF

		'>>> Bottom of read equal loop <<<
		dnext% = orddet.drrn%
		LOOP
	FOR i% = lin% TO 19 - 1'to fit the invoice paper
		PRINT #98, "                                                                                                                             "
		NEXT
	PRINT #98, " "

	ldisc = ordprt.gvdisc
	advalue = ordprt.gadvalue
	adtax = ordprt.gadtax

	'>- If the pointer on the detail file is not zero the order
	'has more details, But these details might all be backordered.
	IF dnext% > 0 AND inv.lt.printed < hinvq THEN
		more.on.pickslip% = -1
		PRINT #98, ""
		PRINT #98, ""
		PRINT #98, ""
		PRINT #98, ""
		PRINT #98, ""
		PRINT #98, USING "                                                                                               &Continued...&"; heavy$; rheavy$
		GOTO XRETURN.1
	END IF


	invmsg3$ = ""
	invmsg4$ = ""
	IF tot.dg200% > 0 THEN invmsg3$ = invmsg3$ + " 200L=" + MID$(STR$(tot.dg200%), 2)
	IF tot.dg60% > 0 THEN invmsg3$ = invmsg3$ + " 60L=" + MID$(STR$(tot.dg60%), 2)
	IF tot.dg20% > 0 THEN invmsg3$ = invmsg3$ + " 20L=" + MID$(STR$(tot.dg20%), 2)
	IF tot.dg10% > 0 THEN invmsg3$ = invmsg3$ + " 10L=" + MID$(STR$(tot.dg10%), 2)
	IF tot.dg4% > 0 THEN invmsg3$ = invmsg3$ + " 4L=" + MID$(STR$(tot.dg4%), 2)
	IF tot.dg2% > 0 THEN invmsg3$ = invmsg3$ + " 2L=" + MID$(STR$(tot.dg2%), 2)
	IF tot.dg1% > 0 THEN invmsg3$ = invmsg3$ + " 1L=" + MID$(STR$(tot.dg1%), 2)
	IF tot.dg850% > 0 THEN invmsg3$ = invmsg3$ + " .85L=" + MID$(STR$(tot.dg850%), 2)
	IF tot.dg500% > 0 THEN invmsg3$ = invmsg3$ + " .5L=" + MID$(STR$(tot.dg500%), 2)
	IF tot.dg300% > 0 THEN invmsg3$ = invmsg3$ + " .3L=" + MID$(STR$(tot.dg300%), 2)
	IF tot.dg250% > 0 THEN invmsg3$ = invmsg3$ + " .25L=" + MID$(STR$(tot.dg250%), 2)
	IF invmsg3$ > "" THEN
		invmsg4$ = "DANGEROUS GOODS - CLASS 3 - ON THIS DELIVERY"
		invmsg3$ = invmsg3$ + "  Total= " + STR$(tot.dglt!) + "lt"
		END IF

	IF doc.type$ = "TAX INVOICE" THEN
	PRINT #98, USING "   LT/Ordered ##,###    LT/Invoiced ##,###       Rate/LT #.###      Backorder ##,###     Sub Total               $$##,###.##  "; tot.ord; tot.ltinv; Rate!; hordq; tot.ext
	ELSE
	PRINT #98, USING "   LT/Ordered ##,###    LT/Credited ##,###       Rate/LT #.###      Backorder ##,###     Sub Total               $$##,###.##  "; tot.ord; tot.ltinv; Rate!; hordq; tot.ext
	END IF


	IF ldisc! = 0 THEN
	PRINT #98, " "
	ELSE
	PRINT #98, USING "                                                                                         Discount                $$##,###.##  "; ldisc!
	END IF

'Write Export
	WRITE #97, "BLANK", "invmsg1$, invmsg2$, invmsg3$, invmsg4$"
	WRITE #97, "DIMSG", invmsg1$, invmsg2$, invmsg3$, invmsg4$
	WRITE #97, "BLANK", "tot.ltinv, tot.ord, Rate!, tot.ext, advalue, adtax "
	WRITE #97, "DITOT", tot.ltinv, tot.ord, Rate!, tot.ext, advalue, adtax


	PRINT #98, USING "  &\                                        \& "; wide$; invmsg1$; rwide$
	PRINT #98, USING "  &\                                        \& "; wide$; invmsg2$; rwide$;
	PRINT #98, USING "  G.S.T.                    $$####.##"; adtax '15 SPACES ADDED
	PRINT #98, " "
	PRINT #98, USING "  &\                                        \&"; wide$; invmsg3$; rwide$

	IF doc.type$ = "TAX INVOICE" THEN
	PRINT #98, USING "  &\                                                                                  \&   &AMOUNT DUE& \ \$$##,###.##  "; rwide$; invmsg4$; rwide$; heavy$; rheavy$; ordprt.gOSCurrency; advalue
	ELSE
	PRINT #98, USING "  &\                                                                                  \&   &  CREDIT  & \ \$$##,###.##  "; rwide$; invmsg4$; rwide$; heavy$; rheavy$; ordprt.gOSCurrency; advalue
	END IF

	'>Reverse of the four at the top
	'PRINT #98,
	'PRINT #98,
	'PRINT #98,
	'PRINT #98,

XRETURN.1:
		PRINT #98, CHR$(18); CHR$(12);
		'CLOSE #98

		shella$ = "COPY " + b$ + " LPT2"

RETURN
'/////////////////////////////////////////////////////////////
'/////    T H E   S E C O N D  F O R M   T Y P E  (CASH INVOICE)
'////////////////////////////////////////////////////////////
actual.print.2:
	'-- Print control
	heavy$ = CHR$(14) + CHR$(27) + "E"
	rheavy$ = CHR$(20) + CHR$(27) + "F"
	wide$ = CHR$(27) + "W1"
	rwide$ = CHR$(27) + "W0"

	''/// Set page length to 33 lines (5 1/2 inches ///
	''/// This treats the current position as the top of page ///
	PRINT #98, CHR$(27); "C"; CHR$(33);
	'>>>- Dont waste the six lines at the top of every form <<<
	'>>>  Each 30 is one line backwards
	PRINT #98, " "
	PRINT #98, " "
	PRINT #98, USING "   \                        \   \         \"; cus.sname$; doc.type$
	PRINT #98, USING "   \                            \ !!\       \!!"; cus.saddr$; CHR$(27); "E"; ordhed.linvnum$; CHR$(27); "F"
	PRINT #98, USING "   \                    \    \  \ !Date..\      \!"; cus.suburb$; cus.spcode$; CHR$(15); MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2); CHR$(18)
	PRINT #98, CHR$(15);
	PRINT #98, " "
	PRINT #98, CHR$(27); "j"; CHR$(15); '>> Half a line jump
	PRINT #98, " "

'Export record
	WRITE #97, "CS-ID", "Debtor Invoice"
	WRITE #97, "BLANK", "cus.sname$, cus.search$, cus.stype$, cvi(cus.sno), cus.saddr$, cus.saddr2$, cus.suburb$, cus.spcode$, pickup.pname1$, pickup.pname2$, pickup.pname3$, pickup.pname4$"
	WRITE #97, "DIHED", RTRIM$(cus.sname$), RTRIM$(cus.search$), RTRIM$(cus.stype$), CVI(cus.sno), RTRIM$(cus.saddr$), RTRIM$(cus.saddr2$), RTRIM$(cus.suburb$), RTRIM$(cus.spcode$), RTRIM$(PICKUP.pname1$), RTRIM$(PICKUP.pname2$), RTRIM$(PICKUP.pname3$ _
), RTRIM$(PICKUP.pname4$)'??
	WRITE #97, "BLANK", "ordhed.hreford$, ordhed.linvnum$, FNDYY$(ordhed.hdate$), FNDYY$(mid$(ordhed.htaxe$,1,9)), DATE$, pickup.pname1$, pickup.pname2$, pickup.pname3$, pickup.pname4$"
	WRITE #97, "DIINF", RTRIM$(ordhed.hreford$), ordhed.linvnum$, FNDYY$(ordhed.hdate$), ordhed.htaxe$, MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2), RTRIM$(PICKUP.pname1$), RTRIM$(PICKUP.pname2$), RTRIM$(PICKUP.pname3$),  _
RTRIM$(PICKUP.pname4$)

'>>>> Read throught the linked list of the details file <<<<
	dnext% = start.det.rec%
	l% = 0: lin% = 0
	DO WHILE dnext% > 0 AND lin% < 16
		GET #49, dnext%, orddet
		l% = l% + 1
		'>>> Decode the detail file <<<
		dord% = orddet.dord%
		ditem% = CVI(orddet.ditem$)
		dlinvq% = CVI(orddet.dlinvq$)
		IF ditem% < 1 OR ditem% > maxacc% OR dlinvq% = 0 THEN
			PRINT #98, "                                                                                                                              "
		ELSE
			lin% = lin% + 1
			GET 3, ditem%, acstk
			dprice = CVS(orddet.dprice$)
			dordq% = CVI(orddet.dordq$)
			dinvq% = CVI(orddet.dinvq$)
			size = VAL(acstk.size$)
			dtax = CVS(orddet.dtax$)
			ext! = (dprice + dtax) * dlinvq%
			tot.ext = tot.ext + ext!
			ltinv = 0
			IF acstk.unit$ = "LT" THEN ltinv = dlinvq% * size
			IF acstk.unit$ = "ML" THEN ltinv = dlinvq% * size / 1000
			tot.ltinv = tot.ltinv + ltinv
			IF dtax > 0 THEN
				Tot.taxvol = Tot.taxvol + ltinv
				END IF

			PRINT #98, USING "    ####  \ \\\ \                       \ \        \   ####.##   ###,###.##"; dlinvq%; acstk.size$; acstk.unit$; acstk.desc1$; acstk.desc2$; dprice + dtax; ext!
			inv.lt.printed = inv.lt.printed + ltinv
			GOSUB writeexternal
			END IF

		'>>> Bottom of read equal loop <<<
		dnext% = orddet.drrn%
		LOOP
	FOR i% = lin% TO 16
		PRINT #98, "  "
	NEXT

	ldisc = ordprt.gvdisc
	advalue = ordprt.gadvalue
	adtax = ordprt.gadtax

	'>- If the pointer on the detail file is not zero the order
	'has more details, But these details might all be backordered.
	IF dnext% > 0 AND inv.lt.printed < hinvq THEN
		more.on.pickslip% = -1
		PRINT #98, ""
		PRINT #98, ""
		PRINT #98, USING "                                                &Continued...&"; heavy$; rheavy$
		GOTO XRETURN.2
	END IF


	IF doc.type$ = "TAX INVOICE" THEN
	PRINT #98, USING "    V/Discount on ##,###Lt at #.###/Lt               Total.... $$###,###.## "; tot.ltinv; Rate!; tot.ext
	ELSE
	PRINT #98, USING "    Lt/Credited = ##,###Lt at #.###/Lt               Total.... $$###,###.## "; tot.ltinv; Rate!; tot.ext
	END IF
	PRINT #98, USING "    \                                    \           Discount.  $$##,###.## "; invmsg1$; ldisc!

	PRINT #98, USING "    \                                    \           G.S.T....  $$##,###.## "; invmsg2$; adtax
	IF doc.type$ = "TAX INVOICE" THEN
	PRINT #98, USING "         A.B.N. - 52 106 096 655          &AMOUNT DUE& $$###,###.## "; heavy$; rheavy$; advalue
	ELSE
	PRINT #98, USING "    \                                    \&  CREDIT  &  $$##,###.## "; invmsg3$; heavy$; rheavy$; advalue
	END IF
	PRINT #98,
	PRINT #98,
	PRINT #98,

'Write Export
	WRITE #97, "BLANK", "invmsg1$, invmsg2$, invmsg3$, invmsg4$"
	WRITE #97, "DIMSG", invmsg1$, invmsg2$, invmsg3$, invmsg4$
	WRITE #97, "BLANK", "tot.ltinv, tot.ord, Rate!, tot.ext, advalue, adtax "
	WRITE #97, "DITOT", tot.ltinv, tot.ord, Rate!, tot.ext, advalue, adtax


XRETURN.2:
	PRINT #98, CHR$(18); CHR$(12);

	'Advance lines for tear off
	FOR i% = 1 TO 9
		PRINT #98, ""
	NEXT

	'CLOSE #98

	shella$ = "COPY " + b$ + " LPT3"
RETURN

writeexternal:
IF dprice = 0 THEN
WRITE #97, "DIDET", dlinvq%, acstk.size$, acstk.unit$, ditem%, acstk.desc1$, acstk.desc2$, dprice, dtax, ext!, acstk.rmc, 0, acstk.cogs, 0
ELSE
WRITE #97, "DIDET", dlinvq%, acstk.size$, acstk.unit$, ditem%, acstk.desc1$, acstk.desc2$, dprice, dtax, ext!, acstk.rmc, 1 - (acstk.rmc / dprice), acstk.cogs, 1 - (acstk.cogs / dprice)
END IF
RETURN
x.prtinv:
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
