'///////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>> RAW MATERIAL GROUP FILE <<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
OPEN "msrmgp.dat" FOR RANDOM SHARED AS #39 LEN = 64

TYPE RcdFmtmsrmgp
	id  AS STRING * 5  '1.1.1'
	rmgroup AS STRING * 22
	filler AS STRING * 37
END TYPE
DIM SHARED msrmgp AS RcdFmtmsrmgp

