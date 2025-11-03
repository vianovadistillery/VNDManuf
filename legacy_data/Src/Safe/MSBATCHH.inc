'////////////////////////////////////////////////////////////////////
'>>  BATCH HISTORY FILE
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
bhfile$ = "Batchnn.hst"
MID$(bhfile$, 6, 2) = MID$(DATE$, 9, 2)
bhfile$ = "Batch93.hst"
OPEN bhfile$ FOR RANDOM SHARED AS #26 LEN = 128
DIM SHARED batchh AS RcdFmtbatch
