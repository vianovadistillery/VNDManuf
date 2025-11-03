DECLARE SUB accbrowse (rec%)
DECLARE SUB accbrowseo (rec%)
DECLARE SUB add.up.order (tot.ltact!, tot.ord!, tot.ext!)
DECLARE SUB browse30 (browse30.result%, updwn%)
DECLARE SUB browse38i (browse38.result%)
DECLARE SUB browse38 (browse38.result%, updwn%)
DECLARE SUB browse57 (browse57.result%, updwn%)
DECLARE SUB browse.idx (firstonscreen%, ch1%, ch2%)
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
DECLARE SUB prtstk (totltr!)
DECLARE SUB ReturntoStock (form$, thisltr!)
DECLARE SUB resins (startsearch%, seq%, updwn%)
DECLARE SUB rightprice (price!)
DECLARE SUB save.lines (rec26%, auto%)
DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB selectfile (filename$, updwn%)
DECLARE SUB UpdateOrder (hord%, updwn%)
DECLARE FUNCTION format$ (VALUE!, definition$)
'///////////////////////////////////////////////////////////////////////////
'>>>>>>>>>
'///////////////////////////////////////////////////////////////////////////

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
	DIM SHARED c%(8), in$(maxlines%, 16), rrn%(maxlines%)
	'1=qty%,2=size,3=unit,4=itm,5=desc,6=price,7=SOH,8=ext
	'9=tax flag,10=ordqty%,11=Invqty,12=BoFlag,13=save qty
	'14=Save item, 15=Overtyped price, 16-Pack


'.dc - Complete
	'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "MSBCH02"
	''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CLOSE

	'$INCLUDE: '\tpmanuf\src\msbatch.inc'
	'$INCLUDE: '\tpmanuf\src\msbatchh.inc'
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	''$INCLUDE: '\tpmanuf\src\msclass.inc'
	''$INCLUDE: '\tpmanuf\src\acmgn.inc'
	'$INCLUDE: '\tpmanuf\src\acstk.inc'
	''$INCLUDE: '\tpmanuf\src\company.inc'
	'$INCLUDE: '\tpmanuf\src\msrmat.inc'
	'$INCLUDE: '\tpmanuf\src\ordhed.inc'
	CLOSE #48
	'$INCLUDE: '\tpmanuf\src\orddet.inc'
	CLOSE #49
	'$INCLUDE: '\tpmanuf\src\ordprt.inc'
	'$INCLUDE: '\tpmanuf\src\tnthed.inc'
	CLOSE #54
	'$INCLUDE: '\tpmanuf\src\forhed.inc'
	'$INCLUDE: '\tpmanuf\src\tntdet.inc'
	CLOSE #55



	keyl% = 20: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)
	CALL index("OPEN ", ind%, "acstkx3.acf", 7, keyl%)
	OPEN "C:\TPEXE\acstk.WRK" FOR RANDOM SHARED AS #4 LEN = 16
	TYPE RcdFmtWrk1
		wrkqty AS STRING * 2
		wrkrrn AS STRING * 2
		END TYPE
	DIM SHARED wrk1 AS RcdFmtWrk1
	GET #36, 1, msmisc
	qtyf% = CVI(msmisc.qtyf$): bchoff% = CVI(msmisc.bchoff$): bchno% = CVI(msmisc.bchno$)
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	maxacc% = CVI(msmisc.max5$): maxtypes% = CVI(msmisc.max6$): maxcus% = CVI(msmisc.max7$)
	maxbrw% = 500
	maxord% = 999
	datafile$ = "Hist."
	datafile$ = "Batch"


start:
	COLOR 2, 0
	CALL setup("BATCH DATA ENTRY")
	 btm$ = "F1-Exit  F5-History  F6-Browse   F8-Rmat   F9-Acc   F10-Quality Control": COLOR 2, 0
	'btm$ = "F1-Exit          F5-History           F6-Browse         F10-Change batch data": COLOR 2, 0
	COLOR 0, 3: LOCATE 25, 4: PRINT btm$;
	IF rec26% > 0 AND rec26% < 9999 THEN
		CALL dsply(rec26%)
	END IF

