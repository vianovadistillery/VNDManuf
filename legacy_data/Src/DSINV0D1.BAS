DECLARE SUB DoSort (sortarray() AS ANY, Low AS INTEGER, High AS INTEGER)
DECLARE SUB getdt (OSCurrency$, updwn%)
DECLARE SUB accbrowse (rec%)
DECLARE SUB add.bo.msg (updwn%)
DECLARE SUB add.up.order (tot.ltact!, tot.ord!, tot.ext!)
DECLARE SUB addmessage (invmsg1$, invmsg2$, invmsg3$, invmsg4$)
DECLARE SUB cf8 (l%, d.elem%, newdata$)
DECLARE SUB change.disc (discovr!)
DECLARE SUB chglin (ln%, l%, d.elem%, updwn%)
DECLARE SUB delOrder (hord%, n%, clr%, autodel$, thissup$, norders%)
DECLARE SUB dsply (sno%, norders%)
DECLARE SUB dsplyLine (l%, d.elem%)
DECLARE SUB dsporders (dspstart%, norders%, custin$)
DECLARE SUB ean13 (in$, dind%)
DECLARE SUB findnext (hord%, norders%, ok%)
DECLARE SUB findorders (thissup$, norders%, hord%)
DECLARE FUNCTION funclimit$ (climit!)
DECLARE SUB get.order.vs (hord%, updwn%)
DECLARE SUB getname (tender$, updwn%)
DECLARE SUB limit.warn (s90!, s60!, s30!, scur!, climit!, updwn%, allow$)
DECLARE SUB linkedl (rrn%(), n%, firstrec%, ord%, chd%)
DECLARE SUB loadLine (m%, il%, ditem%, ordqty%, Invqty%, price!, otprice$, pikqty%)
DECLARE SUB open.cash.drawer ()
DECLARE SUB openpslip (opt%)
DECLARE SUB parse (hord%, opt%, cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, invmsg1$, invmsg2$)
DECLARE SUB prtinv (hord%, opt%, cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, OSCurrency$)
DECLARE SUB prtjobslip (hord%, opt%, thissup$, sno%)
DECLARE SUB prtpslip (hord%, opt%, discovr!)
DECLARE SUB rightprice (price!)
DECLARE SUB search.month (rec%, begyymd$)
DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB setaudit (n%)
DECLARE SUB UpdateOrder (hord%, updwn%)

COMMON SHARED maxsup%, maxform%, maxrmat%, maxacc%, maxtypes, maxcus%, maxord%
COMMON SHARED custin$, sno%, hasip%
COMMON SHARED qk$, keyl%, rep$
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "DSMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CONST maxlines% = 45 '
	CONST GST! = 10  '10%
	DIM SHARED C%(8), in$(maxlines%, 15), rrn%(maxlines%)
	'1=qty%,2=size,3=unit,4=itm,5=desc,6=price,7=SOH,8=ext
	'9=picked,10=ordqty%,11=Invqty,12=BoFlag,13=save qty
	'14=Save item, 15=Overtyped price

	DIM SHARED orders%(1001)
	DIM SHARED mode$, beg$, status$, vmode$
	DIM SHARED TaxRate!, DiscRate!
	DIM SHARED ext.has.changed%, rec50%, ctl%, cash%
	DIM SHARED vdisc!, Rate!, discovr!, climit!, ovrPrice!
	DIM SHARED tot.gst!, tot.ext!, tot.allup!, tot.gp!
	DIM SHARED skipexit%
	DIM SHARED doc.type$, formtype$
	DIM SHARED tot.ord!, tot.ltact, tot.ltinv, tot.dollr, tot.items&
	DIM SHARED hord%
	DIM SHARED newsearch$
	DIM SHARED bysearch$
	DIM SHARED search.key$
	DIM SHARED tot.qty, Tot.taxvol
	DIM SHARED tot.dg200%, tot.dg60%, tot.dg20%, tot.dg10%, tot.dg4%, tot.dg2%, tot.dg1%, tot.dg850%, tot.dg500%, tot.dg300%, tot.dg250%, tot.dglt!
	DIM SHARED extdisc!, inv.lt.printed!
	DIM SHARED tender$
	DIM SHARED invmsg1$, invmsg2$, invmsg3$, invmsg4$
	
	DIM SHARED auditfile$(15), naudit%, acstkf$
	DIM SHARED ean$


	keyl% = 20: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)

	DATA 2,7,10,13,18,56,63,72
	FOR i% = 1 TO 8: READ C%(i%): NEXT
	RESET
	typefields% = -1
	acstkf$ = "..."
	parm$ = ENVIRON$("PARM$")
	IF VAL(parm$) > 0 THEN pass.getcust% = -1: custin$ = parm$: updwn% = 13
	parm2$ = ENVIRON$("PARM2$")
	IF parm2$ = "PRE..." THEN acstkf$ = "PRE"
		'$INCLUDE: '\tpmanuf\src\iprice.inc'
		'$INCLUDE: '\tpmanuf\src\whof.inc'
		'$INCLUDE: '\tpmanuf\src\cusx.inc'
		'$INCLUDE: '\tpmanuf\src\supx.inc'
		'$INCLUDE: '\tpmanuf\src\cus.inc'
		'$INCLUDE: '\tpmanuf\src\ACSTK.INC'
		'$INCLUDE: '\tpmanuf\src\ASAUDIT.INC'
		'$INCLUDE: '\tpmanuf\src\ordhed.inc'
		'$INCLUDE: '\tpmanuf\src\orddet.inc'
		'$INCLUDE: '\tpmanuf\src\ordprt.inc'

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

