 DECLARE SUB searchindex (keyin$, chi%, found%)
'.dc - Complete
	'///////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>> ACIDX03L - Accessory invoic. index list. <<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
	'ACIDX03L.BAS
	'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
	pgm$ = "ACFMENU"
	'/////////////////////////////////////////////////////
	'///  KEY LIST
	'///      KFLD    ACSTK.ASEARCH$   10
	'///      KFLD    sup.SEARCH$     4
	'///      KFLD    sup.STYPE$      1
	'///      KFLD    ACSTK.ASIZE$      3
	'///      KFLD    ANO%        2  (Low byte,High byte)
	'//////////////////////////////////////////////////////
	'
	keyl% = 20: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)
	COLOR 2
	'////////////////////////
	'0 - Build index
	'1 - List index only
	'2 - Both
	'////////////////////////
	lonly = 1
	cursup$ = "    ": savsup$ = "@@@@": skey$ = "    "
	sp10$ = SPACE$(10)
	nul10$ = STRING$(10, 0)
	KEY 1, "end" + CHR$(13)
	CLOSE
	IF lonly < 0 OR lonly > 2 THEN STOP

	IF lonly = 1 OR lonly = 2 THEN
		'STDOUT$ = "CON"
		OPEN STDOUT$ FOR OUTPUT AS #99
		END IF
	'

	IF lonly = 0 OR lonly = 2 THEN
		OPEN "acstkx3.acf" FOR RANDOM AS #2 LEN = 12
		CLOSE : KILL "acstkx3.acf"
	END IF
	'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\ACSTK.INC'     '#03 LEN=128
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'    '#36 LEM=128
	'$INCLUDE: '\tpmanuf\src\whof.INC'       '#43 LEN=300
	'$INCLUDE: '\tpmanuf\src\sup.INC'       '#43 LEN=300
	'$INCLUDE: '\tpmanuf\src\supX.INC'      '#45 LEN=7
	'
	GET #36, 1, msmisc
	'
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxhst% = CVI(msmisc.max4$): maxacc% = CVI(msmisc.max5$)
	CLS : COLOR 2
	LOCATE 1, 1: PRINT "Date:"; DATE1$
	LOCATE 1, 68: PRINT "Time:"; TIME$
	COLOR 4
	LOCATE 1, 23: PRINT " ACCESSORY FILES INDEX BUILD "
	LOCATE 2, 23: PRINT "============================="
	COLOR 7
	LOCATE 22, 30: PRINT "F1 - exit."
	COLOR 2: X = 28
350  T$ = "Y"
	'LOCATE 8,X:PRINT "continue (y/n)..>";T$;CHR$(FNE)
	'LOCATE 8,X+17:INPUT "",T$
	IF LEN(T$) = 0 THEN T$ = "Y"
	IF T$ = "end" THEN GOTO endpgm
	IF T$ = "y" THEN T$ = "Y"
	IF T$ = "n" THEN T$ = "N"
	IF T$ <> "Y" AND T$ <> "N" THEN COLOR 14: LOCATE 24, 1: PRINT "Enter 'Y' to continue, or 'N' to exit.": COLOR 2: GOTO 350
	LOCATE 24, 1: PRINT CHR$(FNE)
	IF T$ = "N" THEN GOTO endpgm
	'
	'<<<<<<<<<<<<<<  O P E N  I N D E X
	'
	CALL index("OPEN ", ind%, "acstkx3.acf", 2, keyl%)
	sfx$ = "  ": osuplr$ = "~~": N% = 0
	IF lonly = 1 THEN GOTO dolist
	'
	'<<<<<<<<<<<<<<  L O A D   I N D E X
	nitems% = 1
	test$ = " "
	GET #3, nitems%, acstk
	WHILE NOT EOF(3) AND nitems% < maxacc%
		'
		ano% = acstk.no%
		LSET test$ = acstk.search$: IF test$ = CHR$(0) THEN test$ = " "
		IF test$ <> " " AND ano% = nitems% THEN
			'
			IF acstk.suplr$ <> osuplr$ THEN
				CALL searchindex(acstk.suplr$, 45, found%)
				asuplr% = CVI(supx.wrrn$)
				IF NOT found% THEN asuplr% = -1
				 IF asuplr% < 1 OR asuplr% > maxsup% THEN
					 LSET osuplr$ = "~~"
					 ELSE
					 GET #43, asuplr%: SOUND 50, 1
					 LSET osuplr$ = acstk.suplr$
				END IF
			END IF
			'
			ano$ = MKI$(acstk.no%)
			MID$(sfx$, 1, 1) = MID$(ano$, 2, 1): MID$(sfx$, 2, 1) = MID$(ano$, 1, 1)
			aa$ = acstk.search$ + sup.search$ + sup.stype$ + acstk.size$ + sfx$
			FOR I% = 1 TO LEN(aa$)
				IF MID$(aa$, I%, 1) = CHR$(0) THEN MID$(aa$, I%, 1) = " "'WHY??
			NEXT
			'
			LSET qk$ = aa$
			LSET rep$ = qk$
			CALL index("WRITE", ind%, qk$, 2, keyl%)
			N% = N% + 1: ano% = acstk.no%
			LOCATE 10, 20: PRINT USING "|&|####| Total:####"; rep$; ano%; N%
		END IF
		GET #3, , acstk
		nitems% = nitems% + 1
	WEND
	'<<<<<<<<<<<<<<  L I S T   I N D E X
dolist:
	IF lonly = 0 THEN GOTO endpgm
	I% = 0: ind% = 0: A$ = "  ": L% = 2
	st$ = SPACE$(25): hldst$ = SPACE$(25)
	CLS
	COLOR 4: PRINT "LIST OF RECORDS IN INDEX": COLOR 2
	pag% = 0: lin% = 9999
	'
	CALL index("FIRST", ind%, qk$, 2, keyl%)
	WHILE ind% > 0
		I% = I% + 1
		rec% = ind%
		GET #3, rec%, acstk
		LSET st$ = LEFT$(qk$, 18) + STR$(rec%)

		IF qk$ < hldst$ THEN BEEP: PRINT "Index corrupt!!": X$ = INPUT$(1)
		LSET hldst$ = qk$
		L% = L% + 1: IF L% > 22 THEN L% = 3':X$=INPUT$(1)
		lin% = lin% + 1
		IF lin% > 50 THEN GOSUB heading
		LOCATE L%, 1
		PRINT #99, st$
		CALL index("READ ", ind%, qk$, 2, keyl%)

	WEND
	'
	CLOSE
	'
endpgm:
	'
	CALL exitpgm(pgm$)
	CHAIN pgm$

END

'////////////////////////////////////////////////////////////////////////////
'>>>>
'////////////////////////////////////////////////////////////////////////////
heading:
	pag% = pag% + 1: IF pag% > 1 THEN PRINT #99, CHR$(12)

	PRINT #99, : PRINT #99, ; CHR$(14); msmisc.CC$
	PRINT #99, "#ACIDX03L"; TAB(60); DATE1$; " "; TIME$
	PRINT #99, "S T O C K   F I L E   I N D E X";
	PRINT #99, TAB(69); "page: "; pag%
	PRINT #99, STRING$(79, "=")
	lin% = 1


RETURN

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB
