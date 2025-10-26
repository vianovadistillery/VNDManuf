DECLARE SUB browse38i (browse38.result%)
DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB calcusecost ()
DECLARE SUB setchannel ()
DECLARE SUB Change.tanks (rec&, updwn%)
DECLARE SUB psi.write.form ()
DECLARE SUB browse29 (browse29.result%, updwn%)
DECLARE SUB printit ()
DECLARE SUB height.in.tank (updwn%, seq%, Ltrs.in!, Height.from.btm!, Height.from.top!)
DECLARE SUB load.index (loadonly%)
DECLARE SUB insert.recipe (idx53%, updwn%, seed$)
DECLARE SUB resins (startsearch%, seq%, updwn%)
DECLARE SUB solvents (startsearch%)
DECLARE SUB browse30 (browse30.result%, updwn%)
DECLARE SUB browse38 (browse38.result%, updwn%)
DECLARE SUB Browse54 (browse54result%, updwn%)
DECLARE SUB calc.hdr ()
DECLARE SUB change (rec&, updwn%)
DECLARE SUB cpy.all.old (updwn%)
DECLARE SUB cvt.tnt (tnt$, tnt%, tntf$)
DECLARE SUB del.all (idx53%, updwn%)
DECLARE SUB details (rec&, updwn%, auto%)
DECLARE SUB dsply (rec&, getrec$)
DECLARE SUB dsply.line (rec&, lin%, first.seq%, calc%)
DECLARE SUB exchange.rmat (updwn%)
DECLARE FUNCTION format$ (VALUE!, definition$)
DECLARE SUB hazard (code$)
DECLARE SUB history (rec&, updwn%)
DECLARE SUB load.lines (rec&)
DECLARE SUB qsort (in$(), in%(), n%, ok%)
DECLARE SUB save.lines (rec&, auto%)
'////////////////////////////////////////////////////////////////////////
'////    T I N T    R E C I P E   R E C A L C U L A T I O N
'////////////////////////////////////////////////////////////////////////
'.dc - Complete
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "MSMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CONST maxformseq% = 38
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.inc'
	'$INCLUDE: '\tpmanuf\src\supx.inc'
	'$INCLUDE: '\tpmanuf\src\cusx.inc'
	'$INCLUDE: '\tpmanuf\src\cus.inc'
	'$INCLUDE: '\tpmanuf\src\tnthedx.inc'
	'$INCLUDE: '\tpmanuf\src\tnthed.inc'
	'$INCLUDE: '\tpmanuf\src\tntdet.inc'
	'$INCLUDE: '\tpmanuf\src\forhedx.inc'
	'$INCLUDE: '\tpmanuf\src\forhed.inc'
	'$INCLUDE: '\tpmanuf\src\fordet.inc'
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	'$INCLUDE: '\tpmanuf\src\msrmat.inc'
	'$INCLUDE: '\tpmanuf\src\mscomt.inc'
	'$INCLUDE: '\tpmanuf\src\msbatch.inc'
	'$INCLUDE: '\tpmanuf\src\fmhist.inc'
	CLOSE #34
	'$INCLUDE: '\tpmanuf\src\tnhist.inc'
	CLOSE #72
	'$INCLUDE: '\tpmanuf\src\msclass.INC'

	DIM SHARED ch.hedx%, ch.hed%, ch.det%
	DIM SHARED rmno%(maxformseq%), qty!(maxformseq%), cmtno%(maxformseq%), cmtqty!(maxformseq%)
	DIM SHARED desc$(maxformseq%), vpct!(maxformseq%), wpct!(maxformseq%), ltr!(maxformseq%), kg!(maxformseq%), ext!(maxformseq%)
	DIM SHARED Vsol!(maxformseq%), Wsol!(maxformseq%)
	DIM SHARED cost.or.ltrs$
	DIM SHARED tot.ext!, tot.ltr!, tot.kg!, tot.Vsol!, tot.Wsol!
	DIM SHARED tot.vsolpct!, tot.wsolpct!, tot.pvcpct!, tot.pbrpct!
	DIM SHARED maxrmat%, maxcmt%, maxtnt%
	DIM SHARED mode$, msg$, Modedesc$
	DIM SHARED perc!(6), c1%(6)
	DIM SHARED resin.id%(6), resin.Lt!(6), resin.SolidKG!(6)
	DIM SHARED YC040!(6), Cobalt!(6), lead!(6), Calcium!(6), Manganese!(6), Meko!(6), POLY!(6)'*****
	DIM SHARED rrn%(20)
	DIM SHARED auditfile$(15), naudit%


	'>>- Hold of rmat file fields
	DIM SHARED rm.sg!(maxformseq%), rm.wtsolid!(maxformseq%), rm.solidsg!(maxformseq%)
	DIM SHARED rm.useunit$(maxformseq%), rm.cond$(maxformseq%), rm.tanksize!(maxformseq%)
	GET #36, 1, msmisc
	maxtnt% = 999
	maxcmt% = 99
	maxrmat% = 9999
	cca$ = msmisc.cc$
	parm3$ = ENVIRON$("PARM3$"): IF MID$(parm3$, 1, 1) <> "." THEN cca$ = parm3$
	mode$ = ENVIRON$("TINTS.OR.A-F$")  'A - F,Tints, JOT....
	parm$ = ENVIRON$("PARM$")
	IF parm$ <> "AUTOC." THEN parm$ = "......"

	CALL setchannel
	CALL load.index(0)

	IF parm$ = "AUTOC." THEN
		ENVIRON "PARM$=......"

		FOR pass% = 1 TO 2
			FOR idx53% = 1 TO 999
				rec& = tnthedx.rrn%(idx53%)
				IF rec& > 0 THEN
					CALL dsply(rec&, "Y")
					auto% = -1
					cost.or.ltrs$ = "Litres"
					CALL load.lines(rec&)
					CALL details(rec&, updwn%, auto%)
					CALL save.lines(rec&, auto%)
					X$ = INKEY$
					IF X$ = CHR$(27) THEN EXIT FOR
				END IF
			NEXT
			BEEP
		NEXT
		CLOSE
		CALL EXITPGM(apgm$): CHAIN apgm$
		END IF


	idx53% = 0
	clr% = -1
start:
	IF idx53% < 1 THEN idx53% = 0: rec& = 0
	IF idx53% > maxtnt% THEN idx53% = maxtnt%
	IF idx53% > 0 THEN rec& = tnthedx.rrn%(idx53%)
	IF dontclr% THEN
		dontclr% = 0
		ELSE
		CALL setup(cca$)
		END IF
	btm$ = "F1-Exit F2-Hist F3/F4-Ins/Del F5=BSize F6-Browse F8-Exchange F9-Details F10-Chg."
	CALL prtbtm(btm$): COLOR 2, 0

GET.TINT:

	CALL dsply(rec&, "Y")
	CALL sndmsg(msg$): msg$ = "":
	'IF rec& < 1 OR rec& > maxtnt% THEN  ELSE COLOR 7, 0: LOCATE 24, 56: PRINT "Ê";
	COLOR 2, 0
																		 
	IF mode$ = "Tints" THEN
		COLOR 10, 0: LOCATE 3, 12: PRINT "Tinter................>"; : COLOR 2, 0: PRINT " "
	ELSE
		COLOR 2, 0: LOCATE 3, 12: PRINT "Formula number........>"; : COLOR 2, 0: PRINT " "
	END IF
	LOCATE 3, 35
	IF NOT skiptnt% THEN
		tnt$ = ""
			CALL inpnew(tnt$, 104!, updwn%, "13,59" + ALT$): GOSUB ALT
			IF rec& = 0 THEN
			IF updwn% <> 13 AND updwn% <> 59 AND updwn% <> 61 AND updwn% <> 64 THEN GOTO GET.TINT
		END IF
	END IF
	skiptnt% = 0

FOR idx53% = 1 TO maxtnt% '??

	CALL cvt.tnt(tnt$, tnt%, tntf$)
	
			auto% = 0
			cost.or.ltrs$ = "Litres"
			CALL load.lines(rec&)
			CALL details(rec&, updwn%, auto%)
			CALL save.lines(rec&, auto%)
			GOTO start
	CASE 68: CALL change(rec&, updwn%)
	CASE 13:
			found% = 0
			FOR i% = 1 TO maxtnt%
				IF tnt$ = tnthedx.tnta$(i%) THEN idx53% = i%: found% = -1: EXIT FOR
				IF tnthedx.tnta$(i%) > tnt$ THEN EXIT FOR
			NEXT

			tntfound% = 0
			IF found% THEN
				rec& = tnthedx.rrn%(idx53%)
				tntfound% = -1
			END IF

			IF MID$(tnt$, 1, 3) = "000" THEN
				idx53% = idx53% + 1
				rec& = tnthedx.rrn%(idx53%)
				tntfound% = -1
			END IF

	 IF tntfound% = 0 THEN
			msg$ = "This recipe is not on file. (" + tnt$ + ").  Use F3 to insert."
			tntforinsert$ = tnt$
			idx53% = i%
			rec& = tnthedx.rrn%(idx53%)
			rec& = 0
	 END IF

	END SELECT

	GOTO GET.TINT

SUB browse29 (browse29.result%, updwn%) STATIC
PCOPY 0, 1
4380    '>>>>> U P D A T E   A   C L A S S
	 h$ = "F O R M U L A   U P D A T E"
	 CALL setup(h$)
	 COLOR 4: LOCATE 3, 29: PRINT "UPDATE A CLASS"
	 COLOR 8, 3:
	 LOCATE 25, 16: PRINT "F7 - Roll Foward.  F8 - Roll Backward.";
	 COLOR 2, 0: k% = 1: GOTO 4540
4440 LOCATE 4, 23: PRINT CHR$(FNE); "Enter class number..>"
	 LOCATE 4, 45
	 CALL inpnew(a$, 2!, updwn%, "13,59,81,73")
	 IF updwn% = 59 THEN pass = 1: GOTO x.browse29
	 IF updwn% = 81 THEN k% = 50
	 IF updwn% = 73 THEN k% = 1
	 b$ = "  ": LSET b$ = a$: b% = VAL(b$)
	 IF b% < 1 OR b% > 99 THEN 4540
	 LOCATE 4, 23: PRINT USING "Enter class ## desciption.>"; b%
	 LOCATE 4, 50
	 CALL inpnew(a$, 120!, updwn%, "13,59,81,73")
	 IF updwn% = 59 THEN 4440
	 LSET msclass.cldesc$ = a$
	 PUT #29, b%, msclass
4540 LOCATE 5, 1
	FOR i% = k% TO k% + 16
	j% = i% + 17: kk% = j% + 17
	 a$ = SPACE$(25): b$ = a$: c$ = a$
	 GET #29, i%, msclass: LSET a$ = msclass.cldesc$
	 GET #29, j%, msclass: LSET b$ = msclass.cldesc$
	 IF i% = k% THEN browse30.result% = i%
	 IF kk% < 100 THEN GET #29, kk%, msclass: LSET c$ = msclass.cldesc$
	 LOCATE , 2: PRINT USING "### \                    \ "; i%; a$;
	 LOCATE , 27: PRINT USING "### \                    \ "; j%; b$;
	 IF kk% < 100 THEN LOCATE , 52: PRINT USING "### \                    \"; kk%; c$;
	 IF kk% > 99 THEN PRINT CHR$(FNE);
	 PRINT : NEXT
	 GOTO 4440

x.browse29:
PCOPY 1, 0
END SUB

SUB browse30 (browse30.result%, updwn%) STATIC
	 REDIM inuse%(100)
4150 h$ = "F O R M U L A   U P D A T E"
	 CALL setup(h$)
	 COLOR 4: LOCATE 3, 29: PRINT " UPDATE A COMMENT "
	 COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit   F6-Check usage"; : LOCATE 25, 71: PRINT CHR$(24); CHR$(25); "-Move";
	 COLOR 2, 0: k% = 1: GOTO 4290

4200 LOCATE 4, 23: PRINT CHR$(FNE); "Enter comment number..>"
	 LOCATE 4, 47
	 a$ = ""
	 CALL inpnew(a$, 2!, updwn%, "13,59,64,72,73,80,81")
	 IF updwn% = 59 THEN pass = 1: GOTO x.browse30
	 IF updwn% = 72 THEN k% = 1: GOTO 4290      '***** UP arrow
	 IF updwn% = 73 THEN k% = 1: GOTO 4290      '***** PGUP
	 IF updwn% = 80 THEN k% = 50: GOTO 4290     '***** DN arrow
	 IF updwn% = 81 THEN k% = 50: GOTO 4290     '***** PGDN
	 IF updwn% = 64 THEN
		IF checkusage% THEN checkusage% = 0 ELSE checkusage% = -1
		'-Pre pass to check active flag
		FOR i% = 1 TO 100: inuse%(i%) = 0: NEXT
		IF checkusage% THEN
			'-Formualations
			rec65% = 1
			GET #65, rec65%, tntdet
			DO WHILE rec65% < 5000
				IF tntdet.rmat% >= 1 AND tntdet.rmat% < 9999 THEN
						IF tntdet.cmt >= 1 AND tntdet.cmt <= 99 THEN
							IF inuse%(tntdet.cmt) = 0 THEN
								GET #30, tntdet.cmt, mscomt
								IF RTRIM$(mscomt.spk) = "" THEN
									tntdet.cmt = 0
									PUT #65, rec65%, tntdet
								END IF

								IF mscomt.spk > "" THEN
									inuse%(tntdet.cmt) = -1
								END IF
							END IF
						END IF
					END IF
				GET #65, , tntdet: rec65% = rec65% + 1
			LOOP
			'-Tints
			rec55& = 1
			GET #55, rec55&, tntdet
			DO WHILE rec55& < 5000
				IF tntdet.rmat% >= 1 AND tntdet.rmat% < 9999 THEN
						IF tntdet.cmt >= 1 AND tntdet.cmt <= 99 THEN
							IF inuse%(tntdet.cmt) = 0 THEN
								GET #30, tntdet.cmt, mscomt
								IF RTRIM$(mscomt.spk) = "" THEN
									tntdet.cmt = 0
									PUT #55, rec55&, tntdet
								END IF

								IF mscomt.spk > "" THEN
									inuse%(tntdet.cmt) = -1
								END IF
							END IF
						END IF
					END IF
				GET #55, , tntdet: rec55& = rec55& + 1
			LOOP

		END IF
		GOTO 4290
	 END IF
	 b$ = "  ": LSET b$ = a$: b% = VAL(b$)
	 IF b% < 1 OR b% > 99 THEN GOTO x.browse30
	 LOCATE 4, 23: PRINT CHR$(FNE); "Enter new Comment..>"
	 LOCATE 4, 44
	 GET #30, b%, mscomt
	 a$ = mscomt.spk$
	 CALL inpnew(a$, 122!, updwn%, "13,59")
	 mscomt.spk$ = a$
	 PUT #30, b%, mscomt
	 k% = 50: IF b% < 50 THEN k% = 1
