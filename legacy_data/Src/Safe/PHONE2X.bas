	DECLARE SUB split (Firstname$, lastname$)
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
	GET #43, rec%, sup
		DO WHILE NOT EOF(43)
			IF rec% = CVI(sup.sno$) THEN
			IF sup.sdate$ > "19000101" AND sup.sdate$ < "20991231" THEN
			n% = n% + 1: IF n% > max% THEN n% = max%: BEEP
			in%(n%) = CVI(sup.sno$)
			in$(n%) = sup.search$ + sup.stype$ + "43"
			END IF
		END IF
	GET #43, , sup: rec% = rec% + 1
	LOOP
	PRINT USING "##,###"; rec%
	LOCATE 7, 20: PRINT "Reading Supplier file...........";
	rec% = 1
	GET #44, rec%, sup
		DO WHILE NOT EOF(44)
			IF rec% = CVI(sup.sno$) THEN
			IF sup.sdate$ > "19000101" AND sup.sdate$ < "20991231" THEN
			n% = n% + 1: IF n% > max% THEN n% = max%: BEEP
			in%(n%) = CVI(sup.sno$)
			in$(n%) = sup.search$ + sup.stype$ + "44"
			END IF
		END IF
	GET #44, , sup: rec% = rec% + 1
	LOOP
	PRINT USING "##,###"; rec%
	LOCATE 8, 20: PRINT "Reading xxxxxxxx file...........";
	rec% = 1
	GET #64, rec%, sup
		DO WHILE NOT EOF(64)
			IF rec% = CVI(sup.sno$) THEN ' AND sup.stype = "S" THEN???
			IF sup.sdate$ > "19000101" AND sup.sdate$ < "20991231" THEN
			n% = n% + 1: IF n% > max% THEN n% = max%: BEEP
			in%(n%) = CVI(sup.sno$)
			in$(n%) = sup.search$ + sup.stype$ + "64"
			END IF
		END IF
	GET #64, , sup: rec% = rec% + 1
	LOOP
	PRINT USING "##,###"; rec%
'>>>>>>>>>>>> - .............................................. - <<<<<<<<<<<<
	LOCATE 12, 20: PRINT "Sorting the records............."
	CALL qsort(in$(), in%(), n%, ok%)
	COLOR 2, 0
	LOCATE 14, 20: PRINT "Writing new file................"
	LOCATE 1, 1
	CLOSE #52
	OPEN "phonex.who" FOR OUTPUT SHARED AS #52 LEN = LEN(phonex)
	CLOSE #52
	OPEN "phonex.who" FOR RANDOM SHARED AS #52 LEN = LEN(phonex)
'----------------------------------------------------------------------------
'>>>>>>>>>>>>> -                 Write new file.               - <<<<<<<<<<<<
'----------------------------------------------------------------------------
	FOR i% = 1 TO n%
		rec% = in%(i%)
		ch% = VAL(MID$(in$(i%), 6, 2))
			GET #ch%, rec%, sup
				phonex.key = in$(i%)
			SELECT CASE ch%
				CASE 43: phonex.type = "DB"
				CASE 44: phonex.type = "CR"
				CASE 64: phonex.type = "--"
				CASE ELSE: phonex.type = "??"
			END SELECT
			phonex.company = sup.sname$
			phonex.compnum = MID$(STR$(rec%), 2)
			phonex.name = sup.scont$
			phonex.sPhone = sup.sPhone$
			phonex.sPhone1 = sup.sPhone1$
			FOR j% = 1 TO 6
				phonex.ContactFirstName(j%) = sup.ContactFirstName(j%)
				phonex.ContactSurName(j%) = sup.ContactSurName(j%)
				phonex.ContactTitle(j%) = sup.ContactTitle(j%)
				phonex.ContactPhone(j%) = sup.ContactPhone(j%)
				phonex.contactmobile(j%) = sup.contactmobile(j%)
				phonex.Contactemail(j%) = sup.Contactemail(j%)
			NEXT
				phonex.email = sup.email
				phonex.www = sup.www
				phonex.pstncc$ = sup.pstncc$
				phonex.crlf$ = CHR$(13) + CHR$(10)

'>>>>>>>>>>>> -  Don't write records if the numbers are blank  - <<<<<<<<<<<<
			P1Blank% = 0
			P2Blank% = 0
			P3Blank% = 0

			IF phonex.sPhone = "111-1111-1111" THEN P1Blank% = -1
			IF phonex.sPhone1 = "111-1111-1111" THEN P2Blank% = -1
			IF phonex.contactmobile$(1) = "1111-111-111" THEN P3Blank% = -1
			ok% = -1
			IF P1Blank% AND P2Blank% AND P3Blank% THEN ok% = 0
			IF NOT ok% THEN GOTO NEXTI
