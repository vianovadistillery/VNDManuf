DECLARE SUB get.markups ()
DECLARE SUB dolist (start%, finish%, runtype$, printsizes$)
DECLARE SUB get.can.labour (show%)
DECLARE SUB getcost (costsheet%, c200!, c60!, C21!, C20!, c10!, c4!, c2!, c1!, c05!, c025!, cbulk!)
DECLARE SUB print.line (costsheet%, runtype$, printsizes$)
DECLARE SUB quote ()
DECLARE SUB doheading (costsheet%, runtype$, printsizes$)
'.dc - Complete
'>>>>>>>>>>>>>>>>>>> costing listing      <<<<<<<<<<<<<<<<<<<<<<<<
'$INCLUDE: '\tpmanuf\src\pgmhead.INC'
''$INCLUDE: '\tpmanuf\src\pgmerr.INC'
	DIM SHARED mk!(11), mkon%(11)
	DIM SHARED m$(11), ff!
	DIM SHARED can.labour!(11) '200lt,60lt,20lt,,10lt,20lt,4lt,2lt,1lt,500ml,250ml,BULK
	DIM SHARED wrkcost!, fetch%
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\msrmat.INC'
	'$INCLUDE: '\tpmanuf\src\msmisc.INC'
	'$INCLUDE: '\tpmanuf\src\msmkp.INC'
	'$INCLUDE: '\tpmanuf\src\tnthed.INC'
	'$INCLUDE: '\tpmanuf\src\forhed.INC'
	'$INCLUDE: '\tpmanuf\src\tnthedx.INC'
	'$INCLUDE: '\tpmanuf\src\forhedx.INC'

	GET #36, 1, msmisc
	GET #63, 1, tnthedx


	m$(0) = "Raw Material Cost  "
	CALL setup("CENTRAL COSTING REPORT")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit      F5-Cans/Labels/Labour      F9-Swap size       F10-Swap R.M.C  "; : COLOR 2, 0
	CALL get.markups
	CALL get.can.labour(0)
	printsizes$ = "A": runtype$ = "A"

start:
	COLOR 14: LOCATE 4, 21
	rep1$ = "All sizes     "
	IF printsizes$ = "M" THEN rep1$ = "Major sizes   "
	IF runtype$ = "A" THEN rep1$ = rep1$ + "- Allocated R.M.C." ELSE rep1$ = rep1$ + "- Real R.M.C.       "
	PRINT rep1$
	COLOR 2, 0

	FOR i% = 0 TO 9
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
	CASE 63: CALL get.can.labour(-1)
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
	IF costsheet% <> 10 AND printsizes$ = "A" THEN PRINT #99, "         PRODUCT               20Lt.. 20Lt.. 10Lt.. 4Lt.. 2Lt.. 1Lt.. .5Lt. .25Lt"
	IF costsheet% <> 10 AND printsizes$ = "M" THEN PRINT #99, "         PRODUCT               20Lt.. 10Lt..  4Lt.. 1Lt.."
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

		STDOUT$ = "LPT1"
		'STDOUT$ = "junk.jnk"
		OPEN STDOUT$ FOR OUTPUT AS #99
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

		IF idx% MOD 100 = 0 THEN CALL sndmsg("Record " + STR$(idx%))
		idx% = idx% + 1
		LOOP
	PRINT #99, CHR$(12)
	CLOSE 99

680
	NEXT

END SUB

SUB get.can.labour (show%)
	IF NOT show% THEN GOTO get.can.labour99

	CALL BOX(2, 3, 79, 21, 0, 0, 0)
	DIM sizedesc$(10)
	sizedesc$(0) = "200lt"
	sizedesc$(1) = " 60lt"
	sizedesc$(2) = " 20lt"
	sizedesc$(3) = " 20lt"
	sizedesc$(4) = " 10lt"
	sizedesc$(5) = "  4lt"
	sizedesc$(6) = "  2lt"
	sizedesc$(7) = "  1lt"
	sizedesc$(8) = "500ml"
	sizedesc$(9) = "250ml"
	sizedesc$(10) = " Bulk"

	IF msmisc.cansidx% < 1 THEN msmisc.cansidx% = 1
	IF msmisc.labelidx% < 1 THEN msmisc.labelidx% = 1
	IF msmisc.labouridx% < 1 THEN msmisc.labouridx% = 1
	mode$ = "cans.."

