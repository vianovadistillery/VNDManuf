DECLARE SUB supqtyconv (rec%, purconv)
DECLARE SUB upd.who (cha%, chw%, upd.audit%)
DECLARE SUB getdt (OSCurrency$, updwn%)
DECLARE SUB accbrowse (rec%)
DECLARE SUB add.bo.msg (updwn%)
DECLARE SUB add.up.order (tot.ltact!, tot.ord!, tot.ext!)
DECLARE SUB addmessage (invmsg1$, invmsg2$, invmsg3$, invmsg4$)
DECLARE SUB cf8 (l%, d.elem%, newdata$)
DECLARE SUB change.disc (discovr!)
DECLARE SUB chglin (ln%, l%, d.elem%, updwn%)
DECLARE SUB delOrder (hord%, n%, clr%, autodel$, thissup$, norders%)
DECLARE SUB dsply (sno%, norders%)
DECLARE SUB dsplyLine (l%, d.elem%)
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
DECLARE SUB parse (hord%, opt%, Cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, invmsg1$, invmsg2$)
DECLARE SUB prtinv (hord%, opt%, Cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, OSCurrency$)
DECLARE SUB prtpslip (hord%, opt%, discovr!)
DECLARE SUB rightprice (price!)
DECLARE SUB search.month (rec%, begyymd$)
DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB setaudit (n%)
DECLARE SUB UpdateOrder (hord%, updwn%)

	'Added to try to set up sub programs ---
	COMMON SHARED c%(), in$(), rrn%()
	COMMON SHARED auditfile$(), orders%()

	COMMON SHARED mode$, beg$
	COMMON SHARED TaxRate!, DiscRate!
	COMMON SHARED maxsup%, maxform%, maxrmat%, maxacc%, maxtypes%, maxcus%, maxord%
	COMMON SHARED ext.has.changed%, rec50%, ctl%, Cash%
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
	CONST gst! = 10  '10%

	DIM SHARED c%(8), in$(maxlines%, 17), rrn%(maxlines%)
	'1=qty%,2=size,3=unit,4=itm,5=desc,6=price,7=SOH,8=ext
	'9=tax flag,10=ordqty%,11=Invqty,12=BoFlag,13=save qty,14=Save item
	'15-unitprice
	DIM SHARED orders%(1001), auditfile$(15)

	keyl% = 20: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)

	DATA 2,7,10,13,18,56,63,72
	FOR i% = 1 TO 8: READ c%(i%): NEXT
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

SUB browse.idx (firstonscreen%, ch1%, ch2%) STATIC
	PCOPY 0, 1
	max% = LOF(ch1%) / 7
	maxbpage% = 20
	bbtm$ = " F1-Return.      F3-Search       F5-Swap information     F7-Totals    "
	GOSUB binit
	bdatatype$ = "name"
	xsearch$ = ""
	btype$ = "keyed"
	GOSUB bsetfilekey
	skey$ = SPACE$(LEN(filekey$))
	'//////////////////////////////////////////////////////
	'>>>>> B R O W S E   T H E   F I L E
	'//////////////////////////////////////////////////////
	CALL setup(bheading$)
	CALL prtbtm(bbtm$)
	rec2% = firstonscreen%
	GOSUB b.dsply
	'>>>>> whats the next record to browse from
2540
	LOCATE 2, 21: COLOR 7, 0: PRINT "ออต"; : LOCATE , 49: PRINT "ฦออ": COLOR 2, 0
	IF btype$ = "keyed" THEN
		COLOR 2, 0
		LOCATE 2, 24: PRINT "From key ..........>";
		LOCATE 2, 44
		CALL inpnew(keyed$, 205!, updwn%, "13,59-61,63,65,72-73,80-81")
		keyed$ = UCASE$(keyed$)
		IF VAL(keyed$) > 0 THEN arrival$ = keyed$: keyed$ = "": btype$ = "arrival"
		COLOR 2, 0
	ELSE
		COLOR 2, 0
		LOCATE 2, 24: PRINT "From number........>";
		LOCATE 2, 44
		CALL inpnew(arrival$, 205!, updwn%, "13,59-61,63,65,72-73,80-81")
		arrival$ = UCASE$(arrival$)
		IF VAL(arrival$) = 0 AND LEN(arrival$) > 1 THEN keyed$ = arrival$: arrival$ = "": btype$ = "keyed"
		COLOR 2, 0
	END IF

	IF updwn% = 61 THEN
		COLOR 2, 0
		LOCATE 2, 24: PRINT "Search.>";
		LOCATE 2, 32
		CALL inpnew(xsearch$, 117!, updwn%, "13,59-60,63,65,72-73,80-81")
		COLOR 2, 0
		arrival$ = "1"
		btype$ = "arrival"
		updwn% = 13
	END IF

	SELECT CASE updwn%
	CASE 59: GOTO bret

	CASE 13:
		IF btype$ = "keyed" THEN
			LSET skey$ = keyed$
			GOSUB bsearchindex
			SELECT CASE ch2%

			CASE 43: rec2% = CVI(CUSX.wrrn$)
			CASE 44: rec2% = CVI(supx.wrrn$)
			CASE 64: rec2% = CVI(whox.wrrn$)

			CASE ELSE
			END SELECT
		ELSE
			rec2% = VAL(arrival$)
		END IF

		GOSUB b.dsply

	CASE 63:                        'Swap data typer
		SELECT CASE bdatatype$
		CASE "name": bdatatype$ = "data"
		CASE "data": bdatatype$ = "name"
		CASE ELSE: bdatatype$ = "name"
		END SELECT
		rec2% = firstonscreen% - maxbpage%
		GOSUB b.dsply
	CASE 65:
		t90@ = 0: t60@ = 0: t30@ = 0: tcur@ = 0
		rec% = 1
		GET #ch2%, rec%, who
		DO WHILE NOT EOF(ch2%)
			t90@ = t90@ + CVS(who.s90$)
			t60@ = t60@ + CVS(who.s60$)
			t30@ = t30@ + CVS(who.s30$)
			tcur@ = tcur@ + CVS(who.scur$)
			GET #ch2%, , who: rec% = rec% + 1
			LOOP
			ttotal@ = t90@ + t60@ + t30@ + tcur@
			LOCATE 24, 2
			PRINT USING "  &   $$###,###.## $$###,###.## $$###,###.## $$###,###.## $$####,###.##"; "Total"; t90@; t60@; t30@; tcur@; ttotal@;
			LOCATE 1, 1
	CASE 72:
			IF firstonscreen% < 1 THEN firstonscreen% = 1
			rec2% = firstonscreen% - 1
			GOSUB b.dsply
	CASE 80:
			IF firstonscreen% < 1 THEN firstonscreen% = 1
			rec2% = firstonscreen% + 1
			GOSUB b.dsply

	CASE 81:                'Next Page
		GOSUB b.dsply
	CASE 73:                'Prev page
		SELECT CASE btype$
		CASE "keyed"
			IF firstonscreen% < 1 THEN firstonscreen% = 1
			SELECT CASE ch2%
			CASE 43: GET #ch2%, firstonscreen%, cus
			CASE 44: GET #ch2%, firstonscreen%, sup
			CASE 64: GET #ch2%, firstonscreen%, who
			CASE ELSE
			END SELECT

			GOSUB bsetfilekey
			skey$ = filekey$
			GOSUB bsearchindex
			rec1% = rec1% - maxbpage%
			IF rec1% < 1 THEN rec1% = 1

			SELECT CASE ch2%
			CASE 43:
					GET #ch1%, rec1%, CUSX
					rec2% = CVI(CUSX.wrrn$)
			CASE 44:
					GET #ch1%, rec1%, supx
					rec2% = CVI(supx.wrrn$)
			CASE 64:
					GET #ch1%, rec1%, whox
					rec2% = CVI(whox.wrrn$)
			CASE ELSE
			END SELECT

		CASE "arrival"
			rec2% = firstonscreen% - maxbpage%
		END SELECT
		GOSUB b.dsply
	CASE ELSE
	END SELECT
