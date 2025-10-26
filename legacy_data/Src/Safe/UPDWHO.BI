'////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>> UPDATE THE SUPPLIER FILE <<<<<<<<<<<<<<<<<<<<<<
'////////////////////////////////////////////////////////////////////////////
'.dc - Complete
REM SUB upd.who (chaudit%, chb%, upd%) STATIC

	'// Check absolute value of value
	orgvalue! = audit.advalue
	adtax! = audit.adtax!
	cust$ = Audit.adcust$
	custd$ = Audit.adsname$
	Value = ABS(orgvalue!)
	adtype$ = audit.adtype

	advalue = ABS(orgvalue!)

	SELECT CASE audit.adtype$
	CASE "CI": advalue = O - advalue: adtax = O - adtax
	CASE "DC": advalue = O - advalue: adtax = O - adtax
	CASE "DP": advalue = O - advalue: adtax = O - adtax
	CASE "DD": advalue = O - advalue: adtax = O - adtax
	CASE "PT": advalue = O - advalue: adtax = O - adtax
	CASE "LC": advalue = O - advalue: adtax = O - adtax
	CASE ELSE
	END SELECT


	'>>> If the UPD% is not zero then a record is being updated <<<
	IF upd% > 0 THEN
		GET #chaudit%, upd%, audit
		'>> Set the record fields <<<
		audit.advalue = advalue
		audit.adtax! = adtax!
		LSET Audit.adcust$ = cust$
		LSET Audit.adsname$ = custd$

		'/////////////////  Check figures are rounded    ///////////////////////
		test$ = STR$(audit.advalue)
		xc% = INSTR(test$, ".")
		IF xc% < 1 THEN xc% = LEN(test$): test$ = test$ + ".00"
		test$ = test$ + "00"
		small$ = MID$(test$, xc% + 3)
		IF VAL(small$) <> 0 THEN
			test$ = MID$(test$, 1, xc% + 2)
			audit.advalue = VAL(test$)
			IF small$ >= "50" THEN
				IF audit.advalue < 0 THEN audit.advalue = audit.advalue - .01
				IF audit.advalue >= 0 THEN audit.advalue = audit.advalue + .01
				END IF
		END IF

		'/// Update the audit file ///
		nxtrec% = upd%
		PUT #chaudit%, upd%, audit
		END IF

