DECLARE SUB cvt.tnt (tnt$, tnt%, tntf$)
cf4b: '>>>>> F R O M   F O R M U L A <<<<<<<
	 tnt$ = acstk.form$
	 LOCATE fl% + 4, c1% + 5: CALL inpnew(tnt$, 104!, updwn%, "13,59,60")
	 acstk.form$ = tnt$
	 CALL cvt.tnt(tnt$, tnt%, tntf$)
	 LOCATE fl% + 4, c1% + 10: PRINT USING "- \                              \"; tnthed.desc$
RETURN


SUB export (rec%)

GET #3, rec%, acstk

export:
	y$ = STR$(acstk.no%)
	MID$(y$, 1, 1) = "0"
	y$ = "00000000" + y$
	z$ = RIGHT$(y$, 7)

	OPEN ".\tovb\f" + z$ + ".stk" FOR OUTPUT AS #98

	aa$ = STR$(acstk.no%)
	ab$ = acstk.Search$
	ac$ = STR$(acstk.ean13)
	ad$ = acstk.Desc1$
	ae$ = acstk.Desc2$
	af$ = acstk.suplr$
	ag$ = acstk.Size$
	ah$ = acstk.unit$
	ai$ = STR$(acstk.pack%)
	aj$ = STR$(acstk.Weight)
	ak$ = acstk.dgflag$
	al$ = acstk.form$
	am$ = acstk.offspec$
	an$ = acstk.Active$

	'Finalcial Description
	ba$ = acstk.taxinc$
	bb$ = acstk.salestaxcde$
	bc$ = STR$(acstk.PurCost)
	bd$ = STR$(acstk.purtax)
	be$ = STR$(acstk.wholesalecost)
	bf$ = acstk.disccdeone$
	bg$ = acstk.disccdetwo$

	bh$ = acstk.wholesalecde$
	bi$ = acstk.retailcde$
	bj$ = acstk.countercde$
	bk$ = acstk.tradecde$
	bl$ = acstk.contractcde$
	bm$ = acstk.industrialcde$
	bn$ = acstk.distributorcde$

	bo$ = STR$(acstk.retail)
	bp$ = STR$(acstk.counter)
	bq$ = STR$(acstk.trade)
	br$ = STR$(acstk.contract)
	bs$ = STR$(acstk.industrial)
	bt$ = STR$(acstk.distributor)

	bu$ = acstk.suplr4stdcost$
	bv$ = acstk.search4stdcost$

	'Stock holding
	ca$ = STR$(acstk.sohold%)
	cb$ = STR$(acstk.COGS)
	cc$ = STR$(acstk.soh%)
	cd$ = STR$(acstk.SOHValue)
	ce$ = STR$(acstk.SOO%)
	cf$ = STR$(acstk.sold%)
	cg$ = acstk.Date$

'detailed cogs
	d$ = STR$(acstk.filling)
	da$ = STR$(acstk.reo)
	DB$ = STR$(acstk.release)
	dc$ = STR$(acstk.curing)
	dd$ = STR$(acstk.finish)
	de$ = STR$(acstk.toolcost)
	df$ = STR$(acstk.cleaning)
	dg$ = STR$(acstk.packaging)
	dh$ = STR$(acstk.misccogs)
	di$ = STR$(acstk.totalcogs)
	ea$ = acstk.updatesoh$
	eb$ = STR$(acstk.minsoh)
	ec$ = acstk.prodtype$
	ed$ = STR$(acstk.cogsofstock)
	ee$ = DATE$ + " " + TIME$
IF acstk.no% > 0 THEN
WRITE #98, "F", aa$, ab$, ac$, ad$, ae$, af$, ag$, ah$, ai$, aj$, ak$, al$, am$, an$, ba$, bb$, bc$, bd$, be$, bf$, bg$, bh$, bi$, bj$, bk$, bl$, bm$, bn$, bo$, bp$, bq$, br$, bs$, bt$, bu$, bv$, ca$, cc$, cd$, ce$, cf$, cg$, cb$, d$, da$, DB$, dc$, _
 dd$, de$, df$, dg$, dh$, di$, ea$, eb$, ec$, ee$
END IF
CLOSE #98


END SUB

