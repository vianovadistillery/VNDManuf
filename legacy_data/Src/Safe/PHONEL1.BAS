'///////////////////////////////////////////////////////////////////////////
'>>>> List
'///////////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
APGM$ = "MSMENU"
'$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	CALL setup("LIST ALL PHONE NUMBERS ON FILE")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : COLOR 2, 0
	 stdout$ = "LPT1"
'    stdout$ = ""
	'$INCLUDE: '\tpmanuf\src\phonex.inc'

	do.list$ = "S"
START:
	LOCATE 5, 25: PRINT "Print phone numbers,All or Short (A/S)...> "
	DO
		LOCATE 5, 67
		CALL INPNEW(do.list$, 101!, UPDWN%, "13,59")
		do.list$ = UCASE$(do.list$)
		IF UPDWN% = 59 THEN EXIT DO
		LOOP UNTIL do.list$ = "A" OR do.list$ = "S"
	IF UPDWN% = 59 THEN CLOSE : CALL EXITPGM(APGM$): CHAIN APGM$
	GOSUB do.list
	do.list$ = " "

	IF stdout$ > "" THEN
		shella$ = "copy Phonel1.prn " + stdout$
		SHELL shella$
	END IF

	GOTO START
'///////////////////////////////////////////////////////////////////////////
'>>>> Print the List
'///////////////////////////////////////////////////////////////////////////
do.list:
	OPEN "Phonel1.prn" FOR OUTPUT AS #99
	WIDTH #99, 132

	COLOR 2, 0
	pag% = 0: lin% = 999: paglen% = 54
	rec% = 1
	GET #52, rec%, phonex

	DO WHILE NOT EOF(52) AND rec% < 999'???

		'>- Allow F1
		CALL INPNEW(a$, 0!, UPDWN%, "")
		x$ = INKEY$
		IF LEN(x$) = 2 THEN
			IF ASC(MID$(x$, 2)) = 59 THEN EXIT DO
			END IF

		LOCATE 9, 25: PRINT USING "Record #,###   Selected #,###"; rec%; sel%
		phone1$ = phonex.sphone$:
		phone2$ = phonex.sphone1$
		phone3$ = phonex.contactmobile$(1)

		IF VAL(MID$(phone1$, 1, 3)) <= 0 THEN phone1$ = ""
		IF VAL(MID$(phone1$, 1, 3)) = 111 THEN phone1$ = ""

		IF VAL(MID$(phone2$, 1, 3)) <= 0 THEN phone2$ = ""
		IF VAL(MID$(phone2$, 1, 3)) = 111 THEN phone2$ = ""

		IF VAL(MID$(phone3$, 1, 3)) <= 0 THEN phone3$ = ""
		IF VAL(MID$(phone3$, 1, 3)) = 111 THEN phone3$ = ""

		ok% = -1
		IF do.list$ = "S" THEN
			IF phone1$ = "" AND phone2$ = "" AND phone3$ = "" THEN ok% = 0
		END IF

		IF ok% THEN
			IF lin% >= paglen% THEN GOSUB HEADING
			PRINT #99, USING "     \                            \        \   \       \                  \      \          \      \          \     \           \"; phonex.company; phonex.key; phonex.name; phone1$; phone2$; phone3$
			lin% = lin% + 1: sel% = sel% + 1

			FOR c% = 2 TO 6
				IF RTRIM$(phonex.contactfirstname(c%)) > "A" THEN
					who1$ = RTRIM$(phonex.contactfirstname(c%))
					who2$ = RTRIM$(phonex.contactsurname(c%))
					who$ = who1$ + " " + who2$
					phone1$ = phonex.contactphone$(c%)
					phone2$ = phonex.contactfax$(c%)
					phone3$ = phonex.contactmobile$(c%)

					IF VAL(MID$(phone1$, 1, 3)) <= 0 THEN phone1$ = ""
					IF VAL(MID$(phone1$, 1, 3)) = 111 THEN phone1$ = ""

					IF VAL(MID$(phone2$, 1, 3)) <= 0 THEN phone2$ = ""
					IF VAL(MID$(phone2$, 1, 3)) = 111 THEN phone2$ = ""

					IF VAL(MID$(phone3$, 1, 3)) <= 0 THEN phone3$ = ""
					IF VAL(MID$(phone3$, 1, 3)) = 111 THEN phone3$ = ""


				PRINT #99, USING "                                                       \                        \\          \      \          \     \           \"; who$; phone1$; phone2$; phone3$
				lin% = lin% + 1
				END IF
			NEXT

		END IF


		GET #52, , phonex: rec% = rec% + 1
		LOOP
	PRINT #99, CHR$(12);
	CLOSE #99

	LOCATE 11, 25: COLOR 2: PRINT "Print complete"
RETURN
'////////////////////////////////////////////////////////////////////////////
'>>>>>  H E A D I N G
'////////////////////////////////////////////////////////////////////////////
HEADING:
	pag% = pag% + 1: lin% = 0
	IF pag% > 1 THEN PRINT #99, CHR$(12)
	PRINT #99, CHR$(18)
	PRINT #99, "   #Phonel1 "; date1$; TAB(68); "Page: "; pag%
	PRINT #99, "                           T E L E P H O N E     L I S T"
	PRINT #99, "   Company...........    Cde    Name........    Phone.     Fax...    Mobile "
	PRINT #99, "   "; STRING$(72, "-")
	PRINT #99, CHR$(15);
RETURN

