DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB qsort (in$(), in%(), n%, ok%)
'.dc - Complete
'/////////////////////////////////////////////////////////////////////////////
'>>>--- RAW MATERIAL REBUILD
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
	CONST maxlines% = 20'19
	
	'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "MSMENU"
	''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	'$INCLUDE: '\tpmanuf\src\MSRMat.INC'

who$ = "\tpmanuf"
who$ = "\BRISTOL"
who$ = "\henkel"
who$ = "\hichem"
who$ = "\Jordan"
who$ = "\JOTUN"
who$ = "\Merlion"
who$ = "\redic"
who$ = "\SICPA"
who$ = "\SPARTAN"
who$ = "\WAGON"
file$ = "C:\TPMANUF" + who$ + "\msrmnew.msf"
	OPEN file$ FOR RANDOM SHARED AS #138 LEN = LEN(msrmat)

START:
	CALL setup("MERGE RAW MATERIAL REBUILD")
	COLOR 0, 3: LOCATE 25, 4:  PRINT "F1-Exit"; : COLOR 2, 0

	GOSUB DO.IT

	CLOSE


	END

'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'>>>>>>>>>>  change rmat
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
DO.IT:
	count% = 0

	FOR i% = 1 TO 9999
		GET #138, i%, msrmat
		IF i% = msrmat.no THEN
			PUT #38, i%, msrmat
			count% = count% + 1
		END IF
	NEXT

	LOCATE 10, 10
	PRINT "Merged:"; count%; " from "; who$

RETURN

