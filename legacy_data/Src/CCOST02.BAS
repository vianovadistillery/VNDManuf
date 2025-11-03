DECLARE SUB getcost (costsheet%, c025!, c05!, c1!, c2!, c4!, c10!, c20d!, c20p!, c60!, c200!, cbulk!)
DECLARE FUNCTION searchrmatfor! (sfor$, stype$)
DECLARE SUB get.can.costs (show%, cansidx%, labelidx%, labouridx%)
DECLARE SUB get.markups ()
DECLARE SUB dolist (start%, finish%, runtype$, printsizes$)
DECLARE SUB print.line (costsheet%, runtype$, printsizes$)
DECLARE SUB quote ()
DECLARE SUB doheading (costsheet%, runtype$, printsizes$)
'.dc - Complete
'>>>>>>>>>>>>>>>>>>> costing listing      <<<<<<<<<<<<<<<<<<<<<<<<
'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	DIM SHARED mk!(11), mkon%(11)
	DIM SHARED m$(11), ff!
	'1=250ml,500ml,1lt,2lt,4lt,10lt,20lt,20lt,60lt,10=200lt,11=Bulk
	DIM SHARED can.allcost!(11)
	DIM SHARED can.cancost!(11), can.labourcost!(11), can.labelcost!(11)
	DIM SHARED wrkcost!, fetch%, maxrmat%
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\msrmat.INC'
	'$INCLUDE: '\tpmanuf\src\msmisc.INC'
	'$INCLUDE: '\tpmanuf\src\msmkp.INC'
	'$INCLUDE: '\tpmanuf\src\tnthed.INC'
	'$INCLUDE: '\tpmanuf\src\forhed.INC'
	'$INCLUDE: '\tpmanuf\src\tnthedx.INC'
	'$INCLUDE: '\tpmanuf\src\forhedx.INC'

	GET #36, 1, msmisc
	maxrmat% = CVI(msmisc.max3)
	GET #63, 1, tnthedx
		cansidx% = searchrmatfor("CAN.......", "cans")
	lablelidx% = searchrmatfor("LABEL.....", "label")
	labouridx% = searchrmatfor("LABOUR....", "labour")

	m$(0) = "Raw Material Cost  "
	CALL setup("CENTRAL COSTING REPORT")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit      F5-Cans/Labels/Labour      F9-Swap size       F10-Swap R.M.C  "; : COLOR 2, 0
	CALL get.markups
	CALL get.can.costs(0, cansidx%, lablelidx%, labouridx%)
	printsizes$ = "A": runtype$ = "A"

start:
	COLOR 14: LOCATE 4, 21
	rep1$ = "All sizes     "
	IF printsizes$ = "M" THEN rep1$ = "Major sizes   "
	IF runtype$ = "A" THEN rep1$ = rep1$ + "- Allocated R.M.C." ELSE rep1$ = rep1$ + "- Real R.M.C.       "
	PRINT rep1$
	COLOR 2, 0

	FOR i% = 1 TO 9
	IF mk!(i%) <> 0 OR i% = 0 THEN
			LOCATE i% + 5, 2
			PRINT TAB(20); i%; "...Produce price sheet for "; m$(i%)
			'LOCATE i% + 5, 60: PRINT USING "(##.###)"; mk!(i%)
			END IF
		NEXT

	LOCATE 16, 20: PRINT "40... Recost all recipes"
	LOCATE 17, 20: PRINT "50... Raw material cost list"
	LOCATE 18, 20: PRINT "90... Eject a page"
	LOCATE 19, 20: PRINT "98... Display quotation"
	LOCATE 20, 20: PRINT "99... Print all sheets"
	LOCATE 21, 20: PRINT " Select one..> ";
	a$ = ""
	LOCATE 21, 34
	CALL inpnew(a$, 2!, updwn%, "13,59,63,67,68" + ALT$): GOSUB ALT
	SELECT CASE updwn%
	CASE 59: CLOSE : bpgm$ = "msmenu": CALL exitpgm(bpgm$): CHAIN bpgm$
	CASE 63: CALL get.can.costs(-1, cansidx%, lablelidx%, labouridx%)
	CASE 67: IF printsizes$ = "A" THEN printsizes$ = "M" ELSE printsizes$ = "A"
	CASE 68: IF runtype$ = "A" THEN runtype$ = "R" ELSE runtype$ = "A"
	CASE 13
		opt% = VAL(a$)
		start% = opt%: finish% = opt%
		ok% = 0
		IF opt% = 0 AND LEN(a$) > 0 THEN ok% = -1
		IF opt% >= 1 AND opt% <= 9 THEN ok% = -1
		IF opt% = 40 THEN GOTO autocost
		IF opt% = 90 THEN PRINT #99, CHR$(12)
		IF opt% = 98 THEN CALL quote
		IF opt% = 99 THEN start% = 0: finish% = 9: ok% = -1

		IF ok% THEN CALL dolist(start%, finish%, runtype$, printsizes$)
	CASE ELSE
	END SELECT

	GOTO start
