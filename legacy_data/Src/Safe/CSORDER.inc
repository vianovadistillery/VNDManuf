'/////////////////////////////////////////////////////////////////////
'>>>  JOURNAL OF CASH SALES
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

OPEN "csorder.sht" FOR RANDOM SHARED AS #69 LEN = 87

TYPE RcdFmtcsorder
	no AS STRING * 5
	bar AS STRING * 1
	text AS STRING * 80
	cr AS STRING * 1
END TYPE
DIM SHARED csorder AS RcdFmtcsorder

