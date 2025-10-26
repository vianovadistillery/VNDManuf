DECLARE SUB prtstk (totltr!)
DECLARE SUB accbrowse (rec%)
DECLARE SUB accbrowseo (rec%)
DECLARE SUB add.up.order (tot.ltact!, tot.ord!, tot.ext!)
DECLARE SUB browse30 (browse30.result%, updwn%)
DECLARE SUB browse38i (browse38.result%)
DECLARE SUB browse38 (browse38.result%, updwn%)
DECLARE SUB browse57 (browse57.result%, updwn%)
DECLARE SUB browse.idx (firstonscreen%, ch1%, ch2%)
DECLARE SUB calc.hdr ()
DECLARE SUB calcusecost ()
DECLARE SUB cf8 (l%, d.elem%, newdata$)
DECLARE SUB change (rec26%, updwn%)
DECLARE SUB chglin (ln%, l%, d.elem%, updwn%)
DECLARE SUB cvt.tnt (tnt$, tnt%, tntf$)
DECLARE SUB delOrder (hord%, n%, clr%, autodel$, thissup$, norders%)
DECLARE SUB details (rec&, updwn%, auto%, rview%)
DECLARE SUB dsply (rec26%)
DECLARE SUB dsplyLine (l%, d.elem%)
DECLARE SUB dsply.line (rec&, lin%, first.seq%, calc%)
DECLARE SUB dsporders (dspstart%, norders%, custin$)
DECLARE SUB ean13 (in$, dind%)
DECLARE SUB findnext (hord%, norders%, ok%)
DECLARE SUB findorders (thissup$, norders%, hord%)
DECLARE SUB height.in.tank (updwn%, seq%, Ltrs.in!, Height.from.btm!, Height.from.top!)
DECLARE SUB killa (file$)
DECLARE SUB linkedl (rrn%(), n%, firstrec%, ord%, chd%)
DECLARE SUB loadLine (m%, il%, ditem%, ordqty%, invqty%, price!, gate!)
DECLARE SUB load.lines (rec%, eyld!)
DECLARE SUB mline (hord%, rview%, thisbatch$)
DECLARE SUB printit ()
DECLARE SUB printstk (totltr!)
DECLARE SUB ReturntoStock (form$, thisltr!)
DECLARE SUB resins (startsearch%, seq%, updwn%)
DECLARE SUB rightprice (price!)
DECLARE SUB save.lines (rec26%, auto%)
DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB selectfile (filename$, updwn%)
DECLARE SUB UpdateOrder (hord%, updwn%)
DECLARE FUNCTION format$ (VALUE!, definition$)

	COMMON SHARED maxsup%, maxform%, maxrmat%, maxacc%, maxtypes, maxcus%, maxord%, bchno%
	COMMON SHARED qk$, keyl%, rep$
	COMMON SHARED batchltr!, perltr!, fillcost!, batchsg!, pack%
	COMMON SHARED msg$, datafile$
	COMMON SHARED maxbrw%, rec26%
	COMMON SHARED maxformseq%
	COMMON SHARED cost.or.ltrs$
	COMMON SHARED mode$, beg$
	COMMON SHARED TaxRate!, DiscRate!
	COMMON SHARED ext.has.changed%, rec50%, ctl%, Cash%
	COMMON SHARED vdisc!, Rate!, discovr!, climit!, ovrPrice!
	COMMON SHARED tot.gst!, tot.exti!, tot.allup!
	COMMON SHARED skipexit%
	COMMON SHARED doc.type$, formtype$, sno%
	COMMON SHARED tot.ord!, tot.ltact, tot.ltinv, tot.dollr, tot.items&
	COMMON SHARED hord%
	COMMON SHARED newsearch$
	COMMON SHARED bysearch$
	COMMON SHARED search.key$
	COMMON SHARED tot.qty, Tot.taxvol
	COMMON SHARED tot.dg200%, tot.dg60%, tot.dg20%, tot.dg10%, tot.dg4%, tot.dg2%, tot.dg1%, tot.dg850%, tot.dg500%, tot.dg300%, tot.dg250%, tot.dglt!
	COMMON SHARED extdisc!, inv.lt.printed!
	COMMON SHARED tender$
	COMMON SHARED invmsg1$, invmsg2$, invmsg3$, invmsg4$
	COMMON SHARED ean$
	COMMON SHARED tot.ext!, tot.ltr!, tot.kg!, tot.Vsol!, tot.Wsol!
	COMMON SHARED tot.vsolpct!, tot.wsolpct!, tot.pvcpct!, tot.pbrpct!
	COMMON SHARED Modedesc$


COMMON SHARED qty!(), ext!(), kg!(), ltr!(), vpct!(), wpct!(), Wsol!(), Vsol!()
COMMON SHARED resin.id%(), resin.Lt!(), resin.SolidKG!()
COMMON SHARED Cobalt!(), lead!(), Manganese!(), Calcium!(), Meko!(), POLY!()
COMMON SHARED rmno%(), rm.sg!(), rm.wtsolid!(), rm.solidsg!(), rm.cond$(), rm.useunit$(), rm.tanksize!(), rm.tankltmm!()
COMMON SHARED cmtno%(), cmtqty!(), desc$(), rmbno$()


	CONST maxlines% = 45 '
	CONST GST! = 10  '10%
	maxformseq% = 38
	typefields% = -1



	DIM SHARED perc!(6), c1%(6)
	DIM SHARED resin.id%(6), resin.Lt!(6), resin.SolidKG!(6)
	DIM SHARED Cobalt!(6), lead!(6), Calcium!(6), Manganese!(6), Meko!(6), POLY!(6)'***** YC040!(6),
	DIM SHARED rmno%(maxformseq%), qty!(maxformseq%), cmtno%(maxformseq%), cmtqty!(maxformseq%)
	DIM SHARED desc$(maxformseq%), vpct!(maxformseq%), wpct!(maxformseq%), ltr!(maxformseq%), kg!(maxformseq%), ext!(maxformseq%)
	DIM SHARED Vsol!(maxformseq%), Wsol!(maxformseq%), rmbno$(maxformseq%)
	DIM SHARED rm.sg!(maxformseq%), rm.wtsolid!(maxformseq%), rm.solidsg!(maxformseq%)
	DIM SHARED rm.useunit$(maxformseq%), rm.cond$(maxformseq%), rm.tanksize!(maxformseq%), rm.tankltmm!(maxformseq%)
	DIM SHARED auditfile$(15), naudit%, acstkf$
	DIM SHARED orders%(1001)
	DIM SHARED c%(8), in$(maxlines%, 15), rrn%(maxlines%)
	'1=qty%,2=size,3=unit,4=itm,5=desc,6=price,7=SOH,8=ext
	'9=tax flag,10=ordqty%,11=Invqty,12=BoFlag,13=save qty
	'14=Save item, 15=Overtyped price, 16=Pack


'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "DSMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'

	acstkf$ = "..."
	parm3$ = ""
	parm$ = ENVIRON$("PARM$")
	IF VAL(parm$) > 0 THEN pass.getcust% = -1: custin$ = parm$: updwn% = 13
	parm2$ = ENVIRON$("PARM2$")
	IF parm2$ = "PRE..." THEN acstkf$ = "PRE"


	'$INCLUDE: '\tpmanuf\src\msbatch.inc'
	'$INCLUDE: '\tpmanuf\src\msbatchh.inc'
	'$INCLUDE: '\tpmanuf\src\msclass.inc'
	'$INCLUDE: '\tpmanuf\src\acmgn.inc'
	'$INCLUDE: '\tpmanuf\src\acstk.inc'
	'$INCLUDE: '\tpmanuf\src\company.inc'
	'$INCLUDE: '\tpmanuf\src\msrmat.inc'
	'$INCLUDE: '\tpmanuf\src\ordhed.inc'
	'$INCLUDE: '\tpmanuf\src\orddet.inc'
	'$INCLUDE: '\tpmanuf\src\ordprt.inc'
	'$INCLUDE: '\tpmanuf\src\tnthed.inc'
	CLOSE #54
	'$INCLUDE: '\tpmanuf\src\forhed.inc'
	'$INCLUDE: '\tpmanuf\src\tntdet.inc'
	CLOSE #55

	keyl% = 20: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)

	DATA 2,7,10,13,18,56,63,72
	FOR i% = 1 TO 8: READ c%(i%): NEXT
	RESET

	SELECT CASE acstkf$
	CASE "PRE": CALL index("OPEN ", ind%, "acstkx3.pre", 7, keyl%)
	CASE ELSE: CALL index("OPEN ", ind%, "acstkx3.acf", 7, keyl%)
	END SELECT
		'$INCLUDE: '\tpmanuf\src\msmisc.inc'
		'$INCLUDE: '\tpmanuf\src\pickup.INC'
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxacc% = CVI(msmisc.max5$): maxtypes% = CVI(msmisc.max6$): maxcus% = CVI(msmisc.max7$)
	maxord% = 999
	'CALL setaudit(naudit%)
	parm$ = ENVIRON$("PARM$")
	IF parm$ = "/prt.." THEN
		ENVIRON "PARM$=......"
		after.prtinv% = -1
		CALL mline(hord%, rview%, thisbatch$)
	END IF

	'Clear all but the invnum and invnumrec%
	hord% = 0: opt% = 0: Cash% = 0: tender$ = ""
	chginv# = 0: chginv.rrn% = 0
	thissup$ = "": norders% = 0
	invmsg1$ = "": invmsg2$ = ""

SUB accbrowseo (rec%) STATIC
'npgm$ = "dsinv04d"
'CALL EXITPGM(npgm$)
'SHELL npgm$
END SUB

SUB add.up.order (tot.ltact!, tot.ord!, tot.ext!) STATIC
add.up.order:
	'- Add up total litres and calc discount $
	tot.ltact = 0
	tot.ext = 0
	tot.items& = 0
	FOR i% = 1 TO maxlines%
		'- Add up litres order and actualy on order
		ltact = 0
		qty = VAL(in$(i%, 1))
		size! = VAL(in$(i%, 2))

		SELECT CASE UCASE$(in$(i%, 3))
			CASE "ML":
				ltact = qty! * VAL(in$(i%, 2)) / 1000
			CASE "LT":
				ltact = qty! * VAL(in$(i%, 2))
			CASE "LS":
				ltact = qty! * VAL(in$(i%, 2))
			CASE "GM":
				ltact = qty! * VAL(in$(i%, 2)) / 1000 / batchsg
			CASE "GS":
				ltact = qty! * VAL(in$(i%, 2)) / 1000 / batchsg
			CASE "KG":
				ltact = qty! * VAL(in$(i%, 2)) / batchsg
			CASE ELSE: ltact = 0
		END SELECT
			 ltact = ltact * VAL(in$(i%, 16))


		'IF in$(i%, 3) = "LS" THEN ltact = qty * size!
		'IF in$(i%, 3) = "LT" THEN ltact = qty * size!
		'IF in$(i%, 3) = "ML" THEN ltact = qty * size! / 1000

		tot.ltact = tot.ltact + ltact
		ext! = VAL(in$(i%, 8))
		tot.ext = tot.ext + ext!
		tot.items& = tot.items& + qty
	NEXT
	'- Set the total litres ever placed on this order
	tot.ord! = CVS(ordhed.horgq$)
	IF tot.ltact! > tot.ord! THEN tot.ord! = tot.ltact!
	IF discovr! <> 0 THEN tot.ord! = discovr!

	'- Calculate the volume discount
	a = tot.ord!
	IF CUS.stype$ = "W" THEN a = 0
	CALL round(a, .5)
	vdisc! = 0: DiscRate! = 0
	SELECT CASE a'Total ordered + header volume adjustment
	CASE 100 TO 199: vdisc! = tot.ltact * .05: DiscRate! = .05
	CASE 200 TO 399: vdisc! = tot.ltact * .075: DiscRate! = .075
	CASE 400 TO 599: vdisc! = tot.ltact * .1: DiscRate! = .1
	CASE 600 TO 999: vdisc! = tot.ltact * .122: DiscRate! = .125
	CASE IS >= 1000: vdisc! = tot.ltact * .15: DiscRate! = .15
	CASE ELSE: vdisc! = 0: DiscRate! = 0
	END SELECT
	'no volume discount
	vdisc! = 0: DiscRate! = 0
'- Round the very bottom price for cash items
	IF Cash% AND 1 = 2 THEN
'Start a +10Cents and step back to -10Cents.
			tot.allup = tot.ext - vdisc!
			temptotal = tot.allup
			tot.gst! = temptotal * (TaxRate! / 100): CALL round(tot.gst!, 2.5)
			tot.allup = temptotal + tot.gst!
			Cents! = tot.allup - FIX(tot.allup)
			Cents% = Cents! * 100
			IF Cents% MOD 5 = 0 THEN   'Until 5 Cent round
			END IF
	END IF
'- Print out bottom line of the invoice
	tot.allup = tot.ext - vdisc!
	temptotal = tot.allup
	tot.gst! = temptotal * (TaxRate! / 100): CALL round(tot.gst!, 2.5)
