	DECLARE SUB split (firstname$, lastname$)
	DECLARE SUB qsort (in$(), in%(), n%, ok%)
'>>>>>>>>>>>> -  Sorted index suitable for BINARY CHOP search  - <<<<<<<<<<<<
		'$INCLUDE: '\tpmanuf\src\PGMHEAD.INC'
	APGM$ = "FIMENU"
		'$INCLUDE: '\tpmanuf\src\PGMERR.INC'
	typefields% = -1
		'$INCLUDE: '\tpmanuf\src\whof.INC'
		'$INCLUDE: '\tpmanuf\src\cus.INC'
		'$INCLUDE: '\tpmanuf\src\sup.INC'
		'$INCLUDE: '\tpmanuf\src\who.INC'
	typefields% = -1
		'$INCLUDE: '\tpmanuf\src\phonex.inc'
	OPEN "phimport.asc" FOR OUTPUT AS #2
	OPEN "fximport.asc" FOR OUTPUT AS #3
	OPEN "WHO.psi" FOR OUTPUT AS #98
	max% = 3000
	DIM in%(max%), in$(max%)
	DIM h%(15)
	CALL setup("CREATE TELEPHONE FILE")
	CALL prtbtm("F1 - Exit")
	COLOR 2, 0
	LOCATE 4, 20: PRINT "Index file create commencing....": LOCATE 1, 1
	LOCATE 6, 20: PRINT "Reading customer file...........";
	rec% = 1
	GET #43, rec%, SUP
	DO WHILE NOT EOF(43)
		IF rec% = CVI(SUP.sno$) THEN
			IF SUP.sdate$ > "19000101" AND SUP.sdate$ < "20991231" THEN
			n% = n% + 1: IF n% > max% THEN n% = max%: BEEP
			in%(n%) = CVI(SUP.sno$)
			in$(n%) = SUP.search$ + SUP.stype$ + "43"
			END IF
		END IF
	GET #43, , SUP: rec% = rec% + 1
	LOOP
	PRINT USING "##,###"; rec%
	LOCATE 7, 20: PRINT "Reading Supplier file...........";
	rec% = 1
	GET #44, rec%, SUP
	DO WHILE NOT EOF(44)
		IF rec% = CVI(SUP.sno$) THEN
			IF SUP.sdate$ > "19000101" AND SUP.sdate$ < "20991231" THEN
			n% = n% + 1: IF n% > max% THEN n% = max%: BEEP
			in%(n%) = CVI(SUP.sno$)
			in$(n%) = SUP.search$ + SUP.stype$ + "44"
			END IF
		END IF
	GET #44, , SUP: rec% = rec% + 1
	LOOP
	PRINT USING "##,###"; rec%
	LOCATE 8, 20: PRINT "Reading xxxxxxxx file...........";
	rec% = 1
	GET #64, rec%, SUP
	DO WHILE NOT EOF(64)
		IF rec% = CVI(SUP.sno$) THEN
			IF SUP.sdate$ > "19000101" AND SUP.sdate$ < "20991231" THEN
			n% = n% + 1: IF n% > max% THEN n% = max%: BEEP
			in%(n%) = CVI(SUP.sno$)
			in$(n%) = SUP.search$ + SUP.stype$ + "64"
			END IF
		END IF
	GET #64, , SUP: rec% = rec% + 1
	LOOP
	PRINT USING "##,###"; rec%
'>>>>>>>>>>>>>>>>>>>>>>>> - ............................ - <<<<<<<<<<<<<<<<<<<
	LOCATE 12, 20: PRINT "Sorting the records............."
	CALL qsort(in$(), in%(), n%, ok%)
	COLOR 2, 0
	LOCATE 14, 20: PRINT "Writing new file................"
	LOCATE 1, 1
	CLOSE #52
	OPEN "phonex.who" FOR OUTPUT SHARED AS #52 LEN = LEN(phonex)
	CLOSE #52
	OPEN "phonex.who" FOR RANDOM SHARED AS #52 LEN = LEN(phonex)
