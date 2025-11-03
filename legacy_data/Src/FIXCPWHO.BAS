DECLARE SUB movedata ()
	'$INCLUDE: '\tpmanuf\src\pgmhead.INC'

CHDIR "z:\TPMANUF"
'CHDIR "z:\TPMANUF\BRISTOL"
'CHDIR "z:\TPMANUF\DULUX"
'CHDIR "z:\TPMANUF\HEMPEL"
'CHDIR "z:\TPMANUF\JOTUN"
'CHDIR "z:\TPMANUF\OLDSYS"
'CHDIR "z:\TPMANUF\SICPA"
'CHDIR "z:\TPMANUF\SPARTAN"
'CHDIR "z:\TPMANUF\WAGON"

	CALL setup("COPY WHO,CUS,SUP to new format")
	' INCLUDE: '\tpmanuf\src\whof.inc'
	' INCLUDE: '\tpmanuf\src\cus.inc'
	' INCLUDE: '\tpmanuf\src\sup.inc'
	' INCLUDE: '\tpmanuf\src\who.inc'
	'$INCLUDE: '\tpmanuf\src\whoext.inc'

'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'>>>>>>>>>>>>>>>>>>>  LEADS FILE
'//////////////////////////////////////////////////////////////////
TYPE RcdFmtWHO
	'Address
	sno AS STRING * 2
	search AS STRING * 4
	stype AS STRING * 1
	sname AS STRING * 40
	saddr AS STRING * 40
	saddr2 AS STRING * 40
	suburb AS STRING * 20
	state AS STRING * 20
	spcode AS STRING * 8
	spbox AS STRING * 8
	spboxsub AS STRING * 40
	email AS STRING * 40
	www AS STRING * 40

	'Phone country
	pstnCC AS STRING * 3

	'Contact details
	scontTitle AS STRING * 3
	scont AS STRING * 40
	sphone AS STRING * 12
	sphone1 AS STRING * 12   ' Fax
	mobile AS STRING * 12

	'Customer Service
	ServiceTitle AS STRING * 3
	ServiceName AS STRING * 30
	Servicephone AS STRING * 12
	ServiceFax AS STRING * 12


	'Flags and cross ref..
	taxe AS STRING * 10
	sgl AS STRING * 4
	rep AS STRING * 1
	callfreq AS STRING * 1

	sdays AS STRING * 2
	sterms AS STRING * 4
	daysmax AS STRING * 2


	'Accounting
	scur AS STRING * 4
	s0 AS STRING * 4
	s30 AS STRING * 4
	s60 AS STRING * 4
	s90 AS STRING * 4
	opn AS STRING * 4
	opn30 AS STRING * 4
	opn60 AS STRING * 4
	opn90 AS STRING * 4
	account AS STRING * 4
	advalue AS STRING * 4
	climit AS STRING * 4

	'Pickup info
	spnum AS STRING * 2
	spname AS STRING * 30
	spsub AS STRING * 40

	'Invoice groups
	sdist AS STRING * 1
	sret AS STRING * 1
	countercde AS STRING * 1
	tradecde AS STRING * 1
	contractcde AS STRING * 1
	industrialcde AS STRING * 1
	scont1 AS STRING * 1
	scont2 AS STRING * 1
	wholesalecde AS STRING * 1

	'Audit trail
	addocnum AS STRING * 8
	addate AS STRING * 8

	'No longer used
	sunpoz AS STRING * 2
	smlpoz AS STRING * 4

	'Filler
	sdate AS STRING * 8
	Active AS STRING * 1

	filler1 AS STRING * 1
	filler2 AS STRING * 1
	filler4 AS STRING * 6
	filler5 AS STRING * 166
END TYPE