'>-- The price may be overwritten
	IF ovrPrice! <> -9999 THEN
		tot.allup! = ovrPrice!
		tot.gst! = tot.allup! / 11: CALL round(tot.gst!, 2.5)
		temptotal = tot.allup! - tot.gst!
		vdisc! = tot.ext! - (tot.allup! - tot.gst!)
	END IF
	tot.allup = temptotal + tot.gst!
	COLOR 2, 0
	fillcost! = perltr! * batchltr! / tot.ltact!
	LOCATE 21, 2: PRINT USING " Manufactured cost of Bulk $$##.###/L       Litres in Batch           #,###.##"; perltr!; batchltr!
	LOCATE 22, 2: PRINT USING "       Filled cost of Bulk $$##.###/L       Volume Allocated          #,###.##"; fillcost!; tot.ltact!
	LOCATE 23, 2: PRINT USING "                     Yield   ###.##%        Volume Unallocated       ##,###.##"; tot.ltact! / batchltr! * 100; batchltr! - tot.ltact!
	IF batchltr! - tot.ord! < 0 THEN
		COLOR 4
		LOCATE 23, 71: PRINT USING "##,###.##"; batchltr! - tot.ltact!
	END IF
	COLOR 7, 0
	'LOCATE 24, 69: PRINT USING "µ$$#####.##º"; tot.allup; : COLOR 2, 0
	'COLOR 10, 0:
	'LOCATE 24, 70: PRINT USING "$$#####.##"; tot.allup; : COLOR 2, 0
	COLOR 2, 0
	ext.has.changed% = 0
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
								IF RTRIM$(mscomt.spk$) = "" THEN
									tntdet.cmt = 0
									PUT #65, rec65%, tntdet
								END IF

								IF mscomt.spk$ > "" THEN
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
								IF RTRIM$(mscomt.spk$) = "" THEN
									tntdet.cmt = 0
									PUT #55, rec55&, tntdet
								END IF

								IF mscomt.spk$ > "" THEN
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
	 B$ = "  ": LSET B$ = a$: B% = VAL(B$)
	 IF B% < 1 OR B% > 99 THEN GOTO x.browse30
	 LOCATE 4, 23: PRINT CHR$(FNE); "Enter new Comment..>"
	 LOCATE 4, 44
	 GET #30, B%, mscomt
	 a$ = mscomt.spk$
	 CALL inpnew(a$, 122!, updwn%, "13,59")
	 mscomt.spk$ = a$
	 PUT #30, B%, mscomt
	 k% = 50: IF B% < 50 THEN k% = 1
4290

	LOCATE 5, 1:
		l% = 0
	FOR i% = k% TO k% + 16
		l% = l% + 1
		c0$ = " ": c1$ = " ": c2$ = " "
		j% = i% + 17: kk% = j% + 17
		GET #30, i%, mscomt: a$ = mscomt.spk$
		GET #30, j%, mscomt: B$ = mscomt.spk$
		IF inuse%(i%) THEN c0$ = CHR$(127)
		IF inuse%(j%) THEN c1$ = CHR$(127)

		IF kk% < 100 THEN
			GET #30, kk%, mscomt: c$ = mscomt.spk$
			IF inuse%(kk%) THEN c2$ = CHR$(127)
		END IF

		LOCATE l% + 4, 2:  PRINT USING "###!\                    \"; i%; c0$; a$;
		LOCATE l% + 4, 28: PRINT USING "###!\                    \"; j%; c1$; B$;
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

SUB browse38i (browse38.result%) STATIC

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
	CALL round(tot.ext!, 2.5)
	CALL round(tot.ltr!, 1.5)
	CALL round(tot.kg!, 1.5)

	tot.Vsol! = 0: tot.Wsol! = 0
	tot.Vpigment! = 0: tot.vresin! = 0
	tot.Wpigment! = 0
	tot.Wresinsolids! = 0
	FOR i% = 1 TO maxformseq%
		'>- Calc the % to the totals
		vpct!(i%) = 0: IF tot.ltr! <> 0 THEN vpct!(i%) = ltr!(i%) / tot.ltr! * 100
		wpct!(i%) = 0: IF tot.kg! <> 0 THEN wpct!(i%) = kg!(i%) / tot.kg! * 100
		CALL round(vpct!(i%), 2.5)
		CALL round(wpct!(i%), 2.5)

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
	CALL round(tot.vsolpct!, 2.5)
	CALL round(tot.wsolpct!, 2.5)
	CALL round(tot.pvcpct!, 2.5)
	CALL round(tot.pbrpct!, 2.5)

	COLOR 7, 0: LOCATE 24, 74: PRINT "ÍÍÍÍÍÍ"; : COLOR 2, 0
	etimer = TIMER
END SUB

SUB cf8 (l%, d.elem%, newdata$)
REDIM x20%(20)
'--EXTENSION
cf8:
	qty! = VAL(in$(l%, 1))
	size! = VAL(in$(l%, 2))
	price! = VAL(in$(l%, 6))
'>-- Stock items 1-20 are special reusable items
	IF VAL(in$(l%, 4)) = 1 AND ctl% = 4 THEN
'Load an array of the first 20 stock units on order
		FOR i% = 1 TO 20: x20%(i%) = 0: NEXT:
		x20%(1) = -1: x20%(2) = -1: x20%(3) = -1'On backorder' ' order complete'
		i% = 1
		GET #49, i%, orddet
		DO WHILE i% < 10000 AND NOT EOF(49)
			IF orddet.dord% <> -1 THEN
				j% = CVI(orddet.ditem$)
				IF j% > 1 AND j% <= 20 THEN x20%(j%) = -1
			END IF
			GET #49, , orddet: i% = i% + 1
		LOOP
		FOR i% = 1 TO maxlines%
			j% = VAL(in$(i%, 4))
			IF j% > 1 AND j% <= 20 THEN x20%(j%) = -1
		NEXT
		spec% = 1
		FOR i% = 1 TO 20
			IF x20%(i%) = 0 THEN spec% = i%: EXIT FOR
		NEXT
		in$(l%, 4) = STR$(spec%)
		d.elem% = 1' this is hard coded
		ln% = (l% - d.elem%) MOD 15 + 1: ln% = ln% + 4
		LOCATE ln%, c%(4): PRINT USING "####"; spec%
		LOCATE ln%, c%(5): PRINT acstk.Desc1$; " "; acstk.desc2$
		dkt$ = acstk.Desc1$
		LOCATE ln%, c%(5)
		CALL inpnew(dkt$, 125!, updwn%, "13,60")
		LSET acstk.Desc1$ = dkt$
		dkt$ = acstk.desc2$
		LOCATE ln%, c%(5) + 26
		CALL inpnew(dkt$, 110!, updwn%, "13,60")
		LSET acstk.desc2$ = dkt$
		LOCATE ln%, c%(5): PRINT acstk.Desc1$; " "; acstk.desc2$
		in$(l%, 5) = acstk.Desc1$ + " " + acstk.desc2$
		LOCATE ln%, c%(6)
		in$(l%, 6) = STR$(acstk.PurCost!)
								CALL inpnew(in$(l%, 6), 5.2, updwn%, "13")
		price! = VAL(in$(l%, 6))
		TaxRate! = GST
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
		ctl% = 6
	END IF
	old.ext! = VAL(in$(l%, 8))
		SELECT CASE UCASE$(in$(l%, 3))
			CASE "ML":
				ext! = qty! * VAL(in$(l%, 2)) / 1000
			CASE "LT":
				ext! = qty! * VAL(in$(l%, 2))
			CASE "LS":
				ext! = qty! * VAL(in$(l%, 2))
			CASE "GM":
				ext! = qty! * VAL(in$(l%, 2)) / 1000 / batchsg
			CASE "GS":
				ext! = qty! * VAL(in$(l%, 2)) / 1000 / batchsg
			CASE "KG":
				ext! = qty! * VAL(in$(l%, 2)) / batchsg
			CASE ELSE: ltact = 0
		END SELECT
			 ext! = ext! * VAL(in$(l%, 16))

	'ext! = qty! * VAL(in$(l%, 2)) '?? - to make rview work - but does it stop normal
	in$(l%, 8) = STR$(ext!)
	IF old.ext! <> ext! THEN ext.has.changed% = -1
END SUB

SUB chglin (ln%, l%, d.elem%, updwn%)

	ctl% = 1: chg = 0: maxctl% = 7
	WHILE NOT ctl%
		'Edit
		IF ctl% < 1 OR ctl% > maxctl% THEN ctl% = 1
		ON ctl% GOSUB cf1, cf2, cf3, cf4, cf5, cf6, cf7
		' Pgm ctl processing
		ctl% = ctl% + 1
		'Mimick F1 if enter is pressed on a blank line
		IF updwn% = 13 AND VAL(in$(l%, 1)) = 0 AND VAL(in$(l%, 4)) = 0 THEN
			ctl% = ctl% - 1'This stays there
		END IF
		IF updwn% = 60 THEN ctl% = ctl% - 2     'F2 - Back one
		IF updwn% = 72 THEN ctl% = -1           'Up Arrow
		IF updwn% = 80 THEN ctl% = -1           'Down Arrow
		IF updwn% = 73 THEN ctl% = -1           'Pg Up
		IF updwn% = 81 THEN ctl% = -1           'Pg Down
		IF updwn% = 60 AND ctl% = 0 THEN ctl% = -1'F2 at first
		IF updwn% = 59 THEN ctl% = -1           'F1 Save
		IF ctl% > maxctl% THEN ctl% = -1        'End of line
		WEND
GOTO x.chglin

'--- Detail entry subroutines
	'-QTY
cf1:
	IF ext.has.changed% THEN
		TaxRate! = GST
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
	END IF
	LOCATE ln%, c%(1)
	in$ = in$(l%, 1)
	old.qty = VAL(in$(l%, 1))

	IF updwn% = 113 THEN 'The last one was scanned, get ready for another
		in$ = "1"
		updwn% = 13
	ELSE
		CALL inpnew(in$, 204!, updwn%, "13,27,59-60,62-65,68,72-73,80-81")
	END IF

	in$ = UCASE$(in$)
	IF updwn% = 27 THEN
		in$(l%, 1) = "0": in$(l%, 2) = "   ": in$(l%, 3) = "": in$(l%, 4) = "": in$(l%, 5) = "": in$(l%, 6) = "0"
		in$(l%, 7) = "0": in$(l%, 8) = "0": in$(l%, 9) = "N/": in$(l%, 10) = "0": in$(l%, 11) = "0": in$(l%, 12) = "N"
		CALL dsplyLine(l%, d.elem%)
		TaxRate! = GST
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
		GOTO cf1
	END IF

	'IF updwn% = 63 THEN '-Instant price browse
	'END IF
	IF updwn% = 64 THEN
		PCOPY 0, 1
		CALL accbrowseo(rec%)
		PCOPY 1, 0
		GOTO cf1
	END IF
	IF updwn% = 65 THEN ' overtype price
		CALL sndmsg("F5-To reinstate price to original")
		LOCATE ln%, 56
		a$ = (in$(l%, 6))
		CALL inpnew(a$, 5.2, updwn%, "13,59,63")
		CALL sndmsg("")
		IF updwn% = 13 THEN
			in$(l%, 6) = STR$(VAL(a$))
			in$(l%, 15) = "Y"
		END IF
		IF updwn% = 63 THEN
			'get original price
			IF VAL(in$(l%, 4)) > 0 AND VAL(in$(l%, 4)) < maxacc% THEN
				GET #3, VAL(in$(l%, 4)), acstk
				CALL rightprice(oprice!)
				in$(l%, 6) = STR$(oprice!)
				in$(l%, 15) = SPACE$(9)
			END IF
		END IF

		LOCATE ln%, 56: PRINT USING "####.##"; in$(l%, 6)
		CALL dsplyLine(l%, d.elem%)
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
	END IF
	IF updwn% = 68 THEN
		'CALL get.order.vs(hord%, updwn%)
	END IF

	'-
	IF VAL(in$) > 9300 THEN
		in$ = "1"
		SOUND 15000, 10
		SOUND 500, 3
	END IF


	in$(l%, 1) = in$
	newdata$ = "Y": CALL cf8(l%, ctl%, newdata$)
	newsearch$ = "Y"

	IF old.qty <> VAL(in$) THEN
		CALL dsplyLine(l%, d.elem%)
		TaxRate! = GST 'Use the constant
		CALL add.up.order(tot.ltact!, tot.ord!, tot.ext!)
	END IF

RETURN
	'-SIZE
cf2: LOCATE ln%, c%(2)
	learn% = -1
	IF VAL(in$(l%, 4)) = 0 THEN check$ = "13,59,60,62,27" ELSE check$ = ""
	'CALL inpnew(in$(l%, 2), 103!, updwn%, check$)
	IF check$ > "" THEN
	btm$ = ""
	FOR i% = 1 TO 79: btm$ = btm$ + CHR$(SCREEN(25, i%)): NEXT
	btma$ = "F1-Save/Print.   Enter Size or Scan Barcode or F4-Remove Barcode Assigment"

cf2UL:
		COLOR 8, 3: LOCATE 25, 1: PRINT btma$;
		LOCATE ln%, c%(2)
		CALL inpnew(in$(l%, 2), 113!, updwn%, check$)
		IF updwn% = 62 THEN
			learn% = 0
			CALL sndmsg("Remove Barcode assignment.")
			GOTO cf2UL
		END IF

		CALL sndmsg("")
		COLOR 8, 3: LOCATE 25, 1: PRINT btm$;
	END IF

	IF updwn% = 27 THEN
		in$(l%, 1) = "0": in$(l%, 2) = "   ": in$(l%, 3) = "": in$(l%, 4) = "": in$(l%, 5) = "": in$(l%, 6) = "0"
		in$(l%, 7) = "0": in$(l%, 8) = "0": in$(l%, 9) = "N/": in$(l%, 10) = "0": in$(l%, 11) = "0": in$(l%, 12) = "N"
		CALL dsplyLine(l%, d.elem%)
		updwn% = 60
	END IF

	IF VAL(in$(l%, 2)) > 9300 THEN
		ean$ = in$(l%, 2)
		CALL ean13(in$(l%, 2), ind%)
		IF ind% <= 0 THEN
			in$(l%, 2) = ""
			COLOR 13, 0
			LOCATE 3, 35: PRINT USING "\                \"; ean$
			COLOR 2, 0
			CALL sndmsg("Barcode not found. Enter size & Search key to assign.")
			SOUND 1500, 10
			SOUND 300, 10
			GOTO cf2
		END IF

		'>F4 from then ean prompt removes it.
		IF NOT learn% THEN
			IF ind% > 0 AND ind% < maxacc% THEN
				GET #3, ind%, acstk
				acstk.ean13 = 0
				PUT #3, ind%, acstk
				CALL sndmsg("Barcode assignment removed.")
			END IF
			updwn% = 13
			in$(l%, 2) = ""
			GOTO cf2
		END IF


		ditem% = ind%
		price! = -1
		ordqty% = VAL(in$(l%, 1))
		invqty% = 0
		m% = l%
		CALL loadLine(m%, 0, ditem%, ordqty%, invqty%, price!, gate!)
		CALL dsplyLine(l%, d.elem%)
		updwn% = 113 'Says EAN assigned
	END IF


	in$(l%, 2) = UCASE$(in$(l%, 2))
	a$ = "   ": LSET a$ = in$(l%, 2): in$(l%, 2) = a$

	bysearch$ = "N"
	IF in$(l%, 2) <> "   " AND VAL(in$(l%, 4)) = 0 THEN bysearch$ = "Y"

