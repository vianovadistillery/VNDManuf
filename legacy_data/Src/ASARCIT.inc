	'///////////////////////////////////////////////////////////////////////
	'////    ACCOUNTING AUDIT ARCHIVE FILE
	'///////////////////////////////////////////////////////////////////////
	OPEN "asarcit.arc"  FOR RANDOM SHARED AS #46 LEN=88


TYPE RcdFmtasarcit
	adrec AS STRING * 2
	addate AS STRING * 8
	adtype AS STRING * 2
	adsname AS STRING * 30
	adcust AS STRING * 5
	addocnum AS STRING * 8
	adfiller AS STRING * 8
	advalue AS STRING * 4
	adglacc AS STRING * 4
	adtext AS STRING * 17
END TYPE
DIM SHARED asarcit AS RcdFmtasarcit

