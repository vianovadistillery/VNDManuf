'/////////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>         A C M G N 0 1       <<<<<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'.dc - Complete
'>>>>>>>>>> CHANGES     - Accessory margin maintenance
'>>>>>>>>>> 25/3/92 : Help line standard
'>>>>>>>>>> LJC     : Used inpnew & updwn% for help line
'>>>>>>>>>>         :
	'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "ACMENU"
	''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	'$INCLUDE: '\tpmanuf\src\ACMGN.INC'
	LOCATE , , 1
	DIM mc$(80), m(80)
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxacc% = CVI(msmisc.max4$)
	CALL setup("UPDATE ACCESSORY MARGINS")
	COLOR 0, 3: LOCATE 25, 4:
	PRINT "F1-Exit      F7-Change trade discount code (marked by '*')    F10-Change";
	COLOR 2, 0
	'>>>>> Read file into processing array
	GET #1, 1, acmgn: mc$(1) = acmgn.mcode$: m(1) = CVS(acmgn.margin$)
	FOR i% = 2 TO 80: GET #1, , acmgn: mc$(i%) = acmgn.mcode$: m(i%) = CVS(acmgn.margin$): NEXT
	'>>>>> List the lot from the array
	FOR i% = 1 TO 20
	LOCATE i% + 2, 4
	j% = i% + 20: k% = i% + 40: l% = i% + 60
	PRINT USING "  ! ###.##            ! ###.##            ! ###.##            ! ###.##   "; mc$(i%); m(i%); mc$(j%); m(j%); mc$(k%); m(k%); mc$(l%); m(l%)
	IF i% = 1 THEN LOCATE 3, 5: PRINT " No margin": LOCATE 4, 1
	IF i% = 20 THEN
		LOCATE 19, 65: PRINT " {  Future?"
		LOCATE 20, 65: PRINT " |  Set price"
		LOCATE 21, 65: PRINT " }  Deposit"
		LOCATE 22, 65: PRINT " .  No recalc"
		END IF
	NEXT
	'>>>>> Place "*" beside trade discount
	rec = ASC(msmisc.trdisc$) - 46: IF rec < 2 OR rec > 81 THEN LOCATE 24, 1: COLOR 14: PRINT "Trade discount code is not valid."; : COLOR 2: GOTO 440
	xtr% = (INT(rec / 20) * 20)
	ytr% = rec MOD 20
	IF ytr% = 0 THEN ytr% = 20: xtr% = xtr% - 20
	LOCATE ytr% + 2, xtr% + 4
	COLOR 14: PRINT "*": COLOR 2
440 : fgnd = 7: bgnd = 0: ofgnd = 2: obgnd = 8: oprt = 14:
	CALL sndmsg("")
	ys = 23: xs = 46: xmax = 1: flin = 1: aatype = 0: disold = 0:
	COLOR 0, 0: LOCATE 24, 46: CALL inpnew(in$, 0!, updwn%, "13,59,65,68")
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	IF updwn% = 65 THEN GOSUB 840:
	IF updwn% = 68 THEN GOSUB chgmgn
	GOTO 440
chgmgn:     '>>>>> Change a margin
	COLOR 2, 0:
	CALL sndmsg(SPACE$(77))
	LOCATE 24, 5: PRINT "Enter margin code...>";
	fgnd = 7: bgnd = 1: ofgnd = 2: obgnd = 8: oprt = 14
	 LOCATE 24, 26: CALL inpnew(in$, 101!, updwn%, "13,59")
	 IF updwn% = 59 THEN GOTO 440
	 a$ = in$
	'* Check for number being entered fisrt
	IF LEN(a$) <> 2 THEN 590
	b$ = "  ": LSET b$ = a$: b% = VAL(b$)
	IF b% = 1 THEN a$ = "/"
	IF b% > 1 AND b% < 81 THEN rec = b%: GOTO 650
590 '* Now check for the code being entered
	m$ = " ": LSET m$ = a$
	IF m$ = "/" THEN LOCATE 24, 1: COLOR 14: PRINT "    "; "/"; "; is a special margin code which must always be zero."; CHR$(FNE); : COLOR 2: GOTO 440
	IF ASC(m$) < 48 OR ASC(m$) > 125 THEN LOCATE 1, 1: GOTO chgmgn
	rec = ASC(m$) - 46
	CALL sndmsg("")
	'* Make the change
650 GET #1, rec, acmgn
670 CALL sndmsg(SPACE$(77))
	LOCATE 24, 35: PRINT "Enter new margin..>";
	fgnd = 7: bgnd = 1: ofgnd = 2: obgnd = 8: oprt = 14: in$ = "      "
	LOCATE 24, 54: CALL inpnew(in$, 106!, updwn%, "13,59,60")
	IF updwn% = 59 THEN GOTO 440
	IF updwn% = 60 THEN GOTO chgmgn
	a$ = in$
	b$ = "      ": LSET b$ = a$: margin = VAL(b$)
	IF margin < 0 THEN LOCATE 24, 60: COLOR 14: PRINT "Too small!"; : COLOR 2: GOTO 670
	IF margin > 999 THEN LOCATE 24, 60: COLOR 14: PRINT "Too large!"; : COLOR 2: GOTO 670
	LSET acmgn.margin$ = MKS$(margin)
	PUT #1, rec, acmgn
	m(rec) = margin
	'* Find X,Y co-ordinates to change screen
	CALL sndmsg("")
	x% = INT(rec / 20) * 20
	y% = rec MOD 20
	IF y% = 0 THEN y% = 20: x% = x% - 20
	LOCATE y% + 2, x% + 8
	PRINT USING "###.##"; m(rec)
	RETURN
840 '>>>>> CHANGE TRADE DISCOUNT FLAG
	LOCATE 24, 20: PRINT "Enter new discount code..>";
	 
	fgnd = 7: bgnd = 1: ofgnd = 2: obgnd = 8: oprt = 14
	LOCATE 24, 46: CALL inpnew(in$, 101!, updwn%, "13,59,65,68")
	IF updwn% = 59 THEN GOTO 440
	a$ = in$
	IF flin = 0 THEN RETURN
	IF a$ = " " THEN RETURN
	rec = ASC(a$) - 46: IF rec < 2 OR rec > 81 THEN LOCATE 24, 1: COLOR 14: PRINT "Code not valid."; : COLOR 2: GOTO 840
	LOCATE 24, 1: PRINT CHR$(FNE)
	LOCATE ytr% + 2, xtr% + 4: PRINT " "'* Erase old code
	xtr% = (INT(rec / 20) * 20)
	ytr% = rec MOD 20
	IF ytr% = 0 THEN ytr% = 20: xtr% = xtr% - 20
	LOCATE ytr% + 2, xtr% + 4
	PRINT "*"
	GET #36, 1, msmisc
	LSET msmisc.trdisc$ = a$
	PUT #36, 1, msmisc
	RETURN

