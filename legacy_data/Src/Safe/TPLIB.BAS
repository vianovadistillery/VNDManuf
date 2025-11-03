DECLARE SUB setscreen (ok%)
DECLARE SUB shit1 (ok%)
DECLARE SUB exitpgm (apgm$)
DECLARE SUB menu (y0%, x0%, y1%, x1%, opt%, updwn%, check$)
DECLARE SUB INPNEW (in$, fmt!, updwn%, check$)
DECLARE SUB kcheck (updwn%, t$)
DECLARE SUB setup (heading$)
DECLARE SUB prtbtm (btm$)
DECLARE SUB sndmsg (themsg$)
DECLARE SUB box (x1%, y1%, x2%, y2%, fgnd%, bgnd%, Boxtype%)
DECLARE SUB index (q$, qf%, qk$, ch%, keyl%)
DECLARE SUB mail (in2!)
DECLARE SUB help (ys%, xs%)
DECLARE SUB round (in!, CUTOFF!)
DECLARE SUB aerror (RETCODE%)
DECLARE SUB setsec (in1%, in2%, password$, in3%, password2$)
'#########################################################################
'#########################################################################
'####                                                                 ####
'####                                                                 ####
'####           U S E R    L I B R A R Y   S O U R C E                ####
'####                                                                 ####
'####                                                                 ####
'#########################################################################
'#########################################################################
CALL setup("Hello")
'CALL INPNEW(a$, 104!, updwn%, "59,13")
'keyl% = 28: qk$ = SPACE$(keyl%)
'CALL index("OPEN ", ind%, "skux1.psf", 2, keyl%)
'CALL setsec(25, 4, "", 42, "1o4ap03")

SUB aerror (RETCODE%) STATIC
	REDIM EDATA%(11), EDATA$(11), ADATA$(14), BDATA$(14)
	xs% = POS(0): ys% = CSRLIN
	pcopyon% = 0: IF SCREEN(1, 10) <> 98 THEN pcopyon% = -1
	IF pcopyon% THEN PCOPY 0, 2

	EDATA%(1) = 7: EDATA$(1) = "Out of memory."
	EDATA%(2) = 24: EDATA$(2) = "Device time out"
	EDATA%(3) = 25: EDATA$(3) = "Printer not ready."
	EDATA%(4) = 53: EDATA$(4) = "File not found"
	EDATA%(5) = 57: EDATA$(5) = "Device I/O error"
	EDATA%(6) = 68: EDATA$(6) = "Device unavailable"
	EDATA%(7) = 61: EDATA$(7) = "Disk is full"
	EDATA%(8) = 72: EDATA$(8) = "Disk media error"
	EDATA%(9) = 71: EDATA$(9) = "Disk not ready or door is open."
	EDATA%(10) = 70: EDATA$(10) = "Record locked. Waiting for access..."
	EDATA%(11) = 67: EDATA$(11) = "Too many files on disk."

	ADATA$(1) = ""
	ADATA$(2) = ""
	ADATA$(3) = "                An error has occured on the printer"
	ADATA$(4) = ""
	ADATA$(5) = "        Please check;"
	ADATA$(6) = "                   (i) The paper indicator."
	ADATA$(7) = "                  (ii) The printer is switched on."
	ADATA$(8) = "                 (iii) The printer cable is seated properly."
	ADATA$(9) = ""
	ADATA$(10) = "To be set"
	ADATA$(11) = ""
	ADATA$(12) = "       Press SPACE BAR to try again or hit ESC to abort print."
	ADATA$(13) = ""
	ADATA$(14) = ""

	BDATA$(1) = ""
	BDATA$(2) = ""
	BDATA$(3) = "                An general error has occured."
	BDATA$(4) = ""
	BDATA$(5) = ""
	BDATA$(6) = ""
	BDATA$(7) = ""
	BDATA$(8) = ""
	BDATA$(9) = ""
	BDATA$(10) = ""
	BDATA$(11) = ""
	BDATA$(12) = "       Press SPACE BAR to try again or hit ESC to abort print."
	BDATA$(13) = ""
	BDATA$(14) = ""


	'General printer error routine
	ok% = 0
	FOR i% = 1 TO 10
		IF EDATA%(i%) = RETCODE% THEN ok% = -1: EXIT FOR
		NEXT

	'>- If error 70 "Permission Denied" its probably a record lock -<
	IF RETCODE% = 70 THEN
		AC$ = EDATA$(i%)
		GOSUB RECORD.LOCK: ok% = 0
		END IF
	IF ok% = 0 THEN GOTO xaerror

	CALL box(5, 5, 75, 19, 7, 4, 1)
	ADATA$(10) = "       Dos error number " + STR$(EDATA%(i%)) + " - '" + EDATA$(i%) + "'"
	BDATA$(10) = "       Dos error number " + STR$(EDATA%(i%)) + " - '" + EDATA$(i%) + "'"
	FOR i% = 1 TO 14
		LOCATE 6 + i%, 7
		IF ERRDEV = -32758 THEN
			PRINT ADATA$(i%)
			ELSE
			PRINT BDATA$(i%)
			END IF
		NEXT

	'>- Clear the buffer before allowing any new keystrokes -<
	finish% = 0: FOR i% = 1 TO 50: x$ = INKEY$: NEXT

	DO WHILE finish% = 0
		x$ = INKEY$
		IF x$ = " " THEN finish% = 1
		IF LEN(x$) = 1 AND RIGHT$(x$, 1) = CHR$(27) THEN finish% = 2
		LOOP

xaerror:
	IF finish% = 1 THEN RETCODE% = 0
	IF finish% = 2 THEN RETCODE% = -1
	IF pcopyon% THEN PCOPY 2, 0
	LOCATE ys%, xs%
EXIT SUB


RECORD.LOCK:
	LOCATE 24, 1
	COLOR 4, 3
	a$ = SPACE$(80)
	b$ = SPACE$(22) + AC$
	LSET a$ = b$
	PRINT a$;


	finish% = 0
	Stimer! = TIMER
	DO WHILE finish% = 0
		IF ABS(TIMER - Stimer!) > 1 THEN finish% = 1
		x$ = INKEY$
		IF x$ = " " THEN finish% = 1
		IF LEN(x$) = 1 AND RIGHT$(x$, 1) = CHR$(27) THEN finish% = 2
		LOOP

	COLOR 2, 0

RETURN

END SUB

'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
'บ       Draw a box and optional fill it                                 บ
'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
'Boxtype%   :1/Single box   2/Double box    -ve don't fill box
SUB box (y1%, x1%, y2%, x2%, fgnd%, bgnd%, Boxtype%)
	swaped% = 0: IF y2% > 25 THEN SWAP x1%, y1%: SWAP x2%, y2%: swaped% = -1
	pcopyon% = 0: IF SCREEN(1, 10) <> 98 THEN pcopyon% = -1

	x0% = POS(0): y0% = CSRLIN
	COLOR fgnd%, bgnd%
	IF NOT pcopyon% THEN fg% = 7: bg% = 0
	fill% = 1: IF Boxtype% < 0 THEN fill% = 0: Boxtype% = 0 - Boxtype%
	LENTOP% = x2% - x1% - 1: LENSIDE% = y2% - y1%

	SELECT CASE Boxtype%
	CASE 1:   a1% = 192: a2% = 196: a3% = 217: a4% = 218: a5% = 191: a6% = 179
	CASE 2:   a1% = 200: a2% = 205: a3% = 188: a4% = 201: a5% = 187: a6% = 186
	CASE ELSE: a1% = 0: a2% = 0: a3% = 0: a4% = 0: a5% = 0: a6% = 0
	END SELECT

	'Bottom
	a$ = CHR$(a1%) + STRING$(LENTOP%, a2%) + CHR$(a3%)
	LOCATE y2%, x1%: PRINT a$;

	'Top
	a$ = CHR$(a4%) + STRING$(LENTOP%, a2%) + CHR$(a5%)
	LOCATE y1%, x1%: PRINT a$;


	'Left side
	a$ = CHR$(a6%)
	FOR i% = 1 TO LENSIDE% - 1
		LOCATE y1% + i%, x1%: PRINT a$;
		NEXT

	'Right side
	FOR i% = 1 TO LENSIDE% - 1
		LOCATE y1% + i%, x2%: PRINT a$;
		NEXT

	' Fill the box with the background colour
	IF fill% THEN
		x1% = x1% + 1: IF x1% > 80 THEN x1% = 80
		a$ = SPACE$(LENTOP%)
		FOR i% = 1 TO LENSIDE% - 1
			LOCATE y1% + i%, x1%: PRINT a$;
			NEXT
		END IF

	 IF swaped% THEN SWAP x1%, y1%: SWAP x2%, y2%
	'Set cursor back to the same place
	LOCATE y0%, x0%
END SUB

