'///////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>> SUPPLIER FILE INDEX <<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
OPEN "whox.who" FOR RANDOM SHARED AS #65 LEN = 7

TYPE RcdFmtwhox
	wcde AS STRING * 5
	wrrn AS STRING * 2
END TYPE
DIM SHARED whox AS RcdFmtwhox

