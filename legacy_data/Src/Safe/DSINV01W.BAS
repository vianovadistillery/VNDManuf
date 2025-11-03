DECLARE SUB openpslip (opt%)
DECLARE SUB prtjobslip (hord%, opt%)
DECLARE SUB parse (hord%, opt%, Cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, invprt1$, invprt2$, NameOverTyped$, AddrOvertyped$, Suburbovertyped$)
DECLARE SUB init ()
DECLARE SUB setaudit (n%)
'////////////////////////////////////////////////////////////////////////
'////    F U L L     D E B T O R S    I N V O I C E I N G
'////////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "DSMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CONST maxlines% = 45

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
	DIM SHARED tot.qty, tot.dtax, Tot.taxvol
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

	CALL parse(hord%, opt%, Cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, invmsg1$, invmsg2$, NameOverTyped$, AddressOverTyped$, Suburbovertyped$)

	CALL prtjobslip(hord%, opt%)


	rrn78% = 1
	GET #78, rrn78%, ordprt
	ordprt.hMode = "xx"
	PUT #78, rrn78%, ordprt


	npgm$ = "DSINV01D"

	CALL EXITPGM(npgm$)
	ENVIRON "PARM$=/prt.."

	CHAIN npgm$
	END

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
			CALL sndmsg("Waiting...")
			SLEEP 5
			CALL sndmsg("")
			END IF
		LOOP
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

SUB prtjobslip (hord%, opt%)
	IF hord% = 0 THEN GOTO x.prtjobslip
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
		PRINT #99, USING "³ Name....: \                                 \                               ³"; cus.sname$
		PRINT #99, USING "³ Address.: \                                 \ \                   \         ³"; cus.saddr$; cus.suburb$
		PRINT #99, USING "ÃÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ!"; "´"
		PRINT #99, USING "³ P/Slip ³ Account No. ³ O/Date    ³ Order No.     ³ Litres  ³ Due Date.....  !"; "³"
		PRINT #99, USING "³  ####  ³ \   \ - ### ³ \       \ ³ \           \ ³ ######  ³ \           \  ³"; hord%; cus.search$ + cus.stype$; sno%; fndyy$(ordhed.hdate$); ordhed.hreford$; hordq; ordhed.htaxe$ + ""
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

		FOR i% = l% TO 30
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

x.prtjobslip:


END SUB
