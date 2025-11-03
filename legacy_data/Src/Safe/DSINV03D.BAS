DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB upd.who (chaudit%, chcus%, upd%)
DECLARE SUB setaudit (n%)
DECLARE SUB get.order.vs (hord%, updwn%)
DECLARE SUB add.up.order (tot.ltact!, tot.ord!, tot.ltact.taxable!, tot.dtax!, tot.ext!)
DECLARE SUB cf8 (l%, s.elem%, newdata$)
DECLARE SUB dsply (sno%)
DECLARE SUB dsply.line (l%, s.elem%)
DECLARE FUNCTION funclimit$ (climit!)
DECLARE SUB load.line (m%, ditem%, ordqty%, invqty%, price!)
DECLARE SUB rightprice (price!)
'.dc - Complete
'////////////////////////////////////////////////////////////////////////
'////    F R E E   F O R M A T    D E B T O R S    I N V O I C I N G
'////////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "DSMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CONST maxlines% = 45
	keyl% = 20: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)
	invnum# = 0
'>>>---------------------------------------------------<<<
'>>> NOTE: This program is for Suppliers and Customers
'>>>       Pass parm of  /CR or /DB /--
'>>>---------------------------------------------------<<<
	DB.OR.CR$ = ENVIRON$("DB.OR.CR$")
	CR% = INSTR(COMMAND$, "/CR")
	D2% = INSTR(COMMAND$, "/--")
	IF CR% > 0 THEN DB.OR.CR$ = "CR"
	IF D2% > 0 THEN DB.OR.CR$ = "--"
	'DB.OR.CR$ = "CR"


	DIM SHARED c%(8), hdr$(10), in$(maxlines%, 11)
	DIM SHARED maxsup%, maxform%, maxrmat%, maxacc%, maxtypes%, maxcus%, maxord%
	DIM SHARED ext.has.changed%, tot.allup!
	DIM SHARED skipexit%
	DIM SHARED chi%, ch%
	DIM SHARED auditfile$(15), naudit%
	CALL setaudit(naudit%)

	DATA 2,7,10,13,18,56,63,72
	FOR i% = 1 TO 8: READ c%(i%): NEXT
	RESET
	typefields% = -1

	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\cusx.inc'
	'$INCLUDE: '\tpmanuf\src\supx.inc'
	'$INCLUDE: '\tpmanuf\src\cus.inc'
	'$INCLUDE: '\tpmanuf\src\sup.inc'
	'$INCLUDE: '\tpmanuf\src\acstk.inc'
	'$INCLUDE: '\tpmanuf\src\asaudit.inc'
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	'$INCLUDE: '\tpmanuf\src\pickup.INC'

	'$INCLUDE: '\tpmanuf\src\ordhed.inc'
	'$INCLUDE: '\tpmanuf\src\orddet.inc'

	SELECT CASE DB.OR.CR$
	CASE "CR": chi% = 45: ch% = 44: apgm$ = "CSMENU"
	CASE "DB": chi% = 23: ch% = 43: apgm$ = "DSMENU"
	CASE "--": chi% = 65: ch% = 64: apgm$ = "DSMENU"
	CASE ELSE
	END SELECT



	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxacc% = CVI(msmisc.max5$): maxtypes% = CVI(msmisc.max6$): maxcus% = CVI(msmisc.max7$)
	maxord% = 999

	cashonly$ = "M": auditname$ = auditfile$(naudit%)
	GOSUB OPEN.AUDIT '#8
	CLOSE #8
	parm$ = ENVIRON$("PARM$")
	IF VAL(parm$) > 0 THEN pass.getcust% = -1: custin$ = parm$: updwn% = 13

start:
	CALL setup("STAND ALONE INVOICE (" + DB.OR.CR$ + ")")
	btm$ = " F1-Exit.                       F6-Browse                     F10-Order Details "
	COLOR 8, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
	pass.getcust% = 0: custin$ = "ZZZZZ": updwn% = 13

getcust:
	'// Find the end of the audit file
	IF invnum# > 0 THEN
		LOCATE 24, 14: COLOR 7, 0: PRINT USING "µAudit:##,#### ÆÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍÍµInv:############Æ"; invnumrec%; invnum#; : COLOR 2, 0
		END IF
	LOCATE 2, 22
	COLOR 7, 0: PRINT "ÍÍµ";
	COLOR 2, 0: PRINT "Enter Customer......>"; custin$ + "     ";
	COLOR 7, 0: LOCATE 2, 51: PRINT "ÆÍÍÍÍÍ": COLOR 2, 0
	IF NOT pass.getcust% THEN
		LOCATE 2, 46
		CALL inpnew(custin$, 205!, updwn%, "13,59,64-65,68,72,80" + ALT$): GOSUB ALT
		IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
		IF updwn% = 65 THEN CLOSE : bpgm$ = "ASBLD02": CALL exitpgm(bpgm$): CHAIN bpgm$'Examine detail file
		END IF
	pass.getcust% = 0

	IF updwn% = 64 THEN
		npgm$ = "dsinv02d"
		CALL exitpgm(npgm$)
		CLOSE
		CHAIN npgm$
		END IF
	IF updwn% = 13 THEN
			IF VAL(custin$) > 0 THEN
				sno% = VAL(custin$)
				IF sno% < 1 OR sno% > maxsup% THEN sno% = 1
				GET #ch%, sno%, cus
				custin$ = cus.search$ + cus.stype$
				END IF
			keyin$ = custin$
			CALL searchindex(keyin$, chi%, found%)
			IF found% THEN sno% = CVI(supx.wrrn$): CALL sndmsg("")
			IF NOT found% THEN
					msg$ = "          Customer not found.  Use the Up/Down arrows to locate."
					CALL sndmsg(msg$)
					sno% = CVI(supx.wrrn$): custin$ = supx.wcde$
					SOUND 250, 1
					END IF
			END IF

	IF updwn% = 72 THEN 'Up arrow
		p% = LOC(chi%): p% = p% - 1: IF p% < 1 THEN p% = 1
		GET #chi%, p%, supx
		custin$ = supx.wcde$: updwn% = 13
		keyin$ = custin$
		CALL searchindex(keyin$, chi%, found%)
		IF found% THEN sno% = CVI(supx.wrrn$)
		found% = 0
		END IF

	IF updwn% = 80 THEN 'Down arrow
		p% = LOC(chi%): p% = p% + 1
		GET #chi%, p%, supx
		custin$ = supx.wcde$: updwn% = 13
		keyin$ = custin$
		CALL searchindex(keyin$, chi%, found%)
		IF found% THEN sno% = CVI(supx.wrrn$)
		found% = 0
		END IF


	IF sno% < 1 OR sno% > maxcus% THEN GOTO getcust
		CALL dsply(sno%)
		thissup$ = cus.search$ + cus.stype$

		IF clr% = 3 THEN CALL setup("STAND ALONE INVOICE (" + DB.OR.CR$ + ")")
		COLOR 8, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
		CALL dsply(sno%)

	IF clr% = 2 THEN CALL BOX(2, 3, 79, 21, 7, 0, 0): clr% = 0
	IF emsg$ <> "" THEN COLOR 14, 0: LOCATE 21, 2: PRINT emsg$; CHR$(FNE): COLOR 2: updwn% = 59
	COLOR 2, 0
	IF NOT found% THEN GOTO getcust

