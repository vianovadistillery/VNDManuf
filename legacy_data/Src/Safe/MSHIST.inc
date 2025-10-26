
	'///////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>>>> FORMULA HISTORY FILE <<<<<<<<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	OPEN "mshist.hst" FOR RANDOM SHARED AS #36 LEN = 47

TYPE RcdFmtmshist
	hdesc1 AS STRING * 15
	hq AS STRING * 4
	hunit AS STRING * 4
	hd AS STRING * 2
	hc AS STRING * 22
END TYPE
DIM SHARED mshist AS RcdFmtmshist