SUB accbrowse (rec%) STATIC
	 CALL setup("  B R O W S E    F I L E")
	 btype$ = "cost"
	 cbtm$ = " No.Stock description.                  Size  Code Distr. Indus. Trade. Count."
	 kbtm$ = " No.Stock description.                  Size  Distr. COGS    GPC   RMC    GPR "
	 dbtm$ = " No.Stock description.                  Size  Code  A D Barcode       Search  "
	 COLOR 6: LOCATE 3, 2: PRINT cbtm$
	 COLOR 0, 3: LOCATE 25, 1: PRINT SPACE$(80);
	 COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit   F3=Search     F5-Swap     F6-Search Duplicate Barcodes"; : LOCATE 25, 71: PRINT CHR$(24); CHR$(25); "-Move"; : COLOR 2, 0
	 maxpag% = 20
	 IF rec% < 1 OR rec% > maxacc% THEN rec% = 1
	 updwn% = 13: bpos$ = STR$(rec%)
	 xsearch$ = ""
	 showdup% = 0
	 skip$ = "Y"
	 REDIM bar#(maxacc%)
	 cleanbar% = 0

	 '>>>>> Get next REC%ord to browse from.
accBROWSE.A:
	LOCATE 2, 25
	COLOR 7: PRINT "¹ ";
	COLOR 2: PRINT "Start browse from..>      ";
	COLOR 7: PRINT "Ì": COLOR 2
	COLOR 2
	IF skip$ = "Y" THEN
		skip$ = "N"
	ELSE
		bpos$ = ""
		LOCATE 2, 47: CALL inpnew(bpos$, 205!, updwn%, "13,59,61,63-64,68,72,73,80,81")
	END IF

	IF updwn% = 61 THEN
		LOCATE 2, 25: PRINT "Search..>";
		CALL inpnew(xsearch$, 120!, updwn%, "13,59,61,63-64,72,73,80,81")
		bpos$ = "1"
		updwn% = 13
	END IF


	IF updwn% = 13 THEN
			IF VAL(bpos$) = 0 AND LEN(bpos$) > 0 THEN
				keyl% = 20: qk$ = SPACE$(keyl%)
				sa$ = bpos$
				sa$ = UCASE$(sa$): LSET qk$ = sa$
				CALL index("CHAIN", ind%, qk$, 7, keyl%)
				IF ind% < 0 AND qk$ < sa$ THEN CALL index("READ ", ind%, qk$, 7, keyl%)
				bpos$ = MID$(STR$(ind%), 2)
			END IF

			IF VAL(bpos$) = 0 THEN bpos$ = STR$(e%)
			rec% = VAL(bpos$)
			IF rec% < 1 OR rec% > maxacc% THEN rec% = 1
	END IF
	IF updwn% = 59 THEN rec% = s%: GOTO X.accbrowse
	IF updwn% = 63 THEN '***** Swap browse type
		COLOR 6: LOCATE 3, 2
		SELECT CASE btype$
		CASE "cost": btype$ = "key ": PRINT kbtm$
		CASE "key ": btype$ = "data": PRINT dbtm$
		CASE "data": btype$ = "cost": PRINT cbtm$
		END SELECT
		COLOR 2, 0
		rec% = s%
	END IF
	IF updwn% = 64 THEN 'Search for duplicate barcodes
		IF showdup% THEN
			showdup% = 0
		CALL sndmsg("")
		ELSE
			showdup% = -1
		CALL sndmsg("Subset of duplicates")
		END IF

		rec% = 1
		GET #3, rec%, acstk
		DO WHILE rec% < maxacc%

			'>-Clean up malformed barcodes.
			IF acstk.ean13 <> 0 AND cleanbar% THEN
			IF acstk.ean13 < 9300000000000# OR acstk.ean13 > 9399999999999# OR rec% <> acstk.no THEN
				acstk.ean13 = 0
				PUT #3, rec%, acstk
			END IF
			END IF

			IF rec% = acstk.no THEN
				bar#(rec%) = acstk.ean13
			END IF
			GET #3, , acstk: rec% = rec% + 1
		LOOP

		'-> Cleaning the dups
		IF cleanbar% THEN
			rec% = 1
			GET #3, rec%, acstk
			DO WHILE rec% < maxacc%
				IF rec% = acstk.no THEN

					FOR i% = 1 TO maxacc%
						IF i% <> rec% AND bar#(i%) = acstk.ean13 AND acstk.ean13 > 0 THEN

							GET #3, i%, acstk
							acstk.ean13 = 0
							PUT #3, i%, acstk

							GET #3, rec%, acstk
							acstk.ean13 = 0
							PUT #3, rec%, acstk


						END IF
					NEXT

				END IF
				GET #3, , acstk: rec% = rec% + 1
			LOOP
		CALL sndmsg("Cleanup complete.")
			cleanbar% = 0
			rec% = 1
			GOTO accBROWSE.A
		END IF
		rec% = 1
	END IF

	IF updwn% = 68 THEN
	CALL sndmsg("Cleanup dup barcode enabled.")
		cleanbar% = -1
		rec% = 1
	END IF

	IF updwn% = 72 THEN 'UP arrow
		lin% = 1
		rec% = s%
		DO WHILE lin% > 0 AND rec% > 1
			rec% = rec% - 1
			GET #3, rec%, acstk
			IF acstk.no% = rec% THEN lin% = lin% - 1
			LOOP
	END IF
	IF updwn% = 80 THEN 'Down arrow
		rec% = s% + 1
		GET #3, rec%, acstk
		DO WHILE acstk.no <> rec% AND rec% < maxacc%
			rec% = rec% + 1
			GET #3, rec%, acstk
			LOOP

	END IF
	IF updwn% = 73 THEN 'pg up
		lin% = maxpag%
		rec% = s%
		DO WHILE lin% > 0 AND rec% > 1
			rec% = rec% - 1
			GET #3, rec%, acstk
			IF acstk.no% = rec% THEN lin% = lin% - 1
			LOOP
	END IF
	IF updwn% = 81 THEN 'pg dw
		rec% = e% + 1
	END IF