'>>>>>>>>>>>> -         It only gets here it its valid         - <<<<<<<<<<<<
		IF i% = 1 THEN
			PUT #52, i%, phonex
			ELSE
			PUT #52, , phonex
			END IF
		IF LOF(98) = 0 THEN
			WRITE #98, "Search :", "Comp   :", "Addr   :", "....  :", "Phone/Fax:"
			END IF
		WRITE #98, phonex.key$ + " " + phonex.name$, phonex.company$, sup.saddr$, sup.suburb$ + sup.spcode$, sup.sPhone$ + "," + sup.sPhone1$
'>>>>>>>>>>>> -   This section writes to the flat ASCII file   - <<<<<<<<<<<<
		IF VAL(MID$(phonex.sPhone1$, 1, 2)) > 0 THEN
			faxt$ = ""
			Faxadd1$ = sup.saddr$
			Faxadd2$ = ""
			Faxcity$ = sup.suburb$
		  ' Faxstat$ = ""
			Faxzip$ = sup.spcode$
			Faxcc$ = ""
			faxac$ = ""
			faxext$ = ""
			faxalias$ = ""
			Voicecc$ = ""
			Voiceac$ = ""
			voiceext$ = ""
			faxmt$ = ""
			faxma$ = ""
			faxpt$ = ""
			faxpa$ = ""
			faxmo$ = "*"
				IF VAL(phonex.pstncc$) > 0 THEN
				Faxcc$ = phonex.pstncc$
			  ' faxac$ = phonex.pstncc$
				FOR j% = 1 TO LEN(faxac$)
				IF MID$(faxac$, j%, 1) < " " THEN MID$(faxac$, j%, 1) = " "
				NEXT
				Voicecc$ = phonex.pstncc$
			  ' Voiceac$ = phonex.pstncc$
				FOR j% = 1 TO LEN(Voiceac$)
				IF MID$(Voiceac$, j%, 1) < " " THEN MID$(Voiceac$, j%, 1) = " "
				NEXT
				END IF
			  ' CALL split(Firstname$, Lastname$)'????
'>>>>>>>>>>>> -            Write to the PSION file.            - <<<<<<<<<<<<
		WRITE #2, faxt$, Firstname$, lastname$, phonex.company$, Faxadd1$, Faxadd2$, Faxcity$, "AUSTRALIA.", Faxzip$, phonex.key$, "Misc...", "Notes.....", faxtype$, Faxcc$, faxac$, phonex.sPhone1$, faxext$, csid$, faxalias$, Voicecc$, Voiceac$,  _
phonex.sPhone$, voiceext$, faxmt$, faxma$, faxpt$, faxpa$, faxmo$

'>>>>>>>>>>>> -             Write to the FAX file              - <<<<<<<<<<<<
		IF phonex.sPhone1 <> "111-1111-1111" THEN
		WRITE #3, phonex.company$, "", Firstname$ + lastname$, "", faxtype$, Faxcc$, "", phonex.sPhone1$, "", "", "", "", "", Voicecc$, "", phonex.sPhone$, "", "", "", "", "", Faxadd1$, "", "", "AUSTRALIA.", Faxzip$, Faxadd2$, "", "", "", phonex. _
key$, "", "", "", "", ""
		END IF
		f% = f% + 1
		END IF
		IF i% MOD 100 = 0 THEN CALL sndmsg("Writing:" + STR$(i%) + "    Faxes:" + STR$(f%))
NEXTI:
		NEXT
	CLOSE
		CALL exitpgm(APGM$)
	CHAIN APGM$
	END

SUB qsort (in$(), in%(), n%, ok%) STATIC
'$INCLUDE: '\tpmanuf\src\QSORT.bi'
END SUB

SUB split (Firstname$, lastname$)
wrk$ = phonex.name$
wrk$ = RTRIM$(LTRIM$(wrk$))

found% = 0
FOR i% = LEN(wrk$) TO 1 STEP -1
	IF MID$(wrk$, i%, 1) = " " THEN found% = -1: EXIT FOR
	NEXT

IF NOT found% THEN i% = LEN(wrk$): wrk$ = wrk$ + "  "
Firstname$ = MID$(wrk$, 1, i%)
lastname$ = MID$(wrk$, i% + 1)

FOR i% = 1 TO LEN(lastname$)
	IF MID$(lastname$, i%, 1) = "." THEN MID$(lastname$, i%, 1) = " "
	NEXT
Firstname$ = Firstname$ + SPACE$(20): Firstname$ = MID$(Firstname$, 1, 20)
lastname$ = lastname$ + SPACE$(20): lastname$ = MID$(lastname$, 1, 20)
END SUB
