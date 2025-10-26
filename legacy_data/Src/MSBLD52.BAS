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
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	'$INCLUDE: '\tpmanuf\src\fordet.INC'
	'$INCLUDE: '\tpmanuf\src\tntdet.INC'

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

CLS
shella$ = "COPY c:\Zsystem" + who$ + "\fordet.asf c:\tpmanuf\*.asf"
shellb$ = "COPY c:\Zsystem" + who$ + "\msrmnew.msf c:\tpmanuf\*.msf"
PRINT shella$
PRINT shellb$
SHELL shella$
SHELL shellb$
SHELL "pause"


	OPEN "MSRMNEW.X03" FOR OUTPUT AS #138: CLOSE #138
	OPEN "MSRMNEW.X03" FOR RANDOM SHARED AS #138 LEN = LEN(msrmat)

	OPEN "FORDET.X03" FOR OUTPUT AS #165: CLOSE #165
	OPEN "FORDET.X03" FOR RANDOM SHARED AS #165 LEN = 32

	OPEN "TNTDET.X03" FOR OUTPUT AS #155: CLOSE #155
	OPEN "TNTDET.X03" FOR RANDOM SHARED AS #155 LEN = 32

	STDOUT$ = "CON"
	OPEN STDOUT$ FOR OUTPUT AS #99

	DIM h%(15)
	sorted% = 0
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxhst% = CVI(msmisc.max4$): maxacc% = CVI(msmisc.max5$)
	maxrmat% = 4000 '???
	DIM rrn%(maxlines%), k%(maxrmat%), s$(maxrmat%)

START:
	CALL setup("RAW MATERIAL REBUILD")
	COLOR 0, 3: LOCATE 25, 4:  PRINT "F1-Exit"; : COLOR 2, 0
	LOCATE 16, 20: PRINT "Enter Start Raw Material Number..> ";
	CALL inpnew(strrrn$, 105!, updwn%, "13,59" + ALT$)': GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
	strrrn% = VAL(strrrn$)
	IF strrrn% < 1 THEN GOTO START

	IF NOT sorted% THEN
		GOSUB LOAD.SORT
		CALL qsort(s$(), k%(), rmx%, ok%)
		sorted% = -1
	END IF

	GOSUB DO.IT
	GOSUB DO.rec

	CLOSE

shella$ = "COPY c:\tpmanuf\fordet.x03  c:" + who$ + "*.asf"
shellb$ = "COPY c:\tpmanuf\msrmnew.x03 c:" + who$ + "*.msf"
PRINT shella$
PRINT shellb$
SHELL shella$
SHELL shellb$

shella$ = "COPY c:\tpmanuf\fordet.x03  c:\tpmanuf" + who$ + "\*.asf"
shellb$ = "COPY c:\tpmanuf\msrmnew.x03 c:\tpmanuf" + who$ + "\*.msf"
PRINT shella$
PRINT shellb$
SHELL shella$
SHELL shellb$


SHELL "pause"

apgm$ = "MSUPD01"


	END

'/////////////////////////////////////////////////////////////////////////////
'>>--
'/////////////////////////////////////////////////////////////////////////////
LOAD.SORT:
	'***** Read r/m file
	LOCATE 20, 20: PRINT "Loading raw materials for sort.": LOCATE 1, 1
	GET #38, 1, msrmat: rmx% = 0: wrk$ = "  ": wrk2$ = "  ": oldsup = 32767
	
	FOR i% = 1 TO maxrmat%
		IF i% = msrmat.no THEN
			 rmx% = rmx% + 1
			 s$(rmx%) = MID$(msrmat.search$, 1, 5) + msrmat.desc1$ + STR$(msrmat.no%)
			 k%(rmx%) = i%
		END IF
	GET #38, , msrmat
	NEXT

RETURN
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'>>>>>>>>>>  change rmat
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
DO.IT:
	s$ = SPACE$(15)
	savsup% = 9999
	lin = 9999: pag = 0
	vtotstock = 0
	cursup$ = "": savsup$ = ""

	FOR i% = 1 TO rmx%
		IF STDOUT$ <> "CON" THEN
			LOCATE 20, 20: PRINT "Printing raw material "; i%; " out of "; rmx%: LOCATE 1, 1
		END IF

		rec% = k%(i%)
		newrrn% = i% + strrrn% - 1
		GET #38, rec%, msrmat

		'>-- L1 - PROCESSING --<
		cursup$ = msrmat.search$
		IF cursup$ <> savsup$ THEN
			 savsup$ = cursup$

			 keyin$ = msrmat.search$: chi% = 45
			 CALL searchindex(keyin$, chi%, found%)
			 supno% = CVI(supx.wrrn$)
			 IF supno% < 1 OR supno% > maxsup% THEN supno% = 1
			 GET #44, supno%, sup
		END IF
		'>>--  END L1 --<<

		'PRINT #99, USING "#### \      \ \       \... "; CVI(sup.sno); msrmat.search; sup.sname$;
		'PRINT #99, USING "#### \                     \ ### !"; rec%; msrmat.Desc1$; msrmat.Group%; msrmat.Active$; lin = lin + 1

		'Store the new rmat# on the old file.
		GET #38, rec%, msrmat
		msrmat.nno = newrrn%
		IF newrrn% <= 0 THEN STOP'??
		PUT #38, rec%, msrmat

		'>Write new
		msrmat.nno = msrmat.no
		msrmat.no = newrrn%
		PUT #138, newrrn%, msrmat

	NEXT
	PRINT "last raw #"; newrrn%
RETURN

'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'>>>>>>>>>>  update formula details.
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
DO.rec:

	'Formulations
	FOR i& = 1 TO LOF(65) / 32
		GET #65, i&, tntdet
		IF i& = tntdet.tnt& THEN
			nno% = tntdet.rmat%
			IF tntdet.rmat > 0 THEN
				'>-The new rmat# is on the old rmat file.
				GET #38, tntdet.rmat, msrmat
				nno% = msrmat.nno

				'>-Check the record is available
				IF nno% > 0 THEN
				GET #138, nno%, msrmat
				IF msrmat.no <> nno% THEN
					nno% = strrrn% - 1
					IF strrrn% = 1 THEN nno% = 3
				END IF
				END IF
			END IF
								
			GET #65, i&, tntdet
			tntdet.rmat% = nno%
			PUT #165, i&, tntdet
		END IF
	NEXT

	PRINT "Done. "
	'Tints


RETURN

SUB qsort (in$(), in%(), n%, ok%) STATIC
'$INCLUDE: '\tpmanuf\src\qsort.bi'
END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

