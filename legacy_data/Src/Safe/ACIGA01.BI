REM  SUB iga
'.dc - Complete
	CONST lnadd% = 4
	CONST maxlines% = 19
	'
	keyl% = 20: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)
	DIM c%(8), in$(maxlines%, 11), rrn%(maxlines%)
	DIM mm(80), mc$(80)
	c%(1) = 2: c%(2) = 6: c%(3) = 10: c%(4) = 13
	c%(5) = 18: c%(6) = 57: c%(7) = 64: c%(8) = 72
	'
	GET #36, 1, msmisc
	'
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxacc% = CVI(msmisc.max5$): maxcus% = CVI(msmisc.max7$)
	maxord% = 999':MAXACC%=9999
	'
	GOSUB init.iga
	'
	'///////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>> M A I N L I N E <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
	'///////////////////////////////////////////////////////////////////////
	'
start.iga:
	FOR l% = 1 TO maxlines%
		in$(l%, 1) = "0": in$(l%, 2) = "   ": in$(l%, 3) = "": in$(l%, 4) = "": in$(l%, 5) = "": in$(l%, 6) = "0"
		in$(l%, 7) = "0": in$(l%, 8) = "0": in$(l%, 9) = "N/": in$(l%, 10) = "0": in$(l%, 11) = "0"
		GET #4, l%
		wrkqty% = CVI(wrk1.wrkqty$)
		wrkrrn% = CVI(wrk1.wrkrrn$)
		in$(l%, 1) = STR$(wrkqty%)
		in$(l%, 4) = STR$(wrkrrn%)
	 NEXT
	 '
detail:
	CALL setup("STOCK ENTRY")
	btm$ = " F1-Return.  "
	COLOR 8, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
	'
	LOCATE 3, 2: COLOR 6, 0: PRINT "Qty. Size   No.  Description                           Price     Tax    Value"
	LOCATE , 2: COLOR 2, 0: PRINT "ÄÄÄÂÄÄÄÄÄÄÂÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄ"
	FOR l% = 1 TO maxlines%
		GOSUB dsplyline
	NEXT
	'
	'///////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>> Get line entries for the invoice <<<<<<<<<<<<<<<<<
	'///////////////////////////////////////////////////////////////////////
	l% = 1
	DO WHILE updwn% <> 59
		ln% = l% + lnadd%
		GOSUB chglin
		IF updwn% = 62 THEN EXIT DO   'F4 - Delete
		IF updwn% = 60 THEN           'F2 - Back one line
			IF l% > 1 THEN l% = l% - 1
			l% = l% - 1
		END IF
		IF updwn% = 72 THEN           'Back up one line
			IF l% > 1 THEN l% = l% - 1
			l% = l% - 1
		END IF
		'
		l% = l% + 1
		IF l% > maxlines% THEN l% = 1
	LOOP
	'///////////////////////////////////////////////////////////////////////
	'>>>>>>
	'///////////////////////////////////////////////////////////////////////
	'
exitmenu:
	'>> Save what has been keyed to a work file <<
	FOR l% = 1 TO maxlines%
		GET #4, l%
		wrkrrn% = VAL(in$(l%, 4))
		wrkqty% = VAL(in$(l%, 1))
		LSET wrkrrn$ = MKI$(wrkrrn%)
		LSET wrkqty$ = MKI$(wrkqty%)
		PUT #4, l%
	NEXT
	'
	opt$ = "1"
	'
	DO
	CALL BOX(17, 5, 63, 19, 6, 9, 1)
	COLOR 4, 1
	LOCATE 6, 28: PRINT "  E X I T    M E N U "
	COLOR 7, 1
	LOCATE , 28: PRINT "1....Update Stock Entry"
	LOCATE , 28: PRINT "2....Exit and hold keying"
	LOCATE , 28: PRINT "3....Continue Stock Entry"
	LOCATE , 28: PRINT
	LOCATE , 28: PRINT "Option...> ";
	CALL inpnew(opt$, 1!, updwn%, "13,59")
	IF updwn% = 59 THEN GOTO X.IGA
	COLOR 2, 0
	opt% = VAL(opt$)
	LOOP UNTIL opt% >= 0 AND opt% <= 4
	'
	IF opt% = 1 THEN GOSUB upd.stock: GOSUB clr.wrk.file: GOTO X.IGA
	IF opt% = 2 THEN GOTO X.IGA
	IF opt% = 3 THEN GOTO detail
	GOTO start.iga

	'///////////////////////////////////////////////////////////////////////
	'>>>> update the stock file
	'///////////////////////////////////////////////////////////////////////