SUB exitpgm (apgm$) STATIC
	runmode$ = " ": IF SCREEN(1, 60) = 81 THEN runmode$ = "QBX"


	IF runmode$ = "QBX" THEN
		path$ = CURDIR$
		IF INSTR(apgm$, "SRC\") < 1 THEN
		apgm$ = "SRC\" + apgm$
		END IF
	ELSE
		path$ = "C:\TPEXE"
	END IF

	IF INSTR(apgm$, path$) < 1 THEN
		apgm$ = path$ + "\" + apgm$
	END IF

END SUB

'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
'บ                             H E L P                                   บ
'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
SUB help (ys%, xs%) STATIC
	top% = 1: IF ys% <= 12 THEN top% = ys% + 1
	btm% = 23: IF ys% > 12 THEN btm% = ys% - 1
	nbr% = btm% - top% - 1

	CALL box(1, top%, 80, btm%, 8, 4, 1)
	OPEN "HELP.HLP" FOR RANDOM AS #98 LEN = 78
	FIELD #98, 78 AS a$
	FOR i% = 1 TO nbr%
		GET #98, i%
		LOCATE top% + i%, 2: PRINT a$;
		NEXT
	x$ = INPUT$(1)
	CLOSE #98
END SUB

SUB index (q$, qf%, qk$, ch%, keyl%) STATIC
	'************************************************************************
	'****     V A R I A B L E     K E Y     L E N G H T    I N D E X     ****
	'************************************************************************
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ                   I N D E X    R O U T I N E                          บ
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
	'               Q$ = OPTION
	'               QF%= ERROR INDICATOR
	'               QK$= KEY OF FILE
	'               CH%= CHANNEL OF FILE
	'             KEYL%= KEY LENGTH
	'
	IF q$ <> "OPEN " THEN
		FIELD #ch%, 2 AS qr$, 2 AS qd$, 2 AS qm$
		FIELD #ch%, 2 AS LNUM$, 2 AS RNUM$, 2 AS QBAL$, 1 AS QDEL$, keyl% AS qkey$
		END IF
	DIM q%(500)

	' DEBUG OPTIONS IF =1
	' DEBUG OPTIONS AND wait FOR INPUT IF =2
	DEBUG% = 0
	qf% = 0
	OLDK$ = qkey$: OLDK1$ = qkey$: OLDK2$ = qkey$
	OLDL$ = LNUM$: OLDL1$ = LNUM$: OLDL2$ = LNUM$
	OLDR$ = RNUM$: OLDR1$ = RNUM$: OLDR2$ = RNUM$


	SELECT CASE q$
	CASE "OPEN ": GOSUB IOPEN
	CASE "CHAIN": GOSUB ICHAIN
	CASE "WRITE": GOSUB IWRITE
	CASE "DUMP ": GOSUB IDUMP
	CASE "FIRST": GOSUB IFIRST
	CASE "READ ": GOSUB IREAD
	CASE "READP": GOSUB IREADP
	CASE "DELET": GOSUB IDELET
	CASE ELSE: LSET q$ = "ERROR"
	END SELECT


	LSET qk$ = qkey$
	'>> If no error reutrn record number in indicator
	IF q$ = "READ " OR q$ = "READP" OR q$ = "CHAIN" OR q$ = "FIRST" THEN
	IF keyl% > 1 THEN
		a$ = RIGHT$(qk$, 2): sfx$ = "  "
		MID$(sfx$, 1, 1) = MID$(a$, 2, 1): MID$(sfx$, 2, 1) = MID$(a$, 1, 1)
		IF qf% = -1 THEN qf% = 0 - CVI(sfx$) ELSE qf% = CVI(sfx$)
		END IF
		END IF

	IF DEBUG% > 0 THEN LOCATE 24, 40: PRINT q$;
	IF DEBUG% = 2 THEN x$ = INPUT$(1)
	EXIT SUB
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ        O P E N   A    F I L E                                         บ
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
IOPEN:
	IF DEBUG% > 0 THEN LOCATE 24, 1: PRINT "ฎ--O P E N  --ฏ";
	IF DEBUG% = 2 THEN x$ = INPUT$(1)
	OPEN qk$ FOR RANDOM SHARED AS #ch% LEN = keyl% + 7
	FIELD #ch%, 2 AS qr$, 2 AS qd$, 2 AS qm$

	GET #ch%, 1: qr% = CVI(qr$): qd% = CVI(qd$): qm% = CVI(qm$)
	IF MID$(qr$, 1, 1) = CHR$(0) THEN
		qr% = 1: qm% = 0: qd% = 0: LSET qr$ = MKI$(qr%)
		LSET qm$ = MKI$(qm%): LSET qd$ = MKI$(qd%)
		LSET QDEL$ = " "
		PUT #ch%, 1
		IF DEBUG% > 0 THEN LOCATE 24, 1: PRINT "ฎ--F I R S T--ฏ";
		IF DEBUG% = 2 THEN x$ = INPUT$(1)
		END IF
	RETURN
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ   C H A I N    O U T   T O   I N D E X   F O R   L I K E   K E Y
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
ICHAIN:
	IF DEBUG% > 0 THEN LOCATE 24, 1: PRINT "ฎ--C H A I N--ฏ";
	IF DEBUG% = 2 THEN x$ = INPUT$(1)
	q% = 2: QL% = 0: qf% = -2
	IF qr% = 1 THEN
		qf% = -1: QL% = 1: q%(QL%) = 0

	ELSE
	DO WHILE qf% = -2
		QL% = QL% + 1: q%(QL%) = q%
		GET #ch%, q%
		IF qk$ = qkey$ THEN qf% = 0: EXIT DO
			IF qk$ < qkey$ THEN
				'๐๐๐๐๐ LOW END OF SEARCH
				LNUM% = CVI(LNUM$)
				IF LNUM% = 0 THEN qf% = -1 ELSE q% = LNUM%
			ELSE
				'๐๐๐๐๐ HIGH END OF SEARCH
				RNUM% = CVI(RNUM$)
				IF RNUM% = 0 THEN qf% = -1 ELSE q% = RNUM%
			END IF
		LOOP
	END IF

	IF QDEL$ = "D" AND q$ <> "WRITE" THEN qf% = -1'Logical delete
	IF QL% > 1 AND q$ <> "WRITE" AND q$ <> "DELET" THEN QL% = QL% - 1

	RETURN
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ        A D D    R E C O R D S   T O   T  H E   I N D E X              บ
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
IWRITE:
	IF DEBUG% > 0 THEN LOCATE 24, 1: PRINT "ฎ--W R I T E--ฏ";
	IF DEBUG% = 2 THEN x$ = INPUT$(1)
	GOSUB ICHAIN

	add% = 1: DEL% = 0: DEEPER% = 0

	IF qf% = 0 THEN '>> Search found
		IF QDEL$ = "D" THEN
			GET #ch%, q%
			LSET QDEL$ = " "
			PUT #ch%, q%
			DEL% = -1
			qf% = 0

		ELSE
			q$ = "EXISTS": qf% = -1
			add% = 0
			END IF

	ELSE  '>> Search not found, add new node
		IF qr% = 1 THEN
		BAL% = 0: DEEPER% = 1

		ELSE
		'๐๐๐๐๐ SET PREVIOUS INDEX RECORD
		GET #ch%, q%
		IF CVI(LNUM$) = 0 AND CVI(RNUM$) = 0 THEN DEEPER% = 1
		BAL% = 1
		QBAL% = CVI(QBAL$)
		IF qk$ < qkey$ THEN
			LSET LNUM$ = MKI$(qr% + 1)
			IF CVI(RNUM$) <> 0 THEN LSET QBAL$ = MKI$(QBAL% - 1): BAL% = 0
			END IF
		IF qk$ > qkey$ THEN
			LSET RNUM$ = MKI$(qr% + 1)
			IF CVI(LNUM$) <> 0 THEN LSET QBAL$ = MKI$(QBAL% + 1): BAL% = 0
			END IF

		PUT #ch%, q%
		'๐๐๐๐๐ SET NEW INDEX RECORD
		END IF
	q% = qr% + 1
	LSET LNUM$ = MKI$(0): LSET RNUM$ = MKI$(0)
	LSET qkey$ = qk$
	LSET QBAL$ = MKI$(0)
	OLDQ% = q%: OLDK$ = qkey$: OLDL$ = LNUM$: OLDR$ = RNUM$
	LSET QDEL$ = " "
	PUT #ch%, q%: qf% = 0
	'๐๐๐๐๐ WALK BACK UP TREE AND BALANCE
	DO WHILE BAL%
		OLDQ2% = OLDQ%: OLDK2$ = OLDK$: OLDL2$ = OLDL$: OLDR2$ = OLDR$
		OLDQ% = q%: OLDK$ = qkey$: OLDL$ = LNUM$: OLDR$ = RNUM$
		q% = q%(QL%)
		GET #ch%, q%
		IF CVI(LNUM$) = OLDQ% THEN ADJ% = -1
		IF CVI(RNUM$) = OLDQ% THEN ADJ% = 1
		QBAL% = CVI(QBAL$) + ADJ%

		SELECT CASE QBAL%
		CASE IS < -1
			GOSUB RRIGHT: DEEPER% = 0
		CASE IS > 1
			GOSUB RLEFT: DEEPER% = 0
		CASE ELSE
			LSET QBAL$ = MKI$(QBAL%)
			PUT #ch%, q%
			QL% = QL% - 1: IF QL% < 1 THEN BAL% = 0
		END SELECT

		LOOP
	END IF

	'๐๐๐๐๐ UPDATE HEADER RECORD
	LNUM% = CVI(LNUM$): RNUM% = CVI(RNUM$)
	GET #ch%, 1
	qr% = CVI(qr$): qm% = CVI(qm$): qd% = CVI(qd$)
	qr% = qr% + add%
	qd% = qd% + DEL%
	qm% = qm% + DEEPER%
	BAL% = 0: add% = 0: DEEPER% = 0
	LSET qr$ = MKI$(qr%): LSET qm$ = MKI$(qm%): LSET qd$ = MKI$(qd%)
	PUT #ch%, 1

RETURN

RRIGHT:
	LNUM% = CVI(LNUM$): RNUM% = CVI(RNUM$)
	IF CVI(OLDL$) = OLDQ2% THEN
		IF DEBUG% > 0 THEN LOCATE 24, 1: PRINT "ฎ--ROLL RIGHT, EXTERNAL--ฏ AT "; qkey$;
		IF DEBUG% = 2 THEN x$ = INPUT$(1)
		LSET OLDK1$ = qkey$
		LSET qkey$ = OLDK$
		LSET OLDR$ = RNUM$
		LSET RNUM$ = LNUM$
		LSET LNUM$ = OLDL$
		LSET QBAL$ = MKI$(0)
		PUT #ch%, q%

		GET #ch%, LNUM%
		LSET qkey$ = OLDK1$
		LSET LNUM$ = RNUM$
		LSET RNUM$ = OLDR$
		LSET QBAL$ = MKI$(0)
		PUT #ch%, LNUM%


	ELSE
		IF DEBUG% > 0 THEN LOCATE 24, 1: PRINT "ฎ--ROLL RIGHT, INTERNAL--ฏ AT "; qkey$;
		IF DEBUG% = 2 THEN x$ = INPUT$(1)
		LSET OLDK1$ = qkey$
		LSET OLDR1$ = RNUM$
		LSET qkey$ = OLDK2$
		LSET RNUM$ = OLDR$
		LSET QBAL$ = MKI$(0)
		PUT #ch%, q%

		GET #ch%, OLDQ%
		LSET RNUM$ = OLDL2$
		LSET QBAL$ = MKI$(0)
		PUT #ch%, OLDQ%

		GET #ch%, OLDQ2%
		LSET qkey$ = OLDK1$
		LSET LNUM$ = RNUM$
		LSET RNUM$ = OLDR1$
		LSET QBAL$ = MKI$(0)
		PUT #ch%, OLDQ2%
		END IF
	BAL% = 0
	RETURN

RLEFT:
	LNUM% = CVI(LNUM$): RNUM% = CVI(RNUM$)
	IF CVI(OLDR$) = OLDQ2% THEN
		IF DEBUG% > 0 THEN LOCATE 24, 1: PRINT "ฎ--ROLL LEFT, EXTERNAL--ฏ AT "; qkey$;
		IF DEBUG% = 2 THEN x$ = INPUT$(1)
		LSET OLDK1$ = qkey$
		LSET qkey$ = OLDK$
		LSET OLDL$ = LNUM$
		LSET LNUM$ = RNUM$
		LSET RNUM$ = OLDR$
		LSET QBAL$ = MKI$(0)
		PUT #ch%, q%
		GET #ch%, RNUM%
		LSET qkey$ = OLDK1$
		LSET RNUM$ = LNUM$
		LSET LNUM$ = OLDL$
		LSET QBAL$ = MKI$(0)
		PUT #ch%, RNUM%
	ELSE
		IF DEBUG% > 0 THEN LOCATE 24, 1: PRINT "ฎ--ROLL LEFT, INTERNAL--ฏ AT "; qkey$;
		IF DEBUG% = 2 THEN x$ = INPUT$(1)
		LSET OLDK1$ = qkey$
		LSET OLDL1$ = LNUM$
		LSET qkey$ = OLDK2$
		LSET LNUM$ = OLDL$
		LSET QBAL$ = MKI$(0)
		PUT #ch%, q%

		GET #ch%, OLDQ%
		LSET LNUM$ = OLDR2$
		LSET QBAL$ = MKI$(0)
		PUT #ch%, OLDQ%

		GET #ch%, OLDQ2%
		LSET qkey$ = OLDK1$
		LSET RNUM$ = LNUM$
		LSET LNUM$ = OLDL1$
		LSET QBAL$ = MKI$(0)
		PUT #ch%, OLDQ2%
		END IF
	BAL% = 0
	RETURN
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ        D U M P   I N D E X                                            บ
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
IDUMP:
	CLS
	prt.len% = keyl%
	IF prt.len% < 10 OR prt.len% > 40 THEN prt.len% = 40

	GET #ch%, 1: qr% = CVI(qr$): qd% = CVI(qd$): qm% = CVI(qm$)
	PRINT USING "Number of records in file:#####"; qr% - 1
	PRINT USING "Number of deleted records:#####"; qd%
	PRINT USING "Maximum depth of treepath:#####"; qm%
	PRINT
	PRINT " Seq   Key" + SPACE$(prt.len% + 4) + "lnum  Rnum    Bal  Del"
	FOR i% = 2 TO qr% + qd% + 2
		GET #ch%
		l$ = STR$(CVI(LNUM$) - 1): r$ = STR$(CVI(RNUM$) - 1)
		QBAL% = CVI(QBAL$)
		IF CVI(LNUM$) = 0 THEN l$ = SPACE$(5)
		IF CVI(RNUM$) = 0 THEN r$ = SPACE$(5)
		IF QDEL$ = CHR$(0) THEN LSET QDEL$ = " "
		ab$ = RIGHT$(qkey$, 2)
		sfx$ = "  ": MID$(sfx$, 1, 1) = MID$(ab$, 2, 1): MID$(sfx$, 2, 1) = MID$(ab$, 1, 1)
		ab = CVI(sfx$)
		AAA$ = LEFT$(qkey$, prt.len% - 2)
		AAA$ = AAA$ + STR$(ab)
		PRINT USING "####  |&|  \  \   \  \   ###   |!|"; i% - 1; AAA$; l$; r$; QBAL%; QDEL$
		NEXT
	PRINT : PRINT "Press SPACE BAR to continue": COLOR 2
	x$ = "": DO UNTIL x$ = " ": x$ = INKEY$: LOOP
	RETURN
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ        R E A D   F I R S T   R E C O R D   I N   F I L E              บ
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
IFIRST:
	IF DEBUG% > 0 THEN LOCATE 24, 1: PRINT "ฎ--F I R S T--ฏ";
	IF DEBUG% = 2 THEN x$ = INPUT$(1)
	q% = 2: QL% = 0
	GOSUB LOWESTNODE'Get lowest node
	RETURN
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ        R E A D   I N D E X   I N   O R D E R                          บ
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
IREAD:
	IF DEBUG% > 0 THEN LOCATE 24, 1: PRINT "ฎ--R E A D  --ฏ";
	IF DEBUG% = 2 THEN x$ = INPUT$(1)
	IF CVI(RNUM$) > 0 THEN
			'๐๐๐๐๐ Right node found ๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐
			QL% = QL% + 1: q%(QL%) = q%
			q% = CVI(RNUM$)
			GOSUB LOWESTNODE'Get lowest node
		ELSE
			'๐๐๐๐๐ Left node found ๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐
LEFTAGN:
			OLDQ% = q%: q% = q%(QL%): QL% = QL% - 1

			IF q% <= 0 THEN
				qf% = -1
			ELSE
				GET #ch%, q%
				IF CVI(RNUM$) = OLDQ% THEN GOTO LEFTAGN
					END IF
		END IF

	IF qf% = 0 AND QDEL$ = "D" THEN GOTO IREAD
XIREAD:
	RETURN
	'๐๐๐๐๐ Get lowest node in a sub tree ๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐
LOWESTNODE:
	GET #ch%, q%
	LNUM% = CVI(LNUM$)
	DO WHILE LNUM% > 0
		QL% = QL% + 1
		q%(QL%) = q%
		q% = LNUM%
		GET #ch%, q%
		LNUM% = CVI(LNUM$)
		LOOP
	RETURN
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ        R E A D P  I N D E X   I N   R E V E R S E  O R D E R          บ
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
IREADP:
	IF DEBUG% > 0 THEN LOCATE 24, 1: PRINT "ฎ--R E A D P--ฏ";
	IF DEBUG% = 2 THEN x$ = INPUT$(1)
	IF CVI(LNUM$) > 0 THEN
			'๐๐๐๐๐ Left node found ๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐
			QL% = QL% + 1: q%(QL%) = q%
			q% = CVI(LNUM$)
			GOSUB HIGHESTNODE'Get highest node
		ELSE
			'๐๐๐๐๐ Right node found ๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐
RIGHTAGN:
			OLDQ% = q%: q% = q%(QL%): QL% = QL% - 1

			IF q% <= 0 THEN
				qf% = -1
			ELSE
				GET #ch%, q%
				IF CVI(LNUM$) = OLDQ% THEN GOTO RIGHTAGN
			END IF
		END IF

	IF qf% = 0 AND QDEL$ = "D" THEN GOTO IREADP
XIREADP:
	RETURN
	'๐๐๐๐๐ Get highest node in a sub tree ๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐
HIGHESTNODE:
	GET #ch%, q%
	RNUM% = CVI(RNUM$)
	DO WHILE RNUM% > 0
		QL% = QL% + 1
		q%(QL%) = q%
		q% = RNUM%
		GET #ch%, q%
		RNUM% = CVI(RNUM$)
		LOOP
	RETURN
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ     D E L E T E   A   R E C O R D                                     บ
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
IDELET:
	IF DEBUG% > 0 THEN LOCATE 24, 1: PRINT "ฎ--D E L E T E--ฏ";
	IF DEBUG% = 2 THEN x$ = INPUT$(1)
	GOSUB ICHAIN
	DEL% = 0: add% = 0
	IF qf% = -1 OR QDEL$ = "D" THEN
		q$ = "NOT FOUND"

	ELSE
		LSET QDEL$ = "D"
		PUT #ch%, q%: qf% = 0
		DEL% = 1: add% = -1
		END IF

	'๐๐๐๐๐ UPDATE HEADER RECORD
	LNUM% = CVI(LNUM$): RNUM% = CVI(RNUM$)
	GET #ch%, 1
	qr% = CVI(qr$): qd% = CVI(qd$)
	qr% = qr% + add%
	qd% = qd% + DEL%
	LSET qr$ = MKI$(qr%): LSET qd$ = MKI$(qd%)
	PUT #ch%, 1
	RETURN
END SUB

SUB INPNEW (in$, fmt, updwn%, check$) STATIC
'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
'บ            G E N E R A L    I N P U T    R O U T I N E                บ
'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
'IN$           String to be input.
'FMT      -9.2 Nine long with two decimal places signed
'          9.3 Nine long with three decimal places absolute
'              Max length 9
'          110 Alpha 10 long
'          125 Alpha 25 long
'          100 Date format
'          200 and above is treated like a numeric until an alpha is entered
'              then the whole field is treated like an alpha.
'            0 No Display Fn keys only
'
'UPDWN%/
'EDTCDE The hundreds digit is the forground colour.
'       The tens digit is the background colour.
'       If these are invalid COLOR 7,1 is assumed. (White on blue)
'       RETURNS AS:
'       All extended codes (see INKEY$) are supported and are returned in this
'       field. TAB is treated as an extedned code of ASCII 9
'
'CHECK$ Is the list of keys that will exit the routine
'       However if it is a null set the field is displayed and exits immediatly.
'       Can be "ALL". (Means all extended codes,ESC and TAB)
'
'       TILDA "~" is reserved for a field refresh.
'       QUOTE "`" is reserved for a help.
'       SHIFT (CR) Clears to the end of the field.
'
DIM bpos AS LONG, secdate AS LONG, seccount AS LONG
date1$ = "  /  /  ": MID$(date1$, 1, 2) = MID$(DATE$, 4, 2): MID$(date1$, 4, 2) = MID$(DATE$, 1, 2): MID$(date1$, 7, 2) = MID$(DATE$, 9, 2)
begin$ = in$: begfmt = fmt: begupdwn% = updwn%
xs% = POS(0): ys% = CSRLIN
pcopyon% = 0: IF SCREEN(1, 10) <> 98 THEN pcopyon% = -1

updwn$ = STR$(updwn%): fg% = 7: bg% = 1
IF SCREEN(1, 10) <> 32 THEN fg% = 0: bg% = 7
of% = 2: OBND = 0: tf% = 8: tb% = 3
x = SCREEN(ys%, xs%, 1): of% = (x MOD 16): ob% = (((x - of%) / 16) MOD 128)'Set prev colour
IF x > 127 THEN of% = of% + 16: ob% = ob% + 16
x = SCREEN(1, 72, 1): tf% = (x MOD 16): tb% = (((x - tf%) / 16) MOD 128)
IF x > 127 THEN tf% = tf% + 16: tb% = tb% + 16

BEGINALL:
	GOSUB DEFN

	updwn% = 0
	astart! = FIX(TIMER)
	scrn! = FIX(TIMER)

DO WHILE finish%
anow! = FIX(TIMER)
IF ABS(anow! - astart!) > 0 THEN
	 t$ = TIME$
	 LOCATE 1, 72: COLOR tf%, tb%: PRINT t$;
	 astart! = anow!
	 CALL setscreen(ok%)
END IF

IF ABS(anow! - scrn!) > 199 AND imax% = 0 THEN updwn% = -1: finish% = 0
	IF ABS(anow! - scrn!) > 200 AND pcopyon% THEN
		GOSUB SCRNSAVER
	ELSE
		LOCATE ys%, xs% + xpos% - 1, csr%
		x$ = INKEY$'<<<<< The input >>>>>
	END IF
	IF x$ = "" THEN GOTO ALOOP
	scrn! = FIX(TIMER)
	MID$(in2$, 1) = x$
	in = ASC(LEFT$(in2$, 1))                'check 1st char's ASCII code
	chr% = 0

'//////////////////////////////////////////////////////////////////
'PART 1 - Extended codes
'//////////////////////////////////////////////////////////////////
 IF in = 0 THEN                           'if 0 then extented code
	in2 = ASC(RIGHT$(in2$, 1))
	dphit% = 0
	SELECT CASE in2
	CASE 71 'Home ,move cursor to start position
		xpos% = 1
		updwn% = in2
		CALL kcheck(updwn%, check$)
		IF updwn% <> 0 THEN updwn% = in2: finish% = 0
	CASE 77 'Cursor right
		IF xpos% < xmax% THEN xpos% = xpos% + 1
		IF type$ = "D" AND (xpos% = 3 OR xpos% = 6) THEN xpos% = xpos% + 1
		updwn% = in2
		CALL kcheck(updwn%, check$)
		IF updwn% <> 0 THEN updwn% = in2: finish% = 0
	CASE 75 'Cursor left
		IF xpos% > 1 THEN xpos% = xpos% - 1
		IF type$ = "D" AND (xpos% = 3 OR xpos% = 6) THEN xpos% = xpos% - 1
		updwn% = in2
		CALL kcheck(updwn%, check$)
		IF updwn% <> 0 THEN updwn% = in2: finish% = 0
	CASE 79 '<<< End >>> Move cursor to end of valid char
		IF xmax% > 1 THEN
			xpos% = xmax%
			DO WHILE xpos% > 1 AND MID$(in$, xpos%, 1) = " ": xpos% = xpos% - 1: LOOP
			IF xpos% < xmax% THEN xpos% = xpos% + 1
			IF xpos% = 2 AND MID$(in$, xpos% - 1, 1) = " " THEN xpos% = xpos% - 1
			END IF
		updwn% = in2
		CALL kcheck(updwn%, check$)
		IF updwn% <> 0 THEN updwn% = in2: finish% = 0
	CASE 82 '<<< Insert >>> If room and if cursor within
		IF ainsert$ = "Y" THEN
			ainsert$ = "N"
			COLOR tf%, tb%
			LOCATE 1, 65: PRINT "Over   ";
			ELSE
			ainsert$ = "Y"
			COLOR tf%, tb%
			LOCATE 1, 65: PRINT "Insert ";
			END IF
	CASE 83 '<<< Delete >>> If cursor is within string
		ok% = -1
		IF type$ = "D" THEN ok% = 0
		IF neg$ = "Y" AND xpos% = 1 THEN ok% = 0
		IF xpos% = 0 THEN ok% = 0
		IF ok% THEN 'remove char and add space at end
			MID$(in$, xpos%) = MID$(in$, xpos% + 1) + " "
			LOCATE ys%, xs%: COLOR fg%, bg%: PRINT in$;
			END IF
	CASE 115 '^Left arrow (Previous word)
			IF xpos% > 1 THEN xpos% = xpos% - 1
			DO WHILE xpos% > 1 AND ok%
				xpos% = xpos% - 1: x% = SCREEN(ys%, xs% + xpos% - 1)
				ok% = 0
				IF x% >= 48 AND x% <= 47 THEN ok% = -1'0-9
				IF x% >= 65 AND x% <= 90 THEN ok% = -1'A-Z
				IF x% >= 97 AND x% <= 122 THEN ok% = -1'a-z
				LOOP
				IF xpos% < xmax% AND xpos% > 1 THEN xpos% = xpos% + 1
				IF type$ = "D" AND (xpos% = 3 OR xpos% = 6) THEN xpos% = xpos% - 1
	CASE 116 '^Right arrow (Next word)
			IF xpos% < xmax% THEN xpos% = xpos% + 1
			ok% = -1
			DO WHILE xpos% < xmax% AND ok%
				xpos% = xpos% + 1: x% = SCREEN(ys%, xs% + xpos% - 1)
				ok% = 0
				IF x% >= 48 AND x% <= 47 THEN ok% = -1'0-9
				IF x% >= 65 AND x% <= 90 THEN ok% = -1'A-Z
				IF x% >= 97 AND x% <= 122 THEN ok% = -1'a-z
				LOOP
				IF xpos% < xmax% THEN xpos% = xpos% + 1
				IF type$ = "D" AND (xpos% = 3 OR xpos% = 6) THEN xpos% = xpos% + 1
	CASE 104 TO 113, 139, 140'Alt F1 to F10 (Used for Internal mail)
		IF SCREEN(1, 11) <> ASC("m") AND pcopyon% THEN
			mail.begin$ = begin$: mail.begfmt = begfmt
			mail.y0% = ys%: mail.x0% = xs%
			CALL mail(in2)
			begin$ = mail.begin$: begfmt = mail.begfmt
			xs% = mail.x0%: ys% = mail.y0%
			finish% = 0: begin% = 1
			END IF
	CASE 146 'QBX
			IF SCREEN(1, 60) = 81 THEN
				LOCATE 1, 60: COLOR tf%, tb%: PRINT "   ";
				ELSE
				LOCATE 1, 60: COLOR tf%, tb%: PRINT "QBX";
				LOCATE 1, 2: PRINT USING "# ##,###"; ver; seccount
				END IF
	CASE ELSE
		updwn% = in2
		CALL kcheck(updwn%, check$)
		IF updwn% <> 0 THEN updwn% = in2: finish% = 0'Any extended code
	END SELECT
 '//////////////////////////////////////////////////////////////////
 'PART II - If << NOT extented >> code
 '//////////////////////////////////////////////////////////////////
	ELSE
	SELECT CASE in
	CASE 3 '^C - Change case
		x% = SCREEN(ys%, xs% + xpos% - 1)
		IF x% >= 65 AND x% <= 90 THEN chr% = x% + 32'A-Z
		IF x% >= 97 AND x% <= 122 THEN chr% = x% - 32'a-z
		IF chr% = 0 AND xpos% < xmax% THEN xpos% = xpos% + 1
	CASE 8 'Left arror. Back space
		SELECT CASE type$
		CASE "A"
			IF xpos% > 1 THEN
				MID$(in$, xpos% - 1) = MID$(in$, xpos%) + " ": xpos% = xpos% - 1
				LOCATE ys%, xs%: COLOR fg%, bg%: PRINT in$;
				END IF
		CASE "N"
			IF xpos% > 1 THEN
				MID$(in$, xpos% - 1) = MID$(in$, xpos%) + " ": xpos% = xpos% - 1
				LOCATE ys%, xs%: COLOR fg%, bg%: PRINT in$;
				END IF
		CASE "D": IF xpos% > 1 THEN xpos% = xpos% - 1
			IF xpos% = 3 OR xpos% = 6 THEN xpos% = xpos% - 1
		END SELECT
	CASE 9 'Tab
		updwn% = in
		CALL kcheck(updwn%, check$)
		IF updwn% <> 0 THEN finish% = 0
	CASE 10 '^(CR)- Clear to end of line
		MID$(in$, xpos%) = SPACE$(xmax%)
		a$ = MID$(in$, xpos%): xw% = xs% + xpos% - 1
		LOCATE ys%, xw%: COLOR fg%, bg%: PRINT a$;
	CASE 13 '(CR)- Possible exit of field
		updwn% = in
		CALL kcheck(updwn%, check$)
		IF updwn% <> 0 THEN finish% = 0
	CASE 19 '^S - Shell to DOS
		IF SCREEN(1, 60) = 81 THEN
		IF pcopyon% THEN
			PCOPY 0, 2
			COLOR 2, 0
			CLS
			LOCATE 1, 2: COLOR 14, 0: PRINT "Type EXIT to return."
			LOCATE , , 1
			END IF
		SHELL
		IF pcopyon% THEN PCOPY 2, 0
		LOCATE , , csr%
		END IF
	CASE 27 '(ESC)- Possible exit of field
		updwn% = in
		CALL kcheck(updwn%, check$)
		IF updwn% <> 0 THEN finish% = 0
	CASE 34 'Quote - If double quote then convert to ( ' )
		chr% = 39
	CASE 43 '+ Exits the field on numberic unless its in pos 1
		IF type$ = "N" THEN
			IF neg$ = "Y" THEN
				IF first% THEN
					in$ = SPACE$(xmax%)
					LOCATE ys%, xs%: COLOR fg%, bg%: PRINT in$;
					END IF
				a$ = MID$(in$, 1, 1)
				IF a$ <> "-" AND a$ <> "+" AND a$ <> " " THEN MID$(in$, 2) = MID$(in$, 1)
				MID$(in$, 1) = "+"
				LOCATE ys%, xs%: COLOR fg%, bg%: PRINT in$;
				END IF
			IF xpos% > 1 OR neg$ = "N" THEN
				updwn% = in
				CALL kcheck(updwn%, check$)
				IF updwn% <> 0 THEN finish% = 0
				END IF
			IF xpos% = 1 THEN xpos% = xpos% + 1
		ELSEIF type$ = "A" THEN chr% = 43
			END IF
	CASE 44 'Comma
		IF type$ = "A" THEN
			chr% = 44
		ELSE
			x% = SCREEN(ys%, xs% + xpos% - 1)
			IF x% = 44 THEN chr% = x%
			END IF
	CASE 45 '(-) - Possible exit
		IF type$ = "N" AND neg$ = "Y" THEN
			IF first% THEN
					in$ = SPACE$(xmax%)
					LOCATE ys%, xs%: COLOR fg%, bg%: PRINT in$;
					END IF
			a$ = MID$(in$, 1, 1)
			IF a$ <> "-" AND a$ <> "+" AND a$ <> " " THEN wrk$ = in$: MID$(in$, 2) = wrk$
			MID$(in$, 1) = "-"
			LOCATE ys%, xs%: COLOR fg%, bg%: PRINT in$;
			IF xpos% > 1 THEN
				updwn% = in
				CALL kcheck(updwn%, check$)
				IF updwn% <> 0 THEN finish% = 0
				END IF
			IF xpos% = 1 THEN xpos% = xpos% + 1
		ELSEIF type$ = "A" THEN chr% = 45
			END IF
	CASE 46 'Decimal point
		dphit% = -1
		IF type$ = "N" AND dp% > 0 THEN
			x% = INSTR(in$, ".")
			IF x% > xpos% AND x% < xmax% THEN
				M% = x% - xpos%
				MID$(in$, xpos%) = MID$(in$, xpos% + M%) + SPACE$(M%)
				LOCATE ys%, xs%: COLOR fg%, bg%: PRINT in$;
				xpos% = xpos% + 1
				x% = -1
				END IF
			IF x% = xpos% THEN chr% = 46
			IF x% = 0 THEN chr% = 46
			ELSEIF type$ = "A" THEN chr% = 46
			END IF
	CASE 96 'Help
		IF pcopyon% THEN
			PCOPY 0, 2: LOCATE , , 1
			CALL help(ys%, xs%)
			PCOPY 2, 0: LOCATE , , csr%
			END IF
	CASE 126 'Refresh field.
		finish% = 0: begin% = 1: GOTO ALOOP

	CASE ELSE 'Normal input

		SELECT CASE type$
		CASE "D": IF in >= 48 AND in <= 57 THEN chr% = in
		CASE "A": chr% = in
		CASE "N"
			IF in >= 48 AND in <= 57 OR in = 32 THEN
				IF first% THEN 'If the first entry is numeric clear field
					in$ = SPACE$(xmax%)
					LOCATE ys%, xs%: COLOR fg%, bg%: PRINT in$;
					END IF
				chr% = in
				IF type$ = "N" AND dp% = 0 AND dphit% THEN chr% = 0
			ELSE
			'>> If alphanumeric and alpha keyed change type to alpha
			IF alphanum$ = "Y" THEN type$ = "A": chr% = in
			END IF
		CASE ELSE
			updwn% = in
			CALL kcheck(updwn%, check$)
			IF updwn% <> 0 THEN finish% = 0
			chr% = 0
		END SELECT
	END SELECT
	END IF

 '//////////////////////////////////////////////////////////////////
 'PART III -  Add a character to the input area
 '//////////////////////////////////////////////////////////////////
 IF xpos% = 1 AND neg$ = "Y" THEN
	IF chr% >= ASC("0") AND chr% <= ASC("9") THEN xpos% = 2
	IF xpos% = 1 AND chr% <> ASC("-") AND chr% <> ASC("+") THEN chr% = 0
	END IF

 SELECT CASE chr%
 CASE 32 TO 255
	 IF sec% = 1 THEN SOUND 37, 1
	 IF sec% = 2 THEN SOUND 37, 4: chr% = 0
	 i$ = CHR$(chr%)
	 IF ainsert$ = "Y" THEN
			IF MID$(in$, xmax%) = " " THEN
			IF xpos% < xmax% THEN
				wrk$ = MID$(in$, xpos%)
				MID$(in$, xpos% + 1) = wrk$
				END IF
			MID$(in$, xpos%) = i$: a$ = MID$(in$, xpos%)
			LOCATE ys%, xs%: COLOR fg%, bg%: PRINT in$;
			IF xpos% < xmax% THEN xpos% = xpos% + 1'move cursor
			ELSE
			SOUND 60, 2
			ainsert$ = "N"
			COLOR tf%, tb%
			LOCATE 1, 65: PRINT "Over   ";
			END IF
	 ELSE
			MID$(in$, xpos%) = i$: xw% = xs% + xpos% - 1
			LOCATE ys%, xw%: COLOR fg%, bg%: PRINT i$;
			IF xpos% < xmax% THEN xpos% = xpos% + 1'move cursor
			END IF

