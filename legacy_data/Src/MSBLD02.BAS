DECLARE SUB dolist ()
DECLARE FUNCTION format$ (VALUE!, definition$)
DECLARE SUB searchindex (keyin$, chi%, found%)
	'///////////////////////////////////////////////////////////////////////
	'>> MSBLD02 - Build RMAT alpha index
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
	'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
	DIM SHARED lonly%, maxrmat%, maxsup%
	DIM SHARED keyl%, qk$, rep$
	apgm$ = "FIMENU"
	'/////////////////////////////////////////////////////
	'///  KEY LIST
	'///      KFLD    msrmat.Desc1$     25
	'///      KFLD    msrmat.search$     5
	'///      KFLD    msrmat.rno%        2  (Low byte,High byte)
	'//////////////////////////////////////////////////////
	CALL setUp("INDEX FOR RAW MATERIALS")
	CALL prtbtm(" F1 - exit.")
	keyl% = 32: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)
	COLOR 2
	'////////////////////////////////
	'0 - Build index
	'1 - List index only
	'2 - Both
	'////////////////////////////////
	lonly% = 0
	'---------------------------------
	cursup$ = "    ": savsup$ = "@@@@": skey$ = "    "
	sp10$ = SPACE$(10)
	nul10$ = STRING$(10, 0)
	CLOSE

	IF lonly% = 1 OR lonly% = 2 THEN
		stdout$ = "CON"
		OPEN stdout$ FOR OUTPUT AS #99
	END IF

	IF lonly% = 0 OR lonly% = 2 THEN
		OPEN "msrmatx2.new" FOR RANDOM AS #2 LEN = 1
		CLOSE #2: KILL "msrmatx2.new"
	END IF
	'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\msrmat.inc'
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'    '#36 LEM=128
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'       '#44 LEN=300
	'$INCLUDE: '\tpmanuf\src\supX.INC'      '#45 LEN=7
	'
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$):  maxrmat% = CVI(msmisc.max3$)
	COLOR 2, 0
	X = 28
350
	T$ = "Y"
	IF LEN(T$) = 0 THEN T$ = "Y"
	IF T$ = "end" THEN GOTO endpgm
	IF T$ = "y" THEN T$ = "Y"
	IF T$ = "n" THEN T$ = "N"
	IF T$ <> "Y" AND T$ <> "N" THEN COLOR 14: LOCATE 24, 1: PRINT "Enter 'Y' to continue, or 'N' to exit.": COLOR 2: GOTO 350
	IF T$ = "N" THEN GOTO endpgm
	'
	'<<<<<<<<<<<<<<  O P E N  I N D E X
	'
	CALL index("OPEN ", ind%, "msrmatx2.new", 2, keyl%)
	sfx$ = "  ": osearch$ = "~~": N% = 0
	IF lonly% = 1 THEN CALL dolist
	'
	'
	'<<<<<<<<<<<<<<  L O A D   I N D E X
	nitems% = 1
	GET #38, nitems%, msrmat
	DO WHILE NOT EOF(38) AND nitems% <= maxrmat%
		'
		IF msrmat.no% = nitems% THEN
			'
			IF msrmat.search$ <> osearch$ THEN
				CALL searchindex(msrmat.search$, 45, found%)
				asuplr% = CVI(supx.wrrn$)
				IF NOT found% THEN asuplr% = -1
				 IF asuplr% < 1 OR asuplr% > maxsup% THEN
					 LSET osearch$ = "~~"
				 ELSE
					 GET #44, asuplr%': SOUND 50, 1
					 LSET osearch$ = msrmat.search$
				END IF
			END IF
			'
			ano$ = MKI$(msrmat.no%)
			MID$(sfx$, 1, 1) = MID$(ano$, 2, 1): MID$(sfx$, 2, 1) = MID$(ano$, 1, 1)

			'>-Set sort key
			aa$ = msrmat.desc1$ + msrmat.search$ + sfx$

			'>-Clean sort key
			FOR i% = 1 TO LEN(aa$) - 2
				IF MID$(aa$, i%, 1) = CHR$(0) THEN MID$(aa$, i%, 1) = " "
			NEXT


			LSET qk$ = aa$
			LSET rep$ = qk$
			CALL index("WRITE", ind%, qk$, 2, keyl%)
			N% = N% + 1
			LOCATE 10, 20: PRINT USING "|&|####| Total:####"; rep$; msrmat.no%; N%
		END IF
		GET #38, , msrmat
		nitems% = nitems% + 1
	LOOP

	CALL sndmsg("Read " + STR$(N%) + " items.")

	CLOSE #2
	shella$ = "copy msrmatx2.msf *.old"
	shellb$ = "copy msrmatx2.new *.msf"
	SHELL shella$
	SHELL shellb$

	IF lonly% = 2 THEN
		CALL index("OPEN ", ind%, "msrmatx2.new", 2, keyl%)
		CALL dolist
		CLOSE
		END '<---
	END IF


	'
