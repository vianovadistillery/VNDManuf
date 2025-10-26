' SUB setaudit (n%)
' INCLUDE: '\tpmanuf\src\setaudit.bi'
    FOR i% = 1 TO 15: auditfile$(i%) = "": NEXT
    n% = 0

    FOR i% = 1 TO 15
    p% = 88 + i% - 1
    s% = p% + 1
    p$ = RIGHT$("00" + MID$(STR$(p%), 2), 2)
    s$ = RIGHT$("00" + MID$(STR$(s%), 2), 2)
    wrk$ = "YEAR" + p$ + s$ + ".HST"
    ok% = 0
        a$ = DIR$(wrk$)
        IF a$ <> "" THEN
        OPEN wrk$ FOR RANDOM SHARED AS #99
        IF LOF(99) > 0 THEN ok% = -1
        CLOSE #99
        END IF

    IF ok% THEN
        n% = n% + 1
        auditfile$(n%) = wrk$
        END IF
    NEXT

    n% = n% + 1
    auditfile$(n%) = "ASAUDIT.ASF"

