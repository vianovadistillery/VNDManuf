'SUB rebuild.pe (ok%)
'.dc - Complete
    maxpe% = 100
    DIM pe%(100)
     FOR i% = 1 TO maxpe%: pe%(i%) = 0: NEXT
    '/////////////////  First time through get record address //////////////
     rec% = 1: n.pe% = 0: ecount% = 0
     GET #8, rec%, audit
     DO WHILE NOT EOF(8)
     IF audit.ADTYPE$ = "PE" THEN
        IF n.pe% = maxpe% THEN BEEP: EXIT DO
        n.pe% = n.pe% + 1
        pe%(n.pe%) = rec%
        END IF
    '/////////////////  Check figures are rounded    ///////////////////////
    test$ = STR$(audit.advalue)
    xc% = INSTR(test$, ".")
    IF xc% < 1 THEN xc% = LEN(test$): test$ = test$ + ".00"
    test$ = test$ + "00"
    small$ = MID$(test$, xc% + 3)
    IF VAL(small$) <> 0 THEN
        test$ = MID$(test$, 1, xc% + 2)
        audit.advalue = VAL(test$)
        IF small$ >= "50" THEN
                IF audit.advalue < 0 THEN audit.advalue = audit.advalue - .01
                IF audit.advalue >= 0 THEN audit.advalue = audit.advalue + .01
                END IF
        PUT #8, rec%, audit
        msg$ = "Oh shit!!  Values to 3 decimal places found!. Record " + STR$(rec%)
        CALL sndmsg(msg$)
        ecount% = ecount% + 1: IF ecount% < 10 THEN SLEEP 3
    END IF
    IF rec% MOD 100 = 0 THEN
            msg$ = "Rebuilding Period End.  Record " + STR$(rec%)
            CALL sndmsg(msg$)
            x$ = INKEY$: IF x$ = CHR$(0) + CHR$(59) THEN n.pe% = 0: EXIT DO
            END IF
    GET #8, , audit: rec% = rec% + 1
    LOOP
    '/////////////////  Go back and update the file   //////////////////////
     FOR i% = 1 TO n.pe%
        rec% = pe%(i%)
        GET #8, rec%, audit
        MID$(audit.ADSNAME$, 1, 2) = MKI$(pe%(i% + 1))
        MID$(audit.ADSNAME$, 3, 2) = MKI$(pe%(i% - 1))
        MID$(audit.ADSNAME$, 5, 2) = MKI$(pe%(n.pe%))
        PUT #8, rec%, audit
        NEXT

    msg$ = ""
    CALL sndmsg(msg$)

'END SUB


