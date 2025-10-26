'/////////////////////////////////////////////////////////////////////////////
'>>>> Order details
'/////////////////////////////////////////////////////////////////////////////
SELECT CASE acstkf$
CASE "PRE": OPEN "igadet.pre" FOR RANDOM SHARED AS #49 LEN = 32
CASE ELSE: OPEN "igadet.acf" FOR RANDOM SHARED AS #49 LEN = 32
END SELECT

IF NOT typefields% THEN FIELD #49, 2 AS dord$, 2 AS dseq$, 2 AS drrn$, 2 AS ditem$, 4 AS dprice$, 2 AS dordq$, 2 AS dinvq$, 4 AS dtax$, 2 AS dlinvq$

TYPE RcdFmtorddet
	dord AS INTEGER
	dseq AS INTEGER
	drrn AS INTEGER
	ditem AS STRING * 2
	dprice AS STRING * 4
	dordq AS STRING * 2
	dinvq AS STRING * 2
	dtax AS STRING * 4
	dlinvq AS STRING * 2
	dBo AS STRING * 1 '
	dcogs AS STRING * 4
	dfiller AS STRING * 5
END TYPE
DIM SHARED orddet AS RcdFmtorddet