'///////////////////////////////////////////////////////////////////////////
'>>--- L I S T   A   P A G E
'///////////////////////////////////////////////////////////////////////////
	'Given rec% as the first record
	GET #3, rec%, acstk
	lin% = 0: missed% = 0
	DO UNTIL lin% = maxpag% OR rec% > maxacc%'OR missed% > 400

		'Selection
		ok% = -1
		IF acstk.no% <> rec% THEN ok% = 0
		IF btype$ = "key " AND UCASE$(acstk.Active$) <> "A" THEN ok% = 0

		IF showdup% THEN
			ok% = 0
			IF acstk.ean13 > 0 THEN
				FOR i% = 1 TO maxacc%
					IF bar#(i%) = acstk.ean13 AND i% <> rec% AND acstk.ean13 > 0 THEN
						ok% = -1
						EXIT FOR
					END IF
				NEXT
			END IF
		END IF

		IF ok% AND xsearch$ > "" THEN
			ok0% = 0
			IF ok0% = 0 AND INSTR(LCASE$(acstk.desc1$), LCASE$(xsearch$)) > 0 THEN ok0% = -1
			IF ok0% = 0 AND INSTR(LCASE$(acstk.desc2$), LCASE$(xsearch$)) > 0 THEN ok0% = -1
			IF NOT ok0% THEN ok% = 0
		END IF


		IF ok% THEN prttype$ = btype$
		IF NOT ok% THEN prttype$ = "missed"
		bc$ = " ": IF acstk.ean13 > 9300 THEN bc$ = CHR$(127)


		SELECT CASE prttype$
		CASE "cost"
			LOCATE 4 + lin%, 2
			IF acstk.counter > 999 THEN                                                                '
				PRINT USING "####\                       \\        \!\ \\\ \  \####   ####   ####   ####   "; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; acstk.suplr$; acstk.distributor; acstk.industrial; acstk.trade; acstk.counter
			ELSE
				PRINT USING "####\                       \\        \!\ \\\ \  \ ###.## ###.## ###.## ###.##"; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; acstk.suplr$; acstk.distributor; acstk.industrial; acstk.trade; acstk.counter
			END IF
			COLOR 3, 0
			LOCATE 4 + lin%, 2 + 46
			PRINT USING "\  \"; acstk.suplr$
			LOCATE 4 + lin%, 2
			PRINT USING "####"; acstk.no%
			COLOR 2, 0
			COLOR 10, 0: LOCATE 4 + lin%, 41: PRINT bc$; : COLOR 2, 0'BC

			lin% = lin% + 1
			IF lin% = 1 THEN s% = rec%
			e% = rec%
		CASE "key "
			LOCATE 4 + lin%, 2
			IF acstk.distributor > 999 THEN
				kbtm$ = " No.Stock description.                  Size      Distr. COGS  GPC   RMC    GPR "
				PRINT USING "####\                       \\        \!\ \\\   #### #### ###.#% #### ###.#%"; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; acstk.distributor; acstk.cogs; acstk.gpc; acstk.rmc; acstk.gpr
			ELSE
				PRINT USING "####\                       \\        \!\ \\\ ###.## ###.## ###%  ###.## ###% "; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; acstk.distributor; acstk.cogs; acstk.gpc; acstk.rmc; acstk.gpr
			END IF
			COLOR 3, 0
			LOCATE 4 + lin%, 2
			PRINT USING "####"; acstk.no%
			COLOR 2, 0
			COLOR 10, 0: LOCATE 4 + lin%, 41: PRINT bc$; : COLOR 2, 0'BC

			lin% = lin% + 1
			IF lin% = 1 THEN s% = rec%
			e% = rec%
		CASE "data"
			LOCATE 4 + lin%, 2
			IF acstk.ean13 > 0 THEN
				PRINT USING "####\                       \\        \!\ \\\ \  \  ! ! ############# \      \"; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; acstk.suplr$; acstk.Active$; acstk.dgflag$; acstk.ean13; acstk.search$
			ELSE
				PRINT USING "####\                       \\        \!\ \\\ \  \  ! !               \      \"; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; acstk.suplr$; acstk.Active$; acstk.dgflag$; acstk.search$
			END IF
			COLOR 3, 0
			LOCATE 4 + lin%, 2 + 46
			PRINT USING "\  \"; acstk.suplr$
			LOCATE 4 + lin%, 2
			PRINT USING "####"; acstk.no%
			COLOR 2, 0
			COLOR 10, 0: LOCATE 4 + lin%, 41: PRINT bc$; : COLOR 2, 0'BC

			lin% = lin% + 1
			IF lin% = 1 THEN s% = rec%
			e% = rec%

		CASE "missed"
			missed% = missed% + 1
		END SELECT

	bad% = 0
	tmp$ = acstk.suplr4stdcost$ + acstk.search4stdcost
	FOR i% = 1 TO LEN(tmp$)
		IF MID$(tmp$, i%, 1) < " " THEN bad% = -1: EXIT FOR
		IF MID$(tmp$, i%, 1) > "~" THEN bad% = -1: EXIT FOR
	NEXT
	IF bad% THEN
		acstk.suplr4stdcost$ = SPACE$(5)
		acstk.search4stdcost$ = SPACE$(10)
		PUT #3, rec%, acstk
	END IF

	GET #3, , acstk: rec% = rec% + 1
	LOOP


	'IF missed% > 400 THEN
	'  LOCATE , 2: PRINT "More than 400 records searched without an active record being found."; CHR$(FNE)
	'  lin% = lin% + 1
	'END IF
	FOR i% = lin% + 1 TO maxpag%: LOCATE 3 + i%, 2: PRINT SPACE$(78): NEXT


	GOTO accBROWSE.A   '***** Get next REC%ord to browse from