RETURN
	'-UNITS
cf3: LOCATE ln%, c%(3)
	CALL inpnew(in$(l%, 3), 102!, updwn%, "")
RETURN
	'-STOCK NUMBER
cf4: LOCATE ln%, c%(4)
	oldrec% = VAL(in$(l%, 4))
	IF bysearch$ = "Y" OR VAL(in$(l%, 4)) <> 0 THEN
		inpctl$ = ""
	ELSE
		inpctl$ = "13,59,60,62,64"
	END IF

	IF frombrowse% THEN in$(l%, 4) = STR$(rec%): frombrowse% = 0
	CALL inpnew(in$(l%, 4), 4!, updwn%, inpctl$)
		IF updwn% = 64 THEN
			PCOPY 0, 1
			CALL accbrowseo(rec%)
			PCOPY 1, 0
			IF rec% < 1 OR rec% > maxacc% THEN rec% = 1
			in$(l%, 4) = "": updwn% = 0: frombrowse% = -1
			GOTO cf4
		END IF

	ditem% = VAL(in$(l%, 4))
	IF ditem% < 1 OR ditem% > maxacc% THEN ditem% = 0
	IF ditem% <> oldrec% OR ditem% = 0 THEN
		price! = -1
		ordqty% = VAL(in$(l%, 1))
		invqty% = 0
		m% = l%
		CALL loadLine(m%, 0, ditem%, ordqty%, invqty%, price!, gate!)
		CALL dsplyLine(l%, d.elem%)
	END IF
RETURN
	'-DESCRIPTION
cf5: LOCATE ln%, c%(5)
	IF bysearch$ = "N" THEN
		CALL inpnew(in$(l%, 5), 136!, updwn%, "")

	ELSE '/// Search away ///
		IF newsearch$ = "Y" THEN
			in$ = "": IF frombrowse% = -1 THEN in$ = acstk.search$: frombrowse% = 0
			CALL inpnew(in$, 118!, updwn%, "13,59,60,64,62")
			IF LEN(in$) > 0 THEN
					in$ = UCASE$(in$)
					search.key$ = in$
					COLOR 13, 0
					LOCATE 3, 35: PRINT USING "\                \"; search.key$
					COLOR 2, 0
			END IF
			IF updwn% = 59 THEN GOTO xcf5
			IF updwn% = 60 THEN GOTO xcf5
			IF updwn% = 64 THEN
					PCOPY 0, 1
					CALL accbrowseo(rec%)
					PCOPY 1, 0
					IF rec% < 1 OR rec% > maxacc% THEN rec% = 1
					GET #3, rec%, acstk
					frombrowse% = -1
					GOTO cf5
			END IF

			search.dir$ = "N"
			LSET qk$ = search.key$
			CALL index("CHAIN", ind%, qk$, 7, keyl%)
			IF ind% < 0 AND qk$ < search.key$ THEN CALL index("READ ", ind%, qk$, 7, keyl%)
			IF ind% < 0 THEN ind% = 0 - ind%
			END IF
		test = VAL(in$(l%, 2))
		ii% = 0
		FOR i% = LEN(in$(l%, 2)) TO 1 STEP -1
			IF MID$(in$(l%, 2), i%, 1) = " " THEN ii% = ii% + 1
			IF MID$(in$(l%, 2), i%, 1) <> " " THEN EXIT FOR
			NEXT
		testa$ = STRING$(ii%, " ") + in$(l%, 2)
		testa$ = LEFT$(testa$, 3)

		test1$ = MID$(qk$, 1, 1)
		test1$ = MID$(qk$, 1, 1)
		count% = 0
anext3:
		IF MID$(qk$, 16, 3) = testa$ THEN
			test1$ = MID$(qk$, 1, 1)
			IF ind% > 0 AND ind% < maxacc% THEN GET #3, ind%, acstk
			LOCATE ln%, c%(4): PRINT USING "####"; ind%
			LOCATE ln%, c%(5): PRINT acstk.Desc1$; " "; acstk.desc2$
			LOCATE ln%, c%(5)
			IF newsearch$ = "Y" THEN search.dir$ = CHR$(13)
			'// If its the last line leave it in Next/Previous mode on same line //
			IF newsearch$ = "Y" AND l% = maxlines% THEN search.dir$ = ""
			IF newsearch$ = "N" THEN SOUND 1000, 5: search.dir$ = CHR$(13)
			newsearch$ = "N"
			search.dir$ = UCASE$(search.dir$)
			'CALL INPNEW(  0.0,UPDWN%,"13,p,n")
			END IF
		'// If the first letter in the index changes cancel then search //
		IF test1$ <> MID$(qk$, 1, 1) THEN 'Size not found. Go back to size .
				updwn% = 60
				GOTO xcf5
				END IF
		IF search.dir$ = "N" THEN
				CALL index("READ ", ind%, qk$, 7, keyl%)
				count% = count% + 1: IF count% < 3000 THEN GOTO anext3
				END IF
		IF search.dir$ = "P" THEN
				CALL index("READP", ind%, qk$, 7, keyl%)
				GOTO anext3
				END IF
		IF search.dir$ <> CHR$(13) THEN GOTO cf5'AGAIN
		'// Load details of new record into array ///
			ditem% = ind%
			price! = -1
			ordqty% = VAL(in$(l%, 1))
			invqty% = 0
			m% = l%
			CALL loadLine(m%, 0, ditem%, ordqty%, invqty%, price!, gate!)
			CALL dsplyLine(l%, d.elem%)
			'- Place the result of the search in the search key
			search.key$ = acstk.search$
			COLOR 13, 0
			LOCATE 3, 35: PRINT USING "\                \"; search.key$
			COLOR 2, 0

			'>-Learn
			IF ean$ > "" AND acstk.ean13 <> VAL(ean$) THEN
				IF ditem% > 0 AND ditem% < maxacc% THEN
					GET #3, ditem%, acstk
					IF acstk.ean13 > 0 THEN
						CALL sndmsg("Stock already has a barcode. Reassign?..> ")
						SOUND 1000, 1
						LOCATE 24, 45
						a$ = "N"
						CALL inpnew(a$, 101!, updwn%, "59,13")
						IF updwn% = 59 THEN a$ = "N"
						IF UCASE$(a$) = "Y" THEN
							acstk.ean13 = 0
						ELSE
							CALL sndmsg("")
						END IF
					END IF

					IF acstk.ean13 = 0 THEN
						acstk.ean13 = VAL(ean$)
						PUT #3, ditem%, acstk
						CALL sndmsg("Barcode" + STR$(acstk.ean13) + " assigned.")
					END IF

				END IF
			END IF
			ean$ = ""
		END IF

xcf5:
RETURN
	'-PRICE
cf6: LOCATE ln%, c%(6)
				'CALL inpnew(in$(l%, 6), 5.2!, updwn%, "")
RETURN
	'-TAX
cf7:
RETURN
x.chglin:
	
END SUB

SUB cvt.tnt (tnt$, tnt%, tntf$)
	tnt$ = UCASE$(tnt$)

	tnt$ = "    " + tnt$: tnt$ = RIGHT$(tnt$, 4)
	digit% = 4
	SELECT CASE MID$(tnt$, digit%, 1)
	CASE "A" TO "Z"
	'CASE "T"
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

SUB delOrder (hord%, n%, clr%, autodel$, thissup$, norders%)
delOrder:
	IF autodel$ <> "Y" THEN
		COLOR 0, 7: LOCATE 25, 1: PRINT SPACE$(80);
		COLOR 0, 7: LOCATE 25, 20: PRINT "F1 - Exit.        F10 - Continue.";
		LOCATE 1, 1
		CALL inpnew(in$, 0!, updwn%, "59,68")
		IF updwn% = 59 THEN GOTO x.delOrder
		END IF
	autodel$ = "N"

	'-Count the details
	FOR l% = 1 TO maxlines%
		IF VAL(in$(l%, 4)) <> 0 THEN n% = l%
	NEXT
	firstrec% = CVI(ordhed.hrrn$)
	CALL linkedl(rrn%(), 0, firstrec%, hord%, 49)

	'-Delete the HEADER file
	GET #48, hord%, ordhed
	LSET ordhed.hord$ = MKI$(0)
	LSET ordhed.hreford$ = SPACE$(99)
	LSET ordhed.hsup$ = "     "
	LSET ordhed.hrrn$ = MKI$(0)
	LSET ordhed.horgq$ = MKS$(0)
	LSET ordhed.hordq$ = MKS$(0)
	LSET ordhed.hinvq$ = MKS$(0)
	LSET ordhed.hdollar$ = MKS$(0)
	LSET ordhed.hitems$ = MKI$(0)
	LSET ordhed.hnote1$ = SPACE$(99)
	LSET ordhed.hnote2$ = SPACE$(99)
	PUT #48, hord%, ordhed
	hord% = 0

	'If a special item is used (stock # <20) delete it.
	FOR l% = 1 TO maxlines%
		i% = VAL(in$(l%, 4))
		IF i% >= 1 AND i% <= 20 THEN
			GET #3, i%, acstk
			acstk.no = 0
			acstk.Desc1$ = ""
			acstk.desc2$ = ""
			PUT #3, i%, acstk
		END IF

		'-Update the stock file (remove previous)
		sooqty% = VAL(in$(l%, 13))
		svrrn% = VAL(in$(l%, 14))
		IF svrrn% >= 1 AND svrrn% <= maxacc% THEN
			GET #3, svrrn%, acstk
			acstk.soo = acstk.soo - sooqty%
			PUT #3, svrrn%, acstk
		END IF

	NEXT

	clr% = 1
x.delOrder:

END SUB

SUB details (rec&, updwn%, auto%, rview%) STATIC
	first.seq% = 1
	current.lin% = 1
	browse38.result% = 0
	IF auto% THEN skip% = -1: updwn% = 59
