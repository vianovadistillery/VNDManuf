DECLARE SUB export (rec%)
DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB PCASE (ch1%, ch2%, DB.OR.CR$)
DECLARE SUB allchgphone (rec%)
DECLARE SUB rmvnull ()
DECLARE SUB TitleList (a$, updwn%)
DECLARE SUB change (rec%, updwn%, chg%, rerec%, DB.OR.CR$, dpage%)
DECLARE SUB dsply (rec%, DB.OR.CR$, dpage%)
DECLARE SUB copy.rec.to (rec%, updwn%, DB.OR.CR$, ask.del$)
DECLARE SUB LogicalDelete (rec%, updwn%)
DECLARE SUB do.delete (rec%, updwn%, ask.del$)
DECLARE SUB trimfile (ok%)
DECLARE SUB setaudit (n%)
DECLARE SUB change.ordsup (init.search$, new.search$)
DECLARE FUNCTION freqcode$ (in$)
DECLARE FUNCTION funclimit$ (climit!)
DECLARE SUB getphone (phone$, updwn%)
DECLARE FUNCTION repcode$ (in$, DB.OR.CR$)
'.dc - Complete
'/////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>         X X W H O 0 1       <<<<<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
DECLARE SUB browse.pickup (a$)
DECLARE SUB browse.idx (first.on.screen%, ch1%, ch2%)
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "DSMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CLOSE
DIM SHARED mm(80), type$(50)
DIM SHARED maxtyp%, maxwho%, chi%, ch%
DIM SHARED change.type$
DIM SHARED auditfile$(15), naudirec%
DIM SHARED bse%
DIM SHARED ea$(6), eb$(6), ec$(6), ed$(6), ee$(6), ef$(6), eg$(6)

CALL setaudit(naudirec%)
null4$ = CHR$(0) + CHR$(0) + CHR$(0) + CHR$(0)

'>>>---------------------------------------------------<<<
'>>> NOTE: This program is for Suppliers and Customers
'>>>       Pass parm of  /CR or /DB /--
'>>>---------------------------------------------------<<<
	DB.OR.CR$ = ENVIRON$("DB.OR.CR$")
	CR% = INSTR(COMMAND$, "/CR")
	D2% = INSTR(COMMAND$, "/--")
	IF CR% > 0 THEN DB.OR.CR$ = "CR"
	IF D2% > 0 THEN DB.OR.CR$ = "--"
	'DB.OR.CR$ = "--"
	'DB.OR.CR$ = "DB"
	'DB.OR.CR$ = "CR"

	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\whox.INC'
	'$INCLUDE: '\tpmanuf\src\who.INC'
	'$INCLUDE: '\tpmanuf\src\cusx.INC'
	'$INCLUDE: '\tpmanuf\src\cus.INC'
	'$INCLUDE: '\tpmanuf\src\supx.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\types.INC'
	'$INCLUDE: '\tpmanuf\src\msmisc.INC'
	'$INCLUDE: '\tpmanuf\src\acmgn.INC'
	'$INCLUDE: '\tpmanuf\src\pickup.INC'
	'$INCLUDE: '\tpmanuf\src\ordhed.INC'

	'$INCLUDE: '\tpmanuf\src\ASAUDIT.INC'
	 cashonly$ = "M": auditname$ = auditfile$(naudirec%)
	 GOSUB OPEN.AUDIT

	SELECT CASE DB.OR.CR$
	CASE "CR": chi% = 45: ch% = 44: apgm$ = "CSMENU"
	CASE "DB": chi% = 23: ch% = 43: apgm$ = "DSMENU"
	CASE "--": chi% = 65: ch% = 64: apgm$ = "FIMENU"
	CASE ELSE
	END SELECT
	 GET #36, 1, msmisc
	 maxtyp% = CVI(msmisc.max6$)

	 SELECT CASE ch%
	 CASE 44: maxwho% = CVI(msmisc.max1$)
	 CASE 43: maxwho% = CVI(msmisc.max7$)
	 CASE 64: maxwho% = CVI(msmisc.max9$)
	 CASE ELSE
	 END SELECT

	'***** Array the margin file
	 GET #1, 1, acmgn: mm(1) = CVS(acmgn.margin$)
	 FOR i% = 2 TO 80: GET #1, , acmgn: mm(i%) = CVS(acmgn.margin$): NEXT
	 CLOSE #1
	'***** Array the types file
	 GET #42, 1, types: type$(1) = types.dftype$
	 FOR i% = 2 TO maxtyp%: GET #42, , types: type$(i%) = types.dftype$: NEXT
	 FOR i% = 1 TO maxtyp%
	IF type$(i%) = " " THEN type$(i%) = "~"
	 NEXT
300
	SELECT CASE DB.OR.CR$
	CASE "DB": CALL setup("UPDATE DEBTORS FILE ")
	CASE "CR": CALL setup("UPDATE CREDITOR FILE ")
	CASE ELSE: CALL setup("UPDATE EXTRA NUMBER FILE "): maxwho% = 2000
	END SELECT
	 COLOR 7, 0: LOCATE 2, 22: PRINT "µ                                Æ": COLOR 2
	 dpage% = 1
	 IF rerec% = 1 THEN updwn% = 68: GOTO 510
	 IF bse% = 1 THEN bse% = 0: rec% = p: CALL dsply(rec%, DB.OR.CR$, dpage%)'*****Display this record if back from browse
480
	 COLOR 0, 3
	 LOCATE 25, 1: PRINT "F1F2 F3-Hist F4.. F5-Tsp. F6.. F7-Idx. F8-Cpy F9-Note F10.. F11-Phone F12-Credit";
	 COLOR 2, 0

	 SELECT CASE DB.OR.CR$
	 CASE "DB": LOCATE 2, 24: PRINT "Enter customer number..>"; CHR$(FNH)
	 CASE "CR": LOCATE 2, 24: PRINT "Enter creditor number..>"; CHR$(FNH)
	 CASE ELSE: LOCATE 2, 24: PRINT "Enter extra number.....>"; CHR$(FNH)
	 END SELECT

	 IF chg% = 1 THEN rec% = p: CALL dsply(rec%, DB.OR.CR$, dpage%): chg% = 0: updwn% = 68
	 LOCATE 2, 49: p$ = ""
	 CALL inpnew(p$, 105!, updwn%, "13,27,59-61,62,63-66,68,72,80,73,81,25" + ALT$): GOSUB ALT
	 p$ = UCASE$(p$)
	 IF updwn% = 133 THEN updwn% = 68: change.type$ = "Phone" ELSE change.type$ = "All"
	 IF updwn% = 134 THEN updwn% = 68: change.type$ = "Credit" ELSE change.type$ = "All"
	 IF updwn% = 136 THEN CALL allchgphone(rec%)'Shift F12
510
	 IF updwn% = 59 THEN
		bpgm$ = "XXWHO01X"
		ENVIRON "PARM$=" + apgm$
		CLOSE : CALL EXITPGM(bpgm$): CHAIN bpgm$

		CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
	 END IF
	 IF updwn% = 60 THEN CALL PCASE(chi%, ch%, DB.OR.CR$)
	 IF updwn% = 27 THEN
			rec% = p
			CALL dsply(p%, DB.OR.CR$, dpage%)
			IF rec% <= 0 THEN GOTO 480
				GET #ch%, rec%, cus

				IF CVI(cus.sno$) <> rec% THEN
				LSET cus.opn$ = MKS$(0)
				LSET cus.opn30$ = MKS$(0)
				LSET cus.opn60$ = MKS$(0)
				LSET cus.opn90$ = MKS$(0)
				ELSE
				GOSUB chg.opn
				END IF

				PUT #ch%, rec%, cus

			p = p + 1: IF p > maxwho% THEN updwn% = 59
			IF updwn% = 59 THEN bse% = 1: GOTO 300
			updwn% = 27
			GOTO 510
			END IF
	IF updwn% = 61 THEN GOSUB chg306090: GOTO 480 '***** F3 Swap
	IF updwn% = 62 THEN CALL do.delete(rec%, updwn%, "Y"): rec% = p: CALL dsply(rec%, DB.OR.CR$, dpage%): GOTO 480 '***** F4 Delete
	IF updwn% = 63 THEN        '***** F5 Pickup search
		a$ = cus.spname$
		CALL browse.pickup(a$)
		IF rec% >= 1 AND rec% <= 999 THEN
		GET #ch%, rec%, cus
		LSET cus.spname$ = a$
		PUT #ch%, rec%, cus
		END IF
		bse% = 1
		GOTO 300
		END IF
	 IF updwn% = 64 THEN        '***** F6 Client search
		CALL browse.idx(first.on.screen%, chi%, ch%)
		p = first.on.screen%
		bse% = 1
		GOTO 300
		END IF
	 IF updwn% = 65 THEN

		LOCATE 3, 2: PRINT SPACE$(50)
		LOCATE 3, 2: PRINT "Update the Index or trim the file (I,T)..> ";
		CALL inpnew(a$, 101!, updwn%, "13,59")
		a$ = UCASE$(a$)
		IF a$ = "T" THEN CALL trimfile(ok%): RUN
		IF a$ = "I" THEN
			apgm$ = "XXWHO01X"
			CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
			END IF
		END IF
	 IF updwn% = 66 THEN 'Move to "LEAD" file
		CALL copy.rec.to(rec%, updwn%, DB.OR.CR$, "Y")
		p$ = STR$(rec%)
		IF updwn% = 13 THEN
			'ask.del$ = "N"
			'CALL do.delete(rec%, updwn%,ask.del$)
		END IF
		END IF

	 IF updwn% = 68 THEN
		 CALL change(rec%, updwn%, chg%, rerec%, DB.OR.CR$, dpage%)
		 IF change.type$ <> "All" AND updwn% = 13 THEN
			 updwn% = 68: p = p + 1: rec% = p
			 CALL dsply(rec%, DB.OR.CR$, dpage%)
			 GOTO 510
		 END IF
		 IF bse% = 1 THEN rec% = p: CALL dsply(rec%, DB.OR.CR$, dpage%)
		 GOTO 480
		 END IF

	 IF updwn% = 72 THEN   '***** UP arrow Go back one, pressed
		p = p - 1
	 END IF
	 IF updwn% = 80 THEN   '***** DN arrow forward one
		p = p + 1
	 END IF

	 IF updwn% = 13 THEN
	 IF LEN(p$) = 0 THEN
		p = p + 1
		ELSE
		p = VAL(p$)
		IF p <= 0 THEN
		keyin$ = p$
		CALL searchindex(keyin$, chi%, found%)
		'IF found% THEN
			SELECT CASE chi%
			CASE 23: p = CVI(cusx.wrrn$)
			CASE 45: p = CVI(supx.wrrn$)
			CASE 65: p = CVI(whox.wrrn$)
			CASE ELSE
			END SELECT
			p = CVI(supx.wrrn$)

		'    END IF
		END IF
		END IF
		END IF

	 IF updwn% = 73 THEN 'page up
		dpage% = 1
		END IF

	 IF updwn% = 81 THEN 'page down
		dpage% = 2
		END IF

rec% = p
CALL dsply(rec%, DB.OR.CR$, dpage%)
GOTO 480
'////////////////////////////////////////////////////////////////////////////
'>>>>> C H A N G E    T H E   30, 60, 90 DAYS FIELDS
'////////////////////////////////////////////////////////////////////////////
chg306090:
	 IF dpage% <> 1 THEN GOTO xchg3060.noupd
	 IF rec% < 1 OR rec% >= maxwho% THEN GOTO xchg3060.noupd
	 IF DB.OR.CR$ = "DB" THEN
	GET #43, rec%, cus
	 ELSE
	GET #44, rec%, cus
	 END IF
	 scur = CVS(cus.scur$): s30 = CVS(cus.s30$): s60 = CVS(cus.s60$): s90 = CVS(cus.s90$)
	 opn0 = CVS(cus.opn$): opn30 = CVS(cus.opn30$): opn60 = CVS(cus.opn60$): opn90 = CVS(cus.opn90$)
	 COLOR 7
	 totalo = opn0 + opn30 + opn60 + opn90
	 LOCATE 20, 3: PRINT "Last Month.>  90+ days     60 Days     30 Days     Current        Total"
	 COLOR 2
	 LOCATE 21, 3: PRINT USING "            ###,###.##  ###,###.##  ###,###.##  ###,###.## #,###,###.##"; opn90; opn60; opn30; opn0; totalo
	 Total = scur + s30 + s60 + s90
	 LOCATE 23, 3: PRINT USING "            ###,###.##  ###,###.##  ###,###.##  ###,###.## #,###,###.##"; s90; s60; s30; scur; Total
cf1:
	 a$ = STR$(s90)
				 LOCATE 23, 15:  CALL inpnew(a$, -9.2, updwn%, "13,59-61")
	 X% = INSTR(a$, "."): IF X% > 0 THEN a$ = MID$(a$, 1, X% + 2)
	 LSET cus.s90$ = MKS$(VAL(a$)): s90 = VAL(a$)
	 IF updwn% = 59 THEN GOTO xchg3060
	 IF updwn% = 60 THEN GOTO cf1
	 IF updwn% = 61 THEN GOSUB chg.opn: GOTO cf1

cf2:
	 a$ = STR$(s60)
				 LOCATE 23, 27:  CALL inpnew(a$, -9.2, updwn%, "13,59,60")
	 X% = INSTR(a$, "."): IF X% > 0 THEN a$ = MID$(a$, 1, X% + 2)
	 LSET cus.s60$ = MKS$(VAL(a$)): s60 = VAL(a$)
	 IF updwn% = 59 THEN GOTO xchg3060
	 IF updwn% = 60 THEN GOTO cf1


cf3:
	 a$ = STR$(s30)
				 LOCATE 23, 39:  CALL inpnew(a$, -9.2, updwn%, "13,59,60")
	 X% = INSTR(a$, "."): IF X% > 0 THEN a$ = MID$(a$, 1, X% + 2)
	 LSET cus.s30$ = MKS$(VAL(a$)): s30 = VAL(a$)
	 IF updwn% = 59 THEN GOTO xchg3060
	 IF updwn% = 60 THEN GOTO cf2
