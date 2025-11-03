'///////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>> FORMULA HISTORY FILE <<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
OPEN "fmhist.hst" FOR RANDOM SHARED AS #34 LEN = 62


TYPE RcdFmtfmhisth1
	form AS INTEGER
	cost AS STRING * 1
	rev AS INTEGER
	seq AS INTEGER
	rel AS INTEGER
	desc AS STRING * 25
	type AS STRING * 1
	class AS INTEGER
	yld AS SINGLE
	visl AS SINGLE
	vish AS SINGLE
	hdate AS STRING * 8
END TYPE

TYPE RcdFmtfmhisth2
	form AS INTEGER
	cost AS STRING * 1
	rev AS INTEGER
	seq AS INTEGER
END TYPE

TYPE RcdFmtfmhisth3
	form AS INTEGER
	cost AS STRING * 1
	rev AS INTEGER
	seq AS INTEGER
	text AS STRING * 55
END TYPE

TYPE RcdFmtfmhistd1
	form AS INTEGER
	cost AS STRING * 1
	rev AS INTEGER
	seq AS INTEGER
	desc AS STRING * 25
	qty AS SINGLE
	unit AS STRING * 2
	cmtqty AS INTEGER
	cmt AS STRING * 22
END TYPE

DIM SHARED fmhisth1 AS RcdFmtfmhisth1  'Seq 1:  Header
DIM SHARED fmhisth2 AS RcdFmtfmhisth2  'Seq 2:  Header (not used)
DIM SHARED fmhisth3 AS RcdFmtfmhisth3  'Seq 3-6 Comments records
DIM SHARED fmhistd1 AS RcdFmtfmhistd1  '7-nn    Details