TYPE RcdFmtwhonewfmt
	'Address
	sno AS STRING * 2
	search AS STRING * 4
	stype AS STRING * 1
	sname AS STRING * 40
	saddr AS STRING * 40
	saddr2 AS STRING * 40
	suburb AS STRING * 20
	state AS STRING * 20
	spcode AS STRING * 8
	spbox AS STRING * 8
	spboxsub AS STRING * 40
	email AS STRING * 40
	www AS STRING * 40

	'Phone country
	pstnCC AS STRING * 3

	'Contact details
	scontTitle AS STRING * 3
	scont AS STRING * 40
	sphone AS STRING * 18
	sphone1 AS STRING * 18   ' Fax


	'Flags and cross ref..
	taxe AS STRING * 10
	sgl AS STRING * 4
	rep AS STRING * 1
	callfreq AS STRING * 1

	sdays AS STRING * 2
	sterms AS STRING * 4
	daysmax AS STRING * 2


	'Accounting
	scur AS STRING * 4
	s0 AS STRING * 4
	s30 AS STRING * 4
	s60 AS STRING * 4
	s90 AS STRING * 4
	opn AS STRING * 4
	opn30 AS STRING * 4
	opn60 AS STRING * 4
	opn90 AS STRING * 4
	account AS STRING * 4
	advalue AS STRING * 4
	climit AS STRING * 4

	'Pickup info
	spnum AS STRING * 2
	spname AS STRING * 30
	spsub AS STRING * 40

	'Invoice groups
	sdist AS STRING * 1
	sret AS STRING * 1
	countercde AS STRING * 1
	tradecde AS STRING * 1
	contractcde AS STRING * 1
	industrialcde AS STRING * 1
	scont1 AS STRING * 1
	scont2 AS STRING * 1
	wholesalecde AS STRING * 1

	'Audit trail
	addocnum AS STRING * 8
	addate AS STRING * 8

	sdate AS STRING * 8
	Active AS STRING * 1

	'Personal details
	ContactFirstName(6) AS STRING * 16
	ContactSurName(6) AS STRING * 20
	ContactTitle(6) AS STRING * 20
	ContactPhone(6) AS STRING * 18 '+61 xxx3 9xxx xxxx
	ContactMobile(6) AS STRING * 18'+61 x419 x338 x450
	ContactFax(6) AS STRING * 18   '+61 x419 x338 x450
	Contactemail(6) AS STRING * 40



	filler1 AS STRING * 83

END TYPE

	' INCLUDE: '\tpmanuf\src\cus.inc'
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'>>>>>>>>>>>>>>>>>>>  CREDITOR/SUPPLIER FILE  <<<<<<<<<<<<<<<<<<<<<
'//////////////////////////////////////////////////////////////////
OPEN "CUS.SAF" FOR RANDOM SHARED AS #43 LEN = 800
DIM SHARED CUS AS RcdFmtWHO

	' INCLUDE: '\tpmanuf\src\sup.inc'
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'>>>>>>>>>>>>>>>>>>>  CREDITOR/SUPPLIER FILE  <<<<<<<<<<<<<<<<<<<<<
'//////////////////////////////////////////////////////////////////
OPEN "sup.SAF" FOR RANDOM SHARED AS #44 LEN = 800
DIM SHARED sup AS RcdFmtWHO

	' INCLUDE: '\tpmanuf\src\who.inc'
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'>>>>>>>>>>>>>>>>>>>  LEADS FILE
'//////////////////////////////////////////////////////////////////
OPEN "who.SAF" FOR RANDOM SHARED AS #64 LEN = 800
DIM SHARED who AS RcdFmtWHO


	DIM SHARED whonewfmt AS RcdFmtwhonewfmt
	OPEN "cus.who" FOR OUTPUT AS #143: CLOSE 143
	OPEN "cus.who" FOR RANDOM SHARED AS #143 LEN = LEN(whonewfmt)
	rec% = 1
	GET #43, rec%, who
	DO WHILE NOT EOF(43)
		CALL movedata

		PUT #143, rec%, whonewfmt
		IF rec% MOD 100 = 0 THEN
			LOCATE 10, 10: PRINT whonewfmt.sname$, rec%; "  "
		END IF

		GET #43, , who: rec% = rec% + 1
	LOOP

	OPEN "sup.who" FOR OUTPUT AS #144: CLOSE 144
	OPEN "sup.who" FOR RANDOM SHARED AS #144 LEN = LEN(whonewfmt)
	rec% = 1
	GET #44, rec%, who
	DO WHILE NOT EOF(44)
		CALL movedata

		PUT #144, rec%, whonewfmt
		IF rec% MOD 100 = 0 THEN
			LOCATE 10, 10: PRINT whonewfmt.sname$, rec%; "  "
		END IF

		GET #44, , who: rec% = rec% + 1
	LOOP

	OPEN "who.who" FOR OUTPUT AS #164: CLOSE 164
	OPEN "who.who" FOR RANDOM SHARED AS #164 LEN = LEN(whonewfmt)
	rec% = 1
	GET #64, rec%, who
	DO WHILE NOT EOF(64)
		CALL movedata

		PUT #164, rec%, whonewfmt
		IF rec% MOD 100 = 0 THEN
			LOCATE 10, 10: PRINT whonewfmt.sname$, rec%; "  "
		END IF

		GET #64, , who: rec% = rec% + 1
	LOOP