endpgm:
	'

	CLOSE
	CALL exitpgm(apgm$): CHAIN apgm$

	END

SUB dolist

	'<<<<<<<<<<<<<<  L I S T   I N D E X
dolist:
	IF lonly% = 0 THEN EXIT SUB
	i% = 0: ind% = 0: a$ = "  ": l% = 2
	st$ = SPACE$(keyl%): hldst$ = SPACE$(keyl%)
	CLS
	COLOR 4: LOCATE 1, 1: PRINT "LIST OF RECORDS IN INDEX": COLOR 2
	pag% = 0: lin% = 9999
	'
	CALL index("FIRST", ind%, qk$, 2, keyl%)
	DO WHILE ind% > 0
		i% = i% + 1
		rec% = ind%
		GET #38, rec%, msrmat
		LSET st$ = LEFT$(qk$, LEN(qk$) - 2) + STR$(rec%)

		IF qk$ < hldst$ THEN BEEP: PRINT "Index corrupt!!": X$ = INPUT$(1)
		LSET hldst$ = qk$
		l% = l% + 1: IF l% > 22 THEN l% = 3':X$=INPUT$(1)
		lin% = lin% + 1
		IF lin% > 50 THEN GOSUB heading
		LOCATE l%, 1
		PRINT #99, st$ + "-" + STR$(rec%)
		PRINT st$: X$ = INPUT$(1)

		CALL index("READ ", ind%, qk$, 2, keyl%)
	LOOP

	EXIT SUB

heading:
	pag% = pag% + 1: IF pag% > 1 THEN PRINT #99, CHR$(12)

	PRINT #99, : PRINT #99, ; CHR$(14); msmisc.CC$
	PRINT #99, "#ACIDX03L"; TAB(60); DATE1$; " "; TIME$
	PRINT #99, "RAW MATERIAL INDEX";
	PRINT #99, TAB(69); "page: "; pag%
	PRINT #99, STRING$(79, "=")
	lin% = 1


RETURN

END SUB

FUNCTION format$ (VALUE!, definition$) STATIC
	dp% = 0

	'>- Find out how many decimal places,neg etc... -<
	work$ = STR$(VALUE!)
	edtcde$ = " ": dp% = 0
	X% = INSTR(definition$, ".")
	IF X% > 0 THEN
		FOR i% = X% TO LEN(definition$)
			IF MID$(definition$, i%, 1) = "b" THEN MID$(definition$, i%, 1) = "#": edtcde$ = "b"
			IF MID$(definition$, i%, 1) = "#" THEN dp% = dp% + 1
			NEXT
		X% = INSTR(work$, ".")
		IF X% = 0 THEN work$ = work$ + "."
		work$ = work$ + STRING$(dp%, "0")
		X% = INSTR(work$, ".")
		work$ = MID$(work$, 1, X% + dp%)
		END IF


	'>- Move from work pad into definition, from right to left -<
	neg% = MID$(work$, 1, 1) = "-"
	dollars% = 0
	work$ = MID$(work$, 2)
	defwork$ = definition$
	FOR i% = 1 TO LEN(definition$)
		IF MID$(definition$, i%, 1) = "$" THEN dollars% = -1: EXIT FOR
		NEXT

	'>- NOTE: The "d" represents the $ that i have added! -<
	IF dollars% THEN work$ = "d" + work$
	IF neg% THEN work$ = "-" + work$

	num.dollars% = 0
	W% = LEN(work$)

	FOR i% = LEN(defwork$) TO 1 STEP -1
		IF W% < 1 THEN EXIT FOR
		SELECT CASE MID$(defwork$, i%, 1)
		CASE "#": MID$(defwork$, i%, 1) = MID$(work$, W%, 1): W% = W% - 1
		CASE "$": MID$(defwork$, i%, 1) = MID$(work$, W%, 1): W% = W% - 1
		CASE ",": IF MID$(work$, W%, 1) = "d" THEN MID$(defwork$, i%, 1) = "#": i% = i% + 1
		CASE ".": W% = W% - 1
		CASE ELSE
		END SELECT

		NEXT

	FOR i% = 1 TO LEN(defwork$)
		IF MID$(defwork$, i%, 1) >= "1" AND MID$(defwork$, i%, 1) <= "9" THEN EXIT FOR
		IF MID$(defwork$, i%, 1) = "#" THEN MID$(defwork$, i%, 1) = " "
		IF MID$(defwork$, i%, 1) = "$" THEN MID$(defwork$, i%, 1) = " "
		IF MID$(defwork$, i%, 1) = "d" THEN MID$(defwork$, i%, 1) = "$"
		IF MID$(defwork$, i%, 1) = "," THEN MID$(defwork$, i%, 1) = " "
		NEXT

	'>- Zero suppress
	IF edtcde$ = "b" AND VALUE! = 0 THEN defwork$ = STRING$(LEN(defwork$), " ")

	format$ = defwork$
END FUNCTION

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB
