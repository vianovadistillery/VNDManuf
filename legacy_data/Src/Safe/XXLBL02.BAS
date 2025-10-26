DECLARE SUB oneperpage (Stdout$)
DECLARE SUB load.sort (sort.it$, n%)
DECLARE SUB qsort (in$(), in%(), n%)
'.dc - Complete
'///////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>   DSLBL02 - CUSTOMER LISTING   <<<<<<<<<<<<<<<<<<<<<<<<<
'///////////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "DSMENU"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	DIM SHARED in$(1000), in%(1000)
	DIM SHARED maxsup%, chi%, ch%

	DB.OR.CR$ = "DB"
	DB.OR.CR$ = ENVIRON$("DB.OR.CR$")
	cr% = INSTR(COMMAND$, "/CR")
	IF cr% > 0 THEN DB.OR.CR$ = "CR"

	IF DB.OR.CR$ = "CR" THEN
		chi% = 45: ch% = 44: apgm$ = "CSMENU"
		ELSE
		chi% = 23: ch% = 43: apgm$ = "DSMENU"
	END IF

	'Stdout$ = "CON"
	Stdout$ = "XXLBL02.PRT"
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\CUS.INC'
	'$INCLUDE: '\tpmanuf\src\CUSX.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\supX.INC'
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	'$INCLUDE: '\tpmanuf\src\pickup.INC'
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)':MAXRMAT%=100
	'///////////////////////////////////////////////////////////////////////////
	'//// M A I N L I N E
	'///////////////////////////////////////////////////////////////////////////
	CALL setup("SUPPLIER LISTING")
210 COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : COLOR 2, 0
	LOCATE 5, 25: PRINT "|"; DB.OR.CR$; "|"
	LOCATE , 25: PRINT "1...Customer list."
	LOCATE , 25: PRINT "2...Customers with a delivery address list."
	LOCATE , 25: PRINT "3...Only Customers with delivery address"
	LOCATE , 25: PRINT "4...Customer form"
	LOCATE , 25: PRINT "5...One per page"
	LOCATE , 25: PRINT
	LOCATE , 25: PRINT "Option..> "
	LOCATE 12, 35
	CALL inpnew(opt$, 1!, updwn%, "13,59" + alt$): GOSUB alt
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	opt% = VAL(opt$)
	IF opt% < 1 OR opt% > 5 THEN GOTO 210
cf2:
	selectrep$ = "*"
	LOCATE 12, 25: PRINT "Enter Reps code..>    (*-all,B,C,L,M,N,S,T,U,X,G)"
				LOCATE 12, 43: CALL inpnew(selectrep$, 101!, updwn%, "13,59,60")
	selectrep$ = UCASE$(selectrep$)
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(pgm$): CHAIN pgm$
	IF updwn% = 60 THEN GOTO 210
cf3:
	sortit$ = "A"
	LOCATE 13, 25: PRINT "Sort Alpha/Suburb/Type..>    (A/S/T)"
				LOCATE 13, 50: CALL inpnew(sortit$, 101!, updwn%, "13,59,60")
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(pgm$): CHAIN pgm$
	IF updwn% = 60 THEN GOTO 210

	sortit$ = UCASE$(sortit$)

	CALL load.sort(sortit$, n%)
	IF sortit$ = "S" THEN CALL qsort(in$(), in%(), n%)
	IF sortit$ = "T" THEN CALL qsort(in$(), in%(), n%)

	OPEN Stdout$ FOR OUTPUT AS #99
	WIDTH #99, 160

	count% = 0

	IF Stdout$ = "CON" THEN CLS
	pag% = 0: lin% = 9999
	'n% = 999 '???
	FOR i% = 1 TO n%
		rec% = in%(i%)
		IF lin% > 58 THEN GOSUB heading'heading no per page
		GET #ch%, rec%, cus'get from master file
		sprec% = VAL(cus.spname$)
		spok% = 0
		IF opt% = 2 AND sprec% >= 3 AND sprec% <= 999 THEN spok% = -1
		IF opt% = 3 AND sprec% >= 3 AND sprec% <= 999 THEN spok% = -1
		ok% = 0
		IF selectrep$ = "*" THEN ok% = -1
		IF selectrep$ = cus.rep$ THEN ok% = -1
		IF opt% = 3 AND NOT spok% THEN ok% = 0
		
	prt.callfreq$ = RIGHT$("." + cus.callfreq$, 1)

	IF ok% THEN
		SELECT CASE opt%
		CASE 1: PRINT #99, USING "\  \! - \                                 \ - \                  \ \           \ \                            \ \                  \ \  \"; cus.search$; cus.stype$; cus.sname$; cus.scont$; cus.sphone$; cus.saddr$; cus. _
suburb$; cus.spcode$
		CASE 2: PRINT #99, USING "\  \! - \                                 \ - \                  \ \           \ \                            \ \                  \ \  \"; cus.search$; cus.stype$; cus.sname$; cus.scont$; cus.sphone$; cus.saddr$; cus. _
suburb$; cus.spcode$
		CASE 3: PRINT #99, USING "\  \! - \                                 \ - \                  \ \           \ \                            \ \                  \ \  \"; cus.search$; cus.stype$; cus.sname$; cus.scont$; cus.sphone$; cus.saddr$; cus. _
suburb$; cus.spcode$
		CASE 4: PRINT #99, USING "\  \! - \                                 \ |     |     |     |     |     |     |     |     |     |     |     |     |     |     |     |     |"; cus.search$; cus.stype$; cus.sname$
		CASE 5: CALL oneperpage(Stdout$): lin% = 999
		CASE ELSE
		END SELECT

		count% = count% + 1
		lin% = lin% + 1

		sprec% = VAL(cus.spname$)
		IF spok% THEN
			GET #50, sprec%, PICKUP
			 'PRINT #99, USING "------- & & & &  ###"; PICKUP.pname1$; PICKUP.pname2$; PICKUP.pname3$; PICKUP.pname4$; sprec%
			PRINT #99, USING "  ### - & & & &     "; sprec%; PICKUP.pname1$; PICKUP.pname2$; PICKUP.pname3$; PICKUP.pname4$
			lin% = lin% + 1
			END IF
		END IF

		IF Stdout$ <> "CON" THEN
			LOCATE 20, 20: PRINT "Printing record "; i%; cus.sname$; CHR$(FNE)
			END IF
		NEXT
	PRINT #99, CHR$(12)
	CLOSE #99
	IF Stdout$ = "XXLBL02.PRT" THEN SHELL "COPY XXLBL02.PRT LPT1"
	LOCATE 21, 20: PRINT "Total Selected  "; count%; "      "
	GOTO 210
	'//////////////////////////////////////////////////////////////////////////
	'/////////////////            h e a d i n g             ////////////////////
	'//////////////////////////////////////////////////////////////////////////
heading:
	IF pag% > 0 THEN PRINT #99, CHR$(12)
	pag% = pag% + 1: lin% = 9

	IF opt% = 1 THEN head$ = "                     M A S T E R   A D D R E S S   L I S T"
	IF opt% = 2 THEN head$ = "                  D E L I V E R Y    A D D R E S S   L I S T"
	IF opt% = 5 THEN head$ = "                  D E T A I L E D    L I S T I N G"

	IF opt% = 1 THEN colhead$ = "Cde  Customer              Contact       Phone.  Address         Suburb      P/C"
	IF opt% = 2 THEN colhead$ = "Cde  Customer              Contact       Phone.  Address         Suburb      P/C"
	IF opt% = 3 THEN colhead$ = "Cde  Customer              Contact       Phone.  Address         Suburb      P/C"

	PRINT #99, CHR$(18);
	PRINT #99, "#mslbl02"; TAB(66); "Date:"; date1$
	PRINT #99, CHR$(14); msmisc.cc$
	PRINT #99,
	PRINT #99, head$
	PRINT #99, a$; TAB(72); "Page:"; pag%
	PRINT #99, STRING$(80, "=")
	PRINT #99, colhead$
	PRINT #99, STRING$(80, "-")
	PRINT #99, CHR$(15);