details.0:
	CALL setup("ENTER/VIEW FORMULA DETAILS")
	btm$ = " F1-Return F2-Batch# F3-Ins. F4-Del. F5-Stats. F6-Bse. F7-Driers F8-Prt. F10-Chg"
	CALL prtbtm(btm$)
	COLOR 6, 0: LOCATE 3, 2: PRINT "RMat Description                 Qty..                           Cost"
	COLOR 6, 0
	LOCATE 3, 41: PRINT "  %Vol.  %Wt..    Cost.   Kg...   Lt..."
	COLOR 2, 0
	COLOR 7, 0: LOCATE 2, 2: PRINT "µ  Æ": COLOR 2, 0
	COLOR 2, 0: LOCATE 2, 3: PRINT "01"
	LOCATE 23, 2: PRINT STRING$(78, "Ä");
	LOCATE 23, 6: PRINT "Á"

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

	startrec& = rec& * maxformseq% - maxformseq% + 1
	insert.mode% = 0

	DO
		IF lin% < 1 THEN lin% = 1
		IF lin% > 19 THEN lin% = 19
		a$ = STR$(rmno%(lin%))

		IF skip% THEN
			skip% = 0
			ELSE
			IF insert.mode% THEN CALL sndmsg(""): insert.mode% = 0
			LOCATE lin% + 3, 1
			a$ = ">"
			SELECT CASE rview%
				CASE 0:  CALL inpnew(a$, 1!, updwn%, "13,59-65,66-68,72,80,73,81")
				CASE -1: CALL inpnew(a$, 1!, updwn%, "59,63,72,80,73,81")
			END SELECT
			LOCATE lin% + 3, 1: COLOR 7: PRINT "º": COLOR 2, 0
			current.lin% = lin%
		END IF

		IF height.in.tank.called% = -1 THEN
			 CALL sndmsg("")
			 height.in.tank.called% = 0
			 END IF

		IF auto% THEN
			updwn% = 13
			GOTO details.55
		END IF
		SELECT CASE updwn%
		CASE 13
				IF lin% > 1 THEN
					first.seq% = first.seq% + lin% - 1
					IF first.seq% < 1 THEN first.seq% = 1
					FOR lin% = 1 TO 19
						CALL dsply.line(rec&, lin%, first.seq%, 1)
						NEXT
					LOCATE 2, 3: PRINT USING "##"; first.seq%
					lin% = 1
					CALL dsply.line(rec&, lin%, first.seq%, 2)
					END IF

		CASE 59: EXIT DO
		CASE 60: 'Add material Batch Number
				cost.or.ltrs$ = "Batch#"
				COLOR 6
				LOCATE 3, 41: PRINT "                    Batch Number       "
				COLOR 2
				 CALL dsply.line(rec&, lin%, first.seq%, 2)

				seq% = first.seq% + lin% - 1
				
				LOCATE lin% + 3, 60
				rmbno$ = rmbno$(seq%)
				
				CALL inpnew(rmbno$, 115!, updwn%, "13,59-60")

				rmbno$(seq%) = rmbno$
				
				CALL dsply.line(rec&, lin%, first.seq%, 3)
				

		CASE 61: 'Insert a line
				IF lin% < 19 THEN lin% = lin% + 1: current.lin% = lin%
				IF rmno%(maxformseq%) <> 0 THEN BEEP: GOTO details.55
				seq% = first.seq% + lin% - 1
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
					rm.tankltmm!(i%) = rm.tankltmm!(i% - 1)
					NEXT

				rmno%(seq%) = 0: qty!(seq%) = 0: cmtno%(seq%) = 0: cmtqty!(seq%) = 0
				desc$(seq%) = "": vpct!(seq%) = 0: wpct!(seq%) = 0: ltr!(seq%) = 0: kg!(seq%) = 0: ext!(seq%) = 0
				Wsol!(seq%) = 0: Wsol!(seq%) = 0
				rm.sg!(seq%) = 0: rm.wtsolid!(seq%) = 0: rm.solidsg!(seq%) = 0: rm.useunit$(seq%) = "": rm.cond$(seq%) = "": rm.tanksize!(seq%) = 0: rm.tankltmm!(seq%) = 0

				skip% = -1: updwn% = 68: insert.mode% = -1
				CALL sndmsg("Enter 'L' to insert a blank line.")

				FOR lin% = 1 TO 19
					CALL dsply.line(rec&, lin%, first.seq%, 1)
					NEXT
				lin% = current.lin%


		CASE 62: 'Delete a line
				seq% = first.seq% + lin% - 1
				FOR i% = seq% TO maxformseq% - 1
					rmno%(i%) = rmno%(i% + 1)
					qty!(i%) = qty!(i% + 1)
					cmtno%(i%) = cmtno%(i% + 1)
					cmtqty!(i%) = cmtqty!(i% + 1)

					desc$(i%) = desc$(i% + 1)
					vpct!(i%) = vpct!(i% + 1)
					wpct!(i%) = wpct!(i% + 1)
					ltr!(i%) = ltr!(i% + 1)
					kg!(i%) = kg!(i% + 1)
					ext!(i%) = ext!(i% + 1)

					Wsol!(i%) = Wsol!(i% + 1)
					Wsol!(i%) = Wsol!(i% + 1)
					rm.sg!(i%) = rm.sg!(i% + 1)
					rm.wtsolid!(i%) = rm.wtsolid!(i% + 1)
					rm.solidsg!(i%) = rm.solidsg!(i% + 1)
					rm.useunit$(i%) = rm.useunit$(i% + 1)
					rm.cond$(i%) = rm.cond$(i% + 1)
					rm.tanksize!(i%) = rm.tanksize!(i% + 1)
					rm.tankltmm!(i%) = rm.tankltmm!(i% + 1)
					NEXT

				rmno%(maxformseq%) = 0: qty!(maxformseq%) = 0: cmtno%(maxformseq%) = 0: cmtqty!(maxformseq%) = 0
				desc$(maxformseq%) = "": vpct!(maxformseq%) = 0: wpct!(maxformseq%) = 0: ltr!(maxformseq%) = 0: kg!(maxformseq%) = 0: ext!(maxformseq%) = 0
				Wsol!(maxformseq%) = 0: Wsol!(maxformseq%) = 0
				rm.sg!(maxformseq%) = 0: rm.wtsolid!(maxformseq%) = 0: rm.solidsg!(maxformseq%) = 0: rm.useunit$(maxformseq%) = "": rm.cond$(maxformseq%) = "": rm.tanksize!(msformseq%) = 0: rm.tankltmm!(maxformseq%) = 0

				FOR lin% = 1 TO 19
					CALL dsply.line(rec&, lin%, first.seq%, 1)
					NEXT
				lin% = current.lin%
				CALL dsply.line(rec&, lin%, first.seq%, 3)

		 CASE 63:
				 SELECT CASE cost.or.ltrs$
				 CASE "Litres"
					cost.or.ltrs$ = "Cost  "
					COLOR 6
					LOCATE 3, 41: PRINT "  %Vol.  %Wt..    Cost.   Kg...   Lt..."
					COLOR 2
				 CASE "Cost  "
					cost.or.ltrs$ = "Batch#"
					COLOR 6
					LOCATE 3, 41: PRINT "                    Batch Number       "
					COLOR 2
				 CASE "Batch#"
					cost.or.ltrs$ = "Litres"
					COLOR 6
					LOCATE 3, 41: PRINT "  %Vol.  %Wt..    Cost.   Kg...   Lt..."
					COLOR 2
				 CASE ELSE: cost.or.ltrs$ = "Litres"
				 END SELECT

				 CALL dsply.line(rec&, lin%, first.seq%, 2)

		CASE 64: CALL browse38(browse38.result%, updwn%): updwn% = -1: EXIT DO
		CASE 65: seq% = first.seq% + lin% - 1: startsearch% = seq%
				 startsearch% = 1
				 CALL resins(startsearch%, seq%, updwn%)
				 COLOR 0, 3: LOCATE 25, 1: PRINT btm$; : COLOR 2, 0
				 IF updwn% = 60 THEN
					FOR lin% = 1 TO 19
						CALL dsply.line(rec&, lin%, first.seq%, 1)
						NEXT
					lin% = current.lin%
					END IF

		CASE 66:
					CALL printit

		CASE 67:    CALL browse30(browse30.result%, updwn%): updwn% = -1: EXIT DO
		CASE 68
				cost.or.ltrs$ = "Litres"
				seq% = first.seq% + lin% - 1
				'>> Update raw material
				LOCATE lin% + 3, 2
				tst% = rmno%(seq%)
				rmno$ = STR$(rmno%(seq%))
				CALL inpnew(rmno$, 204!, updwn%, "13,59-60,72,80")

				rmno%(seq%) = VAL(rmno$)
				IF rmno%(seq%) = 0 THEN
					qty!(seq%) = 0
					cmtno%(seq%) = 0
					END IF
				IF tst% <> rmno%(seq%) THEN
				CALL dsply.line(rec&, lin%, first.seq%, 3)
				END IF

				IF insert.mode% AND rmno%(seq%) = 0 THEN skip% = -1: updwn% = 62
				IF insert.mode% AND rmno%(seq%) = 0 AND UCASE$(rmno$) = "L" THEN skip% = -1: updwn% = 61
				IF rmno%(seq%) = 0 THEN GOTO details.55
details.qty:
				'>>- Update qty
				LOCATE lin% + 3, 32
				tst! = qty!(seq%)
				qty$ = STR$(qty!(seq%))
				'IF VAL(qty$) < 1 AND rm.useunit$(seq%) = "EA" THEN qty$ = "1"
				IF VAL(qty$) < 1 AND rm.useunit$(seq%) = "EQ" THEN qty$ = ""

																CALL inpnew(qty$, 207.2, updwn%, "13,59-60,72,80")
					'IF VAL(qty$) < 1 AND rm.useunit$(seq%) = "EA" THEN qty$ = "1"
					IF VAL(qty$) < 2 AND rm.useunit$(seq%) = "EQ" THEN qty$ = ""
					qty!(seq%) = VAL(qty$)
					'>> If `k' entered - treat as KG and convert to LT if nescessary.
					IF UCASE$(LEFT$(qty$, 1)) = "K" THEN
						qty$ = RIGHT$(qty$, LEN(qty$) - 1)
						div! = rm.sg!(seq%): IF div! = 0 THEN div! = 1
						SELECT CASE msrmat.useunit$
						CASE "LT": qty!(seq%) = VAL(qty$) / div!
						CASE "ML": qty!(seq%) = VAL(qty$) / div! / 1000
						CASE ELSE: qty!(seq%) = VAL(qty$)
						END SELECT
						END IF
				CALL round(qty!(seq%), 2.5)
				IF tst! <> qty!(seq%) THEN
				CALL dsply.line(rec&, lin%, first.seq%, 3)
				END IF
				IF updwn% = 59 THEN GOTO details.55:
				IF updwn% = 60 THEN GOTO details.55:

				'>>- Add a comment
details.cmt:    LOCATE lin% + 3, 43: PRINT "    "
				IF cmtno%(seq%) = 0 THEN LOCATE lin% + 3, 46: PRINT "<- Enter a comment no."
				LOCATE lin% + 3, 45
				cmt$ = STR$(cmtno%(seq%))
				CALL inpnew(cmt$, 2!, updwn%, "13,59-60,64,67,72,80")
				cmtno%(seq%) = VAL(cmt$)
				CALL dsply.line(rec&, lin%, first.seq%, 1)
				IF updwn% = 59 THEN GOTO details.55:
				IF updwn% = 60 THEN GOTO details.qty:
				IF updwn% = 64 OR updwn% = 67 THEN
					PCOPY 0, 1
					CALL browse30(browse30.result%, updwn%): updwn% = -1
					PCOPY 1, 0
					GOTO details.cmt
					END IF

				'>>- Add a comment qty
				SELECT CASE cmtno%(seq%)
				CASE 98
					seq% = first.seq% + lin% - 1
					Ltrs.in! = ltr!(seq%)
					CALL height.in.tank(updwn%, seq%, Ltrs.in!, Height.from.btm!, Height.from.top!)
					height.in.tank.called% = -1
					IF updwn% = 13 THEN cmtqty!(seq%) = Height.from.btm!
					CALL dsply.line(rec&, lin%, first.seq%, 1)
				CASE 99
					run.ltr! = 0
					FOR i% = 1 TO seq%
						work! = ltr!(i%)
						IF work! = -1 THEN run.ltr! = 0
						IF work! < .1 THEN work! = 0
						run.ltr! = run.ltr! + work!
						IF run.ltr! < .1 THEN run.ltr! = 0
						NEXT
					Ltrs.in! = run.ltr!: CALL round(Ltrs.in!, 2.5)

					seq% = first.seq% + lin% - 1
					CALL height.in.tank(updwn%, seq%, Ltrs.in!, Height.from.btm!, Height.from.top!)
					height.in.tank.called% = -1
					IF updwn% = 13 THEN cmtqty!(seq%) = Height.from.top!
					CALL dsply.line(rec&, lin%, first.seq%, 1)
				CASE ELSE
					LOCATE lin% + 3, 43: PRINT "    "
					LOCATE lin% + 3, 43
					cmtqty$ = STR$(cmtqty!(seq%))
					CALL inpnew(cmtqty$, 4!, updwn%, "13,59-60,72,80")
					cmtqty!(seq%) = VAL(cmtqty$)
					CALL dsply.line(rec&, lin%, first.seq%, 1)
					IF updwn% = 59 THEN GOTO details.55:
					IF updwn% = 60 THEN GOTO details.55:
				END SELECT
				IF insert.mode% THEN skip% = -1: updwn% = 61
		'    lin% = lin% + 1

		CASE 72: 'Up arrow
				IF first.seq% > 1 OR lin% > 1 THEN lin% = lin% - 1
				IF lin% < 1 THEN
					first.seq% = first.seq% - 1
					IF first.seq% < 1 THEN first.seq% = 1
					FOR lin% = 1 TO 19
						CALL dsply.line(rec&, lin%, first.seq%, 1)
						NEXT
					LOCATE 2, 3: PRINT USING "##"; first.seq%
					lin% = current.lin%
					CALL dsply.line(rec&, lin%, first.seq%, 2)
					END IF

		CASE 73: 'Page up
				first.seq% = first.seq% - 19 + 1
				first.seq% = first.seq% - 1
				IF first.seq% < 1 THEN first.seq% = 1
				FOR lin% = 1 TO 19
					CALL dsply.line(rec&, lin%, first.seq%, 1)
					NEXT
				LOCATE 2, 3: PRINT USING "##"; first.seq%
				lin% = current.lin%
				CALL dsply.line(rec&, lin%, first.seq%, 2)

		CASE 80: 'Down arrow
				IF first.seq% + lin% - 1 < maxformseq% THEN lin% = lin% + 1
				IF lin% > 19 THEN
					first.seq% = first.seq% + 1
					IF first.seq% > maxformseq% - 19 + 1 THEN first.seq% = maxformseq% - 19 + 1
					FOR lin% = 1 TO 19
						CALL dsply.line(rec&, lin%, first.seq%, 1)
						NEXT
					LOCATE 2, 3: PRINT USING "##"; first.seq%
					lin% = current.lin%
					CALL dsply.line(rec&, lin%, first.seq%, 2)
					END IF


		CASE 81: 'Page down
				first.seq% = first.seq% + 19 - 1
				first.seq% = first.seq% + 1
				IF first.seq% > maxformseq% - 19 + 1 THEN first.seq% = maxformseq% - 19 + 1
				FOR lin% = 1 TO 19
					CALL dsply.line(rec&, lin%, first.seq%, 1)
					NEXT
				LOCATE 2, 3: PRINT USING "##"; first.seq%
				lin% = current.lin%
				CALL dsply.line(rec&, lin%, first.seq%, 2)

		CASE ELSE: lin% = lin% + 1
		END SELECT
