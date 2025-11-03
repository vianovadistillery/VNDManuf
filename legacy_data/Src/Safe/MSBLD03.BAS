DECLARE SUB copytotpmanuf ()
DECLARE SUB buildrmat (startrrn%, gap%)
DECLARE SUB chgtnt (chh%, chd%)
DECLARE SUB dolist ()
DECLARE FUNCTION format$ (VALUE!, definition$)
DECLARE SUB ResetMSRmat ()
DECLARE SUB searchindex (keyin$, chi%, found%)
	'///////////////////////////////////////////////////////////////////////
	'>> MSBLD03 - Build/List RMAT index
	'>> Then rebuild a sorted RMAT file.
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
	'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
	DIM SHARED lonly%, maxrmat%, maxsup%
	DIM SHARED keyl%, qk$, rep$
	apgm$ = "FIMENU"
	'/////////////////////////////////////////////////////
	'///  KEY LIST
	'///      KFLD    msrmat.search$     5
	'///      KFLD    msrmat.Desc1$     25
	'///      KFLD    msrmat.rno%        2  (Low byte,High byte)
	'//////////////////////////////////////////////////////
	CALL prtbtm(" F1 - exit.")
	keyl% = 32: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)
	COLOR 2
	'////////////////////////////////
	'0 - Build index
	'1 - List index only
	'2 - Both
	'3 - Build index and Rebuild Rmat
	'////////////////////////////////
	lonly% = 3
	'---------------------------------
	cursup$ = "    ": savsup$ = "@@@@": skey$ = "    "
	sp10$ = SPACE$(10)
	nul10$ = STRING$(10, 0)
	CLOSE

	IF lonly% = 1 OR lonly% = 2 THEN
		stdout$ = "CON"
		OPEN stdout$ FOR OUTPUT AS #99
	END IF

	'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\msrmat.inc'
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'    '#36 LEM=128
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'       '#44 LEN=300
	'$INCLUDE: '\tpmanuf\src\supX.INC'      '#45 LEN=7
	'$INCLUDE: '\tpmanuf\src\tnthed.inc'   '#54
	'$INCLUDE: '\tpmanuf\src\tntdet.inc'   '#55
	'$INCLUDE: '\tpmanuf\src\forhed.inc'   '#64
	'$INCLUDE: '\tpmanuf\src\fordet.inc'   '#65
	'
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$):  maxrmat% = CVI(msmisc.max3$)
	cca$ = msmisc.cc

	parm3$ = ENVIRON$("PARM3$"): IF MID$(parm3$, 1, 1) <> "." THEN cca$ = parm3$
	'>-Only allow in Tradepaints
	IF MID$(parm3$, 1, 3) <> "..." THEN GOTO endpgm

	IF lonly% = 0 OR lonly% = 2 OR lonly% = 3 THEN
		OPEN "msrmatx3.new" FOR RANDOM AS #2 LEN = 1
		CLOSE #2: KILL "msrmatx3.new"
	END IF

	startrrn% = 1

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
	CALL index("OPEN ", ind%, "msrmatx3.new", 2, keyl%)
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
			aa$ = msrmat.search$ + msrmat.desc1$ + sfx$

			'>-HYDROXINOL, CAN, LALELS & LABOUR are forces to the top
			'- with a dummy a sort key based on SG.
			spec% = 0
			IF msrmat.no% = 1 THEN spec% = -1
			IF INSTR(msrmat.desc1$, "HYDROXINOL") > 0 AND msrmat.sg > 0 THEN spec% = -1
			IF INSTR(msrmat.desc1$, "CAN.") > 0 AND msrmat.sg > 0 THEN spec% = -1
			IF INSTR(msrmat.desc1$, "LABEL.") > 0 AND msrmat.sg > 0 THEN spec% = -1
			IF INSTR(msrmat.desc1$, "LABOUR.") > 0 AND msrmat.sg > 0 THEN spec% = -1
			IF spec% THEN
				tmp4$ = format$(msrmat.sg, "#.##")
				aa$ = CHR$(0) + tmp4$ + msrmat.desc1$ + sfx$
			END IF

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
	shella$ = "copy " + "msrmatx3.msf " + "*.old"
	shellb$ = "copy " + "msrmatx3.new " + "*.msf"
	SHELL shella$
	SHELL shellb$

	IF lonly% = 2 THEN
		CALL index("OPEN ", ind%, "msrmatx3.new", 2, keyl%)
		lonly% = 2
		CALL dolist
		CLOSE
		END '<---
	END IF

