	'////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>>>>> COMPANY DETAIL FILE  <<<<<<<<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	OPEN "company.dat" FOR RANDOM SHARED AS #18 LEN = 128

IF NOT typefields% THEN FIELD #18, 2 AS cono$, 40 AS codesc$

TYPE RcdFmtcompany
	cono AS STRING * 2
	codesc AS STRING * 40
END TYPE
DIM SHARED company AS RcdFmtcompany