cf4:
	 a$ = STR$(scur)
				 LOCATE 23, 51: CALL inpnew(a$, -9.2, updwn%, "13,59,60")
	 X% = INSTR(a$, "."): IF X% > 0 THEN a$ = MID$(a$, 1, X% + 2)
	 LSET cus.scur$ = MKS$(VAL(a$)): scur = VAL(a$)
	 IF updwn% = 59 THEN GOTO xchg3060
	 IF updwn% = 60 THEN GOTO cf3

xchg3060:
	 COLOR 2
	 Total = scur + s30 + s60 + s90
	 LOCATE 23, 3: PRINT USING "            ###,###.##  ###,###.##  ###,###.##  ###,###.## #,###,###.##"; s90; s60; s30; scur; Total
	 a$ = "Y"
	 LOCATE 23, 77: CALL inpnew(a$, 101!, updwn%, "13,59")
	 a$ = UCASE$(a$)
	 IF a$ = "Y" THEN
		PUT #ch%, rec%, cus
	 END IF

xchg3060.noupd:
	 chg% = 1: p = rec%
	 RETURN
'////////////////////////////////////////////////////////////////////////////
'>>>>> C H A N G E    T H E   OPENIONG BALANCES
'////////////////////////////////////////////////////////////////////////////
chg.opn:
	 scur = CVS(cus.scur$): s30 = CVS(cus.s30$): s60 = CVS(cus.s60$): s90 = CVS(cus.s90$)
	 opn0 = CVS(cus.opn$): opn30 = CVS(cus.opn30$): opn60 = CVS(cus.opn60$): opn90 = CVS(cus.opn90$)
	 COLOR 7
	 totalo = opn0 + opn30 + opn60 + opn90
	 LOCATE 20, 3: PRINT "Statement..>  90+ days     60 Days     30 Days     Current        Total"
	 COLOR 2
	 LOCATE 21, 3: PRINT USING "            ###,###.##  ###,###.##  ###,###.##  ###,###.## #,###,###.##"; opn90; opn60; opn30; opn0; totalo
	 Total = scur + s30 + s60 + s90
	 LOCATE 23, 3: PRINT USING "            ###,###.##  ###,###.##  ###,###.##  ###,###.## #,###,###.##"; s90; s60; s30; scur; Total

cfo2:
	 a$ = STR$(opn90): a$ = LTRIM$(a$)
				 LOCATE 21, 15:  CALL inpnew(a$, -9.2, updwn%, "13,59,60")
	 X% = INSTR(a$, "."): IF X% > 0 THEN a$ = MID$(a$, 1, X% + 2)
	 LSET cus.opn90$ = MKS$(VAL(a$)): opn90 = VAL(a$)
	 IF updwn% = 59 THEN GOTO xchg.opn
	 IF updwn% = 60 THEN GOTO xchg.opn
cfo3:
	 a$ = STR$(opn60): a$ = LTRIM$(a$)
				 LOCATE 21, 27:   CALL inpnew(a$, -9.2, updwn%, "13,59,60")
	 X% = INSTR(a$, "."): IF X% > 0 THEN a$ = MID$(a$, 1, X% + 2)
	 LSET cus.opn60$ = MKS$(VAL(a$)): opn60 = VAL(a$)
	 IF updwn% = 59 THEN GOTO xchg.opn
	 IF updwn% = 60 THEN GOTO cfo2

cfo4:
	 a$ = STR$(opn30): a$ = LTRIM$(a$)
				 LOCATE 21, 39:  CALL inpnew(a$, -9.2, updwn%, "13,59,60")
	 X% = INSTR(a$, "."): IF X% > 0 THEN a$ = MID$(a$, 1, X% + 2)
	 LSET cus.opn30$ = MKS$(VAL(a$)): opn30 = VAL(a$)
	 IF updwn% = 59 THEN GOTO xchg.opn
	 IF updwn% = 60 THEN GOTO cfo3

cfo5:
	 a$ = STR$(opn0): a$ = LTRIM$(a$)
				 LOCATE 21, 51:  CALL inpnew(a$, -9.2, updwn%, "13,59,60")
	 X% = INSTR(a$, "."): IF X% > 0 THEN a$ = MID$(a$, 1, X% + 2)
	 LSET cus.opn$ = MKS$(VAL(a$)): opn0 = VAL(a$)
	 IF updwn% = 59 THEN GOTO xchg.opn
	 IF updwn% = 60 THEN GOTO cfo4
xchg.opn:
	 COLOR 7
	 totalo = opn0 + opn30 + opn60 + opn90
	 LOCATE 22, 3: PRINT "Statment...>  90+ days     60 Days     30 Days     Current        Total";
	 COLOR 2
	 LOCATE 21, 3: PRINT USING "            ###,###.##  ###,###.##  ###,###.##  ###,###.## #,###,###.##"; opn90; opn60; opn30; opn0; totalo

	 a$ = "Y"
	 LOCATE 20, 77:  CALL inpnew(a$, 1!, updwn%, "13,59,60")
	 a$ = UCASE$(a$)
	 IF updwn% = 59 THEN GOTO xchg.opn2
	 IF updwn% = 60 THEN GOTO cfo5
	 IF a$ = "N" THEN GOTO cfo5
xchg.opn2:
RETURN

SUB allchgphone (rec%)


	SELECT CASE DB.OR.CR$
	CASE "CR": chi% = 45: ch% = 44: apgm$ = "CSMENU"
	CASE "DB": chi% = 23: ch% = 43: apgm$ = "DSMENU"
	CASE "--": chi% = 65: ch% = 64: apgm$ = "FIMENU"
	CASE ELSE
	END SELECT

	IF rec% = 0 THEN rec% = 1
	GET #ch%, rec%, cus
	DO WHILE NOT EOF(ch%)


		dpage% = 2
		CALL dsply(rec%, DB.OR.CR$, dpage%)
		CALL rmvnull


		'Phone
		IF RTRIM$(cus.ContactPhone$(1)) = "11-1111-1111" THEN cus.ContactPhone$(1) = cus.sphone$
		IF RTRIM$(cus.ContactPhone$(1)) = "11-1111-1111" THEN cus.ContactPhone$(1) = "111-1111-1111"
		IF INSTR(RTRIM$(cus.ContactPhone$(1)), "11111") > 0 THEN cus.ContactPhone$(1) = "111-1111-1111"

		FOR X% = 1 TO 20
		IF MID$(cus.ContactPhone$(1), X%, 1) = CHR$(0) THEN MID$(cus.ContactPhone$(s%), X%, 1) = " "
		IF MID$(cus.sphone$, X%, 1) = CHR$(0) THEN MID$(cus.sphone$, X%, 1) = " "
		NEXT
		IF RTRIM$(cus.ContactPhone$(1)) = RTRIM$(cus.sphone$) AND LEN(RTRIM$(cus.ContactPhone$(1))) < 13 THEN
			cus.ContactPhone$(1) = " " + cus.ContactPhone$(1)
		END IF

		FOR s% = 2 TO 6
		IF RTRIM$(cus.ContactPhone$(s%)) = "11-1111-1111" THEN cus.ContactPhone$(s%) = "111-1111-1111"
		IF INSTR(RTRIM$(cus.ContactPhone$(s%)), "11111") > 0 THEN cus.ContactPhone$(1) = "111-1111-1111"
		IF LEN(RTRIM$(cus.ContactPhone$(s%))) < 13 THEN
			cus.ContactPhone$(s%) = " " + cus.ContactPhone$(s%)
		END IF

		NEXT

		'Fax
		IF RTRIM$(cus.ContactFax$(1)) = "11-1111-1111" THEN cus.ContactFax$(1) = cus.sphone1$
		IF RTRIM$(cus.ContactFax$(1)) = "11-1111-1111" THEN cus.ContactFax$(1) = "111-1111-1111"
		IF INSTR(RTRIM$(cus.ContactFax$(1)), "11111") > 0 THEN cus.ContactFax$(1) = "111-1111-1111"

		FOR X% = 1 TO 20
		IF MID$(cus.ContactFax$(1), X%, 1) = CHR$(0) THEN MID$(cus.ContactFax$(1), X%, 1) = " "
		IF MID$(cus.sphone1$, X%, 1) = CHR$(0) THEN MID$(cus.sphone1$, X%, 1) = " "
		NEXT

		IF RTRIM$(cus.ContactFax$(1)) = RTRIM$(cus.sphone1$) AND LEN(RTRIM$(cus.ContactFax$(1))) < 13 THEN
			cus.ContactFax$(1) = " " + cus.ContactFax$(1)
		END IF


		FOR s% = 2 TO 6
		IF RTRIM$(cus.ContactFax$(s%)) = "11-1111-1111" THEN cus.ContactFax$(s%) = "111-1111-1111"
		IF LEN(RTRIM$(cus.ContactFax$(s%))) < 13 THEN
			cus.ContactFax$(s%) = " " + cus.ContactFax$(s%)
		END IF

		NEXT

		'Mobile must be 1111-111-111
		FOR s% = 1 TO 6
		IF MID$(cus.ContactMobile$(1), s%, 1) = CHR$(0) THEN MID$(cus.ContactMobile$(1), s%, 1) = " "
		IF INSTR(cus.ContactMobile$(1), "11111") > 0 THEN cus.ContactMobile(s%) = "1111-111-111"
		IF LEN(RTRIM$(cus.ContactMobile(s%))) < 12 THEN
			cus.ContactMobile$(s%) = " " + cus.ContactMobile$(s%)
		END IF


		IF VAL(MID$(cus.ContactMobile$(s%), 1, 4)) > 0 THEN
		IF MID$(cus.ContactMobile$(s%), 5, 1) = " " THEN MID$(cus.ContactMobile$(s%), 5, 1) = "-"
		IF MID$(cus.ContactMobile$(s%), 9, 1) = " " THEN MID$(cus.ContactMobile$(s%), 9, 1) = "-"
		END IF
		NEXT

		'>----------------------------------------------------------
		'>- Test
		'>----------------------------------------------------------
		ok% = -1
		FOR s% = 1 TO 6
		IF VAL(MID$(cus.ContactPhone$(s%), 3, 1)) > 0 THEN
		IF MID$(cus.ContactPhone$(s%), 4, 1) <> "-" THEN ok% = 0: msg$ = "phone"
		IF MID$(cus.ContactPhone$(s%), 9, 1) <> "-" THEN ok% = 0: msg$ = "phone"
		END IF

		IF VAL(MID$(cus.ContactFax$(s%), 3, 1)) > 0 THEN
		IF MID$(cus.ContactFax$(s%), 4, 1) <> "-" THEN ok% = 0: msg$ = "fax" + STR$(s%)
		IF MID$(cus.ContactFax$(s%), 9, 1) <> "-" THEN ok% = 0: msg$ = "fax" + STR$(s%)
		END IF

		IF VAL(MID$(cus.ContactMobile$(s%), 3, 1)) > 0 THEN
		IF MID$(cus.ContactMobile$(s%), 5, 1) <> "-" THEN ok% = 0: msg$ = "Mobile"
		IF MID$(cus.ContactMobile$(s%), 9, 1) <> "-" THEN ok% = 0: msg$ = "Mobile"
		END IF
		IF NOT ok% THEN EXIT FOR
		NEXT

		IF NOT ok% THEN
		IF msg$ > "" THEN
			CALL sndmsg(msg$): msg$ = ""
			END IF
		cus.ContactPhone$(1) = cus.sphone
		cus.ContactFax$(1) = cus.sphone1
		CALL change(rec%, updwn%, chg%, rerec%, DB.OR.CR$, dpage%)
		END IF

		'>- Update and show it!!

		cus.sphone = cus.ContactPhone$(1)
		cus.sphone1 = cus.ContactFax$(1)
		cus.email$ = cus.Contactemail$(1)

		PUT #ch%, rec%, cus
		dpage% = 2
		CALL dsply(rec%, DB.OR.CR$, dpage%)


		'CALL inpnew(a$, 0!, updwn%, "59,13")
		X$ = INKEY$
		IF X$ <> "" THEN updwn% = ASC(X$)
		IF updwn% = 27 THEN EXIT SUB



		GET #ch%, , cus: rec% = rec% + 1
		LOOP




END SUB

SUB browse.idx (firstonscreen%, ch1%, ch2%) STATIC
'$INCLUDE: '\tpmanuf\src\browse01.bi'
END SUB

'/////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>         C S W H O 0 1       <<<<<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'>>>>>>>>>> CHANGES
'>>>>>>>>>> 12/3/92 : updated screen, to new screen design
'>>>>>>>>>> LJC     : PGUP, PGDN, UP & DN arrow key browse
'>>>>>>>>>>         : Added Transport Depot name on screen
'>>>>>>>>>>         : Taken out 0 pick up record numbers
'>>>>>>>>>>         : PGUP key not 100% fixed.
'>>>>>>>>>>         :
'
'
SUB browse.pickup (a$) STATIC
	 rec% = VAL(a$)
	 CALL setup("BROWSE PICKUP ADDRESS")
	 COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : LOCATE 25, 71: PRINT CHR$(24); CHR$(25); "-Move";
	 COLOR 7, 0: LOCATE 2, 23: PRINT "µ                              Æ": COLOR 2
	 LOCATE 2, 25: PRINT "Browse Pickup address..> "
	 COLOR 4, 0: LOCATE 3, 7: PRINT "TRANSPORT COMPANY": LOCATE 3, 41: PRINT "TRANSPORT DEPOT";
	 COLOR 2, 0
