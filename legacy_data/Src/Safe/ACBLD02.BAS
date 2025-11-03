DECLARE SUB searchindex (keyin$, chi%, found%)
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
	'>>>>>>>>>>>>>>>>> ACBLD02 - Accessory index build <<<<<<<<<<<<<<<<<<<<<
	'///////////////////////////////////////////////////////////////////////
'.dc - Complete
	'ACBLD02.BAS
'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
	apgm$ = "ACBLD03"
	'
	'/////////////////////////////////////////////////////////
	'///  KEY LIST                                         ///
	'///      KFLD    sup.SEARCH$     4                        ///
	'///      KFLD    sup.STYPE$      1                        ///
	'///      KFLD    ANO%        2  (Low byte,High byte)  ///
	'/////////////////////////////////////////////////////////
	'
	keyl% = 7: qk$ = SPACE$(keyl%)
	'
	'//////////////////////////
	'0 - Build index
	'1 - List index only
	'2 - Both
	'//////////////////////////
	'
	lonly = 0
	cursup$ = "     ": savsup$ = "@@@@@": skey$ = "     "
	CLOSE
	IF lonly < 0 OR lonly > 2 THEN STOP
	'
	IF lonly = 0 OR lonly = 2 THEN
		OPEN "acstkx2.new" FOR RANDOM AS #2 LEN = 1
		CLOSE : KILL "acstkx2.new"
	END IF
	'
	acstkf$ = "acf"
	IF INSTR(COMMAND$, "FROMFILE=ACSTK.NEW") > 0 THEN acstkf$ = "NEW": SOUND 100, 1
	DB.OR.CR$ = "CR"
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\ACSTK.INC'
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	'
	GET #36, 1, msmisc
	'
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxhst% = CVI(msmisc.max4$): maxacc% = CVI(msmisc.max5$)
	CALL setup(" ACCESSORY FILES INDEX BUILD ")
	IF acstkf$ = "NEW" THEN
		LOCATE 5, 30: PRINT "Reading ACSTK.NEW"
		ELSE
		LOCATE 5, 30: PRINT "Reading ACSTK.ACF"
		END IF
	'
	'<<<<<<<<<<<<<<  O P E N  I N D E X
	'
	CALL index("OPEN ", ind%, "acstkx2.new", 2, keyl%)
	FIELD #2, 2 AS X.QR$, 2 AS X.QD$, 2 AS X.QM$
	sfx$ = "  ": osuplr$ = "~~": n% = 0
	IF lonly = 1 THEN GOTO do.list
	'
	'<<<<<<<<<<<<<<  L O A D   I N D E X
	'
	nitems% = 1
	GET #3, nitems%, acstk
	WHILE NOT EOF(3) AND nitems% <= maxacc%
	'
	ano% = acstk.no%
	IF acstk.date$ <> nul8$ AND acstk.date$ <> sp8$ AND ano% = nitems% THEN '.dc
		'
		IF acstk.suplr$ <> osuplr$ THEN
			CALL searchindex(acstk.suplr$, 45, found%)
			asuplr% = CVI(supx.wrrn$)
			IF NOT found% THEN asuplr% = -1
			IF asuplr% < 1 OR asuplr% > maxsup% THEN
				LSET osuplr$ = "~~"
				ELSE
				GET #44, asuplr%, sup':SOUND 50,1
				LSET osuplr$ = acstk.suplr$
			 END IF
		END IF
		'
		ano$ = MKI$(acstk.no%)
		MID$(sfx$, 1, 1) = MID$(ano$, 2, 1): MID$(sfx$, 2, 1) = MID$(ano$, 1, 1)
		qk$ = sup.search$ + sup.stype$ + sfx$
		CALL index("WRITE", ind%, qk$, 2, keyl%)
		n% = n% + 1: ano% = acstk.no%
		IF n% MOD 100 = 0 THEN
			LOCATE 10, 24: PRINT USING "|\    \ ! ####| Total:####"; sup.search$; sup.stype$; ano%; n%
			END IF
			GET #2, 1
			LOCATE 11, 24: PRINT USING "Record ####  Depth #### Nodes ####"; CVI(X.QR$); CVI(X.QD$); CVI(X.QM$)
	END IF
	'
	GET #3, , acstk
	nitems% = nitems% + 1
	WEND
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
	'<<<<<<<<<<<<<<  L I S T   I N D E X
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
do.list:
	IF lonly = 0 THEN GOTO endpgm
	i% = 0: ind% = 0: st$ = SPACE$(45): a$ = "  ": l% = 2
	CALL setup("LIST OF RECORDS IN INDEX")
	CALL index("FIRST", ind%, qk$, 2, keyl%)
	WHILE ind% > 0 AND X$ <> CHR$(27)
		i% = i% + 1
		rec% = ind%
		GET #3, rec%, acstk
		LSET st$ = STR$(i%) + "|" + LEFT$(qk$, 5) + "|" + STR$(rec%) + "|" + STR$(acstk.no%) + "|" + acstk.desc1$ + "|"
		l% = l% + 1: IF l% > 21 THEN l% = 3: X$ = INPUT$(1)
		LOCATE l%, 2: COLOR 3, 0
		PRINT st$;
		CALL index("READ ", ind%, qk$, 2, keyl%)
	WEND
	'> Blank line to finish
	l% = l% + 1
	IF l% <= 21 THEN
		LOCATE l%, 2
		LSET st$ = SPACE$(99)
		COLOR 3, 0
		PRINT st$;
		END IF
	'
	CLOSE
	'
endpgm:
	'
	CLOSE
	shella$ = "copy acstkx2.acf acstkx2.old"
	shellb$ = "copy acstkx2.new acstkx2.acf"
	SHELL shella$
	SHELL shellb$

	CLOSE
	CALL exitpgm(apgm$): CHAIN apgm$
	END
	'
'<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< END >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB
