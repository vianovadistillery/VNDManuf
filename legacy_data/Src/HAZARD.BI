'SUB hazard (code$) STATIC
    IF NOT dimhaz% THEN
        DIM haz$(30)
        '         "01-3210987654321234567890123"
        haz$(11) = " OVERALLS/SAFETY SHOES "
        haz$(12) = "    GLASSES/GOGGLES    "
        'haz$(13) = "       GOGGLES.        "
        'haz$(14) = "   FULL FACE SHIELD    "
        haz$(15) = "   IMPERVIOUS GLOVES   "
        'haz$(16) = "LONG IMPERVIOUS GLOVES."
        'haz$(17) = "     RUBBER APRON      "
        'haz$(18) = "     RUBBER BOOTS      "
        haz$(19) = "  DRAEGER RUBBER MASK  "
        haz$(20) = "  CARTRIDGE P1 - DUST  "
        haz$(21) = " CARTRIDGE A1 - VAPOUR "
        haz$(22) = " CARTRIDGE K2 - AMINES "
        haz$(23) = " OR A2 - DUST/VAPOUR   "
        'haz$(24) = "     FULL MOON SUIT    "
        END IF

    IF code$ <> "?" AND code$ <> "#" THEN
    y0% = 12: x0% = 55
    CALL box(x0%, y0%, 80, 21, 7, 0, 2)
    LOCATE y0%, 80: PRINT "¹";
    LOCATE 21, 80: PRINT "¹";

    COLOR 2, 0
    SELECT CASE code$
    CASE "W": sel$ = "11,12,@"
    CASE "Y": sel$ = "11,12,15,19,20,23,@"
    CASE "B": sel$ = "11,12,15,19,21,23,@"
    CASE "R": sel$ = "11,12,15,19,22,@"
    'CASE "A": sel$ = "11,@"
    'CASE "B": sel$ = "11,12,15,@"
    'CASE "C": sel$ = "11,13,15,@"
    'CASE "D": sel$ = "11,14,16,17,18,@"
    'CASE "E": sel$ = "11,12,15,19,@"
    'CASE "F": sel$ = "11,13,15,19,@"
    'CASE "G": sel$ = "11,12,15,20,@"
    'CASE "H": sel$ = "11,13,15,20,@"
    'CASE "I": sel$ = "11,14,16,21,@"
    'CASE "J": sel$ = "11,14,16,17,18,21,@"
    'CASE "K": sel$ = "22,@"
    'CASE "L": sel$ = "23,@"
    'CASE "M": sel$ = "24,@"
    CASE ELSE: sel$ = ",@"
    END SELECT

    n% = 0
    FOR i% = 1 TO 30
        x$ = "00" + MID$(STR$(i%), 2)
        x$ = RIGHT$(x$, 2) + ","
        IF INSTR(sel$, x$) > 0 THEN
            n% = n% + 1: IF n% > 10 THEN n% = 10
            LOCATE y0% + n%, x0% + 1:
            PRINT USING "\                     \"; haz$(i%)
            END IF
        NEXT
    END IF

    '>- Show all on '?'
    IF code$ = "?" THEN
        y0% = 2: x0% = 4
        CALL box(x0%, y0%, 39, 10, 7, 0, 2)
        n% = 0
        FOR i% = 11 TO 17
            x$ = "00" + MID$(STR$(i%), 2)
            x$ = RIGHT$(x$, 2) + ","
            IF haz$(i%) > "" THEN
                n% = n% + 1: IF n% > 20 THEN n% = 20
                LOCATE y0% + n%, x0% + 1
                PRINT USING "\\ \                     \"; x$; haz$(i%)
            END IF

            NEXT

        y0% = 2: x0% = 40
        CALL box(x0%, y0%, 78, 10, 7, 0, 2)
        n% = 0
        FOR i% = 19 TO 25
            x$ = "00" + MID$(STR$(i%), 2)
            x$ = RIGHT$(x$, 2) + ","
            IF haz$(i%) > "" THEN
                n% = n% + 1: IF n% > 20 THEN n% = 20
                LOCATE y0% + n%, x0% + 1
                PRINT USING "\\ \                     \"; x$; haz$(i%)
            END IF

            NEXT
    END IF

    '>- Show PROMPT ON  '#'
    IF code$ = "#" THEN

    LOCATE 22, 2: PRINT CHR$(FNE)
    LOCATE 23, 2: PRINT CHR$(FNE)

    FOR i% = ASC("A") TO ASC("Y")
        SELECT CASE CHR$(i%)
        CASE "W": sel$ = "11 12 @"
        CASE "Y": sel$ = "11 12 15 19 20 23 @"
        CASE "B": sel$ = "11 12 15 19 21 23 @"
        CASE "R": sel$ = "11 12 15 19 22 @"
        'CASE "A": sel$ = "11 @"
        'CASE "B": sel$ = "11 12 15 @"
        'CASE "C": sel$ = "11 13 15 @"
        'CASE "D": sel$ = "11 14 16 17 18,@"
        'CASE "E": sel$ = "11 12 15 19 @"
        'CASE "F": sel$ = "11 13 15 19 @"
        'CASE "G": sel$ = "11 12 15 20 @"
        'CASE "H": sel$ = "11 13 15 20 @"
        'CASE "I": sel$ = "11 14 16 21 @"
        'CASE "J": sel$ = "11 14 16 17 18 21 @"
        'CASE "K": sel$ = "22 @"
        'CASE "L": sel$ = "23 @"
        'CASE "M": sel$ = "24 @"
        CASE ELSE: sel$ = ",@"
        END SELECT

        IF CHR$(i%) = "A" THEN LOCATE 22, 2
        IF CHR$(i%) = "R" THEN LOCATE 23, 2
        COLOR 7, 0
        PRINT CHR$(i%); ".";
        COLOR 5, 0
        PRINT LEFT$(sel$, LEN(sel$) - 2); " ";


    NEXT


        END IF

'END SUB