browse.pickup.again:
	 n% = 0
	 w = 0

	 IF rec% < 1 OR rec% > 999 THEN rec% = 1
	 GET #50, rec%, pickup
	 DO WHILE NOT EOF(50)
		IF n% > 19 THEN EXIT DO

		IF n% = 0 THEN s% = rec%
		IF CVI(pickup.pno$) <> rec% THEN
			w = w + 1
			IF updwn% = 73 THEN rec% = rec% - 1
			IF updwn% = 80 THEN rec% = rec% + 1
			ELSE
			LOCATE n% + 4, 2: PRINT CVI(pickup.pno$);
			LOCATE n% + 4, 7: PRINT pickup.pname1$;
			LOCATE n% + 4, 41: PRINT pickup.pname2$;
			n% = n% + 1
			END IF

		GET #50, , pickup: rec% = rec% + 1
		LOOP

	 k% = 0
	 DO WHILE n% < 20
		LOCATE n% + 4, 2: PRINT CHR$(FNE)
		n% = n% + 1
		k% = k% + 1
		LOOP

	 COLOR 2, 0
	 a$ = ""
	 LOCATE 2, 50: CALL inpnew(a$, 3!, updwn%, "13,59,72,73,80,81")
	 COLOR 2, 0
	 IF updwn% = 59 THEN GOTO x.browse.pickup.again:
	 IF updwn% = 72 THEN        '***** UP arrow
	rec% = s% - 1
	DO WHILE w <> 1
		IF rec% = 0 THEN rec% = 1
		GET #50, rec%, pickup
		IF CVI(pickup.pno$) <> 0 THEN EXIT DO
		rec% = rec% - 1
	LOOP
		GOTO browse.pickup.again
	 END IF
	 IF updwn% = 73 THEN        '***** PGUP
	rec% = s% - 19
	GOTO browse.pickup.again
	 END IF
	 IF updwn% = 80 THEN        '***** DN arrow
	IF k% > 18 THEN
		 rec% = s%
	ELSE
		 rec% = s% + 1
	END IF
	GOTO browse.pickup.again
	 END IF
	 IF updwn% = 81 THEN        '***** PGDN
	IF k% > 0 THEN
		 rec% = s%
	ELSE
		 rec% = s% + 19 + w
	END IF
	GOTO browse.pickup.again
	 END IF
	 IF LEN(a$) > 0 THEN rec% = VAL(a$)
	 n% = 0
	 GOTO browse.pickup.again
x.browse.pickup.again:
	 a$ = MID$(STR$(s%), 2)
END SUB

SUB change (rec%, updwn%, chg%, rerec%, DB.OR.CR$, dpage%)
'/////////////////////////////////////////////////////////////////////////////
'>>>>> C H A N G E
'////   /////////////////////////////////////////////////////////////////////////

change:
	 IF rec% < 1 OR rec% > maxwho% THEN updwn% = 60: GOTO x.change
	 IF rerec% = 1 THEN rerec% = 0: GOTO gstype

	 '>>-- Save the customer SEARCH CODE --<<
	 init.search$ = cus.search$ + cus.stype$

	'***** I N I T I L I Z E   S T R I N G S
	 oldsno% = CVI(cus.sno$)
	 oldtype$ = cus.stype$
	 IF CVI(cus.sno$) <> rec% THEN
	LSET cus.sno$ = MKI$(rec%)
	LSET cus.sname$ = SPACE$(30):  LSET cus.spname$ = SPACE$(30)
	LSET cus.saddr$ = SPACE$(20):  LSET cus.spcode$ = SPACE$(4)
	LSET cus.saddr2$ = SPACE$(20)

	LSET cus.spsub$ = SPACE$(30)
	'SET cus.sacode$ = SPACE$(3):
	LSET cus.sphone$ = SPACE$(7)
	'SET cus.sacode1$ = SPACE$(3):
	LSET cus.sphone1$ = SPACE$(7)
	LSET cus.scont$ = SPACE$(15):  LSET cus.suburb$ = SPACE$(15): LSET cus.spbox$ = SPACE$(6)
	'SET cus.sacode$ = SPACE$(3)
	cus.sdist$ = " ": cus.sret$ = " "
	LSET cus.taxe$ = SPACE$(10):   LSET cus.account$ = SPACE$(5)
	LSET cus.pstnCC$ = SPACE$(99)
	END IF
IF dpage% = 2 THEN
	CALL rmvnull


	i% = 1: X% = 1
	DO
	IF i% < 1 OR i% > 6 THEN i% = 1  'JIC

	y% = 11 + i% * 2 - 1



	SELECT CASE X%
	'1st line
	CASE 1: LOCATE y%, 3: CALL inpnew(cus.ContactFirstName$(i%), 116!, updwn%, "13,59-61")
	CASE 2: LOCATE y%, 20: CALL inpnew(cus.ContactSurName$(i%), 120!, updwn%, "13,59-61")
	CASE 3: LOCATE y%, 41: CALL inpnew(cus.ContactTitle$(i%), 120!, updwn%, "13,59-60,61")
	CASE 4: LOCATE y%, 62: CALL inpnew(cus.ContactPhone$(i%), 118!, updwn%, "13,59-60,61")
	'2nd line
	CASE 5: LOCATE y% + 1, 3: CALL inpnew(cus.Contactemail$(i%), 137!, updwn%, "13,59-60,61")
	CASE 6: LOCATE y% + 1, 41: CALL inpnew(cus.ContactFax$(i%), 118!, updwn%, "13,59-60,61")
	CASE 7: LOCATE y% + 1, 62: CALL inpnew(cus.ContactMobile$(i%), 118!, updwn%, "13,59-60,61")
	CASE ELSE: X% = 1
	END SELECT

	IF updwn% = 59 THEN EXIT DO
	IF updwn% = 60 THEN X% = X% - 1: IF X% < 1 THEN i% = i% - 1: X% = 1
	IF updwn% = 61 THEN
		IF X% = 1 THEN cus.ContactFirstName$(i%) = "........................"
		IF X% = 2 THEN cus.ContactSurName$(i%) = "........................."
		IF X% = 4 THEN cus.ContactPhone$(i%) = "111-1111-1111": updwn% = 0
		IF X% = 5 THEN cus.Contactemail$(i%) = STRING$(99, "."): updwn% = 0
		IF X% = 6 THEN cus.ContactFax$(i%) = "111-1111-1111": updwn% = 0
		IF X% = 7 THEN cus.ContactMobile$(i%) = "1111-111-111": updwn% = 0
		IF X% = 3 THEN CALL TitleList(cus.ContactTitle$(i%), updwn%)
		END IF
	IF updwn% = 13 THEN
		IF X% < 7 THEN
			X% = X% + 1
		ELSE
			i% = i% + 1: X% = 1
		END IF
		END IF
	LOOP WHILE i% <= 6

	'Update Scont with first line
	a$ = RTRIM$(cus.ContactFirstName$(1)) + " " + cus.ContactSurName$(1)
	cus.scont$ = a$
	cus.sphone = cus.ContactPhone$(1)
	cus.sphone1 = cus.ContactFax$(1)
	cus.email$ = cus.Contactemail$(1)


GOTO gssave
END IF

'----------------------------------------------------------------------------
IF change.type$ = "Phone" THEN GOTO gsrep
IF change.type$ = "Credit" THEN GOTO gsmd
'----------------------------------------------------------------------------
gstype:      '***** File alpha key
	 a$ = cus.search$
	 LOCATE 3, 31: CALL inpnew(a$, 104!, updwn%, "13,59-60")
	 a$ = UCASE$(a$)
	 IF updwn% = 60 THEN updwn% = 59
	 IF updwn% = 59 THEN
		LSET cus.stype$ = oldtype$
		GOTO gssave     '***** Exit
		END IF
	 ok = 1
	 FOR i% = 1 TO 4
		b$ = MID$(a$, i%, 1)
		IF b$ < "A" OR b$ > "z" THEN ok = 0: EXIT FOR
		IF b$ >= "³" AND b$ <= "^" THEN ok = 0: EXIT FOR
		IF b$ = "'" OR b$ = "~" THEN ok = 0: EXIT FOR
		NEXT
	 IF ok = 0 THEN
	COLOR 14: LOCATE 4, 40: PRINT "Search key not made from A-Z, "; "-"; " or a-z"; CHR$(FNE): COLOR 2
	er = 1
	GOTO gstype
	 END IF
	 keyin$ = p$
	 CALL searchindex(keyin$, chi%, found%)
	 wrrn% = CVI(cusx.wrrn$)
	 IF LEN(a$) > 0 THEN LSET cus.search$ = a$
gtype:         '***** Calling type
	 CALL sndmsg("F4-To revmove from audit calculations")
	 a$ = cus.stype$
	 LOCATE 3, 50: CALL inpnew(a$, 101!, updwn%, "13,59-60,62")
	 CALL sndmsg("")
	 IF updwn% = 59 THEN GOTO gssave   '***** back to enter code question w/change
	 IF updwn% = 60 THEN GOTO gstype
	 IF updwn% = 62 THEN
		CALL LogicalDelete(rec%, updwn%)
		IF updwn% = 59 THEN bse% = 1: GOTO x.change
		IF updwn% = 66 THEN bse% = 1: GOTO x.change 'Reinstate
		ask.del$ = "N"
		CALL copy.rec.to(rec%, updwn%, DB.OR.CR$, ask.del$)
		IF updwn% = 59 THEN bse% = 1: GOTO x.change
		'ask.del$ = "N"
		'CALL do.delete(rec%, updwn%, ask.del$)
		bse% = 1: GOTO x.change
		END IF

	 a$ = UCASE$(a$)
	 ok = 0
	 FOR i% = 1 TO maxtyp%
	IF a$ = type$(i%) THEN ok = 1: EXIT FOR
	 NEXT
	 IF ok = 0 THEN CALL sndmsg("Type not valid."): COLOR 2: GOTO gtype
	 CALL sndmsg("")
	 LSET cus.stype$ = a$
	 b$ = SPACE$(20)
	 GET #42, i%, types: LSET b$ = types.dfdesc$
	 LOCATE 3, 54: PRINT b$;
	 IF DB.OR.CR$ = "CR" THEN
	 ELSEIF UCASE$(cus.stype$) = "Z" THEN
	COLOR 12
	LOCATE 11, 6: PRINT "Charge to..........>";
	COLOR 2
	LOCATE 11, 27: PRINT chargto$;
	 ELSEIF DB.OR.CR$ = "DB" THEN
		 'LOCATE 11, 2: PRINT CHR$(fne)
	 END IF '***** Index check complete

IF change.type$ = "Phone" THEN GOTO gsbpn

gslevel:       '***** pricing level
	 SELECT CASE cus.stype$
	 CASE "D", "H", "G", "M", "Y"
	 CALL sndmsg("Set pricing level above (+ve) or at discount to (-ve) D rate")
	 a$ = SPACE$(6)
	 RSET a$ = STR$(cus.slevel)
		LOCATE 23, 4: CALL inpnew(a$, 106!, updwn%, "13,59-60")
		IF updwn% = 59 THEN GOTO gssave  '***** Exit w/change
		IF updwn% = 60 THEN GOTO gtype  '***** Back
		cus.slevel = VAL(a$)
		LOCATE 23, 4: PRINT USING "###.##%"; cus.slevel
		CALL sndmsg("")
	 CASE ELSE
		cus.slevel = 0
	 END SELECT



gsname:       '***** the suppliers name
	 a$ = cus.sname$
	 LOCATE 4, 15: CALL inpnew(a$, 135!, updwn%, "13,59-60")
	 IF updwn% = 59 THEN GOTO gssave  '***** Exit w/change
	 IF updwn% = 60 THEN GOTO gtype  '***** Back
	 IF LEN(a$) > 0 THEN LSET cus.sname$ = a$
gsgl:       '***** the GENERAL LEDGER
	 a$ = STR$(CVS(cus.sgl$))
	 LOCATE 4, 75: CALL inpnew(a$, 5!, updwn%, "13,59-60")
	 IF updwn% = 59 THEN GOTO gssave  '***** Exit w/change
	 IF updwn% = 60 THEN GOTO gsname  '***** Back
	 IF LEN(a$) > 0 THEN LSET cus.sgl$ = MKS$(VAL(a$))
	 LOCATE 4, 75: PRINT USING "#####"; CVS(cus.sgl$);
gsaddr:            '*****  first part of address
	 a$ = cus.saddr$
	 LOCATE 5, 15: CALL inpnew(a$, 135!, updwn%, "13,59-60")
	 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 IF updwn% = 60 THEN GOTO gsgl
	 LSET cus.saddr$ = a$
gsaddr2:            '*****  first part of address
	 a$ = cus.saddr2$
	 LOCATE 6, 15: CALL inpnew(a$, 135!, updwn%, "13,59-60")
	 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 IF updwn% = 60 THEN GOTO gsgl
	 LSET cus.saddr2$ = a$

gssub:          '***** suburb
	 a$ = cus.suburb$:
	 LOCATE 7, 15: CALL inpnew(a$, 120!, updwn%, "13,59-60")
	 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 IF updwn% = 60 THEN GOTO gsaddr2
	 LSET cus.suburb$ = a$

gspc:            '***** Postcode
	 a$ = cus.spcode$:
	 LOCATE 7, 46: CALL inpnew(a$, 104!, updwn%, "13,59-60")
	 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 IF updwn% = 60 THEN GOTO gssub
	 LSET cus.spcode$ = a$