X.accbrowse:

END SUB

SUB DoSort (sortarray() AS ArrayFmtIprice, Low AS INTEGER, High AS INTEGER)

DIM Lower AS INTEGER
DIM Higher AS INTEGER
DIM RandIndex AS INTEGER
DIM Partition AS INTEGER

IF Low < High THEN

				' *** Only two elements in this subdivision ***
				' *** Swap them if they are out of order, then end recursive calls: ***

				IF High - Low = 1 THEN
								IF sortarray(Low).item% > sortarray(High).item% THEN
												SWAP sortarray(Low), sortarray(High)
								END IF

				ELSE

								'*** Pick a pivot element at random, then move it to the end ***

								RandIndex = INT(RND * (High - Low + 1)) + Low
								SWAP sortarray(High), sortarray(RandIndex)
								Partition = sortarray(High).item%
								DO

												'*** Move in from both sides towards the pivot element ***

												Lower = Low
												Higher = High
												DO WHILE (Lower < Higher) AND (sortarray(Lower).item% <= Partition)
																Lower = Lower + 1
												LOOP

												DO WHILE (Higher > Lower) AND (sortarray(Higher).item% >= Partition)
																Higher = Higher - 1
												LOOP

												'*** If pivot element not reached, it means that ***
												'*** two elements on either side are out of order, ***
												'*** so swap them ***

												IF Lower < Higher THEN
																SWAP sortarray(Lower), sortarray(Higher)
												END IF

								LOOP WHILE Lower < Higher

								'*** Move the pivot element back to its proper place in the array ***

								SWAP sortarray(Lower), sortarray(High)

								'*** Recursively call the SortArray sub ***
								'*** Pass the smaller subdivision first to use less stack space ***

								IF (Lower - Low) < (High - Lower) THEN
												DoSort sortarray(), Low, Lower - 1
												DoSort sortarray(), Lower + 1, High
								ELSE
												DoSort sortarray(), Lower + 1, High
												DoSort sortarray(), Low, Lower - 1
								END IF
				END IF
END IF

END SUB

SUB individualprices
'-- Determine Individual prices for this customer
		iprec% = 1
		adnew% = 0
		bpos$ = STR$(1)
		
ipstart:
		nextrec% = -1
		REDIM ipa(0 TO 0) AS ArrayFmtIprice
		iplast% = LOF(4) / LEN(iprice)
		FOR ip% = 1 TO iplast%
			GET #4, ip%, iprice
			IF nextrec% = -1 AND iprice.no% <> ip% THEN nextrec% = ip%
			IF iprice.search$ = custin$ THEN
				hasip% = -1
				
				'expand dynamic array ipa
				REDIM PRESERVE ipa(LBOUND(ipa) TO UBOUND(ipa) + 1) AS ArrayFmtIprice
				ipa(UBOUND(ipa)).no% = iprice.no%
				ipa(UBOUND(ipa)).item% = iprice.item%
				ipa(UBOUND(ipa)).price = iprice.iprice
			END IF
		NEXT
		IF nextrec% = -1 THEN nextrec% = iplast% + 1

		IF hasip% = 0 THEN
				REDIM PRESERVE ipa(LBOUND(ipa) TO UBOUND(ipa) + 1) AS ArrayFmtIprice
				ipa(UBOUND(ipa)).no% = 0
				ipa(UBOUND(ipa)).item% = 1
				ipa(UBOUND(ipa)).price = 0
		END IF

		IF UBOUND(ipa) > 0 THEN CALL DoSort(ipa(), 1, UBOUND(ipa))


	 CALL setup("  I N D I V I D U A L   P R I C I N G")
	 
	 maxip% = LOF(4) / LEN(iprice)
	 btype$ = "key "
	 cbtm$ = " No.Stock description.                  Size  Code Distr. Indus. Trade. Count."
	 kbtm$ = " No.Stock description.                  Size  Current Indiv  GP   RMC    GPR "
	 dbtm$ = " No.Stock description.                  Size  Date     Notes....              "
	 COLOR 6: LOCATE 3, 2: PRINT kbtm$
	 COLOR 0, 3: LOCATE 25, 1: PRINT SPACE$(80);
	 COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit  F2-Add  F3=Search  F4-Delete  F5-Swap  F10-Change      "; : LOCATE 25, 71: PRINT CHR$(24); CHR$(25); "-Move"; : COLOR 2, 0
	 maxpag% = 20
	 'IF rec% < 1 OR rec% > maxip% THEN rec% = 1
	 updwn% = 13: 'bpos$ = STR$(rec%)
	 xsearch$ = ""
	 showdup% = 0
	 skip$ = "Y"

	 '>>>>> Get next REC%ord to browse from.
ipBROWSE.A:
	LOCATE 2, 25
	COLOR 7: PRINT "¹ ";
	COLOR 2: PRINT "Start browse from..>      ";
	COLOR 7: PRINT "Ì": COLOR 2
	COLOR 2
	IF skip$ = "Y" THEN
		skip$ = "N"
	ELSE
		bpos$ = STR$(ipa(s%).item%)
		LOCATE 2, 47: CALL inpnew(bpos$, 205!, updwn%, "13,59-64,68,72,73,80,81")
	END IF

	IF updwn% = 61 THEN
		LOCATE 2, 25: PRINT "Search..>";
		CALL inpnew(xsearch$, 120!, updwn%, "13,59,61,63-64,68,72,73,80,81")
		bpos$ = "1"
		updwn% = 13
	END IF


	IF updwn% = 13 THEN
			IF VAL(bpos$) = 0 AND LEN(bpos$) > 0 THEN
				keyl% = 20: qk$ = SPACE$(keyl%)
				sa$ = bpos$
				sa$ = UCASE$(sa$): LSET qk$ = sa$
				CALL index("CHAIN", ind%, qk$, 7, keyl%)
				IF ind% < 0 AND qk$ < sa$ THEN CALL index("READ ", ind%, qk$, 7, keyl%)
				bpos$ = MID$(STR$(ind%), 2)
			END IF

			IF VAL(bpos$) = 0 THEN bpos$ = STR$(e%)
			findiprec% = VAL(bpos$)
			found% = 0
			iprec% = s%
			FOR find% = 1 TO UBOUND(ipa)
				IF ipa(find%).item% = findiprec% THEN iprec% = find%: found% = -1: EXIT FOR
			NEXT
			IF iprec% < 1 OR iprec% > UBOUND(ipa) THEN iprec% = 1
	END IF
	IF updwn% = 59 THEN rec% = s%: GOTO X.ipbrowse

	IF updwn% = 60 THEN  '***** Insert/Add
		' Box
		PCOPY 0, 1
		LOCATE 10, 2: COLOR 6, 0: PRINT "     Size   No.  Description                           Price   RMC    I.Price "
		COLOR 2
		LOCATE 11, 2: COLOR 2, 0: PRINT "ÄÄÄÄÂÄÄÄÄÄÂÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄ"
		LOCATE 12, 2:             PRINT "    ³     ³    ³                                    ³       ³       ³         "
		LOCATE 13, 2: COLOR 2, 0: PRINT "ÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄ"

ipadd.size:
		' Size
			fromsizeoritem% = 0
			LOCATE 12, 7:
			CALL inpnew(ipsize$, 103!, updwn%, "13,59")
			IF updwn% = 59 THEN GOTO ipadd.pass
			ipsize$ = UCASE$(ipsize$)
			a$ = "   ": LSET a$ = ipsize$: ipsize$ = a$
		 
		IF VAL(ipsize$) <> 0 THEN
ipadd.search:
			fromsizeoritem% = -1
		'-SEARCH AWAY
			newsearch$ = "Y" ' by pd
			in$ = "": IF frombrowse% = -1 THEN in$ = acstk.search$: frombrowse% = 0
			LOCATE 12, 18:
			CALL inpnew(in$, 118!, updwn%, "13,59,60,64")
			IF LEN(in$) > 0 THEN
					in$ = UCASE$(in$)
					search.key$ = in$
					COLOR 13, 0
					LOCATE 10, 35: PRINT USING "\                \"; search.key$
					COLOR 2, 0
			END IF
			IF updwn% = 59 THEN GOTO ipadd.pass
			IF updwn% = 60 THEN GOTO ipadd.size
			IF updwn% = 64 THEN
					PCOPY 0, 2
					CALL accbrowse(rec%)
					PCOPY 2, 0
					IF rec% < 1 OR rec% > maxacc% THEN rec% = 1
					GET #3, rec%, acstk
					frombrowse% = -1
					GOTO ipadd.search
			END IF

			search.dir$ = "N"
			LSET qk$ = search.key$
			CALL index("CHAIN", ind%, qk$, 7, keyl%)
			IF ind% < 0 AND qk$ < search.key$ THEN CALL index("READ ", ind%, qk$, 7, keyl%)
			IF ind% < 0 THEN ind% = 0 - ind%
			' END IF by pd
		test = VAL(ipsize$)
		ii% = 0
		FOR i% = LEN(ipsize$) TO 1 STEP -1
			IF MID$(ipsize$, i%, 1) = " " THEN ii% = ii% + 1
			IF MID$(ipsize$, i%, 1) <> " " THEN EXIT FOR
			NEXT
		testa$ = STRING$(ii%, " ") + ipsize$
		testa$ = LEFT$(testa$, 3)

		test1$ = MID$(qk$, 1, 1)
		count% = 0