4290

	LOCATE 5, 1:
		l% = 0
	FOR i% = k% TO k% + 16
		l% = l% + 1
		c0$ = " ": c1$ = " ": c2$ = " "
		j% = i% + 17: kk% = j% + 17
		GET #30, i%, mscomt: a$ = mscomt.spk$
		GET #30, j%, mscomt: b$ = mscomt.spk$
		IF inuse%(i%) THEN c0$ = CHR$(127)
		IF inuse%(j%) THEN c1$ = CHR$(127)

		IF kk% < 100 THEN
			GET #30, kk%, mscomt: c$ = mscomt.spk$
			IF inuse%(kk%) THEN c2$ = CHR$(127)
		END IF

		LOCATE l% + 4, 2:  PRINT USING "###!\                    \"; i%; c0$; a$;
		LOCATE l% + 4, 28: PRINT USING "###!\                    \"; j%; c1$; b$;
		IF kk% < 100 THEN
		LOCATE l% + 4, 52: PRINT USING "###!\                    \"; kk%; c2$; c$;
		END IF
		IF kk% > 99 THEN LOCATE l% + 4, 52: PRINT CHR$(FNE);

		IF inuse%(i%) THEN COLOR 10, 0: LOCATE l% + 4, 2 + 3: PRINT CHR$(127): COLOR 2, 0
		IF inuse%(j%) THEN COLOR 10, 0: LOCATE l% + 4, 28 + 3: PRINT CHR$(127): COLOR 2, 0
		IF inuse%(kk%) THEN COLOR 10, 0: LOCATE l% + 4, 52 + 3: PRINT CHR$(127): COLOR 2, 0



	NEXT
	GOTO 4200

x.browse30:
	IF browse30.result% < 1 THEN browse30.result% = 1
	IF browse30.result% < 99 THEN browse30.result% = 99
END SUB

SUB browse38 (browse38.result%, updwn%) STATIC
'$INCLUDE: '\tpmanuf\src\browse38.bi'
END SUB

SUB browse38i (browse38.result%) STATIC

END SUB

SUB Browse54 (browse54result%, updwn%) STATIC
	CALL setup("BROWSE FILE")
	btm$ = " F1-Return     F3-Search    F5-Swap Tints/A-F    F10-Update Allocated cost"
	CALL prtbtm(btm$): COLOR 2, 0

	COLOR 6, 0
	LOCATE 4, 2: PRINT "Seq. Cust. Description................... Yield  L.Yld  Date      Cost.  Allc."
	COLOR 2, 0
	found% = 0
	FOR i% = 1 TO maxtnt%
		IF tnthed.tnta$ = tnthedx.tnta$(i%) THEN idx53% = i%: found% = -1: EXIT FOR
		NEXT
	IF NOT found% THEN idx53% = 1
	zz$ = ""

BROWSE54.10: '>>- Display a page
	lin% = 0
	IF idx53% > maxtnt% THEN idx53% = maxtnt% - 19
	IF idx53% < 1 THEN idx53% = 1

	rec& = tnthedx.rrn%(idx53%)
	IF rec& = 0 AND start% > 0 THEN idx53% = start%: start% = 0: GOTO BROWSE54.10
	DO WHILE lin% < 19 AND rec& < maxtnt% AND rec& >= 1
		GET #ch.hed%, rec&, tnthed
		'?? clear up new work field
		IF tnthed.asRmat < 0 OR tnthed.asRmat > 6000 THEN
			tnthed.asRmat = 0
			PUT #ch.hed%, rec&, tnthed
		END IF
		IF tnthed.CostPer <> "LT" AND tnthed.CostPer <> "KG" THEN
			tnthed.CostPer = "LT"
			PUT #ch.hed%, rec&, tnthed
		END IF



		tmp1$ = MID$(tnthed.name$, 1, 4)
		tmp2$ = MID$(tnthed.name$, 5, 6)
		tmp3$ = MID$(tnthed.name$, 11, 5)
		tmp4$ = MID$(tnthed.name$, 16, 8)

		sel% = 0: seltxt% = 0
		IF tnthed.tnt% = INT(rec&) THEN sel% = -1
		IF mode$ = "Tints" AND MID$(tnthed.tnta$, 4, 1) <> "T" THEN sel% = 0
		IF mode$ <> "Tints" AND MID$(tnthed.tnta$, 4, 1) > "F" THEN sel% = 0

		IF zz$ > "" THEN
			IF INSTR(LCASE$(tnthed.name), LCASE$(zz$)) > 0 THEN seltxt% = -1
			IF INSTR(LCASE$(tnthed.desc), LCASE$(zz$)) > 0 THEN seltxt% = -1
		END IF

		IF zz$ > "" AND NOT seltxt% THEN sel% = 0


		IF sel% THEN
			lin% = lin% + 1
			rrn%(lin%) = rec&
			IF lin% = 1 THEN start% = idx53%
			LOCATE lin% + 4, 2: PRINT USING "\  \ \   \ \                            \ ##### ##### \      \ $$##.## $$##.##"; tnthed.tnta$; tnthed.cust$; tnthed.desc$; tnthed.yield; VAL(tmp3$); FNDYY$(tmp4$); tnthed.rawcost!; tnthed.alccost!
			IF tnthed.cust$ > "" THEN
			COLOR 11, 0
			LOCATE lin% + 4, 7: PRINT USING "\    \"; tnthed.cust$
			COLOR 2, 0
			END IF

			IF tnthed.alccost! = 0 THEN LOCATE lin% + 4, 75: PRINT "     ";
			IF lin% = 1 THEN idx.first.rec% = idx53%: browse54result% = idx53%
			END IF

		idx53% = idx53% + 1
		rec& = tnthedx.rrn%(idx53%)
		LOOP

	FOR lin% = lin% + 1 TO 19
		rrn%(lin%) = 0
		LOCATE lin% + 4, 2: PRINT SPACE$(78)
		NEXT


BROWSE54.20:
	LOCATE 3, 23: PRINT "Browse from number..> "
	LOCATE 3, 74: PRINT Modedesc$
	LOCATE 3, 55: PRINT SPACE$(16)
	IF zz$ > "" THEN
		LOCATE 3, 55: PRINT "Filter:"; zz$
	END IF
	IF NOT skip% THEN
		LOCATE 3, 44
		z$ = ""
		CALL inpnew(z$, 206!, updwn%, "13,59-61,63-64,68,72,73,80,81")
	END IF
	skip% = 0

	IF updwn% = 61 THEN
		LOCATE 3, 23: PRINT "Search..:";
		IF RTRIM$(z$) > "" THEN
			zz$ = z$
		ELSE
			CALL inpnew(zz$, 120!, updwn%, "13,59-60,63-64,68,72,73,80,81")
		END IF
		updwn% = 13
	END IF

	SELECT CASE updwn%
	CASE 59: GOTO X.BROWSE54
	CASE 13:
			z$ = RIGHT$(z$, 4)
			CALL cvt.tnt(z$, tnt%, tntf$)
			found% = 0
			FOR i% = 1 TO maxtnt%
				IF z$ = tnthedx.tnta$(i%) THEN idx53% = i%: found% = -1: EXIT FOR
				IF tnthedx.tnta$(i%) > z$ THEN EXIT FOR
				NEXT
			IF found% THEN
				rec& = tnthedx.rrn%(idx53%)
				END IF
			IF NOT found% THEN
				idx53% = i%
				rec& = tnthedx.rrn%(i%)
				END IF

			IF MID$(tnt$, 1, 3) = "000" THEN
				idx53% = idx53% + 1
				rec& = tnthedx.rrn%(idx53%)
				END IF
	CASE 60:
	CASE 63: SELECT CASE mode$
			 CASE "A - F": mode$ = "Tints"
			 CASE "Tints": mode$ = "A - F"
			 CASE ELSE: mode$ = "A - F"
			 END SELECT
			 CALL setchannel
			 CALL load.index(0)
			 idx53% = 1
	CASE 64: 'Search
			zz$ = RTRIM$(z$)
			z$ = ""
			updwn% = 13
			skip% = -1

	CASE 68:
			ulin% = 1
			DO WHILE updwn% <> 59
				IF ulin% < 1 THEN ulin% = 1
				IF ulin% > 19 THEN ulin% = 19: idx53 = idx.first.rec% + 18: updwn% = 68: skip% = -1: EXIT DO

				urec% = rrn%(ulin%)
				IF urec% < 1 OR urec% > maxtnt% THEN updwn% = 0: EXIT DO
				GET #ch.hed%, urec%, tnthed
				upd$ = MID$(STR$(tnthed.alccost!), 2)
				LOCATE ulin% + 4, 75
																CALL inpnew(upd$, 4.2, updwn%, "13,59-60")
				upd! = VAL(upd$): CALL ROUND(upd!, 2.5)
				IF tnthed.alccost! <> upd! THEN
					tnthed.alccost! = upd!
					PUT #ch.hed%, urec%, tnthed
					END IF

				IF updwn% = 13 THEN ulin% = ulin% + 1
				IF updwn% = 60 THEN ulin% = ulin% - 1
				LOOP
	CASE 72: idx53% = idx.first.rec% - 1
	CASE 73: idx53% = idx.first.rec% - 19
	CASE 80: idx53% = idx.first.rec% + 1
	CASE 81: idx53 = idx.first.rec% + 19
	CASE ELSE
	END SELECT

	GOTO BROWSE54.10

X.BROWSE54:


END SUB

SUB calc.hdr STATIC
	stimer = TIMER
	COLOR 7, 0: LOCATE 24, 74: PRINT "µCalcÆ"; : COLOR 2, 0
	'>- All calcs run from the arrays -<

	'>-Add up formula -<
	tot.ext! = 0: tot.ltr! = 0: tot.kg! = 0
	FOR i% = 1 TO maxformseq%
		tot.ext! = tot.ext! + ext!(i%)
		IF ltr!(i%) > 0 THEN tot.ltr! = tot.ltr! + ltr!(i%)
		tot.kg! = tot.kg! + kg!(i%)
		IF rmno%(i%) > 0 AND ltr!(i%) = -1 THEN tot.ltr! = 0' Tanks and Equipment
		NEXT
	CALL ROUND(tot.ext!, 2.5)
	CALL ROUND(tot.ltr!, 1.5)
	CALL ROUND(tot.kg!, 1.5)

	tot.Vsol! = 0: tot.Wsol! = 0
	tot.Vpigment! = 0: tot.vresin! = 0
	tot.Wpigment! = 0
	tot.Wresinsolids! = 0
	FOR i% = 1 TO maxformseq%
		'>- Calc the % to the totals
		vpct!(i%) = 0: IF tot.ltr! <> 0 THEN vpct!(i%) = ltr!(i%) / tot.ltr! * 100
		wpct!(i%) = 0: IF tot.kg! <> 0 THEN wpct!(i%) = kg!(i%) / tot.kg! * 100
		CALL ROUND(vpct!(i%), 2.5)
		CALL ROUND(wpct!(i%), 2.5)

		'> Volume solids
		SELECT CASE rm.cond$(i%)
		CASE "P": Vsol!(i%) = 0: IF rm.sg!(i%) <> 0 THEN Vsol!(i%) = kg!(i%) / rm.sg!(i%)
		CASE "S": Vsol!(i%) = 0
		CASE "R": Vsol!(i%) = 0: IF rm.solidsg!(i%) <> 0 THEN Vsol!(i%) = kg!(i%) * (rm.wtsolid!(i%) / 100) / rm.solidsg!(i%)
		CASE "A": Vsol!(i%) = 0
		CASE ELSE: Vsol!(i%) = 0
		END SELECT
		tot.Vsol! = tot.Vsol! + Vsol!(i%)

		'> Weight solids (Pigment,Solvent,Resin,Addatives)
		SELECT CASE rm.cond$(i%)
		CASE "P": Wsol!(i%) = kg!(i%)
		CASE "S": Wsol!(i%) = 0
		CASE "R": Wsol!(i%) = kg!(i%) * (rm.wtsolid!(i%) / 100)
		CASE "A": Wsol!(i%) = 0
		CASE ELSE: Wsol!(i%) = 0
		END SELECT
		tot.Wsol! = tot.Wsol! + Wsol!(i%)

		'> Total of volume of pigments
		IF rm.cond$(i%) = "P" THEN
			tot.Vpigment! = tot.Vpigment! + Vsol!(i%)
			tot.Wpigment! = tot.Wpigment! + kg!(i%)
			END IF

		'> Total of volome of resins
		IF rm.cond$(i%) = "R" THEN
			tot.vresin! = tot.vresin! + Vsol!(i%)
			tot.Wresinsolids! = tot.Wresinsolids! + Wsol(i%)
			END IF

		NEXT

	tot.vsolpct! = 0: IF tot.kg! <> 0 THEN tot.vsolpct = tot.Vsol! / tot.kg! * 100
	tot.wsolpct! = 0: IF tot.kg! <> 0 THEN tot.wsolpct! = tot.Wsol! / tot.kg! * 100
	tot.pvcpct! = 0: IF tot.vresin! <> 0 THEN tot.pvcpct = tot.Vpigment! / tot.vresin! * 100
	tot.pbrpct! = 0: IF tot.Wresinsolids! <> 0 THEN tot.pbrpct! = tot.Wpigment! / tot.Wresinsolids! * 100
	CALL ROUND(tot.vsolpct!, 2.5)
	CALL ROUND(tot.wsolpct!, 2.5)
	CALL ROUND(tot.pvcpct!, 2.5)
	CALL ROUND(tot.pbrpct!, 2.5)

	COLOR 7, 0: LOCATE 24, 74: PRINT "ÍÍÍÍÍÍ"; : COLOR 2, 0
	etimer = TIMER