ENDPGM:
CLOSE
CHDIR "z:\TPMANUF"
END

	'->>??
	order$ = STR$(invnum#)
	rrn78% = VAL(RIGHT$(order$, 2))
	ordprt.hord = hord%
	ordprt.hopt = opt%
	ordprt.hcash = cash%
	ordprt.hchginv = chginv#
	ordprt.hchginvrrn = chginv.rrn%
	ordprt.hinvnum = invnum#
	ordprt.hinvnumrec = invnumrec%
	ordprt.hthissup = thissup% ' $AJD
	ordprt.hnorders = norders%
	PUT #78, rrn78%, ordprt

SUB movedata

		whonewfmt.sno = who.sno
		whonewfmt.sname = who.sname
		whonewfmt.saddr = who.saddr
		whonewfmt.saddr2 = SPACE$(99)
		whonewfmt.spcode = who.spcode
		whonewfmt.sphone = who.sphone
		whonewfmt.sdate = who.sdate
		whonewfmt.scontTitle = "    "
		whonewfmt.scont = who.scont
		whonewfmt.suburb = who.suburb
		whonewfmt.state = SPACE$(99)
		whonewfmt.spbox = who.spbox
		whonewfmt.sdist = who.sdist
		whonewfmt.sret = who.sret
		whonewfmt.Active = who.Active
		whonewfmt.pstnCC = who.pstnCC
		whonewfmt.spsub = who.spsub
		whonewfmt.scur = who.scur
		whonewfmt.s30 = who.s30
		whonewfmt.s60 = who.s60
		whonewfmt.s90 = who.s90
		whonewfmt.stype = who.stype
		whonewfmt.sdays = who.sdays
		whonewfmt.sterms = who.sterms
		whonewfmt.search = who.search
		whonewfmt.daysmax = who.daysmax
		whonewfmt.sphone1 = who.sphone1
		whonewfmt.opn = who.opn
		whonewfmt.opn30 = who.opn30
		whonewfmt.opn60 = who.opn60
		whonewfmt.opn90 = who.opn90
		whonewfmt.wholesalecde = who.wholesalecde
		whonewfmt.callfreq = who.callfreq
		whonewfmt.account = who.account
		whonewfmt.advalue = who.advalue
		whonewfmt.climit = who.climit
		whonewfmt.taxe = who.taxe
		whonewfmt.spname = who.spname
		whonewfmt.scont1 = who.scont1
		whonewfmt.scont2 = who.scont2
		whonewfmt.s0 = who.s0
		whonewfmt.sgl = who.sgl
		whonewfmt.countercde = who.countercde
		whonewfmt.tradecde = who.tradecde
		whonewfmt.contractcde = who.contractcde
		whonewfmt.industrialcde = who.industrialcde
		whonewfmt.addocnum = who.addocnum
		whonewfmt.addate = who.addate
		whonewfmt.rep = who.rep
		whonewfmt.email = SPACE$(99)
		whonewfmt.www = SPACE$(99)
		whonewfmt.filler1 = SPACE$(999)

		whonewfmt.scontTitle = SPACE$(99)

		FOR i = 1 TO 10
		whonewfmt.ContactFirstName(i%) = SPACE$(99)
		whonewfmt.ContactSurName(i%) = SPACE$(99)
		whonewfmt.ContactTitle(i%) = SPACE$(99)
		whonewfmt.ContactPhone(i%) = SPACE$(99)
		whonewfmt.ContactMobile(i%) = SPACE$(99)
		whonewfmt.ContactFax(i%) = SPACE$(99)
		whonewfmt.Contactemail(i%) = SPACE$(99)
		NEXT



	whonewfmt.ContactSurName(1) = who.scont
	whonewfmt.ContactMobile(1) = who.mobile

END SUB
