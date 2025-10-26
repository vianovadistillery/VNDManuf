
	DEF FNE : X0% = CSRLIN: Y0% = POS(0): PRINT SPACE$(80 - Y0%): LOCATE X0%, Y0%: FNE = 0: END DEF

	DEF FNH : Y0% = CSRLIN: X0% = POS(0): X0% = X0% + (X0% > 1) + (X0% > 1): LOCATE Y0%, X0%: FNH = SCREEN(Y0%, X0%): END DEF
	DEF FNX : X0% = CSRLIN: Y0% = POS(0): LOCATE 1, 60: PRINT "QBX": LOCATE X0%, Y0%: FNX = 0: END DEF
	DATE1$ = "  /  /  ": MID$(DATE1$, 1, 2) = MID$(DATE$, 4, 2):         MID$(DATE1$, 4, 2) = MID$(DATE$, 1, 2): MID$(DATE1$, 7, 2) = MID$(DATE$, 9, 2)
	DEF FNDYY$ (yyyymmdd$) : DYY$ = "dd/mm/yy": MID$(DYY$, 1, 2) = MID$(yyyymmdd$, 7, 2): MID$(DYY$, 4, 2) = MID$(yyyymmdd$, 5, 2): MID$(DYY$, 7, 2) = MID$(yyyymmdd$, 3, 2): FNDYY$ = DYY$: END DEF
	DEF FNDY$ (ddmmyy$) : DY$ = "yyyymmdd": MID$(DY$, 7, 2) = MID$(ddmmyy$, 1, 2): MID$(DY$, 5, 2) = MID$(ddmmyy$, 4, 2): MID$(DY$, 3, 2) = MID$(ddmmyy$, 7, 2): MID$(DY$, 1, 2) = RIGHT$("00" + LTRIM$(STR$((MID$(ddmmyy$, 7, 2) > "73") + 20)), 2): _
                                FNDY$ = DY$: END DEF
	NUL8$ = STRING$(0, 8): SP8$ = SPACE$(8): SP78$ = SPACE$(78)
	KEY 1, "": KEY 2, "": KEY 3, "": KEY 4, "": KEY 5, ""
	KEY 6, "": KEY 7, "": KEY 8, "": KEY 9, "": KEY 10, ""
	KEY OFF
	STDOUT$ = "LPT1"' Printer file name

	CONST ALT$ = ",16-25,30-35,38,44-50"
	GOTO SKIPTHEALTKEYJUMP:
ALT:
	SELECT CASE updwn%
	'******************** alt A - ACCESSORY MENU.......... ********************
	CASE 30: CLOSE : ACHAIN$ = "ACMENU": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt B - BATCH FILE.............. ********************
	CASE 48: CLOSE : ACHAIN$ = "MSBCH01D": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt C - CREDITORS............... ********************
	CASE 46: CLOSE : ENVIRON "DB.OR.CR$=CR": ACHAIN$ = "XXWHO01": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt D - DEBTORS................. ********************
	CASE 32: CLOSE : ENVIRON "DB.OR.CR$=DB": ACHAIN$ = "XXWHO01": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt E - EXTRA SUPPLIER FILE..... ********************
	CASE 18: CLOSE : ENVIRON "DB.OR.CR$=--": ACHAIN$ = "XXWHO01": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt F - FILE MENU............... ********************
	CASE 33: CLOSE : ACHAIN$ = "FIMENU": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt G - ........................ ********************
	' CASE 34:CLOSE:CHAIN PGM$
	'******************** alt H - ........................ ********************
	' CASE 35:CLOSE:CHAIN PGM$
	'******************** alt I - INVOICE................. ********************
	CASE 23: CLOSE : ENVIRON "PARM2$=......": ACHAIN$ = "DSINV01D": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt J - ........................ ********************
	' CASE 36:CLOSE:CHAIN PGM$
	'******************** alt K - ........................ ********************
	'CASE 37: CLOSE : CHAIN PGM$
	'******************** alt L - LEDGER.................. ********************
	CASE 38: CLOSE : ACHAIN$ = "ASAUD01": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt M - MANUFACTURING MENU...... ********************
	CASE 50: CLOSE : ACHAIN$ = "MSMENU": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt N - NOTE FILE............... ********************
	CASE 49: CLOSE : ACHAIN$ = "NOTES01": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt O - ORDER FILE.............. ********************
	CASE 24: CLOSE : ACHAIN$ = "MSORD01": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt P - PRINT RECIPE............ ********************
	CASE 25: CLOSE : ACHAIN$ = "MSBCH01P": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt Q - QUALITY MENU............ ********************
	CASE 16: CLOSE : ACHAIN$ = "QSMENU": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt R - RAW MATERIAL FILE....... ********************
	CASE 19: CLOSE : ACHAIN$ = "MSUPD01": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt S - STOCK FILE.............. ********************
	CASE 31: CLOSE : ACHAIN$ = "ACSTK01": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt T - TELEPHONE LIST.......... ********************
	CASE 20: SHELL "C:\TPEXE\phone1s"
	'******************** alt U - UPDATE FORMULA.......... ********************
	CASE 22: CLOSE : ACHAIN$ = "MSUPD02D": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt V - ........................ ********************
	' CASE 47:CLOSE:CHAIN PGM$
	'******************** alt W - ........................ ********************
	CASE 17: CLOSE : ACHAIN$ = "WOINV01D": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt X - OPEN CASH DRAWER........ ********************
	CASE 45:
	'******************** alt Y - OLD PRICE INVOICE....... ********************
	CASE 21: CLOSE : ENVIRON "PARM2$=PRE...": ACHAIN$ = "DSINV01D": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$
	'******************** alt Z - MAIN MENU............... ********************
	CASE 44: CLOSE : ACHAIN$ = "MENUTP": CALL EXITPGM(ACHAIN$): CHAIN ACHAIN$

	CASE ELSE: updwn% = updwn%
	END SELECT

	'>>- Any unused ALT code should be mapped to (CR)
	IF updwn% >= 17 AND updwn% <= 21 THEN updwn% = 13
	IF updwn% >= 26 AND updwn% <= 26 THEN updwn% = 13
	IF updwn% >= 28 AND updwn% <= 29 THEN updwn% = 13
	IF updwn% >= 34 AND updwn% <= 21 THEN updwn% = 13
	IF updwn% >= 35 AND updwn% <= 36 THEN updwn% = 13
	IF updwn% >= 36 AND updwn% <= 21 THEN updwn% = 13
	IF updwn% >= 37 AND updwn% <= 21 THEN updwn% = 13


RETURN

SKIPTHEALTKEYJUMP:

