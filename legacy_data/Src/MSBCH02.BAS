'///////////////////////////////////////////////////////////////////////
'>>>>>  M S B C H 0 2
'///////////////////////////////////////////////////////////////////////
'.dc - Complete
	'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	pgm$ = "msmenu"
	''$INCLUDE: '\tpmanuf\src\pgmerr.inc'

	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	'$INCLUDE: '\tpmanuf\src\msbatch.INC'

	DIM mm(80), sz$(100), cst$(10)
	DIM mdesc$(12), ac(100)

	STDOUT$ = "LPT1" '??
	'STDOUT$ = "shit.sht"



	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	qtyf% = CVI(msmisc.qtyf$): bchoff% = CVI(msmisc.bchoff$): bchno% = CVI(msmisc.bchno$)
	maxhist% = CVI(msmisc.max4$)

	FOR rec% = 0 TO 12: READ mdesc$(rec%): NEXT
	DATA ** unknown **,january,february,march,april,may,june,july,august
	DATA september,october,november,december
START:
	a$ = "5"
	CALL setup("BATCH PROCESSING")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : COLOR 2, 0
	LOCATE 8, 15: PRINT "1... Enter batch data"
	LOCATE , 15: PRINT "2... List unfinished batches to date."
	LOCATE , 15: PRINT "3... Raw materials required to complete batches"
	LOCATE , 15: PRINT "9... Page advance."
'///////////////////////////////////////////////////////////////////////
'>>>>> C H E C K   O P T I O N
'///////////////////////////////////////////////////////////////////////
	COLOR 2, 0
	LOCATE 14, 20: COLOR 2: PRINT "Select Option..> "; CHR$(FNH);
	b$ = ""
	CALL inpnew(b$, 101!, updwn%, "13,59" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : RESET: CALL exitpgm(pgm$): CHAIN pgm$
	b% = VAL(b$)
	SELECT CASE b%
		CASE 1: CLOSE : bpgm$ = "msbch01d": CALL exitpgm(bpgm$): CHAIN bpgm$
		CASE 2: GOSUB PRT.UNFINISHED
		CASE 3: CLOSE : bpgm$ = "msbch05": CALL exitpgm(bpgm$): CHAIN bpgm$
		CASE 9: PRINT #99, CHR$(12)
		CASE ELSE
		END SELECT
	GOTO START
'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'>>>>
'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
PRT.UNFINISHED:
	OPEN STDOUT$ FOR OUTPUT AS #99

	'* Unfinished batches
	 lin% = 9999: pag% = 0
	 rec% = 1
	 GET #57, rec%, batch
	 DO WHILE NOT EOF(57)
		IF lin% > 49 THEN GOSUB heading
		LOCATE 18, 10: PRINT "Batch "; batch.bno%; ". "; batch.name$; ". Number"; rec%; " out of"; bchno%
		found% = -1
		IF batch.bno% = 0 THEN found% = 0 'Record is not used
		IF batch.yld! = 0 THEN found% = 0 '* Not made
		IF batch.ayld! > 0 THEN found% = 0'* Finished batch
		IF found% THEN
			LOCATE 20, 10: PRINT "Number of unfinshed batches:"; num% + 1
			PRINT #99, USING "####   \   \     \                            \     ####      ####     \      \"; batch.bno%; batch.form$; batch.name$; batch.yld!; batch.ayld!; FNDYY$(batch.date$)
			num% = num% + 1: lin% = lin% + 1
			END IF
		GET #57, , batch: rec% = rec% + 1
		LOOP
	PRINT #99, ""
	PRINT #99, "Total unfinished batches:"; num%
	PRINT #99, CHR$(12)
	CLOSE #99
	'SHELL "type shit.sht"

RETURN
'////////////////////////////////////////////////////////////////////////////
'>>> Heading for unfinished batches
'////////////////////////////////////////////////////////////////////////////
heading:
	 pag% = pag% + 1: lin% = 0
	IF pag% > 1 THEN PRINT #99, CHR$(12)
	PRINT #99, "msbch02"; TAB(66); "Date: "; DATE1$
	PRINT #99, ; CHR$(14); msmisc.cc$
	PRINT #99, ""
	PRINT #99, TAB(17); "U N F I N I S H E D   B A T C H   L I S T I N G"
	PRINT #99, "Batches on file:"; bchoff% + 1; " - "; bchno% + bchoff%;
	PRINT #99, TAB(72); "page: "; pag%
	PRINT #99, STRING$(79, "=")
	PRINT #99, "Batch  Formula   Description                       Yield     A/Yld     Date   "
	PRINT #99, STRING$(79, "-")
RETURN