gspun:           '*****  the pick up name with indicator
	 a$ = cus.spname$:
	 IF VAL(a$) = 0 THEN a$ = "0"
	 LOCATE 4, 68: CALL inpnew(a$, 3!, updwn%, "13,59-60,63")
	 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 IF updwn% = 60 THEN GOTO gspc
	 IF updwn% = 63 THEN
			 CALL browse.pickup(a$)
			IF rec% >= 1 AND rec% <= 999 THEN
				GET #ch%, rec%, cus
				LSET cus.spname$ = a$
				PUT #ch%, rec%, cus
			END IF
			chg% = 1
			CLS
			updwn% = 60: GOTO x.change
			END IF
			'<<<<<

	 IF LEN(a$) > 0 THEN LSET cus.spname$ = a$
	 IF VAL(cus.spname$) >= 1 AND VAL(cus.spname$) <= 999 THEN
			sprec% = VAL(cus.spname$)
			GET #50, sprec%, pickup
			LSET spcontact$ = pickup.pname1$
			LSET spphone$ = pickup.pphone1$
			LSET spdepph$ = pickup.pphone2$
			LSET spname.dsply$ = pickup.pname2$
			LSET cus.spname$ = MID$(STR$(sprec%), 2)
			LSET spuaddr$ = pickup.pname3$
			LSET spusub$ = pickup.pname4$
			ELSE
			LSET spcontact$ = SPACE$(30)
			LSET spphone$ = SPACE$(30)
			LSET spdepph$ = SPACE$(30)
			LSET spname.dsply$ = cus.spname$
			LSET spuaddr$ = SPACE$(30)
			LSET spusub$ = SPACE$(30)
			END IF
			IF LEN(a$) = 0 AND cus.spname$ = SPACE$(30) THEN LSET cus.spname$ = cus.sname$

			LOCATE 15, 15: PRINT spcontact$;
			LOCATE 15, 64: PRINT spphone$:
			LOCATE 15, 64: PRINT spdepph$:
			LOCATE 16, 15: PRINT spname.dsply$;
			LOCATE 17, 15: PRINT spuaddr$;
			LOCATE 18, 15: PRINT spusub$;

gspobox:            '*****  PO Box Number
	 a$ = cus.spbox$:
	 LOCATE 8, 15: CALL inpnew(a$, 106!, updwn%, "13,59-60")
	 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 IF updwn% = 60 THEN GOTO gspun
	 LSET cus.spbox$ = a$

gspboxsub:
	 a$ = cus.spboxsub$
	 LOCATE 8, 32: CALL inpnew(a$, 120!, updwn%, "13,59-60")
	 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 IF updwn% = 60 THEN GOTO gspobox
	 LSET cus.spboxsub$ = a$

gspboxpcode:
	 a$ = cus.spboxpcode$
	 LOCATE 8, 63: CALL inpnew(a$, 108!, updwn%, "13,59-60")
	 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 IF updwn% = 60 THEN GOTO gspboxsub
	 LSET cus.spboxpcode$ = a$

gstax:            '***** Tax exempted
	IF DB.OR.CR$ <> "DP" THEN '   was CR
		a$ = cus.taxe$
		LOCATE 2, 66: CALL inpnew(a$, 111!, updwn%, "13,59-60")
		a$ = a$ + "           ": a$ = LEFT$(a$, 11)

		'//// Edit the form of the tax exempt number ////   this section out
		' ok% = -1
		 ' IF MID$(a$, 1, 2) <> "VS" AND MID$(a$, 1, 2) <> "EE" THEN ok% = 0
		 ' IF MID$(a$, 3, 1) <> " " THEN ok% = 0
		 ' IF MID$(a$, 4, 1) < "0" OR MID$(a$, 4, 1) > "9" THEN ok% = 0
		 ' IF MID$(a$, 5, 1) < "0" OR MID$(a$, 5, 1) > "9" THEN ok% = 0
		 ' IF MID$(a$, 6, 1) < "0" OR MID$(a$, 6, 1) > "9" THEN ok% = 0
		 ' IF MID$(a$, 7, 1) < "0" OR MID$(a$, 7, 1) > "9" THEN ok% = 0
		 ' IF MID$(a$, 8, 1) < "0" OR MID$(a$, 8, 1) > "9" THEN ok% = 0
		 ' IF MID$(a$, 9, 1) < "0" OR MID$(a$, 9, 1) > "9" THEN ok% = 0
		 ' IF MID$(a$, 10, 1) < "0" OR MID$(a$, 10, 1) > "9" THEN ok% = 0
		 ' IF MID$(a$, 1, 2) = "  " THEN LSET a$ = SPACE$(99): ok% = -1
		 ' IF ok% = 0 THEN GOTO gstax
		'GOTO gstax
		LSET cus.taxe$ = a$
		 ' sndmsg ("")
		END IF

		IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
		IF updwn% = 60 THEN GOTO gspboxpcode
gscont:            '*****  contact name
	 'a$ = cus.scont$:
	 'LOCATE 9, 15: CALL inpnew(a$, 120!, updwn%, "13,59-60")
	 'IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 'IF updwn% = 60 AND DB.OR.CR$ = "--" THEN GOTO gstax
	 'IF updwn% = 60 AND DB.OR.CR$ = "CR" THEN GOTO gspobox
	 'IF updwn% = 60 AND DB.OR.CR$ = "CR" THEN GOTO gspobox
	 'LSET cus.scont$ = a$

gsrep:
	 SELECT CASE DB.OR.CR$
	 CASE "DB": ok$ = "B,M,R,T,U,"
	 CASE "CR": ok$ = "B,L,N,S,U,V,"
	 CASE ELSE: ok$ = "B,C,M,T,U,"
	 END SELECT

	 CALL sndmsg(" Bad, Creditor, LLOYDS, M-retail, NATA, STANDARDS, Trade, Unknown ,VERITAS,")
	 '("Valid codes: " + ok$)
	 LOCATE 5, 58: CALL inpnew(cus.rep$, 101!, updwn%, "13,59-60")
	 ok% = 0
	 X% = INSTR(ok$, cus.rep$)
	 IF X% < 1 THEN GOTO gsrep
	 IF MID$(ok$, X%, 1) = "," THEN GOTO gsrep
	 CALL sndmsg(""): COLOR 2, 0
	 LOCATE 5, 58: PRINT USING "! \                  \"; cus.rep$; repcode$(cus.rep$, DB.OR.CR$)
	 IF updwn% = 59 THEN GOTO gssave
	 IF updwn% = 60 THEN GOTO gstax ' gscont

gsfreq:
	IF DB.OR.CR$ <> "CR" THEN
		ok$ = "W,M,S,Q,H,N,A,T,U"
		CALL sndmsg("Week, Month, SixWeek, Quarter, HalfYear, Never, Annual,Telephone, Unknown,")
		'("Valid codes: " + ok$)
		LOCATE 6, 58: CALL inpnew(cus.callfreq$, 101!, updwn%, "13,59-60")
		ok% = 0
		X% = INSTR(ok$, cus.callfreq$)
		IF X% < 1 THEN GOTO gsfreq
		IF MID$(ok$, X%, 1) = "," THEN GOTO gsfreq
		CALL sndmsg(""): COLOR 2, 0
		LOCATE 6, 58: PRINT USING "! \                  \"; cus.callfreq$; freqcode$(cus.callfreq$)
		END IF

	IF updwn% = 59 THEN GOTO gssave
	IF updwn% = 60 THEN GOTO gsrep


gsbpn:            '***** PHONE NUMBER
	 'a$ = MID$(cus.sphone$, 1, 2) + "-" + MID$(cus.sphone$, 3, 4) + MID$(cus.sphone$, 7, 4)
				 'LOCATE 10, 16: CALL inpnew(a$, 100.1!, updwn%, "13,59-60")
	 'IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 'IF updwn% = 60 THEN GOTO gsfreq
	 'LSET cus.sphone$ = MID$(a$, 1, 2) + MID$(a$, 4, 4) + MID$(a$, 8, 4)

gsfpn:          '***** Fax Phone number
	 'a$ = MID$(cus.sphone1$, 1, 2) + "-" + MID$(cus.sphone1$, 3, 4) + MID$(cus.sphone1$, 7, 4)
				 'LOCATE 10, 36: CALL inpnew(a$, 100.1!, updwn%, "13,59-60")
	 'IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 'IF updwn% = 60 THEN GOTO gsbpn
	 'LSET cus.sphone1$ = MID$(a$, 1, 2) + MID$(a$, 4, 4) + MID$(a$, 8, 4)

gsptsncc:
	 a$ = cus.pstnCC$
				 LOCATE 10, 77: CALL inpnew(a$, 103!, updwn%, "13,59-60")
	 IF updwn% = 59 THEN GOTO gssave
	 IF updwn% = 60 THEN GOTO gsfreq 'rgsfpn
	 LSET cus.pstnCC$ = a$

gwww:
	 a$ = cus.www$
				 LOCATE 11, 15: CALL inpnew(a$, 140!, updwn%, "13,59-61")
	 IF updwn% = 61 THEN cus.www = "www." + SPACE$(40): GOTO gwww
	 IF updwn% = 59 THEN GOTO gssave
	 IF updwn% = 60 THEN GOTO gsfpn
	 LSET cus.www$ = a$
gemail:
	 'a$ = cus.email$
				 'LOCATE 12, 22: CALL inpnew(a$, 140!, updwn%, "13,59-60")
	 'IF updwn% = 59 THEN GOTO gssave
	 'IF updwn% = 60 THEN GOTO gsfpn
	 'LSET cus.email$ = a$


IF change.type$ = "Phone" THEN GOTO gssave

gsrm:            '***** Retail margin
	 IF DB.OR.CR$ = "CR" THEN
		IF UCASE$(cus.stype$) = "A" THEN
			a$ = cus.sret$
			LOCATE 14, 5: CALL inpnew(a$, 101!, updwn%, "13,59-60")
			IF updwn% = 59 THEN GOTO gssave        '****** Exit w/change
			IF updwn% = 60 THEN GOTO gsfpn
			IF a$ = "/" OR a$ = "." THEN
					LSET cus.sret$ = a$: a = 0
					ELSE
					LSET cus.sret$ = a$:
					a% = ASC(cus.sret$) - 46:
					IF a% < 1 OR a% > 80 THEN CALL sndmsg("C:M A R G I N   I N V A L I D"): GOTO gsrm
					a = mm(a%):
					END IF
			LOCATE 14, 6: PRINT USING "###.##"; a;
			CALL sndmsg("")
		END IF
	 END IF
	'>>>>>------------
gscounter:
	 IF DB.OR.CR$ = "CR" THEN
		IF UCASE$(cus.stype$) = "A" THEN
			a$ = cus.countercde$
			LOCATE 14, 13: CALL inpnew(a$, 101!, updwn%, "13,59-60")
			IF updwn% = 59 THEN GOTO gssave        '****** Exit w/change
			IF updwn% = 60 THEN GOTO gsrm
			IF a$ = "/" OR a$ = "." THEN
					LSET cus.countercde$ = a$: a = 0
					ELSE
					LSET cus.countercde$ = a$:
					a% = ASC(cus.countercde$) - 46:
					IF a% < 1 OR a% > 80 THEN CALL sndmsg("C:M A R G I N   I N V A L I D"): GOTO gscounter
					a = mm(a%):
					END IF
			LOCATE 14, 14: PRINT USING "###.##"; a;
			CALL sndmsg("")
		END IF
	 END IF
	'>>>>>------------
gstrade:
	 IF DB.OR.CR$ = "CR" THEN
		IF UCASE$(cus.stype$) = "A" THEN
			a$ = cus.tradecde$
			LOCATE 14, 21: CALL inpnew(a$, 101!, updwn%, "13,59-60")
			IF updwn% = 59 THEN GOTO gssave        '****** Exit w/change
			IF updwn% = 60 THEN GOTO gscounter
			IF a$ = "/" OR a$ = "." THEN
					LSET cus.tradecde$ = a$: a = 0
					ELSE
					LSET cus.tradecde$ = a$:
					a% = ASC(cus.tradecde$) - 46:
					IF a% < 1 OR a% > 80 THEN CALL sndmsg("C:M A R G I N   I N V A L I D"): GOTO gstrade
					a = mm(a%):
					END IF
			LOCATE 14, 22: PRINT USING "###.##"; a;
			CALL sndmsg("")
		END IF
	 END IF

	'>>>>>------------
gscontract:
	 IF DB.OR.CR$ = "CR" THEN
		IF UCASE$(cus.stype$) = "A" THEN
			a$ = cus.contractcde$
			LOCATE 14, 29: CALL inpnew(a$, 101!, updwn%, "13,59-60")
			IF updwn% = 59 THEN GOTO gssave        '****** Exit w/change
			IF updwn% = 60 THEN GOTO gstrade
			IF a$ = "/" OR a$ = "." THEN
					LSET cus.contractcde$ = a$: a = 0
					ELSE
					LSET cus.contractcde$ = a$:
					a% = ASC(cus.contractcde$) - 46:
					IF a% < 1 OR a% > 80 THEN CALL sndmsg("C:M A R G I N   I N V A L I D"): GOTO gscontract
					a = mm(a%):
					END IF
			LOCATE 14, 30: PRINT USING "###.##"; a;
			CALL sndmsg("")
		END IF
	 END IF

	'>>>>>------------
gsindustrial:
	 IF DB.OR.CR$ = "CR" THEN
		IF UCASE$(cus.stype$) = "A" THEN
			a$ = cus.industrialcde$
			LOCATE 14, 37: CALL inpnew(a$, 101!, updwn%, "13,59-60")
			IF updwn% = 59 THEN GOTO gssave        '****** Exit w/change
			IF updwn% = 60 THEN GOTO gscontract
			IF a$ = "/" OR a$ = "." THEN
					LSET cus.industrialcde$ = a$: a = 0
					ELSE
					LSET cus.industrialcde$ = a$:
					a% = ASC(cus.industrialcde$) - 46:
					IF a% < 1 OR a% > 80 THEN CALL sndmsg("C:M A R G I N   I N V A L I D"): GOTO gsindustrial
					a = mm(a%):
					END IF
			LOCATE 14, 38: PRINT USING "###.##"; a;
			CALL sndmsg("")
		END IF