autocost:

CLOSE
ENVIRON "PARM$=AUTOC."
npgm$ = "MSUPD02D"
CALL exitpgm(npgm$): CHAIN npgm$

SUB doheading (costsheet%, runtype$, printsizes$) STATIC
	IF page% > 0 THEN PRINT #99, CHR$(12)
	fetch% = 0: page% = page% + 1
	PRINT #99, ; CHR$(14); msmisc.cc$
	DATE1$ = "  /  /  ": MID$(DATE1$, 1, 2) = MID$(DATE$, 4, 2):         MID$(DATE1$, 4, 2) = MID$(DATE$, 1, 2): MID$(DATE1$, 7, 2) = MID$(DATE$, 9, 2)
	PRINT #99, "#CCOST02"; TAB(67); "Date:"; DATE1$
	m$ = "RAW MATERIAL COST "
	m$ = m$(costsheet%)
	PRINT #99, TAB(25); m$;
	IF runtype$ = "R" THEN PRINT #99, "(Real)"
	IF runtype$ = "A" THEN PRINT #99, "(Allocated)"
	PRINT #99, TAB(72); USING "Page:###"; page%
	PRINT #99, STRING$(79, "=")
	IF costsheet% <> 10 AND printsizes$ = "A" THEN PRINT #99, "         PRODUCT             20LtP. 10Lt..  4Lt.. 2Lt.. 1Lt.  .5Lt  .25Lt"
	IF costsheet% <> 10 AND printsizes$ = "M" THEN PRINT #99, "         PRODUCT             20LtD. 10LtP.  4Lt.. 1Lt.."
	IF costsheet% = 10 THEN PRINT #99, TAB(14); "No       PRODUCT DESCRIPTION               Cost "
	PRINT #99, STRING$(79, "-")


END SUB

SUB dolist (start%, finish%, runtype$, printsizes$)
'////////////////////////////////////////////////////////////////
'/////   FIND LIST TYPE  /////
'////////////////////////////////////////////////////////////////
	mk!(0) = 0
	rec% = 0
	FOR costsheet% = start% TO finish%'* Up to nine markup sheets + RMC
		IF costsheet% > 0 AND costsheet% < 10 THEN
				IF mk!(costsheet%) = 0 THEN 680'* No markup no sheets
				END IF

		stdout$ = "LPT1"
		'stdout$ = "CON"
		OPEN stdout$ FOR OUTPUT AS #99
		idx% = 1: fetch% = -1: page% = 0
		DO WHILE idx% <> 0
			rec% = tnthedx.rrn%(idx%)
			IF rec% < 1 THEN EXIT DO
			GET #64, rec%, tnthed


			IF runtype$ = "A" THEN
				wrkcost! = tnthed.alccost!
				END IF
			IF runtype$ = "R" THEN
				wrkcost! = tnthed.rawcost!
				END IF


		IF wrkcost! <> 0 THEN
			CALL print.line(costsheet%, runtype$, printsizes$)'* Print 20,10,4,2,1,.5,.25 L canned costs
		END IF
		IF stdout$ = "CON" THEN x$ = INPUT$(1)
		IF idx% MOD 100 = 0 THEN CALL sndmsg("Record " + STR$(idx%))
		idx% = idx% + 1
		LOOP
	PRINT #99, CHR$(12)

