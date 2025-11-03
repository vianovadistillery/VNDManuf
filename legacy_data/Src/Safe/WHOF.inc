'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'>>>>>>>>>>>>>>>>>>>  LEADS FILE
'//////////////////////////////////////////////////////////////////
TYPE RcdFmtwho
	'Address
	sno AS STRING * 2
	search AS STRING * 4
	stype AS STRING * 1
	sname AS STRING * 35
	filler1 AS STRING * 5
	saddr AS STRING * 35
	filler2 AS STRING * 5
	saddr2 AS STRING * 35
	filler3 AS STRING * 5
	suburb AS STRING * 20
	state AS STRING * 20
	spcode AS STRING * 8
	spbox AS STRING * 8
	spboxsub AS STRING * 20
	spboxpcode AS STRING * 8
	slevel AS SINGLE
	ytd AS SINGLE
	p1 AS SINGLE
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


	BO AS STRING * 1
	abn AS STRING * 16
	bankcde AS STRING * 3
	bankacct AS STRING * 16
	p2 AS SINGLE
	p3 AS SINGLE
	p4 AS SINGLE
	p5 AS SINGLE
	p6 AS SINGLE
	p7 AS SINGLE
	p8 AS SINGLE
	p9 AS SINGLE
	p10 AS SINGLE
	p11 AS SINGLE
	p12 AS SINGLE
	filler5 AS STRING * 3

END TYPE

TYPE RcdFmtWHOold
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

TYPE RcdFmtWHOnew
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

	'Personal details
	ContactName(10) AS STRING * 20
	ContactTitle(10) AS STRING * 20
	ContactPhone(10) AS STRING * 20
	ContactMobile(10) AS STRING * 20
	Contactemail(10) AS STRING * 40

END TYPE