'>>------------------------------
'>> The point of no return.
'>>------------------------------
	IF lonly% <> 3 THEN STOP  'Just in case!


	CALL setUp("BUILDING RAW MATERIALS")
'>> Build a new sorted rmat file
	CALL index("OPEN ", ind%, "msrmatx3.new", 2, keyl%)

	'?? Note set gap to 1 b4 rebuild and do tpmanuf first.
	gap% = 20
	gap% = 1

	CALL buildrmat(startrrn%, gap%)

	l% = 5
	l% = l% + 1
	LOCATE 5 + l%, 10: PRINT "Formulations."
	OPEN "forhed.asf" FOR RANDOM SHARED AS #154 LEN = 160
	OPEN "fordet.asf" FOR RANDOM SHARED AS #155 LEN = 32
	CALL chgtnt(154, 155)
	CLOSE #154
	CLOSE #155
	'
	l% = l% + 1
	LOCATE 5 + l%, 10: PRINT "Tints."
	OPEN "tnthed.asf" FOR RANDOM SHARED AS #154 LEN = 160
	OPEN "tntdet.asf" FOR RANDOM SHARED AS #155 LEN = 32
	CALL chgtnt(154, 155)
	CLOSE #154
	CLOSE #155
	'
	'-Other sets
	c$(1) = "BRIdet.asf"
	c$(2) = "hendet.asf"
	c$(3) = "hicdet.asf"
	c$(4) = "JOTdet.asf"
	c$(5) = "reddet.asf"
	c$(6) = "SICdet.asf"
	c$(7) = "WAGdet.asf"
	c$(8) = "WATdet.asf"

	FOR c% = 1 TO 8
		x3$ = MID$(c$(c%), 1, 3)

		fhdr$ = x3$ + "hed.asf"
		fdet$ = x3$ + "det.asf"
		a$ = DIR$(fdet$)
		IF a$ > "" THEN
			l% = l% + 1
			LOCATE 5 + l%, 10: PRINT "Other sets:" + c$(c%)
			OPEN fhdr$ FOR RANDOM SHARED AS #154 LEN = 160
			OPEN fdet$ FOR RANDOM SHARED AS #155 LEN = 32
			CALL chgtnt(154, 155)
			CLOSE #154
			CLOSE #155
		END IF
	NEXT

	l% = l% + 1
	LOCATE 5 + l%, 10: PRINT "Done."

	CLOSE
	shellc$ = "copy " + "msrmnew.msf " + "*.old"
	SHELL shellc$

	shellc$ = "copy " + "msrmnew.new " + "*.msf"
	SHELL shellc$

	'
endpgm:
	'
	CLOSE
	CALL exitpgm(apgm$): CHAIN apgm$

	END

SUB buildrmat (startrrn%, gap%)
	OPEN "MSRMNEW.NEW" FOR OUTPUT AS #138
	CLOSE #138
	OPEN "MSRMNEW.NEW" FOR RANDOM SHARED AS #138 LEN = LEN(msrmat)

	IF startrrn% < 1 THEN startrrn% = 1
	ind% = 0: a$ = "  ": l% = 2
	st$ = SPACE$(25): hldst$ = SPACE$(25)
	svSeach$ = "~~~~~"

	cpyto% = 0

	FOR j% = 1 TO startrrn% - 1
		CALL ResetMSRmat
		cpyto% = cpyto% + 1
		msrmat.no% = 0
		PUT #138, , msrmat
	NEXT


	CALL index("FIRST", ind%, qk$, 2, keyl%)
	DO WHILE ind% > 0
		cpyto% = cpyto% + 1
		cpyfrom% = ind%
		GET #38, cpyfrom%, msrmat
		LSET st$ = LEFT$(qk$, LEN(qk$) - 2) + STR$(cpyfrom%)
		IF cpyto% = startrrn% THEN svSeach$ = msrmat.search$

		IF qk$ < hldst$ THEN BEEP: PRINT "Index corrupt!!": X$ = INPUT$(1)
		LSET hldst$ = qk$

		IF msrmat.search$ <> svSeach$ THEN
			FOR j% = 1 TO gap%
				CALL ResetMSRmat
				cpyto% = cpyto% + 1
				msrmat.no% = cpyto%
				PUT #138, , msrmat
			NEXT
			GET #38, cpyfrom%, msrmat
			svSeach$ = msrmat.search$
		END IF

		'>-Change alternates
		found% = 0
		FOR i% = 1 TO 5
			IF msrmat.altno%(i%) = cpyfrom% THEN
				msrmat.altno%(i%) = cpyto%
			END IF
			IF msrmat.altno%(i%) > 9999 OR msrmat.altno%(i%) < 0 THEN
				msrmat.altno%(i%) = 0
			END IF
		NEXT

		'>-Store the new rrn on the OLD Raws file.
		msrmat.nno% = cpyto%
		PUT #38, cpyfrom%, msrmat

		msrmat.nno% = 0
		msrmat.no% = cpyto%
		PUT #138, , msrmat

		CALL index("READ ", ind%, qk$, 2, keyl%)
	LOOP

	CLOSE #138


	EXIT SUB