get.batch:
	CALL sndmsg(msg$): msg$ = ""
	COLOR 2, 0:
	LOCATE 3, 72: PRINT datafile$
	LOCATE 3, 22: PRINT "   Enter batch no...>";
	LOCATE 3, 43: a$ = "    "

	CALL inpnew(a$, 104!, updwn%, "13,59,61,63-64,66-68,72,73,80,81" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
	'IF updwn% = 61 THEN CALL top2btm
	IF updwn% = 72 THEN
		rec26% = rec26% - 1
		CALL dsply(rec26%)
	END IF
	IF updwn% = 73 THEN
		rec26% = rec26% - 10
		CALL dsply(rec26%)
	END IF
	IF updwn% = 80 THEN
		rec26% = rec26% + 1
		CALL dsply(rec26%)
	END IF

	IF updwn% = 81 THEN
		rec26% = rec26% + 10
		CALL dsply(rec26%)
	END IF

	IF updwn% = 68 THEN
			IF batch.flqc$ = "Y" THEN
			ELSE
				CALL change(rec26%, updwn%)
				GOTO start
			END IF
	END IF
	IF updwn% = 63 THEN
		IF datafile$ = "Hist." THEN datafile$ = "Batch" ELSE datafile$ = "Hist."
		IF datafile$ = "Hist." THEN
			CALL selectfile(filename$, updwn%)
			CLOSE #26
			OPEN filename$ FOR RANDOM SHARED AS #26 LEN = LEN(batch)
		END IF
	END IF

	IF updwn% = 64 THEN CALL browse57(rec26%, updwn%): GOTO start
	IF updwn% = 13 THEN
		IF VAL(a$) = 0 THEN a$ = STR$(rec26% + 1)
		rec26% = VAL(a$)
		CALL dsply(rec26%)
	END IF

	IF updwn% = 66 THEN
		IF datafile$ = "Hist." THEN GOTO get.batch
		rview% = 0
		IF rec26% = 0 THEN GOTO get.batch
		IF batch.fltnt$ = "Y" THEN rview% = -1
		PCOPY 0, 3
			auto% = 0
			cost.or.ltrs$ = "Litres"
			rec% = 1
			eyld! = 1
			detfile$ = ".\batches\b" + LTRIM$(RTRIM$(batch.thisbatch$)) + ".bch"
			IF DIR$(detfile$) = "" THEN GOTO get.batch
			OPEN detfile$ FOR RANDOM SHARED AS #65 LEN = 32
			CALL load.lines(rec%, eyld!)
redodet:
			CALL details(rec&, updwn%, auto%, rview%)
			IF NOT rview% THEN CALL save.lines(rec26%, auto%)
			IF redodet% THEN GOTO redodet
			'CLOSE #63
			CLOSE #64
			CLOSE #65


		PCOPY 3, 0
		CALL dsply(rec26%)
	END IF

	IF updwn% = 67 THEN
		IF datafile$ = "Hist." THEN GOTO get.batch
		rview% = 0
		IF rec26% = 0 OR batch.flstk$ = "R" THEN GOTO get.batch
		IF batch.fltnt$ = "Y" THEN
		ELSE
			PCOPY 0, 1
			CALL box(17, 4, 63, 20, 6, 9, 1)
			COLOR 3, 1
			LOCATE 5, 28: PRINT "      N O T E        "
			COLOR 6, 1
			LOCATE , 28: PRINT ""
			LOCATE , 28: PRINT "Finalise Raw Material      "
			LOCATE , 28: PRINT "  actuals first (F8)          "
			LOCATE , 28: CALL inpnew(a$, 1, updwn%, "13" + ALT$): GOSUB ALT
			PCOPY 1, 0
			GOTO get.batch
		END IF
		IF batch.flstk$ = "Y" THEN rview% = -1
		PCOPY 0, 3
		CALL mline(hord%, rview%, batch.thisbatch$)
		PCOPY 3, 0
		CALL dsply(rec26%)
	END IF


GOTO get.batch

SUB accbrowse (rec%)
'$INCLUDE: '\tpmanuf\src\accbrow.bi'
END SUB

SUB allocateSIP (rec57%)

	IF rec57% < 1 OR rec57% > 9999 THEN GOTO x.reallocate
	GET #57, rec57%, batch

	IF MID$(batch.form$, 4, 1) = "T" AND mode$ <> "Tints" THEN
		msg$ = "The formula in this batch is a Tint.  Hit F5 and try again."
		GOTO x.reallocate
	END IF
	IF MID$(batch.form$, 4, 1) <> "T" AND mode$ = "Tints" THEN
		msg$ = "The formula in this batch not is a Tint.  Hit F5 and try again."
		GOTO x.reallocate
	END IF

	CALL ReturntoStock(batch.form$, batch.yld!)
	msg$ = "Raw Materials for Batch" + STR$(batch.bno%) + ":  Formula " + batch.form$ + " finalised"

x.reallocate:
END SUB

SUB browse.idx (firstonscreen%, ch1%, ch2%) STATIC
''$INCLUDE: '\tpmanuf\src\browse01.bi'
END SUB

SUB browse38 (browse38.result%, updwn%) STATIC
'$INCLUDE: '\tpmanuf\src\browse38.bi'
END SUB

SUB browse57 (browse57.result%, updwn%)
	btlast% = LOF(57) / 96
	CALL setup("BROWSE FILE")
	COLOR 6, 0
	LOCATE 4, 2: PRINT "Seq Description................... Batch  Form... Theory  Actual    Date. Flag";
	COLOR 0, 3: LOCATE 25, 2: PRINT " F1-Exit       F5-Zero Yields     F6-All    F7-One formula"; : COLOR 2, 0
	COLOR 2, 0
	len.of.browse% = 17
	IF browse57.result% < 1 THEN browse57.result% = 1
	IF browse57.result% > btlast% THEN browse57.result% = btlast%
	s% = browse57.result%
	skip% = -1

	mode$ = "all"' "zero","form"


2510
	LOCATE 3, 2: PRINT "Current number.:"; browse57.result%;
	LOCATE 3, 72: PRINT mode$
	LOCATE 3, 23: PRINT "Browse from number..> "; CHR$(FNH);
	IF NOT skip% THEN
		z$ = ""
		CALL inpnew(z$, 204!, updwn%, "13,59-60,63-65,72,73,80,81")
	END IF
	skip% = 0

	LOCATE 3, 44
	SELECT CASE updwn%
	CASE 59: GOTO x.browse57
	CASE 63: mode$ = "zero": GOSUB loadrrn57
	CASE 64: mode$ = "all ": GOSUB loadrrn57
	CASE 65: mode$ = "form": GOSUB loadrrn57
	CASE 72: startrrn% = startrrn% - 1
	CASE 73: startrrn% = startrrn% - len.of.browse%
	CASE 80: startrrn% = startrrn% + 1
	CASE 81: startrrn% = startrrn% + len.of.browse%
	CASE 13: startrrn% = VAL(z$)

	CASE ELSE
	END SELECT
	browse57.result% = startrrn%
	GOSUB listpage57
	GOTO 2510
'>>----------------------------------------------------------------
'>> - load
'>>----------------------------------------------------------------
loadrrn57:
	CALL sndmsg("loading..")
	'FOR i% = 1 TO maxbrw%: btext$(i%) = "": NEXT
	tot.yld! = 0: tot.ayld! = 0
	tot.Resinvar = 0: tot.Solventvar = 0: tot.Thickenervar = 0: tot.Rheomodifier = 0
	tot.Stainer1var = 0: tot.Stainer2var = 0: tot.Stainer3var = 0

	tform$ = "000" + MID$(STR$(VAL(z$)), 2, 3): tform$ = RIGHT$(tform$, 3)

	n% = 0
	rec57% = 1
	IF datafile$ = "Hist." THEN
		GET #26, rec57%, batch
		ELSE
		GET #57, rec57%, batch
		END IF

	DO WHILE NOT EOF(57) AND NOT EOF(26) AND mode$ <> "all "
		ok% = -1
		IF batch.bno% = 0 THEN ok% = 0
		IF mode$ = "zero" AND batch.ayld! > 0 THEN ok% = 0
		IF mode$ = "form" AND MID$(batch.form$, 1, 3) <> tform$ THEN ok% = 0

	 IF ok% THEN
		n% = n% + 1
		b$ = "0000" + MID$(STR$(batch.bno%), 2): b$ = RIGHT$(b$, 4)
		b$ = batch.year$ + b$

		load$ = "   " + STR$(n%): load$ = RIGHT$(load$, 3)
		load$ = load$ + " " + batch.name$ + " " + b$ + " "
		load$ = load$ + " " + batch.form$ + "-" + MID$(STR$(batch.revision%), 2, 1)
		load$ = load$ + "  " + format((batch.ltr! * batch.yld! / batch.yield!), "####.#")
		load$ = load$ + "  " + format(batch.ayld!, "####.#")
		load$ = load$ + "   " + FNDYY$(batch.date$)
		'btext$(n%) = load$

		'>- Stats ----
		IF mode$ = "zero" THEN tot.yld! = tot.yld! + batch.yld!
		IF batch.ayld! > 0 THEN
			tot.yld! = tot.yld! + batch.yld!
			tot.ayld! = tot.ayld! + batch.ayld!
			tot.Resinvar = tot.Resinvar + batch.resinvar / 100 * batch.yld!
			tot.Solventvar = tot.Solventvar + batch.solventvar / 100 * batch.yld!
			tot.Thickenervar = tot.Thickenervar + batch.thickenervar / 100 * batch.yld!
			tot.Rheomodifier = tot.Rheomodifier + batch.rheomodifier / 100 * batch.yld!
			tot.Stainer1var = tot.Stainer1var + batch.stainer1var / 100 * batch.yld!
			tot.Stainer2var = tot.Stainer2var + batch.stainer2var / 100 * batch.yld!
			tot.Stainer3var = tot.Stainer3var + batch.stainer3var / 100 * batch.yld!
			END IF
		END IF

	IF rec57% MOD 100 = 0 THEN CALL sndmsg("loading.." + STR$(rec57%))

	IF datafile$ = "Hist." THEN
		GET #26, , batch: rec57% = rec57% + 1
		ELSE
		GET #57, , batch: rec57% = rec57% + 1
		END IF

		LOOP
	startrrn% = 1

	per.yld! = 0
	per.Resinvar! = 0
	per.Solventvar! = 0
	per.Thickenervar! = 0
	per.Rheomodifier! = 0
	per.Stainer1var! = 0
	per.Stainer2var! = 0
	per.Stainer3var! = 0

	IF tot.ayld! > 0 THEN
		per.yld! = (tot.ayld! / tot.yld!) * 100 - 100
		per.Resinvar! = (tot.Resinvar! / tot.yld!) * 100 - 100
		per.Solventvar! = (tot.Solventvar! / tot.yld!) * 100 - 100
		per.Thickenervar! = (tot.Thickenervar! / tot.yld!) * 100 - 100
		per.Rheomodifier! = (tot.Rheomodifier! / tot.yld!) * 100 - 100
		per.Stainer1var! = (tot.Stainer1var! / tot.yld!) * 100 - 100
		per.Stainer2var! = (tot.Stainer2var! / tot.yld!) * 100 - 100
		per.Stainer3var! = (tot.Stainer3var! / tot.yld!) * 100 - 100
		END IF

	COLOR 10, 0
	LOCATE 22, 2: PRINT USING "  Yield Act Yld  +/- !   Res.    Sol.    Thk.    Rheo    St1.    St2.    St3. "; ""
	LOCATE 23, 2: PRINT USING "####### ####### ##.##% ####.#% ####.#% ####.#% ####.#% ####.#% ####.#% ####.#%"; tot.yld!; tot.ayld!; per.yld!; per.Resinvar!; per.Solventvar!; per.Thickenervar!; per.Rheomodifier!; per.Stainer1var!; per.Stainer2var!;  _
per.Stainer3var!;
	IF per.Resinvar! < -99 THEN LOCATE 22, 25: PRINT "    -  "
	IF per.Solventvar! < -99 THEN LOCATE 22, 33: PRINT "    -  "
	IF per.Thickenervar! < -99 THEN LOCATE 22, 41: PRINT "    -  "
	IF per.Rheomodifier! < -99 THEN LOCATE 22, 49: PRINT "    -  "
	IF per.Stainer1var! < -99 THEN LOCATE 22, 57: PRINT "    -  "
	IF per.Stainer2var! < -99 THEN LOCATE 22, 65: PRINT "    -  "
	IF per.Stainer3var! < -99 THEN LOCATE 22, 73: PRINT "    -  "

	COLOR 2, 0

	CALL sndmsg(""): COLOR 2, 0
RETURN

'>>----------------------------------------------------------------
'>> - display a page (startrrn%)
'>>----------------------------------------------------------------
listpage57:
	IF startrrn% < 1 THEN startrrn% = 1
	IF mode$ <> "all " THEN IF startrrn% > maxbrw% - len.of.browse% THEN startrrn% = maxbrw% - len.of.browse%

	COLOR 2, 0
	FOR lin% = 1 TO len.of.browse%
		LOCATE lin% + 4, 2
		rec5% = lin% + startrrn% - 1
		IF mode$ = "all " THEN
			IF datafile$ = "Hist." THEN
				GET #26, rec5%, batch
				ELSE
				GET #57, rec5%, batch
				END IF

				n% = rec5%
				b$ = "0000" + MID$(STR$(batch.bno%), 2): b$ = RIGHT$(b$, 4)
				b$ = batch.year$ + b$

				load$ = "   " + STR$(n%): load$ = RIGHT$(load$, 3)
				load$ = load$ + " " + batch.name$ + " " + b$ + " "
				load$ = load$ + " " + batch.form$ + "-" + MID$(STR$(batch.revision%), 2, 1)
				load$ = load$ + " " + format(batch.ltr! / batch.yield! * batch.yld!, "####.#")
				load$ = load$ + "  " + format(batch.ayld!, "####.#")
				load$ = load$ + "  " + FNDYY$(batch.date$) + " "
				IF batch.bno% = 0 THEN load$ = SPACE$(75)
				END IF
				COLOR 2
		'IF mode$ <> "all " THEN load$ = btext$(rec5%)
		PRINT load$;
				COLOR 3
				IF batch.fltnt$ = "Y" THEN COLOR 14
				PRINT batch.fltnt$;
				COLOR 3
				IF batch.flstk$ = "Y" OR batch.flstk$ = "R" THEN COLOR 14
				PRINT batch.flstk$;
				COLOR 3
				IF batch.flqc$ = "Y" THEN COLOR 14
				PRINT batch.flqc$
				COLOR 2
		NEXT
RETURN

x.browse57:
	browse57.result% = startrrn%

END SUB

SUB calcusecost

	 '* Calculate use cost from SG & cost price
	ab$ = "LT" + "-" + msrmat.UseUnit$
	SELECT CASE ab$
	CASE "LT-LT": msrmat.UseCost = msrmat.PurCost
	CASE "LT-KG"
				IF msrmat.sg <> 0 THEN msrmat.UseCost = msrmat.PurCost / msrmat.sg
				IF msrmat.sg = 0 THEN msrmat.UseCost = msrmat.PurCost
	CASE "LT-GM"
				IF msrmat.sg <> 0 THEN msrmat.UseCost = msrmat.PurCost / msrmat.sg * 1000
				IF msrmat.sg = 0 THEN msrmat.UseCost = msrmat.PurCost / 1000
	CASE "LT-OZ": msrmat.UseCost = msrmat.PurCost / 28.413
	CASE "LT-UT": msrmat.UseCost = msrmat.PurCost / 28.413 / 64
	CASE "LT-ML": msrmat.UseCost = msrmat.PurCost / 1000
	CASE ELSE: msrmat.UseCost = msrmat.PurCost
	END SELECT
	'* Round to 2 decimal plmsrmat.activees UP ie 3.0001 = 3.01
	CALL round(msrmat.UseCost, 2.5)


END SUB

SUB change (rec26%, updwn%)

cf1a: '***** Notes 1
	LOCATE 20, 54
				CALL inpnew(batch.qcnote1$, 125!, updwn%, "13,59")
	IF updwn% = 59 THEN GOTO x.change

cf1b: '***** Notes 2
	LOCATE 21, 54
				CALL inpnew(batch.qcnote2$, 125!, updwn%, "13,59,60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf1a

cf1c: '***** Notes 3
	LOCATE 22, 54
				CALL inpnew(batch.qcnote3$, 125!, updwn%, "13,59,60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf1b

cf1d: '***** Notes 4
	LOCATE 23, 54
				CALL inpnew(batch.qcnote4$, 125!, updwn%, "13,59,60")
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf1c

cf2a:    '***** Volume Solids

	LOCATE 14, 41: a$ = STR$(batch.qcvsol!)
				CALL inpnew(a$, 5.2, updwn%, "13,59-60")
	batch.qcvsol! = VAL(a$)
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf1d
	LOCATE 14, 41: PRINT USING "###.##%"; batch.qcvsol!

cf2b:    '***** Weight Solids

	LOCATE 15, 41: a$ = STR$(batch.qcwsol!)
				CALL inpnew(a$, 5.2, updwn%, "13,59-60")
	batch.qcwsol! = VAL(a$)
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf2a
	LOCATE 15, 41: PRINT USING "###.##%"; batch.qcwsol!

cf3a:    '***** Viscocity 1
	LOCATE 18, 42: a$ = STR$(batch.qcvisc1!)
	IF batch.visc1l! < 15 THEN
				CALL inpnew(a$, 3.1, updwn%, "13,59-60")
	ELSE
			 CALL inpnew(a$, 104!, updwn%, "13,59-60")
	END IF
	batch.qcvisc1! = VAL(a$)

	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf2b

cf3b:    '***** Viscocity 2
	LOCATE 19, 42: a$ = STR$(batch.qcvisc2!)
	CALL inpnew(a$, 3.1, updwn%, "13,59-60")
	batch.qcvisc2! = VAL(a$)

	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf3a

cf4:    '***** pH
	LOCATE 20, 42: a$ = STR$(batch.qcph!)
	CALL inpnew(a$, 3.1, updwn%, "13,59-60")
	batch.qcph! = VAL(a$)

	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf3b
cf5:
	LOCATE 21, 43: a$ = STR$(batch.qcsg!)
				CALL inpnew(a$, 4.3, updwn%, "13,59-60")
	batch.qcsg! = VAL(a$)
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf4
cf6:
	LOCATE 22, 41: a$ = STR$(batch.qcgloss!)
				CALL inpnew(a$, 103!, updwn%, "13,59-60")
	batch.qcgloss! = VAL(a$)
	IF updwn% = 59 THEN GOTO x.change
	IF updwn% = 60 THEN GOTO cf5

x.change:


'??

		PCOPY 0, 1
		CALL box(10, 28, 12, 52, 3, 0, 1)
		COLOR 2
		LOCATE 11, 30: PRINT "Finalise (Y/N/P)..>"
		LOCATE 11, 49
		a$ = batch.flqc$
		CALL inpnew(a$, 101!, updwn%, "13,59")
		a$ = UCASE$(a$)
		batch.flqc$ = a$
		SELECT CASE a$
			CASE "P"
				IF datafile$ = "Hist." THEN
					btlast% = LOF(57) / 96
				END IF

				IF rec26% >= 1 AND rec26% < bchno% THEN
					IF datafile$ = "Hist." THEN
						PUT #26, rec26%, batch
					ELSE
						PUT #57, rec26%, batch
					END IF
				END IF
			CASE "Y"
				IF datafile$ = "Hist." THEN
					btlast% = LOF(57) / 96
				END IF

				IF rec26% >= 1 AND rec26% < bchno% THEN
					IF datafile$ = "Hist." THEN
						PUT #26, rec26%, batch
					ELSE
						PUT #57, rec26%, batch
					END IF
				END IF
					'>>>---- Open audit record file
					rbq$ = ".\export\B" + RTRIM$(LTRIM$(batch.thisbatch$)) + ".RBQ"
					CLOSE #97
					OPEN rbq$ FOR OUTPUT AS #97
					'--------------> BAQCD
					WRITE #97, "BLANK", "ID", "flag", "note1", "note2", "note3", "note4", "vsol,", "wsol", "pvc", "pbr", "visc1", "visc2", "ph", "gloss", "sg"
					WRITE #97, "BAQCD", batch.thisbatch$, batch.flqc$, batch.qcnote1$, batch.qcnote2$, batch.qcnote3$, batch.qcnote4$, batch.qcvsol, batch.qcwsol, batch.qcpvc, batch.qcpbr, batch.qcvisc1, batch.qcvisc2, batch.qcph, batch.qcgloss, batch.qcsg
					CLOSE #97
			CASE "N"
			CASE ELSE
			 GOTO x.change
		END SELECT


		IF batch.yld! > 0 THEN
			thisbatch$ = batch.year$ + "0000"
			b$ = MID$(STR$(rec26%), 2)
			MID$(thisbatch$, 7 - LEN(b$), LEN(b$)) = b$
			thisbatch$ = "B" + thisbatch$ + ".PRN"
			IF DIR$(thisbatch$) > "" THEN
				CALL killa(thisbatch$)
			END IF
		END IF


END SUB

SUB dsply (rec26%)
	blast% = LOF(57) / LEN(batch)
	bhistlast% = LOF(26) / LEN(batch)
	IF rec26% < 1 OR rec26% > 9999 THEN rec26% = 1
	IF datafile$ = "Hist." THEN
	IF rec26% < 1 OR rec26% > bhistlast% THEN
		FOR i% = 1 TO 20: LOCATE i% + 3, 2: PRINT SPACE$(78): NEXT
		msg$ = "Batch not on file."
		GOTO x.dsplyb
		END IF
	ELSE
	IF rec26% < 1 OR rec26% > blast% THEN
		FOR i% = 1 TO 20: LOCATE i% + 3, 2: PRINT SPACE$(78): NEXT
		msg$ = "Batch not on file."
		GOTO x.dsplyb
		END IF
	END IF

	IF datafile$ = "Hist." THEN
		GET #26, rec26%, batch
	ELSE
		GET #57, rec26%, batch
	END IF
	IF batch.class% < 1 OR batch.class% > 99 THEN batch.class% = 1
	'GET #29, batch.class%, msclass

	COLOR 3, 0
				LOCATE 4, 5: PRINT "Batch Header Information:                              Status Info:"
				LOCATE 8, 5: PRINT "Yield Summary....... Nominal    Litres    Kilograms     S.G.       Cost"
			 LOCATE 13, 5: PRINT "Quality Control      Formula        Testing                Dates"
			 LOCATE 19, 52: PRINT "        Batch Notes        "
	COLOR 2
			 LOCATE 20, 53: PRINT ">                         <"
			 LOCATE 21, 53: PRINT ">                         <"
			 LOCATE 22, 53: PRINT ">                         <"
			 LOCATE 23, 53: PRINT ">                         <"

	COLOR 2, 0
	LOCATE 5, 2:
	LOCATE 5, 5: PRINT USING "Batch number.......: \       \ "; batch.thisbatch$
		LOCATE 6, 5: PRINT USING "Description........: \                             \ "; batch.name$
	LOCATE 7, 5: PRINT USING "Formula number.....: \  \ Rev##    "; batch.form$; batch.revision%
	'LOCATE 9, 5: PRINT USING "Class..............:!###.#- & "; batch.sorw$; batch.class%; msclass.cldesc$
	LOCATE 5, 60: PRINT "Batch.:"
	LOCATE 6, 60: PRINT "Stock.:"
	LOCATE 7, 60: PRINT "Q.C...:"


	SELECT CASE batch.fltnt$
		CASE "P"
			COLOR 14: af$ = "Pending  "
		CASE "N"
			COLOR 14: af$ = "Pending  "
		CASE "Y"
			COLOR 10: af$ = "Complete "
		CASE ELSE: af$ = "        "
	END SELECT
	LOCATE 5, 68: PRINT USING "&"; af$
	SELECT CASE batch.flstk$
		CASE "N"
			COLOR 14: as$ = "Not Alloc"
		CASE "P"
			COLOR 14: as$ = "Pending  "
		CASE "Y"
			COLOR 10: as$ = "Complete "
		CASE "R"
			COLOR 10: as$ = "As RMater"

		CASE ELSE: as$ = "         "
	END SELECT
	LOCATE 6, 68: PRINT USING "&"; as$
	SELECT CASE batch.flqc$
		CASE "N"
			COLOR 6: aq$ = "Not Taken"
		CASE "P"
			COLOR 14: aq$ = "Pending  "
		CASE "Y"
			COLOR 10: aq$ = "Complete "
		CASE ELSE: aq$ = "         "
	END SELECT
	LOCATE 7, 68: PRINT USING "&"; aq$

	COLOR 2
	 LOCATE 9, 5: PRINT USING "Expected from Form.>#,###.#L   #,###.#L   #,###.##kg  #.###kg/L$$###.###/Lt"; batch.yield!; batch.ltr!; batch.kg!; batch.sg!; batch.rawcost!
	LOCATE 10, 5: PRINT USING "Expected from Batch>#,###.#L   #,###.#L   #,###.##kg                       "; batch.yld!; batch.ltr! * batch.yld! / batch.yield!; batch.kg! * batch.yld! / batch.yield!
	LOCATE 11, 5: PRINT USING "Actually Manufact..>           #,###.#L   #,###.##kg  #.###kg/L$$###.###/Lt"; batch.ayld!; batch.resinvar!; batch.rheomodifier!; batch.perltr!
	LOCATE 12, 5: PRINT USING "Filled.> #,###.#L   $$###.###/Lt   Yield..> ###.##%   Waste..> #,###.##L   "; batch.solventvar!; batch.thickenervar!; batch.stainer2var!; batch.stainer1var!
	'IF batch.ayld! = 0 THEN
	'      LOCATE 12, 5: PRINT "Wastage............>               N/A    Yield....>    N/A          N/A   "
	'ELSE
	'LOCATE 12, 5: PRINT USING "Wastage............>           #,###.#L   Yield....> ###.##%   $$###.###   "; batch.stainer1var!; batch.stainer2var!; batch.stainer3var!
	'END IF

	LOCATE 14, 5: PRINT USING "V/Sol..............: ###.##%        ###.##%"; batch.Vsol!; batch.qcvsol!
	LOCATE 15, 5: PRINT USING "W/Sol..............: ###.##%        ###.##%"; batch.Wsol!; batch.qcwsol!
	LOCATE 16, 5: PRINT USING "P.V.C..............: ###.##         ###.##"; batch.pvc!; batch.qcpvc!
	LOCATE 17, 5: PRINT USING "P.B.R..............: ###.##         ###.##"; batch.pbr!; batch.qcpbr!
	IF batch.visc1l! < 15 THEN
	LOCATE 18, 5: PRINT USING "Rotothinner........: #.# to #.# pse.  #.# pse."; batch.visc1l!; batch.visc1h!; batch.qcvisc1!
	ELSE
	LOCATE 18, 5: PRINT USING "Ford Cup _# 4.......:### to ### sec.  ### sec."; batch.visc1l!; batch.visc1h!; batch.qcvisc1!
	END IF
	LOCATE 19, 5: PRINT USING "Cone _& Plate.......: #.# to #.#       #.#     "; batch.visc2l!; batch.visc2h!; batch.qcvisc2!
	LOCATE 20, 5: PRINT USING "pH.................: ##.#            ##.#     "; batch.ph!; batch.qcph!
	LOCATE 21, 5: PRINT USING "S.G................:  #.### kg/L      #.### kg/L"; batch.ph!; batch.qcph!
	LOCATE 22, 5: PRINT USING "Gloss Level (min)..: ##              ##       "; batch.gloss!; batch.qcgloss!
	LOCATE 23, 5: PRINT USING "Filter.............>### Grind (min).>###"; batch.filter%; batch.grind!

	LOCATE 20, 54: PRINT batch.qcnote1$
	LOCATE 21, 54: PRINT batch.qcnote2$
	LOCATE 22, 54: PRINT batch.qcnote3$
	LOCATE 23, 54: PRINT batch.qcnote4$

	LOCATE 14, 57: PRINT USING "Formula Ver.>\        \"; FNDYY$(batch.dateform$)
	LOCATE 15, 57: PRINT USING "Printed.....>\        \"; FNDYY$(batch.date$)
	LOCATE 16, 57: PRINT USING "Requested...>\        \"; FNDYY$(batch.datereq$)
	LOCATE 17, 57: PRINT USING "Manufacture.>\        \"; FNDYY$(batch.dateman$)
	LOCATE 18, 57: PRINT USING "Operator....>\ \"; batch.manby$



	batchltr! = batch.ayld!
	perltr! = batch.perltr!
	hord% = batch.hord%
	batchsg! = batch.rheomodifier!
x.dsplyb:
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

SUB killa (file$)
ON LOCAL ERROR RESUME NEXT
KILL file$
END SUB

SUB selectfile (filename$, updwn%)
	PCOPY 0, 1
	CALL box(4, 17, 20, 55, 2, 0, 1)

	xo% = 0: yo% = 0
	FOR i% = 1 TO 30
	p% = 9 + i% - 1
	s% = p% + 1
	p$ = RIGHT$("00" + MID$(STR$(p%), 2), 2)
	s$ = RIGHT$("00" + MID$(STR$(s%), 2), 2)
	wrk$ = "BATCH" + p$ + ".HST"
	ok% = 0
		a$ = DIR$(wrk$)
		IF a$ <> "" THEN
		OPEN wrk$ FOR RANDOM SHARED AS #99
		IF LOF(99) > 0 THEN ok% = -1
		CLOSE #99
		END IF

	io% = io% + 1
	IF io% > 15 THEN io% = 1: yo% = yo% + 20
	IF ok% THEN
		LOCATE 4 + io%, 20 + yo%: PRINT USING "## &"; i%; wrk$
	END IF
	NEXT

	DO
	LOCATE 21, 23: PRINT "Option..>";
	LOCATE 21, 32:
				CALL inpnew(opt$, 2!, updwn%, "13,59")
	IF updwn% = 59 THEN EXIT DO
	LOOP UNTIL updwn% = 13

	i% = VAL(opt$)
	IF i% < 0 OR i% > 15 THEN i% = 1
	p% = 9 + i% - 1   ' WAS 84
	s% = p% + 1
	p$ = RIGHT$("00" + MID$(STR$(p%), 2), 2)
	s$ = RIGHT$("00" + MID$(STR$(s%), 2), 2)
	wrk$ = "BATCH" + p$ + ".HST"
	filename$ = wrk$

	PCOPY 1, 0
END SUB

SUB top2btm

rec57% = 1
GET #57, rec57%, batch
DO WHILE NOT EOF(57)
IF MID$(batch.date$, 3, 1) = "/" THEN
	a$ = FNDY$(batch.date$)
	batch.date$ = a$
	PUT #57, rec57%, batch
	END IF

GET #57, , batch: rec57% = rec57% + 1
LOOP


END SUB