RETURN

SUB load.sort (sort.it$, n%)

	n% = 0
	FOR i% = 1 TO maxsup%
		GET #ch%, i%, cus
		ok% = -1
		IF CVI(cus.sno$) <> i% THEN ok% = 0
		IF ok% THEN
			n% = n% + 1
			IF cus.suburb$ <= "                    " THEN cus.suburb$ = "ZZZZZ"
			IF sort.it$ = "S" THEN in$(n%) = cus.suburb$ + cus.search$ + cus.stype$
			IF sort.it$ = "T" THEN in$(n%) = cus.stype$ + cus.search$
			in%(n%) = i%
			END IF
		NEXT

END SUB

SUB oneperpage (Stdout$)
	 sno% = CVI(cus.sno$)
	 scur = CVS(cus.scur$): s30 = CVS(cus.s30$): s60 = CVS(cus.s60$): s90 = CVS(cus.s90$)
	 climit! = CVS(cus.climit$): chargto$ = SPACE$(5): chargto$ = cus.account$ + cus.scont1$
	 sterms! = CVS(cus.sterms$): daysmax% = CVI(cus.daysmax$)
	 cusvalue = CVS(cus.advalue$)

	 PRINT #99, cus.search$; " "; cus.stype$; " "; cus.sname$
	 PRINT #99,
	 PRINT #99, "Date/Active.: "; cus.sdate$; " "; cus.Active$
	 PRINT #99, "              "; cus.sname$
	 PRINT #99,
	 
	 PRINT #99, "Address.....: "; cus.saddr$
	 PRINT #99, "Suburb......: "; cus.suburb$; " "; cus.spcode$
	 PRINT #99, USING "............: ###"; VAL(cus.spname$)
	 PRINT #99, "............: "; cus.spbox$
	 PRINT #99, "Tax exempt..: "; cus.taxe$
	 PRINT #99, "Contact.....: "; "cus.scont$;"
	 PRINT #99, USING "............: ! \                  \"; cus.rep$
	 PRINT #99, USING "............: ! \                  \"; cus.callfreq$
	 PRINT #99, USING "............: \           \"; cus.sphone$
	 PRINT #99, USING "............: \           \"; cus.sphone1$
	 PRINT #99, USING "............: \           \"; cus.ContactMobile$(1)

	 PRINT #99, USING "............: \ \"; cus.pstnCC$
	 PRINT #99, "WWW.........: "; cus.www$
	 PRINT #99, "E-mail......: "; cus.email$


	 sprec% = VAL(cus.spname$)
	 IF spok% THEN
		 GET #50, sprec%, PICKUP
		 PRINT #99, "Pickup Address"
		 PRINT #99, USING "------- & & & &  ###"; PICKUP.pname1$; PICKUP.pname2$; PICKUP.pname3$; PICKUP.pname4$; sprec%
	 END IF


	 PRINT #99, USING "Terms..... .: ### ###.##%"; daysmax%; sterms
	 PRINT #99, "Backorder...: "; cus.BO$

	 PRINT #99, " Contact/email-------------------------Title/Fax------------Phone/Mobile------"

	 
	 FOR i% = 1 TO 6
	 IF cus.ContactFirstName$(i%) > SPACE$(30) THEN
	 PRINT #99, USING " & & & &"; cus.ContactFirstName$(i%); cus.ContactSurName$(i%); cus.ContactTitle(i%); cus.ContactPhone$(i%)
	 PRINT #99, USING " & &   &"; LEFT$(cus.Contactemail$(i%), 37); cus.ContactFax$(i%); cus.ContactMobile$(i%)
	 END IF
	 NEXT




IF Stdout$ = "CON" THEN x$ = INPUT$(1)
PRINT #99, CHR$(12)
X.DSPLY:



END SUB

SUB qsort (in$(), in%(), n%) STATIC
'$INCLUDE: '\tpmanuf\src\qsort.bi'
END SUB