gsdm:            '***** Distributor margin
	IF UCASE$(cus.stype$) = "A" THEN
		 a$ = cus.sdist$:
		 LOCATE 14, 45: CALL inpnew(a$, 101!, updwn%, "13,59-60")
		 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
		 IF updwn% = 60 THEN GOTO gsindustrial
		 IF a$ = "/" OR a$ = "." THEN
			LSET cus.sdist$ = a$: b = 0
		 ELSE
			LSET cus.sdist$ = a$:
			a% = ASC(cus.sdist$) - 46:
			IF a% < 1 OR a% > 80 THEN CALL sndmsg("C:M A R G I N    I N V A L I D"): GOTO gsdm
			b = mm(a%):
		 END IF
		 LOCATE 14, 46: PRINT USING "###.##"; b;
		 CALL sndmsg("")
	END IF
gscm1:            '***** Contract margin 1
	IF UCASE$(cus.stype$) = "A" THEN
		 a$ = cus.scont1$:
		 LOCATE 14, 53: CALL inpnew(a$, 101!, updwn%, "13,59-60")
		 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
		 IF updwn% = 60 THEN GOTO gsdm
		 IF a$ = "" OR a$ = "/" THEN
			LSET cus.scont1$ = a$: c = 0
		 ELSE
			LSET cus.scont1$ = a$:
			a% = ASC(cus.scont1$) - 46:
					IF a% < 1 OR a% > 80 THEN CALL sndmsg("C:M A R G I N   I N V A L I D"): GOTO gscm1
			c = mm(a%):
		 END IF
		 LOCATE 14, 54: PRINT USING "###.##"; c;
		 CALL sndmsg("")
	END IF
gscm2:            '***** Contract margin 2
	IF UCASE$(cus.stype$) = "A" THEN
		 a$ = cus.scont2$:
		 LOCATE 14, 61: CALL inpnew(a$, 101!, updwn%, "13,59-60")
		 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
		 IF updwn% = 60 THEN GOTO gscm1
		 IF a$ = "" OR a$ = "/" THEN
			LSET cus.scont2$ = a$: d = 0
		 ELSE
			LSET cus.scont2$ = a$:
			a% = ASC(cus.scont2$) - 46:
					IF a% < 1 OR a% > 80 THEN CALL sndmsg("C:M A R G I N   I N V A L I D"): GOTO gscm2
			d = mm(a%):
		 END IF
		 LOCATE 14, 62: PRINT USING "###.##"; d;
		 CALL sndmsg("")
	END IF
	 ELSE       '***** IF DB.OR.CR = "db" DO THIS BELOW
gsc2:           '***** Charge to
	IF UCASE$(cus.stype$) = "Z" THEN
		 a$ = chargto$:
		 LOCATE 14, 27: CALL inpnew(a$, 105!, updwn%, "13,59-60")
		 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
		 IF updwn% = 60 THEN GOTO gsfpn
		 IF LEN(a$) <> 0 AND a$ <> chargto$ THEN
		'***** Edit account code, Search key of account number for bill
			keyin$ = a$
		 CALL searchindex(keyin$, chi%, found%)
			IF NOT found% THEN LOCATE 12, 25: COLOR 14: PRINT "Account not found. Try again": COLOR 2: GOTO gsc2
		 END IF
		 LSET cus.scont1$ = RIGHT$(a$, 1)
		 LSET cus.account$ = a$:
		 chargto$ = a$
		 LOCATE 14, 25: PRINT CHR$(FNE)
	ELSEIF updwn% = 60 THEN
		 GOTO gsfpn
	END IF
gsac:           '***** Agents code
	 END IF
gswhole:            '***** wholesale margin
	IF UCASE$(cus.stype$) = "A" THEN
		 a$ = cus.wholesalecde$:
		 LOCATE 14, 69: CALL inpnew(a$, 101!, updwn%, "13,59-60")
		 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
		 IF updwn% = 60 THEN GOTO gscm2
		 IF a$ = "/" THEN
			LSET cus.wholesalecde$ = a$: b = 0
		 ELSE
			LSET cus.wholesalecde$ = a$:
			a% = ASC(cus.wholesalecde$) - 46:
			IF a% < 1 OR a% > 80 THEN CALL sndmsg("C:M A R G I N    I N V A L I D"): GOTO gsdm
			b = mm(a%):
		 END IF
		 LOCATE 14, 70: PRINT USING "###.##"; b;
		 CALL sndmsg("")
	END IF

gsmd:           '***** Maximum days
	 daysmax% = CVI(cus.daysmax$)

	 a$ = MID$(STR$(daysmax%), 2):
	 IF a$ = "0" THEN LOCATE 19, 15: PRINT "      "
	 COLOR 12: LOCATE 19, 18: PRINT "Days.": COLOR 2
	 LOCATE 19, 15: CALL inpnew(a$, 103!, updwn%, "13,59-60")
	 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 IF updwn% <> 13 THEN
	IF updwn% = 60 AND DB.OR.CR$ = "DB" THEN
		 GOTO gwww
	ELSEIF (updwn% = 60 AND DB.OR.CR$ = "CR") AND UCASE$(cus.stype$) = "A" THEN
		 GOTO gswhole
	ELSE 'IF UPDWN% = 60 THEN
		 GOTO gwww
	END IF
	 END IF
	 LSET cus.daysmax$ = a$: a% = VAL(cus.daysmax$)
	 LOCATE 19, 18: PRINT "Days.";
	 LSET cus.daysmax$ = MKI$(a%):
gsdot:            '***** % Discount of terms
	 sterms = CVS(cus.sterms$)
	 a$ = MID$(STR$(CVS(cus.sterms$)), 2):
				 LOCATE 19, 48: CALL inpnew(a$, 4.2, updwn%, "13,59-60")
	 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 IF updwn% = 60 THEN GOTO gsmd
	 LSET cus.sterms$ = MKS$(VAL(a$))
		'***** Credit limit
	 climit! = CVS(cus.climit$):
	 a$ = MID$(STR$(climit!), 2):
	 LOCATE 19, 63: CALL inpnew(a$, 6!, updwn%, "13,59-60")
	 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 IF updwn% = 60 THEN GOTO gsdot
	 b1$ = "      ": LSET b1$ = a$: b1 = VAL(b1$)
	 IF LEN(a$) > 0 THEN LSET cus.climit$ = MKS$(b1): climit! = b1:
	 IF sno% >= 1 AND sno% <= 26 THEN LSET cus.climit$ = MKS$(-4)
gsbo:
	 a$ = cus.BO
	 COLOR 2, 0
	 IF a$ <> "Y" AND a$ <> "N" THEN a$ = "Y"
	 LOCATE 19, 75: CALL inpnew(a$, 101!, updwn%, "13,59-60")
	 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 IF updwn% = 60 THEN GOTO gsdot
	 cus.BO = a$

gsbankcde:
	 a$ = cus.bankcde$
	 COLOR 2, 0
	 LOCATE 20, 15: CALL inpnew(a$, 103!, updwn%, "13,59-60")
	 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 IF updwn% = 60 THEN GOTO gsdot
	 cus.bankcde = a$

gsbankacct:
	 a$ = cus.bankacct$
	 COLOR 2, 0
	 LOCATE 20, 19: CALL inpnew(a$, 116!, updwn%, "13,59-60")
	 IF updwn% = 59 THEN GOTO gssave        '***** Exit w/change
	 IF updwn% = 60 THEN GOTO gsdot
	 cus.bankacct = a$


gssave:
	'>>- Just before the record is written check the search code.
	 new.search$ = cus.search$ + cus.stype$
	 IF new.search$ <> init.search$ THEN
		CALL change.ordsup(init.search$, new.search$)
		END IF

	 wrkd$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
	 LSET cus.sdate$ = FNDY$(wrkd$)
	 PUT #ch%, rec%, cus
	 CALL export(rec%)
x.change:
END SUB

SUB change.ordsup (init.search$, new.search$)
	msg$ = ""

	'>- Change order file
	chkrec% = 1
	GET #48, chkrec%, ordhed
	DO WHILE NOT EOF(48)
		IF CVI(ordhed.hord$) = chkrec% AND ordhed.hsup$ = init.search$ THEN
		ordhed.hsup$ = new.search$
		PUT #48, chkrec%, ordhed
		msg$ = init.search$ + " orders have been changed to " + new.search$
		END IF

	GET #48, , ordhed: chkrec% = chkrec% + 1
	LOOP


	CALL sndmsg(msg$): msg$ = ""

END SUB

SUB copy.rec.to (rec%, updwn%, DB.OR.CR$, ask.del$)

IF 1 = 0 THEN
	rec% = 1
	GET #ch%, rec%, cus
	DO WHILE NOT EOF(ch%)
		'PRINT cus.sname$;
		' PRINT "|"; MID$(cus.sphone$, 1);
		' PRINT "|"; MID$(cus.sphone1$, 1)
		 ok% = 0
		 IF MID$(cus.sphone$, 1, 3) = " 03" THEN MID$(cus.sphone$, 1, 3) = "039": ok% = -1
		 IF MID$(cus.sphone1$, 1, 3) = " 03" THEN MID$(cus.sphone1$, 1, 3) = "039": ok% = -1
		 IF cus.rep$ <= " " THEN cus.rep$ = "U": ok% = -1
		 IF cus.callfreq$ <= " " THEN cus.callfreq$ = "U": ok% = -1
		 IF CVS(cus.climit$) < 100 THEN LSET cus.climit$ = MKS$(10): ok% = -1
		 IF ok% THEN PUT #ch%, rec%, cus
		 IF rec% MOD 100 = 0 THEN LOCATE 10, 10: PRINT rec%

		' x$ = INPUT$(1)
		GET #ch%, , cus: rec% = rec% + 1
		LOOP
	GOTO x.copy.rec.to
	END IF

		maxwho% = 9999
		IF rec% < 1 OR rec% > maxwho% THEN updwn% = 59: GOTO x.copy.rec.to

		SELECT CASE DB.OR.CR$
		CASE "CR": chi% = 45: ch% = 44: apgm$ = "CSMENU"
		CASE "DB": chi% = 23: ch% = 43: apgm$ = "DSMENU"
		CASE "--": chi% = 65: ch% = 64: apgm$ = "DSMENU"
		CASE ELSE
		END SELECT

		CALL sndmsg(SPACE$(60))
		DO
		COLOR 2, 0
		SELECT CASE DB.OR.CR$
		CASE "CR": LOCATE 24, 15: PRINT "Copy to Lead file or Debtors   (L,D)..>"; : a$ = "L"
		CASE "DB": LOCATE 24, 15: PRINT "Copy to Lead file or Creditors (L,C)..>"; : a$ = "L"
		CASE "--": LOCATE 24, 15: PRINT "Copy to Creditors or Debtors   (C,D)..>"; : a$ = " "
		CASE ELSE
		END SELECT

		LOCATE 24, 54
		IF ask.del$ = "Y" THEN
			CALL inpnew(a$, 101!, updwn%, "13,59-60")
			ELSE
			a$ = "L"
			updwn% = 13
			ask.del$ = "Y"
			END IF
		IF updwn% = 59 THEN GOTO x.copy.rec.to
		IF updwn% = 60 THEN GOTO x.copy.rec.to
		a$ = UCASE$(a$)
		ok% = 0
		SELECT CASE DB.OR.CR$
		CASE "CR": IF a$ = "L" OR a$ = "D" THEN ok% = -1
		CASE "DB": IF a$ = "L" OR a$ = "C" THEN ok% = -1
		CASE "--": IF a$ = "C" OR a$ = "D" THEN ok% = -1
		CASE ELSE
		END SELECT

		LOOP UNTIL ok%



		SELECT CASE a$
		CASE "D": cto% = 43
		CASE "C": cto% = 44
		CASE "L": cto% = 64
		CASE ELSE
		END SELECT


		new.rec% = 0
		found% = 0
		errmsg$ = ""
		sav.search$ = cus.search$ + cus.stype$
		rec.cto% = 1
		GET #cto%, rec.cto%, cus
		DO WHILE NOT EOF(cto%)
			IF CVI(cus.sno$) = rec.cto% AND cus.search$ + cus.stype$ = sav.search$ THEN
				errmsg$ = "Search code of " + cus.search$ + cus.stype$ + " already exist in target file"
				EXIT DO
				END IF
			IF CVI(cus.sno$) <> rec.cto% AND new.rec% = 0 THEN new.rec% = rec.cto%: found% = -1
			GET #cto%, , cus: rec.cto% = rec.cto% + 1
			LOOP

		IF EOF(cto%) AND NOT found% THEN new.rec% = rec.cto%

		IF errmsg$ = "" THEN
		IF new.rec% < 1 OR new.rec% > maxwho% THEN
			errmsg$ = "No room left in the target file"
			END IF
			END IF

		IF errmsg$ <> "" THEN
			CALL sndmsg(errmsg$)
			updwn% = 59
			GOTO x.copy.rec.to
			END IF

		'>- Move the bastard -<
		GET #ch%, rec%, cus
		cus.sno$ = MKI$(new.rec%)
		PUT #cto%, new.rec%, cus

		SELECT CASE cto%
		CASE 43: msg$ = "This record was copied to record" + STR$(new.rec%) + " in the Debtors file"
		CASE 44: msg$ = "This record was copied to record" + STR$(new.rec%) + " in the Creditors file"
		CASE 64: msg$ = "This record was copied to record" + STR$(new.rec%) + " in the leads file"
		CASE ELSE
		END SELECT

		CALL sndmsg(msg$)
		updwn% = 13

x.copy.rec.to:
END SUB

