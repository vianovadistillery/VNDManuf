'////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>>>>> BATCH FILE <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

OPEN "msbatch.msf" FOR RANDOM SHARED AS #57 LEN = 512

TYPE RcdFmtbatch
	bno AS INTEGER
	year AS STRING * 2
	form AS STRING * 4
	revision AS INTEGER
	SorW AS STRING * 1
	class AS INTEGER
	yld AS SINGLE
	ayld AS SINGLE
	date AS STRING * 8
	name AS STRING * 30
	Resinvar AS SINGLE ' actual kg
	Solventvar AS SINGLE ' filled volume
	Thickenervar AS SINGLE ' filled cost
	Rheomodifier AS SINGLE 'actual SG
	Stainer1var AS SINGLE ' waste volume
	Stainer2var AS SINGLE ' YIELD" %
	Stainer3var AS SINGLE ' waste $

	'New Info
	hord AS INTEGER
	thisbatch AS STRING * 8
	perltr AS SINGLE ' actual cost
	datereq AS STRING * 8
	dateman AS STRING * 8
	manby AS STRING * 3

	'Flags
	fltnt AS STRING * 1
	flstk AS STRING * 1
	flqc AS STRING * 1

	'tnthed
	yield AS SINGLE
	ltr AS SINGLE
	kg AS SINGLE
	visc1h AS SINGLE
	visc1l AS SINGLE
	visc2h AS SINGLE
	visc2l AS SINGLE
	alccost AS SINGLE ' actual cost
	rawcost AS SINGLE
	filter AS INTEGER
	grind AS SINGLE
	ph AS SINGLE
	sg AS SINGLE
	Vsol AS SINGLE
	Wsol AS SINGLE
	pvc AS SINGLE
	pbr AS SINGLE
	gloss AS SINGLE
	Hazard AS STRING * 1
	asRmat AS INTEGER
	CostPer AS STRING * 2

	'QC
	qcnote1 AS STRING * 25
	qcnote2 AS STRING * 25
	qcnote3 AS STRING * 25
	qcnote4 AS STRING * 25
	qcvsol AS SINGLE
	qcwsol AS SINGLE
	qcpvc AS SINGLE
	qcpbr AS SINGLE
	qcvisc1 AS SINGLE
	qcvisc2 AS SINGLE
	qcph AS SINGLE
	qcgloss AS SINGLE
	qcsg AS SINGLE

	priority AS INTEGER
	tnt AS INTEGER
	dateform AS STRING * 8
	Filler AS STRING * 166

END TYPE

DIM SHARED batch AS RcdFmtbatch