anext3:
		IF MID$(qk$, 16, 3) = testa$ THEN
			test1$ = MID$(qk$, 1, 1)
			IF ind% > 0 AND ind% < maxacc% THEN GET #3, ind%, acstk
			LOCATE 12, 13: PRINT USING "####"; ind%
			LOCATE 12, 18: PRINT acstk.desc1$; " "; acstk.desc2$
			
			IF newsearch$ = "Y" THEN search.dir$ = CHR$(13)
			END IF
		'// If the first letter in the index changes cancel then search //
		IF test1$ <> MID$(qk$, 1, 1) THEN 'Size not found. Go back to size .
				updwn% = 60
				GOTO ipadd.search
				END IF
		IF search.dir$ = "N" THEN
				CALL index("READ ", ind%, qk$, 7, keyl%)
				count% = count% + 1: IF count% < 3000 THEN GOTO anext3
				END IF
		IF search.dir$ = "P" THEN
				CALL index("READP", ind%, qk$, 7, keyl%)
				GOTO anext3
				END IF
		IF search.dir$ <> CHR$(13) THEN GOTO ipadd.search 'AGAIN
		
			ditem% = ind%

			'- Place the result of the search in the search key
			search.key$ = acstk.search$
			COLOR 13, 0
			LOCATE 10, 35: PRINT USING "\                \"; search.key$
			COLOR 2, 0

		
		ELSE
ipadd.item:
		'-STOCK NUMBER
			LOCATE 12, 13

			inpctl$ = "13,59,60,64"

			IF frombrowse% THEN ipitem$ = STR$(rec%): frombrowse% = 0
			CALL inpnew(ipitem$, 4!, updwn%, inpctl$)
			IF updwn% = 59 THEN GOTO ipadd.pass
			IF updwn% = 60 THEN GOTO ipadd.size

			IF updwn% = 64 THEN
				PCOPY 0, 2
				CALL accbrowse(rec%)
				PCOPY 2, 0
				IF rec% < 1 OR rec% > maxacc% THEN rec% = 0
				ipitem$ = "": updwn% = 0: frombrowse% = -1
				GOTO ipadd.item
			END IF

			ditem% = VAL(ipitem$)
			IF ditem% < 1 OR ditem% > maxacc% THEN GOTO ipadd.item
		
END IF
			FOR check% = 1 TO UBOUND(ipa)
				IF ipa(check%).item% = ditem% THEN
					COLOR 4
					LOCATE 12, 2: PRINT "   ITEM EXISTS AS AN INDIVIDUAL PRICE ALREADY                  "
					GOTO ipadd.pass
				END IF
				NEXT

			GET #3, ditem%, acstk

			'//// Determine which price to use ////
			price! = -1
	GET #43, sno%, cus
	SELECT CASE cus.stype$
	CASE "A": 'Factory Price
				price! = acstk.counter
	CASE "C": 'Contractor Price
				price! = acstk.contract
	CASE "D": 'Distributor Price
				price! = acstk.distributor * (1 + cus.slevel / 100)
	CASE "G": 'Group Price
				price! = acstk.distributor * (1 + cus.slevel / 100)
	CASE "H": 'Hardware Price
				price! = acstk.distributor * (1 + cus.slevel / 100)
	CASE "I": 'Industrial Price
				price! = acstk.industrial
	CASE "M": 'Mitre Ten Price
				price! = acstk.distributor * (1 + cus.slevel / 100)
	CASE "P": 'Painter Price
				price! = acstk.industrial
	CASE "S": 'Special Price
				price! = acstk.trade
	CASE "T": 'Trade Price
				price! = acstk.trade
	CASE "W": 'Best Possible Price
				price! = acstk.wholesalecost
	CASE "Y": 'Group Office Price
				price! = acstk.distributor * (1 + cus.slevel / 100)
	CASE "Z": 'Group store price
				price! = acstk.distributor * (1 + cus.slevel / 100)

	CASE ELSE: 'All Other Codes Are Retail Price
				price! = acstk.retail
	END SELECT
			

			ipsize$ = acstk.size$
			ipunit$ = acstk.unit$
			ipdesc$ = acstk.desc1$ + " " + acstk.desc2$
			ipprice$ = STR$(price!)
			iprmc$ = STR$(acstk.rmc!)
			ipchange$ = STR$(price!)

			LOCATE 12, 55: PRINT USING "####.##"; price!;
			LOCATE 12, 63: PRINT USING "$###.##"; acstk.rmc!;
			COLOR 14
			LOCATE 12, 71: PRINT USING "######.##"; price!
			COLOR 2
			LOCATE 12, 13: PRINT USING "####"; ind%
			LOCATE 12, 18: PRINT acstk.desc1$; " "; acstk.desc2$

ipadd.ip:
		LOCATE 12, 71:
		CALL inpnew(ipchange$, 208.2, updwn%, "13,59,60")
		IF updwn% = 59 THEN GOTO ipadd.pass
		IF updwn% = 60 THEN
			IF fromsizeoritem% = -1 THEN GOTO ipadd.search
			GOTO ipadd.item
		END IF
		iprice.no% = nextrec%
		iprice.item% = iplast% + 1
		iprice.item% = ditem%
		iprice.search$ = custin$
		iprice.iprice = VAL(ipchange$)
		iprice.date$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
		iprice.notes$ = SPACE$(50)
		iprice.filler$ = SPACE$(100)
		'- Find first available record
		PUT #4, nextrec%, iprice
		PCOPY 1, 0
		bpos$ = STR$(ditem%)
		GOTO ipstart:

ipadd.pass:
		PCOPY 1, 0
		
	END IF

	IF updwn% = 62 THEN '***** Delete
		PCOPY 0, 1
