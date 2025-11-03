DECLARE SUB setaudit (n%)
'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'>>>>>>>>>>>>>>>>>>    Archive audit file    <<<<<<<<<<<<<<<<<<<<<<<<<<<<
'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'.dc - Complete
	'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	pgm$ = "ASAUD01"
   ''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CONST max.pe% = 99
	CONST show.pe% = 13
	yy% = VAL(MID$(DATE$, 9, 2))
	'yy% = yy% - 1
	yy$ = RIGHT$("00" + MID$(STR$(yy%), 2, 2), 2)
	to.dt$ = "01/07/" + yy$
	STDOUT$ = "LPT1"
	RESET
	DIM SHARED auditfile$(15), naudit%
	CALL setaudit(naudit%)

	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\ASAUDIT.INC'
	cashonly$ = "M": auditname$ = auditfile$(naudit%)
	GOSUB OPEN.AUDIT
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	'OPEN "yearxxyy.hst" AS #2 LEN=92'output only
	OPEN "asaudit.new" FOR RANDOM SHARED AS #3 LEN = 92'output only
	OPEN STDOUT$ FOR OUTPUT AS #99
	DIM pe%(max.pe%), dt$(max.pe%)
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$)
	maxcus% = CVI(msmisc.max7$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	'*
start:
	CALL setup("ACCOUNTING AUDIT FILE ARCHIVE")
	LOCATE 21, 50: PRINT "Archive to "; to.dt$
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit";
	CALL sndmsg(msg$): msg$ = ""
	COLOR 6, 0: LOCATE 3, 2
	PRINT "No. Supplier/Customer name         Contact              Telephone     SEARCH"
	COLOR 2, 0
	GOSUB load.pe
	GOSUB BROWSE.PE.ONLY
	GOSUB HIGHLIGHT.DATE
	yorn$ = "N"
	DO
		LOCATE 21, 20: PRINT "Are you sure (Y/N).> "; CHR$(FNH);
		CALL inpnew(yorn$, 101!, updnw%, "13,59" + alt$): GOSUB alt
		yorn$ = UCASE$(yorn$)
		IF updwn% = 59 THEN yorn$ = "N"
		LOOP UNTIL yorn$ = "Y" OR yorn$ = "N"
		LOCATE 21, 20: PRINT CHR$(FNE)
	IF yorn$ = "N" THEN GOTO ENDPGM
	GOSUB ARCHIVE
	IF updwn% = 59 THEN GOTO start
	CLOSE
	IF NOT aborted% THEN
		OPEN "ASAUDIT.OLD" FOR RANDOM AS #8: CLOSE
		KILL "ASAUDIT.OLD"
		NAME "ASAUDIT.ASF" AS "ASAUDIT.OLD"
		NAME "ASAUDIT.NEW" AS "ASAUDIT.ASF"
		END IF
ENDPGM:
	CLOSE
	CALL exitpgm(pgm$)
	CHAIN pgm$
'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'>>>>> LOAD P.E. IN ARRAYS
'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
load.pe:
	FOR i% = 1 TO max.pe%
		pe%(i%) = 0
		NEXT
	'>>>> First time through grab the address of the records <<<<
	rec% = 1: load.pe% = 0
	GET #8, rec%, audit
	DO WHILE NOT EOF(8) AND load.pe% < max.pe% + 1
		load.pe% = load.pe% + 1
		pe%(load.pe%) = rec%
		dt$(load.pe%) = FNDYY$(audit.addate$)
		adnxtpe% = CVI(MID$(audit.adsname$, 1, 2))
		adprepe% = CVI(MID$(audit.adsname$, 3, 2))
		adlstpe% = CVI(MID$(audit.adsname$, 5, 2))
		rec% = adnxtpe%
		IF rec% = 0 THEN EXIT DO
		GET #8, rec%, audit
		LOOP
RETURN
'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'>>>>> B R O W S E   P.E. ONLY
'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
BROWSE.PE.ONLY:
	last% = show.pe%: IF load.pe% < show.pe% THEN last% = load.pe%
	FOR i% = 1 TO last%
		GET #8, pe%(i%), audit
		'/// Convert fields to numeric
		adnxtpe% = CVI(MID$(audit.adsname$, 1, 2))
		adprepe% = CVI(MID$(audit.adsname$, 3, 2))
		adlstpe% = CVI(MID$(audit.adsname$, 5, 2))
		LOCATE i% + 3, 2
		COLOR 5
		PRINT USING "##### & \\ ==================== Next#####      Prev#####      Last#####"; audit.adrec%; FNDYY$(audit.addate$); audit.adtype$; adnxtpe%; adprepe%; adlstpe%
		NEXT
	IF load.pe% > show.pe% THEN
		COLOR 14
		LOCATE , 2
		PRINT USING "More P.E. are in the system. First ## only are shown"; show.pe%
		END IF
	COLOR 2, 0
RETURN
'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'>>>>> HIGHLIGHT DATE
'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
HIGHLIGHT.DATE:
	FOR i% = 1 TO show.pe%
			IF pe%(i%) > 0 THEN GET #8, pe%(i%), audit
			'/// Convert fields to numeric
			adnxtpe% = CVI(MID$(audit.adsname$, 1, 2))
			adprepe% = CVI(MID$(audit.adsname$, 3, 2))
			adlstpe% = CVI(MID$(audit.adsname$, 5, 2))
			COLOR 5
			IF to.dt$ = dt$(i%) THEN COLOR 10
			LOCATE i% + 3, 2
			PRINT USING "##### & \\ ==================== Next#####      Prev#####      Last#####"; audit.adrec%; FNDYY$(audit.addate$); audit.adtype$; adnxtpe%; adprepe%; adlstpe%
		NEXT
	COLOR 2, 0
RETURN
'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
'>>>>> ARCHIVE
'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
ARCHIVE:
	aborted% = 0
	'>> Find the record number to start the ARCHIVE <<
	FOR i% = 1 TO max.pe%
		IF to.dt$ = dt$(i%) THEN backup.to% = pe%(i%)
		NEXT
	IF backup.to% = 0 THEN
		msg$ = "The last date was not found"
		updwn% = 59
		GOTO x.archive
		END IF
	aopen$ = "YEAR0000.HST"
	toyy% = VAL(MID$(to.dt$, 7, 2))
	toxx% = toyy% - 1: IF toxx% = -1 THEN toxx% = 99
	toyy$ = "0" + MID$(STR$(toyy%), 2)
	toxx$ = "0" + MID$(STR$(toxx%), 2)
	MID$(aopen$, 7, 2) = RIGHT$(toyy$, 2)
	MID$(aopen$, 5, 2) = RIGHT$(toxx$, 2)
	OPEN aopen$ FOR RANDOM AS #2 LEN = 92'output only
	IF LOF(2) > 0 THEN
		LOCATE 21, 10
		COLOR 14
		PRINT USING "File & already contains data. Archive aborted."; aopen$
		btm$ = SPACE$(30) + "    F1-Return.                      "
		COLOR 8, 3: LOCATE 25, 1: PRINT btm$; : LOCATE 1, 1
		CALL inpnew(a$, 0!, updwn%, "13,59")
		aborted% = -1
		GOTO x.archive
		END IF
	LOCATE 19, 2: PRINT CHR$(FNE)
	LOCATE 20, 2: PRINT CHR$(FNE)
	LOCATE 21, 2: PRINT CHR$(FNE)

	'>>- Start archive -<<
	rec% = 1: rec2% = 0: rec3% = 0
	GET #8, rec%, audit
	DO WHILE NOT EOF(8)
		adnxtpe% = CVI(MID$(audit.adsname$, 1, 2))
		adprepe% = CVI(MID$(audit.adsname$, 3, 2))
		adlstpe% = CVI(MID$(audit.adsname$, 5, 2))
		IF rec% MOD 100 = 0 THEN
			LOCATE 19, 2
			PRINT USING "Reading record ##,###"; rec%
			END IF


		IF audit.adtype$ = "PE" THEN
			IF rec% = backup.to% THEN adnxtpe% = 0
			adprepe% = adprepe%
			adlstpe% = backup.to%
			END IF


		MID$(audit.adsname$, 1, 2) = MKI$(adnxtpe%)
		MID$(audit.adsname$, 3, 2) = MKI$(adprepe%)
		MID$(audit.adsname$, 5, 2) = MKI$(adlstpe%)
		'>>- Write to xxxxx files -<<
		IF rec% <= backup.to% THEN
			rec2% = rec2% + 1
			audit.adrec% = rec2%
			PUT #2, rec2%, audit
			IF rec% MOD 100 = 0 THEN
				LOCATE 20, 2
				PRINT USING "Writing ##,### to &"; rec2%; aopen$
				END IF
			END IF

		'>>- Write to xxxxx files -<<
		IF rec% >= backup.to% THEN
			rec3% = rec3% + 1
			audit.adrec% = rec3%
			PUT #3, rec3%, audit
			IF rec% MOD 100 = 0 THEN
				LOCATE 21, 2
				PRINT USING "Writing ##,### to &"; rec3%; "ASAUDIT.NEW"
				END IF
			END IF


		GET #8, , audit: rec% = rec% + 1
		LOOP
x.archive:
RETURN

SUB setaudit (n%)
'$INCLUDE: '\tpmanuf\src\setaudit.bi'
END SUB
