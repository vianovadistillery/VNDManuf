'SUB qsort (in$(), in%(), n%) STATIC
'>>>>> Quick-sort algorithmn
    DIM h%(15)
    ii% = 0
    h%(1) = 1
    FOR i% = 2 TO 15
    h%(i%) = 3 * h%(i% - 1) + 1: IF h%(i%) >= n% THEN GOTO QSORT750
    NEXT i%
    n% = -1
    GOTO x.qsort
QSORT750:
    t% = i% - 2: IF t% < 1 THEN t% = 1
    FOR s% = t% TO 1 STEP -1
    h% = h%(s%)
    FOR j% = h% + 1 TO n%
       r$ = in$(j%): k% = in%(j%)
       FOR i% = j% - h% TO 1 STEP -h%
       IF r$ >= in$(i%) THEN ii% = i%: i% = 0: GOTO QSORT830
       in%(i% + h%) = in%(i%): in$(i% + h%) = in$(i%)
QSORT830:
       NEXT'* I
       IF ii% > 0 THEN i% = ii%: ii% = 0
       in%(i% + h%) = k%: in$(i% + h%) = r$
     NEXT'* J
        '>> - Wheel on screen
        chr% = s% MOD 4: chrlist$ = "|/-\"
        char$ = MID$(chrlist$, chr% + 1, 1)
        COLOR 7, 0: LOCATE 24, 78: PRINT char$; : COLOR 2, 0

     NEXT'* S
x.qsort:
        COLOR 7, 0: LOCATE 24, 78: PRINT "Í"; : COLOR 2, 0
'END SUB

