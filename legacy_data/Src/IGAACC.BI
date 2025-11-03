'SUB IGAAcc (rec%)
  IF rec% < 1 OR rec% > maxacc% THEN GOTO xigaacc
  maxlines% = 20
  Toggle$ = "*"
  DIM rrn%(maxlines%)

  GET #44, rec%, sup

'////////////////////////////////////////////////////////////////////////////
  CALL setup("ACCESSORY DELIVERY")
  COLOR 4: LOCATE 3, 2: PRINT "No.  DESCRIPTION                           SIZE     A    COST   STOCK     ADD ";

  COLOR 7, 0: LOCATE 2, 10: PRINT "µ                          Æ"; : COLOR 2
  COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit   F2-Change Cost   F3-Toggle Act/Susp/All"; : LOCATE 25, 71: PRINT CHR$(24); CHR$(25); "-Move"; : COLOR 2, 0
  COLOR 7, 0: LOCATE 2, 43: PRINT USING "µ\                                 \Æ"; sup.sname$: COLOR 2

  frm% = 1
  skip% = -1
  i% = 1

entryAcc:
  COLOR 2: LOCATE 2, 11: PRINT "Enter from number....>";
  IF NOT skip% THEN
    frm$ = "    "
    LOCATE 2, 33
    CALL inpnew(frm$, 4!, updwn%, "13,59,61")
    IF updwn% = 59 THEN GOTO xigaacc
    frm% = VAL(frm$)
    i% = 1
  END IF
  skip% = 0

  IF updwn% = 61 THEN
    SELECT CASE Toggle$
    CASE "*": Toggle$ = "A"
    CASE "A": Toggle$ = "S"
    CASE "S": Toggle$ = "M"
    CASE "M": Toggle$ = "R"
    CASE ELSE: Toggle$ = "*"
    END SELECT
    CALL sndmsg("Selecing " + Toggle$)
  END IF

nxtpagAcc:
  IF frm% <= 0 THEN frm% = 1
  IF frm% >= maxacc% THEN frm% = maxacc%

  n% = 0: r% = 0: fst% = 0
  lastline% = 0
  '***** set first screen with details
  r% = frm%
  IF r% < 1 OR r% >= maxacc% THEN GOTO entryAcc
  GET #3, r%, acstk

  DO WHILE n% <= maxlines% - 1 AND r% < maxacc%

     '-Selection
     ok% = 0
     IF acstk.suplr = sup.search$ + sup.stype$ THEN
     IF r% >= frm% THEN
     IF Toggle$ = "*" OR Toggle$ = acstk.active$ THEN
     IF acstk.purcost > .0001 THEN
        ok% = -1
     END IF
     END IF
     END IF
     END IF

     IF ok% THEN
       n% = n% + 1
       LOCATE n% + 3, 2
       GOSUB prtlineAcc
       rrn%(n%) = r%   '***** Save record number
       lastline% = n%
     END IF

    GET #3, , acstk: r% = r% + 1
    IF EOF(38) THEN EXIT DO
  LOOP

  '***** If maxlines% records not found clear to end of screen
  FOR j% = n% TO maxlines% - 1
     LOCATE j% + 4, 2
     PRINT CHR$(FNE)
     rrn%(j% + 1) = 0
  NEXT
  IF n% <= 0 THEN GOTO entryAcc

  IF i% <= 0 THEN i% = 0
  IF i% > lastline% THEN i% = lastline%

  '***** Key in new stock
  DO
    r% = rrn%(i%)
    IF r% < 1 OR r% > maxacc% THEN EXIT DO     '***** No record
    GET #3, r%, acstk
    upd0$ = ""
    upd1$ = ""
    GOTO cf3bAcc

cf3aAcc:
    upd0$ = STR$(acstk.purcost)
    LOCATE i% + 3, 56
                CALL inpnew(upd0$, 6.2, updwn%, "13,59,60,72,73,80,81")
    IF updwn% = 59 THEN     '***** F1 pressed
      LOCATE i% + 3, 2
      GOSUB prtlineAcc
      EXIT DO
    END IF


