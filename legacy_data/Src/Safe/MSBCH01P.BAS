DECLARE SUB copytnthed (rec54&, rec57%, auto%)
DECLARE SUB accbrowse (rec%)
DECLARE SUB add.up.order (tot.ltact!, tot.ord!, tot.ext!)
DECLARE SUB alcbatch (gen$, rec57%, thisltr!, thisbatch$)
DECLARE SUB browse38 (browse38.result%, updwn%)
DECLARE SUB cf8 (L%, d.elem%, newdata$)
DECLARE SUB chglin (ln%, L%, d.elem%, updwn%)
DECLARE SUB copybatch (rec54&)
DECLARE SUB custombatch (rec54&, thisltr!, updwn%, auto%)
DECLARE SUB cvt.tnt (tnt$, tnt%, tntf$)
DECLARE SUB delOrder (hord%, n%, clr%, autodel$, thissup$, norders%)
DECLARE SUB doprint (rec&, thisbatch$, thisltr!, prt.batch%, prt.costs%, updwn%)
DECLARE SUB dsply (sno%, norders%)
DECLARE SUB dsplyLine (L%, d.elem%)
DECLARE SUB dsporders (dspstart%, norders%, custin$)
DECLARE SUB ean13 (in$, dind%)
DECLARE SUB findnext (hord%, norders%, ok%)
DECLARE SUB findorders (thissup$, norders%, hord%)
DECLARE SUB getform (opt%, form$, rec54&, updwn%)
DECLARE SUB height.in.tank (updwn%, seq%, Ltrs.in!, Height.from.btm!, Height.from.top!)
DECLARE SUB linkedl (rrn%(), n%, firstrec%, ord%, chd%)
DECLARE SUB loadLine (m%, il%, ditem%, ordqty%, invqty%, price!, rmc!)
DECLARE SUB mline ()
DECLARE SUB reallocate (rec57%, rec54&)
DECLARE SUB reprint (rec57%, rec54&)
DECLARE SUB ReturntoStock (form$, thisltr!)
DECLARE SUB rightprice (price!)
DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB setaudit (n%)
DECLARE SUB setchannel ()
DECLARE SUB UpdateOrder (hord%, updwn%)
DECLARE FUNCTION format$ (VALUE!, definition$)

	COMMON SHARED maxsup%, maxform%, maxrmat%, maxacc%, maxtypes, maxcus%, maxord%
	COMMON SHARED qk$, keyl%, rep$
	COMMON SHARED batchltr!, alprod%, hord%, batchsg!
	COMMON SHARED maxtnt%, msg$, maxtankrrn%
	COMMON SHARED ff!
	COMMON SHARED ch.hedx%, ch.hed%, ch.det%
	COMMON SHARED mode$, Modedesc$
	COMMON SHARED beg$, datereq$
	COMMON SHARED TaxRate!, DiscRate!
	COMMON SHARED ext.has.changed%, rec50%, ctl%, Cash%
	COMMON SHARED vdisc!, Rate!, discovr!, climit!, ovrPrice!
	COMMON SHARED tot.gst!, tot.ext!, tot.allup!
	COMMON SHARED skipexit%
	COMMON SHARED doc.type$, formtype$, sno%
	COMMON SHARED tot.ord!, tot.ltact, tot.ltinv, tot.dollr, tot.items&
	COMMON SHARED newsearch$
	COMMON SHARED bysearch$
	COMMON SHARED search.key$
	COMMON SHARED tot.qty, Tot.taxvol
	COMMON SHARED tot.dg200%, tot.dg60%, tot.dg20%, tot.dg10%, tot.dg4%, tot.dg2%, tot.dg1%, tot.dg850%, tot.dg500%, tot.dg300%, tot.dg250%, tot.dglt!
	COMMON SHARED extdisc!, inv.lt.printed!
	COMMON SHARED tender$
	COMMON SHARED invmsg1$, invmsg2$, invmsg3$, invmsg4$
	COMMON SHARED ean$, naudit%, acstkf$

	COMMON SHARED c%(), in$(), rrn%()
	COMMON SHARED tankrrn%()
	COMMON SHARED rm.tanksize!(), rm.tankltmm!()'Size of the tank for every line
	COMMON SHARED orders%()
	COMMON SHARED auditfile$()

	CONST maxlines% = 45 '
	CONST GST! = 10  '10%
	CONST debug% = 0
	typefields% = -1
	maxtankrrn% = 5

	DIM SHARED tankrrn%(maxtankrrn%)
	DIM SHARED rm.tanksize!(38), rm.tankltmm!(38) 'Size of the tank for every line
	DIM SHARED orders%(1001)
	DIM SHARED auditfile$(15)
	DIM SHARED c%(8), in$(maxlines%, 16), rrn%(maxlines%)
	'1=qty%,2=size,3=unit,4=itm,5=desc,6=price,7=SOH,8=ext
	'9=tax flag,10=ordqty%,11=Invqty,12=BoFlag,13=save qty
	'14=Save item, 15=Overtyped price


	'.dc - Complete
	'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
	apgm$ = "msmenu"
	'$ INCLUDE: '\tpmanuf\src\pgmerr.INC'
	
	'$INCLUDE: '\tpmanuf\src\acstk.INC'
	CLOSE #3
	'$INCLUDE: '\tpmanuf\src\msrmat.INC'
	'$INCLUDE: '\tpmanuf\src\msclass.INC'
	CLOSE #29
	'$INCLUDE: '\tpmanuf\src\mscomt.INC'
	'$INCLUDE: '\tpmanuf\src\tnthedx.INC'
	'$INCLUDE: '\tpmanuf\src\tnthed.INC'
	'$INCLUDE: '\tpmanuf\src\tntdet.INC'
	'$INCLUDE: '\tpmanuf\src\forhedx.inc'
	'$INCLUDE: '\tpmanuf\src\forhed.inc'
	'$INCLUDE: '\tpmanuf\src\fordet.inc'
	'$INCLUDE: '\tpmanuf\src\tntwrk.inc'
	'$INCLUDE: '\tpmanuf\src\msmisc.INC'
	'$INCLUDE: '\tpmanuf\src\msbatch.inc'



	keyl% = 20: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)
	maxord% = 999
	mode$ = "A - F"
	CALL setchannel
	SELECT CASE acstkf$
	CASE "PRE": CALL index("OPEN ", ind%, "acstkx3.pre", 7, keyl%)
	CASE ELSE: CALL index("OPEN ", ind%, "acstkx3.acf", 7, keyl%)
	END SELECT

	GET #36, 1, msmisc
	CLOSE #36
	maxsup% = CVI(msmisc.max1$): maxfrom% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxacc% = CVI(msmisc.max5$): maxtnt% = 999
	ff! = 2.5 / 100
	GET #ch.hedx%, 1, tnthedx