details.55:

		'>- Recalc height in tank for every line
		heightchanged% = 0' Flag
		FOR i% = 1 TO 38
			seq% = i%
			IF cmtno%(seq%) = 99 THEN
				run.ltr! = 0
				FOR ii% = 1 TO seq%
					work! = ltr!(ii%)
					IF work! = -1 THEN run.ltr! = 0
					IF work! < .1 THEN work! = 0
					run.ltr! = run.ltr! + work!
					IF run.ltr! < .1 THEN run.ltr! = 0
					NEXT
				Ltrs.in! = run.ltr!: CALL round(Ltrs.in!, 2.5)
				CALL height.in.tank(updwn%, seq%, Ltrs.in!, Height.from.btm!, Height.from.top!)
				IF updwn% = 13 AND cmtqty!(seq%) <> Height.from.top! THEN heightchanged% = -1
				IF updwn% = 13 THEN cmtqty!(seq%) = Height.from.top!
				END IF

			IF cmtno%(seq%) = 98 THEN
				Ltrs.in! = ltr!(seq%)'Calc height on side
				CALL height.in.tank(updwn%, seq%, Ltrs.in!, Height.from.btm!, Height.from.top!)
				IF updwn% = 13 AND cmtqty!(seq%) <> Height.from.btm! THEN heightchanged% = -1
				IF updwn% = 13 THEN cmtqty!(seq%) = Height.from.btm!
				END IF

			NEXT

		IF heightchanged% THEN
		IF first.seq% < 1 THEN first.seq% = 1
		linsav% = lin%
		FOR lin% = 1 TO 19
			CALL dsply.line(rec&, lin%, first.seq%, 1)
			NEXT
		lin% = linsav%
		END IF

		IF auto% THEN EXIT DO
		LOOP

		IF updwn% = -1 THEN GOTO details.0


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
		rm.sg!(seq%) = msrmat.sg!
		IF msrmat.useunit$ = "EQ" THEN rm.sg!(seq%) = 0
		IF msrmat.useunit$ = "EA" THEN rm.sg!(seq%) = 0
		rm.wtsolid!(seq%) = msrmat.Wtsolid!
		rm.solidsg!(seq%) = msrmat.solidsg!
		rm.useunit$(seq%) = msrmat.useunit$
		rm.cond$(seq%) = msrmat.cond$
		IF msrmat.PurUnit$ = "TK" THEN
		rm.tanksize!(seq%) = msrmat.Wtsolid!
		rm.tankltmm!(seq%) = msrmat.solidsg!
		ELSE
		rm.tanksize!(seq%) = 0
		END IF
		END IF

	IF cmtno%(seq%) > 0 AND cmtno%(seq%) <= maxcmt% THEN
		GET #30, cmtno%(seq%), mscomt
		END IF

	IF rmno%(seq%) = 0 THEN qty!(seq%) = 0
	IF rmno%(seq%) > 0 AND qty!(seq%) < 1 AND rm.useunit$(seq%) = "EA" THEN qty!(seq%) = 1
	IF qty!(seq%) < 0 THEN qty!(seq%) = 0
	IF qty!(seq%) > 9999 THEN qty!(seq%) = 9999

	work! = qty!(seq%)
	IF work! = 0 AND msrmat.useunit$ = "EQ" AND rmno%(seq%) > 0 THEN work! = 1
	ext! = work! * msrmat.usecost!

	IF ext! > 9999 THEN ext! = 9999
	IF ext! < -999 THEN ext! = -999

	 ltr! = qty!(seq%) * rm.sg!(seq%)
	 kg! = 0
	 sg! = rm.sg!(seq%): IF sg! = 0 THEN sg! = .0000001
	 IF msrmat.useunit$ = "KG" THEN ltr! = qty!(seq%) / sg!: kg! = qty!(seq%)
	 IF msrmat.useunit$ = "GM" THEN ltr! = qty!(seq%) / sg! / 1000: kg! = qty!(seq%) / 1000
	 IF msrmat.useunit$ = "LT" THEN ltr! = qty!(seq%): kg! = qty!(seq%) * sg!
	 IF msrmat.useunit$ = "ML" THEN ltr! = qty!(seq%) / 1000: kg! = qty!(seq%) * sg! / 1000
	 IF msrmat.useunit$ = "OZ" THEN ltr! = qty!(seq%) / 28.413: kg! = qty!(seq%) / 28.413 * sg! / 1000
	 IF msrmat.useunit$ = "TK" THEN ltr! = -1: kg! = 0
	 IF msrmat.useunit$ = "EQ" THEN ltr! = -1: kg! = 0

	 'prtbuf$ = "1234³6789 123456789 123456789 123456789 123456789 123456789 123456789 12345678"
	 'prtbuf$ = "####³\                       \  ####\\   #### \                    \  $$###.##"
	prtbuf$ = "    ³                                                                "
	IF rmno%(seq%) > 0 THEN
	MID$(prtbuf$, 1, 4) = format$(CSNG(rmno%(seq%)), "####")
	MID$(prtbuf$, 6, 26) = msrmat.Desc1$
	IF qty!(seq%) > 0 THEN
		MID$(prtbuf$, 33, 6) = format$(qty!(seq%), "###.##")
		MID$(prtbuf$, 39, 2) = LCASE$(msrmat.useunit$)
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
	CALL round(vpct!(i%), 2.5)
	CALL round(wpct!(i%), 2.5)

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
		CASE "Batch#"
			LOCATE i% + 3, 1 + 42: PRINT USING "\                \\             \     "; desc$(seq%); rmbno$(seq%)

		CASE ELSE: LOCATE i% + 3, 71: PRINT "         "; " "
		END SELECT

		END IF

		NEXT

x.dsply.line:
END SUB

SUB dsplyLine (l%, d.elem%) STATIC
		ln% = (l% - d.elem%) MOD 15 + 1: ln% = ln% + 4'+4 Lines from the top of the screen
		COLOR 2, 0
		qty% = VAL(in$(l%, 1))
		IF qty% < 1 OR qty% > 9999 THEN
			LOCATE ln%, 2
			PRINT "    ³     ³    ³                                    ³       ³       ³         "
		ELSE
			qty% = VAL(in$(l%, 1))
			LSET acstk.size$ = in$(l%, 2)
			LSET acstk.unit$ = in$(l%, 3)
			ano% = VAL(in$(l%, 4))
			LSET acstk.Desc1$ = in$(l%, 5)
			LSET acstk.desc2$ = MID$(in$(l%, 5), LEN(acstk.Desc1$) + 2, 10)
			newdata$ = "N": CALL cf8(l%, d.elem%, newdata$)
			price! = VAL(in$(l%, 6)) '??
			gate! = VAL(in$(l%, 7)) '??
			SELECT CASE acstk.unit$
				CASE "ML": price! = price! / 1000
				CASE ELSE
			END SELECT

			
			ext! = VAL(in$(l%, 8))

			'- On BO
			IF in$(l%, 12) = "Y" THEN
				COLOR 10
			END IF
			IF MID$(in$(l%, 15), 1, 1) = "Y" THEN
				COLOR 14
			END IF

			'- Condition red
			IF ext! <= .01 AND qty% > 0 AND ano% > 0 THEN
				COLOR 4
				SOUND 250, 10
				cond.red$ = "There are zero values on the invoice"
			ELSE
				cond.red$ = ""
			END IF
			a$ = "³" + acstk.size$ + acstk.unit$ + "³"
			B$ = "³" + acstk.Desc1$ + " " + acstk.desc2$ + "³"
			c$ = "³"
			LOCATE ln%, 2: PRINT USING "####"; qty%
			LOCATE ln%, 6: PRINT a$;
			LOCATE ln%, 13: PRINT USING "####"; ano%
			LOCATE ln%, 17: PRINT B$;
			LOCATE ln%, 55: PRINT USING "####.##"; price!;
			LOCATE ln%, 62: PRINT c$;
			LOCATE ln%, 63: PRINT USING "####.##"; gate!;

			COLOR 2
			LOCATE ln%, 70: PRINT c$;
			LOCATE ln%, 71: PRINT USING "######.##"; ext!
		END IF
END SUB

SUB dsporders (dspstart%, norders%, custin$) STATIC
	IF dspstart% > norders% - 10 THEN dspstart% = norders% - 10
	IF dspstart% < 1 THEN dspstart% = 1

	x% = 2
	y% = 12

	FOR i% = dspstart% TO dspstart% + 32
		IF y% > 22 THEN
			x% = x% + 26
			y% = 12
			END IF
		y% = y% + 1
		LOCATE y%, x%
		IF norders% > 10 THEN
		PRINT "                         ";
		END IF

	IF i% <= norders% THEN
		GET #48, orders%(i%), ordhed
		a$ = "B/o."
		a$ = "Ord."
		IF custin$ = "*" THEN a$ = " <" + ordhed.hsup$ + ">"
		a = CVS(ordhed.horgq$)
		IF discovr! <> 0 THEN a = discovr!
		LOCATE y%, x%
		IF norders% < 10 THEN
		PRINT USING "### \   \ ###### ##### ######$$#######.## \      \  \          \ \        \"; CVI(ordhed.hord$); a$; a; CVS(ordhed.hinvq$); CVS(ordhed.hordq$); CVS(ordhed.hdollar$); FNDYY$(ordhed.hdate$); ordhed.hreford$; ordhed.htaxe$
		ELSE

		PRINT USING "### \   \ \   \ \        \"; CVI(ordhed.hord$); FNDYY$(ordhed.hdate$); ordhed.hsup$; ordhed.hreford$
		END IF

		END IF
		NEXT


END SUB

SUB ean13 (in$, dind%)
	thsEan# = VAL(in$)
	found% = 0

	dind% = 1
	GET #3, dind%, acstk
	DO WHILE NOT EOF(3) AND dind% <= maxacc%
		IF acstk.ean13 = thsEan# THEN
			found% = -1
			EXIT DO
		END IF
		GET #3, , acstk: dind% = dind% + 1
	LOOP

	IF NOT found% THEN
		dind% = 0
	END IF

END SUB

SUB findnext (hord%, norders%, ok%) STATIC
findnext:
	IF norders% > 1001 THEN
		emsg$ = "Their are already EIGHT orders open for this customer."
		END IF
	IF hord% < 1 OR hord% > maxord% THEN hord% = 1
	oldhord% = hord%
	top% = 0
	GET #48, hord%, ordhed
	DO WHILE CVI(ordhed.hord$) = hord% AND emsg$ = ""
		IF top% AND hord% = oldhord% THEN emsg$ = "No unused orders could be found. Delete old orders before continuing.": EXIT DO
		IF hord% >= maxord% THEN hord% = 0: top% = -1
		hord% = hord% + 1
		GET #48, hord%, ordhed
		LOOP
	IF emsg$ = "" THEN
		'- Grab the record first up.
		LOCK #48, hord%
		GET #48, hord%, ordhed
		IF CVI(ordhed.hord$) = hord% THEN
			UNLOCK #48, hord%
			GOTO x.findnext
			END IF
		LSET ordhed.hord$ = MKI$(hord%)
		PUT #48, hord%, ordhed
		UNLOCK #48, hord%

		LSET ordhed.hdate$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
		LSET ordhed.htaxe$ = CUS.taxe$
		LSET ordhed.hreford$ = SPACE$(99)
		LSET ordhed.hsup$ = "     "
		LSET ordhed.hrrn$ = MKI$(0)
		LSET ordhed.horgq$ = MKS$(0)
		LSET ordhed.hordq$ = MKS$(0)
		LSET ordhed.hinvq$ = MKS$(0)
		LSET ordhed.hdollar$ = MKS$(0)
		LSET ordhed.hitems$ = MKI$(0)
		LSET ordhed.hitems$ = MKI$(0)
		LSET ordhed.linvnum$ = SPACE$(99)
		PUT #48, hord%, ordhed

		'- Clear out the detail arrays
		'- Set order/pickslip mode
		mode$ = "ord"
		norders% = norders% + 1
		orders%(norders%) = hord%
		PUT #48, hord%, ordhed
		END IF

x.findnext:
	IF updwn% = 59 THEN
		LSET ordhed.hord$ = MKI$(0)
		PUT #48, hord%, ordhed
		END IF

END SUB

SUB findorders (thissup$, norders%, hord%)
	FOR i% = 1 TO 1001: orders%(i%) = 0: NEXT
	norders% = 0
	hord% = 1
	GET #48, hord%, ordhed
	DO WHILE NOT EOF(48)
		IF thissup$ = "ZZZZZ" THEN
			skey$ = "     ": LSET skey$ = ordhed.hsup$
			keyin$ = skey$: chi% = 23
			CALL searchindex(keyin$, chi%, found%)
			IF NOT found% THEN ordhed.hsup$ = thissup$
			END IF
		IF thissup$ = "*    " AND ordhed.hsup$ > "      " THEN
			ordhed.hsup$ = thissup$
			END IF
		IF CVI(ordhed.hord$) = hord% AND ordhed.hsup$ = thissup$ THEN
			norders% = norders% + 1
			IF norders% < 1001 THEN
				orders%(norders%) = hord%
				END IF
			END IF

		GET #48, , ordhed: hord% = hord% + 1
		IF hord% > 5001 THEN EXIT DO
		LOOP

	hord% = orders%(norders%)
	IF thissup$ = "*    " THEN hord% = 0

END SUB

SUB height.in.tank (updwn%, seq%, Ltrs.in!, Height.from.btm!, Height.from.top!) STATIC
	'$INCLUDE: '\tpmanuf\src\MSTANK.INC'
END SUB

SUB linkedl (rrn%(), n%, firstrec%, ord%, chd%) STATIC
'$INCLUDE: '\tpmanuf\src\linkedl.bi'
END SUB

SUB load.lines (rec%, eyld!) STATIC
	startrec% = rec% * maxformseq% - maxformseq% + 1
	ch.det% = 65
	FOR first.seq% = 1 TO maxformseq%
	drec% = startrec% + first.seq% - 1
		GET #65, drec%, tntdet
	IF tntdet.tnt& <> drec% THEN
		tntdet.tnt& = 0
		tntdet.rmat% = 0
		tntdet.qty! = 0
		tntdet.cmt% = 0
		tntdet.cmtqty! = 0
		PUT #ch.det%, drec%, tntdet
	END IF

	 rmno%(first.seq%) = tntdet.rmat%
	 qty!(first.seq%) = tntdet.qty! * eyld!
	 cmtno%(first.seq%) = tntdet.cmt%
	 cmtqty!(first.seq%) = tntdet.cmtqty!
	 rmbno$(first.seq%) = tntdet.tfiller$

	'>- These are set in DSPLY.LINE
	 desc$(first.seq%) = ""
	 vpct!(first.seq%) = 0
	 wpct!(first.seq%) = 0
	 ltr!(first.seq%) = 0
	 kg!(first.seq%) = 0
	 ext!(first.seq%) = 0

	 NEXT

END SUB

SUB loadLine (m%, il%, ditem%, ordqty%, invqty%, price!, gate!)
loadLine:
		'- lokup the details
		IF ditem% > 0 AND ditem% < maxacc% THEN
			GET #3, ditem%, acstk
			ano% = acstk.no%
		ELSE
			ano% = 0
			price! = 0
			LSET acstk.size$ = in$(m%, 2)
			LSET acstk.unit$ = SPACE$(99)
			LSET acstk.Desc1$ = SPACE$(99)
			LSET acstk.desc2$ = SPACE$(99)
			LSET acstk.taxinc$ = SPACE$(99)
		END IF
	'//// Determine which price to use ////
		'- Add up litres order and actualy on order
		ltact = 0
		size! = VAL(acstk.size$)
		pack% = acstk.pack%
		IF pack% = 0 THEN pack% = 1
		SELECT CASE UCASE$(acstk.unit$)
			CASE "ML":
				ltact = ordqty% * size! / 1000
			CASE "LT":
				ltact = ordqty% * size!
			CASE "LS":
				ltact = ordqty% * size!
			CASE "GM":
				ltact = ordqty% * size! / 1000 / batchsg
			CASE "GS":
				ltact = ordqty% * size! / 1000 / batchsg
			CASE "KG":
				ltact = ordqty% * size! / batchsg
			CASE ELSE: ltact = 0
		END SELECT
			 ltact = ltact * pack%

		in$(m%, 1) = STR$(ordqty%)
		in$(m%, 2) = acstk.size$
		in$(m%, 3) = acstk.unit$
		in$(m%, 4) = STR$(ano%)
		in$(m%, 5) = acstk.Desc1$ + " " + acstk.desc2$
		in$(m%, 6) = STR$(price!)'rmc
		in$(m%, 7) = STR$(gate!)'
		in$(m%, 8) = STR$(ltact)
		newdata$ = "Y": CALL cf8(m%, d.elem%, newdata$)
		in$(m%, 9) = acstk.taxinc$
		in$(m%, 10) = STR$(ordqty%)
		in$(m%, 11) = STR$(invqty%)
		IF orddet.dBo$ < " " OR orddet.dBo$ > "~" THEN orddet.dBo$ = "N" 'jic
		in$(m%, 12) = orddet.dBo$
		IF il% THEN
			in$(m%, 13) = STR$(ordqty%)
			in$(m%, 14) = STR$(ano%)
		END IF
		in$(m%, 15) = otprice$
		in$(m%, 16) = STR$(acstk.pack%)
