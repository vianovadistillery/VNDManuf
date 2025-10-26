'/////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>> XXsup01L -LIST SUPPLIER FILE INDEX <<<<<<<<<<<<<<<<<<<<
'/////////////////////////////////////////////////////////////////////
'.dc - Complete
	 '$INCLUDE: '\tpmanuf\src\pgmhead.INC'
	 apgm$ = "FIMENU"
'>>>---------------------------------------------------<<<
'>>> NOTE: This program is for Suppliers and Customers
'>>>       Pass parm of  /CR or /DB
'>>>---------------------------------------------------<<<
	DB.OR.CR$ = "DB"
	DB.OR.CR$ = ENVIRON$("DB.OR.CR$")
	CR% = INSTR(COMMAND$, "/CR")
	IF CR% > 0 THEN DB.OR.CR$ = "CR"

	IF DB.OR.CR$ = "CR" THEN
		chmain% = 44: chindex% = 45
		ELSE
		chmain% = 43: chindex% = 23
		END IF
		'>>>>> OPEN FILES
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\msmisc.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	'$INCLUDE: '\tpmanuf\src\CUS.INC'
	'$INCLUDE: '\tpmanuf\src\CUSX.INC'
	 'STDOUT$ = "con"
	 OPEN STDOUT$ FOR OUTPUT AS #99
	 GET #36, 1, msmisc

	maxsup% = 1000
	PAG% = 0: lin% = 9999
	j% = 0
	FOR i% = 1 TO maxsup%
		GET #45, i%, supx
		IF j% = 0 THEN
			IF supx.wcde$ = "~~~~~" THEN EXIT FOR
			lin% = lin% + 1
			IF lin% > 50 THEN GOSUB heading
			END IF

		PRINT #99, USING "| \   \ #### "; supx.wcde$; CVI(supx.wrrn$);
		j% = j% + 1
		IF j% = 6 THEN PRINT #99, "|": j% = 0
		NEXT
	PRINT #99, CHR$(12)
	CLOSE
	CALL exitpgm(apgm$)
	CHAIN apgm$
'////////////////////////////////////////////////////////////////////////////
'>>>>
'////////////////////////////////////////////////////////////////////////////
heading:
	PAG% = PAG% + 1: IF PAG% > 1 THEN PRINT #99, CHR$(12)

	PRINT #99, : PRINT #99, ; CHR$(14); msmisc.cc$
	PRINT #99, "#ACIDX03L"; TAB(60); DATE1$; " "; TIME$
	PRINT #99, "S T O C K   F I L E   I N D E X";
	PRINT #99, TAB(69); "page: "; PAG%
	PRINT #99, STRING$(79, "=")
	lin% = 1


RETURN

