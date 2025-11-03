	'////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>>> batch header file <<<<<<<<<<<<<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	OPEN "MSBCHHD.HST" FOR RANDOM SHARED AS #27 LEN = 4

IF NOT typefields% THEN FIELD #27, 2 AS bchlow$, 2 AS bchhi$

TYPE RcdFmtmsbchhd
	bchlow AS STRING * 2
	bchhi AS STRING * 2
END TYPE
DIM SHARED msbchhd AS RcdFmtmsbchhd
