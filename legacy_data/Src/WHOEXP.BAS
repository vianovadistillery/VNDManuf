typefields% = -1
	'$INCLUDE: '\tpmanuf\src\WHOF.INC'
	'$INCLUDE: '\tpmanuf\src\CUS.INC'
	'$INCLUDE: '\tpmanuf\src\SUP.INC'
	'$INCLUDE: '\tpmanuf\src\pickup.INC'
rec% = 1
last% = LOF(44) / LEN(CUS)

FOR rec% = 1 TO last%

GET #44, rec%, CUS

ascii = ASC(CUS.stype$)


IF ascii = 0 THEN GOTO skip:
PRINT CUS.search$ + CUS.stype$

DIM ea$(6), eb$(6), ec$(6), ed$(6), ee$(6), ef$(6), eg$(6)
		ext$ = ".\export\" + CUS.search$ + CUS.stype$ + ".who"
OPEN ext$ FOR OUTPUT AS #97
			a$ = STR$(CVI(CUS.sno$))
			b$ = CUS.search$ + CUS.stype$
			c$ = CUS.sname
			d$ = CUS.saddr$
			e$ = CUS.saddr2$
			f$ = CUS.suburb$
			g$ = CUS.state$
			h$ = CUS.spcode$
			i$ = CUS.spbox$
			j$ = CUS.spboxsub$
			k$ = CUS.spboxpcode$
			l = CVS(CUS.sgl$)
			m$ = CUS.email$
			n$ = CUS.www$
			o$ = CUS.pstnCC$
			p$ = CUS.scontTitle$
			q$ = CUS.scont$
			r$ = CUS.sphone$
			s$ = CUS.sphone1$
			t$ = CUS.taxe$
			u$ = CUS.rep$
			v$ = CUS.callfreq$
			w$ = CUS.sdays$
			X$ = STR$(CVS(CUS.sterms))
			y$ = CUS.daysmax$

			aa$ = STR$(CVS(CUS.scur$))
			ab$ = STR$(CVS(CUS.s0$))
			ac$ = STR$(CVS(CUS.s30$))
			ad$ = STR$(CVS(CUS.s60$))
			ae$ = STR$(CVS(CUS.s90$))
			af$ = STR$(CVS(CUS.opn$))
			ag$ = STR$(CVS(CUS.opn30$))
			ah$ = STR$(CVS(CUS.opn60$))
			ak$ = STR$(CVS(CUS.advalue$))
			al$ = STR$(CVS(CUS.climit$))

			'Pickup info
			ba$ = CUS.spnum$
			bb$ = CUS.spname$
			bc$ = CUS.spsub$

			'Invoice groups
			ca$ = CUS.sdist$
			cb$ = CUS.sret$
			cc$ = CUS.countercde$
			cd$ = CUS.tradecde$
			ce$ = CUS.contractcde$
			cf$ = CUS.industrialcde$
			cg$ = CUS.scont1$
			ch$ = CUS.scont2$
			ci$ = CUS.wholesalecde$

			'Audit trail
			da$ = CUS.addocnum$
			DB$ = CUS.addate$

			dc$ = CUS.sdate$
			dd$ = CUS.Active$

			'Personal details
			FOR i% = 1 TO 6
				ea$(i%) = CUS.ContactFirstName$(i%)
				eb$(i%) = CUS.ContactSurName$(i%)
				ec$(i%) = CUS.ContactTitle$(i%)
				ed$(i%) = CUS.ContactPhone$(i%)
				ee$(i%) = CUS.ContactMobile$(i%)
				ef$(i%) = CUS.ContactFax$(i%)
				eg$(i%) = CUS.Contactemail$(i%)
			NEXT i%

			fa$ = CUS.BO$
			fb$ = CUS.abn$
			fc$ = CUS.bankcde$
			fd$ = CUS.bankacct$
			'fe$ = STR$(cus.myob)
			'ff$ = cus.cardid$

			'***** the pickup address off pickup file
			sprec% = VAL(MID$(CUS.spname$, 1, 3))
			IF sprec% >= 1 AND sprec% <= 999 THEN
				GET #50, sprec%, pickup
				ga$ = pickup.pno$
				gb$ = pickup.pname1$
				gc$ = pickup.pname2$
				gd$ = pickup.pname3$
				ge$ = pickup.pname4$
				gf$ = pickup.pactive$
				gg$ = pickup.pphone1$
				gh$ = pickup.pphone2$
			ELSE
				ga$ = ""
				gb$ = ""
				gc$ = ""
				gd$ = ""
				ge$ = ""
				gf$ = ""
				gg$ = ""
				gh$ = ""
			END IF

			gi$ = DATE$ + " " + TIME$

	WRITE #97, "L1", ch%, a$, b$, c$, d$, e$, f$, g$, h$, i$, j$, k$, l, m$, n$, o$, p$, q$, r$, s$, t$, u$, v$, X$, y$, aa$, ab$, ac$, ad$, ae$, af$, ag$, ai$, aj$, ak$, al$, ba$, bb$, bc$, ca$, cb$, cd$, ce$, cf$, cg$, ci$, da$, DB$, dc$, dd$, fa$,  _
fb$
	WRITE #97, "L2", fc$, fd$, ea$(1), eb$(1), ec$(1), ed$(1), ee$(1), ef$(1), eg$(1), ea$(2), eb$(2), ec$(2), ed$(2), ee$(2), ef$, ea$(3), eb$(3), ec$(3), ed$(3), ee$(3), ef$(3), eg$(3), ea$(4), eb$(4), ec$(4), ed$(4), ee$(4), ef$(4), eg$(4)
	WRITE #97, "L3", ga$, gb$, gc$, gd$, ge$, gf$, gg$, gh$, gi$
	CLOSE #97

skip:
NEXT

END

