'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'>>>>>>>>>>>>>>>  CREDITOR/SUPPLIER EXTENTIONS  <<<<<<<<<<<<<<<<<<<
'//////////////////////////////////////////////////////////////////

OPEN "whoext.who" FOR RANDOM SHARED AS #68 LEN = 1600

TYPE RcdFmtwhoext
	no AS INTEGER
	search AS STRING * 5
	names(3) AS STRING * 25
	phone1(3) AS STRING * 20
	phone2(3) AS STRING * 20
	addr AS STRING * 25
	sub AS STRING * 20
	pcode AS STRING * 4
	machine(5) AS STRING * 8
	text(13) AS STRING * 77
	filler AS STRING * 67

END TYPE
DIM SHARED whoext AS RcdFmtwhoext

