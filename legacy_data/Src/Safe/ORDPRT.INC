'/////////////////////////////////////////////////////////////////////////////
'>>>> Hold file for printing orders
'/////////////////////////////////////////////////////////////////////////////
'OPEN "ordhed.prt" FOR RANDOM SHARED AS #78 LEN = 431
OPEN "C:\tpexe\ordhed.wrk" FOR RANDOM SHARED AS #78 LEN = 431

TYPE RcdFmtordprt
	hord AS INTEGER
	hopt AS INTEGER
	hcash AS INTEGER
	hchginv AS DOUBLE
	hchginvrrn AS INTEGER
	hinvnum AS DOUBLE
	hinvnumrec AS INTEGER
	hthissup  AS STRING * 5
	hnorders AS INTEGER
	hMode AS STRING * 3
	hTaxRate AS DOUBLE   '10 = 10%
	hDiscRate AS DOUBLE   '0.20  = 20c in the dollar
	hnote1 AS STRING * 42
	hnote2 AS STRING * 42
	hNameOvertyped AS STRING * 35
	hAddrOvertyped AS STRING * 20
	hSuburbOvertyped AS STRING * 20

	'Globals
	gsno AS INTEGER
	gtaxin AS STRING * 1
	gtender AS STRING * 1
	gdoctype  AS STRING * 11    'TAX INVOICE'
	gformtype  AS STRING * 14  '
	gexdisc AS DOUBLE
	gvdisc AS DOUBLE
	gadvalue AS CURRENCY
	gadtax AS CURRENCY
	gOSCurrency AS STRING * 3
	hfiller AS STRING * 156

END TYPE
DIM SHARED ordprt AS RcdFmtordprt
