	'/////////////////////////////////////////////////////////////////////
	'>>>  JOURNAL OF CASH SALES
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	OPEN "cashsal.acf"  FOR RANDOM SHARED  AS #47  LEN=19

IF NOT typefields% THEN 
FIELD #47,2  AS CNO$,2  AS CUPDREC$,3  AS CSIZE$,10 AS CSEARCH$,			2  AS CQTYSOLD$
END IF

TYPE RcdFmtcashsal
	cno AS STRING * 2 
	cupdrec AS STRING * 2 
	csize AS STRING * 3 
	csearch AS STRING * 10
	cqtysold AS STRING * 2 
END TYPE 
DIM SHARED cashsal AS RcdFmtcashsal

	CASHSALLAST%=LOF(47)/19