END SUB

SUB calcusecost
	 '* Calculate use cost from SG & cost price
	ab$ = msrmat.PurUnit$ + "-" + msrmat.UseUnit$
	SELECT CASE ab$
	CASE "KG-LT": msrmat.UseCost = msrmat.PurCost * msrmat.Sg
	CASE "KG-ML": msrmat.UseCost = msrmat.PurCost * msrmat.Sg / 1000
	CASE "LT-KG"
				IF msrmat.Sg <> 0 THEN msrmat.UseCost = msrmat.PurCost / msrmat.Sg
				IF msrmat.Sg = 0 THEN msrmat.UseCost = msrmat.PurCost
	CASE "LT-GM"
				IF msrmat.Sg <> 0 THEN msrmat.UseCost = msrmat.PurCost / msrmat.Sg * 1000
				IF msrmat.Sg = 0 THEN msrmat.UseCost = msrmat.PurCost / 1000
	CASE "/M-EA": msrmat.UseCost = msrmat.PurCost / 1000
	CASE "/H-EA": msrmat.UseCost = msrmat.PurCost / 100
	CASE "MT-KG": msrmat.UseCost = msrmat.PurCost / 1000
	CASE "MT-GM": msrmat.UseCost = msrmat.PurCost / 1000 / 1000
	CASE "MT-LT": msrmat.UseCost = msrmat.PurCost * msrmat.Sg / 1000
	CASE "MT-ML": msrmat.UseCost = msrmat.PurCost * msrmat.Sg / 1000000
	CASE "LT-OZ": msrmat.UseCost = msrmat.PurCost / 26.7
	CASE "LT-UT": msrmat.UseCost = msrmat.PurCost / 26.7 / 48
	CASE "LT-ML": msrmat.UseCost = msrmat.PurCost / 1000
	CASE "KG-GM": msrmat.UseCost = msrmat.PurCost / 1000
	CASE "GM-LT": msrmat.UseCost = msrmat.PurCost * msrmat.Sg / 1000
	CASE "ML-LT": msrmat.UseCost = msrmat.PurCost * 1000
	CASE "TK": msrmat.UseCost = msrmat.PurCost
	CASE ELSE: msrmat.UseCost = msrmat.PurCost
	END SELECT
	'* Round to 2 decimal plmsrmat.activees UP ie 3.0001 = 3.01
	CALL ROUND(msrmat.UseCost, 2.5)
END SUB

SUB change (rec&, updwn%) STATIC
	sav.tnta$ = tnthed.tnta$
	IF updwn% = 63 THEN rollingupdate% = -1: GOTO CF2'Rolling update

	'> Display hidden lines
	SELECT CASE tnthed.visc1l
	CASE IS < 15: LOCATE 11, 12: PRINT USING "Visc Low/High.> #.# to #.# pse. - Cone _& Plate."; tnthed.visc2l!; tnthed.visc2h!
	CASE ELSE: LOCATE 11, 12: PRINT USING "Visc Low/High.> #.# to #.# pse. - Cone _& Plate."; tnthed.visc2l!; tnthed.visc2h!
	END SELECT
	LOCATE 14, 12: PRINT USING "Filter........> ###"; tnthed.filter%
	LOCATE 15, 12: PRINT USING "Grind (min)...> ##"; tnthed.grind!
	LOCATE 16, 12: PRINT USING "PH....(min)...> #"; tnthed.ph!
	LOCATE 17, 12: PRINT USING "Gloss.(min)...> ##"; tnthed.gloss!


	IF MID$(tnthed.tnta$, 1, 3) > "000" THEN GOTO cf1
cf1a:
	CALL sndmsg("To move the formula, Enter a new number")
	LOCATE 3, 42
	keyin$ = tnthed.tnta$
				CALL inpnew(keyin$, 204!, updwn%, "13,59-60")
	CALL cvt.tnt(keyin$, a%, a$)
	CALL sndmsg("")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf1
	IF keyin$ = tnthed.tnta$ THEN GOTO cf1

	'>- Look to see if the number has already been used if so swap it!
	found% = 0
	FOR i% = 1 TO maxtnt%
		IF keyin$ = tnthedx.tnta$(i%) THEN idx53% = i%: found% = -1: EXIT FOR
		NEXT

	CALL box(12, 7, 52, 11, 7, 0, 1)
	IF found% THEN
		a$ = "N"
		COLOR 2, 0
		LOCATE 8, 14: PRINT USING "\  \ exits.      Swap \  \ with \  \"; keyin$; tnthed.tnta$; keyin$
		LOCATE 10, 14: PRINT USING "Do you wan't to swap numbers..>!"; a$
		END IF
	IF NOT found% THEN
		a$ = "N"
		COLOR 2, 0
		LOCATE 8, 18: PRINT USING "Move \  \ to \   \"; tnthed.tnta$; keyin$
		LOCATE 10, 14: PRINT USING "Do you wan't to continue?.....>!"; a$
		END IF

				LOCATE 10, 45: CALL inpnew(a$, 101!, updwn%, "13,59")
	a$ = UCASE$(a$)
	IF updwn% = 59 THEN GOTO x.change
	IF a$ <> "Y" THEN GOTO x.change

	rec57% = 1
	GET #57, rec57%, batch
	DO WHILE NOT EOF(57)
		IF batch.form$ = tnthed.tnta$ THEN
			batch.form$ = keyin$
			PUT #57, rec57%, batch
			END IF
		GET #57, , batch: rec57% = rec57% + 1
		LOOP

	SELECT CASE mode$
	CASE "A - F": OPEN "fmhist.hst" FOR RANDOM SHARED AS #34 LEN = 62
	CASE "Tints": OPEN "tnhist.hst" FOR RANDOM SHARED AS #34 LEN = 62
	CASE ELSE: OPEN MID$(mode$, 1, 2) + "hist.hst" FOR RANDOM SHARED AS #34 LEN = 62
	END SELECT

	f% = VAL(MID$(tnthed.tnta$, 1, 3))
	f$ = MID$(tnthed.tnta$, 4, 1)
	rec34% = 1
	GET #34, rec34%, fmhisth1
	DO WHILE NOT EOF(34)
		IF fmhisth1.form% = f% THEN
		IF fmhisth1.cost$ = f$ THEN
			fmhisth1.form% = VAL(MID$(keyin$, 1, 3))
			fmhisth1.cost$ = MID$(keyin$, 4, 1)
			PUT #34, rec34%, fmhisth1
			END IF
			END IF
		IF rec34% MOD 100 = 0 THEN CALL sndmsg("Hist. Record:" + STR$(rec34%))
		GET #34, , fmhisth1: rec34% = rec34% + 1
		LOOP
	CLOSE #34
	CALL sndmsg("")
	COLOR 2, 0


	msg$ = sav.tnta$ + " changed to " + keyin$
	IF found% THEN
		swap.rec% = tnthedx.rrn%(idx53%)
		GET #ch.hed%, swap.rec%, tnthed
		tnthed.tnt% = swap.rec%
		tnthed.tnta$ = sav.tnta$
		PUT #ch.hed%, swap.rec%, tnthed
		GET #ch.hed%, rec&, tnthed
		msg$ = sav.tnta$ + " Swapped with " + keyin$
		END IF

	tnthed.tnta$ = keyin$
	rebuild.index% = -1
	GOTO x.change

cf1:
	LOCATE 5, 28
	keyin$ = tnthed.desc$
				CALL inpnew(keyin$, 130!, updwn%, "13,59-60")
	tnthed.desc$ = keyin$
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf1a

CF2:
	LOCATE 6, 28
	keyin$ = MID$(tnthed.name$, 1, 4)
	CALL inpnew(keyin$, 4!, updwn%, "13,59-60")
	MID$(tnthed.name$, 1, 4) = keyin$
	IF updwn% = 59 THEN rollingupdate% = 0: GOTO x.change
	IF updwn% = 60 THEN rollingupdate% = 0: GOTO cf1
	IF rollingupdate% THEN updwn% = 63: GOTO x.change

cf3:
	IF updwn% = 60 AND mode$ = "A - F" THEN GOTO CF2
	IF updwn% = 13 AND mode$ = "A - F" THEN GOTO cf4
	LOCATE 6, 42
	keyin$ = tnthed.cust$
				CALL inpnew(keyin$, 105!, updwn%, "13,59-60")

	IF MID$(keyin$, 1, 1) = " " THEN
		tnthed.cust$ = SPACE$(5)
	END IF

	CALL searchindex(keyin$, 23, found%)
	IF found% THEN
		tnthed.cust$ = keyin$
		CALL dsply(rec&, "N")
	END IF

	IF LEN(keyin$) < 1 OR MID$(keyin$, 1, 1) = " " THEN
		tnthed.cust$ = SPACE$(5)
	END IF

	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO CF2

cf3a:
	LOCATE 7, 28
	keyin$ = MID$(tnthed.name$, 5, 6)
				CALL inpnew(keyin$, 106!, updwn%, "13,59-60,62")
	MID$(tnthed.name$, 5, 6) = keyin$

	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf3

cf3b:
	LOCATE 7, 44
	keyin$ = MID$(tnthed.name$, 11, 5)
				CALL inpnew(keyin$, 105!, updwn%, "13,59-60,62")
	MID$(tnthed.name$, 11, 5) = keyin$

	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf3a
cf3c:
	LOCATE 7, 62
	keyin$ = MID$(tnthed.name$, 16, 8)
	CALL inpnew(keyin$, 108, updwn%, "13,59-60,62")
	MID$(tnthed.name$, 16, 8) = keyin$

	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf3b


cf4:
	LOCATE 8, 28
	keyin$ = "xnn"
	MID$(keyin$, 1, 1) = tnthed.SorW$
	MID$(keyin$, 2, 2) = MID$(STR$(tnthed.class%), 2, 2)
				CALL inpnew(keyin$, 103!, updwn%, "13,59-60,62")
	tnthed.SorW$ = UCASE$(MID$(keyin$, 1, 1))
	tnthed.class% = VAL(MID$(keyin$, 2, 2))

	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf3a
	IF updwn% = 62 THEN CALL browse29(browse29.result%, updwn%): GOTO cf4

cf5:
	LOCATE 9, 28
	keyin$ = STR$(tnthed.yield!)
				CALL inpnew(keyin$, 106.1, updwn%, "13,59-60")
	tnthed.yield! = VAL(keyin$)
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf4

cf5a:
	LOCATE 9, 36
	keyin$ = tnthed.CostPer
				CALL inpnew(keyin$, 102!, updwn%, "13,59-60")
	keyin$ = UCASE$(keyin$)
	IF keyin$ <> "LT" AND keyin$ <> "KG" THEN keyin$ = "LT"
	tnthed.CostPer = keyin$
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf5

cf5b:
	LOCATE 9, 62
	keyin$ = STR$(tnthed.asRmat)
				CALL inpnew(keyin$, 4!, updwn%, "13,59-60")
	tnthed.asRmat = VAL(keyin$)
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf5a


cf6:
	LOCATE 10, 27
	keyin$ = STR$(tnthed.visc1l!)
				CALL inpnew(keyin$, 4.1, updwn%, "13,59-60")
	tnthed.visc1l! = VAL(keyin$)
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf5b

cf7:
	LOCATE 10, 34
	keyin$ = STR$(tnthed.visc1h!)
				CALL inpnew(keyin$, 4.1, updwn%, "13,59-60")
	tnthed.visc1h! = VAL(keyin$)
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf6

cf8:
	LOCATE 11, 28
	keyin$ = STR$(tnthed.visc2l!)
				CALL inpnew(keyin$, 2.1, updwn%, "13,59-60")
	tnthed.visc2l! = VAL(keyin$)
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf7

cf9:
	LOCATE 11, 35
	keyin$ = STR$(tnthed.visc2h!)
				CALL inpnew(keyin$, 2.1, updwn%, "13,59-60")
	tnthed.visc2h! = VAL(keyin$)
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf8


cf10:
	LOCATE 12, 28
	keyin$ = STR$(tnthed.alccost!)
				CALL inpnew(keyin$, 6.2, updwn%, "13,59-60")
	tnthed.alccost! = VAL(keyin$)
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf9