SUB do.delete (rec%, updwn%, ask.del$)
'//////////////////////////////////////////
'>>>>> D E L E T E   R E C O R D S
'//////////////////////////////////////////
do.delete:
	IF rec% < 1 OR rec% > maxwho% THEN RETURN
	keyin$ = cus.search$ + cus.stype$
	found% = 0
	rec8% = 1
	GET #8, rec8%, Audit
	DO WHILE NOT EOF(8) AND cus.Active$ <> "I"
		IF keyin$ = Audit.adcust$ THEN found% = -1: EXIT DO
		IF rec8% MOD 100 = 0 THEN CALL sndmsg("Checking audit file.    Record:" + STR$(rec8%))
		IF INKEY$ = CHR$(0) + CHR$(59) THEN found% = -1: EXIT DO
		GET #8, , Audit: rec8% = rec8% + 1
		LOOP

	IF found% THEN
		SOUND 900, 20: SOUND 800, 20: SOUND 300, 20
		CALL sndmsg("This customer exist on the audit trail.")
		IF ask.del$ = "N" THEN GOTO 5010

		COLOR 2, 0: LOCATE 1, 1
		LOCATE 25, 1: PRINT SPACE$(80);
		LOCATE 25, 4: PRINT "F1-Exit";
		CALL inpnew(a$, 0!, updwn%, "13,27,59,68")
		IF updwn% <> 68 THEN 5010   '***** Exit no delete
		END IF


	IF ask.del$ <> "N" THEN
		 COLOR 14: LOCATE 4, 25: PRINT "Deletion pending";
		COLOR 0, 3: LOCATE 25, 2: PRINT SPACE$(76);
		LOCATE 25, 1: PRINT SPACE$(80);
		LOCATE 25, 4: PRINT "F1-Exit"; : LOCATE 25, 60: PRINT "F10-Delete";
		COLOR 2, 0: LOCATE 1, 1
		CALL inpnew(a$, 0!, updwn%, "13,27,59,68")
		IF updwn% <> 68 THEN 5010   '***** Exit no delete
		END IF


	ask.del$ = "Y"
	OPEN "DELETE.LOG" FOR APPEND AS #98
	PRINT #98, "Deleting:" + cus.search$ + cus.stype$ + "," + cus.sname + "," + DATE$ + " " + TIME$
	CLOSE #98

	'>>>>> Reals
	 LSET cus.s0$ = MKS$(0):     LSET cus.scur$ = MKS$(0)
	 LSET cus.s30$ = MKS$(0):    LSET cus.s60$ = MKS$(0)
	 LSET s90$ = MKS$(0):    LSET cus.sterms$ = MKS$(0)
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


		PUT #ch%, rec%, cus


5010 '***** End of delete main file
	 COLOR 2, 0
	 LOCATE 4, 25: PRINT CHR$(FNE)

END SUB

SUB dsply (rec%, DB.OR.CR$, dpage%)
'///////////////////////////////////////////////////////////////////////////
'>>>>>  record and display
'///////////////////////////////////////////////////////////////////////////
spcontact$ = SPACE$(30): spphone$ = SPACE$(15): spdepph$ = SPACE$(15)
spuaddr$ = SPACE$(30): spusub$ = SPACE$(30)
spname.dsply$ = SPACE$(30)

dsply: '
		IF rec% < 1 OR rec% > maxwho% THEN
		COLOR 14: LOCATE 4, 25: PRINT "Not found on file.": COLOR 2
		rec% = -1
		GOTO X.DSPLY
		ELSE
		LOCATE 4, 25: PRINT CHR$(FNE)
		END IF

		GET #ch%, rec%, cus

	 sno% = CVI(cus.sno$)
	 scur = CVS(cus.scur$): s30 = CVS(cus.s30$): s60 = CVS(cus.s60$): s90 = CVS(cus.s90$)
	 climit! = CVS(cus.climit$): chargto$ = SPACE$(5): chargto$ = cus.account$ + cus.scont1$
	 sterms! = CVS(cus.sterms$): daysmax% = CVI(cus.daysmax$)
	 cusvalue = CVS(cus.advalue$)

	 a = 0: b = 0: c = 0: d = 0: e = 0: f = 0: g = 0: h = 0: i = 0
	 a% = ASC(cus.sret$) - 46: IF a% >= 1 AND a% <= 80 THEN a = mm(a%)
	 a% = ASC(cus.countercde$) - 46: IF a% >= 1 AND a% <= 80 THEN b = mm(a%)
	 a% = ASC(cus.tradecde$) - 46: IF a% >= 1 AND a% <= 80 THEN c = mm(a%)
	 a% = ASC(cus.contractcde$) - 46: IF a% >= 1 AND a% <= 80 THEN d = mm(a%)
	 a% = ASC(cus.industrialcde$) - 46: IF a% >= 1 AND a% <= 80 THEN e = mm(a%)
	 a% = ASC(cus.sdist$) - 46: IF a% >= 1 AND a% <= 80 THEN f = mm(a%)
	 a% = ASC(cus.scont1$) - 46: IF a% >= 1 AND a% <= 80 THEN g = mm(a%)
	 a% = ASC(cus.scont2$) - 46: IF a% >= 1 AND a% <= 80 THEN h = mm(a%)
	 a% = ASC(cus.wholesalecde$) - 46: IF a% >= 1 AND a% <= 80 THEN i = mm(a%)

	 j% = 0
	 a$ = SPACE$(25)
	 FOR i% = 1 TO 26
		IF cus.stype$ = type$(i%) THEN j% = i%: i% = 9999
	 NEXT
	 '***** the pickup address off pickup file
		sprec% = VAL(MID$(cus.spname$, 1, 3))
	 IF sprec% >= 1 AND sprec% <= 999 THEN
		GET #50, sprec%, pickup
		LSET spcontact$ = pickup.pname1$
		LSET spphone$ = pickup.pphone1$
		LSET spdepph$ = pickup.pphone2$
		LSET spname.dsply$ = pickup.pname2$
		LSET spuaddr$ = pickup.pname3$
		LSET spusub$ = pickup.pname4$
		ELSE
		LSET spcontact$ = SPACE$(30)
		LSET spphone$ = SPACE$(30)
		LSET spdepph$ = SPACE$(30)
		LSET spname.dsply$ = cus.spname$
		LSET spuaddr$ = SPACE$(30)
		LSET spusub$ = SPACE$(30)
		END IF
	 IF j% = 0 OR j% > 26 THEN
		a$ = "** UNKNOWN **"
		ELSE
		GET #42, j%, types: LSET a$ = types.dfdesc$
		END IF


	 '***** Do the headings
	 COLOR 12
	 LOCATE 3, 44: PRINT "Type.>";
	 LOCATE 4, 5: PRINT "Name.....>";
	 LOCATE 4, 72: PRINT "G/L.";
	 LOCATE 5, 5: PRINT "Address..>";
	 LOCATE 6, 5: PRINT "      2..>";
	 LOCATE 7, 5: PRINT "Suburb...>";
	 LOCATE 7, 37: PRINT "P/code..>"
	 LOCATE 4, 61: PRINT "P/up..>";
	 LOCATE 8, 5: PRINT "PO Box...>";
	 LOCATE 8, 23: PRINT "Suburb..>";
	 LOCATE 8, 54: PRINT "P/code..>"
	 IF DB.OR.CR$ = "CR" THEN LOCATE 2, 60: PRINT "G.S.T.";
	 LOCATE 9, 5: PRINT "Contact..:";
	 IF DB.OR.CR$ = "DB" THEN LOCATE 5, 51: PRINT "Rep..>";
	 IF DB.OR.CR$ = "CR" THEN LOCATE 5, 51: PRINT "Qual.>";
	 IF DB.OR.CR$ = "--" THEN LOCATE 5, 51: PRINT "Stat.>";
	 IF DB.OR.CR$ = "DB" THEN LOCATE 6, 51: PRINT "Freq.>";
	 IF DB.OR.CR$ = "CR" THEN LOCATE 6, 51: PRINT "Freq.>";
	 IF DB.OR.CR$ = "--" THEN LOCATE 6, 51: PRINT "Freq.>";

	 LOCATE 10, 5: PRINT "Telephone.";
	 LOCATE 10, 31: PRINT "Fax.";
	 LOCATE 10, 51: PRINT "Mobile.";
	 LOCATE 10, 72: PRINT "Int.";
	 LOCATE 11, 2: PRINT CHR$(FNE);
	 LOCATE 11, 5: PRINT "Website..>";
	 LOCATE 12, 5: PRINT "e-mail...:"
	 '***** Fields for the headings
	 sr$ = cus.search$
	 IF cus.search$ = "    " OR cus.search$ = null4$ THEN
		sr$ = "No search key found."
		COLOR 14
		LOCATE 3, 15: PRINT sno%; "           ";
		LOCATE 4, 30: PRINT sr$;
		ELSE
		COLOR 2
		LOCATE 3, 15: PRINT sno%; "  ";
		LOCATE 3, 31: PRINT sr$;
		END IF

	 LOCATE 3, 50: PRINT cus.stype$; " "; a$;
	 LOCATE 3, 3: PRINT FNDYY$(cus.sdate$); " "; cus.Active$
	 LOCATE 4, 15: PRINT cus.sname$;
	 LOCATE 4, 75: PRINT USING "#####"; CVS(cus.sgl$);
	 LOCATE 5, 15: PRINT cus.saddr$;
	 LOCATE 6, 15: PRINT cus.saddr2$;
	 LOCATE 7, 15: PRINT cus.suburb$
	 LOCATE 7, 46: PRINT cus.spcode$;
	 LOCATE 4, 68: PRINT USING "###"; VAL(cus.spname$);
	 LOCATE 8, 15: PRINT cus.spbox$;
	 LOCATE 8, 32: PRINT cus.spboxsub$;
	 LOCATE 8, 63: PRINT cus.spboxpcode$;
	 LOCATE 2, 66: PRINT cus.taxe$
	 LOCATE 9, 15: PRINT cus.scont$;
	 LOCATE 5, 58: PRINT USING "! \                  \"; cus.rep$; repcode$(cus.rep$, DB.OR.CR$)
	 LOCATE 6, 58: PRINT USING "! \                  \"; cus.callfreq$; freqcode$(cus.callfreq$)
	 LOCATE 10, 16: PRINT USING "\           \"; cus.sphone$
	 LOCATE 10, 36: PRINT USING "\           \"; cus.sphone1$
	 LOCATE 10, 59: PRINT USING "\           \"; cus.ContactMobile$(1)



	 LOCATE 10, 77: PRINT USING "\ \"; cus.pstnCC$
	 LOCATE 11, 15: PRINT cus.www$
	 LOCATE 12, 15: PRINT cus.email$

		IF DB.OR.CR$ = "DB" THEN
		IF UCASE$(cus.stype$) = "Z" THEN
			LOCATE 12, 27: PRINT chargto$;
			END IF
		END IF

CALL BOX(2, 13, 79, 23, 1, 0, 0)

IF dpage% = 1 THEN
	 COLOR 12

	 LOCATE 15, 5: PRINT "Transport>";
	 LOCATE 15, 57: PRINT "Phone.";
	 LOCATE 16, 5: PRINT "Depot....>"
	 LOCATE 16, 57: PRINT "Phone.";
	 LOCATE 17, 5: PRINT "Address..>";
	 LOCATE 18, 5: PRINT "Suburb...>";

	 COLOR 2
	 LOCATE 15, 15: PRINT spcontact$;
	 LOCATE 15, 64: PRINT spphone$:
	 LOCATE 16, 64: PRINT spdepph$:
	 LOCATE 16, 15: PRINT spname.dsply$;
	 LOCATE 17, 15: PRINT spuaddr$;
	 LOCATE 18, 15: PRINT spusub$;

	 IF DB.OR.CR$ = "CR" THEN

	IF UCASE$(cus.stype$) = "A" THEN
		COLOR 12, 0
		LOCATE 13, 2: PRINT USING "   Retail. Counter Trade.. C/tract Indust. Distr.. Disc-1. Disc-2. W/Sale.!"; " "
		COLOR 2, 0
		LOCATE 14, 2: PRINT USING "   !###.## !###.## !###.## !###.## !###.## !###.## !###.## !###.## !###.##"; cus.sret$; a; cus.countercde$; b; cus.tradecde$; c; cus.contractcde$; d; cus.industrialcde$; e; cus.sdist$; f; cus.scont1$; g; cus.scont2$; h _
; cus.wholesalecde$; i
		ELSE
		LOCATE 13, 2: PRINT SPACE$(78)
		LOCATE 14, 2: PRINT SPACE$(78)
		END IF
	END IF

	IF DB.OR.CR$ = "DB" THEN
		IF UCASE$(cus.stype$) = "Z" THEN
		LOCATE 10, 6: PRINT "Charge to..........>";
		LOCATE 10, 41: PRINT "Agent code.........>";
		END IF
	 END IF

	 COLOR 12
	 LOCATE 19, 2: PRINT SPACE$(78)
	 LOCATE 20, 2: PRINT SPACE$(78)
	 LOCATE 21, 2: PRINT SPACE$(78)
	 LOCATE 22, 2: PRINT SPACE$(78)
	 LOCATE 19, 5: PRINT "Terms....>";
	 LOCATE 19, 18: PRINT "Days.";
	 LOCATE 19, 27: PRINT "Settlement ";
	 LOCATE 19, 50: PRINT "Limit ";
	 LOCATE 20, 5: PRINT "Bank Det.>";
	 LOCATE 20, 37: PRINT "L/pay..:";
	 LOCATE 19, 70: PRINT "B/O.>";

	 COLOR 2
	 LOCATE 19, 15: PRINT daysmax%
	 LOCATE 19, 38: PRINT USING "##.##%"; sterms;
	 LOCATE 19, 55: PRINT USING " &"; funclimit(climit!)
	 LOCATE 20, 15: PRINT cus.bankcde
	 LOCATE 20, 19: PRINT cus.bankacct
	 LOCATE 20, 45: PRINT USING "$$##,###.##   \      \  \       \"; cusvalue; FNDYY$(cus.addate$); cus.addocnum$
	 COLOR 12
				 LOCATE 22, 3: PRINT " P/Level   90+ days     60 Days     30 Days     Current        Total";
	 Total = scur + s30 + s60 + s90
	 COLOR 7
	 LOCATE 23, 3: PRINT USING " ###.##%$$##,###.## $$##,###.## $$##,###.##$$###,###.## $$###,###.##"; cus.slevel; s90; s60; s30; scur; Total
	 COLOR 2, 0
	 LOCATE 19, 75: PRINT cus.BO$



END IF