'>>>>>>>>>>>>>>>>>>>>>>> -     Write new file.        - <<<<<<<<<<<<<<<<<<<<<
	FOR i% = 1 TO n%
		rec% = in%(i%)
		ch% = VAL(MID$(in$(i%), 6, 2))
			GET #ch%, rec%, SUP
			phonex.key = in$(i%)
			SELECT CASE ch%
			CASE 43: phonex.type = "DB"
			CASE 44: phonex.type = "CR"
			CASE 64: phonex.type = "--"
			CASE ELSE: phonex.type = "??"
			END SELECT
			phonex.company = SUP.sname$
			phonex.compnum = MID$(STR$(rec%), 2)
			phonex.name = SUP.scont$
			phonex.sphone = SUP.sphone$
			phonex.sphone1 = SUP.sphone1$

			FOR j% = 1 TO 6
			phonex.ContactFirstName(j%) = SUP.ContactFirstName(j%)
			phonex.ContactSurName(j%) = SUP.ContactSurName(j%)
			phonex.ContactTitle(j%) = SUP.ContactTitle(j%)
			phonex.ContactPhone(j%) = SUP.ContactPhone(j%)
			phonex.contactmobile(j%) = SUP.contactmobile(j%)
			phonex.Contactemail(j%) = SUP.Contactemail(j%)
			NEXT

			phonex.email = SUP.email
			phonex.www = SUP.www
			phonex.pstncc$ = SUP.pstncc$
			phonex.crlf$ = CHR$(13) + CHR$(10)
'>>>>>>>>>>>> -  Don't write records if the numbers are blank  - <<<<<<<<<<<<
			ok% = -1
		'IF (MID$(phonex.sphone1$, 1, 3)) = "111" THEN ok% = 0 'FAX   '????
		'IF (MID$(phonex.sphone$, 1, 3)) = "111" THEN ok% = 0  'PHONE '????
			 IF NOT ok% THEN GOTO NEXTI
'>>>>>>>>>>>>>>>>>>>>>>>> - It only gets here it its valid - <<<<<<<<<<<<<<<<
		IF i% = 1 THEN
			PUT #52, i%, phonex
			ELSE
			PUT #52, , phonex
			END IF
		IF LOF(98) = 0 THEN
		WRITE #98, "Code. Name................ Company....................... Address.................................. Suburb.............. P/Code.. Phone.............-Fax..............."
		END IF
		WRITE #98, phonex.key$, phonex.name$, phonex.company$, SUP.saddr$, SUP.suburb$, SUP.spcode$, SUP.sphone$, SUP.sphone1$
				IF VAL(phonex.pstncc$) < 1 THEN country$ = "   "
				IF VAL(phonex.pstncc$) >= 1 THEN country$ = phonex.pstncc$
'>>>>>>>>>>>>>>>>>>>>>>>> - Writes to the ASCII file - <<<<<<<<<<<<<<<<<<<<<<
		'>>>> - FORMAT FOR WINFAX - <<<<<
		company$ = phonex.company$
		csid$ = ""
		'lastname$            'lastname
		'firstname$           'firstname
		title$ = ""
		type$ = ""
		faxctry$ = country$
		faxarea$ = MID$(phonex.sphone1$, 1, 3)
		faxnum$ = MID$(phonex.sphone1$, 5, 13)
		faxext$ = ""
		altctry$ = ""
		altarea$ = "" ' MID$(phonex.sphone2$, 1, 3)
		altnum$ = "" ' MID$(phonex.sphone2$, 5, 13)
		altext$ = ""
		voicectry$ = country$
		voicearea$ = MID$(phonex.sphone$, 1, 3)
		voicenum$ = MID$(phonex.sphone$, 5, 13)
		voiceext$ = ""
		'can we input the mobile phones in this form
		celctry$ = "" ' country$
		celarea$ = "" ' (MID$(phonex.cell$, 1, 4)
		celnum$ = "" ' (MID$(phonex.cell$, 6, 12)
		celext$ = ""
		'sup.saddr$        'faxaddress1
		'sup.suburb$       'city
		state$ = ""
		'country$          country
		IF VAL(country$) < 1 THEN country$ = "Australia...."
		IF VAL(country$) = 1 THEN country$ = "America......"
		IF VAL(country$) = 27 THEN country$ = "South Africa."
		IF VAL(country$) = 39 THEN country$ = "Italy........"
		IF VAL(country$) = 55 THEN country$ = "Brazil......."
		IF VAL(country$) = 60 THEN country$ = "Malaysia....."
		IF VAL(country$) = 62 THEN country$ = "Indonesia...."
		IF VAL(country$) = 63 THEN country$ = "Phillipines.."
		IF VAL(country$) = 64 THEN country$ = "New Zealand.."
		IF VAL(country$) = 65 THEN country$ = "Singapore...."
		IF VAL(country$) = 66 THEN country$ = "Thailand....."
		IF VAL(country$) = 67 THEN country$ = "Brunei......."
		IF VAL(country$) = 81 THEN country$ = "Japan........"
		IF VAL(country$) = 82 THEN country$ = "Korea........"
		IF VAL(country$) = 86 THEN country$ = "P.R. Cinna..."
		IF VAL(country$) = 91 THEN country$ = "?????????????"
		'How do I hard code these better ?????
		'sup.spcode$       'zip
		faxaddress2$ = ""
		notes$ = "N"
		covpage$ = ""
		misc$ = "M"
		'phonex.key$       'bill
		ematype$ = ""
		emaaddr$ = ""
		exctype$ = ""
		excaddr$ = ""
		exchadd$ = ""
		CALL split(firstname$, lastname$)