ipdelete:
		
		LOCATE 11, 2: COLOR 2, 0: PRINT "ÄÄÄÄÂÄÄÄÄÄÂÄÄÄÄÂÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÂÄÄÄÄÄÄÄÄÄ"
		LOCATE 12, 2:             PRINT "    ³     ³    ³                                                    ³         "
		LOCATE 13, 2: COLOR 2, 0: PRINT "ÄÄÄÄÁÄÄÄÄÄÁÄÄÄÄÁÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÄÁÄÄÄÄÄÄÄÄÄ"

		LOCATE 12, 35: PRINT "Delete Item " + STR$(ipa(s%).item%) + "...>";
		yn$ = "Y"
		CALL inpnew(yn$, 201!, updwn%, "13,59") ' yet to add F2
		IF updwn% = 59 THEN GOTO ipdelete.pass
		IF UCASE$(yn$) = "N" THEN GOTO ipdelete.pass
		IF UCASE$(yn$) = "Y" THEN GOTO ipdelete.ok
		GOTO ipdelete
ipdelete.ok:
		iprice.no% = 0
		iprice.item% = 0
		iprice.search$ = SPACE$(5)
		iprice.iprice = 0
		iprice.date$ = SPACE$(8)
		iprice.notes$ = SPACE$(50)
		iprice.filler$ = SPACE$(100)
		PUT #4, ipa(s%).no%, iprice
		IF ipa(s%).no% > 1 THEN bpos$ = STR$(ipa(s% - 1).item%)
		IF ipa(s%).no% = 1 THEN bpos$ = STR$(ipa(s% + 1).item%)
		GOTO ipstart
ipdelete.pass:
		iprec% = s%
		PCOPY 1, 0
END IF

	IF updwn% = 63 THEN '***** Swap browse type
		COLOR 6: LOCATE 3, 2
		SELECT CASE btype$
		CASE "cost": btype$ = "key ": PRINT kbtm$
		CASE "key ": btype$ = "data": PRINT dbtm$
		CASE "data": btype$ = "cost": PRINT cbtm$
		END SELECT
		COLOR 2, 0
		iprec% = s%
	END IF


	IF updwn% = 68 THEN  '***** Change
		IF btype$ = "key " THEN
		LOCATE 4, 54
		'????
		ipchange$ = STR$(ipa(s%).price)
		CALL inpnew(ipchange$, 206.2, updwn%, "13,59")
		IF updwn% = 59 THEN GOTO pass.change
		ipa(s%).price = VAL(ipchange$)
		GET #4, ipa(s%).no%, iprice
		iprice.iprice = ipa(s%).price
		iprice.date$ = FNDY$(MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2))
		PUT #4, ipa(s%).no%, iprice
		END IF
pass.change:
		updwn% = 13
		iprec% = s%
	END IF

	IF updwn% = 72 THEN 'UP arrow
		lin% = 1
		iprec% = s%
		DO WHILE lin% > 0 AND ipa(iprec%).item% > 1
			iprec% = iprec% - 1
			IF iprec% < 1 THEN iprec% = 1
			GET #3, ipa(iprec%).item%, acstk
			IF acstk.no% = ipa(iprec%).item% THEN lin% = lin% - 1
			LOOP
	END IF
	IF updwn% = 80 THEN 'Down arrow
		iprec% = s% + 1
		IF iprec% > UBOUND(ipa) THEN iprec% = UBOUND(ipa)
		GET #3, ipa(iprec%).item%, acstk
		DO WHILE acstk.no <> ipa(iprec%).item% AND ipa(iprec%).item% < maxacc%
			iprec% = iprec% + 1
			GET #3, ipa(iprec%).item%, acstk
			LOOP

	END IF
	IF updwn% = 73 THEN 'pg up
		lin% = maxpag%
		iprec% = s%
		DO WHILE lin% > 0 AND iprec% > 1
			iprec% = iprec% - 1
			GET #3, ipa(iprec%).item%, acstk
			IF acstk.no% = ipa(iprec%).item% THEN lin% = lin% - 1
			LOOP
	END IF
	IF updwn% = 81 THEN 'pg dw
		iprec% = e% + 1
		IF iprec% > UBOUND(ipa) THEN iprec% = UBOUND(ipa)
	END IF