IF dpage% = 2 THEN
	 COLOR 12
	 LOCATE 19, 2: PRINT SPACE$(78)
	 LOCATE 20, 2: PRINT SPACE$(78)
	 LOCATE 21, 2: PRINT SPACE$(78)
	 LOCATE 22, 2: PRINT SPACE$(78)
	 LOCATE 19, 5: PRINT "Trading terms......>";
	 LOCATE 19, 18: PRINT "Days.";
	 LOCATE 19, 27: PRINT "Settlement ";
	 LOCATE 19, 50: PRINT "Limit ";
	 LOCATE 20, 45: PRINT "Last payment:";

	 COLOR 2
	 LOCATE 19, 15: PRINT daysmax%
	 LOCATE 19, 38: PRINT USING "##.##%"; sterms;
	 LOCATE 19, 55: PRINT USING " &"; funclimit(climit!)
	 LOCATE 20, 45: PRINT USING "$$##,###.##   \      \  \       \"; cusvalue; FNDYY$(cus.addate$); cus.addocnum$
	 COLOR 12
	 LOCATE 21, 3: PRINT "              90+ days     60 Days     30 Days     Current        Total";
	 Total = scur + s30 + s60 + s90
	 COLOR 7
	 'LOCATE 22, 3: PRINT USING "           $$##,###.## $$##,###.## $$##,###.## $$##,###.##  $$##,###.##"; s90; s60; s30; scur; Total
	 LOCATE 22, 3: PRINT USING "           $$##,###.## $$##,###.## $$##,###.##$$###,###.## $$###,###.##"; s90; s60; s30; scur; Total

	 COLOR 12
	 LOCATE 11, 2: PRINT " Contact/email-------------------------Title/Fax------------Phone/Mobile------"

	 COLOR 2
	 FOR i% = 1 TO 6
	 LOCATE 11 + i% * 2 - 1, 2: PRINT USING " & & & &"; cus.ContactFirstName$(i%); cus.ContactSurName$(i%); cus.ContactTitle(i%); cus.ContactPhone$(i%);
	 LOCATE 11 + i% * 2 - 0, 2: PRINT USING " & &   &"; LEFT$(cus.Contactemail$(i%), 37); cus.ContactFax$(i%); cus.ContactMobile$(i%);
	 NEXT

	 COLOR 12
	 FOR i% = 1 TO 6
	 LOCATE 11 + i% * 2 - 1, 40: PRINT "|"
	 LOCATE 11 + i% * 2 - 1, 61: PRINT "|"
	 LOCATE 11 + i% * 2 - 0, 40: PRINT "|"
	 LOCATE 11 + i% * 2 - 0, 61: PRINT "|"
	 NEXT


END IF

X.DSPLY:

END SUB

SUB export (rec%)
		GET #ch%, rec%, cus
		ext$ = ".\export\" + cus.search$ + cus.stype$ + ".who"
OPEN ext$ FOR OUTPUT AS #97
			a$ = STR$(CVI(cus.sno$))
			b$ = cus.search$ + cus.stype$
			c$ = cus.sname
			d$ = cus.saddr$
			e$ = cus.saddr2$
			f$ = cus.suburb$
			g$ = cus.state$
			h$ = cus.spcode$
			i$ = cus.spbox$
			j$ = cus.spboxsub$
			k$ = cus.spboxpcode$
			l = CVS(cus.sgl$)
			m$ = cus.email$
			n$ = cus.www$
			o$ = cus.pstnCC$
			p$ = cus.scontTitle$
			q$ = cus.scont$
			r$ = cus.sphone$
			s$ = cus.sphone1$
			t$ = cus.taxe$
			u$ = cus.rep$
			v$ = cus.callfreq$
			w$ = cus.sdays$
			X$ = STR$(CVS(cus.sterms))
			y$ = cus.daysmax$

			aa$ = STR$(CVS(cus.scur$))
			ab$ = STR$(CVS(cus.s0$))
			ac$ = STR$(CVS(cus.s30$))
			ad$ = STR$(CVS(cus.s60$))
			ae$ = STR$(CVS(cus.s90$))
			af$ = STR$(CVS(cus.opn$))
			ag$ = STR$(CVS(cus.opn30$))
			ah$ = STR$(CVS(cus.opn60$))
			ak$ = STR$(CVS(cus.advalue$))
			al$ = STR$(CVS(cus.climit$))

			'Pickup info
			ba$ = cus.spnum$
			bb$ = cus.spname$
			bc$ = cus.spsub$

			'Invoice groups
			ca$ = cus.sdist$
			cb$ = cus.sret$
			cc$ = cus.countercde$
			cd$ = cus.tradecde$
			ce$ = cus.contractcde$
			cf$ = cus.industrialcde$
			cg$ = cus.scont1$
			ch$ = cus.scont2$
			ci$ = cus.wholesalecde$

			'Audit trail
			da$ = cus.addocnum$
			DB$ = cus.addate$

			dc$ = cus.sdate$
			dd$ = cus.Active$

			'Personal details
			FOR i% = 1 TO 6
				ea$(i%) = cus.ContactFirstName$(i%)
				eb$(i%) = cus.ContactSurName$(i%)
				ec$(i%) = cus.ContactTitle$(i%)
				ed$(i%) = cus.ContactPhone$(i%)
				ee$(i%) = cus.ContactMobile$(i%)
				ef$(i%) = cus.ContactFax$(i%)
				eg$(i%) = cus.Contactemail$(i%)
			NEXT i%

			fa$ = cus.BO$
			fb$ = cus.abn$
			fc$ = cus.bankcde$
			fd$ = cus.bankacct$
			'fe$ = STR$(cus.myob)
			'ff$ = cus.cardid$

			'***** the pickup address off pickup file
			sprec% = VAL(MID$(cus.spname$, 1, 3))
			IF sprec% >= 1 AND sprec% <= 999 THEN
				GET #50, sprec%, pickup
				ga$ = pickup.pno$
				gb$ = pickup.pname1$
				gc$ = pickup.pname2$
				gd$ = pickup.pname3$
				ge$ = pickup.pname4$
				gf$ = pickup.pactive$
				gg$ = pickup.pphone1$
				gh$ = pickup.pphone2$
			ELSE
				ga$ = ""
				gb$ = ""
				gc$ = ""
				gd$ = ""
				ge$ = ""
				gf$ = ""
				gg$ = ""
				gh$ = ""
			END IF

			gi$ = DATE$ + " " + TIME$

	WRITE #97, "L1", ch%, a$, b$, c$, d$, e$, f$, g$, h$, i$, j$, k$, l, m$, n$, o$, p$, q$, r$, s$, t$, u$, v$, X$, y$, aa$, ab$, ac$, ad$, ae$, af$, ag$, ai$, aj$, ak$, al$, ba$, bb$, bc$, ca$, cb$, cd$, ce$, cf$, cg$, ci$, da$, DB$, dc$, dd$, fa$,  _
fb$
	WRITE #97, "L2", fc$, fd$, ea$(1), eb$(1), ec$(1), ed$(1), ee$(1), ef$(1), eg$(1), ea$(2), eb$(2), ec$(2), ed$(2), ee$(2), ef$, ea$(3), eb$(3), ec$(3), ed$(3), ee$(3), ef$(3), eg$(3), ea$(4), eb$(4), ec$(4), ed$(4), ee$(4), ef$(4), eg$(4)
	WRITE #97, "L3", ga$, gb$, gc$, gd$, ge$, gf$, gg$, gh$, gi$
	CLOSE #97

END SUB

FUNCTION freqcode$ (in$)

	SELECT CASE in$
	CASE "W": wrk$ = "****** WEEKLY ******"
	CASE "M": wrk$ = "***** MONTHLY. *****"
	CASE "S": wrk$ = "**** SIX WEEKLY ****"
	CASE "Q": wrk$ = "**** QUARTERLY. ****"
	CASE "H": wrk$ = "*** HALF YEARLY. ***"
	CASE "A": wrk$ = "***** ANNUALLY *****"
	CASE "T": wrk$ = "**** TELEPHONE. ****"
	CASE "U": wrk$ = "***** UNKNOWN. *****"
	CASE "N": wrk$ = "****** NEVER. ******"
	CASE ELSE
	END SELECT

	freqcode$ = wrk$

END FUNCTION

FUNCTION funclimit$ (climit!)
	wrk$ = "     "
	climit$ = STR$(climit!)
	LSET wrk$ = climit$
	IF climit! = 0 THEN wrk$ = "C.O.D. ONLY  "
	IF climit! = -1 THEN wrk$ = "Invoice value"
	IF climit! = -2 THEN wrk$ = "Invoice plus "
	IF climit! = -3 THEN wrk$ = "Bank Cheque  "
	IF climit! = -4 THEN wrk$ = "Counter Sales"
	funclimit$ = wrk$
END FUNCTION

SUB getphone (phone$, updwn%)
	'Phone number format  '064 aaa-11112222'
	'Phone number format  '064-aaa-1111-2222'..................ajd
	'                      123456789 123456789 '
	FOR i% = 1 TO 20
		IF MID$(phone$, i%, 1) < "0" THEN MID$(phone$, i%, 1) = " "
		IF MID$(phone$, i%, 1) > "9" THEN MID$(phone$, i%, 1) = " "
		NEXT
	country$ = MID$(phone$, 1, 3)
	area$ = MID$(phone$, 5, 3)
	'dial8$ = MID$(phone$, 9, 8)
	dial8$ = MID$(phone$, 9, 9)
	Y0% = CSRLIN: X0% = POS(1)

cfgp1a:
	updwn% = 13

	 ' LOCATE Y0%, X0%: PRINT USING "\ \ \ \-\      \"; country$; area$; dial8$
	LOCATE Y0%, X0%: PRINT USING "\ \ \ \-\       \"; country$; area$; dial8$'.................ajd

cfgp1:
	IF country$ = "   " AND updwn% <> 60 THEN GOTO cfgp2
	LOCATE Y0%, X0%
				CALL inpnew(country$, 3!, updwn%, "13,59,60")
	country$ = "   " + country$: country$ = RIGHT$(country$, 3)
	IF updwn% = 59 THEN GOTO xgetphone
	IF updwn% = 60 THEN GOTO xgetphone
cfgp2:
	IF area$ = "   " AND updwn% <> 60 THEN GOTO cfgp8
	LOCATE Y0%, X0% + 4
				CALL inpnew(area$, 3!, updwn%, "13,59,60")
	area$ = "   " + area$: area$ = RIGHT$(area$, 3)
	IF updwn% = 59 THEN GOTO xgetphone
	IF updwn% = 60 THEN GOTO cfgp1
cfgp8:
	LOCATE Y0%, X0% + 8
	CALL inpnew(dial8$, 8, updwn%, "13,59,60")
	IF updwn% = 59 THEN GOTO xgetphone
	IF updwn% = 60 THEN GOTO cfgp2
xgetphone:
	'>> Assemble the phone number
	phone$ = country$ + " " + area$ + "-" + dial8$
	LOCATE Y0%, X0%: PRINT phone$

END SUB

SUB LogicalDelete (rec%, updwn%)
	IF rec% < 1 OR rec% > maxwho% THEN RETURN

	COLOR 14: LOCATE 4, 24: PRINT "Remove from Audit Calculations Pending";
	COLOR 0, 3: LOCATE 25, 2: PRINT SPACE$(76);
	LOCATE 25, 1: PRINT SPACE$(80);
	LOCATE 25, 4: PRINT "F1-Exit"; : LOCATE 25, 40: PRINT "F8-Reinstate Now     F10-Remove Now";
	COLOR 2, 0: LOCATE 1, 1
	CALL inpnew(a$, 0!, updwn%, "59,66,68")
	COLOR 2, 0: LOCATE 4, 24: PRINT "                                      ";
	IF updwn% = 59 THEN GOTO xLogicalDelete


	IF updwn% = 66 THEN upd$ = "A"
	IF updwn% = 68 THEN upd$ = "*"


	GET #ch%, rec%, cus
	keyin$ = cus.search$ + cus.stype$

	CLOSE #8

	 FOR auditf% = 1 TO naudirec%
	 auditname$ = auditfile$(auditf%)
	 OPEN auditname$ FOR RANDOM SHARED AS #8 LEN = 92



	rec8% = 1
	GET #8, rec8%, Audit
	DO WHILE NOT EOF(8)
		IF keyin$ = Audit.adcust$ THEN
		IF Audit.adactive$ <> upd$ THEN
			LSET Audit.adactive$ = upd$
			PUT #8, rec8%, Audit
		END IF
		END IF
		IF rec8% MOD 100 = 0 THEN CALL sndmsg("Marking audit file " + auditname$ + "    Record:" + STR$(rec8%))
		IF INKEY$ = CHR$(0) + CHR$(59) THEN found% = -1: EXIT DO
		GET #8, , Audit: rec8% = rec8% + 1
		LOOP

	CLOSE #8
	NEXT 'Audit file

	IF upd$ = " " THEN
		CALL sndmsg("Reinstate complete")
	ELSE
		CALL sndmsg("Remove from calculations complete")
	END IF

	'>-Set the status
	GET #ch%, rec%, cus
	cus.Active = upd$
	PUT #ch%, rec%, cus

	 '>- Reopen the file
	 auditname$ = auditfile$(naudirec%)
	 OPEN auditname$ FOR RANDOM SHARED AS #8 LEN = 92

xLogicalDelete:
COLOR 2, 0
END SUB