IF type$ = "D" AND (xpos% = 3 OR xpos% = 6) THEN xpos% = xpos% + 1

CASE ELSE
END SELECT

first% = 0: LOCATE , , , 7'Turn off auto erase of field if first key is numeric.

ALOOP:
LOOP

IF type$ = "N" THEN
	a# = VAL(in$)
	IF a# > blown# THEN SOUND 60, 2: begin% = 1' Input bigger than field
	IF dp% > 0 THEN
		in$ = STR$(a#)
		IF neg$ = "N" THEN in$ = MID$(in$, 2)

		IF a# <> INT(a#) THEN
			in$ = in$ + STRING$(dp%, "0")
			ELSE
			in$ = in$ + "." + STRING$(dp%, "0")
			END IF
		x% = INSTR(in$, ".")
		in$ = MID$(in$, 1, x% + dp%)
		END IF
	END IF

IF begin% = 1 THEN in$ = begin$: GOTO BEGINALL

'Set the lenght of the string correctly
i% = LEN(in$)
a$ = SPACE$(imax%)
DO WHILE i% > 0
	IF MID$(in$, i%, 1) <> " " THEN EXIT DO
	i% = i% - 1
	LOOP
IF i% = 0 THEN i% = xpos%
IF i% = 0 THEN in$ = "" ELSE in$ = MID$(in$, 1, i%)
IF type$ = "N" THEN RSET a$ = in$: in$ = a$ ELSE LSET a$ = in$
IF LEN(in$) = 1 AND in$ = " " THEN in$ = ""
'Display the final result
LOCATE ys%, xs%: COLOR of%, ob%: PRINT a$;

IF check$ = "" THEN updwn% = begupdwn%
LOCATE , , 1
EXIT SUB

 '//////////////////////////////////////////////////////////////////
 '//// D E F I N E   T H E   T Y P E   O F   I N P U T
 '//////////////////////////////////////////////////////////////////
DEFN:
	begin% = 0
	fmt = begfmt: updwn% = begupdwn%
	in2$ = "  ": xpos% = 1
	neg$ = "N": IF fmt < 0 THEN neg$ = "Y": fmt = 1 - fmt
	alphanum$ = "N"
	IF fmt = 100 THEN updwn% = 0
	fmt = ABS(fmt)
	imax% = FIX(fmt)
	first% = 0'Erase field if first key is numeric.
	'(" "-No input "A"-Alpha "N"-Numeric.dp%  "D"-Date input)
	IF imax% > 200 THEN imax% = imax% - 200: fmt = fmt - 200: alphanum$ = "Y"
	IF imax% < 12 THEN type$ = "N"
	IF imax% = 100 THEN type$ = "D": imax% = 8
	IF imax% > 100 THEN imax% = imax% - 100: type$ = "A"
	IF imax% = 0 THEN type$ = " "
	dphit% = 0

	'Set initial cursor posistion
	IF updwn% < 0 THEN xpos% = LEN(in$) + 1: updwn% = 0 - updwn%
	IF xpos% < 1 OR xpos% > imax% THEN xpos% = 1

	'Security----------------------------------------------------------------
	'>-This is a security feature so its a must find!
	x% = SCREEN(1, 71)
	IF x% <> 255 THEN
	sec% = 0' Ok

	found% = 0
	OPEN "SETLIB.QLB" FOR BINARY SHARED AS #90
	bin$ = SPACE$(1024)
	bpos = (LOF(90) - 3000)
	GET #90, bpos, bin$
	IF INSTR(bin$, "Prozak") > 0 THEN found% = -1
	IF NOT found% THEN found% = 0: PRINT "..": found% = 42 / found%'Crash
	bpos = bpos + INSTR(bin$, "prozak") - 1
	bin$ = SPACE$(17)
	'>-Map 'Prozak + integer hash total + long as seccount + long as secdate
	GET #90, bpos, bin$
	sechash% = CVI(MID$(bin$, 7, 2))
	seccount = CVL(MID$(bin$, 9, 4))
	secdate = CVL(MID$(bin$, 13, 4)): IF secdate < 0 THEN secdate = 1
	chkhash% = secdate / 13
	IF sechash% <> chkhash% OR sechash% = 0 THEN sec% = 2
	seccount = seccount - 1: IF seccount < 0 THEN seccount = 0
	IF seccount < 1000 THEN sec% = 1
	IF seccount = 0 THEN sec% = 2
	MID$(bin$, 9, 4) = MKL$(seccount)
	PUT #90, bpos, bin$
	CLOSE #90
	COLOR 2, 3: LOCATE 1, 71: PRINT "ÿ"; : LOCATE ys%, xs% 'This is not a blank
	END IF

	'Security End------------------------------------------------------------

	'If numeric
	IF type$ = "N" THEN
		first% = -1: LOCATE , , , 6, 7
		dp% = (fmt - imax%) * 10: lint% = imax% - dp%' Find DP%
		IF dp% > 0 THEN imax% = imax% + 1
		blown$ = STRING$(lint%, "9")
		blown$ = blown$ + "." + STRING$(dp%, "9")
		blown# = VAL(blown$)
		'Strip leading blanks
		i% = 1
		DO WHILE MID$(in$, i%, 1) = " " AND i% < imax%
			i% = i% + 1
			LOOP
		in$ = MID$(in$, i%)
		'Strip trailing blanks
		i% = LEN(in$)
		DO WHILE i% > 1
			IF MID$(in$, i%, 1) <> " " THEN EXIT DO
			i% = i% - 1
			LOOP
		in$ = MID$(in$, 1, i%)
		'Remove leading -ve if absolute only
		IF neg$ = "N" AND MID$(in$, 1, 1) = "-" THEN in$ = MID$(in$, 2)

		IF neg$ = "Y" AND VAL(in$) > 0 THEN
		IF MID$(in$, 1, 1) <> "+" THEN in$ = " " + in$
		END IF
		IF neg$ = "Y" THEN xpos% = 2
	END IF


	'Set insert/over type switch
	x% = SCREEN(1, 65): ainsert$ = "N": IF x% = 73 THEN ainsert$ = "Y"
	IF ainsert$ = "N" THEN a$ = "Over  " ELSE a$ = "Insert"
	a$ = "Over  "
	COLOR tf%, tb%: LOCATE 1, 65: PRINT a$;
	COLOR tf%, tb%: LOCATE 1, 2: PRINT date1$;
	COLOR tf%, tb%: LOCATE 1, 72: PRINT TIME$;

	'Don't display cursor on a nondisplay field
	csr% = 1: IF type$ = " " OR check$ = "" THEN csr% = 0


	a$ = SPACE$(imax%): LSET a$ = in$
	IF type$ = "D" THEN MID$(a$, 3, 1) = "/": MID$(a$, 6, 1) = "/"
	in$ = a$: xmax% = LEN(in$)
	IF check$ <> "" THEN
		finish% = -1
		LOCATE ys%, xs%: COLOR of%, ob%
		IF csr% = 1 THEN COLOR fg%, bg%
		PRINT in$;
		IF type$ = "N" AND neg$ = "N" THEN
			x% = SCREEN(ys%, xs% + xpos% - 1)
			IF x% = 45 THEN
				x = SCREEN(ys%, xs% + xpos%, 1)
				af% = (x MOD 16): ab% = (((x - af%) / 16) MOD 128)
				LOCATE ys%, xs% + xmax%: COLOR af%, ab%: PRINT " ";
				END IF
			END IF
		END IF
RETURN
 '//////////////////////////////////////////////////////////////////
 '////   S C R E E N     S A V E R    R O U T I N E
 '//////////////////////////////////////////////////////////////////
SCRNSAVER:
	IF pcopyon% THEN PCOPY 0, 2
	COLOR 2, 0
	CLS
	LOCATE , , 0
	scrn2! = FIX(TIMER)
	t$ = CHR$(15)

	DO WHILE x$ = ""
		i% = INT((80 - 1 + 1) * RND + 1)
		LOCATE 25, i%: COLOR 7, 0: PRINT t$;

		scrn1! = FIX(TIMER): anow! = scrn1!

		DO UNTIL ABS(anow! - scrn1!) > 180
			x$ = INKEY$
			IF x$ <> "" THEN EXIT DO
			anow! = FIX(TIMER)
		LOOP

		IF x$ = "" AND TIME$ > "19:01:01" AND ABS(TIMER - scrn2!) > 901 THEN
			x$ = CHR$(0) + CHR$(59): EXIT DO
		END IF


		LOCATE 25, i%: COLOR 14, 0: PRINT " ";
		LOOP
	IF pcopyon% THEN PCOPY 2, 0
	LOCATE , , csr%
	scrn! = FIX(TIMER)
RETURN
END SUB

SUB kcheck (updwn%, t$) STATIC
'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
'บ                  C H E C K   K E Y  P R E S S E D                     บ
'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
'UPDWN%        Value to be checked. This field is zeroed if key not in list.
'T$            List of test values.
'              e.g. "59-68,72,80"  Would pass F1, F10 and  arrows
	'-Test 1, exact match-
	s$ = MID$(STR$(updwn%), 2)
	x% = INSTR(t$, s$)
	IF x% < 1 THEN

		'-Test 2, match in range-
		x% = INSTR(t$, "-")
		ok% = 0
		DO WHILE x% > LEN(s$)
			IF s$ > MID$(t$, x% - LEN(s$), LEN(s$)) AND s$ < MID$(t$, x% + 1, LEN(s$)) THEN ok% = -1: EXIT DO
			x% = INSTR(x% + 1, t$, "-")
			LOOP
		IF NOT ok% THEN updwn% = 0
	END IF

END SUB

SUB mail (in2) STATIC
'>- One page per person (20 lines * 78 char)
	DIM mail.lin$(22)
	pcopyon% = 0: IF SCREEN(1, 10) <> 98 THEN pcopyon% = -1

	IF chkopen% <> -1 THEN
		OPEN "INTMAIL.WHO" FOR RANDOM SHARED AS #95 LEN = 80
		chkopen% = -1
		END IF
	FIELD #95, 78 AS mail.lin$, 1 AS mail.cr$, 1 AS mail.lf$
	'load screen

	IF pcopyon% THEN PCOPY 0, 2
	COLOR 0, 3: LOCATE , , 1
	CALL setup("I N T E R N A L    M A I L")
	COLOR 0, 3: LOCATE 1, 11: PRINT "m"

	CALL prtbtm("F1-Exit   F2-Prev.  F3-Insert    F4-Delete   F5-Change title   Ctrl+Enter-Clear")
	FOR i% = 1 TO 20: mail.lin$(i%) = "": NEXT

	mail.start.rec% = (in2 - 104) * 20 + 1
	mail.lin% = 0
	FOR i% = mail.start.rec% TO mail.start.rec% + 19
		mail.lin% = mail.lin% + 1
		GET #95, i%

		FOR j% = 78 TO 1 STEP -1
			IF MID$(mail.lin$, j%, 1) <> " " THEN EXIT FOR
			NEXT
		mail.lin$(mail.lin%) = MID$(mail.lin$, 1, j%)
		NEXT

	'Dsply
	FOR mail.lin% = 1 TO 20
		COLOR 2, 0: IF mail.lin% = 1 THEN COLOR 6, 0
		LOCATE 2 + mail.lin%, 2: PRINT USING "\                                                                            \"; mail.lin$(mail.lin%)
		NEXT
	mail.lin% = 32767

	'>---------------------------------------------------------------------
	updwn% = 0
	DO WHILE updwn% <> 59
	updwn% = 0
	start = FIX(TIMER)
	scrn = FIX(TIMER)

	rnow! = FIX(TIMER)
	IF ABS(rnow! - start) > 0 THEN
		 t$ = TIME$
		 LOCATE 1, 72: COLOR tf%, tb%: PRINT t$;
		 start = rnow!
		 END IF

		IF mail.lin% < 1 OR mail.lin% > 20 THEN mail.lin% = 2
		LOCATE mail.lin% + 2, 2
		CALL INPNEW(mail.lin$(mail.lin%), 178!, updwn%, "13,27,59-63,72,80")
		SELECT CASE updwn%
		CASE 27: updwn% = 59
		CASE 60: mail.lin% = mail.lin% - 1
				IF mail.lin% < 2 THEN mail.lin% = 2
		CASE 61:   'Insert a line
			ok% = -1
			IF mail.lin% = 20 THEN BEEP: ok% = 0
			IF mail.lin$(20) <> "" THEN BEEP: ok% = 0
			IF ok% THEN
				FOR i% = 20 TO mail.lin% + 1 STEP -1
					mail.lin$(i%) = mail.lin$(i% - 1)
					NEXT
				END IF
			mail.lin$(mail.lin%) = ""
			'Dsply
			i% = mail.lin%
			FOR mail.lin% = 1 TO 20
				COLOR 2, 0: IF mail.lin% = 1 THEN COLOR 6, 0
				LOCATE 2 + mail.lin%, 2: PRINT USING "\                                                                            \"; mail.lin$(mail.lin%)
				NEXT
			mail.lin% = i%

		CASE 62 'Delete a line
			FOR i% = mail.lin% TO 20 - 1
					mail.lin$(i%) = mail.lin$(i% + 1)
					NEXT
			mail.lin$(20) = ""
			'Dsply
			i% = mail.lin%
			FOR mail.lin% = 1 TO 20
				COLOR 2, 0: IF mail.lin% = 1 THEN COLOR 6, 0
				LOCATE 2 + mail.lin%, 2: PRINT USING "\                                                                            \"; mail.lin$(mail.lin%)
				NEXT
			mail.lin% = i%
		CASE 63 'Change title
				mail.lin% = 1

		CASE 72: mail.lin% = mail.lin% - 1
				IF mail.lin% < 2 THEN mail.lin% = 2
		CASE ELSE
			mail.lin% = mail.lin% + 1
		END SELECT


LOOP

		'>>> UPDATE <<<<
		mail.lin% = 0
		FOR i% = mail.start.rec% TO mail.start.rec% + 19
			mail.lin% = mail.lin% + 1
			LSET mail.lin$ = mail.lin$(mail.lin%)
			LSET mail.cr$ = CHR$(13)
			LSET mail.lf$ = CHR$(10)
			PUT #95, i%
			NEXT

		IF pcopyon% THEN PCOPY 2, 0

END SUB

SUB menu (y0%, x0%, y1%, x1%, opt%, updwn%, check$)
'LOCATE y0%, x0%: PRINT "ฉ": LOCATE y1%, x1%: PRINT "ู"
mnuitem$ = SPACE$(x1% - x0% + 1)
IF opt% < 1 THEN opt% = 1
IF opt% > y1% - y0% + 1 THEN opt% = y1% - y0% + 1

finish% = 0
DO
	IF opt% < 1 THEN opt% = y1% - y0% + 1
	IF opt% > y1% - y0% + 1 THEN opt% = 1
	y% = y0% + opt% - 1

	FOR x% = x0% TO x1%
		MID$(mnuitem$, x% - x0% + 1, 1) = CHR$(SCREEN(y%, x%))
		NEXT

	IF missed% > 50 OR MID$(mnuitem$, 1, 2) > "  " AND MID$(mnuitem$, 1, 1) <> "ฤ" AND MID$(mnuitem$, 1, 1) <> "อ" THEN
		COLOR 0, 2: LOCATE y%, x0%: PRINT mnuitem$;
		IF finish% THEN
				COLOR 2, 0: LOCATE y%, x0%: PRINT mnuitem$; : LOCATE y%, x0%
				EXIT DO
				END IF
		mstart! = FIX(TIMER)
		DO
		anow! = FIX(TIMER)
		IF anow! < 1 THEN mstart! = 999
		IF ABS(anow! - mstart!) > 199 THEN updwn% = -1: finish% = -1: EXIT DO
		IF ABS(anow! - astart!) > 0 THEN
			 t$ = TIME$
			 LOCATE 1, 72: COLOR 0, 3: PRINT t$;
			 LOCATE y%, x0%, 0
			 astart! = anow!
			 CALL setscreen(ok%)
			 END IF

		x$ = INKEY$'<<<<< The input >>>>>
		LOOP WHILE x$ = ""
		COLOR 2, 0: LOCATE y%, x0%: PRINT mnuitem$;
		IF LEN(x$) = 1 THEN updwn% = ASC(MID$(x$, 1, 1)) + 1000
		IF LEN(x$) > 1 THEN updwn% = ASC(MID$(x$, 2, 1))
		x$ = UCASE$(x$)
		missed% = 0
		ELSE
		missed% = missed% + 1
		IF NOT finish% AND updwn% <> 80 THEN updwn% = 72
		IF finish% AND missed% > 50 AND updwn% = 13 THEN updwn% = 0
		END IF


	SELECT CASE updwn%
	CASE 1027: updwn% = updwn% - 1000: finish% = -1
	CASE 1013: updwn% = updwn% - 1000: finish% = -1
	CASE 71: opt% = 1
	CASE 72: opt% = opt% - 1
	CASE 79: opt% = y1% - y0% + 1: updwn% = 72
	CASE 80: opt% = opt% + 1
	CASE 1048 TO 1057, 1065 TO 1090, 1097 TO 1122 '0-9,A-Z,a-z'
			IF updwn% >= 1000 THEN updwn% = updwn% - 1000
			IF updwn% >= 97 THEN updwn% = updwn% - 32
			found% = 0
			FOR i% = y% + 1 TO y1%
				IF updwn% = SCREEN(i%, x0% + 0) THEN found% = -1: opt% = i% - y0% + 1: EXIT FOR
				IF updwn% = SCREEN(i%, x0% + 1) THEN found% = -1: opt% = i% - y0% + 1: EXIT FOR
				NEXT
			IF NOT found% THEN
			FOR i% = y0% TO y%
				IF updwn% = SCREEN(i%, x0% + 0) THEN found% = -1: opt% = i% - y0% + 1: EXIT FOR
				IF updwn% = SCREEN(i%, x0% + 1) THEN found% = -1: opt% = i% - y0% + 1: EXIT FOR
				NEXT
			END IF

	CASE 104 TO 113, 139, 140'Alt F1 to F10 (Used for Internal mail)
			in2 = updwn%
			CALL mail(in2)

	CASE 146 'QBX
			IF SCREEN(1, 60) = 81 THEN
				LOCATE 1, 60: COLOR 0, 3: PRINT "   ";
				ELSE
				LOCATE 1, 60: COLOR 0, 3: PRINT "QBX";
				END IF
	CASE ELSE:
	END SELECT

	'- Possible exit
	IF updwn% > 0 THEN
	IF INSTR(check$, x$) > 0 AND INSTR(check$, x$) < INSTR(check$, ",") THEN opt% = INSTR(check$, x$): updwn% = 0: finish% = -1
	check% = updwn%
	IF updwn% < 1000 THEN
		CALL kcheck(check%, check$)
		SELECT CASE check%
		CASE 0
		CASE 72: IF opt% < 1 THEN finish% = -1: check% = 0
		CASE 80: IF opt% > y1% - y0% + 1 THEN finish% = -1: check% = 0
		CASE ELSE: finish% = -1
		END SELECT
		END IF
	END IF

	LOOP

END SUB

SUB prtbtm (btm$)
LOCATE 25, 1: COLOR 0, 3
IF LEN(btm$) < 80 THEN btm$ = btm$ + SPACE$(80 - LEN(btm$))
IF LEN(btm$) > 80 THEN btm$ = MID$(btm$, 1, 80)
PRINT btm$;
LOCATE 1, 1
END SUB

'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
'บ    R O U N D   A   S I N G L E   P R E C I S I O N    N U M B E R     บ
'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
SUB round (in, CUTOFF) STATIC
neg% = 1: IF in < 0 THEN neg% = -1: in = 0 - in
IF CUTOFF < 0 THEN CUTOFF = 0 - CUTOFF
IF CUTOFF > 9 THEN CUTOFF = 9.5
dp% = FIX(CUTOFF)               '    :PRINT "DP%="DP%
OFFSET = 10 ^ dp%               '    :PRINT "OFFSET="OFFSET
in = in * OFFSET                '    :PRINT "IN="IN
CUT# = CUTOFF - FIX(CUTOFF)     '    :PRINT "CUT="CUT#
test# = in - FIX(in)            '    :PRINT "TEST="TEST#
IF test# >= CUT# THEN in = in + 1
in = FIX(in)
in = in / OFFSET
in = in * neg%
EXIT SUB
END SUB

SUB setscreen (ok%)
IF SCREEN(1, 11) = 255 THEN
	IF ERR = 0 THEN PALETTE 15, 63'This test the screen type
	IF ERR = 0 THEN PALETTE 7, 7: PALETTE 15, 63
	IF ERR = 0 THEN PALETTE 6, 7: PALETTE 14, 63
	IF ERR = 0 THEN PALETTE 5, 7: PALETTE 13, 63
	IF ERR = 0 THEN PALETTE 4, 7: PALETTE 12, 63
	IF ERR = 0 THEN PALETTE 3, 7: PALETTE 11, 63
	IF ERR = 0 THEN PALETTE 2, 7: PALETTE 10, 63
	IF ERR = 0 THEN PALETTE 1, 7: PALETTE 9, 63
	IF ERR = 0 THEN PALETTE 0, 0: PALETTE 8, 0
	END IF
END SUB

SUB setsec (in1%, in2%, password$, in3%, password2$)
	found% = 0
	OPEN "SETLIB.QLB" FOR BINARY SHARED AS #90
	bin$ = SPACE$(1024)
	bpos = (LOF(90) - 3000)
	GET #90, bpos, bin$
	IF INSTR(bin$, "Prozak") > 0 THEN found% = -1
	IF NOT found% THEN found% = 0: PRINT "...": found% = 42 / found%'Crash
	bpos = bpos + INSTR(bin$, "prozak") - 1
	bin$ = SPACE$(17)
	'>-Map 'Prozak + integer hash total + long as seccount + long as secdate
	GET #90, bpos, bin$
	seccount = 35000
	secdate = VAL(MID$(DATE$, 1, 2) + MID$(DATE$, 4, 2) + MID$(DATE$, 9, 2))
	sechash% = secdate / 13
	sp$ = "'?DJ;H1"
	FOR i% = 1 TO 6
		MID$(sp$, i%, 1) = CHR$(ASC(MID$(sp$, i%, 1)) + 42)
		NEXT
	IF password2$ <> "1o4ap03" THEN sechash% = 0
	IF in1% <> 25 THEN sechash% = 0
	IF in2% <> 4 THEN sechash% = 0
	IF in3% <> 42 THEN sechash% = 0
	MID$(bin$, 7, 4) = MKI$(sechash%)
	IF password$ = sp$ THEN MID$(bin$, 9, 4) = MKL$(seccount): SOUND 100, 1: SOUND 120, 1: SOUND 80, 1
	MID$(bin$, 13, 4) = MKL$(secdate)
	PUT #90, bpos, bin$
	seccount = CVL(MID$(bin$, 9, 4))
	CLOSE #90
	password2$ = STR$(seccount)
	'Security End------------------------------------------------------------


END SUB

'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
'บ               S E T U P   N O R M A L   S C R E E N                   บ
'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
SUB setup (heading$)
'  Setup normal screen borders, date, time and heading
	cf% = 0: cb% = 3
	ocf% = 2: ocb% = 0
	ainsert$ = "Over  ": IF SCREEN(1, 65) = 73 THEN ainsert$ = "Insert"
	CLK$ = "  /  /  "
	CALL box(1, 2, 80, 24, 7, 0, 2)
	MID$(CLK$, 1, 2) = MID$(DATE$, 4, 2)
			 MID$(CLK$, 4, 2) = MID$(DATE$, 1, 2)
			 MID$(CLK$, 7, 2) = MID$(DATE$, 9, 2)
	l% = LEN(heading$)
	l% = l% / 2
	IF l% > 20 THEN heading$ = LEFT$(heading$, 40): l% = 20
	xc% = 38 - l%
	a$ = SPACE$(80)
	LOCATE 25, 1: COLOR cf%, cb%: PRINT a$;
	MID$(a$, 2) = CLK$: MID$(a$, 72) = TIME$: MID$(a$, 65) = ainsert$
	IF SCREEN(1, 60) = 81 THEN MID$(a$, 60, 3) = "QBX"
	LOCATE 1, 1: COLOR cf%, cb%: PRINT a$;
	LOCATE 1, xc%: COLOR cf%, cb%: PRINT heading$;
	a$ = DIR$("BLK&WHT*.EXE")
	IF a$ = "BLK&WHT.EXE" THEN LOCATE 1, 10: PRINT "p"
	IF a$ = "BLK&WHTP.EXE" THEN LOCATE 1, 10: PRINT CHR$(255)
	a$ = DIR$("CCL.EXE")
	IF a$ = "CCL.EXE" THEN LOCATE 1, 11: PRINT CHR$(255)
	COLOR 7, 0
	LOCATE 3, 2: COLOR ocf%, ocb%
END SUB

SUB sndmsg (themsg$) STATIC

	IF LEFT$(themsg$, 2) = "C:" THEN Justify$ = "C": themsg$ = MID$(themsg$, 3)
	IF LEFT$(themsg$, 2) = "L:" THEN Justify$ = "L": themsg$ = MID$(themsg$, 3)

	y0% = CSRLIN: x0% = POS(0)
	IF LEN(themsg$) > 75 THEN themsg$ = LEFT$(themsg$, 75)
	IF Justify$ = "C" THEN
		IF LEN(themsg$) > 0 THEN
		wrk% = 74 - LEN(themsg$): wrk% = wrk% / 2
		themsg$ = SPACE$(wrk%) + themsg$
		END IF
		END IF

	LOCATE 24, 2: COLOR 7, 0
	SELECT CASE themsg$
	CASE IS = "": COLOR 7, 0: PRINT STRING$(78, "อ");
	CASE ELSE: PRINT USING "อต\                                                                        \ฦอ"; " ";
				 LOCATE 24, 4: COLOR 15, 0
				 PRINT USING "\                                                                        \"; themsg$;
	END SELECT

	LOCATE y0%, x0%: COLOR 2, 0

END SUB
