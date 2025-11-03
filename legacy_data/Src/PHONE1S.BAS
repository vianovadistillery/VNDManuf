DECLARE SUB find.name (a$, opt%, found%)
DECLARE SUB contacts ()
DECLARE SUB box (x1%, y1%, x2%, y2%, fgnd%, bgnd%, box.type%)

'$INCLUDE: '\tpmanuf\src\PGMHEAD.INC'
   apgm$ = "*DOS"
''$INCLUDE: '\tpmanuf\src\PGMERR.INC'
	typefields% = -1
   '$INCLUDE: '\tpmanuf\src\phonex.inc'
   DIM SHARED scrnd%(21, 80), scrnc%(21, 80)
   '>>- Save the four lines of screen
	FOR y% = 1 TO 21
		FOR x% = 1 TO 80
		scrnd%(y%, x%) = SCREEN(y% + 0, x%, 0)
		scrnc%(y%, x%) = SCREEN(y% + 0, x%, 1)
		NEXT
	NEXT

	CALL box(1, 4, 80, 8, 10, 0, 2)

	'Get the last one we were looking at from the first record.
	 GET #52, 1, phonex
	a$ = phonex.key$
	skip% = -1
	opt% = 1
DO
	COLOR 10, 0
	LOCATE 4, 19: PRINT "µEnter search code...>     Æ"
	COLOR 6, 0
	LOCATE 5, 2: PRINT "Comp..."
	LOCATE 5, 9: COLOR 10, 0:
	PRINT USING "\                             \"; phonex.company$;
	LOCATE 5, 40: COLOR 6, 0: PRINT "Phone........ Fax.......... Mobile......"
	LOCATE 4, 40
	IF NOT skip% THEN CALL inpnew(a$, 105!, updwn%, "13,59,73,81,80")
	skip% = 0
	IF updwn% = 59 THEN EXIT DO
	IF updwn% = 73 THEN a$ = "*PREV"
	IF updwn% = 81 THEN a$ = "*NEXT"
	'IF updwn% = 80 THEN CALL contacts: GOTO iterate

	CALL find.name(a$, opt%, ok%)
	IF VAL(phonex.pstncc$) = 0 THEN
		wrkpstncc$ = "    "
		ELSE
		wrkpstncc$ = "(" + phonex.pstncc$ + ")"
		END IF

	COLOR 6, 0
	LOCATE 6, 2: PRINT "Name..."
	LOCATE 6, 9: COLOR 10, 0:                  '111-1111-1111 111-1111-1111 1111-111-111
	PRINT USING "\                   \    \   \ \            \\            \\          \"; phonex.name$; wrkpstncc$; phonex.sphone$; phonex.sphone1$; phonex.contactmobile(1)
	COLOR 6, 0
	LOCATE 7, 2: PRINT "H/page."
	LOCATE 7, 40: PRINT "e-mail."
	COLOR 10, 0:
	LOCATE 7, 9
	PRINT USING "\                           \"; phonex.www$;
	LOCATE 7, 47
	PRINT USING "\                             \"; phonex.email;
	CALL contacts
iterate:
LOOP

'>>- Restore the four lines of screen
 FOR y% = 1 TO 21
	 FOR x% = 1 TO 80
	 of% = (scrnc%(y%, x%) MOD 16): ob% = (((scrnc%(y%, x%) - of%) / 16) MOD 128)'Set prev colour
	 IF scrnc%(y%, x%) > 127 THEN of% = of% + 16': ob% = ob% + 16
	 COLOR of%, ob%
	 LOCATE y% + 0, x%: PRINT CHR$(scrnd%(y%, x%))
	 NEXT
 NEXT
 'Save the last one we were looking at in the first record.
  PUT #52, 1, phonex
END

SUB contacts

'>-Set the number of
count% = 0
FOR j% = 2 TO 6
IF MID$(phonex.contactfirstname(j%), 1, 1) > " " OR MID$(phonex.contactsurname(j%), 1, 1) > " " THEN
	count% = count% + 1
END IF
NEXT
IF count% = 0 THEN
	LOCATE 8, 1: PRINT "È"; STRING$(78, "Í"); "¼";
	GOTO x.contacts
END IF

CALL box(1, 8, 80, count% * 2 + 8, 10, 0, 2)
COLOR 10, 0
LOCATE 8, 1: PRINT "º"
LOCATE 8, 80: PRINT "º"
LOCATE 8, 2: COLOR 2, 0: PRINT SPACE$(78)

COLOR 2, 0

FOR j% = 1 TO count%
	k% = j% + 1
	LOCATE 6 + j% * 2 + 0, 2: PRINT "XXX"
	LOCATE 6 + j% * 2 + 0, 2: PRINT phonex.contactfirstname(k%); " "; phonex.contactsurname(k%);
	LOCATE 6 + j% * 2 + 0, 42: PRINT phonex.ContactTitle(k%); phonex.ContactPhone(k%);
	LOCATE 6 + j% * 2 + 1, 25: PRINT phonex.contactemail(k%);
	LOCATE 6 + j% * 2 + 1, 62: PRINT phonex.contactmobile(k%);
NEXT

x.contacts:

'>>- Restore the four lines of screen
 FOR y% = count% * 2 + 9 TO 21
	 FOR x% = 1 TO 80
	 of% = (scrnc%(y%, x%) MOD 16): ob% = (((scrnc%(y%, x%) - of%) / 16) MOD 128)'Set prev colour
	 IF scrnc%(y%, x%) > 127 THEN of% = of% + 16': ob% = ob% + 16
	 COLOR of%, ob%
	 LOCATE y% + 0, x%: PRINT CHR$(scrnd%(y%, x%))
	 NEXT
 NEXT


END SUB

SUB find.name (a$, opt%, found%) STATIC
'Note: The first record is used to rember where we are up to!
	found% = 0
	a$ = UCASE$(a$)
	SELECT CASE a$
	CASE "*NEXT": rec% = rec% + 1: s% = rec%: e% = rec%: GET #52, rec%, phonex: a$ = phonex.key$
	CASE "*PREV": rec% = rec% - 1: s% = rec%: e% = rec%: GET #52, rec%, phonex: a$ = phonex.key$
	CASE "*USED": rec% = 1: s% = rec%: e% = rec%: a$ = ""
	CASE ELSE: s% = 1: e% = (LOF(52) / LEN(phonex)) + 1
	END SELECT
	IF e% < 1 THEN EXIT SUB
	IF s% < 2 THEN s% = 2
	old.rec% = -1
DO WHILE rec% <> old.rec%
	old.rec% = rec%
	rec% = (e% - s%) / 2 + s%
	GET #52, rec%, phonex
	IF a$ = phonex.key$ THEN found% = -1: EXIT DO
	IF a$ < phonex.key$ THEN e% = rec%
	IF a$ > phonex.key$ THEN s% = rec%
	LOOP
	IF NOT found% AND rec% <> s% THEN
		rec% = s%
		GET #52, rec%, phonex
		END IF
END SUB