'>>> If the UPD% is equal to zero only update customer info <<<
	'>>> If the UPD% is LESS than zero then a new record is being added <<<
	IF upd% < 0 THEN
		audit.advalue = advalue
		audit.adtax = adtax
		'// Find the end of the audit file
		adlast% = LOF(chaudit%) / 92
		nxtrec% = adlast% + 1

		IF upd% = -2 THEN 'Add to previous entry ofthe same type
			i% = adlast%
			GET #chaudit%, i%, audit
			DO WHILE i% > 1
				IF audit.adtype = adtype$ THEN
					EXIT DO
				END IF
				i% = i% - 1
				GET #chaudit%, i%, audit
			LOOP

			IF audit.adtype = adtype$ THEN
				nxtrec% = i%
				GET #chaudit%, nxtrec%, audit
				audit.advalue = orgvalue! + audit.advalue
				audit.adtax = adtax! + audit.adtax
				audit.adtext = "*" + RTRIM$(audit.adtext)
				'??
			END IF
		END IF




		'/////////////////  Check figures are rounded    ///////////////////////
		test$ = STR$(audit.advalue)
		xc% = INSTR(test$, ".")
		IF xc% < 1 THEN xc% = LEN(test$): test$ = test$ + ".00"
		test$ = test$ + "00"
		small$ = MID$(test$, xc% + 3)
		IF VAL(small$) <> 0 THEN
			test$ = MID$(test$, 1, xc% + 2)
			audit.advalue = VAL(test$)
			IF small$ >= "50" THEN
				IF audit.advalue < 0 THEN audit.advalue = audit.advalue - .01
				IF audit.advalue >= 0 THEN audit.advalue = audit.advalue + .01
				END IF
		END IF


		'/// Write to the audit file ///
		Audit.adrec% = nxtrec%
		PUT #chaudit%, nxtrec%, audit
		END IF


	'>>>> Now update the customer info <<<
	IF chcus% = 44 THEN cha% = 45: chb% = 44
	IF chcus% = 43 THEN cha% = 23: chb% = 43

	SELECT CASE cha%
	CASE 45
		sno% = CVI(sup.sno$)
		IF sno% < 1 OR sno% > 1000 THEN sno% = 1
		GET #chb%, sno%, cus
		scur = CVS(sup.scur$)
		s30 = CVS(sup.s30$)
		s60 = CVS(sup.s60$)
		s90 = CVS(sup.s90$)
	CASE 23
		sno% = CVI(cus.sno$)
		IF sno% < 1 OR sno% > 1000 THEN sno% = 1
		GET #chb%, sno%, cus
		scur = CVS(cus.scur$)
		s30 = CVS(cus.s30$)
		s60 = CVS(cus.s60$)
		s90 = CVS(cus.s90$)
	CASE ELSE
	END SELECT

	IF advalue < 0 THEN
		tot.db! = 0: tot.cr! = 0 - advalue
		ELSE
		tot.db! = advalue: tot.cr! = 0
		END IF

	roll% = 0

	'> --- This section is copied to UPDWHO.BI --- < (TOP)
	'Test on       02/11/94 (Try to fix -ve rolling)
	'Patch for CR  10/12/94
	SELECT CASE cha%
	CASE 45 '<<<  Creditors  >>>>

	IF roll% THEN
		s90! = s90! + s60!
		s60! = s30!
		s30! = scur!
		scur! = 0
		END IF

	'If there is +ve values in any bucket they reduce the total CREDITS
	IF s90! < 0 THEN
		wrk! = s90!: s90! = s90! + tot.cr!: tot.cr! = 0
		IF s90! > 0 THEN tot.cr! = s90!: s90! = 0
		END IF
	IF s60! < 0 THEN
		wrk! = s60!: s60! = s60! + tot.cr!: tot.cr! = 0
		IF s60! > 0 THEN tot.cr! = s60!: s60! = 0
		END IF
	IF s30! < 0 THEN
		wrk! = s30!: s30! = s30! + tot.cr!: tot.cr! = 0
		IF s30! > 0 THEN tot.cr! = s30!: s30! = 0
		END IF

	s0! = tot.db! - tot.cr!

	IF s90! > 0 THEN
		s90! = s90! - tot.db!: tot.db! = 0: CALL ROUND(s90!, 2.5)
		IF s90! < 0 THEN tot.db! = ABS(s90!): s90! = 0
		END IF
	IF s60! > 0 THEN
		s60! = s60! - tot.db!: tot.db! = 0: CALL ROUND(s60!, 2.5)
		IF s60! < 0 THEN tot.db! = ABS(s60!): s60! = 0
		END IF
	IF s30! > 0 THEN
		s30! = s30! - tot.db!: tot.db! = 0: CALL ROUND(s30!, 2.5)
		IF s30! < 0 THEN tot.db! = ABS(s30!): s30! = 0
		END IF

	scur! = scur! + tot.cr! - tot.db!: CALL ROUND(scur!, 2.5)
	tot.cr! = 0: tot.db! = 0


	CASE ELSE'<<< DEBTORS >>>
	IF roll% THEN
		s90! = s90! + s60!
		s60! = s30!
		s30! = scur!
		scur! = 0
		END IF

	scurplus! = tot.db! + scur!
	scur.s30! = tot.db! + scur! + s30!
	scur.s30.s60! = tot.db! + scur! + s30! + s60!
	scur.s30.s60.s90! = tot.db! + scur! + s30! + s60! + s90!
	s30.s60! = s30! + s60!
	s30.s60.s90! = s30! + s60! + s90!
	s60.s90! = s60! + s90!

	IF tot.cr! = scur.s30.s60! THEN tot.db! = 0: scur! = 0: s30! = 0: s60! = 0: tot.cr! = 0
	IF tot.cr! = s30.s60.s90! THEN s30! = 0: s60! = 0: s90! = 0: tot.cr! = 0
	IF tot.cr! = s60.s90! THEN s60! = 0: s90! = 0: tot.cr! = 0
	IF tot.cr! = s30.s60! THEN s30! = 0: s60! = 0: tot.cr! = 0
	IF tot.cr! = scur.s30! THEN tot.db! = 0: scur! = 0: s30! = 0: tot.cr! = 0
	IF tot.cr! = scurplus! THEN tot.db! = 0: scur! = 0: tot.cr! = 0
	IF tot.cr! = s30! THEN s30! = 0: tot.cr! = 0
	IF tot.cr! = s60! THEN s60! = 0: tot.cr! = 0

	'If there is -ve values in any bucket they reduce the total debits
	IF s90! < 0 THEN
		wrk! = s90!: s90! = s90! + tot.db!: tot.db! = 0
		IF s90! > 0 THEN tot.db! = s90!: s90! = 0
		END IF
	IF s60! < 0 THEN
		wrk! = s60!: s60! = s60! + tot.db!: tot.db! = 0
		IF s60! > 0 THEN tot.db! = s60!: s60! = 0
		END IF
	IF s30! < 0 THEN
		wrk! = s30!: s30! = s30! + tot.db!: tot.db! = 0
		IF s30! > 0 THEN tot.db! = s30!: s30! = 0
		END IF

	IF s90! > 0 THEN
		s90! = s90! - tot.cr!: tot.cr! = 0: CALL ROUND(s90!, 2.5)
		IF s90! < 0 THEN tot.cr! = ABS(s90!): s90! = 0
		END IF
	IF s60! > 0 THEN
		s60! = s60! - tot.cr!: tot.cr! = 0: CALL ROUND(s60!, 2.5)
		IF s60! < 0 THEN tot.cr! = ABS(s60!): s60! = 0
		END IF
	IF s30! > 0 THEN
		s30! = s30! - tot.cr!: tot.cr! = 0: CALL ROUND(s30!, 2.5)
		IF s30! < 0 THEN tot.cr! = ABS(s30!): s30! = 0
		END IF

	scur! = scur! + tot.db! - tot.cr!: CALL ROUND(scur!, 2.5)
	tot.db! = 0: tot.cr! = 0
	END SELECT

	stotal! = scur! + s30! + s60! + s90!
	CALL ROUND(stotal!, 2.5)
	cf! = stotal!


	'> --- This section is copied to UPDWHO.BI --- <  (BOTTOM)


	SELECT CASE cha%
	CASE 45
		LSET sup.scur$ = MKS$(scur)
		LSET sup.s30$ = MKS$(s30)
		LSET sup.s60$ = MKS$(s60)
		LSET sup.s90$ = MKS$(s90)
		LSET sup.active$ = "A"
		PUT #chb%, sno%, sup
	CASE 23
		LSET cus.scur$ = MKS$(scur)
		LSET cus.s30$ = MKS$(s30)
		LSET cus.s60$ = MKS$(s60)
		LSET cus.s90$ = MKS$(s90)
		LSET cus.active$ = "A"
		PUT #chb%, sno%, cus
	CASE ELSE
	END SELECT


	 '>>>>>>>>>>>> Send a message to the user  <<<<<<<<<<<<<<<<<<<<
	 PCOPY 0, 1
	 CALL BOX(20, 6, 52, 9, 7, 8, 1)
	 LOCATE 7, 21: COLOR 10, 1: PRINT USING "##### Written to audit file.  "; nxtrec%: COLOR 2, 0
	 start = TIMER: WHILE TIMER - start < 1: WEND
	 PCOPY 1, 0


REM END SUB