upd.stock:
'    CALL box(17, 5, 63, 19, 6, 9, 1)
'    LOCATE 9, 18
	'
	'>>> Update the files <<<
	'
	COLOR 2, 0
	FOR l% = 1 TO maxlines%
		wrkqty% = VAL(in$(l%, 1))
		wrkrrn% = VAL(in$(l%, 4))
		IF wrkrrn% > 0 AND wrkrrn% <= maxacc% THEN
			GET #3, wrkrrn%, acstk
			acstk.soh = acstk.soh + wrkqty%
			PUT #3, wrkrrn%, acstk: SOUND 20000, 1
		END IF
	NEXT
	'
x.upd.stock:
	'
	RETURN
	'///////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>> Change an invoice entry line
	'///////////////////////////////////////////////////////////////////////
chglin:
	ctl% = 1: chg = 0: maxctl% = 7
	WHILE NOT ctl%
		'Edit
		IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
		ON ctl% GOSUB cfiga1, cfiga2, cfiga3, cfiga4, cfiga5, cfiga6, cfiga7
		' Pgm ctl processing
		ctl% = ctl% + 1
		'Mimick F1 if enter is pressed on a blank line
		IF updwn% = 13 AND VAL(in$(l%, 1)) = 0 AND VAL(in$(l%, 4)) = 0 THEN updwn% = 59
		'
		IF updwn% = 60 THEN ctl% = ctl% - 2     'F2 - Back one field
		IF updwn% = 72 THEN ctl% = -1           'Up Arrow
		IF updwn% = 80 THEN ctl% = -1           'Down Arrow
		IF updwn% = 60 AND ctl% = 0 THEN ctl% = -1'F2 at first field
		IF updwn% = 59 THEN ctl% = -1           'F1 Save
		IF ctl% > maxctl% THEN ctl% = -1        'End of line
	WEND
	RETURN
	'
	RETURN
	'///////////////////////////////////////////////////////////////////////
	'>>>> Lookup index file. Passed skey$. Returns SKEY, 0 if not found. <<<<<
	'>>>> SKEY1, one after insertion place                               <<<<<
	'///////////////////////////////////////////////////////////////////////
searchindex.iga:
	skey = 0: skey1 = 0: found% = 0
	IF skey$ = "     " THEN skey1 = 0: RETURN
	s% = 0: e% = maxcus%
searchagain.iga:
	p% = (e% - s%) / 2 + s%
	GET #45, p%, supx
	IF CVI(supx.wrrn$) = 0 THEN LSET supx.wcde$ = STRING$(99, CHR$(255))
	IF supx.wcde$ + wtyp$ = skey$ THEN skey = p%: skey1 = p%: found% = -1: RETURN
	IF e% - s% = 1 THEN skey = 0: skey1 = s%: RETURN
	IF supx.wcde$ + wtyp$ < skey$ THEN s% = p%: GOTO searchagain.iga
	IF supx.wcde$ + wtyp$ > skey$ THEN e% = p%: GOTO searchagain.iga
	RETURN
	'///////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>> Detail entry subroutines
	'///////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>> QTY
cfiga1:
	LOCATE ln%, c%(1)
	in$ = in$(l%, 1)
	CALL inpnew(in$, 203!, updwn%, "13,27,59,60,62,64,72,80")
		in$ = UCASE$(in$)
	IF updwn% = 27 THEN
		in$(l%, 1) = "0": in$(l%, 2) = "   ": in$(l%, 3) = "": in$(l%, 4) = "": in$(l%, 5) = "": in$(l%, 6) = "0"
		in$(l%, 7) = "0": in$(l%, 8) = "0": in$(l%, 9) = "N/": in$(l%, 10) = "0": in$(l%, 11) = "0"
		GOSUB dsplyline
		GOTO cfiga1
		END IF
	IF updwn% = 64 THEN
		PCOPY 0, 1
		CALL accbrowse(rec%)
		PCOPY 1, 0
		GOTO cfiga1
		END IF

	'
	'>>>>>>>>>>>>>>>>>>>> Drop back into Next/Previos search mode
	IF in$ = "N" OR in$ = "P" THEN
		ctl% = 4: updwn% = 0: search.dir$ = in$: newsearch$ = "S"
		'>>>>>>>>>>>>>>> Back up one line
		IF l% > 1 THEN l% = l% - 1
		ln% = l% + lnadd%
	ELSE
		in$(l%, 1) = in$
		GOSUB cfiga8
		newsearch$ = "Y"
	END IF
	RETURN
	'>>>>>>>>>>>>>>>>>>>> SIZE