680
	NEXT
	CLOSE #99

END SUB

SUB get.can.costs (show%, cansidx%, labelidx%, labouridx%)

	IF NOT show% THEN GOTO get.can.costs99

	CALL BOX(2, 3, 79, 21, 0, 0, 0)


	DIM sizedesc$(11)
	sizedesc$(1) = "250ml"
	sizedesc$(2) = "500ml"
	sizedesc$(3) = "  1lt"
	sizedesc$(4) = "  2lt"
	sizedesc$(5) = "  4lt"
	sizedesc$(6) = " 10lt"
	sizedesc$(7) = " 20lt"
	sizedesc$(8) = " 20lt"
	sizedesc$(9) = " 60lt"
	sizedesc$(10) = "200lt"
	sizedesc$(11) = "bulklt"

	IF cansidx% < 1 THEN cansidx% = 1
	IF labelidx% < 1 THEN labelidx% = 1
	IF labouridx% < 1 THEN labouridx% = 1
	mode$ = "cans.."

cf1:
	COLOR 6, 0
	LOCATE 6, 15: PRINT "Costed   Rmat.Description                   Cost"
	LOCATE 7, 15: PRINT "------------------------------------------------"
	COLOR 2, 0
	FOR i% = 1 TO 11
		SELECT CASE mode$
		CASE "cans..": rec% = cansidx% + i% - 1
		CASE "labels": rec% = labelidx% + i% - 1
		CASE "labour": rec% = labouridx% + i% - 1
		CASE ELSE
		END SELECT

		GET #38, rec%, msrmat
		LOCATE , 16
		PRINT USING "& | #### & $$###.##"; sizedesc$(i%); msrmat.no%; msrmat.desc1$; msrmat.UseCost
	NEXT
	LOCATE 5, 15: PRINT USING "Start number for \    \.> "; mode$
	a$ = ""
	LOCATE 5, 40: CALL inpnew(a$, 4!, updwn%, "59-60,13")
	IF VAL(a$) <> cansidx% AND VAL(a$) > 0 THEN
		SELECT CASE mode$
		CASE "cans..": cansidx% = VAL(a$)
		CASE "labels": labelidx% = VAL(a$)
		CASE "labour": labouridx% = VAL(a$)
		CASE ELSE
		END SELECT
		GOTO cf1
	END IF

	IF mode$ = "cans.." THEN mode$ = "labels": GOTO cf1
	IF mode$ = "labels" THEN mode$ = "labour": GOTO cf1


	CALL BOX(2, 3, 79, 21, 0, 0, 0)

get.can.costs99:

	FOR c% = 1 TO 11
		idx% = c% '12 - c%
		can.allcost!(idx%) = 0

		GET #38, cansidx% + c% - 1, msrmat
		can.allcost!(idx%) = can.allcost!(idx%) + msrmat.UseCost
		can.cancost!(idx%) = msrmat.UseCost

		GET #38, labelidx% + c% - 1, msrmat
		can.allcost!(idx%) = can.allcost!(idx%) + msrmat.UseCost
		can.labelcost!(idx%) = msrmat.UseCost

		GET #38, labouridx% + c% - 1, msrmat
		can.allcost!(idx%) = can.allcost!(idx%) + msrmat.UseCost
		can.labourcost!(idx%) = msrmat.UseCost
	NEXT

END SUB

SUB get.markups

	mk!(0) = 0: mkon%(0) = 0: m$(0) = "GATE COST                     "
	FOR i% = 1 TO 10

		GET #37, i%, msmkp
		mk!(i%) = CVS(msmkp.mk$)
		m$(i%) = msmkp.mm$
		mkon%(i%) = CVI(msmkp.mkon$)
		NEXT

	GET #37, 10, msmkp
	ff! = CVS(msmkp.mk$)

