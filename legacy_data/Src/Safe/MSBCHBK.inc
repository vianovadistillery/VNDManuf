
	'////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>>>>> BATCH BACKUP FILE <<<<<<<<<<<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

	OPEN "MSBCHBK.HST" FOR RANDOM SHARED AS #26 LEN = 59

IF NOT typefields% THEN FIELD #26, 2 AS bno$, 2 AS bfno$, 1 AS bccost$, 2 AS brev$, 1 AS btype$, 2 AS bclass$, 2 AS byld$, 2 AS bayld$, 8 AS bdate$, 25 AS bdesc$, 4 AS bvisl$, 4 AS bvish$, 4 AS bavis$

TYPE RcdFmtMSbchBK
	bno AS STRING * 2
	bfno AS STRING * 2
	bccost AS STRING * 1
	brev AS STRING * 2
	btype AS STRING * 1
	bclass AS STRING * 2
	byld AS STRING * 2
	bayld AS STRING * 2
	bdate AS STRING * 8
	bdesc AS STRING * 25
	bvisl AS STRING * 4
	bvish AS STRING * 4
	bavis AS STRING * 4
END TYPE
DIM SHARED MSbtchbk AS RcdFmtMSbchBK