cfiga2: LOCATE ln%, c%(2)
	IF VAL(in$(l%, 4)) = 0 THEN check$ = "13,59,60,62" ELSE check$ = ""
        CALL inpnew(in$(l%, 2), 103!, updwn%, check$)
	a$ = "   ": LSET a$ = in$(l%, 2): in$(l%, 2) = a$
	'
	'///////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>> Set up search or non search mode
	bysearch$ = "N"
	IF in$(l%, 2) <> "   " AND VAL(in$(l%, 4)) = 0 THEN bysearch$ = "Y"
	'///////////////////////////////////////////////////////////////////////
	RETURN
	'>>>>>>>>>>>>>>>>>>>> UNITS
cfiga3: LOCATE ln%, c%(3)
	CALL inpnew(in$(l%, 3), 102!, updwn%, "")
	'
	RETURN
	'>>>>>>>>>>>>>>>>>>> STOCK NUMBER
cfiga4:
	LOCATE ln%, c%(4)
	IF updwn% = 13 THEN oldrec% = VAL(in$(l%, 4))
	IF bysearch$ = "Y" OR VAL(in$(l%, 4)) <> 0 AND updwn% = 13 THEN
		inpctl$ = ""
		ELSE
		inpctl$ = "13,59,60,62,64"
	END IF
	'
	CALL inpnew(in$(l%, 4), 4!, updwn%, inpctl$)

	IF updwn% = 64 THEN
		PCOPY 0, 1
		CALL accbrowse(rec%)
		PCOPY 1, 0
		in$(l%, 4) = STR$(rec%)
		GOTO cfiga4
		END IF

	'
	ditem% = VAL(in$(l%, 4))
	IF ditem% < 1 OR ditem% > maxacc% THEN ditem% = 0
	IF ditem% <> oldrec% AND ditem% <> 0 THEN
		 ordqty% = VAL(in$(l%, 1))
		 prevordqty% = 0
		 invqty% = 0
		 IF acstk.date$ = nul8$ OR acstk.date$ = sp8$ THEN GOTO cfiga4 '.cv
		 GOSUB dsplyline
	END IF
	'
	RETURN
	'
	'>>>>>>>>>>>>>>>>>>> DESCRIPTION
cfiga5: LOCATE ln%, c%(5)
	IF bysearch$ = "N" THEN
		CALL inpnew(in$(l%, 5), 125!, updwn%, "")
	ELSE '>>>>>>>>>>>>>> Search away
		IF newsearch$ = "Y" THEN
			in$ = ""
			CALL inpnew(in$, 118!, updwn%, "13,59,60,62")
			IF LEN(in$) > 0 THEN
										in$ = UCASE$(in$)
					search.key$ = in$
					COLOR 13, 0
					LOCATE 3, 35: PRINT USING "\                \"; search.key$
					COLOR 2, 0
			END IF
			IF updwn% = 59 THEN GOTO xcfiga5
			IF updwn% = 60 THEN GOTO xcfiga5
			search.dir$ = "N"
			LSET qk$ = search.key$
			CALL index("CHAIN", ind%, qk$, 7, keyl%)
			'
			IF ind% < 0 AND qk$ < search.key$ THEN CALL index("READ ", ind%, qk$, 7, keyl%)
			IF ind% < 0 THEN ind% = 0 - ind%
	END IF
	'
		test = VAL(in$(l%, 2))
		test1$ = MID$(qk$, 1, 1)
		'
