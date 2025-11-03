	 ' Q S M E N U
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "MENUTP"
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	GET #36, 1, msmisc
	cca$ = msmisc.cc$
	CLOSE
start:
	CALL SETUP(cca$)
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : COLOR 2, 0
	COLOR 4, 0
	LOCATE 4, 23: PRINT " Q U A L I T Y    S Y S T E M "
	LOCATE 5, 23: PRINT "=============================="
	COLOR 2, 0
	LOCATE 7, 25: PRINT "1.....Complaints.............."
	LOCATE 9, 25: PRINT "2.....Exposure Panels........."
	LOCATE 11, 25: PRINT "3.....Non Comformance Data...."
	LOCATE 13, 25: PRINT "4.....Development Projects...."
	LOCATE 15, 25: PRINT "5.....Trading Projects........"
	LOCATE 17, 25: PRINT "6.....Extra 2................."
	LOCATE 19, 25: PRINT "91....Copy data to diskette..."
	LOCATE 20, 25: PRINT "92....Copy data from diskette."

	IF msmisc.inside$ = "N" AND 1 = 0 THEN
		Newword$ = ""
		CALL SNDMSG("Enter password..>")
		DO
			a$ = ""
			LOCATE 24, 21 + LEN(Newword$)
			DO UNTIL a$ <> "": a$ = INKEY$: LOOP
			IF LEN(a$) = 1 AND a$ = CHR$(13) THEN EXIT DO
			Newword$ = Newword$ + a$
			LOOP
		IF UCASE$(Newword$) <> "QAS" THEN END
		CALL setsec(25, 4, "", 42, "1o4ap03")
		CALL SNDMSG("")
	END IF

	'>>>>> OPTIONS
getopt: LOCATE 22, 27: PRINT "Option..> ";
	a$ = "": updwn% = 1: LOCATE 22, 36
	CALL inpnew(a$, 102!, updwn%, "59,13" + alt$): GOSUB alt
	IF updwn% = 59 THEN CLOSE : CALL exitpgm(apgm$): CHAIN apgm$
	b% = VAL(a$)
	IF b% = 1 THEN ENVIRON ("PARM$=com."): achain$ = "qscom01": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 2 THEN ENVIRON ("PARM$=...."): achain$ = "qsexp01": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 3 THEN ENVIRON ("PARM$=ncr."): achain$ = "qscom01": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 4 THEN ENVIRON ("PARM$=pro."): achain$ = "qspro01": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 5 THEN ENVIRON ("PARM$=ext1"): achain$ = "qspro02": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 6 THEN ENVIRON ("PARM$=ext2"): achain$ = "qspro02": CALL exitpgm(achain$): CHAIN achain$
	IF b% = 91 THEN
				LOCATE 23, 26: PRINT "Continue.(Y/N)..>";
				a$ = "N"
				DO
				LOCATE 23, 43: CALL inpnew(a$, 101!, updwn%, "13,27,59")
				a$ = UCASE$(a$)
				IF updwn% = 27 THEN a$ = "N"
				IF updwn% = 59 THEN a$ = "N"
				LOOP UNTIL a$ = "Y" OR a$ = "N"
				IF a$ = "N" THEN GOTO start

				shella$ = "COPY QS*.EXE      A:\"
				shellb$ = "COPY \QB7\BRT71EFR.EXE     A:\"
				shellc$ = "COPY *.QLB        A:\"
				shelld$ = "COPY MSMISC.MSF   A:\"
				shelle$ = "COPY CUS*.WHO     A:\"
				shellf$ = "COPY SUP*.WHO     A:\"
				shellg$ = "COPY COMPLNT.DAT  A:\"
				shellh$ = "COPY EXPOSURE.DAT A:\"
				shelli$ = "COPY NONCONF.DAT  A:\"
				LOCATE 2, 1
				SHELL shella$
				SHELL shellb$
				SHELL shellc$
				SHELL shelld$
			 OPEN "A:msmisc.msf" FOR RANDOM SHARED AS #36 LEN = 128
			 GET #36, 1, msmisc
			 msmisc.inside$ = "N"
			 PUT #36, 1, msmisc
			 CLOSE #36
				SHELL shelle$
				SHELL shellf$
				SHELL shellg$
				SHELL shellh$
				SHELL shelli$
		END IF

	IF b% = 92 THEN
				LOCATE 23, 26: PRINT "Continue.(Y/N)..>";
				a$ = "N"
				DO
				LOCATE 23, 43: CALL inpnew(a$, 101!, updwn%, "13,27,59")
				a$ = UCASE$(a$)
				IF updwn% = 27 THEN a$ = "N"
				IF updwn% = 59 THEN a$ = "N"
				LOOP UNTIL a$ = "Y" OR a$ = "N"
				IF a$ = "N" THEN GOTO start

				shella$ = "COPY A:COMPLNT.DAT  \TPMANUF\*.MNT"
				shellb$ = "COPY A:EXPOSURE.DAT \TPMANUF\*.MNT"
				shellc$ = "COPY A:NONCONF.DAT  \TPMANUF\*.MNT"
				LOCATE 2, 1
				SHELL shella$
				SHELL shellb$
				SHELL shellc$
		END IF

	GOTO getopt