cf1:
	COLOR 6, 0
	LOCATE 6, 15: PRINT "Costed   Rmat.Description                   Cost"
	LOCATE 7, 15: PRINT "------------------------------------------------"
	COLOR 2, 0
	FOR i% = 0 TO 9
		SELECT CASE mode$
		CASE "cans..": rec% = msmisc.cansidx% + i%
		CASE "labels": rec% = msmisc.labelidx% + i%
		CASE "labour": rec% = msmisc.labouridx% + i%
		CASE ELSE
		END SELECT

		GET #38, rec%, msrmat
		LOCATE , 16
		PRINT USING "& | #### & $$###.##"; sizedesc$(i%); msrmat.no%; msrmat.desc1$; msrmat.UseCost
		NEXT
	LOCATE 5, 15: PRINT USING "Start number for \    \.> "; mode$
	a$ = ""
	LOCATE 5, 40: CALL inpnew(a$, 4!, updwn%, "59-60,13")
	IF VAL(a$) <> msmisc.cansidx% AND VAL(a$) > 0 THEN
		SELECT CASE mode$
		CASE "cans..":  msmisc.cansidx% = VAL(a$)
		CASE "labels": msmisc.labelidx% = VAL(a$)
		CASE "labour":  msmisc.labouridx% = VAL(a$)
		CASE ELSE
		END SELECT
		GOTO cf1
		END IF

	IF mode$ = "cans.." THEN mode$ = "labels": GOTO cf1
	IF mode$ = "labels" THEN mode$ = "labour": GOTO cf1


	CALL BOX(2, 3, 79, 21, 0, 0, 0)

get.can.labour99:
	FOR c% = 0 TO 10'* CAN,LABEL,LABOUR ******(WAS 1- 9)(WAS 0- 9)*********
		GET #38, 3400 + c%, msrmat: can.labour!(c%) = msrmat.UseCost'* cost of can
		GET #38, 3420 + c%, msrmat: can.labour!(c%) = can.labour!(c%) + msrmat.UseCost '* Cost of LABEL
		GET #38, 3440 + c%, msrmat: can.labour!(c%) = can.labour!(c%) + msrmat.UseCost '* Cost of LABOUR
		NEXT

END SUB

SUB get.markups

	mk!(0) = 0: mkon%(0) = 0: m$(0) = "GATE COST                     "
	FOR i% = 1 TO 9
		GET #37, i%, msmkp
		mk!(i%) = CVS(msmkp.mk$)
		m$(i%) = msmkp.mm$
		mkon%(i%) = CVI(msmkp.mkon$)
		NEXT

	GET #37, 10, msmkp
	ff! = CVS(msmkp.mk$)

END SUB

