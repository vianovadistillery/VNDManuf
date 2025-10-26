DECLARE SUB setaudit (n%)
DECLARE SUB searchindex (keyin$, chi%, found%)
	DIM SHARED auditfile$(15), naudit%
	apgm$ = "FIMENU"
	CALL setaudit(naudit%)
	cashonly$ = "M": auditname$ = auditfile$(naudit%)
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\ASAUDIT.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	'$INCLUDE: '\tpmanuf\src\CUS.INC'
	'$INCLUDE: '\tpmanuf\src\CUSX.INC'
	CALL setup("GENERAL LEDGER ACCOUNT REBUILD")
	GOSUB open.audit

	DB.OR.CR$ = "DB"
	DB.OR.CR$ = ENVIRON$("DB.OR.CR$")
	CR% = INSTR(COMMAND$, "/CR")
   CR% = 1 '<<<-Swap to CR. System use cr% = 1
   'CR% = 0
   IF CR% > 0 THEN DB.OR.CR$ = "CR"
	 IF DB.OR.CR$ = "CR" THEN
		cha% = 45: chb% = 44
		ELSE
		cha% = 23: chb% = 43
	 END IF

	rrn% = 1
	GET #8, rrn%, audit
	DO WHILE NOT EOF(8)
		test$ = MID$(audit.adtype$, 1, 1)
		IF test$ = MID$(DB.OR.CR$, 1, 1) THEN

		skey$ = audit.adcust$
		CALL searchindex(skey$, cha%, found%)
		IF NOT found% THEN
			msg$ = "Customer " + audit.adcust$ + " " + audit.adtype$ + "  at record " + STR$(rrn%) + " of the audit file."
			updwn% = 59
			EXIT DO
			END IF

		idx% = CVI(supx.wrrn$)
		GET #chb%, idx%, sup

		LOCATE 8, 2
		PRINT USING "#### & & & ###.## change to ###.##"; audit.adrec%; audit.adtype$; audit.adcust$; audit.addocnum$; audit.adglacc!; CVS(sup.sgl$)
		'x$ = INPUT$(1)

		IF audit.adcust$ = sup.search$ + sup.stype$ THEN
		IF audit.adglacc! <> CVS(sup.sgl$) THEN
				LOCATE 10, 2
			   PRINT USING "#### & & & ###.## change to ###.##"; audit.adrec%; audit.adtype$; audit.adcust$; audit.addocnum$; audit.adglacc!; CVS(sup.sgl$)
			   LOCATE 12, 20
				a$ = "Y"
			   'CALL inpnew(a$, 101!, updwn%, "13,59") 'Change all
			   IF updwn% = 59 THEN EXIT DO
			   IF a$ = "Y" THEN
					audit.adglacc! = CVS(sup.sgl$)
					PUT #8, rrn%, audit
					count% = count% + 1
					END IF
			   END IF
			   END IF

		END IF

		IF rrn% MOD 100 = 0 THEN
			LOCATE 22, 2: PRINT USING "record ##,###   Changed ##,###"; rrn%; count%
			END IF
		X$ = INKEY$
		IF X$ = CHR$(0) + CHR$(59) THEN updwn% = 59: EXIT DO
		IF X$ = CHR$(0) + CHR$(60) THEN updwn% = 60: EXIT DO
		GET #8, , audit: rrn% = rrn% + 1
		LOOP


	CLOSE
	CALL exitpgm(apgm$): CHAIN apgm$
	END

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

SUB setaudit (n%)
'    DIM SHARED auditfile$(15), naudit%
'    CALL setaudit(naudit%)
'    cashonly$ = "M": auditname$ = auditfile$(naudit%)
'$INCLUDE: '\tpmanuf\src\setaudit.bi'
END SUB