cf11:
	LOCATE 13, 28
	keyin$ = tnthed.hazard$
				CALL inpnew(keyin$, 101!, updwn%, "13,59-60")
	tnthed.hazard$ = keyin$
	CALL hazard(tnthed.hazard$)
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf10

cf12:
	LOCATE 14, 28
	keyin$ = STR$(tnthed.filter%)
	CALL inpnew(keyin$, 3!, updwn%, "13,59-60")
	tnthed.filter% = VAL(keyin$)
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf11


cf13:
	LOCATE 15, 28
	keyin$ = STR$(tnthed.grind!)
	CALL inpnew(keyin$, 2!, updwn%, "13,59-60")
	tnthed.grind! = VAL(keyin$)
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf12


cf14:
	LOCATE 16, 28
	keyin$ = MID$(STR$(tnthed.ph!), 2)
	CALL inpnew(keyin$, 1!, updwn%, "13,59-60")
	tnthed.ph! = VAL(keyin$)
	LOCATE 16, 12: PRINT USING "PH............> #"; tnthed.ph!
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf13

cf15:
	LOCATE 17, 28
	keyin$ = STR$(tnthed.gloss!)
	CALL inpnew(keyin$, 2!, updwn%, "13,59-60")
	tnthed.gloss! = VAL(keyin$)
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf14


	

x.change:
	IF tnthed.tnt% <> rec& THEN rebuild.index% = -1
	tnthed.tnt% = INT(rec&)
	wrkd$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
	tnthed.date$ = FNDY$(wrkd$)
	PUT #ch.hed%, rec&, tnthed
	CALL dsply(rec&, "Y")
	IF rebuild.index% THEN
		CALL load.index(-1)
		rebuild.index% = 0
	END IF


END SUB

SUB Change.tanks (rec&, updwn%)
	DIM tankrrn&(5)

	CALL box(4, 10, 20, 70, 7, 0, 2)
	COLOR 10, 0
	LOCATE 5, 14: PRINT "              TANK AND YIELD SELECTION"
	COLOR 6, 0
	LOCATE 9, 14: PRINT "Code  ID.  Description                     Yield "
	COLOR 2, 0

	COLOR 6, 0: LOCATE 9, 17: PRINT "R/Mat Description.....": COLOR 2, 0


	FOR i% = 1 TO 5: tankrrn&(i%) = 0: NEXT
	startrec& = rec& * maxformseq% - maxformseq% + 1


	'>-- Find the tank records
	n% = 0
	FOR first.seq% = 1 TO maxformseq%
		drec& = startrec& + first.seq% - 1
		GET #ch.det%, drec&, tntdet

		IF tntdet.rmat% >= 1 AND tntdet.rmat% < 9999 THEN
			GET #38, tntdet.rmat, msrmat
		END IF
		sel% = 0
		IF msrmat.UseUnit$ = "EQ" THEN sel% = -1
		IF msrmat.UseUnit$ = "TK" THEN sel% = -1
		rm.tanksize!(lin%) = 0

		IF sel% THEN
			n% = n% + 1
			tankrrn&(n%) = drec&
			rm.tanksize!(lin%) = msrmat.Wtsolid
			tntdet.qty = -1
			COLOR 2, 0
			LOCATE n% + 9, 17: PRINT USING "####| \                  \"; tntdet.rmat%; msrmat.desc1$
			END IF
		NEXT

	'>-Show tank sizes
	thisltr! = tnthed.yield!
	thisltr$ = STR$(thisltr!)

	lin% = 1
	DO
		IF lin% < 1 THEN lin% = 1
		IF lin% > n% THEN lin% = n%

		drec& = tankrrn&(lin%)
		GET #ch.det%, drec&, tntdet
		
		IF tntdet.rmat% >= 1 AND tntdet.rmat% < 9999 THEN
		GET #38, tntdet.rmat, msrmat
		END IF
		LOCATE lin% + 9, 17: PRINT USING "####| \                  \"; tntdet.rmat%; msrmat.desc1$

		LOCATE lin% + 9, 17
		a$ = STR$(tntdet.rmat)
		CALL sndmsg("F6 - Browse")
		CALL inpnew(a$, 4!, updwn%, "13,59,60,64,72,80")
		CALL sndmsg("")
		IF updwn% = 59 THEN EXIT DO
		IF updwn% = 64 THEN
			browse38.result% = tntdet.rmat
			PCOPY 0, 1
			CALL browse38(browse38.result%, updwn%)
			PCOPY 1, 0
			a$ = MID$(STR$(browse38.result%), 2)
			updwn% = 13
			END IF
		IF updwn% = 72 THEN a$ = STR$(tntdet.rmat + 1)
		IF updwn% = 80 THEN a$ = STR$(tntdet.rmat - 1)
		IF updwn% = 60 THEN lin% = lin% - 1
		a! = VAL(a$)
		IF updwn% = 13 AND a! = tntdet.rmat THEN lin% = lin% + 1
		IF a! <> tntdet.rmat AND a! > 0 AND a! < 9999 THEN
			tntdet.rmat = a!
			IF tntdet.rmat < 1 OR tntdet.rmat > 9999 THEN tntdet.rmat = 1
			GET #38, tntdet.rmat, msrmat
			rm.tanksize!(lin%) = msrmat.Wtsolid
			PUT #ch.det%, drec&, tntdet
			
			END IF

		LOOP UNTIL lin% > n%
		IF updwn% = 59 THEN GOTO x.custombatch

		'>-Recalc the header
		auto% = -1
		cost.or.ltrs$ = "Litres"
		CALL load.lines(rec&)
		CALL details(rec&, updwn%, auto%)
		CALL save.lines(rec&, auto%)
		auto% = 0
		updwn% = 0


x.custombatch:
END SUB

SUB cvt.tnt (tnt$, tnt%, tntf$)
	tnt$ = UCASE$(tnt$)

	tnt$ = "    " + tnt$: tnt$ = RIGHT$(tnt$, 4)
	digit% = 4
	SELECT CASE MID$(tnt$, digit%, 1)
	CASE "A" TO "F"
	CASE "T"
	CASE "0" TO "9": tnt$ = tnt$ + "A": tnt$ = RIGHT$(tnt$, 4)
	CASE ELSE: MID$(tnt$, digit%, 1) = "A"
	END SELECT

	alpha% = 0
	alpha% = 0
	FOR digit% = 1 TO 3
	IF MID$(tnt$, digit%, 1) <> " " THEN
		IF MID$(tnt$, digit%, 1) < "0" OR MID$(tnt$, digit%, 1) > "9" THEN MID$(tnt$, digit%, 1) = " ": alpha% = -1
		END IF
	IF alpha% THEN MID$(tnt$, digit%, 1) = " "
	NEXT

	IF ch.hedx% = 53 THEN MID$(tnt$, 4, 1) = "T" ' Force tints

	tnt% = VAL(MID$(tnt$, 1, 3))
	tntf$ = RIGHT$(tnt$, 1)
	tnt$ = "000" + LTRIM$(STR$(tnt%)): tnt$ = RIGHT$(tnt$, 3) + tntf$

END SUB

SUB del.all (idx53%, updwn%) STATIC

	 COLOR 14: LOCATE 4, 21: PRINT "D E L E T I O N    P E N D I N G "
	 LOCATE 25, 1: COLOR 0, 3: PRINT SPACE$(80);
	 LOCATE 25, 21: PRINT "F1 - Abort.     F10 -  Continue.";
	 COLOR 2, 0: LOCATE 1, 1
	 rec& = tnthedx.rrn%(idx53%)


				CALL inpnew(del$, 0!, updwn%, "59,68")
	IF rec& < 1 THEN updwn% = 59
	IF updwn% = 68 THEN
		startrec& = rec& * maxformseq% - maxformseq% + 1

		FOR first.seq% = 1 TO maxformseq%
			drec& = startrec& + first.seq% - 1
			tntdet.tnt& = 0
			tntdet.rmat% = 0
			tntdet.qty! = 0
			tntdet.cmt% = 0
			tntdet.cmtqty! = 0
			tntdet.ltkg$ = " "
			PUT #ch.det%, drec&, tntdet
			NEXT

		GET #ch.hed%, rec&, tnthed
		tnthed.tnt% = 0
		tnthed.tnta$ = ""
		tnthed.revision% = 0
		tnthed.name$ = ""
		tnthed.desc$ = ""
		tnthed.cust$ = ""
		tnthed.SorW$ = ""
		tnthed.class% = 0
		tnthed.yield! = 0
		tnthed.ltr! = 0
		tnthed.kg! = 0
		tnthed.visc1h! = 0
		tnthed.visc1l! = 0
		tnthed.alccost! = 0
		tnthed.rawcost! = 0
		tnthed.filter% = 0
		tnthed.grind! = 0
		tnthed.ph! = 0
		tnthed.Sg! = 0
		tnthed.Vsol! = 0
		tnthed.Wsol! = 0
		tnthed.pvc! = 0
		tnthed.pbr! = 0
		tnthed.gloss! = 0
		tnthed.hazard$ = ""
		tnthed.date$ = ""
		PUT #ch.hed%, rec&, tnthed
	END IF
	CALL load.index(-1)
	idx53% = 0: rec& = 0
END SUB

SUB details (rec&, updwn%, auto%) STATIC
	first.seq% = 1
	current.lin% = 1
	browse38.result% = 0
	IF auto% THEN skip% = -1: updwn% = 59
details.0:
'  CALL setup("UPDATE TINT DETAILS")
'  btm$ = " F1-Return   F3-Ins.  F4-Del.  F5- Stats.  F6-Bse.   F7-Driers  F8-Prt.  F10-Chg"
'  CALL prtbtm(btm$)
'  COLOR 6, 0: LOCATE 3, 2: PRINT "RMat Description                 Qty..                           Cost"
'  COLOR 6, 0
'  LOCATE 3, 41: PRINT "  %Vol.  %Wt..    Cost.   Kg...   Lt..."
'  COLOR 2, 0
'  COLOR 7, 0: LOCATE 2, 2: PRINT "µ  Æ": COLOR 2, 0
'  COLOR 2, 0: LOCATE 2, 3: PRINT "01"
'  LOCATE 23, 2: PRINT STRING$(78, "Ä");
'  LOCATE 23, 6: PRINT "Á"

	'-Becasue all the calcs are done in dpsly.line we must dsply all lines first
	first.seq% = 20
	FOR lin% = 1 TO 19
		CALL dsply.line(rec&, lin%, first.seq%, 0)
		NEXT
	first.seq% = 1
	FOR lin% = 1 TO 19
		CALL dsply.line(rec&, lin%, first.seq%, 1)
		NEXT
	lin% = current.lin%
	CALL dsply.line(rec&, lin%, first.seq%, 3)


END SUB