anext3:
		c$ = MID$(qk$, 16, 3)'Size
		IF VAL(c$) = test THEN
			test1$ = MID$(qk$, 1, 1)
			IF ind% > 0 AND ind% < maxacc% THEN GET #3, ind%, acstk
			'
			in$(l%, 4) = STR$(ind%)
			in$(l%, 5) = acstk.desc1$ + " " + acstk.desc2$
			GOSUB cfiga6
			GOSUB cfiga8
			GOSUB dsplyline
			LOCATE ln%, c%(5)
			IF newsearch$ = "Y" THEN search.dir$ = CHR$(13)
			'>>>>>>>>>> If its the last line leave it in Next/Previous mode on same line //
			IF newsearch$ = "Y" AND l% = maxlines% THEN search.dir$ = ""
			IF newsearch$ = "N" THEN search.dir$ = INPUT$(1)
			newsearch$ = "N"
						search.dir$ = UCASE$(search.dir$)
			'?? CALL INPNEW(  0.0,UPDWN%,"13,p,n")
		END IF
		'
		'>>>>>>>>>>>>>>> If the first letter in the index changes cancel then search
		IF test1$ <> MID$(qk$, 1, 1) THEN 'Size not found. Return to size field.
				updwn% = 60
				GOTO xcfiga5
		END IF
		'
		IF search.dir$ = "N" THEN
				CALL index("READ ", ind%, qk$, 7, keyl%)
				GOTO anext3
		END IF
		'
		IF search.dir$ = "P" THEN
				CALL index("READP", ind%, qk$, 7, keyl%)
				GOTO anext3
		END IF
		'
		IF search.dir$ <> CHR$(13) THEN GOTO cfiga5'AGAIN
		'>>>>>>>>>>>>>>> Load details of new record into array
			ditem% = ind%
			ordqty% = VAL(in$(l%, 1))
			invqty% = 0
			GOSUB dsplyline
		END IF
xcfiga5:
	RETURN
	'
	'>>>>>>>>>>>>>>>>>>>> PRICE
cfiga6: LOCATE ln%, c%(6)
        'CALL inpnew(in$(l%, 6), 5.2!, updwn%, "")
	'in$(l%, 6) = STR$(acstk.wholesalecost)
	'
	RETURN
	'>>>>>>>>>>>>>>>>>>>> TAX - Calulated in the extention routine
cfiga7:
	RETURN
	'
	'>>>>>>>>>>>>>>>>>>>> EXTENSION
cfiga8:
	ext = price * qty%
	in$(l%, 8) = STR$(ext)
	CALL ROUND(ext, 2.5)
	IF ext = 0 THEN in$(l%, 8) = " "
	'
	RETURN
	'
	'///////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>>  D I S P L A Y   S I N G L E   D A T A   L I N E
	'///////////////////////////////////////////////////////////////////////
dsplyline:
		ln% = l% + lnadd%
		COLOR 2, 0
		ano% = VAL(in$(l%, 4))
		'
	IF ano% < 1 OR ano% > maxacc% THEN
			LOCATE ln%, 2
			COLOR 2, 0
			PRINT "   ³      ³    ³                                     ³       ³       ³       "
	ELSE
			GET #3, ano%, acstk
			qty% = VAL(in$(l%, 1))
			in$(l%, 2) = acstk.size$
			in$(l%, 3) = acstk.unit$
			in$(l%, 5) = acstk.desc1$ + " " + acstk.desc2$
			price = acstk.wholesalecost
			priceshown = acstk.wholesalecost

			GOSUB cfiga8'Calculate ONLY
			a$ = "³" + acstk.size$ + " " + acstk.unit$ + "³"
			b$ = "³" + acstk.desc1$ + " " + acstk.desc2$ + " ³"
			'
			LOCATE ln%, 2: PRINT USING "###"; qty%
			LOCATE ln%, 5: PRINT a$;
			LOCATE ln%, 13: PRINT USING "####"; ano%
			LOCATE ln%, 17: PRINT b$;
			LOCATE ln%, 56: PRINT USING "####.##³####.##³#####.##"; priceshown; tax; ext
	END IF
	'
	RETURN
	'
	'///////////////////////////////////////////////////////////////////////
	'>>>>>>
	'///////////////////////////////////////////////////////////////////////
clr.wrk.file:
	'>> Save what has been keyed to a work file <<
	FOR l% = 1 TO maxlines%
		GET #4, l%
		LSET wrkrrn$ = MKI$(0)
		LSET wrkqty$ = MKI$(0)
		PUT #4, l%
	NEXT
	'
	RETURN
	'
	'///////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>> Setup things
	'///////////////////////////////////////////////////////////////////////
init.iga:
	'>>>>>>>>>>>>>>>>>>>> Array the margin file
	GET #1, 1, acmgn: mm(1) = CVS(acmgn.margin$): mc$(1) = acmgn.mcode$
	FOR i% = 2 TO 80: GET #1, , acmgn: mm(i%) = CVS(acmgn.margin$): mc$(i%) = acmgn.mcode$: NEXT
	RETURN
	'
'<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< END >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
X.IGA:

REM END SUB