END SUB

SUB getcost (costsheet%, c025!, c05, c1!, c2!, c4!, c10!, c20d!, c20p!, c60!, c200!, cbulk!)
'//////////////////////////////////////////////////
'* Get cost per each label
'//////////////////////////////////////////////////
	'>>> Add in fuckup factor <<<
	'wrkcost! = wrkcost! + wrkcost! * ff!

	'>>> Find cost of item with can,label,labour and no markup  <<<
	c025! = can.allcost!(1) + (wrkcost! * .25)
	c05! = can.allcost!(2) + (wrkcost! * .5)
	c1! = can.allcost!(3) + (wrkcost! * 1)
	c2! = can.allcost!(4) + (wrkcost! * 2)
	c4! = can.allcost!(5) + (wrkcost! * 4)
	c10! = can.allcost!(6) + (wrkcost! * 10)
	c20d! = can.allcost!(7) + (wrkcost! * 20)
	c20p! = can.allcost!(8) + (wrkcost! * 20)
	c60! = can.allcost!(9) + (wrkcost! * 60)
	c200! = can.allcost!(10) + (wrkcost! * 200)
	cbulk! = can.allcost!(11) + (wrkcost!)

	'>>>---------------------------------------------------------------<<<
	'>>>    Now add the calculated margin off each list based on list
	'>>>---------------------------------------------------------------<<<

		mult! = 1 + mk!(costsheet%)

		i% = costsheet%
		DO WHILE mkon%(i%) > 0
			i% = mkon%(i%)
			mult! = mult! * (1 + mk!(i%))
		LOOP
		cbulk! = mult! * cbulk!
		c025! = mult! * c025!
		c05! = mult! * c05!
		 c1! = mult! * c1!
		 c2! = mult! * c2!
		 c4! = mult! * c4!
		c10! = mult! * c10!
		c20d! = mult! * c20d!
		c20p! = mult! * c20p!
		c60! = mult! * c60!
	 c200! = mult! * c200!

END SUB

SUB print.line (costsheet%, runtype$, printsizes$) STATIC
'//////////////////////////////////////////////////
'// Get cost for each label in then array
'//////////////////////////////////////////////////
	IF fetch% THEN CALL doheading(costsheet%, runtype$, printsizes$): lin% = 0

	CALL getcost(costsheet%, c025, c05, c1, c2, c4, c10, c20d, c20p, 60, c200, cbulk)
	tmp3$ = MID$(tnthed.tnta$, 1, 3)

	IF costsheet% = 10 THEN
		s$ = SPACE$(12)
		PRINT #99, USING "&  \   \   \                       \    #####.###"; s$; tnthed.tnta$; tnthed.desc$; wrkcost!
	ELSE
		IF printsizes$ = "A" THEN PRINT #99, USING "\  \\                       \   ###.## ###.## ##.## ##.## ##.## ##.## ##.##"; tmp3$; tnthed.desc$; c20d; c10; c4; c2; c1; c05; c025



		IF printsizes$ = "M" THEN PRINT #99, USING "\  \\                       \   ###.## ###.## ##.## ##.##"; tmp3$; tnthed.desc$; c20d; c10; c4; c1
	END IF
	 lin% = lin% + 1: IF lin% > 50 THEN fetch% = -1

END SUB

SUB quote
'//////////////////////////////////////////////////
'* Display a quote
'//////////////////////////////////////////////////
	KEY 1, ""
	PCOPY 0, 1
	CALL setup("Q U O T A T I O N")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : COLOR 2, 0