SUB dsply (rec&, getrec$) STATIC
	IF rec& < 1 OR rec& > maxtnt% THEN
		CALL box(2, 3, 79, 23, 0, 0, 0)
		GOTO x.dsply
		END IF
	IF getrec$ = "Y" THEN
		GET #ch.hed%, rec&, tnthed
		END IF

	keyin$ = tnthed.cust$
	CALL searchindex(keyin$, 23, found%)
	IF NOT found% THEN LSET CUS.sname$ = "?"
	IF keyin$ = "     " THEN LSET CUS.sname$ = " "

	IF found% THEN
		rec43% = CVI(supx.wrrn$)
		IF rec43% < 1 THEN rec43% = 1
		GET #43, rec43%, CUS
		END IF

	 IF tnthed.class% < 1 OR tnthed.class% > 99 THEN
		LSET cldesc$ = "** NO CLASS **"
		ELSE
		GET #29, tnthed.class%, msclass
		cldesc$ = LEFT$(msclass.cldesc$, 15)
	 END IF
	SELECT CASE tnthed.SorW$
	CASE "S": sw$ = "Solvent Based"
	CASE "W": sw$ = "Water Based  "
	CASE ELSE: sw$ = "*NOT LISTED*"
	END SELECT


	LOCATE 3, 42: PRINT USING "\   \ Rev##"; tnthed.tnta$; tnthed.revision%
	LOCATE 3, 71: PRINT USING "\       \"; FNDYY$(tnthed.date$)
	LOCATE 4, 74: PRINT Modedesc$
	LOCATE 5, 12: PRINT USING "Description...> \                             \"; tnthed.desc$
	'COLOR 4, 0: LOCATE 5, 60: PRINT "(MAX)": COLOR 2, 0
	IF mode$ = "Tints" THEN
		LOCATE 6, 36: PRINT USING "Cust..\   \-\                             \"; tnthed.cust$; CUS.sname$
		COLOR 6, 0: LOCATE 6, 36: PRINT "Cust..": COLOR 2, 0
	END IF

	tmp1$ = MID$(tnthed.name$, 1, 4)
	tmp2$ = MID$(tnthed.name$, 5, 6)
	tmp3$ = MID$(tnthed.name$, 11, 5)
	tmp4$ = MID$(tnthed.name$, 16, 8)

	LOCATE 6, 12: PRINT USING "Nominal Batch.> \  \"; tmp1$
	LOCATE 7, 12: PRINT USING "Last Batch....: \    \  Size..  \   \    Date.... \      \"; tmp2$; tmp3$; FNDYY$(tmp4$)
	COLOR 6, 0: LOCATE 7, 36: PRINT "Size..": COLOR 2, 0
	COLOR 6, 0: LOCATE 7, 53: PRINT "Date....": COLOR 2, 0

	LOCATE 8, 12: PRINT USING "Solvent/Water.> !##     Class. \       \ Solvent. \             \"; tnthed.SorW$; tnthed.class%; cldesc$; sw$
	COLOR 6, 0: LOCATE 8, 36: PRINT "Class.": COLOR 2, 0
	COLOR 6, 0: LOCATE 8, 53: PRINT "Solvent.": COLOR 2, 0
	LOCATE 9, 12: PRINT USING "Yield.........> ####.#  \\               Material ####"; tnthed.yield!; tnthed.CostPer$; tnthed.asRmat
	IF tnthed.CostPer = "KG" THEN
	COLOR 6, 0: LOCATE 9, 36: PRINT "Kilos.": COLOR 2, 0
	END IF
	IF tnthed.CostPer = "LT" THEN
	COLOR 6, 0: LOCATE 9, 36: PRINT "Litres": COLOR 2, 0
	END IF


	SELECT CASE tnthed.visc1l
	CASE IS < 15: LOCATE 10, 12: PRINT USING "Visc Low/High.>##.# to ##.# pse. - Rotothinner. "; tnthed.visc1l!; tnthed.visc1h!
	CASE ELSE: LOCATE 10, 12: PRINT USING "Visc Low/High.> ### to ### sec. - Ford Cup _# 4."; tnthed.visc1l!; tnthed.visc1h!
	END SELECT

	IF tnthed.visc2l = 0 THEN
		LOCATE 11, 12: PRINT SPACE$(60)
		ELSE
		LOCATE 11, 12: PRINT USING "Visc Low/High.> #.# to #.# pse. - Cone _& Plate."; tnthed.visc2l!; tnthed.visc2h!
		END IF

	LOCATE 12, 12: PRINT USING "Cost (Alloc.).> $$##.##"; tnthed.alccost!
	LOCATE 13, 12: PRINT USING "Hazard........> !"; tnthed.hazard$

	LOCATE 14, 12: PRINT SPACE$(20)
	LOCATE 15, 12: PRINT SPACE$(20)
	LOCATE 16, 12: PRINT SPACE$(20)
	LOCATE 17, 12: PRINT SPACE$(20)

	IF tnthed.filter% > 0 THEN LOCATE 14, 12: PRINT USING "Filter........> ###"; tnthed.filter%
	IF tnthed.grind! > 0 THEN LOCATE 15, 12: PRINT USING "Grind (min)...> ##"; tnthed.grind!
	IF tnthed.ph! > 0 THEN LOCATE 16, 12: PRINT USING "PH....(min)...> #"; tnthed.ph!
	IF tnthed.gloss! > 0 THEN LOCATE 17, 12: PRINT USING "Gloss (min)...> ##"; tnthed.gloss!

	COLOR 6, 0
	LOCATE 18, 2: PRINT USING "  Litres.     Kilos..     Sg....     Cost/LT!"; ""
	LOCATE 20, 2: PRINT USING "   V/Sol.      W/Sol.     P.V.C.      P.B.R !"; ""
	COLOR 2, 0
	LOCATE 19, 2: PRINT USING "  ####.##     ####.##     ##.###      ##.###"; tnthed.ltr!; tnthed.kg!; tnthed.Sg!; tnthed.rawcost!
	LOCATE 21, 2: PRINT USING "   ###.##      ###.##    ###.##      ###.## "; tnthed.Vsol!; tnthed.Wsol!; tnthed.pvc!; tnthed.pbr!
	CALL hazard(tnthed.hazard$)
x.dsply:
END SUB

SUB dsply.line (rec&, lin%, first.seq%, calc%) STATIC
	'Where rec&       is the record of the formula header
	'      first.seq% is the offset of the first detail record.
	'eg.   Formula 12 and the 14th detail record of that formula.
	'seq% then becomes the array index of the detail arrays

	'Calc% 0= no calc, no dsply (just load line)
	'      1= no calc, dsply one line only
	'      2= no calc, dsply running totals
	'      3= Calc & dsply running totals

	seq% = first.seq% + lin% - 1
	IF seq% > maxformseq% THEN
		IF seq% = maxformseq% + 1 THEN
		LOCATE lin% + 3, 2: PRINT "ÄÄÄÄÁ" + STRING$(73, "Ä")
		ELSE
		LOCATE lin% + 3, 2: PRINT STRING$(78, "  ")
		END IF
		GOTO x.dsply.line
		END IF

	IF rmno%(seq%) > 0 AND rmno%(seq%) < maxrmat% THEN
		GET #38, rmno%(seq%), msrmat
		rm.sg!(seq%) = msrmat.Sg!
		IF msrmat.UseUnit$ = "EQ" THEN rm.sg!(seq%) = 0
		IF msrmat.UseUnit$ = "EA" THEN rm.sg!(seq%) = 0
		rm.wtsolid!(seq%) = msrmat.Wtsolid!
		rm.solidsg!(seq%) = msrmat.Solidsg!
		rm.useunit$(seq%) = msrmat.UseUnit$
		rm.cond$(seq%) = msrmat.cond$
		IF msrmat.PurUnit$ = "TK" THEN rm.tanksize!(seq%) = msrmat.Wtsolid! ELSE rm.tanksize!(seq%) = 0
		END IF

	IF cmtno%(seq%) > 0 AND cmtno%(seq%) <= maxcmt% THEN
		GET #30, cmtno%(seq%), mscomt
		END IF

	IF rmno%(seq%) = 0 THEN qty!(seq%) = 0
	IF rmno%(seq%) > 0 AND qty!(seq%) < 1 AND rm.useunit$(seq%) = "EA" THEN qty!(seq%) = 1
	IF qty!(seq%) < 0 THEN qty!(seq%) = 0
	IF qty!(seq%) > 9999 THEN qty!(seq%) = 9999

	work! = qty!(seq%)
	IF work! = 0 AND msrmat.UseUnit$ = "EQ" AND rmno%(seq%) > 0 THEN work! = 1
	ext! = work! * msrmat.UseCost!

	IF ext! > 9999 THEN ext! = 9999
	IF ext! < -999 THEN ext! = -999

	 ltr! = qty!(seq%) * rm.sg!(seq%)
	 kg! = 0
	 Sg! = rm.sg!(seq%): IF Sg! = 0 THEN Sg! = .0000001
	 IF msrmat.UseUnit$ = "KG" THEN ltr! = qty!(seq%) / Sg!: kg! = qty!(seq%)
	 IF msrmat.UseUnit$ = "GM" THEN ltr! = qty!(seq%) / Sg! / 1000: kg! = qty!(seq%) / 1000
	 IF msrmat.UseUnit$ = "LT" THEN ltr! = qty!(seq%): kg! = qty!(seq%) * Sg!
	 IF msrmat.UseUnit$ = "ML" THEN ltr! = qty!(seq%) / 1000: kg! = qty!(seq%) * Sg! / 1000
	 IF msrmat.UseUnit$ = "TK" THEN ltr! = -1: kg! = 0
	 IF msrmat.UseUnit$ = "EQ" THEN ltr! = -1: kg! = 0

	 'prtbuf$ = "1234³6789 123456789 123456789 123456789 123456789 123456789 123456789 12345678"
	 'prtbuf$ = "####³\                       \  ####\\   #### \                    \  $$###.##"
	prtbuf$ = "    ³                                                                "
	IF rmno%(seq%) > 0 THEN
	MID$(prtbuf$, 1, 4) = format$(CSNG(rmno%(seq%)), "####")
	MID$(prtbuf$, 6, 26) = msrmat.desc1$
	IF qty!(seq%) > 0 THEN
		MID$(prtbuf$, 33, 6) = format$(qty!(seq%), "###.##")
		MID$(prtbuf$, 39, 2) = LCASE$(msrmat.UseUnit$)
		END IF
	IF cmtno%(seq%) > 0 THEN
		MID$(prtbuf$, 47, 22) = mscomt.spk$
	IF cmtqty!(seq%) > 0 THEN
		MID$(prtbuf$, 42, 4) = format$(cmtqty!(seq%), "####")
		END IF
		END IF
	

	END IF


	IF calc% > 0 THEN
		COLOR 2, 0
		LOCATE lin% + 3, 2: PRINT prtbuf$
		COLOR 10, 0
		LOCATE lin% + 3, 40: PRINT MID$(prtbuf$, 39, 2)
		COLOR 2, 0
		END IF


	vpct!(i%) = 0: IF tot.ltr! <> 0 THEN vpct!(i%) = ltr!(i%) / tot.ltr! * 100
	wpct!(i%) = 0: IF tot.kg! <> 0 THEN wpct!(i%) = kg!(i%) / tot.kg! * 100
	CALL ROUND(vpct!(i%), 2.5)
	CALL ROUND(wpct!(i%), 2.5)

	ltr!(seq%) = ltr!
	kg!(seq%) = kg!
	desc$(seq%) = MID$(prtbuf$, 42, 30)
	ext!(seq%) = ext!


	'>---------------------------------<
	IF calc% < 2 GOTO x.dsply.line
	'>---------------------------------<
	IF calc% = 3 THEN CALL calc.hdr

	COLOR 7, 0
	LOCATE 2, 55: PRINT "µ"
	COLOR 2, 0
	LOCATE 2, 56: PRINT USING "$$###.## ####.## ####.##"; tot.ext!; tot.kg!; tot.ltr!
	COLOR 2, 0


	'>- Now go back and display running totals
	run.ltr! = 0: run.ltr.old! = 0
	FOR seq% = 1 TO maxformseq%
		work! = ltr!(seq%)
		IF work! = -1 THEN run.ltr! = 0
		IF work! < .1 THEN work! = 0
		run.ltr! = run.ltr! + work!
		IF run.ltr! < .1 THEN run.ltr! = 0
		IF seq% >= first.seq% AND seq% < first.seq% + 19 THEN
		i% = seq% - first.seq% + 1
		SELECT CASE cost.or.ltrs$
		CASE "Litres"
			IF run.ltr! <> run.ltr.old! AND run.ltr! > 0 THEN
			LOCATE i% + 3, 1 + 42: PRINT USING "\                            \####.##"; desc$(seq%); run.ltr!
			run.ltr.old! = run.ltr!
			ELSE
			LOCATE i% + 3, 1 + 42: PRINT USING "\                            \       "; desc$(seq%)
			END IF
		CASE "Cost  "
			prt$ = "null"
			IF ext!(seq%) > 0 THEN prt$ = "cost"
			IF kg!(seq%) > 0 OR ltr!(seq%) > 0 THEN prt$ = "all "
			SELECT CASE prt$
			CASE "all ": LOCATE i% + 3, 42: PRINT USING "###.## ###.## $$###.## ####.## ####.##"; vpct!(seq%); wpct!(seq%); ext!(seq%); kg!(seq%); ltr!(seq%)
			CASE "cost": LOCATE i% + 3, 42: PRINT USING "              $$###.##                "; ext!(seq%)
			CASE "null": LOCATE i% + 3, 42: PRINT USING "                                     !"; " "
			CASE ELSE
			END SELECT
		CASE ELSE: LOCATE i% + 3, 71: PRINT USING "         "; " "
		END SELECT

		END IF

		NEXT

x.dsply.line:
END SUB

SUB exchange.rmat (updwn%)
	CALL setup("RAW MATERIAL EXCHANGE")
	EXIT SUB '??
	btm$ = " F1-Return."
	CALL prtbtm(btm$): COLOR 2, 0