GOTO 2540
'/////////////////////////////////////////////////////////////////////////////
'>>>      L I S T   A   P A G E
'/////////////////////////////////////////////////////////////////////////////
b.dsply:
	IF rec2% < 1 OR rec2% > max% THEN rec2% = 1
	COLOR 6, 0: LOCATE 3, 2
	IF bdatatype$ = "name" THEN PRINT bheadingname$ ELSE PRINT bheadingdata$
	COLOR 2, 0

	SELECT CASE ch2%
	CASE 43: GET #ch2%, rec2%, cus
	CASE 44: GET #ch2%, rec2%, sup
	CASE 64: GET #ch2%, rec2%, who
	CASE ELSE
	END SELECT

	'>> The index must be kept in sync
	saverec2% = rec2%
	GOSUB bsetfilekey
	skey$ = filekey$
	GOSUB bsearchindex
	SELECT CASE ch2%
	CASE 43:
		rec2% = CVI(CUSX.wrrn$)
		IF rec2% < 1 OR rec2% > max% THEN GET #ch1%, 1, CUSX
		rec2% = CVI(CUSX.wrrn$)
	CASE 44:
		rec2% = CVI(supx.wrrn$)
		IF rec2% < 1 OR rec2% > max% THEN GET #ch1%, 1, supx
		rec2% = CVI(supx.wrrn$)
	CASE 64:
		rec2% = CVI(whox.wrrn$)
		IF rec2% < 1 OR rec2% > max% THEN GET #ch1%, 1, whox
		rec2% = CVI(whox.wrrn$)

	CASE ELSE
	END SELECT

	IF rec2% < 1 OR rec2% > max% THEN GOTO x.B.dsply
	IF rec2% <> saverec2% THEN rec2% = saverec2%: SOUND 50, 1
	firstonscreen% = 0
	n% = 0
	SELECT CASE ch2%
	CASE 43: GET #ch2%, rec2%, cus
	CASE 44: GET #ch2%, rec2%, sup
	CASE 64: GET #ch2%, rec2%, who
	CASE ELSE
	END SELECT

	LOCATE 4, 2
	missed% = 0
	DO WHILE n% < maxbpage% AND rec2% >= 1 AND rec2% <= max%
		SELECT CASE ch2%
		CASE 43: GET #ch2%, rec2%, cus
		CASE 44: GET #ch2%, rec2%, sup
		CASE 64: GET #ch2%, rec2%, who
		CASE ELSE
		END SELECT

		GOSUB btest
		IF ok% THEN
			'> Save the first record on screen
			IF firstonscreen% = 0 THEN firstonscreen% = rec2%
			LOCATE , 2
			SELECT CASE ch2%
			CASE 43:
					xxx% = CVI(cus.sno$)
					IF xxx% >= 1000 THEN xxx% = xxx% - 1000
					IF xxx% >= 1000 THEN xxx% = xxx% - 1000
					scur! = CVS(cus.scur$): s30! = CVS(cus.s30$): s60! = CVS(cus.s60$): s90! = CVS(cus.s90$)
					stotal! = scur! + s30! + s60! + s90!
					IF bdatatype$ = "name" THEN
					phone$ = MID$(cus.sphone$, 1, 13)
					PRINT USING "### & & & &! &"; xxx%; LEFT$(cus.sname$, 35); LEFT$(cus.scont$, 16); phone$; cus.search$; cus.stype$; cus.active$
					ELSE
					PRINT USING "### &   $$###,###.## $$###,###.## $$###,###.## $$###,###.## $$####,###.##"; xxx%; cus.search$ + cus.stype$; s90!; s60!; s30!; scur!; stotal!
					END IF
			CASE 44:
					xxx% = CVI(sup.sno$)
					IF xxx% >= 1000 THEN xxx% = xxx% - 1000
					IF xxx% >= 1000 THEN xxx% = xxx% - 1000
					scur! = CVS(sup.scur$): s30! = CVS(sup.s30$): s60! = CVS(sup.s60$): s90! = CVS(sup.s90$)
					stotal! = scur! + s30! + s60! + s90!
					IF bdatatype$ = "name" THEN
					phone$ = MID$(sup.sphone$, 1, 13)
					PRINT USING "### & & & && &"; xxx%; LEFT$(sup.sname$, 35); LEFT$(sup.scont$, 16); phone$; sup.search$; sup.stype$; sup.active$
					ELSE
					PRINT USING "### &   $$###,###.## $$###,###.## $$###,###.## $$###,###.## $$####,###.##"; xxx%; sup.search$ + sup.stype$; s90!; s60!; s30!; scur!; stotal!
					END IF
			CASE 64:
					xxx% = CVI(who.sno$)
					IF xxx% >= 1000 THEN xxx% = xxx% - 1000
					IF xxx% >= 1000 THEN xxx% = xxx% - 1000
					scur! = CVS(who.scur$): s30! = CVS(who.s30$): s60! = CVS(who.s60$): s90! = CVS(who.s90$)
					stotal = scur! + s30! + s60! + s90!
					IF bdatatype$ = "name" THEN
					phone$ = MID$(who.sphone$, 1, 13)
					PRINT USING "### & & & &! &"; xxx%; LEFT$(who.sname$, 35); LEFT$(who.scont$, 16); phone$; who.search$; who.stype$; who.active$
					ELSE
					PRINT USING "### &   $$###,###.## $$###,###.## $$###,###.## $$###,###.## $$####,###.##"; xxx%; who.search$ + who.stype$; s90!; s60!; s30!; scur!; stotal!
					END IF
			CASE ELSE

			END SELECT
			n% = n% + 1
			END IF
		'>>> Read area for loop
		IF btype$ = "keyed" THEN
			SELECT CASE ch2%
			CASE 43:
				GET #ch1%, , CUSX
				rec2% = CVI(CUSX.wrrn$)
			CASE 44:
				GET #ch1%, , supx
				rec2% = CVI(supx.wrrn$)
			CASE 64:
				GET #ch1%, , whox
				rec2% = CVI(whox.wrrn$)

			CASE ELSE
			END SELECT

			ELSE
			rec2% = rec2% + 1
			END IF
	LOOP
	'Clear out to the end of screen
	rec% = 0
	FOR i% = n% + 1 TO maxbpage%
		IF rec% THEN
			 ttotal = scur! + s30! + s60! + s90!
			 PRINT USING "### &   $$###,###.## $$###,###.## $$###,###.## $$###,###.## $$####,###.##"; xxx%; "Total"; t90!; t60!; t30!; tcur!; ttotal!
			 rec% = 0
			 END IF
		LOCATE , 2
		PRINT SPACE$(78)
		NEXT