'>>>>>>>>>>>>>>>>>>>>>>> - Writes to the PSION file. - <<<<<<<<<<<<<<<<<<<<<<<
		WRITE #2, faxt$, firstname$, lastname$, phonex.company$, Faxadd1$, Faxadd2$, Faxcity$, country$, Faxzip$, phonex.key$, "Misc...", "Notes.....", faxtype$, country$, faxarea$, faxnum$, faxext$, csid$, faxalias$, country$, voicearea$, voicenum$ _
, voiceext$, faxmt$, faxma$, faxpt$, faxpa$, faxmo$
'>>>>>>>>>>>>>>>>>>>>>>> - Writes to the FAX.. file  - <<<<<<<<<<<<<<<<<<<<<<<
		IF (MID$(phonex.sphone1$, 1, 3)) <> "111" THEN
		WRITE #3, phonex.company$, csid$, RTRIM$(lastname$), RTRIM$(firstname$), title$, type$, faxctry$, faxarea$, faxnum$, faxext$, altctry$, altarea$, altnum$, altext$, voicectry$, voicearea$, voicenum$, voiceext$, celctry$, celarea$, celnum$,  _
celext$, SUP.saddr$, SUP.suburb$, state$, country$, faxaddress2$, SUP.spcode$, notes$, coverpage$, misc$, phonex.key$, emailtype$, emailaddress$, exchtype$, exchaddtype$, exchadd$
		END IF
		f% = f% + 1
		IF i% MOD 100 = 0 THEN CALL sndmsg("Writing:" + STR$(i%) + "    Faxes:" + STR$(f%))
NEXTI:
		NEXT
	CLOSE
	CALL exitpgm(APGM$)
	CHAIN APGM$
	END
'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
'can we extend the print for #2 to #6 record on who-file - say with an
'appropriate letter added -  eg. -  briaga,briagb,briagc etc. and add the
'email address into the file - see winfax list

SUB qsort (in$(), in%(), n%, ok%) STATIC
'$INCLUDE: '\tpmanuf\src\QSORT.bi'
END SUB

SUB split (firstname$, lastname$)
wrk$ = phonex.name$
wrk$ = RTRIM$(LTRIM$(wrk$))

found% = 0
FOR i% = LEN(wrk$) TO 1 STEP -1
	IF MID$(wrk$, i%, 1) = " " THEN found% = -1: EXIT FOR
	NEXT

IF NOT found% THEN i% = LEN(wrk$): wrk$ = wrk$ + " "
firstname$ = MID$(wrk$, 1, i%)
lastname$ = MID$(wrk$, i% + 1)

FOR i% = 1 TO LEN(lastname$)
	IF MID$(lastname$, i%, 1) = "." THEN MID$(lastname$, i%, 1) = " "
	NEXT
firstname$ = firstname$ + SPACE$(20): firstname$ = MID$(firstname$, 1, 20)
lastname$ = lastname$ + SPACE$(20): lastname$ = MID$(lastname$, 1, 20)
END SUB