getcustdet:
gn1:
	LOCATE 14, 10
	CALL inpnew(hdr$(1), 125!, updwn%, "13,59-60,64,68,73,81" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	IF updwn% = 60 THEN GOTO getcust
	IF updwn% = 68 THEN GOSUB mline: GOTO start
gn2:
	LOCATE 15, 10
	CALL inpnew(hdr$(2), 125!, updwn%, "13,59-60,64,68,73,81" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	IF updwn% = 60 THEN GOTO gn1
	IF updwn% = 68 THEN GOSUB mline: GOTO start
gn3:
	LOCATE 16, 10
	CALL inpnew(hdr$(3), 130!, updwn%, "13,59-60,64,68,73,81" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	IF updwn% = 60 THEN GOTO gn2
	IF updwn% = 68 THEN GOSUB mline: GOTO start
gn4:
	LOCATE 17, 10
	CALL inpnew(hdr$(4), 130!, updwn%, "13,59-60,64,68,73,81" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	IF updwn% = 60 THEN GOTO gn3
	IF updwn% = 68 THEN GOSUB mline: GOTO start

gn5:
	LOCATE 14, 50
	CALL inpnew(hdr$(5), 125!, updwn%, "13,59-60,64,68,73,81" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	IF updwn% = 60 THEN GOTO getcust
	IF updwn% = 68 THEN GOSUB mline: GOTO start
gn6:
	LOCATE 15, 50
	CALL inpnew(hdr$(6), 125!, updwn%, "13,59-60,64,68,73,81" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	IF updwn% = 60 THEN GOTO gn1
	IF updwn% = 68 THEN GOSUB mline: GOTO start
gn7:
	LOCATE 16, 50
	CALL inpnew(hdr$(7), 130!, updwn%, "13,59-60,64,68,73,81" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	IF updwn% = 60 THEN GOTO gn2
	IF updwn% = 68 THEN GOSUB mline: GOTO start
gn8:
	LOCATE 17, 50
	CALL inpnew(hdr$(8), 130!, updwn%, "13,59-60,64,68,73,81" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	IF updwn% = 60 THEN GOTO gn3
	IF updwn% = 68 THEN GOSUB mline: GOTO start

	GOTO getcustdet
'/////////////////////////////////////////////////////////
'>>>>> M A I N L I N E    O F    E D I T   S E C T I O N
'/////////////////////////////////////////////////////////
mline:
	ordhed.hdate$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
	ordhed.hreford$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
	ordhed.htaxe$ = SPACE$(12)
det:
	mode$ = "ord"
	GOSUB detail
	opt$ = " "
	IF Cash% THEN opt$ = "5"
	IF tot.ext = 0 THEN opt$ = "6"
exitmenu:
	DO
	SELECT CASE skipexit%
	CASE -1: opt$ = "": updwn% = 60
	CASE ELSE
		CALL BOX(17, 5, 63, 19, 6, 9, 1)
		COLOR 4, 1
		LOCATE 6, 28: PRINT "  E X I T    M E N U "
		COLOR 7, 1
		LOCATE , 28: PRINT "1....Exit without update."
		LOCATE , 28: PRINT ""
		LOCATE , 28: PRINT "3....Invoice."
		LOCATE , 28: PRINT ""
		LOCATE , 28: PRINT ""
		LOCATE , 28: PRINT "6....Overtype price."
		LOCATE , 28: PRINT "7....Override discount."
		LOCATE , 28: PRINT "8....Enter message lines."
		LOCATE , 28: PRINT "9....Print a credit note."
		COLOR 14
		LOCATE , 22: PRINT cond.red$
		COLOR 2
		LOCATE , 28: PRINT "Option...> "
		COLOR 6, 1
		LOCATE , 20: PRINT "F1-Exit.         F2-Cont         F4-Cancel."
		LOCATE 17, 38: COLOR 2, 0
		CALL inpnew(opt$, 1!, updwn%, "13,59-60,62,68")
	END SELECT
	skipexit% = 0

	opt% = VAL(opt$)
	IF updwn% = 13 AND opt% = 0 THEN updwn% = 59
	IF updwn% = 59 THEN opt% = 0
	IF updwn% = 60 THEN opt% = -1'F2 - Save & Cont
	IF updwn% = 62 THEN opt% = -2'F4 - Cancel the order

	IF opt% = 2 OR opt% = 4 OR opt% = 5 THEN opt% = -99


	LOOP UNTIL opt% >= -2 AND opt% <= 9

	sav% = 0
	doc.type$ = "INVOICE"
	formtype$ = "*PRE.PRINTED.1"


	IF opt% = -2 THEN mode$ = "del": sav% = 0
	IF opt% = -1 THEN mode$ = "ord": sav% = -1
	IF opt% = 0 THEN mode$ = "ord": sav% = -1
	IF opt% = 1 THEN mode$ = "nil": sav% = 0
	IF opt% = 2 THEN mode$ = "ord": sav% = -1
	IF opt% = 3 THEN mode$ = "inv": sav% = -1
	IF opt% = 4 THEN mode$ = "b/o": sav% = -1
	IF opt% = 5 THEN mode$ = "inv": sav% = -1: formtype$ = "*PRE.PRINTED.2"
	IF opt% = 6 THEN GOSUB change.price: GOTO exitmenu
	IF opt% = 7 THEN GOSUB change.disc: GOTO exitmenu
	IF opt% = 8 THEN GOSUB message: GOTO exitmenu
	IF opt% = 9 THEN mode$ = "inv": sav% = -1: doc.type$ = "CREDIT "
	IF opt% = 9 AND Cash% THEN mode$ = "inv": sav% = -1: doc.type$ = "CREDIT ": formtype$ = "*PRE.PRINTED.2"

	IF tot.allup! = 0 THEN doc.type$ = "DOCKET "

	'/// Print and exit or delete ///
	IF opt% = -1 THEN GOTO mline
	IF updwn% <> 59 THEN
		'>>> Supliers from 1 to MAXTYPES are for CASH ONLY <<<
		'>>> Get the description from the screen     <<<
		IF mode$ = "inv" OR mode$ = "b/o" THEN
			IF Cash% THEN
				GOSUB get.name
				IF updwn% = 59 THEN GOTO exitmenu
				END IF
			END IF
		IF mode$ = "inv" THEN GOSUB prtinv
		IF mode$ = "b/o" THEN GOSUB prtinv
		END IF
mlend:
	'>> Change F1 to prevent the real mainline ending the program. <<
	updwn% = 13
	clr% = 3
RETURN
'/////////////////////////////////////////////////////////
'>>>>> CHANGE THE VOLUME ADJUSTMENT
'/////////////////////////////////////////////////////////
change.disc:
		LOCATE 21, 12
		in$ = STR$(discovr!)
		CALL inpnew(in$, 5!, updwn%, "13,59")
		discovr! = VAL(in$)
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ltact.taxable!, tot.dtax!, tot.ext!)
RETURN
'/////////////////////////////////////////////////////////
'>>>>> CHANGE THE TOTAL INVOICE PRICE & CALC DISC
'/////////////////////////////////////////////////////////
change.price:
change.price0:
		LOCATE 22, 72
		in$ = STR$(tot.ext - vdisc! - exdisc!)
                CALL inpnew(in$, 7.2!, updwn%, "13,59")
		in = VAL(in$)
		exdisc! = tot.ext - vdisc! - in!
		CALL ROUND(exdisc, 2.5)
		IF tot.ext > 0 AND exdisc < 0 THEN exdisc = 0: SOUND 250, 1: GOTO change.price0
		IF tot.ext = 0 THEN exdisc = 0 - in
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ltact.taxable!, tot.dtax!, tot.ext!)
RETURN
'/////////////////////////////////////////////////////////
'>>>>> GET THE CASH CUSTOMERS NAME TO WRITE TO THE AUDIT FILE
'/////////////////////////////////////////////////////////
get.name:
		PCOPY 0, 1
		CALL BOX(24, 9, 52, 16, 7, 0, 2)
		LOCATE 10, 28: PRINT "Tender.> "
		LOCATE 11, 28: PRINT "        1.Cash"
		LOCATE 12, 28: PRINT "        2.Cheque"
		LOCATE 13, 28: PRINT "        3.Credit card"
		LOCATE 15, 28: PRINT "        9.Type Desc"


tender:
		tender$ = "1"
                LOCATE 10, 36: CALL inpnew(tender$, 101!, updwn%, "13,59")
		IF updwn% = 59 THEN GOTO xname
		IF tender$ <> "1" AND tender$ <> "2" AND tender$ <> "3" AND tender$ <> "9" GOTO tender

		'>>> Sname <<<
		IF tender$ = "9" THEN
			CALL BOX(3, 17, 78, 21, 7, 0, 2)
			LOCATE 18, 5: PRINT USING "Name...>\                           \"; cus.sname$
			LOCATE , 5: PRINT USING "Addr...>\                  \         "; cus.saddr$
			LOCATE , 5: PRINT USING "Subu... \                  \Code\   \"; cus.suburb$; cus.spcode$

			a$ = cus.sname$
			LOCATE 18, 13: CALL inpnew(a$, 127!, updwn%, "13,59,60")
			LSET cus.sname$ = a$
			IF updwn% = 59 THEN GOTO xname
			IF updwn% = 60 THEN GOTO tender
			GOTO tender
			END IF

xname:
		PCOPY 1, 0
RETURN
'/////////////////////////////////////////////////////////
'>>>>> ADD A MESSAGE TO THE INVOICE
'/////////////////////////////////////////////////////////
message:
		PCOPY 0, 1
		CALL BOX(12, 16, 71, 19, 7, 0, 2)
		LOCATE 17, 16: PRINT "Message..>"; invmsg2$
		LOCATE , 16: PRINT "         >"; invmsg3$
cmsg1:
		LOCATE 17, 26: CALL inpnew(invmsg2$, 142!, updwn%, "13,59,60")
		IF updwn% = 59 THEN GOTO xmessage
		IF updwn% = 60 THEN GOTO xmessage
cmsg2:
		LOCATE 18, 26: CALL inpnew(invmsg3$, 142!, updwn%, "13,59,60")
		IF updwn% = 59 THEN GOTO xmessage
		IF updwn% = 60 THEN GOTO cmsg1
		GOTO xmessage
xmessage:
		PCOPY 1, 0
RETURN
	'////////////////////////////////////////////////////////////
	'/////    I N V O I C E   D E T A I L S
	'////////////////////////////////////////////////////////////
detail:
	CALL setup("I N V O I C E   E N T R Y")
	btma$ = "F1-Save/Print.    F5-Prices     F6-Browse "
	COLOR 8, 3: LOCATE 25, 1: PRINT btma$;
	CALL add.up.order(tot.ltact!, tot.ord!, tot.ltact.taxable!, tot.dtax!, tot.ext!)

	s.elem% = 1'Start at element number 1.
	scrn.pag% = 1
	l% = 1
detail.a:
	IF updwn% = 73 THEN l% = s.elem%'page up
	IF updwn% = 81 THEN l% = s.elem%'page down
	e.elem% = s.elem% + 14
	COLOR 7, 0: LOCATE 2, 2: PRINT "µ": LOCATE 2, 79: PRINT "Æ"
	COLOR 2, 0:
	LOCATE 2, 3: PRINT USING " Order:####"; hord%;
	a$ = "  " + cus.sname$ + " " + cus.scont$ + " " + cus.search$ + cus.stype$ + "  "
	COLOR 2
	PRINT a$
	COLOR 2

	IF tax.in$ = "Y" THEN
		LOCATE , 2: COLOR 6, 0: PRINT "Qty. Size   No.  Description                           Price    I.Tax    Value"
	ELSE
		LOCATE , 2: COLOR 6, 0: PRINT "Qty. Size   No.  Description                           Price    +Tax    Value"
	END IF


	COLOR 2
	LOCATE , 2: COLOR 2, 0: PRINT "ÄÄÄÄÂÄÄÄÄÄÂÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄ"
	LOCATE , 2: COLOR 10: PRINT USING "p #"; scrn.pag%: COLOR 2
	sav.l% = l%
	FOR l% = s.elem% TO e.elem%
			ditem% = VAL(in$(l%, 4))
			ordqty% = VAL(in$(l%, 1)): intqty% = 0
			IF ditem% > 0 AND ordqty% > 0 THEN
				CALL load.line(l%, ditem%, ordqty%, invqty%, price!)
				END IF
		CALL dsply.line(l%, s.elem%)
		NEXT
	l% = sav.l%
	LOCATE , 2: COLOR 2, 0: PRINT "ÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄ"
	'/////////////////////////////////////
	'>>>> Get line entries for the invoice
	'/////////////////////////////////////
	updwn% = 0
	sav.scrn.pag% = scrn.pag%
	DO WHILE updwn% <> 59 AND sav.scrn.pag% = scrn.pag%
		ln% = (l% - s.elem%) MOD 15 + 1: ln% = ln% + 4'+4 Lines from the top of the screen
		GOSUB chglin
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
'///////////////////////////////////////////////////////////////////////
'///// Change an invoice entry line
'///////////////////////////////////////////////////////////////////////
chglin:
	ctl% = 1: chg = 0: maxctl% = 7
	DO WHILE NOT ctl%
		'Edit
		IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
		ON ctl% GOSUB cf1, cf2, cf3, cf4, cf5, cf6, cf7
		' Pgm ctl processing
		ctl% = ctl% + 1
		'Mimick F1 if enter is pressed on a blank line
		'IF ctl% = 2 AND updwn% = 13 AND VAL(in$(l%, 1)) = 0 AND VAL(in$(l%, 4)) = 0 THEN
		'    ctl% = ctl% - 1'This stays there
		'    END IF
		IF ctl% = 6 AND updwn% = 13 AND VAL(in$(l%, 1)) = 0 AND VAL(in$(l%, 4)) = 0 THEN
			EXIT DO
			END IF
		IF ctl% = 2 AND updwn% = 13 AND VAL(in$(l%, 1)) = 0 AND VAL(in$(l%, 4)) = 0 THEN
			ctl% = 5
			END IF

		IF updwn% = 60 THEN ctl% = ctl% - 2     'F2 - Back one
		IF updwn% = 72 THEN ctl% = -1           'Up Arrow
		IF updwn% = 80 THEN ctl% = -1           'Down Arrow
		IF updwn% = 73 THEN ctl% = -1           'Pg Up
		IF updwn% = 81 THEN ctl% = -1           'Pg Down
		IF updwn% = 60 AND ctl% = 0 THEN ctl% = -1'F2 at first
		IF updwn% = 59 THEN ctl% = -1           'F1 Save
		IF ctl% > maxctl% THEN ctl% = -1        'End of line
		LOOP
RETURN
'///////////////////////////////////////////////////////////////////////
'///// Detail entry subroutines
'///////////////////////////////////////////////////////////////////////
	'>>>>> QTY <<<<<<<
cf1:
	IF ext.has.changed% THEN
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ltact.taxable!, tot.dtax!, tot.ext!)
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
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ltact.taxable!, tot.dtax!, tot.ext!)
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
		PCOPY 1, 0
		GOTO cf1
		END IF

	IF updwn% = 68 THEN
		CALL get.order.vs(hord%, updwn%)
		updwn% = 59: skipexit% = -1 'Emulate save, update and continue
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
	CALL inpnew(in$(l%, 2), 103!, updwn%, "13,59,60,62")
	in$(l%, 2) = UCASE$(in$(l%, 2))
RETURN
	'>>>>> UNITS <<<<<<<
cf3: LOCATE ln%, c%(3)
	CALL inpnew(in$(l%, 3), 102!, updwn%, "13,59,60,62")
RETURN
	'>>>>> STOCK NUMBER <<<<<<<
cf4: LOCATE ln%, c%(4)
	IF frombrowse% THEN in$(l%, 4) = STR$(rec%): frombrowse% = 0
	IF VAL(in$(l%, 2)) = 0 THEN
		CALL inpnew(in$(l%, 4), 4!, updwn%, "13,59,60")
		END IF

	ditem% = VAL(in$(l%, 4))
	IF ditem% < 1 OR ditem% > maxacc% THEN ditem% = 0
	IF ditem% <> oldrec% THEN
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
		CALL inpnew(in$(l%, 5), 135!, updwn%, "13,59,60")
xcf5:
RETURN
	'>>>>> PRICE <<<<<<<
cf6: LOCATE ln%, c%(6) - 2
        CALL inpnew(in$(l%, 6), 7.2!, updwn%, "13,59,60")
	CALL dsply.line(l%, s.elem%)
RETURN
	'>>>>> TAX <<<<<<< Calulated in the extention routine
cf7:
RETURN
'////////////////////////////////////////////////////////////
'/////    P R I N T   I N V O I C E
'////////////////////////////////////////////////////////////
prtinv:
	cashonly$ = "M": auditname$ = auditfile$(naudit%)
	GOSUB OPEN.AUDIT '#8
	'>>> Find highest document number of the same type <<<
	invnum# = 0
	'// Find the end of the audit file
	adlast% = LOF(8) / 92
	startinvnum% = adlast%
	IF chginv# > 0 THEN startinvnum% = chginv.rrn%
	IF startinvnum% >= 1 THEN
		GET #8, startinvnum%, audit
		invnum# = VAL(audit.addocnum$)
		invnumrec% = adlast%
		END IF
	SELECT CASE doc.type$
	CASE "INVOICE": test$ = "DI": IF chi% = 45 THEN test$ = "CI"
	CASE "CREDIT ": test$ = "DC": IF chi% = 45 THEN test$ = "CC"
	CASE "DOCKET ": test$ = "DI":  IF chi% = 45 THEN test$ = "CI"
	CASE ELSE: test$ = "DI": IF chi% = 45 THEN test$ = "CI"
	END SELECT

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
	'>>>>>>>> This section backs out the value on the audit file <<<<<<<<
	IF chginv# > 0 THEN
		GET #8, chginv.rrn%, audit
		invnum# = chginv# - 1
		upd.audit% = chginv.rrn%
		chginv# = 0: chginv.rrn% = 0'To prevent it happening next update!
		'>>> BACK OUT THE OLD AUDIT RECORD <<<
		cha% = 8'Channel of audit file
		chw% = 43'Channel of cus file
		adtax! = audit.adtax!
		advalue = audit.advalue
		advalue = 0 - advalue
		adtax! = 0 - adtax!
		LSET audit.adsname$ = cus.sname$
		LSET audit.adcust$ = cus.search$ + cus.stype$
		audit.adtax! = adtax!
		audit.advalue = advalue
		IF NOT Cash% THEN GET #chw%, sno%
		CALL upd.who(cha%, chw%, upd.audit%)
		END IF
	 '>>>> Set up statics for raw material entry
	 LSET audit.adsname$ = cus.sname$
	 LSET audit.addate$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
	 '??
	 SELECT CASE doc.type$
	 CASE "INVOICE"
		LSET audit.adtype$ = "DI"
		LSET audit.adtext$ = "DELIVERY INVOICE."
		IF chi% = 45 THEN audit.adtype$ = "CI": LSET audit.adtext$ = "PICKUP INVOICE."

		IF Cash% THEN
			SELECT CASE tender$
			CASE "1": LSET audit.adtext$ = "Cash"
			CASE "2": LSET audit.adtext$ = "Cheque"
			CASE "3": LSET audit.adtext$ = "Credit Card"
			CASE ELSE
			END SELECT
			END IF
	CASE "CREDIT "
		LSET audit.adtype$ = "DC"
		LSET audit.adtext$ = "DELIVERY CREDIT"
		IF Cash% THEN LSET audit.adtext$ = "Credit return (Cash)"
		IF chi% = 45 THEN audit.adtype$ = "CC": LSET audit.adtext$ = "PICKUP CREDIT"
	CASE "DOCKET "
		LSET audit.adtype$ = "DI"
		LSET audit.adtext$ = "DELIVERY DOCKET"
		IF chi% = 45 THEN audit.adtype$ = "CI"
	CASE ELSE
	END SELECT

	 LSET audit.adcust$ = cus.search$ + cus.stype$
	 LSET audit.addate$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
	 '??
	 audit.advalue = 0 'set Later
	 audit.adglacc! = 170!
	 LSET audit.adpaid$ = " "
	'>- The invoice for an order uses the detail rrn off the header file
	'>  2nd and subsequent invoices use the next rrn off the detail file.
	inv.lt.printed = 0
	inv.lt.to.print = lt.inv
inv.per.page:
	invnum# = invnum# + 1
	invnum$ = MID$(STR$(invnum#), 2)
	LSET audit.addocnum$ = invnum$
	'>>>---- Open an invoice copy file
	a$ = STR$(invnum#)
	MID$(a$, 1, 1) = "0"
	a$ = "00000000" + a$
	b$ = RIGHT$(a$, 8)

	SELECT CASE doc.type$
	CASE "INVOICE": b$ = b$ + ".INS": IF chi% = 45 THEN MID$(b$, LEN(b$) - 2, 3) = "DDS"
	CASE "CREDIT ": b$ = b$ + ".CRS": IF chi% = 45 THEN MID$(b$, LEN(b$) - 2, 3) = "CDS"
	CASE "DOCKET ": b$ = b$ + ".DKS"
	CASE ELSE
	END SELECT

	OPEN b$ FOR OUTPUT AS #98
	tot.qty = 0
	tot.dtax = 0
	tot.ext = 0
	tot.ltinv = 0
	tot.taxvol = 0
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
	ldisc! = vdisc!
	more.on.pickslip% = 0
	IF formtype$ = "*PRE.PRINTED.1" THEN GOSUB actual.print.1
	'////////////////////////////////////////////////////////////
	'>>>>>>>>>>>> Write to audit file record <<<<<<<<<<<<<<<<<<<<
	'////////////////////////////////////////////////////////////
	cha% = 8'Channel of audit file
	chw% = 43'Channel of cus file
	audit.advalue = advalue
	audit.adtax! = adtax!
	GET #chw%, sno%, cus
	CALL upd.who(cha%, chw%, upd.audit%)
	'>- If there is more than a page on an order go and pick the details
	'>- up. Remember the rrn from the detail file.
	IF more.on.pickslip% THEN
		start.det.rec% = orddet.drrn%
		GOTO inv.per.page
		END IF

	'>>- Only open the audit file when needed -<<
	CLOSE #8
RETURN
'////////////////////////////////////////////////////////////
'/////    T H E   F I R S T  F O R M   T Y P E
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
	'PRINT #98, CHR$(27); "j"; CHR$(15); '>> Half a line jump
	PRINT #98, " "
	PRINT #98, " " '                             ÜÜÜÜÜÜÜÜÜÜÜÜÜÜ                            " 'chr 220
	PRINT #98, " "'                              ßßßßßßßßßßßßßß           A.C.N 005 686 822" 'chr 223
	PRINT #98, CHR$(15)'Condensed print

	SELECT CASE doc.type$
	CASE "INVOICE"
	PRINT #98, "  Invoiced to:                                                              Delivery:"
	PRINT #98, " "
	CASE "CREDIT "
	PRINT #98, "  Credited to:                                                              Delivery:"
	PRINT #98, " "
	CASE ELSE
	PRINT #98, "  Despatch to:                                                              Delivery:"
	PRINT #98, " "
	END SELECT

	PRINT #98, USING "          &\                            \&                   \                            \     "; wide$; hdr$(1); rwide$; hdr$(5)
	PRINT #98, USING "          &\                            \&                   \                            \     "; wide$; hdr$(2); rwide$; hdr$(6)
	PRINT #98, USING "          &\                            \&                   \                            \              "; wide$; hdr$(3); rwide$; hdr$(7)
	PRINT #98, USING "          &\                            \&                   \                            \     "; wide$; SPACE$(1); rwide$; hdr$(8)
	PRINT #98, CHR$(27); "J"; CHR$(15); '>> Half a line jump
	PRINT #98, " "
	PRINT #98, " "
	PRINT #98, USING "                                                                                                                  \       \   "; invnum$
	PRINT #98, USING "!                                               !!!\     \!!!"; CHR$(18); CHR$(14); CHR$(27); "E"; doc.type$; CHR$(15); CHR$(27); "F"
	PRINT #98, USING "   \    \ - ###     \       \    \           \    \           \                                                    \       \   "; cus.search$ + cus.stype$; sno%; FNDYY$(ordhed.hdate$); ordhed.hreford$; ordhed.htaxe$; MID$(DATE$,  _
4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
	PRINT #98, " "
	PRINT #98, " "
	PRINT #98, " "
	PRINT #98, " "
	'>>>> Read throught the linked list of the details file <<<<
	l% = 0: lin% = 0
	DO WHILE lin% < 15 AND l% < 45
		l% = l% + 1
		'>>> Decode the detail file <<<
		dord% = VAL(in$(l%, 1))
		ditem% = VAL(in$(l%, 4))
		dordq% = VAL(in$(l%, 1))
		dinvq% = VAL(in$(l%, 1))
		dlinvq% = VAL(in$(l%, 1))
		desc1$ = MID$(in$(l%, 5), 1, 25)
		desc2$ = MID$(in$(l%, 5), 26)
		dprice! = VAL(in$(l%, 6))
		dtax! = 0
		ext! = (dprice + dtax) * dlinvq%
		tot.ext = tot.ext + ext!
		tot.dtax = tot.dtax + (dtax! * dlinvq%)

		IF ditem% < 1 OR ditem% > maxacc% OR dlinvq% = 0 THEN
			IF MID$(in$(l%, 5), 1, 1) <= " " THEN
				'PRINT #98, USING " &"; " "
				ELSE
				IF dord% <> 0 THEN PRINT #98, USING " ####   \  \\ \   ####   \                       \\        \                               ####.##    #####.##     $$,###.##  "; dlinvq%; in$(l%, 2); in$(l%, 3); ditem%; desc1$; desc2$; dprice; dtax; ext!
				 IF dord% = 0 THEN PRINT #98, USING "                         \                       \\        \                                                                  "; desc1$; desc2$

				lin% = lin% + 1
				END IF
		ELSE
			GET #3, ditem%, acstk
			size! = VAL(acstk.size$)
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
				tot.taxvol = tot.taxvol + ltinv'wHAT
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
			PRINT #98, USING " ####   \  \\ \   ####   \                        \\        \                              ####.##    #####.##     $$,###.##  "; dlinvq%; acstk.size$; acstk.unit$; ditem%; acstk.desc1$; acstk.desc2$; dprice; dtax; ext!
			lin% = lin% + 1
			END IF
		'>>> Bottom of read equal loop <<<
		LOOP
	FOR i% = lin% TO 14  '15 lines fit on the invoice
		PRINT #98, "                                                                                                                              "
		NEXT

	ldisc = tot.ltinv * rate!
	discofftax = tot.taxvol * rate! / 5
	tot.dtax! = tot.dtax - discofftax
	advalue = tot.ext - ldisc - exdisc
	adtax! = tot.dtax
	invmsg1$ = ""
	IF tot.dg200% > 0 THEN invmsg1$ = invmsg1$ + " 200L=" + MID$(STR$(tot.dg200%), 2)
	IF tot.dg60% > 0 THEN invmsg1$ = invmsg1$ + " 60L=" + MID$(STR$(tot.dg60%), 2)
	IF tot.dg20% > 0 THEN invmsg1$ = invmsg1$ + " 20L=" + MID$(STR$(tot.dg20%), 2)
	IF tot.dg10% > 0 THEN invmsg1$ = invmsg1$ + " 10L=" + MID$(STR$(tot.dg10%), 2)
	IF tot.dg4% > 0 THEN invmsg1$ = invmsg1$ + " 4L=" + MID$(STR$(tot.dg4%), 2)
	IF tot.dg2% > 0 THEN invmsg1$ = invmsg1$ + " 2L=" + MID$(STR$(tot.dg2%), 2)
	IF tot.dg1% > 0 THEN invmsg1$ = invmsg1$ + " 1L=" + MID$(STR$(tot.dg1%), 2)
	IF tot.dg850% > 0 THEN invmsg1$ = invmsg1$ + " .85L=" + MID$(STR$(tot.dg850%), 2)
	IF tot.dg500% > 0 THEN invmsg1$ = invmsg1$ + " .5L=" + MID$(STR$(tot.dg500%), 2)
	IF tot.dg300% > 0 THEN invmsg1$ = invmsg1$ + " .3L=" + MID$(STR$(tot.dg300%), 2)
	IF tot.dg250% > 0 THEN invmsg1$ = invmsg1$ + " .25L=" + MID$(STR$(tot.dg250%), 2)
	warn$ = ""
	IF invmsg1$ > "" THEN
		warn$ = SPACE$(26) + "DANGEROUS GOODS - CLASS 3 - ON THIS DELIVERY"
		invmsg1$ = invmsg1$ + "  Total= " + STR$(tot.dglt!) + "lt"
		END IF


	PRINT #98, warn$
	PRINT #98, ""
	IF doc.type$ = "INVOICE" THEN
	PRINT #98, USING "   LT/Ordered ##,###    LT/Invoiced ##,###       Rate/LT #.###      Backorder ##,###         Total    #####.##    $$#,###.##  "; tot.ord; tot.ltinv; rate!; hordq; tot.dtax; tot.ext
	END IF

	IF doc.type$ = "CREDIT " THEN
	PRINT #98, USING "   LT/Ordered ##,###    LT/Credited ##,###       Rate/LT #.###      Backorder ##,###         Total    #####.##    $$#,###.##  "; tot.ord; tot.ltinv; rate!; hordq; tot.dtax; tot.ext
	END IF

	IF doc.type$ = "DOCKET " THEN
	PRINT #98, USING "                                                                                             Total    #####.##    $$#,###.##  "; tot.dtax; tot.ext
	END IF


	PRINT #98, USING "  &\                                        \&   V/discount   #,###.##      #,###.##  "; wide$; "      "; rwide$; 0; ldisc!
	PRINT #98, USING "   \                                                                                \    Sales tax    #####.##   $$##,###.##  "; invmsg1$; 0; 0
	IF exdisc = 0 THEN PRINT #98, USING "  &\                                        \& "; wide$; invmsg2$; rwide$
	IF exdisc > 0 THEN PRINT #98, USING "  &\                                        \&   Discount                 $$#,###.##  "; wide$; invmsg3$; rwide$; exdisc
	PRINT #98, USING "  &\                                        \& "; wide$; invmsg3$; rwide$
	IF doc.type$ = "INVOICE" THEN
	PRINT #98, USING "  &\                                        \&   &AMOUNT DUE&    $$##,###.##  "; wide$; invmsg4$; rwide$; heavy$; rheavy$; advalue
	END IF

	IF doc.type$ = "CREDIT " THEN
	PRINT #98, USING "  &\                                        \&   &  CREDIT  &    $$##,###.##  "; wide$; invmsg4$; rwide$; heavy$; rheavy$; advalue
	END IF

	IF doc.type$ = "DOCKET " THEN
	PRINT #98, USING "  &\                                        \&   &  DOCKET  &    $$##,###.##  "; wide$; invmsg4$; rwide$; heavy$; rheavy$; advalue
	END IF

	' PRINT #98, CHR$(27); "j"; CHR$(15); '>> Half a line jump BACKWARDS. ie small "j"
	PRINT #98, CHR$(18); CHR$(12);
	CLOSE #98
	exdisc = 0
	shella$ = "COPY " + b$ + " LPT2: > NUL"
	X! = FRE(-1)
	IF X! > 55000 THEN
		SHELL shella$
		END IF
	'>- If the pointer on the detail file is not zero
	'   the order has more details, But these details
	'   might all be backordered.
	inv.lt.printed = inv.lt.printed + tot.ltinv
	IF dnext% > 0 AND inv.lt.printed < hinvq THEN
		more.on.pickslip% = -1
		END IF
RETURN

SUB add.up.order (tot.ltact!, tot.ord!, tot.ltact.taxable!, tot.dtax!, tot.ext!) STATIC
'/////////////////////////////////////////////////////////////////////////////
'>>>>> Add up the suple order
'/////////////////////////////////////////////////////////////////////////////
add.up.order:
	'>>> Add up total litres and calc discount $ <<<
	tot.ltact = 0
	tot.ltact.taxable = 0
	tot.dtax = 0
	tot.ext = 0

	FOR i% = 1 TO maxlines%
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
		NEXT


	'>>> Calculate the volume discount <<<<
	a = tot.ord!
	IF cus.stype$ = "W" THEN a = 0
	CALL ROUND(a, .5)
	vdisc! = 0: rate! = 0
	SELECT CASE a'Total ordered + header volume adjustment
	CASE 100 TO 199: vdisc! = tot.ltact * .05: rate! = .05
	CASE 200 TO 399: vdisc! = tot.ltact * .075: rate! = .075
	CASE 400 TO 999: vdisc! = tot.ltact * .1: rate! = .1
	CASE IS >= 1000: vdisc! = tot.ltact * .125: rate! = .125
	CASE ELSE: vdisc! = 0: rate! = 0
	END SELECT

	discofftax = tot.ltact.taxable * rate! / 5


	'>>> Round the very bottom price for cash items
	Cash% = 0
	IF sno% >= 1 AND sno% <= maxtypes% THEN Cash% = -1
	IF rec50% = 0 OR rec50% = 2 THEN Cash% = -1
	IF Cash% THEN
		IF exdisc < .1 THEN exdisc = 0
		vbp1 = tot.ext - vdisc! - exdisc
		vbp2 = tot.ext - vdisc! - exdisc
		CALL ROUND(vbp1, 1.5)
		CALL ROUND(vbp2, 2.5)
		adj10cents! = vbp2 - vbp1
		IF adj10cents! < 0 THEN adj10cents! = adj10cents! + .1
		CALL ROUND(adj10cents!, 2.5)
		exdisc = exdisc + adj10cents!
		END IF


	'>>> Print out bottom line of the invoice <<<<
	tot.allup! = tot.ext - vdisc! - exdisc
	COLOR 2, 0
	LOCATE 21, 2: PRINT USING "Ordered :###,###                                          $$####.##$$######.##"; tot.ord!; tot.dtax; tot.ext
	LOCATE 22, 2: PRINT USING "Actual  :###,###                              Tax discount$$####.## $$#####.##"; tot.ltact; discofftax; vdisc

	COLOR 7, 0
	LOCATE 24, 69: PRINT USING "µ$$#####.##º"; tot.allup!; : COLOR 2, 0
	COLOR 10, 0:
	LOCATE 24, 70: PRINT USING "$$#####.##"; tot.allup!; : COLOR 2, 0
	COLOR 2, 0
	IF exdisc <> 0 THEN
		LOCATE 22, 29: PRINT USING "Price adj$$###.##"; exdisc
		END IF

	ext.has.changed% = 0
	LOCATE 1, 1'??
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
		in$(l%, 5) = acstk.desc1$ + " " + acstk.desc2$

		LOCATE ln%, c%(6)
		in$(l%, 6) = STR$(acstk.purcost!)
                CALL inpnew(in$(l%, 6), 5.2!, updwn%, "13")
		price! = VAL(in$(l%, 6))
		END IF
	'>---------------------------------------------------------------
	old.ext! = VAL(in$(l%, 8))
	ext! = qty! * (price! + tax!)
	in$(l%, 8) = STR$(ext!)
	IF old.ext! <> ext! THEN ext.has.changed% = -1

END SUB

SUB dsply (sno%) STATIC
'/////////////////////////////////////////////////////
'>>>>> Get record and display
'/////////////////////////////////////////////////////
dsply:
	IF sno% < 1 OR sno% > maxcus% THEN GOTO x.dsply
	GET #ch%, sno%, cus
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
	x0% = 5
	COLOR 2, 0
	LOCATE 3, 3: PRINT USING " &  &  &    &  "; cus.sname$; cus.scont$; cus.sphone$; cus.search$; cus.stype$
	COLOR 7: LOCATE 4, 2: PRINT "ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ": COLOR 2
	LOCATE 5, 2: PRINT USING "Address:\                             \ Deliver:\                            \"; cus.saddr$; PICKUP.pname1$
	LOCATE 6, 2: PRINT USING "        \                  \ \    \             \                            \"; cus.suburb$; cus.spcode$; PICKUP.pname2$
	COLOR 6
	SELECT CASE daysmax%
	CASE 1: LOCATE 7, x0%: PRINT USING "Terms:## day for ##% discount. "; daysmax%; sterms
	CASE ELSE: LOCATE 7, x0%: PRINT USING "Terms:## days for ##% discount."; daysmax%; sterms
	END SELECT
	COLOR 2
	LOCATE 7, 50: PRINT USING "\                            \"; PICKUP.pname3$

	COLOR 6
	LOCATE , x0%: PRINT "90 Days.     60 Days.     30 Days.     Current.       Total.     C/Limit."
	COLOR 2
	LOCATE , 2: PRINT USING " ###,###.##   ###,###.##   ###,###.##   ###,###.## #,###,###.## "; s90; s60; s30; scur; s90 + s60 + s30 + scur

	IF climit! < 1 THEN COLOR 14
	LOCATE 9, 67: PRINT funclimit(climit!)
	COLOR 2

	COLOR 7: LOCATE , 2: PRINT "ÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ": COLOR 2
	CALL BOX(2, 12, 79, 21, 7, 0, 0)
	LOCATE 11, 20: PRINT "Address details to be used for docket"

	COLOR 6, 0
	LOCATE 13, 2: PRINT USING "        Customer address...............         Delivery Address.............!"; ""
	COLOR 2, 0
	LOCATE 14, 2: PRINT USING "Address>\                             \ Deliver>\                           \"; hdr$(1); hdr$(5)
	LOCATE 15, 2: PRINT USING "       >\                             \        >\                           \"; hdr$(2); hdr$(6)
	LOCATE 16, 2: PRINT USING "       >\                             \        >\                           \"; hdr$(3); hdr$(7)
	LOCATE 17, 2: PRINT USING "       >\                             \        >\                           \"; hdr$(4); hdr$(8)

	hdr$(1) = cus.sname$: hdr$(5) = PICKUP.pname1$
	hdr$(2) = cus.saddr$: hdr$(6) = PICKUP.pname2$
	hdr$(3) = cus.suburb$ + cus.spcode$: hdr$(7) = PICKUP.pname3$
	hdr$(4) = SPACE$(26): hdr$(8) = PICKUP.pname4$



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
			PRINT USING "    ³     ³    ³\                                  \³       ³       ³         "; in$(l%, 5)
			ELSE
			qty% = VAL(in$(l%, 1))
			LSET acstk.size$ = in$(l%, 2)
			LSET acstk.unit$ = in$(l%, 3)
			ano% = VAL(in$(l%, 4))
			LSET acstk.desc1$ = in$(l%, 5)
			LSET acstk.desc2$ = MID$(in$(l%, 5), LEN(acstk.desc1$) + 1, 10)
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
			a$ = "³" + acstk.size$ + acstk.unit$ + "³"
			b$ = "³" + acstk.desc1$ + acstk.desc2$ + " " + "³"
			c$ = "³"
			LOCATE ln%, 2: PRINT USING "####"; qty%
			LOCATE ln%, 6: PRINT a$;
			LOCATE ln%, 13: PRINT USING "####"; ano%
			LOCATE ln%, 17: PRINT b$;
			LOCATE ln%, 55: PRINT USING "####.##"; price!;
			LOCATE ln%, 62: PRINT c$;
			IF tax.in$ = "Y" THEN
				COLOR 13
				ELSE
				COLOR 14
				END IF
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

SUB get.order.vs (hord%, updwn%)
		IF hord% > 0 AND hord% < maxord% THEN GET #48, hord%, ordhed
		' IF cash% THEN GOTO tx99
		'>>>>> Get the tax exempt number and the tax order number <<<<<
		LOCATE 21, 2: PRINT SPACE$(78)
		LOCATE 22, 2: PRINT SPACE$(78)
		LOCATE 21, 10: PRINT USING "Order number..>\          \   Tax exempt number..>\          \"; ordhed.hreford$; ordhed.htaxe$

		'/// Get their referance order number ////
TX1:
		a$ = ordhed.hreford$
		LOCATE 22, 10: COLOR 10, 0: PRINT "Blanket orders must start B01-B12. (Number denotes month)": COLOR 2, 0
		LOCATE 21, 25: CALL inpnew(a$, 112!, updwn%, "13,59-60")
		LOCATE 22, 10: COLOR 6, 0: PRINT "                                                          ": COLOR 2, 0
		IF updwn% = 59 THEN GOTO x.get.order.vs
		IF updwn% = 60 THEN GOTO x.get.order.vs
		LSET ordhed.hreford$ = a$
		IF ordhed.hreford$ = SPACE$(12) THEN
			LSET ordhed.hreford$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
			LSET ordhed.htaxe$ = SPACE$(99)
			GOTO TX1
			GOTO x.get.order.vs
			END IF
		'//// Get the tax exempt numnber ////
TX2:
		a$ = ordhed.htaxe$
		LOCATE 21, 60: CALL inpnew(a$, 110!, updwn%, "13,59-60")
		LSET ordhed.htaxe$ = a$
		IF updwn% = 59 THEN GOTO x.get.order.vs
		IF updwn% = 60 THEN GOTO TX1
		'//// Edit the form of the tax exempt number ////
		ok% = -1
		IF MID$(ordhed.htaxe$, 1, 2) <> "VS" AND MID$(ordhed.htaxe$, 1, 2) <> "EE" THEN ok% = 0
		IF MID$(ordhed.htaxe$, 3, 1) <> " " THEN ok% = 0
		IF MID$(ordhed.htaxe$, 4, 1) < "0" OR MID$(ordhed.htaxe$, 4, 1) > "9" THEN ok% = 0
		IF MID$(ordhed.htaxe$, 5, 1) < "0" OR MID$(ordhed.htaxe$, 5, 1) > "9" THEN ok% = 0
		IF MID$(ordhed.htaxe$, 6, 1) < "0" OR MID$(ordhed.htaxe$, 6, 1) > "9" THEN ok% = 0
		IF MID$(ordhed.htaxe$, 7, 1) < "0" OR MID$(ordhed.htaxe$, 7, 1) > "9" THEN ok% = 0
		IF MID$(ordhed.htaxe$, 8, 1) < "0" OR MID$(ordhed.htaxe$, 8, 1) > "9" THEN ok% = 0
		IF MID$(ordhed.htaxe$, 9, 1) < "0" OR MID$(ordhed.htaxe$, 9, 1) > "9" THEN ok% = 0
		IF MID$(ordhed.htaxe$, 10, 1) < "0" OR MID$(ordhed.htaxe$, 10, 1) > "9" THEN ok% = 0
		IF MID$(ordhed.htaxe$, 1, 1) = " " THEN LSET ordhed.htaxe$ = SPACE$(99): ok% = -1
		IF ok% = 0 THEN
			COLOR 14
			LOCATE 22, 60: PRINT "VS Number incorrect."
			COLOR 2
			GOTO TX2
			END IF
x.get.order.vs:
		IF hord% > 0 AND hord% < maxord% THEN PUT #48, hord%, ordhed

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
			LSET acstk.desc1$ = SPACE$(99)
			LSET acstk.desc2$ = SPACE$(99)
			LSET acstk.taxinc$ = SPACE$(99)
			END IF
	'//// All these are TRADEPAINTS ////
	tp% = CVI(acstk.suplr$)
	SELECT CASE tp%
	CASE 282: tp% = -1
	CASE 283: tp% = -1
	CASE 284: tp% = -1
	CASE ELSE: tp% = 0
	END SELECT
	'//// Determine which price to use ////
	IF price! THEN
		IF ditem% <> 1 THEN
			CALL rightprice(price!)
			END IF
		price! = price! - tax!
		IF MID$(ordhed.htaxe$, 1, 2) > "  " THEN tax! = 0
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
		in$(m%, 5) = acstk.desc1$ + " " + acstk.desc2$
		in$(m%, 6) = STR$(price!)' Price is set only the first time in since it cannot change
		in$(m%, 7) = STR$(tax!)
		in$(m%, 8) = STR$(0)
		newdata$ = "Y": CALL cf8(l%, s.elem%, newdata$)
		in$(m%, 9) = acstk.taxinc$
		in$(m%, 10) = STR$(ordqty%)
		in$(m%, 11) = STR$(invqty%)

END SUB

SUB openpslip (opt%) STATIC
ON LOCAL ERROR RESUME NEXT

IF opt% = 2 THEN
	OPEN "LPT1" FOR OUTPUT SHARED AS #99
	END IF

IF opt% <> 2 THEN
	ok% = 0
	DO WHILE ok% = 0
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
	CASE "Y": 'Group Office Price
				price! = acstk.distributor
	CASE "Z": 'Group store price
				price! = acstk.distributor
	CASE "W": 'Best Possible Price
				price! = acstk.wholesalecost
	CASE ELSE: 'All Other Codes Are Retail Price
				price! = acstk.retail
	END SELECT

	'IF acstk.pack% < 1 THEN acstk.pack% = 1
	'price!= price! / pack%


x.rightprice:

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