'///////////////////////////////////////////////////////////////////////////
'>>--- L I S T   A   P A G E
'///////////////////////////////////////////////////////////////////////////
	'Given rec% as the first record
	
	IF ipa(iprec%).item% < 1 OR rec% > maxacc% THEN iprec% = 1
	GET #3, ipa(iprec%).item%, acstk
	lin% = 0: missed% = 0
	DO UNTIL lin% = maxpag% OR iprec% > UBOUND(ipa) 'OR missed% > 400

		'Selection
		ok% = -1
		IF acstk.no% <> ipa(iprec%).item% THEN ok% = 0
		IF btype$ = "key " AND UCASE$(acstk.Active$) <> "A" THEN ok% = 0

		IF showdup% THEN
			ok% = 0
		END IF

		IF ok% AND xsearch$ > "" THEN
			ok0% = 0
			IF ok0% = 0 AND INSTR(LCASE$(acstk.desc1$), LCASE$(xsearch$)) > 0 THEN ok0% = -1
			IF ok0% = 0 AND INSTR(LCASE$(acstk.desc2$), LCASE$(xsearch$)) > 0 THEN ok0% = -1
			IF NOT ok0% THEN ok% = 0
		END IF


		IF ok% THEN prttype$ = btype$
		IF NOT ok% THEN prttype$ = "missed"
		bc$ = " ": IF acstk.ean13 > 9300 THEN bc$ = CHR$(127)

	GET #43, sno%, cus
	SELECT CASE cus.stype$
	CASE "A": 'Factory Price
				price! = acstk.counter
	CASE "C": 'Contractor Price
				price! = acstk.contract
	CASE "D": 'Distributor Price
				price! = acstk.distributor * (1 + cus.slevel / 100)
	CASE "G": 'Group Price
				price! = acstk.distributor * (1 + cus.slevel / 100)
	CASE "H": 'Hardware Price
				price! = acstk.distributor * (1 + cus.slevel / 100)
	CASE "I": 'Industrial Price
				price! = acstk.industrial
	CASE "M": 'Mitre Ten Price
				price! = acstk.distributor * (1 + cus.slevel / 100)
	CASE "P": 'Painter Price
				price! = acstk.industrial
	CASE "S": 'Special Price
				price! = acstk.trade
	CASE "T": 'Trade Price
				price! = acstk.trade
	CASE "W": 'Best Possible Price
				price! = acstk.wholesalecost
	CASE "Y": 'Group Office Price
				price! = acstk.distributor * (1 + cus.slevel / 100)
	CASE "Z": 'Group store price
				price! = acstk.distributor * (1 + cus.slevel / 100)

	CASE ELSE: 'All Other Codes Are Retail Price
				price! = acstk.retail
	END SELECT


		SELECT CASE prttype$
		CASE "cost"
			LOCATE 4 + lin%, 2
			IF acstk.counter > 999 THEN                                                                '
				PRINT USING "####\                       \\        \!\ \\\ \  \####   ####   ####   ####   "; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; acstk.suplr$; acstk.distributor; acstk.industrial; acstk.trade; acstk.counter
			ELSE
				PRINT USING "####\                       \\        \!\ \\\ \  \ ###.## ###.## ###.## ###.##"; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; acstk.suplr$; acstk.distributor; acstk.industrial; acstk.trade; acstk.counter
			END IF
			COLOR 3, 0
			LOCATE 4 + lin%, 2 + 46
			PRINT USING "\  \"; acstk.suplr$
			LOCATE 4 + lin%, 2
			PRINT USING "####"; acstk.no%
			COLOR 2, 0
			COLOR 10, 0: LOCATE 4 + lin%, 41: PRINT bc$; : COLOR 2, 0'BC

			lin% = lin% + 1
			IF lin% = 1 THEN s% = iprec%
			e% = iprec%
		CASE "key "
			LOCATE 4 + lin%, 2
			IF acstk.distributor > 999 THEN
				kbtm$ = " No.Stock description.                  Size     Current Indiv  GP   RMC    GPR "
				PRINT USING "####\                       \\        \!\ \\\   #### #### ###.#% #### ###.#%"; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; price!; ipa(iprec%).price; 100 * (1 - acstk.rmc / ipa(iprec%).price); acstk.rmc _
; acstk.gpr
			ELSE
				PRINT USING "####\                       \\        \!\ \\\ ###.## ###.## ###%  ###.## ###% "; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; price!; ipa(iprec%).price; 100 * (1 - acstk.rmc / ipa(iprec%).price); acstk. _
rmc; acstk.gpr
			END IF
			COLOR 3, 0
			LOCATE 4 + lin%, 2
			PRINT USING "####"; acstk.no%
			COLOR 11, 0
			LOCATE 4 + lin%, 55
			PRINT USING "###.##"; ipa(iprec%).price

			COLOR 2, 0
			COLOR 10, 0: LOCATE 4 + lin%, 41: PRINT bc$; : COLOR 2, 0'BC

			lin% = lin% + 1
			IF lin% = 1 THEN s% = iprec%
			e% = iprec%
		CASE "data"
			LOCATE 4 + lin%, 2
				GET #4, ipa(iprec%).no%, iprice
				PRINT USING "####\                       \\        \!\ \\\ \      \ \                     \"; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; FNDYY$(iprice.date$); iprice.notes$
			
			COLOR 3, 0
			LOCATE 4 + lin%, 2 + 46
			PRINT USING "\      \"; FNDYY$(iprice.date$)
			LOCATE 4 + lin%, 2
			PRINT USING "####"; acstk.no%
			COLOR 2, 0
			COLOR 10, 0: LOCATE 4 + lin%, 41: PRINT bc$; : COLOR 2, 0'BC

			lin% = lin% + 1
			IF lin% = 1 THEN s% = iprec%
			e% = iprec%

		CASE "missed"
			missed% = missed% + 1
		END SELECT

	bad% = 0
	tmp$ = acstk.suplr4stdcost$ + acstk.search4stdcost
	FOR i% = 1 TO LEN(tmp$)
		IF MID$(tmp$, i%, 1) < " " THEN bad% = -1: EXIT FOR
		IF MID$(tmp$, i%, 1) > "~" THEN bad% = -1: EXIT FOR
	NEXT
	IF iprec% < UBOUND(ipa) THEN
			iprec% = iprec% + 1
		ELSE
			EXIT DO
	END IF
	GET #3, ipa(iprec%).item%, acstk:
	LOOP


	'IF missed% > 400 THEN
	'  LOCATE , 2: PRINT "More than 400 records searched without an active record being found."; CHR$(FNE)
	'  lin% = lin% + 1
	'END IF
	FOR i% = lin% + 1 TO maxpag%: LOCATE 3 + i%, 2: PRINT SPACE$(78): NEXT


	GOTO ipBROWSE.A   '***** Get next REC%ord to browse from

X.ipbrowse:


END SUB