SUB getcost (costsheet%, c200!, c60!, C21!, C20!, c10!, c4!, c2!, c1!, c05!, c025!, cbulk!)
'//////////////////////////////////////////////////
'* Get cost per each label
'//////////////////////////////////////////////////
	'>>> Add in fuckup factor <<<
	'wrkcost! = wrkcost! + wrkcost! * ff!

	'>>> Find cost of item with can,label,labour and no markup  <<<
	c200! = can.labour!(0) + (wrkcost! * 200)
	c60! = can.labour!(1) + (wrkcost! * 60)
	C21! = can.labour!(2) + (wrkcost! * 20)
	C20! = can.labour!(3) + (wrkcost! * 20)
	c10! = can.labour!(4) + (wrkcost! * 10)
	c4! = can.labour!(5) + (wrkcost! * 4)
	c2! = can.labour!(6) + (wrkcost! * 2)
	c1! = can.labour!(7) + (wrkcost! * 1)
	c05! = can.labour!(8) + (wrkcost! * .5)
	c025! = can.labour!(9) + (wrkcost! * .25)
	cbulk! = can.labour!(10) + (wrkcost! * 1)

	'>>>---------------------------------------------------------------<<<
	'>>>    Now add the calculated margin off each list based on list
	'>>>---------------------------------------------------------------<<<

		mult! = 1 + mk!(costsheet%)

		i% = costsheet%
		DO WHILE mkon%(i%) > 0
			i% = mkon%(i%)
			mult! = mult! * (1 + mk!(i%))
			LOOP


		c200! = mult! * c200!
		c60! = mult! * c60!
		C21! = mult! * C21!
		C20! = mult! * C20!
		c10! = mult! * c10!
		c4! = mult! * c4!
		c2! = mult! * c2!
		c1! = mult! * c1!
		c05! = mult! * c05!
		c025! = mult! * c025!
		cbulk! = mult! * cbulk!

END SUB

SUB print.line (costsheet%, runtype$, printsizes$) STATIC
'//////////////////////////////////////////////////
'// Get cost for each label in then array
'//////////////////////////////////////////////////
	IF fetch% THEN CALL doheading(costsheet%, runtype$, printsizes$): lin% = 0

	CALL getcost(costsheet%, c200, c60, C21, C20, c10, c4, c2, c1, c05, c025, cbulk)

	IF costsheet% = 10 THEN
		s$ = SPACE$(12)
		PRINT #99, USING "&  \   \   \                       \    #####.###"; s$; tnthed.tnta$; tnthed.desc$; wrkcost!
		ELSE
		IF printsizes$ = "A" THEN PRINT #99, USING "\   \\                       \ ###.## ###.## ###.## ##.## ##.## ##.## #.## #.##"; tnthed.tnta$; tnthed.desc$; C21; C20; c10; c4; c2; c1; c05; c025
		IF printsizes$ = "M" THEN PRINT #99, USING "\   \\                       \ ###.## ###.## ###.## ##.## ##.##"; tnthed.tnta$; tnthed.desc$; C21; C20; c10; c4; c1
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
	'COLOR 6, 0: LOCATE 5, 2: PRINT "LIST   200Lt    60Lt   20Lt   10Lt    5Lt    4Lt   2Lt   1lt 500ml 250ml  BULK"
	COLOR 6, 0: LOCATE 5, 2: PRINT "LIST   200Lt   D60Lt  D20Lt  P20Lt  P10Lt    4Lt   2Lt   1Lt 500Ml 250Ml  BULK"
	LOCATE , 2: PRINT STRING$(78, 196)
	COLOR 2, 0
	FOR costsheet% = 0 TO 10
		IF mk!(costsheet%) <> 0 OR costsheet% = 0 THEN
			CALL getcost(costsheet%, c200, c60, C21, C20, c10, c4, c2, c1, c05, c025, cbulk)
			LOCATE costsheet% + 7, 2
			PRINT USING "\  \ ####.## ####.## ###.## ###.## ###.## ###.## ##.## ##.## ##.## ##.## ##.##"; m$(costsheet%); c200; c60; C21; C20; c10; c4; c2; c1; c05; c025; cbulk
			END IF
		NEXT
	LOCATE , 2: COLOR 6: PRINT STRING$(78, 196)
	LOCATE , 2: PRINT USING "Pack ####.## ####.## ###.## ###.## ###.## ###.## ##.## ##.## ##.## ##.## ##.##"; can.labour!(0); can.labour!(1); can.labour!(2); can.labour!(3); can.labour!(4); can.labour!(5); can.labour!(6); can.labour!(7); can.labour!(8 _
); can.labour!(9); can.labour!(10)
	COLOR 2
	GOTO agn
	'//////////////////////////
xquote:
	PCOPY 1, 0

END SUB