x.B.dsply:
RETURN
'//////////////////////////////////////////////////////////////////////////
'>>>>> Lookup index file Passed skey$ Returns SKEY, 0 if not found <<<<<
'>>>>> SKEY1, one after insertion place                               <<<<<
'//////////////////////////////////////////////////////////////////////////
bsearchindex:
	skey = 0: skey1 = 0: found% = 0
	IF skey$ = "     " THEN skey1 = 0: RETURN
	s% = 0: e% = max%
bsearchagain:
	rec1% = (e% - s%) / 2 + s%
	IF rec1% = 0 THEN skey = 0: skey1 = s%: RETURN
	SELECT CASE ch2%
	CASE 43:
		GET #ch1%, rec1%, CUSX
		IF CVI(CUSX.wrrn$) = 0 THEN LSET CUSX.wcde$ = STRING$(99, CHR$(255))

		aaa$ = CUSX.wcde$ + wtyp$
		IF CUSX.wcde$ + wtyp$ = skey$ THEN skey = rec1%: skey1 = rec1%: found% = -1: RETURN
		IF e% - s% = 1 THEN skey = 0: skey1 = s%: RETURN
		IF CUSX.wcde$ + wtyp$ < skey$ THEN s% = rec1%: GOTO bsearchagain
		IF CUSX.wcde$ + wtyp$ > skey$ THEN e% = rec1%: GOTO bsearchagain
	CASE 44:
		GET #ch1%, rec1%, supx
		IF CVI(supx.wrrn$) = 0 THEN LSET supx.wcde$ = STRING$(99, CHR$(255))

		aaa$ = supx.wcde$ + wtyp$
		IF supx.wcde$ + wtyp$ = skey$ THEN skey = rec1%: skey1 = rec1%: found% = -1: RETURN
		IF e% - s% = 1 THEN skey = 0: skey1 = s%: RETURN
		IF supx.wcde$ + wtyp$ < skey$ THEN s% = rec1%: GOTO bsearchagain
		IF supx.wcde$ + wtyp$ > skey$ THEN e% = rec1%: GOTO bsearchagain
	CASE 64:
		GET #ch1%, rec1%, whox
		IF CVI(whox.wrrn$) = 0 THEN LSET whox.wcde$ = STRING$(99, CHR$(255))

		aaa$ = supx.wcde$ + wtyp$
		IF whox.wcde$ + wtyp$ = skey$ THEN skey = rec1%: skey1 = rec1%: found% = -1: RETURN
		IF e% - s% = 1 THEN skey = 0: skey1 = s%: RETURN
		IF whox.wcde$ + wtyp$ < skey$ THEN s% = rec1%: GOTO bsearchagain
		IF whox.wcde$ + wtyp$ > skey$ THEN e% = rec1%: GOTO bsearchagain

	CASE ELSE
	END SELECT

RETURN
'//////////////////////////////////////////////////////////////////////////
'>>>
'//////////////////////////////////////////////////////////////////////////
binit:
	bheading$ = "BROWSE CUSTOMER FILE"
	btype$ = "keyed"
	btype$ = "arrival"
	bheadingname$ = "No. Supplier/Customer name              Contact              Telephone    KEY"
	bheadingdata$ = "No. Search          90+ days     60 Days     30 Days     Current        Total"

RETURN
'>>> -
bsetfilekey:
	filekey$ = "12345"
	SELECT CASE ch2%
	CASE 43: LSET filekey$ = cus.search$ + cus.stype$
	CASE 44: LSET filekey$ = sup.search$ + sup.stype$
	CASE 64: LSET filekey$ = who.search$ + who.stype$
	CASE ELSE
	END SELECT