END SUB

SUB chgtnt (chh%, chd%)

	'>-Formulation header          Some formulations create Raws
	'>--------------------
	i% = 1
	GET #chh%, i%, tnthed
	DO WHILE NOT EOF(chh%) AND i% < 32000
		IF i% = tnthed.tnt THEN
			nno% = tnthed.asRmat%
			IF tnthed.asRmat > 0 THEN
				'>-The new rmat# is on the old rmat file.
				GET #38, tnthed.asRmat, msrmat
				nno% = msrmat.nno
			END IF

			GET #chh%, i%, tnthed
			tnthed.asRmat% = nno%
			PUT #chh%, i%, tnthed
		END IF

		GET #chh%, , tnthed: i% = i% + 1
	LOOP

	'>-Formulation details
	'---------------------
	i& = 1
	GET #chd%, i&, tntdet
	DO WHILE NOT EOF(chd%)
		IF i& = tntdet.tnt& THEN
			nno% = tntdet.rmat%
			IF tntdet.rmat > 0 THEN
				'>-The new rmat# is on the old rmat file.
				GET #38, tntdet.rmat, msrmat
				nno% = msrmat.nno
			END IF

			GET #chd%, i&, tntdet
			tntdet.rmat% = nno%
			PUT #chd%, i&, tntdet
		END IF

		IF i& MOD 1000 = 0 THEN CALL sndmsg("Record " + STR$(i&))
		GET #chd%, , tntdet: i& = i& + 1
	LOOP


END SUB

SUB copytotpmanuf
	a$ = ".\XXXX\MSRMNEW.MSF"
	STOP'??
	CLOSE #138
	CLOSE #38
	OPEN ".\XXXX\MSRMNEW.MSF" FOR RANDOM SHARED AS #138 LEN = LEN(msrmat)
	OPEN "MSRMNEW.MSF" FOR RANDOM SHARED AS #38 LEN = LEN(msrmat)

	rec% = 2600
	GET #138, rec%, msrmat
	DO WHILE NOT EOF(138)
		IF msrmat.active = "A" OR msrmat.active = "M" THEN
			PUT #38, rec%, msrmat
		END IF

		GET #138, , msrmat: rec% = rec% + 1
	LOOP


END SUB

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
		PRINT #99, st$
		PRINT st$: X$ = INPUT$(1)

		CALL index("READ ", ind%, qk$, 2, keyl%)
	LOOP

	EXIT SUB

heading:
	pag% = pag% + 1: IF pag% > 1 THEN PRINT #99, CHR$(12)

	PRINT #99, : PRINT #99, ; CHR$(14); msmisc.cc$
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

SUB ResetMSRmat
		msrmat.no = 0
		msrmat.desc1 = SPACE$(99)
		msrmat.desc2 = SPACE$(99)
		msrmat.nno = 0
		msrmat.search = SPACE$(99)
		msrmat.sg = 0
		msrmat.PurCost = 0
		msrmat.PurUnit = SPACE$(99)
		msrmat.UseCost = 0
		msrmat.useunit = SPACE$(99)
		msrmat.DealCost = 0
		msrmat.Dealqty = 0
		msrmat.Group = 0
		msrmat.active = SPACE$(99)
		msrmat.Volsolid = 0
		msrmat.Solidsg = 0
		msrmat.Wtsolid = 0
		msrmat.Notes = SPACE$(99)
		msrmat.soh = 0
		msrmat.Osoh = 0
		msrmat.date = SPACE$(99)
		msrmat.hazard = SPACE$(99)
		msrmat.cond = SPACE$(99)
		msrmat.altno(1) = 0
		msrmat.altno(2) = 0
		msrmat.altno(3) = 0
		msrmat.altno(4) = 0
		msrmat.altno(5) = 0
		msrmat.filler2 = SPACE$(99)
END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB
