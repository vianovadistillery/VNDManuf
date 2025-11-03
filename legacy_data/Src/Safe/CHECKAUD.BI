'SUB checkaudit (updwn%,DB.OR.CR$)
    CALL sndmsg("Checking all records on audit file for customer records.  F1-stop")

    msg$ = ""
    rrn% = 1
    GET #8, rrn%, Audit
    DO WHILE NOT EOF(8)
        IF audit.adactive <> "*" THEN

        test$ = MID$(Audit.ADTYPE$, 1, 1)
        IF test$ = MID$(DB.OR.CR$, 1, 1) THEN
            skey$ = Audit.adcust$
            CALL searchindex(skey$, cha%, found%)
            IF NOT found% THEN
              msg$ = "Customer " + Audit.adcust$ + " " + Audit.ADTYPE$ + "  at record " + STR$(rrn%) + " of the audit file."
              CALL sndmsg(msg$)

              atimer = TIMER
              DO:
                x$ = INKEY$
                IF x$ > "" THEN EXIT DO
              LOOP WHILE ABS(TIMER - atimer) < 2.5
              IF x$ = CHR$(0) + CHR$(59) THEN updwn% = 59: EXIT DO
              IF x$ = CHR$(0) + CHR$(60) THEN updwn% = 60: EXIT DO

              'CALL inpnew(a$, 0!, updwn%, "13,59-60")
              'IF updwn% = 59 THEN EXIT DO
            END IF
        END IF

        END IF
        IF rrn% MOD 100 = 0 THEN LOCATE 24, 69: PRINT USING "##,###"; rrn%;
        x$ = INKEY$
        IF x$ = CHR$(0) + CHR$(59) THEN updwn% = 59: EXIT DO
        IF x$ = CHR$(0) + CHR$(60) THEN updwn% = 60: EXIT DO
        GET #8, , Audit: rrn% = rrn% + 1
        LOOP

    CALL sndmsg(msg$)
'END SUB