RETURN
'>>> -
btest:
	SELECT CASE ch2%
	CASE 43:
		ok% = -1
		IF CVI(cus.sno$) <> rec2% THEN ok% = 0
		IF cus.sdate$ <= SPACE$(8) THEN ok% = 0 '.dc
	CASE 44:
		ok% = -1
		IF CVI(sup.sno$) <> rec2% THEN ok% = 0
		IF sup.sdate$ <= SPACE$(8) THEN ok% = 0 '.dc
	CASE 64:
		ok% = -1
		IF CVI(who.sno$) <> rec2% THEN ok% = 0
		IF who.sdate$ <= SPACE$(8) THEN ok% = 0 '.dc
	CASE ELSE
	END SELECT

	IF ok% AND xsearch$ > "" THEN
		ok1% = 0
		tmp$ = LCASE$(xsearch$)
		'??
		SELECT CASE ch2%
		CASE 43:
		IF ok1% = 0 AND INSTR(LCASE$(cus.sname$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(cus.saddr$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(cus.saddr2$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(cus.email$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(cus.www$), tmp$) > 0 THEN ok1% = -1
		CASE 44:
		IF ok1% = 0 AND INSTR(LCASE$(sup.sname$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(sup.saddr$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(sup.saddr2$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(sup.email$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(sup.www$), tmp$) > 0 THEN ok1% = -1
		CASE 64:
		IF ok1% = 0 AND INSTR(LCASE$(who.sname$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(who.saddr$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(who.saddr2$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(who.email$), tmp$) > 0 THEN ok1% = -1
		IF ok1% = 0 AND INSTR(LCASE$(who.www$), tmp$) > 0 THEN ok1% = -1
		CASE ELSE
		END SELECT

		'??

		IF NOT ok1% THEN
			ok% = 0
		END IF
	END IF

RETURN
bret:


PCOPY 1, 0
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
		IF updwn% = 60 THEN ctl% = ctl% - 2    'F2 - Back one
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
		TaxRate! = gst
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
	END IF
	LOCATE ln%, c%(1)
	in$ = in$(l%, 1)
	old.qty = VAL(in$(l%, 1))

	' Changed so you can add/edit lines again as per Marlaynes request.
	' It means that if items are received any changes made at invoicing point
	' won't be reflected in stocks. Could be added if important - which it isn't.
	'IF mode$ = "rec" THEN
	'  LOCATE ln%, c%(1) + 4
	'  arrow$ = ">"
	'  CALL inpnew(arrow$, 1!, updwn%, "13,59,63,68,72-73,80-81")
	'  LOCATE ln%, c%(1) + 4: PRINT "ณ"
	'ELSE
		CALL inpnew(in$, 204!, updwn%, "13,27,59-60,62-64,68,72-73,80-81")
	'END IF

	in$ = UCASE$(in$)
	IF updwn% = 27 THEN
		in$(l%, 1) = "0": in$(l%, 2) = "   ": in$(l%, 3) = "": in$(l%, 4) = "": in$(l%, 5) = "": in$(l%, 6) = "0"
		in$(l%, 7) = "0": in$(l%, 8) = "0": in$(l%, 9) = "N/": in$(l%, 10) = "0": in$(l%, 11) = "0": in$(l%, 12) = "N": in$(l%, 16) = "0": in$(l%, 17) = "0"
		CALL dsplyLine(l%, d.elem%)
		TaxRate! = gst
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
		GOTO cf1
	END IF

	IF updwn% = 63 THEN '-Instant price change
		PCOPY 0, 1
		IF VAL(in$(l%, 1)) = 0 THEN GOTO cf1

		keep$ = ""
		keep$ = in$(l%, 6)
		keepu$ = ""
		keepu$ = in$(l%, 16)

cp1:
		CALL BOX(4, 9, 77, 15, 3, 0, 1)
		i% = VAL(in$(l%, 4))
		IF i% > 0 AND i% < maxacc% THEN
			GET #38, i%, msrmat
		END IF
		
		COLOR 6, 0
		LOCATE 10, 5: PRINT USING "Company \     \   ->####  &              "; msrmat.search$; msrmat.no%; msrmat.Desc1$
					LOCATE 12, 5: PRINT "Current File Price>"
					LOCATE 13, 5: PRINT "This Invoice Price>"
					LOCATE 14, 5: PRINT "Update to File (Y/N) F1-No Change>          F5-Return to File Price"

		COLOR 6, 0
					LOCATE 11, 5: PRINT "                         Ex GST    Inc. GST   per" + STR$(msrmat.purqty%) + msrmat.SupUnit$ + " ex.    Inc"
		COLOR 2, 0
		CALL rightprice(fileprice!)
		testa = 0
		testa = VAL(in$(l%, 16))
		CALL ROUND(testa, 2.5)
		in$(l%, 16) = STR$(testa)
		LOCATE 12, 27: PRINT USING "$#####.##   $#####.##   $#####.##   $#####.##"; msrmat.PurCost; msrmat.PurCost * 1.1; fileprice!; fileprice! * 1.1
		LOCATE 13, 27: PRINT USING "$#####.##   $#####.##   $#####.##   $#####.##"; VAL(in$(l%, 16)); VAL(in$(l%, 16)) * 1.1; VAL(in$(l%, 6)); VAL(in$(l%, 6)) * 1.1
		LOCATE 13, 28
		a$ = in$(l%, 16)
		CALL inpnew(a$, 8.2, updwn%, "13,59,60,63")
		changeprice% = 0
		IF updwn% = 59 THEN
				PCOPY 1, 0
				GOTO cf1
		END IF
		IF updwn% = 63 THEN
			in$(l%, 16) = STR$(msrmat.PurCost)
			CALL rightprice(price!)
			in$(l%, 6) = STR$(price!)
			GOTO cp1u
		END IF
		IF updwn% = 60 THEN
				LOCATE 13, 40
				a$ = STR$(VAL(in$(l%, 16)) * 1.1)
				CALL inpnew(a$, 8.2, updwn%, "13,59,60,63")
				IF updwn% = 59 THEN
						PCOPY 1, 0
						GOTO cf1
				END IF
				IF updwn% = 60 THEN GOTO cp1
				IF updwn% = 63 THEN
					in$(l%, 16) = STR$(msrmat.PurCost)
					CALL rightprice(price!)
					in$(l%, 6) = STR$(price!)
					GOTO cp1u
				END IF

				IF updwn% = 13 THEN
						in$(l%, 16) = STR$(VAL(a$) / 1.1)
						CALL rightprice(newprice!)
						newprice! = newprice! / msrmat.PurCost * VAL(a$) / 1.1
						in$(l%, 6) = STR$(newprice!)
				END IF
			changeprice% = -1
		END IF
		
		IF NOT changeprice% THEN
						in$(l%, 16) = STR$(VAL(a$))
						CALL rightprice(newprice!)
						newprice! = newprice! / msrmat.PurCost * VAL(a$)
						in$(l%, 6) = STR$(newprice!)
		END IF
cp1u:    'update to file?
				LOCATE 13, 27: PRINT USING "$#####.##   $#####.##   $#####.##   $#####.##"; VAL(in$(l%, 16)); VAL(in$(l%, 16)) * 1.1; VAL(in$(l%, 6)); VAL(in$(l%, 6)) * 1.1
				LOCATE 14, 42
				b$ = " "
				CALL inpnew(b$, 101!, updwn%, "13,59,60")
				b$ = UCASE$(b$)
				IF updwn% = 59 THEN
					in$(l%, 6) = keep$
					in$(l%, 16) = keepu$
					GOTO x.cp1
				END IF
				IF updwn% = 60 THEN GOTO cp1
				IF b$ = "Y" THEN
						unit! = 0
					msrmat.PurCost = VAL(in$(l%, 16))
					PUT #38, i%, msrmat
					GOTO x.cp1
				END IF
				IF b$ = "N" THEN
					GOTO x.cp1
				END IF
		 GOTO cp1u
x.cp1:
		PCOPY 1, 0
		unit! = VAL(in$(l%, 16)) '?? to try get otype working
		CALL ROUND(unit!, 2.5)
		price! = -1
		ordqty% = VAL(in$(l%, 1))
		invqty% = 0
		m% = l%
	
		CALL loadLine(m%, 0, i%, ordqty%, invqty%, price!, unit!)
		CALL dsplyLine(l%, d.elem%)
		TaxRate! = gst
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
		
		GOTO cf1
	END IF


	IF updwn% = 64 THEN
		PCOPY 0, 1
		CALL accbrowse(rec%)
		PCOPY 1, 0
		GOTO cf1
	END IF
	IF updwn% = 68 AND mode$ <> "rec" THEN
		CALL get.order.vs(hord%, updwn%)
		updwn% = 59: skipexit% = -1'Emualate. exit update and continue
	END IF
	IF updwn% = 68 AND mode$ = "rec" THEN updwn% = 13
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
		CALL dsplyLine(l%, d.elem%)
		TaxRate! = gst 'Use the constant
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
	END IF

RETURN
	'-SIZE
cf2:
	'edit by PD to skip ean
'  ctl% = ctl% + 1
'  bysearch$ = "N"
'  in$(l%, 2) = ""
'RETURN
	LOCATE ln%, c%(2)
	learn% = -1
	IF VAL(in$(l%, 4)) = 0 THEN check$ = "13,59,60,62,27" ELSE check$ = ""
	'CALL inpnew(in$(l%, 2), 103!, updwn%, check$)
	IF check$ > "" THEN
	btm$ = ""
	FOR i% = 1 TO 79: btm$ = btm$ + CHR$(SCREEN(25, i%)): NEXT
	btma$ = "F1-Save/Print.   Enter Size or Scan Barcode or F4-Remove Barcode Assigment"

cf2UL:
		COLOR 8, 3: LOCATE 25, 1: PRINT btma$;
		LOCATE ln%, c%(2)
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
		in$(l%, 7) = "0": in$(l%, 8) = "0": in$(l%, 9) = "N/": in$(l%, 10) = "0": in$(l%, 11) = "0": in$(l%, 12) = "N": in$(l%, 16) = "0"
		CALL dsplyLine(l%, d.elem%)
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
				GET #38, ind%, msrmat
				'acstk.ean13 = 0
				PUT #38, ind%, msrmat
				CALL SNDMSG("Barcode assignment removed.")
			END IF
			updwn% = 13
			in$(l%, 2) = ""
			GOTO cf2
		END IF


		ditem% = ind%
		price! = -1
		ordqty% = VAL(in$(l%, 1))
		invqty% = 0
		m% = l%
		CALL loadLine(m%, 0, ditem%, ordqty%, invqty%, price!, unit!)
		IF nomatch% THEN
			in$(l%, 1) = ""
			in$(l%, 2) = ""
			in$(l%, 3) = ""
			in$(l%, 4) = ""
			in$(l%, 5) = ""
			in$(l%, 6) = ""
			in$(l%, 7) = ""
			in$(l%, 8) = ""
			
			GOTO cf1
		END IF
		CALL dsplyLine(l%, d.elem%)
		updwn% = 113 'Says EAN assigned
	END IF


	in$(l%, 2) = UCASE$(in$(l%, 2))
	a$ = "       ": LSET a$ = in$(l%, 2): in$(l%, 2) = a$

	bysearch$ = "N"
	IF in$(l%, 2) <> "       " AND VAL(in$(l%, 4)) = 0 THEN bysearch$ = "Y"

RETURN
	'-UNITS
cf3: LOCATE ln%, c%(3)
	CALL inpnew(in$(l%, 3), 102!, updwn%, "")
RETURN
	'-STOCK NUMBER
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
		CALL loadLine(m%, 0, ditem%, ordqty%, invqty%, price!, unit!)
		IF nomatch% THEN
			in$(l%, 1) = ""
			in$(l%, 2) = ""
			in$(l%, 3) = ""
			in$(l%, 4) = ""
			in$(l%, 5) = ""
			in$(l%, 6) = ""
			in$(l%, 7) = ""
			in$(l%, 8) = ""
			nomatch% = 0
			CALL dsplyLine(l%, d.elem%)
			GOTO cf1
		END IF

		CALL dsplyLine(l%, d.elem%)
	END IF
RETURN
	'-DESCRIPTION
cf5: LOCATE ln%, c%(5)
	IF bysearch$ = "N" THEN
		CALL inpnew(in$(l%, 5), 125!, updwn%, "")

	ELSE '/// Search away ///
		IF newsearch$ = "Y" THEN
			in$ = "": IF frombrowse% = -1 THEN in$ = msrmat.searchs$: frombrowse% = 0
			CALL inpnew(in$, 125!, updwn%, "13,59,60,64,62")
			IF LEN(in$) > 0 THEN
					in$ = UCASE$(in$)
					search.key$ = in$
					COLOR 13, 0
					LOCATE 3, 35: PRINT USING "\      \"; search.key$
					COLOR 2, 0
			END IF
			IF updwn% = 59 THEN GOTO xcf5
			IF updwn% = 60 THEN GOTO xcf5
			IF updwn% = 64 THEN
					PCOPY 0, 1
					CALL accbrowse(rec%)
					PCOPY 1, 0
					IF rec% < 1 OR rec% > maxacc% THEN rec% = 1
					GET #38, rec%, msrmat
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
		testa$ = LEFT$(testa$, 7)

		test1$ = MID$(qk$, 1, 1)
		test1$ = MID$(qk$, 1, 1)
		count% = 0
anext3:
		IF VAL(MID$(qk$, 16, 7)) = VAL(testa$) THEN
			test1$ = MID$(qk$, 1, 1)
			IF ind% > 0 AND ind% < maxrmat% THEN GET #38, ind%, msrmat
			LOCATE ln%, c%(4): PRINT USING "####"; ind%
			' disallow line if not from correct supplier
			IF NOT msrmat.search$ = custin$ THEN
				COLOR 13, 0
				LOCATE 3, 35: PRINT USING "Wrong Suppiler-\   \"; msrmat.search$
				COLOR 2, 0
				LOCATE ln%, 2
				PRINT "    ณ     ณ    ณ                                    ณ       ณ       ณ         "
				in$(l%, 1) = "": in$(l%, 2) = "": in$(l%, 3) = "": in$(l%, 4) = ""
				in$(l%, 5) = "": in$(l%, 6) = "": in$(l%, 7) = "": in$(l%, 8) = ""
				GOTO cf1
			END IF
			LOCATE ln%, c%(5): PRINT msrmat.Desc1$; " "
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
			CALL loadLine(m%, 0, ditem%, ordqty%, invqty%, price!, unit!)
		IF nomatch% THEN
			in$(l%, 1) = ""
			in$(l%, 2) = ""
			in$(l%, 3) = ""
			in$(l%, 4) = ""
			in$(l%, 5) = ""
			in$(l%, 6) = ""
			in$(l%, 7) = ""
			in$(l%, 8) = ""

			GOTO cf1
		END IF

			CALL dsplyLine(l%, d.elem%)
			'- Place the result of the search in the search key
			search.key$ = msrmat.search$
			COLOR 13, 0
			LOCATE 3, 35: PRINT USING "\      \"; search.key$
			COLOR 2, 0

			'>-Learn
			IF ean$ > "" AND acstk.ean13 <> VAL(ean$) THEN
				IF ditem% > 0 AND ditem% < maxacc% THEN
					GET #38, ditem%, msrmat
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

'          IF acstk.ean13 = 0 THEN
'            acstk.ean13 = VAL(ean$)
'            PUT #38, ditem%, msrmat
'            CALL SNDMSG("Barcode" + STR$(acstk.ean13) + " assigned.")
'          END IF

				END IF
			END IF
			ean$ = ""
		END IF

xcf5:
RETURN
	'-PRICE
cf6: LOCATE ln%, c%(6)
				'LOCATE ln%, 47: PRINT USING "####.##"; unit!;
				'CALL inpnew(in$(l%, 6), 5.2, updwn%, "")
RETURN
	'-TAX
cf7:
RETURN
x.chglin:

END SUB

SUB invoiceentry (hord%, addate$, adnum$, status$, exitexit%)
'?? From CPay01
invoiceentry:
	'Set Screen
	PCOPY 0, 1

	CALL setup("INVOICE PARTICULARS ENTRY")

	btm$ = " F1-Exit.  "
	COLOR 8, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
	COLOR 6
		d% = 5
		LOCATE d%, 3: PRINT "  Customer Card File....> "
			LOCATE , 3: PRINT "  Invoice Date..........> "
			LOCATE , 3: PRINT "  Invoice number........> "
			LOCATE , 3: PRINT "  Purchase Order........> "
			LOCATE , 3: PRINT "  Text..................> "
			LOCATE , 3: PRINT "  Payment Method........> "
			LOCATE , 3: PRINT "  Total Amount..........> "
			LOCATE , 3: PRINT "  MYOB Account..........> "
			LOCATE , 3: PRINT "  Notes.................> "
			LOCATE , 3: PRINT "                        > "
			
		COLOR 2


	'>>>> Set up static fields for raw material entry
	'Get order information
	GET #48, hord%, ordhed
	
	GET #44, sno%, sup

	CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)

	'>>>> Set up statics for raw material entry
	'Set Date
	wrkd$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)'??
	addate$ = FNDY$(wrkd$)
	adsname$ = sup.sname$
	adsname$ = sup.sname$
	adcust$ = sup.search$ + sup.stype$
	addocnum$ = "PROFORMA"
	adtext$ = text$
	adtype$ = "CI"
	adtext$ = "CREDITOR INVOICE."
	advalue = tot.ext!
	adglacc$ = sup.sgl$
	audit.adpaid$ = " "
	



' /////////// Display Entry Information \\\\\\\\\\\\\\\\\\\\\\

	COLOR 2
		LOCATE d%, 29: PRINT sup.search$ + sup.stype$
			LOCATE , 29: PRINT FNDYY$(addate$)
			LOCATE , 29: PRINT addocnum$
			LOCATE , 29: PRINT ordhed.hreford$
			LOCATE , 29: PRINT adtext$
			LOCATE , 29: PRINT  'audit.adcategory$
LOCATE , 29: PRINT USING "$#,###,###.##"; tot.allup
			LOCATE , 29: PRINT CVS(sup.sgl$)
			LOCATE , 29: PRINT ordhed.hnote1$
			LOCATE , 29: PRINT ordhed.hnote2$
'  //////////// Update Information \\\\\\\\\\\\\\\\\\\\\\
1180 '///////////////////  Invoice date

		LOCATE d% + 1, 29
		in$ = FNDYY$(addate$)
		CALL inpnew(in$, 100!, updwn%, "13,59,60,72,80")
		LSET addate$ = FNDY$(in$)
	 IF updwn% = 59 THEN
		IF mode$ = "r-i" THEN mode$ = "rec"
		IF mode$ = "inv" THEN mode$ = "ord"
		exitexit% = -1
		GOTO x.invoiceentry
	 END IF'Back to start
	 'GOSUB xer1
	 IF updwn% = 72 THEN updwn% = 60
	 IF updwn% = 60 THEN 1180

1250 '/////////////////// document number

	 updwn% = 0:
		LOCATE d% + 2, 29
		in$ = addocnum$
		COLOR 2
		CALL inpnew(in$, 108!, updwn%, "13,59,60,72,80")
		LSET addocnum$ = in$
		LSET a$ = in$ + SPACE$(22)
	 IF updwn% = 59 THEN GOTO endinp
	 IF updwn% = 72 THEN updwn% = 60
	 IF updwn% = 60 THEN 1180

1320 '/////////////////// Order Number

'    LOCATE d%+3, 29
'    in$ = ordhed.hreford$
'    CALL inpnew(in$, 115!, updwn%, "13,59,60,72,80")
'    LSET ordhded.hreford$ = in$
'   IF updwn% = 59 THEN GOTO endinp
'   IF updwn% = 72 THEN updwn% = 60
'   IF updwn% = 60 THEN 1250
'    job$ = ""
'    ordhded.hreford$ = job$
1490 '/////////////////// Text
	 LOCATE d% + 4, 29
		in$ = adtext$
		CALL inpnew(in$, 130!, updwn%, "13,59,60,72,80")
		LSET adtext$ = in$
		IF updwn% = 59 THEN GOTO endinp
		IF updwn% = 72 THEN updwn% = 60
		IF updwn% = 60 THEN 1250

1500 '/////////////////// Payment Method

		'LOCATE 19, 29
		'in$ = audit.adcategory$
		'CALL inpnew(in$, 116!, updwn%, "13,59,60,72,80")
		'LSET audit.adcategory$ = in$
		'IF updwn% = 59 THEN GOTO endinp
		'IF updwn% = 72 THEN updwn% = 60
		'IF updwn% = 60 THEN 1490


1470 '/////////////////// Total
	'LOCATE 20, 30
	'in$ = STR$(audit.adcredit)
	'      CALL inpnew(in$, 12.2, updwn%, "13,59,60,72,80")
	'audit.advalue = VAL(in$)
	'audit.advalue = ABS(audit.advalue)
	'audit.adcredit = audit.advalue
	'IF updwn% = 59 THEN GOTO endinp
	'IF updwn% = 72 THEN updwn% = 60
	'IF updwn% = 60 THEN 1490
	'LOCATE 20, 29: PRINT USING "$#,###,###.##"; audit.advalue

1600 '////////////////// G/L account number
	 'LOCATE 21, 30: updwn% = 1
	 'in$ = audit.adglacc$
	 '      CALL inpnew(in$, 6!, updwn%, "13,59,60,72,80")
	 'LSET audit.adglacc = in$
	 'IF updwn% = 59 THEN GOTO endinp
	 'IF updwn% = 72 THEN updwn% = 60
	 'IF updwn% = 60 THEN 1490

endinp:
	 IF updwn% = 59 OR updwn% = 1 THEN GOTO 1180
	'///////////////// EDIT KEY PARTS ////
	 '*-DATE--*'
	IF audit.addate$ = SPACE$(8) THEN msg$ = "Date not valid.": 'GOSUB er1: GOTO 1180

 '/////////////////// CONFIRM FINISHED ////

	 COLOR 14: LOCATE 19, 7: PRINT "All correct? (Y/N)..>";
	 updwn% = 0: in$ = "Y"
		LOCATE 19, 29
		CALL inpnew(in$, 101!, updwn%, "13,59-60")
	 IF updwn% = 59 OR updwn% = 1 THEN GOTO 1180 '??
	 IF updwn% = 60 THEN in$ = "N"
	 in$ = UCASE$(in$)
	 IF in$ <> "Y" AND in$ <> "N" THEN GOTO endinp
	 IF in$ = "N" THEN
		LOCATE 22, 2: PRINT SPACE$(40)
		GOTO 1490
		END IF
	 IF addocnum$ = "PROFORMA" GOTO 1250
	 'Set mode to inv for printing and save info to file
	 mode$ = "inv"
	 ordhed.hstatus$ = "I"
	 ordhed.hinvdate$ = addate$
	 ordhed.linvnum$ = addocnum$
	 ordhed.hsup$ = sup.search$ + sup.stype$
	 status$ = "I"
	 PUT #48, hord%, ordhed
x.invoiceentry:

	 PCOPY 1, 0

END SUB

SUB linkedl (rrn%(), n%, firstrec%, ord%, chd%) STATIC
'$INCLUDE: '.\SRC\linkedl.bi'
END SUB

SUB prtinv (hord%, opt%, Cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, OSCurrency$)

'////////////////////////////////////////////////////////////
'/////    P R I N T   I N V O I C E
'////////////////////////////////////////////////////////////

prtinv:

	GET #48, hord%, ordhed
	upd.audit% = -1
	GET #44, sno%, sup
	'>>>> Set up statics for raw material entry
	adsname$ = sup.sname$
	addate$ = ordhed.hinvdate$
	adtype$ = "CI"
	adtext$ = "CREDITOR INVOICE."
	adcust$ = ordhed.hsup$
	advalue = 0 'set Later
	adglacc$ = sup.sgl$
	audit.adpaid$ = " "
	tot.invext! = 0
	tot.invord! = 0  'Ordered litres
	invnum$ = STR$(invnum#)
	addocnum$ = ordhed.linvnum$
	start.det.rec% = CVI(ordhed.hrrn$)


	'>>>---- Open an invoice copy file
	IF RTRIM$(ordhed.hreford$) = "" THEN ordhed.hreford$ = MID$(DATE$, 4, 2) + MID$(DATE$, 1, 2) + sup.search$
	ext$ = ".\export\" + MID$(ordhed.hreford$, 1, 8) + ".RCI"
	CLOSE #97
	OPEN ext$ FOR OUTPUT AS #97

	tot.qty = 0
	tot.ext = 0
	tot.ltinv = 0
	Tot.taxvol = 0

	'//// Update the last invoice number for this order ////
	GET #48, hord%, ordhed
	RSET ordhed.linvnum$ = addocnum$
	PUT #48, hord%, ordhed
	ldisc = CVS(ordhed.ldisc$)
	hinvq = CVS(ordhed.hinvq$)
	hordq = CVS(ordhed.hordq$)
	start.det.rec% = CVI(ordhed.hrrn$)

	IF formtype$ = "*PRE.PRINTED.1" THEN GOSUB actual.print.1


	CLOSE #97
	x! = FRE(-1): x! = FRE(-1)
	IF x! > 65000 AND tender$ <> "?" THEN
	'??        SHELL shella$
	END IF

	'////////////////////////////////////////////////////////////
	 '>>>>>>>>>>>> Write to audit file record <<<<<<<<<<<<<<<<<<<<
	 '////////////////////////////////////////////////////////////
	 '/// Save payment total to update the cumstomer file.
	cha% = 8'Channel of audit file
	chw% = 44'Channel of sup file

	CLOSE #97

GOTO x.prtinv

'////////////////////////////////////////////////////////////
'/////    T H E   F I R S T  F O R M   T Y P E - INVOICE
'////////////////////////////////////////////////////////////
actual.print.1:
	WRITE #97, "CI-ID", "Creditor Invoice"
	WRITE #97, "BLANK", "sup.sname$", "sup.search$", "sup.stype$", "sup.sno", "sup.saddr$", "sup.saddr2$", "sup.suburb$", "sup.spcode$", "pickup.pname1$", "pickup.pname2$", "pickup.pname3$", "pickup.pname4$"
	WRITE #97, "CIHED", RTRIM$(sup.sname$), RTRIM$(sup.search$), RTRIM$(sup.stype$), CVI(sup.sno), RTRIM$(sup.saddr$), RTRIM$(sup.saddr2$), RTRIM$(sup.suburb$), RTRIM$(sup.spcode$), RTRIM$(pickup.pname1$), RTRIM$(pickup.pname2$), RTRIM$(pickup.pname3$ _
), RTRIM$(pickup.pname4$)'??

	WRITE #97, "BLANK", "PONum", "InvNo", "FNDYY$(ordhed.hdate$)", "ordhed.htaxe$", "DATE$", "GL", "contact", "phonenum", "dd-date", "ddocketnum"
	WRITE #97, "CIINF", RTRIM$(ordhed.hreford$), addocnum$, FNDYY$(ordhed.hdate$), FNDYY$(ordhed.htaxe$), FNDYY$(ordhed.hinvdate$), CVS(sup.sgl$), sup.scont$, sup.sphone1$, ordhed.hdddate$, ordhed.hdocket$

	WRITE #97, "BLANK", "dordq%", "PURQTY", "supunit$", "ditem%", "desc1$", "desc2$", "dprice", "dtax", "ext!", "purcost", "purunit", "usecost", "unseunit", "gl", "useqty"

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
			GET #38, ditem%, msrmat
			dprice = CVS(orddet.dprice$)
			unit! = CVS(MID$(orddet.dfiller$, 1, 4))
			dordq% = CVI(orddet.dordq$)
			dinvq% = CVI(orddet.dinvq$)
			size! = msrmat.purqty
			dtax = CVS(orddet.dtax$)
			ext! = (dprice + dtax) * dlinvq%
			tot.ext = tot.ext + ext!

			tot.invext! = tot.invext! + ext!
			tot.invord! = tot.invord! + ltinv
			inv.lt.printed = inv.lt.printed + ltinv
			END IF

		GOSUB WriteExternal
			PUT #38, ditem%, msrmat
		'>>> Bottom of read equal loop <<<

		dnext% = orddet.drrn%
		LOOP

	ldisc = ordprt.gvdisc
	advalue = ordprt.gadvalue
	adtax = ordprt.gadtax

	WRITE #97, "BLANK", "invmsg1$", "invmsg2$", "invmsg3$", "invmsg4$"
	WRITE #97, "CIMSG", invmsg1$, invmsg2$, invmsg3$, invmsg4$

	WRITE #97, "BLANK", "tot.ltinv", "tot.ord", "Rate!", "tot.ext", "advalue"
	WRITE #97, "CITOT", tot.ltinv, tot.ord, Rate!, tot.ext, tot.gst

RETURN

WriteExternal:
	ab$ = msrmat.SupUnit$ + "-" + msrmat.UseUnit$
	SELECT CASE ab$
	CASE "KG-LT": purconv = 1 / msrmat.Sg
	CASE "KG-ML": purconv = 1000 / msrmat.Sg
	CASE "LT-KG"
				IF msrmat.Sg <> 0 THEN purconv = msrmat.Sg
				IF msrmat.Sg = 0 THEN purconv = 1
	CASE "LT-GM"
				IF msrmat.Sg <> 0 THEN purconv = msrmat.Sg * 1000
				IF msrmat.Sg = 0 THEN purconv = 1000
	CASE "/M-EA": purconv = 1000
	CASE "/H-EA": purconv = 100
	CASE "MT-KG": purconv = 1000
	CASE "MT-GM": purconv = 1000000
	CASE "MT-LT": purconv = 1000 / msrmat.Sg
	CASE "MT-ML": purconv = 1000000 / msrmat.Sg
	CASE "LT-OZ": purconv = 28.413
	CASE "LT-UT": purconv = 64 * 28.413
	CASE "LT-ML": purconv = 1000
	CASE "KG-GM": purconv = 1000
	CASE "GM-LT": purconv = 1 / msrmat.Sg / 1000
	CASE "ML-LT": purconv = 1 / 1000
	CASE "KL-LT": purconv = 1000
	CASE "KL-KG": purconv = 1000 * msrmat.Sg
	CASE "TK": purconv = 1
	CASE ELSE: purconv = 1
	END SELECT
	purconv = purconv * msrmat.purqty%

WRITE #97, "CIDET", dlinvq%, msrmat.purqty%, msrmat.SupUnit$, ditem%, msrmat.Desc1$, msrmat.Desc2$, dprice, dtax, ext!, unit!, msrmat.PurUnit$, msrmat.UseCost, msrmat.UseUnit$, msrmat.Osoh, dlinvq% * purconv
msrmat.lastpur$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
RETURN

x.prtinv:


END SUB

SUB receivedelivery (hord%, hddate$, hdocket$, exitexit%)
'Set hdocket
'Set hddate
	GET #48, hord%, ordhed
	'Set Screen
	PCOPY 0, 1

	CALL setup("DELIVERY DOCKET INFORMATION")

	btm$ = " F1-Exit.  "
	COLOR 8, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
	COLOR 6
		d% = 5
		LOCATE d%, 3: PRINT "  Customer Card File....> "
			LOCATE , 3: PRINT "  Delivery Date.........> "
			LOCATE , 3: PRINT "  Docket number.........> "
			LOCATE , 3: PRINT "  Purchase Order........> "
			LOCATE , 3: PRINT "  Text..................> "

		COLOR 2


	'>>>> Set up static fields for raw material entry
	'Get order information
	GET #48, hord%, ordhed

	GET #44, sno%, sup

	CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)

	'>>>> Set up statics for raw material entry
	'Set Date
	wrkd$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)'??
	hddate$ = FNDY$(wrkd$)
	adsname$ = sup.sname$
	adsname$ = sup.sname$
	adcust$ = sup.search$ + sup.stype$
	hdocket$ = "PROFORMADD"




' /////////// Display Entry Information \\\\\\\\\\\\\\\\\\\\\\

	COLOR 2
		LOCATE d%, 29: PRINT sup.search$ + sup.stype$
			LOCATE , 29: PRINT FNDYY$(hddate$)
			LOCATE , 29: PRINT hdocket$
			LOCATE , 29: PRINT ordhed.hreford$
			LOCATE , 29: PRINT adtext$

'  //////////// Update Information \\\\\\\\\\\\\\\\\\\\\\

r1180:  '///////////////////  Invoice date"

		LOCATE d% + 1, 29
		in$ = FNDYY$(hddate$)
		CALL inpnew(in$, 100!, updwn%, "13,59,60,72,80")
		LSET hddate$ = FNDY$(in$)
	 IF updwn% = 59 THEN
		mode$ = "ord"
		exitexit% = -1
		GOTO x.receivedelivery 'Back to start
	 END IF
	 IF updwn% = 72 THEN updwn% = 60
	 IF updwn% = 60 THEN GOTO r1180

r1250: '/////////////////// document number

	 updwn% = 0:
		LOCATE d% + 2, 29
		in$ = hdocket$
		COLOR 2
		CALL inpnew(in$, 110!, updwn%, "13,59,60,72,80")
		LSET hdocket$ = in$
		
	 IF updwn% = 59 THEN GOTO x.rinp
	 IF updwn% = 72 THEN updwn% = 60
	 IF updwn% = 60 THEN GOTO r1180



x.rinp:
	IF updwn% = 59 OR updwn% = 1 THEN GOTO r1180
	'///////////////// EDIT KEY PARTS ////
	 '*-DATE--*'
	IF hddate$ = SPACE$(8) THEN msg$ = "Date not valid.": 'GOSUB er1: GOTO 1180

 '/////////////////// CONFIRM FINISHED ////

	 COLOR 14: LOCATE 19, 7: PRINT "All correct? (Y/N)..>";
	 updwn% = 0: in$ = "Y"
		LOCATE 19, 29
		CALL inpnew(in$, 101!, updwn%, "13,59-60")
	 IF updwn% = 59 OR updwn% = 1 THEN GOTO r1180 '??
	 IF updwn% = 60 THEN in$ = "N"
	 in$ = UCASE$(in$)
	 IF in$ <> "Y" AND in$ <> "N" THEN GOTO x.rinp
	 IF in$ = "N" THEN
		LOCATE 19, 2: PRINT SPACE$(40)
		GOTO r1250
		END IF
	 IF hdocket$ = "PROFORMADD" GOTO r1250

x.rinput:
	 ordhed.hdddate$ = hddate$
	 ordhed.hdocket$ = hdocket$
	 ordhed.hstatus$ = "R"
	 PCOPY 1, 0
	 PUT #48, hord%, ordhed

x.receivedelivery:

END SUB

SUB supqtyconv (rec%, purconv)

		GET #38, rec%, msrmat

		'PD Need to define and calculate purconv to convert between order qty and use qty.
		purconv = 1

			ab$ = msrmat.SupUnit$ + "-" + msrmat.UseUnit$
			SELECT CASE ab$
				CASE "EA-EA": purconv = 1
				CASE "KG-LT": purconv = 1 / msrmat.Sg
				CASE "KG-ML": purconv = 1000 / msrmat.Sg
				CASE "LT-KG"
					 IF msrmat.Sg <> 0 THEN purconv = msrmat.Sg
					 IF msrmat.Sg = 0 THEN purconv = 1
				CASE "LT-GM"
					 IF msrmat.Sg <> 0 THEN purconv = msrmat.Sg * 1000
					 IF msrmat.Sg = 0 THEN purconv = 1000
				CASE "/M-EA": purconv = 1000
				CASE "/H-EA": purconv = 100
				CASE "MT-KG": purconv = 1000
				CASE "MT-GM": purconv = 1000000
				CASE "MT-LT": purconv = 1000 / msrmat.Sg
				CASE "MT-ML": purconv = 1000000 / msrmat.Sg
				CASE "LT-OZ": purconv = 28.413
				CASE "LT-UT": purconv = 64 * 28.413
				CASE "LT-ML": purconv = 1000
				CASE "KG-GM": purconv = 1000
				CASE "GM-LT": purconv = 1 / msrmat.Sg / 1000
				CASE "ML-LT": purconv = 1 / 1000
				CASE "KL-LT": purconv = 1000
				CASE "KL-KG": purconv = 1000 * msrmat.Sg
				CASE "TK": purconv = 1
				CASE ELSE: purconv = 1
			END SELECT
				purconv = purconv * msrmat.supqty!


END SUB

'////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>  UPDATE THE SUPPLIER FILE <<<<<<<<<<<<<<<<<<<<<<
'////////////////////////////////////////////////////////////////////////////
SUB upd.who (chaudit%, chcus%, upd%) STATIC
'$INCLUDE: '.\src\updwho.bi'

'PRINT #97, "AUD01", audit.adrec, audit.addate, "??"
END SUB