END SUB

SUB mline (hord%, rview%, thisbatch$)

	c%(1) = 2
	c%(2) = 7
	c%(3) = 10
	c%(4) = 13
	c%(5) = 18
	c%(6) = 56
	c%(7) = 63
	c%(8) = 72

IF rview% THEN
	c$ = ".\batches\B" + LTRIM$(RTRIM$(thisbatch$)) + ".stk"
	OPEN c$ FOR RANDOM SHARED AS #96 LEN = 32
END IF

s.mline:
CLOSE #3
CLOSE #48, #49
OPEN "acstk.acf" FOR RANDOM SHARED AS #3 LEN = 256
OPEN "igahed.acf" FOR RANDOM SHARED AS #48 LEN = 320
OPEN "igadet.acf" FOR RANDOM SHARED AS #49 LEN = 32

	custin$ = "ZSTOA"

getcust:
		custin$ = "ZSTOA"
		GOSUB mline

'--E D I T   S E C T I O N
mline:
GOSUB load.det
aRETURN:
GOSUB detail

exitmenu:
	DO

	SELECT CASE skipexit%
	CASE -1: opt$ = "": updwn% = 60
	CASE ELSE
		CALL box(17, 4, 63, 20, 6, 9, 1)
		COLOR 3, 1
		LOCATE 5, 28: PRINT "  E X I T    M E N U "
		COLOR 6, 1
		LOCATE , 28: PRINT ""
		COLOR 14
		LOCATE , 22: PRINT cond.red$
		COLOR 2
		LOCATE , 28: PRINT "Option...> "
		COLOR 6, 1
		LOCATE , 20: PRINT "F1-Commit. F2-Save & Cont. F3-Hold. F4-Return."
		LOCATE 19, 38: COLOR 2, 0
		CALL inpnew(opt$, 201!, updwn%, "13,59-60,61,62")
	END SELECT
	skipexit% = 0

	opt% = VAL(opt$)

	IF updwn% = 13 AND opt% = 0 THEN updwn% = 62
	IF updwn% = 59 THEN opt% = 3
	IF updwn% = 60 THEN opt% = -1'F2 - Save & Cont
	IF updwn% = 61 THEN opt% = -1'F3 - Save & Hold
	IF updwn% = 62 THEN opt% = -2'F4 - Return

	LOOP UNTIL opt% >= -2 AND opt% <= 3


	sav% = 0
	doc.type$ = "TAX INVOICE"
	formtype$ = "*PRE.PRINTED.1"

	IF opt% = -2 THEN GOTO aRETURN
	IF opt% = -1 THEN mode$ = "ord": sav% = -1
	'IF opt% = 0 THEN mode$ = "ord": sav% = -1
	'IF opt% = 1 THEN mode$ = "nil": sav% = 0
	'IF opt% = 2 THEN mode$ = "ord": sav% = -1
	IF opt% = 3 THEN mode$ = "inv": sav% = -1
	'IF opt% = 4 THEN mode$ = "b/o": sav% = -1

	IF sav% THEN
		totltr! = tot.ltact!
		CALL UpdateOrder(hord%, updwn%)
		IF updwn% = 60 THEN GOTO mline
	END IF

	'/// Print and exit or delete ///

		'- Only open the audit file when needed -<<
		cashonly$ = "M"


		'GOSUB OPEN.AUDIT '#8

		IF mode$ = "inv" THEN CALL prtstk(totltr!)

		CLOSE #8
after.prtinv:


		anyDelDone% = 0


		IF NOT anyDelDone% THEN
		IF mode$ = "inv" THEN
			autodel$ = "Y"
			CALL delOrder(hord%, n%, clr%, autodel$, thissup$, norders%)
			anyDelDone% = -1
			CALL findorders(thissup$, norders%, hord%)
		END IF
		END IF

mlend:
	'- Change F1 to prevent the real mainline ending the program. <<

	updwn% = 13
	clr% = 3
GOTO igacc02.x

'--L O A D   I N V O I C E   D E T A I L S ???
load.det:
	FOR l% = 1 TO maxlines%
		in$(l%, 1) = "0": in$(l%, 2) = "   ": in$(l%, 3) = "": in$(l%, 4) = "": in$(l%, 5) = "": in$(l%, 6) = "0"
		in$(l%, 7) = "0": in$(l%, 8) = "0": in$(l%, 9) = "N/": in$(l%, 10) = "0": in$(l%, 11) = "0": in$(l%, 12) = "N"
		in$(l%, 13) = "0": in$(l%, 14) = "0": in$(l%, 15) = ""
	NEXT
IF NOT rview% THEN
	tot.ltact = 0      'Litres on order
	tot.ltinv = 0      'Litres invoiced
	tot.dollr = 0
	tot.items& = 0
	discovr! = 0'Discount override
	ovrPrice! = -9999
	invmsg1$ = ""'Clear out any old messages
	invmsg2$ = ""
	invmsg3$ = ""
	invmsg4$ = ""
	IF hord% = 0 THEN CALL findnext(hord%, norders%, ok%) ', add1$, add2$, add3$, add4$
	GET #48, hord%, ordhed
	invmsg1$ = ordhed.hnote1
	invmsg2$ = ordhed.hnote2

	hinvq = CVS(ordhed.hinvq$)

	nn% = -1: firstrec% = CVI(ordhed.hrrn$)
	CALL linkedl(rrn%(), nn%, firstrec%, hord%, 49)
END IF
	'-> Read throught the linked list of the details file
	dnext% = CVI(ordhed.hrrn$)
	IF rview% THEN
		dnext% = 1
		dlast% = LOF(96) / 32
	END IF
	l% = 0: m% = 0
	DO WHILE dnext% > 0
		IF NOT rview% THEN GET #49, dnext%, orddet
		IF rview% THEN GET #96, dnext%, orddet
		l% = l% + 1: IF l% > maxlines% THEN l% = maxlines%: EXIT DO
		ditem% = CVI(orddet.ditem$)
		ordqty% = CVI(orddet.dordq$)
		invqty% = CVI(orddet.dinvq$)
		IF rview% THEN
			ordqty% = invqty%
			invqty% = 0
		END IF
		rmc! = CVS(orddet.dprice$)
		gate! = CVS(orddet.dtax$)
		IF ordqty% > 0 THEN
			m% = m% + 1
			CALL loadLine(m%, -1, ditem%, ordqty%, invqty%, rmc!, gate!)'initial load
		END IF
		'- Bottom of read equal loop
		IF NOT rview% THEN dnext% = orddet.drrn%
		IF review% AND dnext% = dlast% THEN EXIT DO
		IF rview% THEN dnext% = dnext% + 1
	LOOP
	'Clear out items above loaded number.
	s% = m% + 1
	FOR m% = s% TO l%
		invqty% = 0
		ordqty% = 0
		ditem% = 0
		CALL loadLine(m%, -1, ditem%, ordqty%, invqty%, rmc!, gate!)
	NEXT

	TaxRate! = GST
	IF NOT rview% THEN CALL add.up.order(tot.ltact!, tot.ord!, tot.weight!)
RETURN

detail:
	CALL setup("S T O C K    E N T R Y")
	btma$ = "F1-Save/Enter.    F6-Browse  "
	IF rview% THEN btma$ = "F1-Return"
	COLOR 8, 3: LOCATE 25, 1: PRINT btma$;

	IF NOT rview% THEN CALL add.up.order(tot.ltact!, tot.ord!, tot.weight!)
	IF tot.exe! <> 0 THEN BEEP: CALL sndmsg("Empty order has a dollar value!"): BEEP

	d.elem% = 1'Start at element number 1.
	scrn.pag% = 1
	l% = 1
detail.a:
	IF updwn% = 73 THEN l% = d.elem%'page up
	IF updwn% = 81 THEN l% = d.elem%'page down
	e.elem% = d.elem% + 14
	IF e.elem% > maxlines% THEN e.elem% = maxlines%
	COLOR 7, 0: LOCATE 2, 2: PRINT "µ": LOCATE 2, 79: PRINT "Æ"
	COLOR 2, 0:
	LOCATE 2, 3: PRINT USING " Order:####"; hord%;
	a$ = "  " + LEFT$(CUS.sname$, 20) + " " + LEFT$(CUS.scont$, 20) + " " + CUS.search$ + CUS.stype$ + "  "
	COLOR 2
	PRINT a$
	COLOR 2

	LOCATE , 2: COLOR 6, 0: PRINT "Qty. Size   No.  Description                            RMC    Gate   Volume"

	COLOR 2
	LOCATE , 2: COLOR 2, 0: PRINT "ÄÄÄÄÂÄÄÄÄÄÂÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄ"
	LOCATE , 2: COLOR 10: PRINT USING "p #"; scrn.pag%: COLOR 2
	sav.l% = l%
	FOR l% = d.elem% TO e.elem%
		CALL dsplyLine(l%, d.elem%)
		NEXT
	l% = sav.l%
	LOCATE , 2: COLOR 2, 0: PRINT "ÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄ"

	IF rview% THEN
		CALL inpnew(a$, 0, updwn%, "59")
		IF updwn% = 59 THEN GOTO igacc02.x
		
	END IF

	'--Get line entries
	updwn% = 0
	sav.scrn.pag% = scrn.pag%
	DO WHILE updwn% <> 59 AND sav.scrn.pag% = scrn.pag%
		ln% = (l% - d.elem%) MOD 15 + 1: ln% = ln% + 4
		CALL chglin(ln%, l%, d.elem%, updwn%)
		IF updwn% = 62 THEN EXIT DO   'F4 - Delete
		IF updwn% = 60 THEN l% = l% - 2'F2 - Back one line
		IF updwn% = 72 THEN l% = l% - 2'/\ - Back up one line
		IF updwn% = 73 THEN l% = l% - 16'Page up one screen
		IF updwn% = 81 THEN l% = l% + 16'Page down one screen

		IF updwn% = 72 AND l% = -1 THEN 'end- Find next unused line
				l% = maxlines% + 1
				DO UNTIL VAL(in$(l% - 1, 1)) <> 0
					l% = l% - 1
					IF l% = 1 THEN EXIT DO
					LOOP
				l% = l% - 1
				END IF
		l% = l% + 1
		IF l% > maxlines% THEN l% = maxlines%
		sav.scrn.pag% = scrn.pag%
		SELECT CASE l%
		CASE 31 TO 45: d.elem% = 31: scrn.pag% = 3
		CASE 16 TO 30: d.elem% = 16: scrn.pag% = 2
		CASE ELSE: d.elem% = 1: scrn.pag% = 1
		END SELECT
		IF l% > maxlines% THEN l% = maxlines%' Past end of data
		IF l% < 1 THEN l% = 1              ' Before start of data
		IF l% > d.elem% + 14 THEN l% = d.elem% + 15' Past end of screen
		IF l% < d.elem% THEN l% = d.elem%  ' Before start of screen
		LOOP
	IF sav.scrn.pag% <> scrn.pag% AND updwn% <> 59 THEN GOTO detail.a
RETURN

igacc02.x:
	CLOSE #3
	CLOSE #43
	CLOSE #49
	IF rview% THEN CLOSE #96

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
	PRINT #99, USING "Hazard........> !"; tnthed.Hazard$

	PRINT #99, USING "|---------------------------------------------|!"; ""
	PRINT #99, USING "|  Litres.     Kilos..     Sg....     Cost/LT |!"; ""
	PRINT #99, USING "|   V/Sol.      W/Sol.     P.V.C.      P.B.R  |!"; ""
	PRINT #99, USING "|  ####.##     ####.##     ##.###      ##.### |"; tnthed.ltr!; tnthed.kg!; tnthed.sg!; tnthed.rawcost!
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
	MID$(prtbuf$, 6, 26) = msrmat.Desc1$
	IF qty!(seq%) > 0 THEN
		MID$(prtbuf$, 33, 6) = format$(qty!(seq%), "###.##")
		MID$(prtbuf$, 39, 2) = LCASE$(msrmat.useunit$)
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
	PRINT #99, USING "³COLOUR =      ³SHEEN =    ³DRY.. =    ³FILTER ### ³ S/G #.### ³Date.         !"; tnthed.filter%; tnthed.sg!; "³"
	PRINT #99, USING "ÀÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄ!"; "Ù"

	PRINT #99, CHR$(12);
	CLOSE #99
END SUB

