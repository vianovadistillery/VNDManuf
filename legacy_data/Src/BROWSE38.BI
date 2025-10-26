'SUB browse38 (browse38.result%, updwn%) STATIC
     CALL setup("BROWSE FILE")
     COLOR 6, 0
     LOCATE 4, 2: PRINT "SEQ. DESCRIPTION.............. SUPL. A     PRICE. Restk  SOH.  SIP.  SOO. Reqd.";
     COLOR 2, 0
     btm$ = " F1-Exit   F3-Search   F5-Active/Suspended/Miscellaneous   F6-Alpha"
     CALL prtbtm(btm$): COLOR 2, 0
     REDIM rrn38%(maxrmat%)
     n% = 0
     paglen% = 19
     aselect$ = "*"
     xactive$ = "*"
     prevselect$ = aselect$
     dsplyfrom% = 1
     start% = browse38.result%
     skip% = -1
     updwn% = 13

browse38cf1:
    LOCATE 3, 23: PRINT "Browse from ........> ";
    IF NOT skip% THEN
      z$ = ""
      CALL inpnew(z$, 205!, updwn%, "13,59-61,63-64,72,73,80,81")
    END IF
    skip% = 0

    IF updwn% = 61 THEN
      LOCATE 3, 23: PRINT "Search......> ";
      z$ = ""
      CALL inpnew(z$, 215!, updwn%, "13,59-61,63-64,72,73,80,81")
      updwn% = 13

    END IF


    z$ = UCASE$(z$)
    IF MID$(z$, 1, 1) >= "A" AND MID$(z$, 1, 1) <= "Z" THEN aselect$ = z$
    IF prevselect$ <> aselect$ THEN
        n% = 0
        dsplyfrom% = 1
        start% = 1
        prevselect$ = aselect$
    END IF

    IF VAL(z$) > 0 THEN
        aselect$ = "*"
        n% = 0
        dsplyfrom% = 1
        start% = VAL(z$)
        prevselect$ = aselect$
    END IF


    SELECT CASE updwn%
    CASE 59: GOTO xbrowse38
    CASE 63:
            SELECT CASE xactive$
            CASE "*": xactive$ = "A"
            CASE "A": xactive$ = "S"
            CASE "S": xactive$ = "R"
            CASE "R": xactive$ = "M"
            CASE "M": xactive$ = "*"
            CASE ELSE: xactive$ = "*"
            END SELECT
            LOCATE 3, 70: PRINT USING "Active..:&"; xactive$
            n% = 0
            dsplyfrom% = 1
            start% = 1
    CASE 64: CALL browse38i(rec%)
             CALL setup("BROWSE FILE")
             COLOR 6, 0
             LOCATE 4, 2: PRINT "SEQ. DESCRIPTION.............. SUPL. A     PRICE. Restk  SOH.  SIP.  SOO. Reqd.";
             COLOR 2, 0
             btm$ = " F1-Exit   F3-Search   F5-Active/Suspended/Miscellaneous   F6-Alpha"
             CALL prtbtm(btm$): COLOR 2, 0


    CASE 72: dsplyfrom% = dsplyfrom% - 1
             IF dsplyfrom% <= 0 AND aselect$ = "*" THEN
                n% = 0
                start% = firstrec% - 1
                dsplyfrom% = 1
                prevselect$ = aselect$
                END IF
    CASE 73: dsplyfrom% = dsplyfrom% - paglen%
             IF dsplyfrom% <= 0 AND aselect$ = "*" THEN
                n% = 0
                dsplyfrom% = 1
                start% = firstrec% - paglen%
                prevselect$ = aselect$
                END IF

    CASE 80: dsplyfrom% = dsplyfrom% + 1
    CASE 81: dsplyfrom% = dsplyfrom% + paglen%
    CASE 13
    CASE ELSE
    END SELECT

    GOSUB load38
    GOSUB dsply38from
    GOTO browse38cf1


'>-- Load ---<
load38:
    thispag% = 0
    IF start% < 1 THEN start% = 1

    IF updwn% = 72 AND aselect$ = "*" THEN
    rec% = start%
    GET #38, rec%, msrmat
    DO WHILE msrmat.no% <> rec% AND rec% > 1
        start% = start% - 1
        rec% = start%
        GET #38, rec%, msrmat
    LOOP
    END IF

    FOR rec% = start% TO maxrmat%
        GET #38, rec%, msrmat
        IF msrmat.no% = rec% THEN       '??
          ok% = 0
          IF aselect$ = "*" THEN ok% = -1
          IF aselect$ = MID$(msrmat.desc1$, 1, LEN(aselect$)) THEN ok% = -1
          'IF INSTR(msrmat.desc1, aselect$) > 0 THEN ok% = -1
          'IF INSTR(msrmat.desc2, aselect$) > 0 THEN ok% = -1

          IF ok% AND xactive$ <> "*" AND msrmat.active$ <> xactive$ THEN ok% = 0
          
          IF ok% THEN
              n% = n% + 1
              rrn38%(n%) = rec%
              thispag% = thispag% + 1
              'IF thispag% > paglen% THEN EXIT FOR
              IF aselect$ = "*" AND thispag% > paglen% THEN EXIT FOR
              'IF aselect$ <> "*" THEN GOSUB dsply38from
          END IF
        END IF
        x$ = INKEY$
        IF x$ = CHR$(27) OR x$ = CHR$(0) + CHR$(59) THEN EXIT FOR
        IF rec% MOD 100 = 0 AND aselect$ <> "*" THEN CALL sndmsg(STR$(rec%))
        NEXT

        CALL sndmsg("")
        start% = rec% + 1'
RETURN


dsply38from:
IF dsplyfrom% < 1 THEN dsplyfrom% = 1
IF dsplyfrom% > n% THEN dsplyfrom% = n%


FOR lin% = 1 TO paglen%
    item% = dsplyfrom% + lin% - 1
    IF n% = 0 THEN EXIT FOR
    IF item% > n% THEN EXIT FOR

    rec% = rrn38%(item%)
    GET #38, rec%, msrmat
    LOCATE lin% + 4, 2: COLOR 2, 0
    reqd = msrmat.sip + msrmat.restock - msrmat.soh
    'LOCATE 4, 2: PRINT "SEQ. DESCRIPTION.............. SUPL. A     PRICE. Restk  SOH.  SIP.  SOO. Reqd.";
            PRINT USING "#### \                       \ \   \ \\#####.##\\ ##### ##### ##### ##### #####"; msrmat.no%; msrmat.desc1$; msrmat.search$; msrmat.active$; msrmat.PurCost; msrmat.PurUnit$; msrmat.restock; msrmat.soh; msrmat.sip; msrmat.soo _
; reqd
    IF lin% = 1 THEN firstrec% = rec%
    NEXT

i% = lin%
FOR lin% = i% TO paglen%
    LOCATE lin% + 4, 2: COLOR 2, 0
    PRINT SPACE$(78);
    NEXT
RETURN

xbrowse38:
    browse38.result% = firstrec%
    IF browse38.result% < 1 THEN browse38.result% = 1
    IF browse38.result% > maxrmat% THEN browse38.result% = 1
'END SUB