exchange.rmat.0:
	COLOR 2, 0
	LOCATE 8, 10: PRINT "From raw material number..>"
				LOCATE 8, 37: CALL inpnew(cpyfrom$, 4!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.exchange.rmat
	IF updwn% = 60 THEN GOTO exchange.rmat.0
	cpyfrom% = VAL(cpyfrom$)
	IF cpyfrom% < 1 OR cpyfrom% > maxrmat% THEN GOTO exchange.rmat.0
	GET #38, cpyfrom%, msrmat
	LOCATE 10, 10: PRINT msrmat.desc1$

exchange.rmat.1:
	COLOR 2, 0
	LOCATE 12, 10: PRINT "  To raw material number..>"
				LOCATE 12, 37: CALL inpnew(cpyto$, 4!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.exchange.rmat
	IF updwn% = 60 THEN GOTO exchange.rmat.0
	cpyto% = VAL(cpyto$)
	IF cpyto% < 1 OR cpyto% > maxrmat% THEN GOTO exchange.rmat.1
	GET #38, cpyto%, msrmat
	LOCATE 14, 10: PRINT msrmat.desc1$; SPACE$(40)

	'<<< If the destination does not exist then move RMAT record as well >>>
	addnew% = 0
	IF msrmat.no% <> cpyto% THEN
		LOCATE 14, 10: PRINT "Create new raw material."
		addnew% = -1
		END IF
	IF msrmat.date$ = "        " THEN
		LOCATE 14, 10: PRINT msrmat.desc1$; "    (Date Blanked)"
		addnew% = -1
		END IF

	confirm$ = "N"
exchange.rmat.2:
	COLOR 2, 0
	LOCATE 16, 10: PRINT "       Confirm (Y/N)......>"
				LOCATE 16, 37: CALL inpnew(confirm$, 101!, updwn%, "13,59-60")
	confirm$ = UCASE$(confirm$)
	IF updwn% = 59 THEN GOTO x.exchange.rmat
	IF updwn% = 60 THEN GOTO exchange.rmat.1
	IF confirm$ <> "Y" THEN GOTO exchange.rmat.2
STOP'?? sets
	'>- Go for it!
	IF addnew% THEN
		GET #38, cpyfrom%, msrmat
		msrmat.date$ = "        "
		PUT #38, cpyfrom%, msrmat

		msrmat.no% = cpyto%
		PUT #38, cpyto%, msrmat
		END IF

	count% = 0
	found% = 0
	rec55& = 1
	GET #ch.det%, rec55&, tntdet
	DO WHILE NOT EOF(ch.det%)
		IF rec55& MOD 100 = 0 THEN LOCATE 16, 50: PRINT USING "##,###"; rec55&
		IF tntdet.rmat% = cpyfrom% THEN
			tntdet.rmat% = cpyto%
			PUT #ch.det%, rec55&, tntdet
			count% = count% + 1
			END IF
		GET #ch.det%, , tntdet: rec55& = rec55& + 1
	LOOP

	msg$ = cpyfrom$ + " exchanged with " + cpyto$ + " with " + STR$(count%) + " occurances."
	CALL sndmsg(msg$)
	GOTO exchange.rmat.0


x.exchange.rmat:
	CALL sndmsg("")

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

SUB hazard (code$) STATIC
'$INCLUDE: '\tpmanuf\src\hazard.bi'
END SUB

SUB height.in.tank (updwn%, seq%, Ltrs.in!, Height.from.btm!, Height.from.top!) STATIC
	'$INCLUDE: '\tpmanuf\src\MSTANK.INC'
END SUB

SUB history (rec&, updwn%)
	OPEN "c:\tpexe\msupd02d.wrk" FOR RANDOM SHARED AS #97
	FIELD #97, 55 AS wrk97$

	 COLOR 10: LOCATE 4, 21: PRINT "TRANSFER TO HISTORY": COLOR 2, 0
	 LOCATE 25, 1: COLOR 0, 3: PRINT SPACE$(80);
	 LOCATE 25, 21: PRINT "F1 - Abort.     F10 -  Continue.";
	 COLOR 2, 0: LOCATE 1, 1
				 CALL inpnew(del$, 0!, updwn%, "59,68")
	 IF updwn% <> 68 THEN GOTO x.history

	CALL box(11, 7, 67, 13, 7, 0, 1)
	COLOR 6, 0: LOCATE 8, 13: PRINT "Enter batch history comments....;": COLOR 2, 0
	COLOR 0, 3: LOCATE 24, 1: PRINT SPACE$(80);
	COLOR 0, 3: LOCATE 24, 2: PRINT " F1 - Abort.     F2 - Prev. (Incuding Revision #)";
	COLOR 2, 0
	GET #97, 1: a1$ = wrk97$
	GET #97, 2: a2$ = wrk97$
	GET #97, 3: a3$ = wrk97$
	GET #97, 4: a4$ = wrk97$
	LOCATE 9, 12: PRINT a1$
	LOCATE 10, 12: PRINT a2$
	LOCATE 11, 12: PRINT a3$
	LOCATE 12, 12: PRINT a4$

	GOTO h1
h0:
				LOCATE 3, 52: CALL inpnew(arev$, 2!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.history
	IF updwn% = 60 THEN GOTO h0
	IF updwn% = 13 THEN
		GET #ch.hed%, rec&, tnthed
		arev% = VAL(arev$)
		IF arev% < 1 THEN arev% = 1
		tnthed.revision% = arev%
		PUT #ch.hed%, rec&, tnthed
		END IF


h1:
				LOCATE 9, 12: CALL inpnew(a1$, 155!, updwn%, "13,59-60")
	LSET wrk97$ = a1$: PUT #97, 1
	IF updwn% = 59 THEN GOTO x99.history
	IF updwn% = 60 THEN GOTO h0
h2:
				LOCATE 10, 12: CALL inpnew(a2$, 155!, updwn%, "13,59-60")
	LSET wrk97$ = a2$: PUT #97, 2
	IF updwn% = 59 THEN GOTO x99.history
	IF updwn% = 60 THEN GOTO h1
h3:
				LOCATE 11, 12: CALL inpnew(a3$, 155!, updwn%, "13,59-60")
	LSET wrk97$ = a3$: PUT #97, 3
	IF updwn% = 59 THEN GOTO x99.history
	IF updwn% = 60 THEN GOTO h2
h4:
				LOCATE 12, 12: CALL inpnew(a4$, 155!, updwn%, "13,59-60")
	LSET wrk97$ = a4$: PUT #97, 4
	IF updwn% = 59 THEN GOTO x99.history
	IF updwn% = 60 THEN GOTO h3

	startrec& = rec& * maxformseq% - maxformseq% + 1
	maxrecipe% = 1
	FOR first.seq% = 1 TO maxformseq%
		drec& = startrec& + first.seq% - 1
		GET #ch.det%, drec&, tntdet
		IF tntdet.rmat% >= 1 AND tntdet.rmat% <= maxrmat% THEN maxrecipe% = first.seq%
		NEXT

x99.history:
	CLOSE #97
	IF updwn% = 59 THEN GOTO x.history

	SELECT CASE mode$
	CASE "A - F": OPEN "fmhist.hst" FOR RANDOM SHARED AS #34 LEN = 62
	CASE "Tints": OPEN "tnhist.hst" FOR RANDOM SHARED AS #34 LEN = 62
	CASE ELSE: OPEN MID$(mode$, 1, 2) + "hist.hst" FOR RANDOM SHARED AS #34 LEN = 62
	END SELECT
	
		hstrec% = LOF(34) / 62

		fmhisth1.form% = VAL(MID$(tnthed.tnta$, 1, 3))
		fmhisth1.cost$ = MID$(tnthed.tnta$, 4, 1)
		fmhisth1.rev% = tnthed.revision%
		fmhisth1.seq% = 1
		fmhisth1.rel% = 1
		fmhisth1.desc$ = tnthed.desc$
		fmhisth1.type$ = tnthed.SorW$
		fmhisth1.class% = tnthed.class%
		fmhisth1.yld! = tnthed.yield!
		fmhisth1.visl! = tnthed.visc1l!
		fmhisth1.vish! = tnthed.visc1h!
		fmhisth1.hdate = tnthed.date
		hstrec% = hstrec% + 1
		PUT #34, hstrec%, fmhisth1

		fmhisth2.form% = VAL(MID$(tnthed.tnta$, 1, 3))
		fmhisth2.cost$ = MID$(tnthed.tnta$, 4, 1)
		fmhisth2.rev% = 1
		fmhisth2.seq% = 2
		hstrec% = hstrec% + 1
		PUT #34, hstrec%, fmhisth2


		fmhisth3.form% = VAL(MID$(tnthed.tnta$, 1, 3))
		fmhisth3.cost$ = MID$(tnthed.tnta$, 4, 1)
		fmhisth3.rev% = 1
		fmhisth3.seq% = 3
		fmhisth3.text$ = a1$
		hstrec% = hstrec% + 1
		PUT #34, hstrec%, fmhisth3

		fmhisth3.form% = VAL(MID$(tnthed.tnta$, 1, 3))
		fmhisth3.cost$ = MID$(tnthed.tnta$, 4, 1)
		fmhisth3.rev% = 1
		fmhisth3.seq% = 4
		fmhisth3.text$ = a2$
		hstrec% = hstrec% + 1
		PUT #34, hstrec%, fmhisth3

		fmhisth3.form% = VAL(MID$(tnthed.tnta$, 1, 3))
		fmhisth3.cost$ = MID$(tnthed.tnta$, 4, 1)
		fmhisth3.rev% = 1
		fmhisth3.seq% = 5
		fmhisth3.text$ = a3$
		hstrec% = hstrec% + 1
		PUT #34, hstrec%, fmhisth3

		fmhisth3.form% = VAL(MID$(tnthed.tnta$, 1, 3))
		fmhisth3.cost$ = MID$(tnthed.tnta$, 4, 1)
		fmhisth3.rev% = 1
		fmhisth3.seq% = 6
		fmhisth3.text$ = a4$
		hstrec% = hstrec% + 1
		PUT #34, hstrec%, fmhisth3

		startrec& = rec& * maxformseq% - maxformseq% + 1

		seq% = 6
		FOR first.seq% = 1 TO maxrecipe%
			drec& = startrec& + first.seq% - 1
			GET #ch.det%, drec&, tntdet

			fmhistd1.form% = VAL(MID$(tnthed.tnta$, 1, 3))
			fmhistd1.cost$ = MID$(tnthed.tnta$, 4, 1)
			fmhistd1.rev% = 1
			seq% = seq% + 1: fmhistd1.seq% = seq%

			IF tntdet.rmat% >= 1 AND tntdet.rmat% <= maxrmat% THEN
				GET #38, tntdet.rmat%, msrmat
				rmat% = -1
				ELSE
				rmat% = 0
				END IF
			IF tntdet.cmt% > 1 AND tntdet.cmt% <= 99 THEN
				GET #30, tntdet.cmt%, mscomt
				cmt% = -1
				ELSE
				cmt% = 0
				END IF

			fmhistd1.desc$ = SPACE$(99)
			fmhistd1.qty! = 0
			fmhistd1.unit$ = "  "
			fmhistd1.cmtqty% = 0
			fmhistd1.cmt$ = ""

			IF rmat% THEN
				fmhistd1.desc$ = msrmat.desc1$
				fmhistd1.qty! = tntdet.qty!
				fmhistd1.unit$ = msrmat.UseUnit$
				fmhistd1.cmtqty% = 0
				END IF

			IF cmt% THEN
				fmhistd1.cmtqty% = tntdet.cmtqty!
				fmhistd1.cmt$ = mscomt.spk$
				END IF

			hstrec% = hstrec% + 1
			PUT #34, hstrec%, fmhistd1
			NEXT



	 msg$ = ("Transfer successful")
	 CALL sndmsg(msg$)
	 SLEEP 1

	 GET #ch.hed%, rec&, tnthed
	 tnthed.revision% = tnthed.revision% + 1
	 PUT #ch.hed%, rec&, tnthed

	CLOSE #34

x.history:
END SUB

SUB insert.recipe (idx53%, updwn%, tnt$) STATIC
	CALL setup("COPY RECIPE FROM OTHER SYSTEM")
	btm$ = " F1-Return.          F5-Stats.       F6-Browse"
	CALL prtbtm(btm$): COLOR 2, 0
	idx53% = 0: updwn% = 0
	svmode$ = mode$: svhedx% = ch.hedx%: svhed% = ch.hed%
	xmode$ = mode$

	fromtnta$ = tnthed.tnta$
	
insert.recipe.1:
	COLOR 2, 0
	LOCATE 8, 10: PRINT "This recipe is not on file."
	LOCATE 10, 10: PRINT "Add a new recipe?..>" + tnt$
	LOCATE 12, 10: PRINT "Option  (Y/N,C)....>"
	LOCATE 13, 10: PRINT USING "From set \    \ "; mode$
	LOCATE 14, 10: PRINT USING "    copy \    \ "; fromtnta$

	'tnt$ = ""
				LOCATE 10, 30: CALL inpnew(tnt$, 104!, updwn%, "13,59-60")
	IF updwn% = 59 THEN updwn% = 0: GOTO x.insert.recipe
	IF updwn% = 60 THEN updwn% = 0: GOTO x.insert.recipe
	CALL cvt.tnt(tnt$, a%, af$)
	IF a% = 0 THEN GOTO insert.recipe.1
	LOCATE 10, 30: PRINT tnt$

	opt$ = "N"
				LOCATE 12, 30: CALL inpnew(opt$, 101!, updwn%, "13,59-60")
	opt$ = UCASE$(opt$)
	IF updwn% = 59 THEN updwn% = 0: GOTO x.insert.recipe
	IF updwn% = 60 THEN updwn% = 0: GOTO x.insert.recipe
	IF opt$ <> "Y" AND opt$ <> "C" THEN updwn% = 0: GOTO x.insert.recipe
	CALL cvt.tnt(tnt$, a%, af$)
	IF a% = 0 THEN GOTO insert.recipe.1

	'>- Check it does not exist
	found% = 0
	FOR i% = 1 TO maxtnt%
		IF tnt$ = tnthedx.tnta$(i%) THEN found% = -1: EXIT FOR
	NEXT
	IF found% THEN
		msg$ = "Formula " + tnt$ + " already exits"
		CALL sndmsg(msg$)
		GOTO insert.recipe.1
	END IF


	'>-- Find the copy from recipe (if any)
	IF opt$ = "C" THEN
		GOTO insert.recipe.3:
insert.recipe.2:
		xmode$ = mode$
								LOCATE 13, 19: CALL inpnew(xmode$, 105!, updwn%, "13,59-60")
		IF updwn% = 59 THEN updwn% = 0: GOTO x.insert.recipe
		IF updwn% = 60 THEN updwn% = 0: GOTO x.insert.recipe

		mode$ = xmode$
		CALL setchannel: xmode$ = mode$
		CALL load.index(0)
		LOCATE 13, 19: PRINT mode$

insert.recipe.3:
								LOCATE 14, 19: CALL inpnew(fromtnta$, 104!, updwn%, "13,59-60")
		IF updwn% = 59 THEN updwn% = 0: GOTO x.insert.recipe
		IF updwn% = 60 THEN updwn% = 0: GOTO insert.recipe.2:

		MID$(fromtnta$, 4, 1) = UCASE$(MID$(fromtnta$, 4, 1))

		'-Auto swap modes
		'-"A - F"
		IF MID$(fromtnta$, 4, 1) >= "A" AND MID$(fromtnta$, 4, 1) <= "F" THEN
			IF xmode$ <> "A - F" AND mode$ <> "A - F" THEN
				xmode$ = "A - F"
				mode$ = xmode$
				CALL setchannel: xmode$ = mode$
				CALL load.index(0)
				LOCATE 13, 19: PRINT mode$
			END IF
		END IF
		'-Tints
		IF MID$(fromtnta$, 4, 1) >= "T" AND MID$(fromtnta$, 4, 1) <= "T" THEN
			IF xmode$ <> "Tints" AND mode$ <> "Tints" THEN
				xmode$ = "Tints"
				mode$ = xmode$
				CALL setchannel: xmode$ = mode$
				CALL load.index(0)
				LOCATE 13, 19: PRINT mode$
			END IF
		END IF



		CALL cvt.tnt(fromtnta$, a%, af$)
		IF a% = 0 THEN GOTO insert.recipe.3
			LOCATE 14, 19: PRINT fromtnta$

			IF xmode$ <> svmode$ THEN 'Copy from another system
				mode$ = xmode$
				CALL setchannel
				CALL load.index(0)
			END IF

			found% = 0
			FOR i% = 1 TO maxtnt%
				IF fromtnta$ = tnthedx.tnta$(i%) THEN
					idx53% = i%: found% = -1: EXIT FOR
				END IF
				IF tnthedx.tnta$(i%) > fromtnta$ THEN EXIT FOR
			NEXT
			IF found% THEN
				fromrec& = tnthedx.rrn%(idx53%)
			ELSE
				fromrec& = 0
			END IF


			IF NOT found% THEN
				CALL sndmsg("From recipe not found.")
				GOTO insert.recipe.3
			ELSE
				CALL sndmsg("")
			END IF
		END IF


	'>-- Continue with the insert
	'>-- Show the yield of the formula
	'Set to target system
	mode$ = xmode$
	CALL setchannel
	CALL load.index(0)
	frmch.hedx% = ch.hedx%: frmch.hed% = ch.hed%: frmch.det% = ch.det%

	'Set to source system to store the from file numbers
	mode$ = svmode$
	CALL setchannel
	CALL load.index(0)



	GET #ch.hed%, fromrec&, tnthed
	COLOR 2
	LOCATE 15, 10: PRINT "Previous yield..>"; tnthed.yield
	LOCATE 16, 10: PRINT "Required yield..> "

	ry$ = STR$(tnthed.yield)
				LOCATE 16, 28: CALL inpnew(ry$, 6.1, updwn%, "13,59-60")
	IF updwn% = 59 THEN updwn% = 0: GOTO x.insert.recipe
	IF updwn% = 60 THEN updwn% = 0: GOTO x.insert.recipe
	Mult! = VAL(ry$) / tnthed.yield
	CALL ROUND(Mult!, 5.5)


	'>- Now look for a empty record
	found% = 0
	rec54% = 1
	GET #ch.hed%, rec54%, tnthed
	DO WHILE NOT EOF(ch.hed%)
		IF MID$(tnthed.tnta$, 1, 3) <= "000" THEN found% = -1: EXIT DO
		GET #ch.hed%, , tnthed: rec54% = rec54% + 1
	LOOP

	IF NOT found% AND EOF(ch.hed%) AND rec54% <= maxtnt% THEN found% = -1
	IF NOT found% THEN
		msg$ = "The file is full. Suck eggs baby!!"
		CALL sndmsg(msg$)
		GOTO insert.recipe.1
	END IF

	rec& = rec54%

	tnthed.tnt% = INT(rec&)
	tnthed.tnta$ = tnt$
	tnthed.revision% = 1
	tnthed.name$ = "New."
	tnthed.desc$ = "New.."
	tnthed.cust$ = ""
	tnthed.SorW$ = ""
	tnthed.class% = 0
	tnthed.yield! = 0
	tnthed.ltr! = 0
	tnthed.kg! = 0
	tnthed.visc1h! = 0
	tnthed.visc1l! = 0
	tnthed.alccost! = 0
	tnthed.rawcost! = 0
	tnthed.filter% = 0
	tnthed.grind! = 0
	tnthed.ph! = 0
	tnthed.Sg! = 0
	tnthed.Vsol! = 0
	tnthed.Vsol! = 0
	tnthed.pvc! = 0
	tnthed.pbr! = 0
	tnthed.gloss! = 0
	tnthed.hazard$ = ""
	tnthed.date$ = ""
	PUT #ch.hed%, rec&, tnthed

	msg$ = "Formula " + tnthed.tnta$ + " added"
	CALL sndmsg(msg$)

	'<--Now do the copy
	IF opt$ = "C" THEN
		GET #frmch.hed%, fromrec&, tnthed
		from$ = tnthed.tnta$
		tnthed.tnt% = INT(rec&)
		tnthed.name$ = "Copied from " + from$
		tnthed.revision% = 1
		tnthed.yield = VAL(ry$)
		tnthed.tnta$ = tnt$
		PUT #ch.hed%, rec&, tnthed

		'-<< Copy Details
		sfromrec& = fromrec& * maxformseq% - maxformseq% + 1
		startrec& = rec& * maxformseq% - maxformseq% + 1

		FOR first.seq% = 1 TO maxformseq%
			dfromrec& = sfromrec& + first.seq% - 1
			GET #frmch.det%, dfromrec&, tntdet
			drec& = startrec& + first.seq% - 1
			tntdet.tnt& = drec&
			tntdet.qty = tntdet.qty * Mult! 'Convert to portion
			PUT #ch.det%, drec&, tntdet
			NEXT

		msg$ = msg$ + " and loaded with a copy of " + from$
		CALL sndmsg(msg$)
		END IF

	CALL load.index(-1)
	found% = 0
	FOR i% = 1 TO maxtnt%
		IF tnt$ = tnthedx.tnta$(i%) THEN idx53% = i%: found% = -1: EXIT FOR
		NEXT
	IF NOT found% THEN
	idx53% = 0
	END IF


	'>-Find the  tank records.
	CALL Change.tanks(rec&, updwn%)
	tnt$ = ""

x.insert.recipe:
	CALL sndmsg("")
	mode$ = svmode$
	CALL setchannel
	CALL load.index(0)

END SUB

SUB load.index (rebuild%)
	IF NOT rebuild% THEN GOTO loadonly
	maxtnt% = 999
	DIM in$(maxtnt%), in%(maxtnt%)
	rec& = 1
	GET #ch.hed%, rec&, tnthed
	DO WHILE NOT EOF(ch.hed%)
		in$(rec&) = tnthed.tnta$: in%(rec&) = rec&
		IF tnthed.tnt% <> rec& THEN in$(rec&) = "~~~~": in%(rec&) = 0
		IF MID$(tnthed.tnta$, 1, 3) < "000" THEN in$(rec&) = "~~~~": in%(rec&) = 0

		'>> - Wheel on screen
		chr% = rec& MOD 4: chrlist$ = "|/-\"
		char$ = MID$(chrlist$, chr% + 1, 1)
		COLOR 7, 0: LOCATE 24, 78: PRINT char$; : COLOR 2, 0
		GET #ch.hed%, , tnthed: rec& = rec& + 1
		LOOP

	s% = rec&
	FOR rec& = s% TO maxtnt%
		in$(rec&) = "~~~~": in%(rec&) = 0
		NEXT


	n% = maxtnt%
	CALL qsort(in$(), in%(), n%, ok%)

	FOR rec& = 1 TO maxtnt%
		tnthedx.tnta$(rec&) = in$(rec&)
		tnthedx.rrn%(rec&) = in%(rec&)
		NEXT

	PUT #ch.hedx%, 1, tnthedx

loadonly:
	GET #ch.hedx%, 1, tnthedx

END SUB

SUB load.lines (rec&) STATIC
	startrec& = rec& * maxformseq% - maxformseq% + 1

	FOR first.seq% = 1 TO maxformseq%
	drec& = startrec& + first.seq% - 1
	GET #ch.det%, drec&, tntdet
	IF tntdet.tnt& <> drec& THEN
		tntdet.tnt& = 0
		tntdet.rmat% = 0
		tntdet.qty! = 0
		tntdet.cmt% = 0
		tntdet.cmtqty! = 0
		tntdet.ltkg$ = " "
		PUT #ch.det%, drec&, tntdet
		END IF

	 rmno%(first.seq%) = tntdet.rmat%
	 qty!(first.seq%) = tntdet.qty!
	 cmtno%(first.seq%) = tntdet.cmt%
	 cmtqty!(first.seq%) = tntdet.cmtqty!
							
	'>- These are set in DSPLY.LINE
	 desc$(first.seq%) = ""
	 vpct!(first.seq%) = 0
	 wpct!(first.seq%) = 0
	 ltr!(first.seq%) = 0
	 kg!(first.seq%) = 0
	 ext!(first.seq%) = 0

	 NEXT

END SUB

SUB printit
	'STDOUT$ = "shit.sht"
	STDOUT$ = "lpt1"

	 IF tnthed.class% < 1 OR tnthed.class% > 99 THEN
		LSET cldesc$ = "** NO CLASS **"
		ELSE
		GET #29, tnthed.class%, msclass
		cldesc$ = LEFT$(msclass.cldesc$, 15)
		END IF
	SELECT CASE tnthed.SorW$
	CASE "S": sw$ = "Solvent"
	CASE "W": sw$ = "Water  "
	CASE ELSE: sw$ = "Martians"
	END SELECT


	OPEN STDOUT$ FOR OUTPUT AS #99
	PRINT #99, TAB(1); CHR$(14); msmisc.cc$
	PRINT #99, " #msupd01d"; TAB(71); DATE1$
	PRINT #99, TAB(10); CHR$(14); tnthed.desc$
	PRINT #99, "ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿"
	IF tnthed.yield! < 100 THEN
	PRINT #99, USING "³Formula \   \  Rev. ##  ³ Class \      \    ³          Custom Yield:##.## Lt.³"; tnthed.tnta$; tnthed.revision%; cldesc$; tnthed.yield!
	ELSE
	PRINT #99, USING "³Formula \   \  Rev. ##  ³ Class \      \    ³          Custom Yield:##### Lt.³"; tnthed.tnta$; tnthed.revision%; cldesc$; tnthed.yield!
	PRINT #99, USING "ÃÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ!"; "´"
	END IF

	PRINT #99, USING "Customer......> \    \ - \                             \"; tnthed.cust$; CUS.sname$
	PRINT #99, USING "Solvent/Water.> !##   \     \-\        \      "; tnthed.SorW$; tnthed.class%; "Solvent"; sw$; cldesc$
	PRINT #99, USING "Cost (Alloc.).> $$##.##"; tnthed.alccost!
	PRINT #99, USING "Hazard........> !"; tnthed.hazard$

	PRINT #99, USING "|---------------------------------------------|!"; ""
	PRINT #99, USING "|  Litres.     Kilos..     Sg....     Cost/LT |!"; ""
	PRINT #99, USING "|   V/Sol.      W/Sol.     P.V.C.      P.B.R  |!"; ""
	PRINT #99, USING "|  ####.##     ####.##     ##.###      ##.### |"; tnthed.ltr!; tnthed.kg!; tnthed.Sg!; tnthed.rawcost!
	PRINT #99, USING "|   ###.##      ###.##    ###.##      ###.##  |"; tnthed.Vsol!; tnthed.Wsol!; tnthed.pvc!; tnthed.pbr!
	PRINT #99, USING "|---------------------------------------------|!"; ""

	PRINT #99, " "
	PRINT #99, "ÃÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ´"
	PRINT #99, "³No. ³ COMPONENT                ³ Lt/Kg.³%Vol.  %Wt      Cost    Kg...   Lt...³"
	PRINT #99, "ÀÄÄÄÄÅÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÙ"

	FOR seq% = 1 TO 38

	IF rmno%(seq%) = 0 THEN qty!(seq%) = 0
	IF rmno%(seq%) > 0 AND qty!(seq%) < 1 AND rm.useunit$(seq%) = "EA" THEN qty!(seq%) = 1
	IF qty!(seq%) < 0 THEN qty!(seq%) = 0
	IF qty!(seq%) > 9999 THEN qty!(seq%) = 9999

	'prtbuf$ = "1234³6789 123456789 123456789 12345678   "
	'prtbuf$ = "####³\                       \  ####\\   "
	 prtbuf$ = "    ³                                    "

	IF rmno%(seq%) > 0 THEN
	IF rmno%(seq%) > 0 AND rmno%(seq%) < maxrmat% THEN
		GET #38, rmno%(seq%), msrmat
		END IF

	MID$(prtbuf$, 1, 4) = format$(CSNG(rmno%(seq%)), "####")
	MID$(prtbuf$, 6, 26) = msrmat.desc1$
	IF qty!(seq%) > 0 THEN
		MID$(prtbuf$, 33, 6) = format$(qty!(seq%), "###.##")
		MID$(prtbuf$, 39, 2) = LCASE$(msrmat.UseUnit$)
		END IF


	PRINT #99, " "; prtbuf$;

	prt$ = "null"
	IF ext!(seq%) > 0 THEN prt$ = "cost"
	IF kg!(seq%) > 0 OR ltr!(seq%) > 0 THEN prt$ = "all "
	SELECT CASE prt$
	CASE "all ": PRINT #99, USING "##.##  ##.## $$###.## ####.## ####.##"; vpct!(seq%); wpct!(seq%); ext!(seq%); kg!(seq%); ltr!(seq%)
	CASE "cost": PRINT #99, USING "             $$###.##                "; ext!(seq%)
	CASE "null": PRINT #99, USING "                                    !"; " "
	CASE ELSE
	END SELECT


	END IF
	NEXT

	PRINT #99, USING "ÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ!"; ""
	PRINT #99, USING "& $$###.## ####.## ####.##"; SPACE$(53); tot.ext!; tot.kg!; tot.ltr!


	text1$ = "                    "
	text2$ = "                 "
	text3$ = "                      "

	IF tnthed.visc1l! > 0 AND tnthed.visc1l < 10 THEN
		text1$ = "R/T " + format$(tnthed.visc1l!, "#.#") + " - " + format$(tnthed.visc1h!, "#.#") + " =     "
		END IF

	IF tnthed.visc1l! > 10 THEN
		text1$ = "CUP " + format$(tnthed.visc1l!, "###") + " - " + format$(tnthed.visc1h!, "###") + " =     "
		END IF

	IF tnthed.ph! > 0 THEN
		text2$ = "PH.. >" + format$(tnthed.ph!, "#") + " =     "
		END IF

	IF tnthed.grind! > 0 THEN
		text2$ = "HEG. <" + format$(tnthed.grind!, "#.#") + " =     "
		END IF

	IF tnthed.visc2l! > 0 THEN
		text3$ = "C&P " + format$(tnthed.visc2l!, "#.#") + " - " + format$(tnthed.visc2h!, "#.#") + " =     "
		END IF


	PRINT #99, USING "ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄ!"; "¿"
	PRINT #99, USING "³\                  \³\               \³\                     \³Iss. \      \ !"; text1$; text2$; text3$; DATE1$; "³"
	PRINT #99, USING "ÃÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÁÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÅÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÅÄÄÄÄÄÄÄÄÄÄÄÄÄÄ!"; "´"
	PRINT #99, USING "³COLOUR =      ³SHEEN =    ³DRY.. =    ³FILTER ### ³ S/G #.### ³Date.         !"; tnthed.filter%; tnthed.Sg!; "³"
	PRINT #99, USING "ÀÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄ!"; "Ù"

	PRINT #99, CHR$(12);
	CLOSE #99
END SUB

SUB psi.write.form
END SUB

SUB qsort (in$(), in%(), n%, ok%) STATIC
'$INCLUDE: '\tpmanuf\src\QSORT.bi'
END SUB

SUB resins (startsearch%, seq%, updwn%)
'//////////////////////////////////////////////////
'/////   SOLVENT
'//////////////////////////////////////////////////
	' CALL setup("SOLVENTS")
	seq.sav% = seq%
	updwn% = 0
	'>- Search for solvents -<
	a$ = ""
	IF startsearch% < 1 THEN startsearch% = 1
	IF startsearch% > maxformseq% THEN startsearch% = maxformseq%
	FOR i% = 1 TO 5: resin.id%(i%) = 0: resin.Lt!(i%) = 0: resin.SolidKG!(i%) = 0: NEXT

	FOR pass% = 1 TO 5

		found% = 0
		FOR i% = startsearch% TO maxformseq%
			IF rm.cond$(i%) = "R" AND rmno%(i%) <> resin.id%(1) AND rmno%(i%) <> resin.id%(2) AND rmno%(i%) <> resin.id%(3) AND rmno%(i%) <> resin.id%(4) AND rmno%(i%) <> resin.id%(5) THEN found% = -1: startsearch% = startsearch% + 1: EXIT FOR
		NEXT
		IF NOT found% THEN EXIT FOR

		resin.id%(pass%) = rmno%(i%)

		'>> Add up all occurances of this solvent <<
		resin.Lt!(pass%) = 0
		resin.SolidKG!(pass%) = 0
		FOR i% = 1 TO maxformseq%
			IF rmno%(i%) <> 2890 THEN
				IF rmno%(i%) = resin.id%(pass%) THEN resin.SolidKG!(pass%) = resin.SolidKG!(pass%) + Wsol!(i%)
				IF rmno%(i%) = resin.id%(pass%) THEN resin.Lt!(pass%) = resin.Lt!(pass%) + qty!(i%)
			END IF
		NEXT

	NEXT pass%

	COLOR 7, 0
	 LOCATE 24, 2: PRINT USING "µ #### #,###.##³ #### #,###.##³ #### #,###.##³ #### #,###.##³ #### #,###.##Æ"; resin.id%(1); resin.Lt!(1); resin.id%(2); resin.Lt!(2); resin.id%(3); resin.Lt!(3); resin.id%(4); resin.Lt!(4); resin.id%(5); resin.Lt!(5);
	btm$ = " F1 - Exit.    F7-Calculate driers"
	CALL prtbtm(btm$): COLOR 2, 0
				LOCATE 24, 1: CALL inpnew(a$, 0!, updwn%, "13,59,60,65")
	IF updwn% = 59 THEN GOTO x.solvents
	IF updwn% = 60 THEN GOTO x.solvents
	IF updwn% = 13 THEN GOTO x.solvents


	'<< Calcs for resin solids <<
'  Tot.YC040! = 0
	Tot.Cobalt! = 0
	Tot.Lead! = 0
	Tot.Calcium! = 0
	Tot.Manganese! = 0                                          '*******
	Tot.Poly! = 0                                          '*******
	FOR pass% = 1 TO 6                                          '*******
		SolidKG! = resin.SolidKG!(pass%)
		'YC040!(pass%) = SolidKG! * .06
		'Cobalt!(pass%) = YC040!(pass%) * .14
		Cobalt!(pass%) = resin.SolidKG!(pass%) * .05 / 6     '*******
		'Lead!(pass%) = YC040!(pass%) * .26
		lead!(pass%) = resin.SolidKG!(pass%) * .5 / 24        '*******
		'Calcium!(pass%) = YC040!(pass%) * .42
		Calcium!(pass%) = resin.SolidKG!(pass%) * .1 / 5        '*******
		'Manganese!(pass%) = YC040!(pass%) * .07                 '*******
		Manganese!(pass%) = resin.SolidKG!(pass%) * .025 / 6    '*******
		Meko!(pass%) = SolidKG! * .01
		POLY!(pass%) = SolidKG! * .015

		'ALL ROUND(YC040!(pass%), 2.5)
		CALL ROUND(Cobalt!(pass%), 2.5)
		CALL ROUND(lead!(pass%), 2.5)
		CALL ROUND(Calcium!(pass%), 2.5)
		CALL ROUND(Manganese!(pass%), 2.5)                      '*******
		CALL ROUND(Meko!(pass%), 2.5)
		CALL ROUND(POLY!(pass%), 2.5)

		'Tot.YC040! = Tot.YC040! + YC040(pass%)
		Tot.Cobalt! = Tot.Cobalt! + Cobalt!(pass%)
		Tot.Lead! = Tot.Lead! + lead!(pass%)
		Tot.Calcium! = Tot.Calcium! + Calcium!(pass%)
		Tot.Manganese! = Tot.Manganese! + Manganese!(pass%)     '*******
		Tot.Meko! = Tot.Meko! + Meko!(pass%)
		Tot.Poly! = Tot.Poly! + POLY!(pass%)
		'y% = pass% + 10
		'LOCATE y%, 2: PRINT USING "µCob 6% ##.##³PB 32% ##.##³CA 5%  ##.##³Meko  ###.##³YC040  ##.##          Æ"; Cobalt!(pass%); Lead!(pass%); Calcium!(pass%); Meko!(pass%); YC040!(pass%);

		NEXT

		LOCATE 24, 2: PRINT USING "µCO 6% #.##³PB24% #.##³CA 5% #.##³MN 5% #.##- Meko #.##³             PA #.## Æ"; Tot.Cobalt!; Tot.Lead!; Tot.Calcium!; Tot.Manganese!; Tot.Meko!; Tot.Poly!;
	 'LOCATE 24, 2: PRINT USING "µCO 6% #.##³PB32% #.##³CA 5% #.##³MN 5% #.##- Meko #.##³YC040 ##.##- PA #.## Æ"; Tot.Cobalt!; Tot.Lead!; Tot.Calcium!; Tot.Manganese!; Tot.Meko!; Tot.YC040!; Tot.Poly!;

	btm$ = "F1 - Exit.    F7-Add Driers and MEKO to formula"
	CALL prtbtm(btm$): COLOR 2, 0
				LOCATE 24, 1: CALL inpnew(a$, 0!, updwn%, "13,59,60,65")
	IF updwn% = 59 THEN GOTO x.solvents
	IF updwn% = 60 THEN GOTO x.solvents
	IF updwn% = 65 THEN
				seq% = seq% + 1
				FOR j% = 1 TO 6
				FOR i% = maxformseq% TO seq% + 1 STEP -1
					rmno%(i%) = rmno%(i% - 1)
					qty!(i%) = qty!(i% - 1)
					cmtno%(i%) = cmtno%(i% - 1)
					cmtqty!(i%) = cmtqty!(i% - 1)

					desc$(i%) = desc$(i% - 1)
					vpct!(i%) = vpct!(i% - 1)
					wpct!(i%) = wpct!(i% - 1)
					ltr!(i%) = ltr!(i% - 1)
					kg!(i%) = kg!(i% - 1)
					ext!(i%) = ext!(i% - 1)

					Wsol!(i%) = Wsol!(i% - 1)
					Wsol!(i%) = Wsol!(i% - 1)
					rm.sg!(i%) = rm.sg!(i% - 1)
					rm.wtsolid!(i%) = rm.wtsolid!(i% - 1)
					rm.solidsg!(i%) = rm.solidsg!(i% - 1)
					rm.useunit$(i%) = rm.useunit$(i% - 1)
					rm.cond$(i%) = rm.cond$(i% - 1)
					rm.tanksize!(i%) = rm.tanksize!(i% - 1)

					NEXT

				rmno%(seq%) = 0: qty!(seq%) = 0: cmtno%(seq%) = 0: cmtqty!(seq%) = 0
				desc$(seq%) = "": vpct!(seq%) = 0: wpct!(seq%) = 0: ltr!(seq%) = 0: kg!(seq%) = 0: ext!(seq%) = 0

				NEXT

'??
				rmno%(seq% + 0) = 2890: qty!(seq% + 0) = Tot.Poly!
				rmno%(seq% + 1) = 1775: qty!(seq% + 1) = Tot.Cobalt!
				rmno%(seq% + 2) = 1727: qty!(seq% + 2) = Tot.Lead!
				rmno%(seq% + 3) = 1777: qty!(seq% + 3) = Tot.Calcium!
				rmno%(seq% + 4) = 1779: qty!(seq% + 4) = Tot.Manganese!
				rmno%(seq% + 5) = 2434: qty!(seq% + 5) = Tot.Meko!
				seq% = 38
				DO WHILE rmno%(seq% - 1) = 0
					seq% = seq% - 1
				LOOP
				'rmno%(seq%) = 2737
				'qty!(seq%) = Tot.YC040!
				updwn% = 60

		END IF

x.solvents:
	seq% = seq.sav%

END SUB

SUB save.lines (rec&, auto%) STATIC
	 CALL setup("E X I T   F O R U M U L A   E D I T")
	 COLOR 8, 3: LOCATE 25, 1: PRINT SPACE$(80); : COLOR 4, 0
	 COLOR 6: LOCATE 7, 25: PRINT "Return to Initial Menu"
	 COLOR 2
	 LOCATE 8, 25: PRINT "   1.  WITHOUT UPDATE"
	 LOCATE 9, 25: PRINT "   2.  WITH    UPDATE"
	 LOCATE 11, 29: PRINT "Your choice.> "; 'CHR$(FNH);
	 opt% = 2 '**Force save (NOTE: The system keeps track of save by its self)
	 IF NOT auto% THEN
			in$ = STR$(opt%): in$ = MID$(in$, 2)
			LOCATE 11, 43: CALL inpnew(in$, 1!, updwn%, "13")
			opt% = VAL(in$)
	 END IF

	'>>----- S A V E -----<<
	IF opt% = 2 THEN
	startrec& = rec& * maxformseq% - maxformseq% + 1
		
	FOR seq% = 1 TO maxformseq%
		drec& = startrec& + seq% - 1
		tntdet.tnt& = drec&
		tntdet.rmat% = rmno%(seq%)
		tntdet.qty! = qty!(seq%)
		tntdet.cmt% = cmtno%(seq%)
		tntdet.cmtqty! = cmtqty!(seq%)
		
		PUT #ch.det%, drec&, tntdet
	 NEXT

	 GET #ch.hed%, rec&, tnthed
	 tnthed.rawcost! = 0
	 IF tnthed.yield! <> 0 THEN
		 tnthed.rawcost! = tot.ext! / tnthed.yield!
		 CALL ROUND(tnthed.rawcost!, 2.5)
	 END IF
	 tnthed.ltr! = tot.ltr!
	 tnthed.kg! = tot.kg!
	 tnthed.Sg! = 0: IF tot.ltr! <> 0 THEN tnthed.Sg! = tot.kg! / tot.ltr!
	 tnthed.Vsol! = tot.vsolpct!
	 tnthed.Wsol! = tot.wsolpct!
	 tnthed.pvc! = tot.pvcpct!
	 tnthed.pbr! = tot.pbrpct!
	 wrkd$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
	 tnthed.date$ = FNDY$(wrkd$)


	 'IF tnthed.alccost! = 0 THEN tnthed.alccost! = tnthed.rawcost!
	 PUT #ch.hed%, rec&, tnthed
	 END IF

	 '>-Transfer to raw material file.
	 IF tnthed.asRmat > 0 AND tnthed.asRmat < maxrmat% THEN
		GET #38, tnthed.asRmat, msrmat
			msrmat.Sg = tnthed.Sg!
			msrmat.PurCost = tnthed.rawcost!
			CALL calcusecost
		PUT #38, tnthed.asRmat, msrmat
	 END IF

END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

SUB setchannel
'$INCLUDE: '\tpmanuf\src\tntfiles.inc'
END SUB

