	'>>>>>>>>>>>>>>>>>>>>>> B08 -  MISCELLANEOUS FILE <<<<<<<<<<<<<<<<<<<<<<<<
		OPEN "msmisc.msf" AS #1 LEN=128
IF NOT typefields% THEN   FIELD #1,2  AS QTYF$, 2  AS BCHNO$, 2  AS BCHOFF$, 40 AS CC$, 6  AS CCDE$, 2  AS MAX1$, 2  AS MAX2$, 2  AS MAX3$, 2  AS MAX4$, 2  AS MAX5$, 2  AS MAX6$, 2  AS MAX7$, 2  AS MAX8$, 2  AS MAX9$, 2  AS MAX10$, 10 AS OLDATE$, 2  AS VERSION$, 1  AS SPECIAL$, 1  AS INSIDE$, 2  AS BCHIST$, 1  AS TRDISC$, 2  AS SYSUNT$, 2  AS SYSNUM$, 1  AS PRTHI$, 1  AS PRTDB$, 1  AS PRTSUB$, 1  AS PRTSUP$, 1  AS PRTHI1$,			 20 AS FILLER

TYPE RcdFmtmsmisc
	qtyf AS STRING * 2
	bchno AS STRING * 2
	bchoff AS STRING * 2
	cc AS STRING * 40
	ccde AS STRING * 6
	max1 AS STRING * 2
	max2 AS STRING * 2
	max3 AS STRING * 2
	max4 AS STRING * 2
	max5 AS STRING * 2
	max6 AS STRING * 2
	max7 AS STRING * 2
	max8 AS STRING * 2
	max9 AS STRING * 2
	max10 AS STRING * 2
	oldate AS STRING * 10
	version AS STRING * 2
	special AS STRING * 1
	inside AS STRING * 1
	bchist AS STRING * 2
	trdisc AS STRING * 1
	sysunt AS STRING * 2
	sysnum AS STRING * 2
	prthi AS STRING * 1
	prtdb AS STRING * 1
	prtsub AS STRING * 1
	prtsup AS STRING * 1
	prthi1 AS STRING * 1
	filler AS STRING * 20
END TYPE
DIM SHARED msmisc AS RcdFmtmsmisc