cf3bAcc:
    upd1$ = ""
    LOCATE i% + 3, 74
    CALL inpnew(upd1$, -4!, updwn%, "13,59,60-61,72,73,80,81")
    LOCATE i% + 3, 73: PRINT "|_____|";

    IF updwn% = 60 GOTO cf3aAcc
    IF updwn% = 59 THEN     '***** F1 pressed
      LOCATE i% + 3, 2
      GOSUB prtlineAcc
      EXIT DO
    END IF
    IF updwn% = 61 THEN
      skip% = -1
      GOTO entryAcc
    END IF



  '***** Calculate stock value and print on screen
    GET #3, r%, acstk
    IF upd0$ > "" THEN
      acstk.purcost = VAL(upd0$)
      CALL calcusecost
    END IF
    acstk.soh = acstk.soh + VAL(upd1$)
    extval = acstk.soh * acstk.purcost
    wrkd$ = MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2)
    LSET acstk.date$ = FNDY$(wrkd$)
    PUT #3, r%, acstk

    LOCATE i% + 3, 2
    GOSUB prtlineAcc

    SELECT CASE updwn%
    CASE 72: IF i% > 1 THEN i% = i% - 1:  ELSE EXIT DO 'Up arrow
    CASE 80: IF i% < maxlines% THEN i% = i% + 1 ELSE EXIT DO 'Dwn arrow
    END SELECT
  LOOP

  IF updwn% = 72 THEN
    'Search Backward
    r% = rrn%(1):
    ok% = 0
    DO
      r% = r% - 1
      IF r% < 1 OR r% > maxacc% THEN r% = 1: EXIT DO
      GET #3, r%, acstk
      '-Selection
      ok% = 0
      IF acstk.suplr = sup.search$ + sup.stype$ THEN
      IF r% >= 1 THEN  'Note was frm% THEN
      IF Toggle$ = "*" OR Toggle$ = acstk.active$ THEN
      IF acstk.purcost > .0001 THEN
         ok% = -1
      END IF
      END IF
      END IF
      END IF

      IF ok% THEN
        EXIT DO
      END IF

    LOOP
    IF ok% THEN frm% = r%
    GOTO nxtpagAcc 'Up arrow
  END IF

  IF updwn% = 80 THEN 'Arrow down
    'Search forward
    r% = rrn%(lastline%)

    ok% = 0
    DO
      r% = r% + 1
      IF r% < 1 OR r% > maxacc% THEN r% = 1: EXIT DO
      GET #3, r%, acstk
      '-Selection
      ok% = 0
      IF acstk.suplr = sup.search$ + sup.stype$ THEN
      IF r% >= 1 THEN  'Note was frm% THEN
      IF Toggle$ = "*" OR Toggle$ = acstk.active$ THEN
      IF acstk.purcost > .0001 THEN
         ok% = -1
      END IF
      END IF
      END IF
      END IF

      IF ok% THEN
        EXIT DO
      END IF

    LOOP
    frm% = rrn%(1)
    IF ok% THEN frm% = rrn%(2)
    GOTO nxtpagAcc
  END IF

   '>>>>> Go back to start of browse
  IF updwn% = 59 THEN GOTO entryAcc
  roll = 1': GOTO ENTRY
'***** If enter is pressed at end of screen fields, start next screen
   frm% = r%
   LOCATE 2, 44: PRINT USING "####"; frm%
   IF frm% < 1 OR frm% > maxacc% THEN frm% = 1
   frm$ = STR$(frm%)
   IF fst% = 0 THEN roll = 1
   fst% = 0
   GOTO nxtpagAcc

'>>>>>  P R I N T    A   L I N E
prtlineAcc:
  IF acstk.soh% < -999 THEN acstk.soh% = -999
  COLOR 2
  PRINT USING "#### \                        \\         \ \  \\\   ! ####.##    ####  |___________|"; r%; acstk.desc1$; acstk.desc2$; acstk.size$; acstk.unit$; acstk.active; acstk.purcost; acstk.soh%
  RETURN
xigaacc:
'END SUB