agn:
	LOCATE 3, 25: PRINT "Enter cost per litre..> "
	updwn% = 1
	LOCATE 3, 48: CALL inpnew(c$, 5.2, updwn%, "13,59")
	IF updwn% = 59 THEN GOTO xquote
	wrkcost! = VAL(c$)
	IF wrkcost! > 23! THEN GOTO agn
	s$ = SPACE$(12)
	 COLOR 6, 0: LOCATE 5, 2: PRINT "LIST   200Lt   D60Lt  D20Lt  P20lt  P10Lt    4Lt   2Lt   1Lt 500Ml 250Ml  Bulk"
	 LOCATE , 2: PRINT STRING$(78, 196)
	 COLOR 2, 0
	 FOR costsheet% = 0 TO 9
			IF mk!(costsheet%) <> 0 OR costsheet% = 0 THEN
				CALL getcost(costsheet%, c025, c05, c1, c2, c4, c10, c20d, c20p, c60, c200, cbulk)
				LOCATE costsheet% + 7, 2
				PRINT USING "\  \#####.## ####.## ###.## ###.## ###.## ###.## ##.## ##.## ##.## ##.## ##.##"; m$(costsheet%); c200; c60; c20d; c20p; c10; c4; c2; c1; c05; c025; cbulk
			END IF
		NEXT
	LOCATE , 2: COLOR 6: PRINT STRING$(78, 196)

	LOCATE , 2: PRINT USING "Can.  ###.##  ###.## ###.##  ##.##  ##.##  ##.## ##.## ##.## ##.## ##.## ##.##"; can.cancost!(10); can.cancost!(9); can.cancost!(8); can.cancost!(7); can.cancost!(6); can.cancost!(5); can.cancost!(4); can.cancost!(3);  _
can.cancost!(2); can.cancost!(1); can.cancost!(11)
	LOCATE , 2: PRINT USING "Labl. ###.##  ###.## ###.##  ##.##  ##.##  ##.## ##.## ##.## ##.## ##.## ##.##"; can.labelcost!(10); can.labelcost!(9); can.labelcost!(8); can.labelcost!(7); can.labelcost!(6); can.labelcost!(5); can.labelcost!(4);  _
can.labelcost!(3); can.labelcost!(2); can.labelcost!(1); can.labelcost!(11)
	LOCATE , 2: PRINT USING "Labr. ###.##  ###.## ###.##  ##.##  ##.##  ##.## ##.## ##.## ##.## ##.## ##.##"; can.labourcost!(10); can.labourcost!(9); can.labourcost!(8); can.labourcost!(7); can.labourcost!(6); can.labourcost!(5); can.labourcost!(4);  _
can.labourcost!(3); can.labourcost!(2); can.labourcost!(1); can.labourcost!(11)
	COLOR 2
	LOCATE , 2: PRINT USING "Tot.  ###.##  ###.## ###.##  ##.##  ##.##  ##.## ##.## ##.## ##.## ##.## ##.##"; can.allcost!(10); can.allcost!(9); can.allcost!(8); can.allcost!(7); can.allcost!(6); can.allcost!(5); can.allcost!(4); can.allcost!(3);  _
can.allcost!(2); can.allcost!(1); can.allcost!(11)
	GOTO agn
	'//////////////////////////
xquote:
	PCOPY 1, 0

END SUB

FUNCTION searchrmatfor (sfor$, stype$)
	'Search for cans index
	IF stype$ = "cans" THEN i% = msmisc.cansidx%
	IF i% < 1 OR i% > maxrmat% THEN i% = 1
	GET #38, i%, msrmat
	IF LEFT$(LCASE$(msrmat.desc1$), 10) = LEFT$(LCASE$(sfor$), 10) THEN
		found% = i%
	END IF
	IF found% = 0 THEN
		i% = 1
		GET #38, i%, msrmat
		DO WHILE NOT EOF(38)
			IF LEFT$(LCASE$(msrmat.desc1$), 10) = LEFT$(LCASE$(sfor$), 10) THEN
				found% = i%
				EXIT DO
			END IF

			GET #38, , msrmat: i% = i% + 1
		LOOP

	END IF

	IF found% < 1 OR found% > maxrmat% THEN found% = 1

	searchrmatfor = found%
END FUNCTION