SUB prtstk (totltr!)
'/////    P R I N T   S T O C K   T O   F I L E    //////////
stockprint:

	'Setup information

	GET #48, hord%, ordhed
	GET #57, rec26%, batch
	start.det.rec% = CVI(ordhed.hrrn$)

	'>>>---- Open an invoice copy file

			thisbatch$ = batch.year$ + "0000"
			B$ = MID$(STR$(rec26%), 2)
			MID$(thisbatch$, 7 - LEN(B$), LEN(B$)) = B$
			thisbatch3$ = "B" + thisbatch$
			thisbatch2$ = "B" + thisbatch$ + ".RBS"
			thisbatch$ = "B" + thisbatch$ + ".STK"
			IF DIR$(".\batches\" + thisbatch$) > "" THEN
				CALL killa(thisbatch$)
			END IF

	STDOUT2$ = ".\export\" + thisbatch2$
	OPEN STDOUT2$ FOR OUTPUT AS #97
	STDOUT3$ = ".\batches\" + thisbatch$
	OPEN STDOUT3$ FOR RANDOM SHARED AS #96 LEN = 32

	WRITE #97, "BS-ID", "Stock made from Completed Batch"
	WRITE #97, "BLANK", "dlinvq%", "size", "unit", "ditem%", "Des1", "Des2", "Bulk", "Pkge", "Label", "Manu", "RMC", "cogs", "Lid", "Box", "BoxLabel"


	'>>>> Read through the linked list of the details file <<<<
	dnext% = start.det.rec%
	l% = 0: lin% = 0

	DO WHILE dnext% > 0 AND lin% < 19
		GET #49, dnext%, orddet
		l% = l% + 1
		'>>> Decode the detail file <<<
		dord% = orddet.dord%
		ditem% = CVI(orddet.ditem$)
		dlinvq% = CVI(orddet.dinvq$) 'PD edit CVI(orddet.dlinvq$)
		IF ditem% < 1 OR ditem% > maxacc% OR dlinvq% = 0 THEN
		ELSE
			lin% = lin% + 1
			manu! = 0
			bulk! = 0
			label! = 0
			pkge! = 0
			lid! = 0
			pbox! = 0
			boxlbl! = 0
			dgate! = 0
			GET #3, ditem%, acstk
			pack% = acstk.pack%
			IF pack% = 0 THEN pack% = 1
			dprice = CVS(orddet.dprice$)
			dordq% = CVI(orddet.dordq$)
			dinvq% = CVI(orddet.dinvq$)
			size! = VAL(acstk.size$)
			'get label, bulk, pkge and manu costs. get routine from acstk

		SELECT CASE UCASE$(acstk.unit$)
			CASE "ML":
				bulk! = VAL(acstk.size$) * fillcost / 1000
			CASE "LT":
				bulk! = VAL(acstk.size$) * fillcost
			CASE "LS":
				bulk! = VAL(acstk.size$) * fillcost
			CASE "GM":
				bulk! = VAL(acstk.size$) * fillcost / 1000 / batch.rheomodifier
			CASE "GS":
				bulk! = VAL(acstk.size$) * fillcost / 1000 / batch.rheomodifier
			CASE "KG":
				bulk! = VAL(acstk.size$) * fillcost / batch.rheomodifier
			CASE ELSE: bulk! = 0
		END SELECT
												
		bulk! = bulk! * pack%
		
			IF acstk.pkge% > 0 THEN
				GET #38, acstk.pkge%, msrmat
				pkge! = msrmat.usecost * pack%
			END IF
			IF acstk.lid% > 0 THEN
				GET #38, acstk.lid%, msrmat
				lid! = msrmat.usecost * pack%
			END IF
			IF acstk.label% > 0 THEN
				GET #38, acstk.label%, msrmat
				label! = msrmat.usecost * pack%
			END IF
			IF acstk.pbox% > 0 THEN
				GET #38, acstk.pbox%, msrmat
				pbox! = msrmat.usecost
			END IF
			IF acstk.boxlbl% > 0 THEN
				GET #38, acstk.boxlbl%, msrmat
				boxlbl! = msrmat.usecost
			END IF
			IF acstk.manu% > 0 THEN
				GET #38, acstk.manu%, msrmat
				manu! = msrmat.usecost
			END IF

			SELECT CASE acstk.unit$
			CASE "ML"
				ltinv! = dlinvq% * size! / 1000
				
			'CASE ELSE: ltinv! = 0
			END SELECT
		END IF
			rmc! = bulk! + pkge! + lid! + label! + pbox! + boxlbl!
			cogs! = rmc! + manu!
			WRITE #97, "BSDET", dlinvq%, acstk.size$, acstk.unit$, ditem%, acstk.Desc1$, acstk.desc2$, bulk!, pkge!, label!, manu!, rmc!, cogs!, lid!, pbox!, boxlbl!

			'Write to audit file
			dprice! = bulk! + pkge! + lid! + label! + pbox! + boxlbl!
			dgate! = dprice! + manu!
			orddet.dprice$ = MKS$(dprice!)
			orddet.dtax$ = MKS$(dgate!)
			PUT #96, l%, orddet

			'Send real rmc to acstk - to be done
			acstk.bulk! = bulk!
			acstk.rmc! = bulk! + pkge! + lid! + label! + pbox! + boxlbl!
			acstk.cogs! = bulk! + pkge! + lid! + label! + pbox! + boxlbl! + manu!
			acstk.gpc! = (1 - acstk.cogs! / acstk.distributor!) * 100
			acstk.gpr! = (1 - acstk.rmc! / acstk.distributor!) * 100
			PUT #3, ditem%, acstk
		'>>> Bottom of read equal loop <<<
		dnext% = orddet.drrn%
LOOP
		'Save flag to batch record
		batch.flstk$ = "Y"
		batch.solventvar! = totltr!
		batch.thickenervar! = fillcost!
		batch.stainer1var! = batch.ayld! - totltr!
		batch.stainer2var! = (totltr! / batch.ayld!) * 100
		PUT #57, rec26%, batch

		'Send yield & last filled cost to tnthed.
		CLOSE #64
		OPEN "forhed.asf" FOR RANDOM SHARED AS #64 LEN = 160
		GET #64, batch.tnt%, tnthed
		tnthed.alccost! = fillcost!
		MID$(tnthed.name$, 24, 4) = MKS$(batch.stainer2var!)
		PUT #64, batch.tnt%, tnthed
		'CLOSE #64

		WRITE #97, "BLANK", "thisbatch", "dateman", "flstk", "FLtr", "FCostPer", "YPct", "WLtr", "WCost"
		WRITE #97, "BSACT", batch.thisbatch$, batch.dateman$, batch.flstk$, batch.solventvar!, batch.thickenervar!, batch.stainer2var!, batch.stainer1var!, 0

XRETURN.1:
CLOSE #97
CLOSE #96



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
		CALL round(Cobalt!(pass%), 2.5)
		CALL round(lead!(pass%), 2.5)
		CALL round(Calcium!(pass%), 2.5)
		CALL round(Manganese!(pass%), 2.5)                      '*******
		CALL round(Meko!(pass%), 2.5)
		CALL round(POLY!(pass%), 2.5)

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
					rm.tankltmm!(i%) = rm.tankltmm!(i% - 1)
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

SUB ReturntoStock (form$, thisltr!)


	CALL sndmsg("Consuming Stock in Production of Batch " + form$)
	atimer! = TIMER

	
	'Calcultate the multiplier for this batch size
	'mult# = thisltr! / tnthed.yield!
	 mult# = 1 'done already in work file?

	FOR lin% = 1 TO 38
		startrec54% = 1
		drec54% = startrec54% + lin% - 1

		'open detail work file for this batch from batchnumber file in batches
		GET #ch.det%, drec54%, tntdet

		IF tntdet.rmat% >= 1 AND tntdet.rmat% <= maxrmat% THEN '1=Hydroxinol - Don't update stock
			GET #38, tntdet.rmat, msrmat

			thisqty! = ABS(tntdet.qty!)
			SELECT CASE msrmat.useunit$
			CASE "KG", "LT", "GM", "MT", "OZ", "ML": thisqty! = thisqty! * mult#
			CASE ELSE
			END SELECT

			SELECT CASE msrmat.useunit$
			CASE "EQ", "EA", "MN", "HR"
			CASE ELSE
				GET #38, tntdet.rmat, msrmat
				'msrmat.soh = msrmat.soh + Thisqty!
				msrmat.sip = msrmat.sip - thisqty!
				PUT #38, tntdet.rmat, msrmat
			END SELECT

		END IF

	NEXT

	DO WHILE ABS(TIMER - atimer!) < 1: LOOP
	CALL sndmsg("")

x.returntostock:

END SUB

SUB rightprice (price!) STATIC
				price! = acstk.distributor
x.rightprice:

END SUB

SUB save.lines (rec26%, auto%) STATIC
	 CALL setup("F I N A L I S E   F O R U M U L A   E N T R Y")
	 COLOR 8, 3: LOCATE 25, 1: PRINT SPACE$(80); : COLOR 2, 0
	 
	 'set batch formula details
	 GET #57, rec26%, batch

	 batch.alccost! = tot.ext!
	 CALL round(batch.alccost!, 2.5)
	 batch.perltr! = tot.ext! / tot.ltr!
	 CALL round(batch.perltr!, 2.5)
	 batch.ayld! = tot.ltr!
	 batch.resinvar! = tot.kg!
	 batch.rheomodifier! = 0: IF tot.ltr! <> 0 THEN batch.rheomodifier! = tot.kg! / tot.ltr!
	 batch.qcpvc! = tot.pvcpct!
	 batch.qcpbr! = tot.pbrpct!
	 wrkd$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
	 batch.dateman$ = FNDY$(wrkd$)

	 ' Setup display for info
	 IF batch.flstk$ = "R" THEN LOCATE 9, 20: PRINT USING "Lt Filled as Raw Mat..> #####.##"; batch.ayld
	 LOCATE 10, 20: PRINT USING "Manufacturing Date...>  \      \"; FNDYY$(batch.dateman$)
	 LOCATE 11, 20: PRINT USING "Operator.............>  \ \"; batch.manby$

	 LOCATE 12, 20: PRINT USING "Actual Yield.........>   #,###.## L"; batch.ayld!
	 LOCATE 13, 20: PRINT USING "Actual Kilograms.....>   #,###.## kg"; batch.resinvar!
	 LOCATE 14, 20: PRINT USING "Actual Cost..........>$$##,###.##"; batch.alccost!
	 LOCATE 15, 20: PRINT USING "Actual PVC...........>     ###.##"; batch.qcpvc!
	 LOCATE 16, 20: PRINT USING "Actual PBR...........>     ###.##"; batch.qcpbr!
	 

	 'Change info from above
IF batch.flstk$ = "R" THEN
sl0:    '***** Filled asRmat  volume
	LOCATE 9, 44: a$ = STR$(batch.ayld)
	CALL inpnew(a$, 7.2, updwn%, "13,59")
	batch.solventvar = VAL(a$)
END IF
sl1:    '***** Manufacturing Date
	LOCATE 10, 44: a$ = FNDYY$(batch.dateman$)
	CALL inpnew(a$, 100!, updwn%, "13,59")
	batch.dateman$ = FNDY$(a$)

	IF updwn% = 59 THEN GOTO save.lines.input
	IF updwn% = 60 AND batch.flstk$ = "R" THEN GOTO sl0

sl2:    '***** Operator
	LOCATE 11, 44: a$ = batch.manby$
	CALL inpnew(a$, 103!, updwn%, "13,59-60")
	batch.manby$ = UCASE$(a$)

	IF updwn% = 59 THEN GOTO save.lines.input
	IF updwn% = 60 THEN GOTO sl1

save.lines.input:

	 COLOR 2
	 LOCATE 18, 25: PRINT "   1.  WITHOUT UPDATE"
	 LOCATE 19, 25: PRINT "   2.  FINALISE VALUES"
	 LOCATE 21, 29: PRINT "Your choice.> "; 'CHR$(FNH);
	 opt% = 2 '**Force save (NOTE: The system keeps track of save by its self)
	 IF NOT auto% THEN
			in$ = STR$(opt%): in$ = MID$(in$, 2)
			LOCATE 21, 43: CALL inpnew(in$, 1!, updwn%, "13,60")
			IF updwn% = 60 THEN GOTO sl2
			opt% = VAL(in$)
	 END IF

	'>>----- S A V E -----<<
	IF opt% = 2 THEN
		'Save Batch info
		batch.fltnt$ = "Y"

	 '>-Transfer to raw material file.
	 IF batch.asRmat > 0 AND batch.asRmat < maxrmat% AND batch.flstk$ = "R" THEN

		
		GET #38, batch.asRmat, msrmat
			msrmat.sg = batch.rheomodifier!
			msrmat.PurCost = batch.perltr!
			SELECT CASE UCASE$(msrmat.useunit$)
				 CASE "LT": msrmat.soh = msrmat.soh + batch.solventvar
				 CASE "KG": msrmat.soh = msrmat.soh + batych.resinvar * (batch.solventvar / batch.ayld)
				 CASE "KL": msrmat.soh = msrmat.soh + batch.solventvar / 1000
				 CASE "MT": msrmat.soh = msrmat.soh + batych.resinvar * (batch.solventvar / batch.ayld) / 1000
				 CASE "ML": msrmat.soh = msrmat.soh + batch.solventvar * 1000
				 CASE "GM": msrmat.soh = msrmat.soh + batych.resinvar * (batch.solventvar / batch.ayld) * 1000
				 CASE "OZ": msrmat.soh = msrmat.soh + batch.solventvar / 28.413
				 CASE ELSE: msrmat.soh = msrmat.soh + batch.solventvar
			END SELECT
				 
			CALL calcusecost
			msrmat.usecost = msrmat.usecost * (batch.solventvar / batch.ayld)
		PUT #38, batch.asRmat, msrmat
		
	 END IF


		PUT #57, rec26%, batch
	
	'>>>---- Open audit record file
	rba$ = ".\export\B" + RTRIM$(LTRIM$(batch.thisbatch$)) + ".RBA"
	OPEN rba$ FOR OUTPUT AS #97
				
	WRITE #97, "BA-ID", "Batch Record upon Completion"

	'--------------> BAHED
	WRITE #97, "BLANK", "thisbatch$", "form$+revision", "name", "sorw", "class", "yld", "datesch", "datereq", "dateman", "fltnt", "flstk", "flqc", "manby"
	WRITE #97, "BAHED", batch.thisbatch$, batch.form$ + STR$(batch.revision), batch.name$, batch.SorW$, batch.class, batch.yld, FNDYY$(batch.date$), FNDYY$(batch.datereq$), FNDYY$(batch.dateman$), batch.fltnt$, batch.flstk$, batch.flqc$, batch.manby$

	'--------------> BATNT
	tnt1 = batch.gloss
	tnt2$ = batch.Hazard$
	tnt3% = batch.asRmat%
	tnt4$ = batch.CostPer

	WRITE #97, "BLANK", "Yield", "Ltr", "kg", "visc1h", "visc1l", "visc2h", "visc2l", "rawcost", "filter", "grind", "ph", "sg", "vsol", "wsol", "pvc", "pbr", "gloss", "hazard", "asrmat", "costper"
	WRITE #97, "BATNT", batch.yield, batch.ltr, batch.kg, batch.visc1h, batch.visc1l, batch.visc2h, batch.visc2l, batch.rawcost, batch.filter%, batch.grind, batch.ph, batch.sg, batch.Vsol, batch.Wsol, batch.pvc, batch.pbr, tnt1, tnt2$, tnt3%, tnt4$

	'--------------> BAACT
	act1 = batch.stainer1var
	act2 = batch.stainer2var
	act3 = batch.stainer3var
	WRITE #97, "BLANK", "ayld", "akg", "asg", "acost", "acostper", "fltr", "fcost", "wltr", "ypct", "wcost"
	WRITE #97, "BAACT", batch.ayld, batch.resinvar, batch.rheomodifier, batch.alccost, batch.perltr, batch.solventvar, batch.thickenervar, batch.sg, batch.resinvar, batch.solventvar, batch.thickenervar, batch.rheomodifier, act1, act2, act3

	'--------------> BAQCD
	WRITE #97, "BLANK", "note1", "note2", "note3", "note4", "vsol,", "wsol", "pvc", "pbr", "visc1", "visc2", "ph", "gloss", "sg"
	WRITE #97, "BAQCD", batch.qcnote1$, batch.qcnote2$, batch.qcnote3$, batch.qcnote4$, batch.qcvsol, batch.qcwsol, batch.qcpvc, batch.qcpbr, batch.qcvisc1, batch.qcvisc2, batch.qcph, batch.qcgloss, batch.qcsg

	'--------------> BADET
	WRITE #97, "BLANK", "oldrmat%", "oldqty!", "olddesc$", "olduseunit$", "oldusecost!", "oldcmt%", "oldcmtqty!", "tntdet.rmat%", "tntdet.qty!", "msrmat.desc2$", "msrmat.useunit$", "msrmat.usecost", "cmt", "cmtqty", "msrmat.Hazard$", "batchno"
	startrec& = 1 * maxformseq% - maxformseq% + 1

	FOR seq% = 1 TO maxformseq%
		'Clear fields
				thisqty! = 0
				thisrmat% = 0
				thisdesc$ = ""
				thisuseunit$ = ""
				thisusecost! = 0
				thiscmt% = 0
				thiscmtqty! = 0

		'>-Reduce SIP
		GET #65, seq%, tntdet
		IF tntdet.rmat% > 0 AND tntdet.rmat% < maxrmat% THEN
			GET #38, tntdet.rmat%, msrmat
				msrmat.sip = msrmat.sip - tntdet.qty!
				thisqty! = ABS(tntdet.qty!)
				thisrmat% = tntdet.rmat%
				thisdesc$ = msrmat.desc2$
				thisuseunit$ = msrmat.useunit$
				thisusecost! = msrmat.usecost!
				thiscmt% = tntdet.cmt%
				thiscmtqty! = tntdet.cmtqty!
			PUT #38, tntdet.rmat%, msrmat
		END IF
		'Set tntdet values from details
		drec& = startrec& + seq% - 1
		tntdet.tnt& = drec&
		tntdet.rmat% = rmno%(seq%)
		tntdet.qty! = qty!(seq%)
		tntdet.cmt% = cmtno%(seq%)
		tntdet.cmtqty! = cmtqty!(seq%)
		tntdet.tfiller$ = rmbno$(seq%)
		PUT #65, drec&, tntdet

	 '>-Remove qty from stock
	 IF tntdet.rmat% > 0 AND tntdet.rmat% < maxrmat% THEN
		GET #38, tntdet.rmat%, msrmat
			msrmat.soh = msrmat.soh - tntdet.qty!
			msrmat.used = msrmat.used + tntdet.qty!
			'sohv
		PUT #38, tntdet.rmat%, msrmat
		rmdesc$ = msrmat.Desc1$: IF RTRIM$(msrmat.desc2$) > "" THEN rmdesc$ = msrmat.desc2$
	 END IF

	 'Setup for export
		IF tntdet.rmat% > 0 THEN
			WRITE #97, "BADET", thisrmat%, thisqty!, thisdesc$, thisuseunit$, thisusecost!, thiscmt%, thiscmtqty!, tntdet.rmat%, tntdet.qty!, msrmat.desc2$, msrmat.useunit$, msrmat.usecost, tntdet.cmt%, tntdet.cmtqty!, msrmat.Hazard$, tntdet.tfiller$
		ELSE
			WRITE #97, "BADET", thisrmat%, thisqty!, thisdesc$, thisuseunit$, thisusecost!, thiscmt%, thiscmtqty!, 0, 0, "", "", 0, 0, 0, "", ""
		END IF
	 NEXT



	CLOSE #97
	CLOSE #96
	

	END IF

x.save.lines:

END SUB

SUB searchindex (keyin$, chi%, found%) STATIC
''$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

SUB UpdateOrder (hord%, updwn%)
UpdateOrder:
	'-First ensure all the details records have been allocated a rrn
	FOR l% = 1 TO maxlines%
		IF VAL(in$(l%, 4)) <> 0 OR VAL(in$(l%, 14)) <> 0 THEN n% = l%
	NEXT
	nn% = n%: firstrec% = CVI(ordhed.hrrn$)
	CALL linkedl(rrn%(), nn%, firstrec%, hord%, 49)
	'-Update the order file before printing the picking slip
	tot.ltact = 0      'Litres on order
	tot.ltinv = 0      'Litres invoiced
	tot.dollr = 0
	tot.items& = 0
	FOR l% = 1 TO nn%
		keyed% = VAL(in$(l%, 1))
		ordqty% = VAL(in$(l%, 10))
		invqty% = VAL(in$(l%, 11))
		sooqty% = VAL(in$(l%, 13))
		svrrn% = VAL(in$(l%, 14))
		BoFlag$ = in$(l%, 12)
		'tmp$ = "Line =" + STR$(l%) + " B4 rrn/qty =" + STR$(svrrn%) + "/" + STR$(sooqty%)

		IF mode$ = "inv" THEN
			invqty% = keyed%
			ordqty% = 0
			dlinvq% = keyed%
			BoFlag$ = "N"
		END IF
		IF mode$ = "ord" THEN
			invqty% = 0
			ordqty% = keyed%
			dlinvq% = CVI(orddet.dlinvq$)
		END IF
		IF mode$ = "b/o" THEN
			invqty% = keyed%
			ordqty% = ordqty% - keyed%
			IF ordqty% < 0 THEN ordqty% = 0
			dlinvq% = keyed%
			BoFlag$ = "N": IF ordqty% > 0 THEN BoFlag$ = "Y"
		END IF
		'-Add up litres order and actualy on order
		ltact = 0: ltinv = 0
		size! = VAL(in$(l%, 2))
		IF in$(l%, 3) = "LT" THEN ltact = ordqty% * size!
		IF in$(l%, 3) = "ML" THEN ltact = ordqty% * size! / 1000
		tot.ltact = tot.ltact + ltact
		IF in$(l%, 3) = "LT" THEN ltinv = invqty% * size!
		IF in$(l%, 3) = "ML" THEN ltinv = invqty% * size! / 1000
		dprice = VAL(in$(l%, 6))
		tot.ltinv = tot.ltinv + ltinv
		tot.dollr = tot.dollr + (dprice * ordqty%)
		tot.items& = tot.items& + ordqty%
		IF ordqty% < 0 THEN ordqty% = 0

		GET #49, rrn%(l%), orddet
		LSET orddet.dinvq$ = MKI$(invqty%)
		LSET orddet.dordq$ = MKI$(ordqty%)
		LSET orddet.dlinvq$ = MKI$(dlinvq%)
		LSET orddet.ditem$ = MKI$(VAL(in$(l%, 4)))
		LSET orddet.dprice$ = MKS$(VAL(in$(l%, 6)))
		LSET orddet.dtax$ = MKS$(VAL(in$(l%, 7)))
		LSET orddet.dBo$ = BoFlag$
		LSET orddet.dfiller$ = in$(l%, 15)
		PUT #49, rrn%(l%), orddet: SOUND 20000, 1

		'-Update the stock file (remove previous)
		IF svrrn% >= 1 AND svrrn% <= maxacc% THEN
			GET #3, svrrn%, acstk
			acstk.sip% = acstk.sip% - sooqty%
			pack% = acstk.pack%
			IF pack% = 0 THEN pack% = 1
			PUT #3, svrrn%, acstk

			IF acstk.pkge% > 0 THEN
				GET #38, acstk.pkge%, msrmat
				msrmat.sip! = msrmat.sip! - sooqty% * pack%
				PUT #38, acstk.pkge%, msrmat
			END IF
			IF acstk.lid% > 0 THEN
				GET #38, acstk.lid%, msrmat
				msrmat.sip! = msrmat.sip! - sooqty% * pack%
				PUT #38, acstk.lid%, msrmat
			END IF
			IF acstk.label% > 0 THEN
				GET #38, acstk.label%, msrmat
				msrmat.sip! = msrmat.sip! - sooqty% * pack%
				PUT #38, acstk.label%, msrmat
			END IF
			IF acstk.pbox% > 0 THEN
				GET #38, acstk.pbox%, msrmat
				msrmat.sip! = msrmat.sip! - sooqty%
				PUT #38, acstk.pbox%, msrmat
			END IF
			IF acstk.boxlbl% > 0 THEN
				GET #38, acstk.boxlbl%, msrmat
				msrmat.sip! = msrmat.sip! - sooqty%
				PUT #38, acstk.boxlbl%, msrmat
			END IF
			IF acstk.manu% > 0 THEN
				GET #38, acstk.manu%, msrmat
				msrmat.sip! = msrmat.sip! - sooqty%
				PUT #38, acstk.manu%, msrmat
			END IF


		END IF

		'-Update the stock file
		ditem% = CVI(orddet.ditem$)
		IF ditem% < 1 OR ditem% > maxacc% THEN
			IF ditem% <> 0 THEN SOUND 50, 1
		ELSE
			GET #3, ditem%, acstk
			acstk.soh% = acstk.soh% + dlinvq%
			acstk.sip% = acstk.sip% + ordqty%
			pack% = acstk.pack%
			IF pack% = 0 THEN pack% = 1
			PUT #3, ditem%, acstk

			IF acstk.pkge% > 0 THEN
				GET #38, acstk.pkge%, msrmat
				msrmat.soh! = msrmat.soh! - dlinvq% * pack%
				msrmat.used! = msrmat.used! + dlinvq% * pack%
				msrmat.sip! = msrmat.sip! + ordqty% * pack%
				PUT #38, acstk.pkge%, msrmat
			END IF
			IF acstk.lid% > 0 THEN
				GET #38, acstk.lid%, msrmat
				msrmat.soh! = msrmat.soh! - dlinvq% * pack%
				msrmat.used! = msrmat.used! + dlinvq% * pack%
				msrmat.sip! = msrmat.sip! + ordqty% * pack%
				PUT #38, acstk.lid%, msrmat
			END IF

			IF acstk.label% > 0 THEN
				GET #38, acstk.label%, msrmat
				msrmat.soh! = msrmat.soh! - dlinvq% * pack%
				msrmat.used! = msrmat.used! + dlinvq% * pack%
				msrmat.sip! = msrmat.sip! + ordqty% * pack%
				PUT #38, acstk.label%, msrmat
			END IF
			IF acstk.pbox% > 0 THEN
				GET #38, acstk.pbox%, msrmat
				msrmat.soh! = msrmat.soh! - dlinvq%
				msrmat.used! = msrmat.used! + dlinvq%
				msrmat.sip! = msrmat.sip! + ordqty%
				PUT #38, acstk.pbox%, msrmat
			END IF
			IF acstk.boxlbl% > 0 THEN
				GET #38, acstk.boxlbl%, msrmat
				msrmat.soh! = msrmat.soh! - dlinvq%
				msrmat.used! = msrmat.used! + dlinvq%
				msrmat.sip! = msrmat.sip! + ordqty%
				PUT #38, acstk.boxlbl%, msrmat
			END IF
			IF acstk.manu% > 0 THEN
				GET #38, acstk.manu%, msrmat
				' no soh for labour
				IF msrmat.cond$ <> "M" THEN msrmat.soh! = msrmat.soh! - dlinvq%
				msrmat.used! = msrmat.used! + dlinvq%
				msrmat.sip! = msrmat.sip! + ordqty%
				PUT #38, acstk.manu%, msrmat
			END IF



			IF in$(l%, 2) = "***" THEN 'special items
				GET #3, ditem%, acstk
				IF acstk.no <> ditem% OR ditem <= 20 THEN
					acstk.no = ditem%
					acstk.Desc1$ = in$(l%, 5)
					acstk.desc2$ = MID$(in$(l%, 5), 27, 10)

					acstk.counter = CVS(orddet.dprice$)
					acstk.contract = acstk.counter
					acstk.distributor = acstk.counter
					acstk.distributor = acstk.counter
					acstk.industrial = acstk.counter
					acstk.trade = acstk.counter
					acstk.wholesalecost = acstk.counter
					acstk.retail = acstk.counter
					PUT #3, ditem%, acstk
				END IF
			END IF
		END IF
		'-End of updating the stock file

		'tmp$ = tmp$ + " AF rrn/qty =" + STR$(ditem%) + "/" + STR$(ordqty%)
		'CALL sndmsg(tmp$): X$ = INPUT$(1)

	NEXT

	GET #48, hord%, ordhed
	hinvq = CVS(ordhed.hinvq$)
	LSET ordhed.hord$ = MKI$(hord%)
	LSET ordhed.hsup$ = CUS.search$ + CUS.stype$

	LSET ordhed.hrrn$ = MKI$(rrn%(1))
	LSET ordhed.horgq$ = MKS$(tot.ord!)
	LSET ordhed.hordq$ = MKS$(tot.ltact)
	LSET ordhed.hinvq$ = MKS$(tot.ltinv)
	LSET ordhed.hdollar$ = MKS$(tot.dollr)
	IF tot.items& < 32000 THEN wrkitems% = tot.items& ELSE wrkitems% = 32000
	LSET ordhed.hitems$ = MKI$(wrk.items%)
	LSET ordhed.ldisc$ = MKS$(vdisc)
	ordhed.hnote1 = invmsg1$
	ordhed.hnote2 = invmsg2$

	PUT #48, hord%, ordhed

END SUB

