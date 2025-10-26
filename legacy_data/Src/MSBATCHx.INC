'////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>>>>> BATCH FILE <<<<<<<<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

OPEN "msbatch.msf" FOR RANDOM SHARED AS #57 LEN = 128
OPEN "msbatch.msx" FOR RANDOM SHARED AS #58 LEN = 512

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
	Resinvar AS SINGLE
	Solventvar AS SINGLE
	Thickenervar AS SINGLE
	Rheomodifier AS SINGLE
	Stainer1var AS SINGLE
	Stainer2var AS SINGLE
	Stainer3var AS SINGLE
	hord AS INTEGER
	thisbatch AS STRING * 8
	perltr AS SINGLE
	Filler AS STRING * 27
END TYPE

TYPE RcdFmtbatchx
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
	Resinvar AS SINGLE
	Solventvar AS SINGLE
	Thickenervar AS SINGLE
	Rheomodifier AS SINGLE
	Stainer1var AS SINGLE
	Stainer2var AS SINGLE
	Stainer3var AS SINGLE
	hord AS INTEGER
	thisbatch AS STRING * 8
	perltr AS SINGLE
	Filler AS STRING * 411
END TYPE

DIM SHARED batch AS RcdFmtbatch
DIM SHARED batchx AS RcdFmtbatchx
