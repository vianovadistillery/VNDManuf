DECLARE SUB sortfile (ok%)
DECLARE SUB qsort (r$(), k%(), n%)
DECLARE SUB erase.index (ok%, chi%)
'////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>> XXwho01X - INDEX OVER who.who FILE <<<<<<<<<<<<<<<<<<<
'////////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
	apgm$ = "XXWHO01"
	'$ INCLUDE: '\tpmanuf\src\pgmerr.INC'
	CLOSE
	max% = 1800
	DIM SHARED k%(max%), r$(max%)
	DIM h%(15)
	DIM SHARED chi%, ch%

'>>>---------------------------------------------------<<<
'>>> NOTE: This program is for Suppliers and Customers
'>>>       Pass parm of  /CR or /DB
'>>>---------------------------------------------------<<<
	DB.OR.CR$ = ENVIRON$("DB.OR.CR$")
	last.pgm$ = ENVIRON$("LAST.PGM$")
	parm$ = ENVIRON$("PARM$")
	CR% = INSTR(COMMAND$, "/CR")
	D2% = INSTR(COMMAND$, "/--")
	IF CR% > 0 THEN DB.OR.CR$ = "CR"
	IF D2% > 0 THEN DB.OR.CR$ = "--"
	'DB.OR.CR$ = "--"
	'DB.OR.CR$ = "DB"


	SELECT CASE DB.OR.CR$
	CASE "CR":  ch% = 44: chi% = 45
				head$ = "INDEX FOR SUPPLIERS (CREDITOR)"
	CASE "DB":  ch% = 43: chi% = 23
				head$ = "INDEX FOR CUSTOMERS (DEBTORS) "
	CASE "--":  ch% = 64: chi% = 65
				head$ = "INDEX FOR --------  (LEADS)   "
	CASE ELSE
	END SELECT
	pass% = 0

start:
	pass% = pass% + 1

	CALL setup(head$)
	'>>>>> DELETE OLD INDEX FILE
		'>>>>> OPEN FILES
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	'$INCLUDE: '\tpmanuf\src\CUS.INC'
	'$INCLUDE: '\tpmanuf\src\CUSX.INC'
	'$INCLUDE: '\tpmanuf\src\who.INC'
	'$INCLUDE: '\tpmanuf\src\whoX.INC'
	'$INCLUDE: '\tpmanuf\src\msmisc.INC'
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxcus% = CVI(msmisc.max7$)
	maxsup% = 3000
	n% = 0
	'*
	LOCATE 8, 20: PRINT "Index file create commencing....": LOCATE 1, 1
	FOR i% = 1 TO max%: k%(i%) = 0: r$(i%) = "~~~~": NEXT'* Set array to *hival
	'*

	LOCATE 10, 20: PRINT "Reading file details.....": LOCATE 1, 1
	rec% = 1
	GET #ch%, rec%, who
	DO WHILE NOT EOF(ch%)

		IF CVI(who.sno$) = rec% THEN
				k%(rec%) = CVI(who.sno$): r$(rec%) = who.search$ + who.stype$
				n% = n% + 1
		ELSE
				k%(rec%) = -1: r$(rec%) = "~~~~~"
				n% = n% + 1
		END IF

		IF rec% MOD 100 = 0 THEN LOCATE 10, 60: PRINT USING "##,###"; rec%
		GET #ch%, , who: rec% = rec% + 1
		LOOP
	'*
	LOCATE 12, 20: PRINT "Sorting records now.......": LOCATE 1, 1
	CALL qsort(r$(), k%(), n%)
	LOCATE 14, 20: PRINT "Writing new file..........": LOCATE 1, 1
	FOR i% = 1 TO n%
		LSET whox.wcde$ = r$(i%): LSET whox.wrrn$ = MKI$(k%(i%))
		PUT #chi%, i%, whox
		LOCATE 16, 20: PRINT "Record...................."; i%: LOCATE 1, 1
		LOCATE 17, 20: PRINT "Code."; whox.wcde$, "RRN."; CVI(whox.wrrn$)
	NEXT

	IF pass% = 1 THEN
		CALL sortfile(ok%)
		CLOSE
		IF ok% THEN
			GOTO start
		ELSE
			CALL sndmsg("Index only. Data file could not be copied.")
			SOUND 200, 1
			SLEEP 1
			END IF
		END IF

ENDPGM:
	CLOSE
	IF parm$ > "......" THEN
		apgm$ = parm$
		ENVIRON "PARM$=......"

	END IF

	CALL exitpgm(apgm$)
	CHAIN apgm$
	END

SUB qsort (in$(), in%(), n%) STATIC
'$INCLUDE: '\tpmanuf\src\qsort.bi'
END SUB

SUB sortfile (ok%)
	ok% = 0

	SELECT CASE chi%
	CASE 23: tofile$ = "cus.who"
	CASE 45: tofile$ = "sup.who"
	CASE 65: tofile$ = "who.who"
	CASE ELSE
	END SELECT


	ON LOCAL ERROR RESUME NEXT
	LOCK #ch%
	IF ERR > 0 THEN GOTO xsortfile
	UNLOCK #ch%
	ON LOCAL ERROR GOTO 0


	OPEN "who.new" FOR OUTPUT AS #1: CLOSE #1
	OPEN "who.new" FOR RANDOM AS #1 LEN = 1696

	maxwho% = 3000

	lin% = 999
	recx% = 1
	GET #chi%, recx%, whox
	DO WHILE NOT EOF(chi%)
		rec% = CVI(whox.wrrn$)
		IF rec% > 0 AND rec% <= maxwho% THEN
			GET #ch%, rec%, who

			nrec% = nrec% + 1
			who.sno$ = MKI$(nrec%)
			PUT #1, nrec%, who

			'lin% = lin% + 1: IF lin% > 22 THEN lin% = 4
			'LOCATE lin%, 2:
			'PRINT USING "#### \    \ &"; CVI(who.sno$); who.search$ + who.stype$; who.sname$
			IF recx% MOD 100 = 0 THEN CALL sndmsg("Record:" + STR$(recx%)): COLOR 2, 0
		END IF
		GET #chi%, , whox: recx% = recx% + 1
	LOOP



	ON LOCAL ERROR RESUME NEXT
	LOCK #ch%
	IF ERR > 0 THEN GOTO xsortfile
	UNLOCK #ch%
	ON LOCAL ERROR GOTO 0

	CLOSE

	ON LOCAL ERROR RESUME NEXT
	OPEN tofile$ FOR RANDOM AS #99
	IF ERR > 0 THEN CLOSE #99: GOTO xsortfile
	CLOSE #99
	ON LOCAL ERROR GOTO 0

	shellb$ = "COPY who.new " + tofile$
	SHELL shellb$
	ok% = -1


xsortfile:


END SUB