start:
	CALL setup("R E P O R T   P R I N T   M E N U")
	LOCATE 25, 4: COLOR 0, 3: PRINT "F1-Exit            F5-Swap Tints/Formulations"; : COLOR 2, 0
	CALL SNDMSG(msg$): msg$ = "": COLOR 2, 0
	LOCATE 3, 33: COLOR 10, 0: PRINT Modedesc$: COLOR 2, 0

	LOCATE 4, 2
	LOCATE , 15: PRINT
	LOCATE , 15: PRINT "          Allocate              Calculate"
	LOCATE , 15: PRINT "          batch No.             formula cost"
	LOCATE , 15: PRINT
	LOCATE , 15: PRINT "1......    Yes                    No"
	LOCATE , 15: PRINT "2......    No                     Yes"
	LOCATE , 15: PRINT "3......    No                     No"
	LOCATE , 15: PRINT "4......    No                     Yes in a range"
	LOCATE , 15: PRINT "5......    No                     No  in a range"
	LOCATE , 15: PRINT "6......    Yes                    No  no print"
	LOCATE , 15: PRINT "7......    Reprint batch sheet"
	LOCATE , 15: PRINT "8......    Reallocate batch number"
	LOCATE , 15: PRINT
	LOCATE , 15: PRINT "9......    Page advance."
	LOCATE , 15: PRINT "10.....    Print formulation list"
	LOCATE , 15: PRINT
	LOCATE 19, 29: PRINT "Option...>"
	LOCATE 19, 39
	CALL inpnew(opt$, 102!, updwn%, "13,59,63" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN GOTO ENDPGM
	IF updwn% = 63 THEN
		SELECT CASE mode$
		CASE "A - F": mode$ = "Tints"
		CASE "Tints": mode$ = "A - F"
		CASE ELSE
		END SELECT
		CALL setchannel
		GET #ch.hedx%, 1, tnthedx
		GOTO start
	END IF
	opt% = VAL(opt$)
	PCOPY 0, 1

	SELECT CASE opt%
	CASE 1 TO 6:
			prt.batch% = 0: prt.costs% = 0
			IF opt% = 1 THEN prt.batch% = -1: prt.costs% = 0
			IF opt% = 2 THEN prt.batch% = 0: prt.costs% = -1
			IF opt% = 3 THEN prt.batch% = 0: prt.costs% = 0
			IF opt% = 4 THEN prt.batch% = 0: prt.costs% = -1
			IF opt% = 5 THEN prt.batch% = 0: prt.costs% = 0
			IF opt% = 6 THEN prt.batch% = -1: prt.costs% = 0

			IF opt% = 4 OR opt% = 5 THEN
				LOCATE 18, 23: PRINT "Select first formulation..."
			END IF
			CALL getform(opt%, form$, rec54&, updwn%)
			IF updwn% = 59 THEN GOTO start
			IF updwn% = 60 THEN GOTO start

			CALL copybatch(rec54&)

			IF opt% < 4 THEN
				IF opt% = 1 THEN CALL alcbatch("Generate", rec57%, thisltr!, thisbatch$)
				GET #ch.hed%, rec54&, tnthed
				batchsg! = tnthed.sg
				auto% = 0
				CALL custombatch(rec54&, thisltr!, updwn%, auto%)
				IF updwn% = 13 THEN

					CALL doprint(rec54&, thisbatch$, thisltr!, prt.batch%, prt.costs%, updwn%)
					IF prt.batch% <> 0 THEN
					CALL alcbatch("update", rec57%, thisltr!, thisbatch$)

					CALL copytnthed(rec54&, rec57%, auto%)
					auto% = 0
					GET #ch.hed%, rec54&, tnthed
						tmp$ = tnthed.name$
						MID$(tmp$, 5, 6) = thisbatch$
						MID$(tmp$, 12, 4) = format(batch.yld!, "#####")
						MID$(tmp$, 16, 8) = batch.date$
						MID$(tmp$, 24, 6) = "      "
						tnthed.name$ = tmp$
					PUT #ch.hed%, rec54&, tnthed



					msg$ = "Batch " + thisbatch$
					END IF
					END IF

				END IF

			IF opt% = 4 OR opt% = 5 THEN
				PCOPY 1, 0
				LOCATE 19, 23: PRINT "Select last formulation..."
				updwn% = -1
				CALL getform(opt%, toform$, rec54&, updwn%)
				MID$(toform$, 4, 1) = "Z"
				IF updwn% = 59 THEN GOTO start
				IF updwn% = 60 THEN GOTO start

				FOR i% = 1 TO 999
					IF tnthedx.tnta$(i%) >= form$ AND tnthedx.tnta$(i%) <= toform$ THEN
						rec54& = tnthedx.rrn%(i%)
						CALL copybatch(rec54&)
						GET #ch.hed%, rec54&, tnthed
						IF opt% = 6 THEN
							CALL alcbatch("Generate", rec57%, thisltr!, thisbatch$)
							END IF
						auto% = -1
						CALL custombatch(rec54&, thisltr!, updwn%, auto%)
						CALL doprint(rec54&, thisbatch$, thisltr!, prt.batch%, prt.costs%, updwn%)
						 IF opt% = 6 THEN
							CALL alcbatch("update", rec57%, thisltr!, thisbatch$)
							END IF
						END IF
					NEXT
				END IF



	CASE 7: CALL reprint(rec57%, rec54&)
	CASE 8: CALL reallocate(rec57%, rec54&)
			IF rec54& > 0 THEN
				CALL copybatch(rec54&)  'DR02

				prt.batch% = -1: prt.costs% = 0
				thisbatch$ = MID$(DATE1$, 7, 2) + "0000"
				b$ = MID$(STR$(rec57%), 2)
				MID$(thisbatch$, 7 - LEN(b$), LEN(b$)) = b$
				GET #ch.hed%, rec54&, tnthed
				auto% = 0
				CALL custombatch(rec54&, thisltr!, updwn%, auto%)
				CALL alcbatch("update", rec57%, thisltr!, thisbatch$)
				IF updwn% = 13 THEN
					CALL doprint(rec54&, thisbatch$, thisltr!, prt.batch%, prt.costs%, updwn%)
				END IF
			END IF

	CASE 9: PRINT #99, CHR$(12);
	CASE 10: CLOSE : npgm$ = "MSREP03": CALL EXITPGM(npgm$): CHAIN npgm$
	CASE ELSE
	END SELECT

	GOTO start
ENDPGM:
	CLOSE
	CALL EXITPGM(apgm$): CHAIN apgm$

SUB alcbatch (gen$, rec57%, thisltr!, thisbatch$) STATIC
	DATE1$ = "  /  /  ": MID$(DATE1$, 1, 2) = MID$(DATE$, 4, 2):         MID$(DATE1$, 4, 2) = MID$(DATE$, 1, 2): MID$(DATE1$, 7, 2) = MID$(DATE$, 9, 2)
	IF gen$ = "Generate" THEN
		'>> Generate batch number
		btlast% = LOF(57) / LEN(batch)
		rec57% = btlast% + 1

		thisbatch$ = MID$(DATE1$, 7, 2) + "0000"
		b$ = MID$(STR$(rec57%), 2)
		MID$(thisbatch$, 7 - LEN(b$), LEN(b$)) = b$
		END IF

	IF gen$ = "update" THEN

	batch.datereq$ = datereq$

	batch.bno% = rec57%
	batch.year$ = MID$(DATE1$, 7, 2)
	batch.form$ = tnthed.tnta$
	batch.revision% = tnthed.revision%
	batch.SorW$ = tnthed.SorW$
	batch.class% = tnthed.class%
	batch.yld! = thisltr!
	batch.ayld! = 0
	batch.date$ = FNDY$(DATE1$)
	batch.name$ = tnthed.desc$
	batch.Resinvar! = 0
	batch.Solventvar! = 0
	batch.Thickenervar! = 0
	batch.Stainer1var! = 0
	batch.Stainer2var! = 0
	batch.hord% = hord%
	batch.thisbatch$ = thisbatch$
	batch.perltr = 0
	batch.dateform$ = MID$(tnthed.name$, 16, 8)
	IF NOT debug% THEN PUT #57, rec57%, batch
	END IF


END SUB

SUB browse38 (browse38.result%, updwn%)
	 CALL setup("BROWSE FILE")
	 COLOR 6, 0
	 LOCATE 4, 2: PRINT "SEQ. DESCRIPTION.............. SUPL. GRP A S/G.. SUPPLY COST NOTES............";
	 COLOR 2, 0
	 btm$ = "F1 - Exit.    F6 - Search again"
	 COLOR 0, 3: LOCATE 25, 1: PRINT btm$; : LOCATE 25, 71: PRINT CHR$(24); CHR$(25); "-Move"; : COLOR 2, 0

	 len.of.browse% = 19
	'***** Correct position - \
	 p = browse38.result%
	 IF p < 1 OR p > maxrmat% THEN p = 1
	k% = 1
	 LOCATE 5, 2: s% = p - 1: x = p: f% = p: GOTO 2540'* First time in list from saved number
2510
	IF f% < 1 OR f% > maxrmat% THEN f% = 1
	LOCATE 3, 2: PRINT "Current number.:"; f%;
	k% = 1
	LOCATE 3, 23: PRINT "Browse from number..> "; CHR$(FNH);
	z$ = ""
	CALL inpnew(z$, 205!, updwn%, "13,59-60,64,72,73,80,81")

	'>-- Search ----<
	start% = 1: IF updwn% = 64 THEN start% = last.found% + 1: z$ = last.search$
	z$ = UCASE$(z$)
	lenz% = LEN(z$)
	IF MID$(z$, 1, 1) >= "A" AND MID$(z$, 1, 1) <= "Z" THEN
	FOR j% = start% TO maxrmat%
		GET #38, j%, msrmat
		rmdesc$ = msrmat.Desc1$: IF RTRIM$(msrmat.Desc2$) > "" THEN rmdesc$ = msrmat.Desc2$
		IF msrmat.no% = j% AND MID$(msrmat.search$, 1, lenz%) = z$ THEN
			last.found% = j%: last.search$ = z$
			z$ = MID$(STR$(j%), 2)
			EXIT FOR
		END IF
		NEXT
		END IF

2540

	IF updwn% = 59 THEN skip$ = "Y": p = f%: p$ = MID$(STR$(p), 2): GOTO x.browse
	LOCATE 3, 44
	IF updwn% = 72 THEN GOSUB 2840: GOTO 2610  '***** UP arrow
	IF updwn% = 73 THEN GOSUB 2820: GOTO 2610  '***** PGUP
	IF updwn% = 80 THEN x = f% + 1: GOTO 2610   '***** DN arrow
	IF updwn% = 81 THEN z$ = ""                '***** PGDN
	IF updwn% = 13 THEN
		IF VAL(z$) <= 1 THEN x = x + 0: z$ = MID$(STR$(x), 2)
		END IF
	IF LEN(z$) = 0 THEN x = s% + 1: GOTO 2610
	zz$ = "     ": RSET zz$ = z$: x = VAL(zz$): IF x > maxrmat% THEN x = maxrmat%
2610 j% = -1: i% = 0
	 '
2630 j% = j% + 1
	 IF x + j% < 1 OR j% + x > maxrmat% THEN LOCATE , 2: PRINT CHR$(FNE); : GOTO 2770
	 IF k% = 1 THEN
		GET #38, j% + x, msrmat: k% = 0
		ELSE
		GET #38, , msrmat
		END IF

		rmdesc$ = msrmat.Desc1$: IF RTRIM$(msrmat.Desc2$) > "" THEN rmdesc$ = msrmat.Desc2$

	 IF msrmat.no% = 0 THEN 2630
	 LOCATE i% + 5, 2
	 PRINT USING "#### \                       \ \   \ ### \\#.### #####.###\ \\               \"; j% + x; rmdesc$; msrmat.search$; msrmat.Group%; msrmat.Active$; msrmat.sg; msrmat.PurCost; msrmat.PurUnit$; msrmat.Notes$
2770 i% = i% + 1: s% = j% + x: IF i% = 1 THEN f% = j% + x
	 IF i% < len.of.browse% THEN 2630
	 GOTO 2510
'//////////////////////////////////////////////////////////////////////
'>>>>> F I N D  F I R S T   R E C O R D   O F   R O L L B A C K
'//////////////////////////////////////////////////////////////////////
2820
	 x = f%: i% = 0
2840 x = x - 1
	 IF x < 1 THEN x = 1: GOTO 2890'BOF
	 GET #38, x, msrmat
	 rmdesc$ = msrmat.Desc1$: IF RTRIM$(msrmat.Desc2$) > "" THEN rmdesc$ = msrmat.Desc2$

	 IF msrmat.no = 0 THEN 2840
	 IF updwn% <> 72 OR updwn% <> 80 THEN
			i% = i% + 1: IF i% < len.of.browse% THEN 2840
	 END IF
2890
RETURN
x.browse:
	browse38.result% = f%

END SUB

SUB copybatch (rec54&)

	'>- Copy batch to a work file
	GET #ch.hed%, rec54&, tnthed
	IF tnthed.tnt% <> rec54& THEN GOTO x.copybatch
	FOR lin% = 1 TO 38
		startrec& = rec54& * 38 - 38 + 1
		drec& = startrec& + lin% - 1
		GET #ch.det%, drec&, tntdet
		tntdet.tnt& = lin%
		PUT #75, lin%, tntdet
		NEXT
x.copybatch:

END SUB

SUB copytnthed (rec54&, rec57%, auto%)

	GET #57, rec57%, batch
	GET #ch.hed%, rec54&, tnthed

					'copy header to batch
						batch.dateman$ = SPACE$(8)
						batch.manby$ = SPACE$(3)
					'Flags
						batch.fltnt$ = "P"
						batch.flstk$ = "N"
						IF auto% = 2 THEN batch.flstk$ = "P"
						IF auto% = 3 THEN batch.flstk$ = "R"
						batch.flqc$ = "P"

						'tnthed
						batch.yield = tnthed.yield
						batch.ltr = tnthed.ltr
						batch.kg = tnthed.kg
						batch.visc1h = tnthed.visc1h
						batch.visc1l = tnthed.visc1l
						batch.visc2h = tnthed.visc2h
						batch.visc2l = tnthed.visc2l
						batch.alccost = tnthed.alccost
						batch.rawcost = tnthed.rawcost
						batch.filter = tnthed.filter
						batch.grind = tnthed.grind
						batch.ph = tnthed.ph
						batch.sg = tnthed.sg
						batch.Vsol = tnthed.Vsol
						batch.Wsol = tnthed.Wsol
						batch.pvc = tnthed.pvc
						batch.pbr = tnthed.pbr
						batch.gloss = tnthed.gloss
						batch.Hazard$ = tnthed.Hazard$
						batch.asRmat% = tnthed.asRmat%
						batch.CostPer$ = tnthed.CostPer$
						batch.tnt% = tnthed.tnt%
PUT #57, rec57%, batch
END SUB

SUB custombatch (rec54&, thisltr!, updwn%, auto%)
	datereq$ = "  /  /  ": MID$(datereq$, 1, 2) = MID$(DATE$, 4, 2):          MID$(datereq$, 4, 2) = MID$(DATE$, 1, 2): MID$(datereq$, 7, 2) = MID$(DATE$, 9, 2)
	datereq$ = FNDY$(datereq$)
	CALL BOX(4, 10, 20, 70, 7, 0, 2)
	COLOR 10, 0
	LOCATE 5, 14: PRINT "              TANK AND YIELD SELECTION"
	COLOR 6, 0
	LOCATE 9, 14: PRINT "Code  ID.  Description                     Yield "
	COLOR 2, 0

	COLOR 6, 0: LOCATE 9, 17: PRINT "R/Mat Description.....": COLOR 2, 0


	FOR i% = 1 TO maxtankrrn%: tankrrn%(i%) = 0: NEXT
	'>-- Find the tank records
	n% = 0
	FOR lin% = 1 TO 38
		drec% = lin%
		GET #75, drec%, tntdet
		sel% = 0
		IF tntdet.rmat% > 0 AND tntdet.rmat% <= maxrmat% THEN
			GET #38, tntdet.rmat, msrmat
			rmdesc$ = msrmat.Desc1$: IF RTRIM$(msrmat.Desc2$) > "" THEN rmdesc$ = msrmat.Desc2$
			IF msrmat.UseUnit$ = "EQ" THEN sel% = -1
			IF msrmat.UseUnit$ = "TK" THEN sel% = -1
		END IF


		rm.tanksize!(lin%) = 0

		IF sel% THEN
			n% = n% + 1: IF n% > maxtankrrn% THEN n% = maxtankrrn%
			tankrrn%(n%) = drec%
			rm.tanksize!(lin%) = msrmat.Wtsolid
			rm.tankltmm!(lin%) = msrmat.Solidsg
			tntdet.qty = -1
			PUT #75, drec%, tntdet
			COLOR 2, 0

			LOCATE n% + 9, 17: PRINT USING "####| \                  \"; tntdet.rmat%; rmdesc$
			END IF
		NEXT

	'>-Show tank sizes
	thisltr! = tnthed.yield!
	thisltr$ = STR$(thisltr!)

custombatch50:
	COLOR 10, 0
	LOCATE 15, 17: PRINT "Batch print ": COLOR 2, 0
	LOCATE 17, 17: PRINT "Litres in this batch..> "
	LOCATE 18, 17: PRINT "Schedule for manuf by.>"
	LOCATE 19, 17: PRINT "Allocate Stock (Y/N/R)> "

	LOCATE 17, 40
	save.thisltr$ = thisltr$
	IF NOT auto% THEN
		CALL inpnew(thisltr$, 5.1, updwn%, "13,59,60")
	END IF
	thisltr! = VAL(thisltr$): CALL ROUND(thisltr!, 1.5)
	IF updwn% = 59 THEN GOTO x.custombatch
	IF updwn% = 13 AND VAL(save.thisltr$) <> VAL(thisltr$) THEN updwn% = 60
	IF thisltr! <= 0 THEN GOTO x.custombatch
	IF tnthed.yield! <= 0 THEN GOTO x.custombatch

	'Calcultate the multiplier for this batch size
	Mult# = thisltr! / tnthed.yield!
	batchltr! = tnthed.ltr! * Mult#
	'>-- Change the tank records
	IF updwn% = 60 THEN
	lin% = 1
	DO
		IF lin% < 1 THEN lin% = 1
		IF lin% > n% THEN lin% = n%

		drec% = tankrrn%(lin%)

		GET #75, drec%, tntdet
		IF tntdet.rmat% > 0 AND tntdet.rmat% < maxrmat% THEN
			GET #38, tntdet.rmat, msrmat
			rmdesc$ = msrmat.Desc1$: IF RTRIM$(msrmat.Desc2$) > "" THEN rmdesc$ = msrmat.Desc2$
		END IF
		LOCATE lin% + 9, 17: PRINT USING "####| \                  \"; tntdet.rmat%; rmdesc$

		LOCATE lin% + 9, 17
		a$ = STR$(tntdet.rmat)
		CALL SNDMSG("F6 - Browse")
		CALL inpnew(a$, 4!, updwn%, "13,59,60,64,72,80")
		CALL SNDMSG("")
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
		IF a! <> tntdet.rmat AND a! > 0 AND a! < maxrmat% THEN
			tntdet.rmat = a!
			IF tntdet.rmat < 1 OR tntdet.rmat > maxrmat% THEN tntdet.rmat = 1
			GET #38, tntdet.rmat, msrmat
			rmdesc$ = msrmat.Desc1$: IF RTRIM$(msrmat.Desc2$) > "" THEN rmdesc$ = msrmat.Desc2$
			rm.tanksize!(drec%) = msrmat.Wtsolid
			rm.tankltmm!(drec%) = msrmat.Solidsg
			PUT #75, drec%, tntdet
		END IF
			
		LOOP UNTIL lin% > n%
		IF updwn% = 59 THEN GOTO x.custombatch
		GOTO custombatch50
		END IF


	'>-- Recalc the height in tank
		run.ltr! = 0
		FOR seq% = 1 TO 38
			drec% = seq%
			GET #75, drec%, tntdet
			save.cmtqty! = tntdet.cmtqty!
			IF tntdet.rmat% > 0 AND tntdet.rmat% < maxrmat% THEN
			GET #38, tntdet.rmat, msrmat
			rmdesc$ = msrmat.Desc1$: IF RTRIM$(msrmat.Desc2$) > "" THEN rmdesc$ = msrmat.Desc2$
		END IF


		'>-Running total of litres
			ltr! = 0
			IF msrmat.UseUnit$ = "LT" THEN
				ltr! = tntdet.qty!
			END IF
			IF msrmat.UseUnit$ = "KG" THEN
				ltr! = tntdet.qty! * msrmat.sg!
			END IF

		 ltr! = tntdet.qty! * msrmat.sg!
		 kg! = 0
		 sg! = msrmat.sg!: IF sg! = 0 THEN sg! = .0000001
		 IF msrmat.UseUnit$ = "KG" THEN ltr! = tntdet.qty! / sg!: kg! = tntdet.qty!
		 IF msrmat.UseUnit$ = "GM" THEN ltr! = tntdet.qty! / sg! / 1000: kg! = tntdet.qty! / 1000
		 IF msrmat.UseUnit$ = "LT" THEN ltr! = tntdet.qty!: kg! = tntdet.qty! * sg!
		 IF msrmat.UseUnit$ = "ML" THEN ltr! = tntdet.qty! / 1000: kg! = tntdet.qty! * sg! / 1000
		 IF msrmat.UseUnit$ = "TK" THEN ltr! = -1: kg! = 0
		 IF msrmat.UseUnit$ = "EQ" THEN ltr! = -1: kg! = 0
		 IF msrmat.UseUnit$ = "EA" THEN ltr! = 0: kg! = 0

		 IF ltr = -1 THEN run.ltr! = 0
		 SELECT CASE msrmat.UseUnit$
		 CASE "KG", "LT", "GM", "MT", "OZ", "ML": ltr! = ltr! * Mult#
		 CASE ELSE
		 END SELECT

		 work! = ltr!
		 IF work! < .1 THEN work! = 0
		 run.ltr! = run.ltr! + work!
		 IF run.ltr! < .1 THEN run.ltr! = 0
		 Ltrs.in! = run.ltr!: CALL ROUND(Ltrs.in!, 2.5)

		'PRINT USING "####|&|#####.#| ### ###            Sg##.# R.LTr ####.#"; Tntdet.rmat%; rmdesc$; Tntdet.qty!; Tntdet.cmt; Tntdet.cmtqty; msrmat.sg!; run.ltr!

		IF tntdet.cmt = 99 THEN
			Ltrs.in! = run.ltr!
			CALL height.in.tank(updwn%, seq%, Ltrs.in!, Height.from.btm!, Height.from.top!)
			IF updwn% = 13 THEN tntdet.cmtqty = Height.from.top!
		END IF

		IF tntdet.cmt = 98 THEN
			Ltrs.in! = ltr!'Calc height on side
			CALL height.in.tank(updwn%, seq%, Ltrs.in!, Height.from.btm!, Height.from.top!)
			IF updwn% = 13 THEN tntdet.cmtqty! = Height.from.btm!
		END IF


		IF tntdet.cmtqty! <> save.cmtqty! THEN
			PUT #75, drec%, tntdet
		END IF

		NEXT

custombatch.sched:
	IF NOT auto% THEN
		LOCATE 18, 40
		datereq$ = FNDYY$(datereq$)
		CALL inpnew(datereq$, 100!, updwn%, "13,60")
		datereq$ = FNDY$(datereq$)
		IF updwn% = 60 THEN GOTO custombatch50
		
	END IF

custombatch.yn:
	IF NOT auto% THEN
		LOCATE 19, 40
		yn$ = "Y"
		CALL inpnew(yn$, 101!, updwn%, "13,60")
		IF updwn% = 60 THEN GOTO custombatch.sched
		IF updwn% = 13 THEN
			IF UCASE$(yn$) = "Y" THEN
				alprod% = -1
				CALL mline
				auto% = 2
				GOTO x.custombatch
			END IF
			IF UCASE$(yn$) = "N" THEN
				alprod% = 0
				GOTO x.custombatch
			END IF
			IF UCASE$(yn$) = "R" THEN
				alprod% = 0
				auto% = 3
				GOTO x.custombatch
			END IF

		END IF
		GOTO custombatch.yn
	END IF

x.custombatch:
END SUB

SUB cvt.tnt (tnt$, tnt%, tntf$)
	tnt$ = UCASE$(tnt$)
	tnt$ = "    " + tnt$: tnt$ = RIGHT$(tnt$, 4)
	digit% = 4
	SELECT CASE MID$(tnt$, digit%, 1)
	CASE "A" TO "Z"
	'CASE "T"
	CASE "0" TO "9":
		IF mode$ = "Tints" THEN
			tnt$ = tnt$ + "T": tnt$ = RIGHT$(tnt$, 4)
		ELSE
			tnt$ = tnt$ + "A": tnt$ = RIGHT$(tnt$, 4)
		END IF
	CASE ELSE: MID$(tnt$, digit%, 1) = "A"
	END SELECT


	FOR digit% = 1 TO 3
	IF MID$(tnt$, digit%, 1) < "0" OR MID$(tnt$, digit%, 1) > "9" THEN MID$(tnt$, digit%, 1) = "0"
	NEXT


	tnt% = VAL(MID$(tnt$, 1, 3))
	tntf$ = RIGHT$(tnt$, 1)

END SUB

SUB doprint (rec&, thisbatch$, thisltr!, prt.batch%, prt.costs%, updwn%) STATIC
	OPEN "msclass.dat" FOR RANDOM SHARED AS #29 LEN = 57
	OPEN ".\batches\B" + thisbatch$ + ".BCH" FOR RANDOM SHARED AS #98 LEN = 32
	IF tnthed.tnt% <> rec& THEN GOTO x.doprint
	COLOR 2, 0
	LOCATE 17, 17: PRINT "Printing....      "; tnthed.tnta$

	DATE1$ = "  /  /  ": MID$(DATE1$, 1, 2) = MID$(DATE$, 4, 2):         MID$(DATE1$, 4, 2) = MID$(DATE$, 1, 2): MID$(DATE1$, 7, 2) = MID$(DATE$, 9, 2)

	'Calcultate the multiplier for this batch size
	Mult# = thisltr! / tnthed.yield!


	 IF tnthed.class% < 1 OR tnthed.class% > 99 THEN
		LSET cldesc$ = "** NO CLASS **"
		ELSE
		GET #29, tnthed.class%, msclass
		cldesc$ = LEFT$(msclass.cldesc$, 15)
		END IF

	'-<<< Actual print >>>-
	IF thisbatch$ > "" THEN
		STDOUT$ = "j:\tpmanuf\batches\b" + LTRIM$(RTRIM$(thisbatch$)) + ".PRN"
		'STDOUT$ = ".\Batches\B" + LTRIM$(RTRIM$(thisbatch$)) + ".PRN"
	ELSE
		STDOUT$ = "c:\tpexe\BR" + LTRIM$(tnthed.tnta$) + ".PRN"
	END IF
	OPEN STDOUT$ FOR OUTPUT AS #99

	PRINT #99, TAB(1); CHR$(14); msmisc.cc$
	'PRINT #99, " #msbch01p"; TAB(71); DATE1$
	 PRINT #99, ""
	PRINT #99, TAB(10); CHR$(14); tnthed.desc$
	PRINT #99, "ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿"
	IF thisltr! < 100 THEN
	PRINT #99, USING "³Formula \   \  Rev. ##  ³ Class \      \    ³          Custom Yield:##.## Lt.³"; tnthed.tnta$; tnthed.revision%; cldesc$; thisltr!
	ELSE
	PRINT #99, USING "³Formula \   \  Rev. ##  ³ Class \      \    ³          Custom Yield:##### Lt.³"; tnthed.tnta$; tnthed.revision%; cldesc$; thisltr!
	END IF
	IF prt.batch% THEN
	PRINT #99, "ÃÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅÄÄÄÄÄÄÄÂÄÄÄÂÄÄÄÄÄÄÄÅÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ´"
	PRINT #99, "³ COMPONENT              ³ LITRE ³HAZ³ KILO  ³CHECK³ INSTRUCTIONS             ³"
	PRINT #99, "ÀÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÙ"
	ELSE
	PRINT #99, "ÃÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÂÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄ´"
	PRINT #99, "³No. ³ COMPONENT                ³ Lt/Kg.³Ut³ INSTRUCTIONS              ³ Cost.³"
	PRINT #99, "ÀÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÙ"
	END IF
	tot.amt! = 0

	FOR lin% = 1 TO 38
		startrec& = rec& * 38 - 38 + 1
		startrec& = 1  'Only for the work file.
		drec& = startrec& + lin% - 1
		'push custombatch size to work file
		GET #75, drec&, tntdet
		tntdet.qty! = tntdet.qty! * Mult#
		PUT #98, drec&, tntdet

		GET #75, drec&, tntdet
		
		IF tntdet.tnt& <> drec% AND 1 = 0 THEN
			tntdet.tnt& = 0
			tntdet.rmat% = 0
			tntdet.qty! = 0
			tntdet.cmt% = 0
			tntdet.cmtqty! = 0
			PUT #75, drec&, tntdet
		END IF

		IF tntdet.cmt% > 0 AND tntdet.cmt% < 100 THEN
			GET #30, tntdet.cmt%, mscomt
		ELSE
			mscomt.spk$ = SPACE$(22)
		END IF

		IF tntdet.rmat% > 0 AND tntdet.rmat% < maxrmat% THEN
			GET #38, tntdet.rmat, msrmat
			rmdesc$ = msrmat.Desc1$: IF RTRIM$(msrmat.Desc2$) > "" THEN rmdesc$ = msrmat.Desc2$
		END IF

		printit% = 0
		IF tntdet.rmat% > 0 OR tntdet.qty! > 0 THEN printit% = -1
		IF tntdet.rmat% > 0 AND msrmat.UseUnit$ = "EQ" THEN printit% = -1
		IF tntdet.rmat% > 0 AND msrmat.UseUnit$ = "TK" THEN printit% = -1

		Thisqty! = ABS(tntdet.qty!)

		IF printit% THEN
			SELECT CASE msrmat.UseUnit$
			CASE "KG", "LT", "GM", "MT", "OZ", "ML": Thisqty! = Thisqty! * Mult#
			CASE ELSE
			END SELECT


			sg! = msrmat.sg!: IF sg! = 0 THEN sg! = .0000001
			IF msrmat.UseUnit$ = "KG" THEN ltr! = Thisqty! / sg!
			IF msrmat.UseUnit$ = "GM" THEN ltr! = Thisqty! / sg! / 1000
			IF msrmat.UseUnit$ = "LT" THEN ltr! = Thisqty!
			IF msrmat.UseUnit$ = "OZ" THEN ltr! = Thisqty! / 28.413
			IF msrmat.UseUnit$ = "ML" THEN ltr! = Thisqty! / 1000
			IF msrmat.UseUnit$ = "TK" THEN ltr! = 0
			IF msrmat.UseUnit$ = "EQ" THEN ltr! = 0
			IF msrmat.UseUnit$ = "EA" THEN ltr! = 0
			CALL ROUND(ltr!, 1.5)

			IF prt.batch% THEN
				SELECT CASE msrmat.UseUnit$
				CASE "EQ": PRINT #99, USING "\                       \ \     \  !  \     \       "; msrmat.Desc2$; "       "; "            "; "       ";
				CASE "EA": PRINT #99, USING "\                       \|\     \| ! |#######|     |"; msrmat.Desc2$; "       "; msrmat.Hazard$; Thisqty!;
				CASE "MN": PRINT #99, USING "\                       \|#######  !  \     \|     |"; msrmat.Desc2$; Thisqty!; "            "; "minutes";
				CASE "HR": PRINT #99, USING "\                       \|#######  !  \     \|     |"; msrmat.Desc2$; Thisqty!; "            "; "hours  ";
				CASE "LT": PRINT #99, USING "\                       \|####.##| ! |\     \|     |"; msrmat.Desc2$; Thisqty!; msrmat.Hazard$; "       ";
				CASE ELSE: PRINT #99, USING "\                       \|\     \| ! |####.##|     |"; msrmat.Desc2$; "       "; msrmat.Hazard$; Thisqty!;
				END SELECT
			END IF

			IF NOT prt.batch% THEN
				SELECT CASE msrmat.UseUnit$
				CASE "EQ": PRINT #99, USING "#### | \                       \ \     \     "; tnthed.tnt%; rmdesc$; " ";
				CASE ELSE: PRINT #99, USING "#### | \                       \|####.## \\  "; tntdet.rmat%; rmdesc$; Thisqty!; msrmat.UseUnit$;
				END SELECT
			END IF

			IF tntdet.cmt% = 0 THEN
				PRINT #99, STRING$(27, " ");
			ELSE
				SELECT CASE tntdet.cmtqty!
				CASE IS < 1: PRINT #99, USING "     &"; mscomt.spk$;
				CASE ELSE: PRINT #99, USING "#### &"; tntdet.cmtqty!; mscomt.spk$;
				END SELECT
			END IF

			IF prt.costs% THEN
				lin.amt! = msrmat.UseCost! * Thisqty!: tot.amt! = tot.amt! + lin.amt!
				PRINT #99, TAB(73); : PRINT #99, USING "####.##"; lin.amt!;
			END IF

		END IF
		PRINT #99, ""

		'>-Update raw mat. Stock
		IF prt.batch% <> 0 THEN
			IF tntdet.rmat% >= 1 AND tntdet.rmat% <= maxrmat% THEN '1=Hydroxinol - Don't update stock
				SELECT CASE msrmat.UseUnit$
				CASE "EQ", "EA", "MN", "HR"
				CASE ELSE
					GET #38, tntdet.rmat, msrmat
					'msrmat.soh = msrmat.soh - Thisqty!
					msrmat.sip = msrmat.sip + Thisqty! 'For production
					PUT #38, tntdet.rmat, msrmat
				END SELECT
			END IF
		END IF

	NEXT


	a$ = SPACE$(5): LSET a$ = STR$(CVI(msmisc.bchno$) + CVI(msmisc.bchoff$))
	wrk.fgwp! = tnthed.sg! / 1000:
	IF wrk.fgwp! > 9 THEN wrk.fgwp! = 9!
	IF wrk.fgwp! < 0 THEN wrk.fgwp! = 0!


	IF fvish < 10 THEN
		prtvisl$ = STR$(fvisl!)
		prtvish$ = STR$(fvish!)
	ELSE
		prtvisl$ = STR$(fvisl!)
		prtvish$ = STR$(fvish!)
	END IF



	text1$ = "                    "
	text2$ = "                 "
	text3$ = "                      "

	IF tnthed.visc1l! > 0 AND tnthed.visc1l < 15 THEN
		text1$ = "R/T   " + format$(tnthed.visc1l!, "##.#") + "-" + format$(tnthed.visc1h!, "##.#") + " =     "
	END IF

	IF tnthed.visc1l! > 10 THEN
		text1$ = "F/CUP " + format$(tnthed.visc1l!, "###") + "-" + format$(tnthed.visc1h!, "###") + " =     "
	END IF

	IF tnthed.ph! > 0 THEN
		text2$ = "PH.. >" + format$(tnthed.ph!, "#.#") + " =     "
	END IF

	IF tnthed.grind! > 0 THEN
		text2$ = "HEG. <" + format$(tnthed.grind!, "#.#") + " =     "
	END IF

	IF tnthed.visc2l! > 0 THEN
		text3$ = "Cn & Pl " + format$(tnthed.visc2l!, "#.#") + "-" + format$(tnthed.visc2h!, "#.#") + " =     "
	END IF

	PRINT #99, USING "ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄ!"; "¿"
	PRINT #99, USING "³\                  \³\               \³\                     \³Iss. \      \ !"; text1$; text2$; text3$; DATE1$; "³"
	PRINT #99, USING "ÃÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÁÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÅÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÅÄÄÄÄÄÄÄÄÄÄÄÄÄÄ!"; "´"
	PRINT #99, USING "³COLOUR =      ³SHEEN =    ³DRY.. =    ³FILTER ### ³ S/G #.### ³Date.         !"; tnthed.filter%; tnthed.sg!; "³"


	IF prt.batch% THEN

	IF alprod% = -1 THEN
		PRINT #99, USING "ÃÄÄÄÄÄÄÄÄÄÄÂÄÄÄÁÄÂÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÁÄÄÂÄÄÄÄÄÄÂÄÁÄÄÄÄÂÄÄÄÄÄÄÄÄÄ!"; "´"

		PRINT #99, USING "³ Item     ³Units³ Name                     Colour    ³Alloc.³ Fill ³ BATCH.  !"; "³"
		PRINT #99, USING "ÃÄÄÄÄÄÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÅÄÄÄÄÄÄÅÄÄÄÄÄÄ´ \    \  !"; thisbatch$; "³"

		FOR L% = 1 TO 8
			IF VAL(in$(L%, 4)) <> 0 OR VAL(in$(L%, 14)) <> 0 THEN
				IF L% = 1 THEN PRINT #99, USING "³ ####     ³\ \\\³\                                  \³ #### ³      ÃÄÄÄÄÄÄÄÄÄ!"; VAL(in$(L%, 4)); in$(L%, 2); in$(L%, 3); in$(L%, 5); VAL(in$(L%, 1)); "´"
				IF L% = 2 THEN PRINT #99, USING "³ ####     ³\ \\\³\                                  \³ #### ³      ³OPERATOR.!"; VAL(in$(L%, 4)); in$(L%, 2); in$(L%, 3); in$(L%, 5); VAL(in$(L%, 1)); "³"
				IF L% > 2 THEN PRINT #99, USING "³ ####     ³\ \\\³\                                  \³ #### ³      ³         !"; VAL(in$(L%, 4)); in$(L%, 2); in$(L%, 3); in$(L%, 5); VAL(in$(L%, 1)); "³"
			ELSE
				PRINT #99, USING "³          ³     ³                                    ³      ³      ³         !"; "³"
			END IF
	 NEXT
		PRINT #99, USING "ÀÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÁÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄ!"; "Ù"


		ELSE

		PRINT #99, USING "ÃÄÄÄÄÄÄÄÄÂÄÄÄÄÄÅÄÄÄÄÄÂÄÄÄÄÄÅÄÄÄÄÄÂÄÄÄÄÄÅÄÄÄÄÄÂÄÄÄÄÄÅÄÄÄÄÄÂÄÄÄÄÄÅÄÄÄÄÄÂÄÄÄÄÄÄÄÄ!"; "´"
		PRINT #99, USING "³Pack    ³ 20L ³ 10L ³  4L ³  2L ³  1L ³ .5L ³.25L ³300g ³900g ³Bulk ³ BATCH. !"; "³"
		PRINT #99, USING "ÃÄÄÄÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄ´ \    \ !"; thisbatch$; "³"
		PRINT #99, USING "³Ordered ³     ³     ³     ³     ³     ³     ³     ³     ³     ³     ³        !"; "³"
		PRINT #99, USING "ÃÄÄÄÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÄÄÄ!"; "´"
		PRINT #99, USING "³Actual  ³     ³     ³     ³     ³     ³     ³     ³     ³     ³     ³ TOTAL. !"; "³"
		PRINT #99, USING "ÃÄÄÄÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄÅÄÄÄÄÄ´        !"; "³"
		PRINT #99, USING "³Litres  ³     ³     ³     ³     ³     ³     ³     ³     ³     ³     ³        !"; "³"
		PRINT #99, USING "ÀÄÄÄÄÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÄÄÄÄ!"; "Ù"
		PRINT #99, " From Top .0500 .0400 .0350 .0300 .0200 .0150 .0100 ***** ***** ***** ******** "
	 END IF

	
	ELSE
	PRINT #99, USING "ÀÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄ!"; "Ù"
	END IF

	IF prt.costs% THEN
	PRINT #99, USING "                  ÚÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄ¿!"; ""
	PRINT #99, USING "                  ³ Total cost of formula............. #####.## ³"; tot.amt!
	PRINT #99, USING "                  ³ Total ammount of expected error... #####.## ³"; (tot.amt! * ff!)
	PRINT #99, USING "                  ³ Total cost of formula with error.. #####.## ³"; tot.amt! + (tot.amt! * ff!)
	PRINT #99, USING "                  ³ Cost per Litre.................... #####.## ³"; tnthed.rawcost!
	PRINT #99, USING "                  ÀÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÙ!"; ""
	END IF

	PRINT #99, CHR$(12);
	CLOSE #99
	shella$ = "type " + STDOUT$ + " > lpt1"
	SHELL shella$



x.doprint:

CLOSE #29
CLOSE #98
END SUB

FUNCTION format$ (VALUE!, definition$) STATIC
	dp% = 0

	'>- Find out how many decimal places,neg etc... -<
	work$ = STR$(VALUE!)
	edtcde$ = " ": dp% = 0
	x% = INSTR(definition$, ".")
	IF x% > 0 THEN
		FOR i% = x% TO LEN(definition$)
			IF MID$(definition$, i%, 1) = "b" THEN MID$(definition$, i%, 1) = "#": edtcde$ = "b"
			IF MID$(definition$, i%, 1) = "#" THEN dp% = dp% + 1
			NEXT
		x% = INSTR(work$, ".")
		IF x% = 0 THEN work$ = work$ + "."
		work$ = work$ + STRING$(dp%, "0")
		x% = INSTR(work$, ".")
		work$ = MID$(work$, 1, x% + dp%)
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
	w% = LEN(work$)

	FOR i% = LEN(defwork$) TO 1 STEP -1
		IF w% < 1 THEN EXIT FOR
		SELECT CASE MID$(defwork$, i%, 1)
		CASE "#": MID$(defwork$, i%, 1) = MID$(work$, w%, 1): w% = w% - 1
		CASE "$": MID$(defwork$, i%, 1) = MID$(work$, w%, 1): w% = w% - 1
		CASE ",": IF MID$(work$, w%, 1) = "d" THEN MID$(defwork$, i%, 1) = "#": i% = i% + 1
		CASE ".": w% = w% - 1
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

SUB getform (opt%, form$, rec54&, updwn%)
	Y0% = 19: IF updwn% = -1 THEN Y0% = 20

	LOCATE Y0%, 23: PRINT "Enter formula number..>"
	LOCATE Y0%, 46
	CALL inpnew(form$, 3!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.getform
	IF updwn% = 60 THEN GOTO x.getform
	CALL cvt.tnt(form$, f%, f1$)


	FOR i% = 1 TO maxtnt%
		IF form$ = tnthedx.tnta$(i%) THEN found% = -1: EXIT FOR
	NEXT
	IF NOT found% THEN
		msg$ = "Formula " + form$ + " not found"
		updwn% = 60
		GOTO x.getform
	END IF

	rec54& = tnthedx.rrn%(i%)
	IF rec54& < 1 OR rec54& > maxtnt% THEN
		msg$ = "Record for " + form$ + " not valid? Rebuild index!"
		updwn% = 60
		GOTO x.getform
	END IF

	'- In a range does not select A-F
	IF opt% = 4 GOTO x.getform
	IF opt% = 5 GOTO x.getform

	CALL BOX(4, 10, 20, 70, 7, 0, 2)
	COLOR 10, 0
	LOCATE 5, 14: PRINT "                 FORMULA SELECTION"
	COLOR 6, 0
	LOCATE 9, 14: PRINT "Code  ID.  Description                     Yield "
	COLOR 2, 0
	s% = i%
	lin% = 9
	FOR i% = s% TO s% + 9
		rec54& = tnthedx.rrn%(i%)
		IF rec54& < 1 OR rec54& > maxtnt% THEN rec54& = 1
		GET #ch.hed%, rec54&, tnthed
		IF MID$(tnthed.tnta$, 1, 3) <> MID$(form$, 1, 3) THEN EXIT FOR

		lin% = lin% + 1
		COLOR 2, 0
		LOCATE lin%, 14
		PRINT USING " !    \  \-\                         \    ##,###"; MID$(tnthed.tnta$, 4, 1); tnthed.tnta$; tnthed.desc$; tnthed.yield
	NEXT

	'lin% = lin% + 1
	'LOCATE lin%, 14
	'PRINT USING " X    \ \X-Custom batch.                        "; MID$(form$, 1, 3)

	rec54& = tnthedx.rrn%(1)
	IF rec54& < 1 OR rec54& > maxtnt% THEN rec54& = 1
	GET #ch.hed%, rec54&, tnthed

	LOCATE 19, 14: PRINT "Select batch (A,B,C etc)....>"
	IF mode$ = "Tints" THEN LOCATE 19, 14: PRINT "Select batch (T Only).......>"

	LOCATE 17, 23: PRINT USING "& & & & & &"; MID$(tnthed.name$, 1, 4); MID$(tnthed.name$, 5, 4); MID$(tnthed.name$, 9, 4); MID$(tnthed.name$, 13, 4); MID$(tnthed.name$, 17, 4); MID$(tnthed.name$, 21, 4)
	COLOR 4, 0
	LOCATE 17, 53: PRINT USING "&"; MID$(tnthed.name$, 25, 5)

	LOCATE 19, 43
	COLOR 2, 0
	a$ = "A"
	IF mode$ = "Tints" THEN a$ = "T"
	CALL inpnew(a$, 101!, updwn%, "13,59")
	IF mode$ = "Tints" THEN a$ = "T"
	a$ = UCASE$(a$)
	IF updwn% = 59 THEN GOTO x.getform
	IF updwn% = 60 THEN GOTO x.getform

	'>--
	MID$(form$, 4, 1) = a$
	found% = 0
	FOR i% = 1 TO maxtnt%
		IF form$ = tnthedx.tnta$(i%) THEN found% = -1: EXIT FOR
	NEXT
	IF NOT found% THEN
		msg$ = "Formula " + form$ + " not found"
		updwn% = 60
		GOTO x.getform
	END IF

	rec54& = tnthedx.rrn%(i%)
	IF rec54& < 1 OR rec54& > maxtnt% THEN
		msg$ = "Record for " + form$ + " not valid? Rebuild index!"
		updwn% = 60
		GOTO x.getform
		END IF

x.getform:
END SUB

SUB height.in.tank (updwn%, seq%, Ltrs.in!, Height.from.btm!, Height.from.top!) STATIC
'$INCLUDE: '\tpmanuf\src\MSTANK.INC'
END SUB

SUB reallocate (rec57%, rec54&)
	b$ = ""
	LOCATE 19, 23: PRINT "Enter batch number..>"
	LOCATE 19, 46
	CALL inpnew(b$, 104!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.reallocate
	IF updwn% = 60 THEN GOTO x.reallocate
	rec57% = VAL(b$)
	IF rec57% < 1 OR rec57% > 9999 THEN GOTO x.reallocate
	GET #57, rec57%, batch
	LOCATE 18, 8: PRINT USING "Batch #####:  \   \ ## &   #### LT #### LT"; batch.bno%; batch.form$; batch.revision%; batch.name$; batch.yld!; batch.ayld!;

	IF MID$(batch.form$, 4, 1) = "T" AND mode$ <> "Tints" THEN
		msg$ = "The formula in this batch is a Tint.  Hit F5 and try again."
		GOTO x.reallocate
	END IF
	IF MID$(batch.form$, 4, 1) <> "T" AND mode$ = "Tints" THEN
		msg$ = "The formula in this batch not is a Tint.  Hit F5 and try again."
		GOTO x.reallocate
	END IF

	opt% = 7
	CALL getform(opt%, form$, rec54&, updwn%)
	IF updwn% = 59 THEN GOTO x.reallocate
	IF updwn% = 60 THEN GOTO x.reallocate

	GET #57, rec57%, batch
	CALL ReturntoStock(batch.form$, batch.yld!)
	msg$ = "Batch" + STR$(batch.bno%) + ":  Formula " + batch.form$ + " changed to " + form$

	DATE1$ = "  /  /  ": MID$(DATE1$, 1, 2) = MID$(DATE$, 4, 2):         MID$(DATE1$, 4, 2) = MID$(DATE$, 1, 2): MID$(DATE1$, 7, 2) = MID$(DATE$, 9, 2)
	thisbatch$ = MID$(DATE1$, 7, 2) + "0000"
	b$ = MID$(STR$(rec57%), 2)
	MID$(thisbatch$, 7 - LEN(b$), LEN(b$)) = b$

	batch.form$ = form$
	GET #ch.hed%, rec54&, tnthed
	thisltr! = tnthed.yield!
	CALL alcbatch("update", rec57%, thisltr!, thisbatch$)
x.reallocate:
END SUB

SUB reprint (rec57%, rec54&)
	b$ = ""
	LOCATE 19, 23: PRINT "Enter batch number..>"
	LOCATE 19, 46
	CALL inpnew(b$, 104!, updwn%, "13,59-60")
	IF updwn% = 59 THEN GOTO x.reprint
	IF updwn% = 60 THEN GOTO x.reprint
	rec57% = VAL(b$)
	IF rec57% < 1 OR rec57% > 9999 THEN GOTO x.reprint
	GET #57, rec57%, batch
	LOCATE 18, 8: PRINT USING "Batch #####:  \   \ ## &   #### LT"; batch.bno%; batch.form$; batch.revision%; batch.name$; batch.ayld!;

	IF MID$(batch.form$, 4, 1) = "T" AND mode$ <> "Tints" THEN
		msg$ = "The formula in this batch is a Tint.  Hit F5 and try again."
		GOTO x.reprint
	END IF
	IF MID$(batch.form$, 4, 1) <> "T" AND mode$ = "Tints" THEN
		msg$ = "The formula in this batch not is a Tint.  Hit F5 and try again."
		GOTO x.reprint
	END IF

	y$ = "Y"
	DO
		COLOR 2, 0
		LOCATE 21, 23: PRINT "Continue..>"
		LOCATE 21, 34
		CALL inpnew(y$, 101!, updwn%, "13,59-60")
		y$ = UCASE$(y$)
		IF updwn% = 59 THEN GOTO x.reprint
		IF updwn% = 60 THEN GOTO x.reprint
	LOOP UNTIL y$ = "Y" OR y$ = "N"

	IF y$ = "Y" THEN
		thisbatch$ = batch.year$ + "0000"
		b$ = MID$(STR$(erec57%), 2)
		MID$(thisbatch$, 7 - LEN(b$), LEN(b$)) = b$
		IF DIR$("j:\tpmanuf\batches\B" + LTRIM$(RTRIM$(batch.thisbatch$)) + ".PRN") <> "" THEN
			shella$ = "COPY j:\tpmanuf\batches\B" + LTRIM$(RTRIM$(batch.thisbatch$)) + ".PRN LPT1"
			SHELL shella$
		ELSE
			COLOR 4
			LOCATE 21, 10: PRINT "Batch file not found. Nothing printed."
		END IF
	END IF

x.reprint:
END SUB

SUB ReturntoStock (form$, thisltr!)

	CALL cvt.tnt(form$, f%, f1$)
	found% = 0
	FOR i% = 1 TO maxtnt%
		IF form$ = tnthedx.tnta$(i%) THEN found% = -1: EXIT FOR
	NEXT
	IF NOT found% THEN GOTO x.returntostock
	CALL SNDMSG("Returning " + form$ + " to stock")
	atimer! = TIMER

	rec54& = tnthedx.rrn%(i%)
	GET #ch.hed%, rec54&, tnthed
	IF tnthed.tnt% <> rec54& THEN GOTO x.returntostock
	IF tnthed.yield! = 0 THEN GOTO x.returntostock
	'tnthed.

	'Calcultate the multiplier for this batch size
	Mult# = thisltr! / tnthed.yield!

	FOR lin% = 1 TO 38
		startrec54& = rec54& * 38 - 38 + 1
		drec54& = startrec54& + lin% - 1
		GET #ch.det%, drec54&, tntdet

		IF tntdet.rmat% >= 1 AND tntdet.rmat% <= maxrmat% THEN '1=Hydroxinol - Don't update stock
			GET #38, tntdet.rmat, msrmat

			Thisqty! = ABS(tntdet.qty!)
			SELECT CASE msrmat.UseUnit$
			CASE "KG", "LT", "GM", "MT", "OZ", "ML": Thisqty! = Thisqty! * Mult#
			CASE ELSE
			END SELECT

			SELECT CASE msrmat.UseUnit$
			CASE "EQ", "EA", "MN", "HR"
			CASE ELSE
				GET #38, tntdet.rmat, msrmat
				msrmat.soh = msrmat.soh + Thisqty!
				PUT #38, tntdet.rmat, msrmat
			END SELECT

		END IF

	NEXT

	DO WHILE ABS(TIMER - atimer!) < 1: LOOP
	CALL SNDMSG("")

x.returntostock:
END SUB

SUB setchannel
'$INCLUDE: '\tpmanuf\src\tntfiles.INC'
END SUB

