'///////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>> FORMULA HISTORY HEADER FILE <<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

OPEN "mshisth.hst" FOR RANDOM SHARED AS #35 LEN = 47

TYPE RcdFmtmshisth
	hform AS STRING * 2
	hcost AS STRING * 1
	hrev AS STRING * 2
	hrel AS STRING * 2
	hdesc AS STRING * 25
	htype AS STRING * 1
	hclass AS STRING * 2
	hyld AS STRING * 4
	hvisl AS STRING * 4
	hvish AS STRING * 4
'    hfirstdet AS INTEGER
'    hlastdet AS INTEGER
END TYPE
DIM SHARED mshisth AS RcdFmtmshisth