SUB PCASE (ch1%, ch2%, DB.OR.CR$) STATIC
		DIM raw AS STRING

		SELECT CASE DB.OR.CR$
		CASE "CR": filen$ = "SUPP.TXT"
		CASE "DB": filen$ = "CUST.TXT"
		CASE "--": filen$ = ""
		CASE ELSE
		END SELECT
		IF filen$ = "" THEN EXIT SUB
		IF DIR$(filen$) = "" THEN EXIT SUB

		PCOPY 0, 1
		CALL setup("MYOB Card file to Who File")

		f% = FREEFILE
		OPEN filen$ FOR INPUT SHARED AS #f%
		LINE INPUT #f%, raw$  'Heading
		LINE INPUT #f%, raw$
		DO WHILE NOT EOF(f%)
			X% = INSTR(raw$, ","): name$ = MID$(raw$, 1, X% - 1): raw$ = MID$(raw$, X% + 1)
			X% = INSTR(raw$, ","): tmp2$ = MID$(raw$, 1, X% - 1): raw$ = MID$(raw$, X% + 1)
			X% = INSTR(raw$, ","): scode$ = MID$(raw$, 1, X% - 1)

			name$ = MID$(name$ + SPACE$(35), 1, 35)

			found2% = 0
			keyin$ = scode$
			CALL searchindex(keyin$, chi%, found%)
			IF found% THEN
				rec% = CVI(supx.wrrn$)
				GET #ch%, rec%, cus
				csearch$ = cus.search$ + cus.stype$
			ELSE
				cus.sname$ = ""
				cus.search$ = ""
				cus.stype$ = ""
				csearch$ = ""
			END IF

			COLOR 2, 0
			LOCATE 11, 10: PRINT "MYOB....:"; name$; "<"; CHR$(FNE); scode$
			LOCATE 12, 10: PRINT "Name....:"; cus.sname$; "< "; cus.search$ + cus.stype$
			LOCATE 13, 10: PRINT "Update Record........> "

			IF NOT found% AND scode$ > "" THEN
				rec% = 1
				GET #ch%, rec%, cus
				DO WHILE NOT EOF(ch%)

					tmp$ = LCASE$(name$)
					tmp2$ = ""
					FOR i% = 1 TO LEN(tmp$)
						IF MID$(tmp$, i%, 1) >= "a" AND MID$(tmp$, i%, 1) <= "z" THEN
							tmp2$ = tmp2$ + MID$(tmp$, i%, 1)
						END IF
					NEXT

					tmp$ = LCASE$(cus.sname$)
					tmp3$ = ""
					FOR i% = 1 TO LEN(tmp$)
						IF MID$(tmp$, i%, 1) >= "a" AND MID$(tmp$, i%, 1) <= "z" THEN
							tmp3$ = tmp3$ + MID$(tmp$, i%, 1)
						END IF
					NEXT

					IF tmp2$ = tmp3$ THEN
						COLOR 4, 0
						LOCATE 12, 10: PRINT "Name....:"; cus.sname$; "< "; cus.search$ + cus.stype$
						found% = -1
						found2% = -1
						EXIT DO
					END IF

					GET #ch%, , cus: rec% = rec% + 1
				LOOP

			END IF

			a$ = "N":
			IF found% AND name$ <> cus.sname$ THEN
				a$ = "Y"
			END IF

			IF (a$ = "Y" OR found2%) AND LCASE$(scode$) <> "*none" THEN
				LOCATE 13, 32
																CALL inpnew(a$, 101!, updwn%, "59,60,13")
				IF updwn% = 59 THEN GOTO xpcase
				IF found% AND a$ = "Y" THEN
					GET #ch%, rec%, cus
					cus.sname$ = name$
					cus.search$ = MID$(scode$, 1, 4)
					cus.stype$ = MID$(scode$, 5, 1)
					PUT #ch%, rec%, cus
					SOUND 1000, 1
				END IF
			END IF


			LINE INPUT #f%, raw$
		LOOP

		CLOSE #f

'    rec% = 1
'    GET #ch2%, rec%, who
'    DO WHILE NOT EOF(ch2%)
'
'      '>--Name
'      tmp$ = who.sname
'      tmp$ = LCASE$(RTRIM$(tmp$))
'      IF tmp$ > "" THEN
'        MID$(tmp$, 1, 1) = UCASE$(MID$(tmp$, 1, 1))
'        X% = 0
'        X% = INSTR(X% + 1, tmp$, " ")
'        DO WHILE X% > 0
'          ok% = -1
'          IF MID$(tmp$, X% + 1, 3) = "and" THEN ok% = 0
'          IF MID$(tmp$, X% + 1, 3) = "or" THEN ok% = 0
'          IF ok% THEN
'            MID$(tmp$, X% + 1, 1) = UCASE$(MID$(tmp$, X% + 1, 1))
'          END IF
'          X% = INSTR(X% + 1, tmp$, " ")
'        LOOP
'        DO WHILE RIGHT$(tmp$, 1) = "."
'          tmp$ = MID$(tmp$, 1, LEN(tmp$) - 1)
'        LOOP
'        IF RIGHT$(tmp$, 2) = "St" THEN
'          X% = INSTR(tmp$, " St")
'          MID$(tmp$, X%, 2) = " St": tmp$ = tmp$ + "."
'        END IF
'        IF RIGHT$(tmp$, 2) = "Rd" THEN
'          X% = INSTR(tmp$, " Rd")
'          MID$(tmp$, X%, 4) = " Rd": tmp$ = tmp$ + "."
'        END IF
'
'        who.sname = tmp$
'      END IF
'
'      '>--address
'      tmp$ = who.saddr
'      tmp$ = LCASE$(RTRIM$(tmp$))
'      IF tmp$ > "" THEN
'        MID$(tmp$, 1, 1) = UCASE$(MID$(tmp$, 1, 1))
'        X% = 0
'        X% = INSTR(X% + 1, tmp$, " ")
'        DO WHILE X% > 0
'          ok% = -1
'          IF MID$(tmp$, X% + 1, 3) = "and" THEN ok% = 0
'          IF MID$(tmp$, X% + 1, 3) = "or" THEN ok% = 0
'          IF ok% THEN
'            MID$(tmp$, X% + 1, 1) = UCASE$(MID$(tmp$, X% + 1, 1))
'          END IF
'          X% = INSTR(X% + 1, tmp$, " ")
'        LOOP
'        DO WHILE RIGHT$(tmp$, 1) = "."
'          tmp$ = MID$(tmp$, 1, LEN(tmp$) - 1)
'        LOOP
'        IF RIGHT$(tmp$, 2) = "St" THEN
'          X% = INSTR(tmp$, " St")
'          MID$(tmp$, X%, 2) = " St": tmp$ = tmp$ + "."
'        END IF
'        IF RIGHT$(tmp$, 2) = "Rd" THEN
'          X% = INSTR(tmp$, " Rd")
'          MID$(tmp$, X%, 4) = " Rd": tmp$ = tmp$ + "."
'        END IF
'
'        who.saddr = tmp$
'      END IF
'
'      PUT #ch2%, rec%, who
'
'      GET #ch2%, , who: rec% = rec% + 1
'    LOOP

'
		BEEP
xpcase:
		FOR i% = 1 TO 100: X$ = INKEY$: NEXT
		PCOPY 1, 0

END SUB

FUNCTION repcode$ (in$, DB.OR.CR$)

	IF DB.OR.CR$ = "CR" THEN
		SELECT CASE in$
		CASE "B": wrk$ = "Bureau Veritas      "
		CASE "C": wrk$ = "...................."
		CASE "L": wrk$ = "Lloyds Register     "
		CASE "M": wrk$ = "...................."
		CASE "N": wrk$ = "N.A.T.A.            "
		CASE "S": wrk$ = "Standards Australia "
		CASE "T": wrk$ = "...................."
		CASE "U": wrk$ = "Unregistered        "
		CASE "X": wrk$ = "...................."
		CASE "V": wrk$ = "** BUREAU VERITAS **"
		CASE ELSE
		END SELECT
		END IF

	IF DB.OR.CR$ = "DB" THEN
		SELECT CASE in$
		CASE "B": wrk$ = "*** BAD ACCOUNT. ***"
		CASE "C": wrk$ = "...................."
		CASE "L": wrk$ = "...................."
		CASE "M": wrk$ = "** SHIRLEY McCONE **"
		CASE "N": wrk$ = "...................."
		CASE "R": wrk$ = "****** COUNTER *****"
		CASE "T": wrk$ = "** TRADE ACCOUNT. **"
		CASE "U": wrk$ = "***** UNKNOWN. *****"
		CASE "V": wrk$ = "...................."
		CASE ELSE
		END SELECT
		END IF

	IF DB.OR.CR$ = "--" THEN
		SELECT CASE in$
		CASE "B": wrk$ = "*** BAD ACCOUNT.****"
		CASE "C": wrk$ = "***** CREDITOR *****"
		CASE "L": wrk$ = "...................."
		CASE "M": wrk$ = "** RESELLER LEAD. **"
		CASE "N": wrk$ = "...................."
		CASE "S": wrk$ = "...................."
		CASE "T": wrk$ = "**** TRADE LEAD ****"
		CASE "U": wrk$ = "***** UNKNOWN.******"
		CASE "V": wrk$ = "...................."
		CASE ELSE
		END SELECT
		END IF

	repcode$ = wrk$
END FUNCTION

SUB rmvnull

	FOR i% = 1 TO 6
	FOR j% = 1 TO LEN(cus.ContactFirstName$(i%))
	IF ASC(MID$(cus.ContactFirstName$(i%), j%, 1)) = 0 THEN MID$(cus.ContactFirstName$(i%), j%, 1) = " "
	NEXT
	NEXT

	FOR i% = 1 TO 6
	FOR j% = 1 TO LEN(cus.ContactSurName$(i%))
	IF ASC(MID$(cus.ContactSurName$(i%), j%, 1)) = 0 THEN MID$(cus.ContactSurName$(i%), j%, 1) = " "
	NEXT
	NEXT

	FOR i% = 1 TO 6
	FOR j% = 1 TO LEN(cus.ContactPhone$(i%))
	IF ASC(MID$(cus.ContactPhone$(i%), j%, 1)) = 0 THEN
		MID$(cus.ContactPhone$(i%), j%, 1) = " "
		END IF
	NEXT
	NEXT

	FOR i% = 1 TO 6
	FOR j% = 1 TO LEN(cus.ContactFax$(i%))
	IF ASC(MID$(cus.ContactFax$(i%), j%, 1)) = 0 THEN MID$(cus.ContactFax$(i%), j%, 1) = " "
	NEXT
	NEXT

	FOR i% = 1 TO 6
	FOR j% = 1 TO LEN(cus.ContactMobile$(i%))
	IF ASC(MID$(cus.ContactMobile$(i%), j%, 1)) = 0 THEN MID$(cus.ContactMobile$(i%), j%, 1) = " "
	NEXT
	NEXT

	FOR i% = 1 TO 6
	FOR j% = 1 TO LEN(cus.sphone$)
	IF ASC(MID$(cus.sphone$, j%, 1)) = 0 THEN MID$(cus.sphone, j%, 1) = " "
	NEXT
	NEXT

	FOR i% = 1 TO 6
	FOR j% = 1 TO LEN(cus.sphone1$)
	IF ASC(MID$(cus.sphone1$, j%, 1)) = 0 THEN MID$(cus.sphone1, j%, 1) = " "
	NEXT
	NEXT


END SUB

SUB searchindex (keyin$, chi%, found%)
'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

SUB setaudit (n%)
'$INCLUDE: '\tpmanuf\src\setaudit.bi'
END SUB

SUB TitleList (a$, updwn%)
DIM sls$(12)
sls$(1) = "....................."
sls$(2) = "....................."
sls$(3) = "Sales Manager.       "
sls$(4) = "Sales Representative."
sls$(5) = "Proprietor.          "
sls$(6) = "Manager.             "
sls$(7) = "Managing Director.   "
sls$(8) = "Technical Service.   "
sls$(9) = "Customer Service.    "
sls$(10) = "Purchasing Officer.  "
sls$(11) = "Accounts Receivable. "
sls$(12) = "Accounts Payable.    "

PCOPY 0, 1
CALL BOX(15, 10, 43, 24, 2, 0, 2)'1-11
FOR i% = 1 TO 12
LOCATE 10 + i%, 16: PRINT USING "##...&"; i%; sls$(i%)
NEXT

LOCATE 23, 16: PRINT "Select..> ";
LOCATE 23, 25
a$ = ""
DO UNTIL VAL(a$) >= 1 AND VAL(a$) <= 12
CALL inpnew(a$, 102!, updwn%, "13,59")
IF updwn% = 59 THEN a$ = "": EXIT DO
LOOP

PCOPY 1, 0

a% = VAL(a$)
IF a% < 1 OR a% > 12 THEN a% = 1

a$ = sls$(a%)
IF updwn% = 13 THEN updwn% = 0

END SUB

SUB trimfile (ok%)
	'Search for the last active record
	lastactive% = 0
	rec% = 1
	GET #ch%, rec%, who
	DO WHILE NOT EOF(ch%)
		IF CVI(who.sno) = rec% THEN lastactive% = rec%
		IF rec% MOD 100 = 0 THEN CALL sndmsg("Searching Record" + STR$(rec%))
		GET #ch%, , who: rec% = rec% + 1
	LOOP
	CALL sndmsg("Last active Record" + STR$(lastactive%))

	OPEN "C:\TPEXE\who.wrk" FOR RANDOM AS #99 LEN = LEN(who)
	rec% = 1
	GET #ch%, rec%, who
	DO WHILE NOT EOF(ch%) AND rec% <= lastactive%
		IF CVI(who.sno) <> rec% THEN
			who.sno = MKI$(0)
			who.addate$ = "        "
		END IF

		PUT #99, rec%, who

		IF rec% MOD 100 = 0 THEN CALL sndmsg("Writing Record" + STR$(rec%))
		GET #ch%, , who: rec% = rec% + 1
	LOOP

	CLOSE #ch%
	CLOSE #99


	SELECT CASE ch%
	CASE 44: SHELL "COPY C:\TPEXE\who.wrk sup.who"
	CASE 43: SHELL "COPY C:\TPEXE\who.wrk cus.who"
	CASE 64: SHELL "COPY C:\TPEXE\who.wrk who.who"
	CASE ELSE
	END SELECT

	'KILL "C:\TPEXE\who.WRK"


END SUB
