'SUB accbrowse (rec%) STATIC
   CALL setup("  B R O W S E    F I L E")
   btype$ = "cost"
   cbtm$ = " No.Stock description.                  Size  Code Distr. Indus. Trade. Count."
   kbtm$ = " No.Stock description.                  Size  Distr. COGS    GPC   RMC    GPR "
   dbtm$ = " No.Stock description.                  Size  Code  A D Barcode       Search  "
   COLOR 6: LOCATE 3, 2: PRINT cbtm$
   COLOR 0, 3: LOCATE 25, 1: PRINT SPACE$(80);
   COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit   F3=Search     F5-Swap     F6-Search Duplicate Barcodes"; : LOCATE 25, 71: PRINT CHR$(24); CHR$(25); "-Move"; : COLOR 2, 0
   maxpag% = 20
   IF rec% < 1 OR rec% > maxacc% THEN rec% = 1
   updwn% = 13: bpos$ = STR$(rec%)
   xsearch$ = ""
   showdup% = 0
   skip$ = "Y"
   REDIM bar#(maxacc%)
   cleanbar% = 0

   '>>>>> Get next REC%ord to browse from.
accBROWSE.A:
  LOCATE 2, 25
  COLOR 7: PRINT "¹ ";
  COLOR 2: PRINT "Start browse from..>      ";
  COLOR 7: PRINT "Ì": COLOR 2
  COLOR 2
  IF skip$ = "Y" THEN
    skip$ = "N"
  ELSE
    bpos$ = ""
    LOCATE 2, 47: CALL inpnew(bpos$, 205!, updwn%, "13,59,61,63-64,68,72,73,80,81")
  END IF

  IF updwn% = 61 THEN
    LOCATE 2, 25: PRINT "Search..>";
    CALL inpnew(xsearch$, 120!, updwn%, "13,59,61,63-64,72,73,80,81")
    bpos$ = "1"
    updwn% = 13
  END IF


  IF updwn% = 13 THEN
      IF VAL(bpos$) = 0 AND LEN(bpos$) > 0 THEN
        keyl% = 20: qk$ = SPACE$(keyl%)
        sa$ = bpos$
        sa$ = UCASE$(sa$): LSET qk$ = sa$
        CALL index("CHAIN", ind%, qk$, 7, keyl%)
        IF ind% < 0 AND qk$ < sa$ THEN CALL index("READ ", ind%, qk$, 7, keyl%)
        bpos$ = MID$(STR$(ind%), 2)
      END IF

      IF VAL(bpos$) = 0 THEN bpos$ = STR$(E%)
      rec% = VAL(bpos$)
      IF rec% < 1 OR rec% > maxacc% THEN rec% = 1
  END IF
  IF updwn% = 59 THEN rec% = s%: GOTO X.accbrowse
  IF updwn% = 63 THEN '***** Swap browse type
    COLOR 6: LOCATE 3, 2
    SELECT CASE btype$
    CASE "cost": btype$ = "key ": PRINT kbtm$
    CASE "key ": btype$ = "data": PRINT dbtm$
    CASE "data": btype$ = "cost": PRINT cbtm$
    END SELECT
    COLOR 2, 0
    rec% = s%
  END IF
  IF updwn% = 64 THEN 'Search for duplicate barcodes
    IF showdup% THEN
      showdup% = 0
    CALL sndmsg("")
    ELSE
      showdup% = -1
    CALL sndmsg("Subset of duplicates")
    END IF

    rec% = 1
    GET #3, rec%, acstk
    DO WHILE rec% < maxacc%

      '>-Clean up malformed barcodes.
      IF acstk.ean13 <> 0 AND cleanbar% THEN
      IF acstk.ean13 < 9300000000000# OR acstk.ean13 > 9399999999999# OR rec% <> acstk.no THEN
        acstk.ean13 = 0
        PUT #3, rec%, acstk
      END IF
      END IF

      IF rec% = acstk.no THEN
        bar#(rec%) = acstk.ean13
      END IF
      GET #3, , acstk: rec% = rec% + 1
    LOOP

    '-> Cleaning the dups
    IF cleanbar% THEN
      rec% = 1
      GET #3, rec%, acstk
      DO WHILE rec% < maxacc%
        IF rec% = acstk.no THEN

          FOR i% = 1 TO maxacc%
            IF i% <> rec% AND bar#(i%) = acstk.ean13 AND acstk.ean13 > 0 THEN

              GET #3, i%, acstk
              acstk.ean13 = 0
              PUT #3, i%, acstk

              GET #3, rec%, acstk
              acstk.ean13 = 0
              PUT #3, rec%, acstk


            END IF
          NEXT

        END IF
        GET #3, , acstk: rec% = rec% + 1
      LOOP
    CALL sndmsg("Cleanup complete.")
      cleanbar% = 0
      rec% = 1
      GOTO accBROWSE.A
    END IF
    rec% = 1
  END IF

  IF updwn% = 68 THEN
  CALL sndmsg("Cleanup dup barcode enabled.")
    cleanbar% = -1
    rec% = 1
  END IF

  IF updwn% = 72 THEN 'UP arrow
    lin% = 1
    rec% = s%
    DO WHILE lin% > 0 AND rec% > 1
      rec% = rec% - 1
      GET #3, rec%, acstk
      IF acstk.no% = rec% THEN lin% = lin% - 1
      LOOP
  END IF
  IF updwn% = 80 THEN 'Down arrow
    rec% = s% + 1
    GET #3, rec%, acstk
    DO WHILE acstk.no <> rec% AND rec% < maxacc%
      rec% = rec% + 1
      GET #3, rec%, acstk
      LOOP

  END IF
  IF updwn% = 73 THEN 'pg up
    lin% = maxpag%
    rec% = s%
    DO WHILE lin% > 0 AND rec% > 1
      rec% = rec% - 1
      GET #3, rec%, acstk
      IF acstk.no% = rec% THEN lin% = lin% - 1
      LOOP
  END IF
  IF updwn% = 81 THEN 'pg dw
    rec% = E% + 1
  END IF


'///////////////////////////////////////////////////////////////////////////
'>>--- L I S T   A   P A G E
'///////////////////////////////////////////////////////////////////////////
  'Given rec% as the first record
  GET #3, rec%, acstk
  lin% = 0: missed% = 0
  DO UNTIL lin% = maxpag% OR rec% > maxacc%'OR missed% > 400

    'Selection
    ok% = -1
    IF acstk.no% <> rec% THEN ok% = 0
    IF btype$ = "key " AND UCASE$(acstk.active$) <> "A" THEN ok% = 0

    IF showdup% THEN
      ok% = 0
      IF acstk.ean13 > 0 THEN
        FOR i% = 1 TO maxacc%
          IF bar#(i%) = acstk.ean13 AND i% <> rec% AND acstk.ean13 > 0 THEN
            ok% = -1
            EXIT FOR
          END IF
        NEXT
      END IF
    END IF

    IF ok% AND xsearch$ > "" THEN
      ok0% = 0
      IF ok0% = 0 AND INSTR(LCASE$(acstk.desc1$), LCASE$(xsearch$)) > 0 THEN ok0% = -1
      IF ok0% = 0 AND INSTR(LCASE$(acstk.desc2$), LCASE$(xsearch$)) > 0 THEN ok0% = -1
      IF NOT ok0% THEN ok% = 0
    END IF


    IF ok% THEN prttype$ = btype$
    IF NOT ok% THEN prttype$ = "missed"
    bc$ = " ": IF acstk.ean13 > 9300 THEN bc$ = CHR$(127)


    SELECT CASE prttype$
    CASE "cost"
      LOCATE 4 + lin%, 2
      IF acstk.counter > 999 THEN                                                                '
        PRINT USING "####\                       \\        \!\ \\\ \  \####   ####   ####   ####   "; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; acstk.suplr$; acstk.distributor; acstk.industrial; acstk.trade; acstk.counter
      ELSE
        PRINT USING "####\                       \\        \!\ \\\ \  \ ###.## ###.## ###.## ###.##"; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; acstk.suplr$; acstk.distributor; acstk.industrial; acstk.trade; acstk.counter
      END IF
      COLOR 3, 0
      LOCATE 4 + lin%, 2 + 46
      PRINT USING "\  \"; acstk.suplr$
      LOCATE 4 + lin%, 2
      PRINT USING "####"; acstk.no%
      COLOR 2, 0
      COLOR 10, 0: LOCATE 4 + lin%, 41: PRINT bc$; : COLOR 2, 0'BC

      lin% = lin% + 1
      IF lin% = 1 THEN s% = rec%
      E% = rec%
    CASE "key "
      LOCATE 4 + lin%, 2
      IF acstk.distributor > 999 THEN
        kbtm$ = " No.Stock description.                  Size      Distr. COGS  GPC   RMC    GPR "
        PRINT USING "####\                       \\        \!\ \\\   #### #### ###.#% #### ###.#%"; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; acstk.distributor; acstk.cogs; acstk.gpc; acstk.rmc; acstk.gpr
      ELSE
        PRINT USING "####\                       \\        \!\ \\\ ###.## ###.## ###%  ###.## ###% "; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; acstk.distributor; acstk.cogs; acstk.gpc; acstk.rmc; acstk.gpr
      END IF
      COLOR 3, 0
      LOCATE 4 + lin%, 2
      PRINT USING "####"; acstk.no%
      COLOR 2, 0
      COLOR 10, 0: LOCATE 4 + lin%, 41: PRINT bc$; : COLOR 2, 0'BC

      lin% = lin% + 1
      IF lin% = 1 THEN s% = rec%
      E% = rec%
    CASE "data"
      LOCATE 4 + lin%, 2
      IF acstk.ean13 > 0 THEN
        PRINT USING "####\                       \\        \!\ \\\ \  \  ! ! ############# \      \"; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; acstk.suplr$; acstk.active$; acstk.dgflag$; acstk.ean13; acstk.search$
      ELSE
        PRINT USING "####\                       \\        \!\ \\\ \  \  ! !               \      \"; acstk.no%; acstk.desc1$; acstk.desc2$; bc$; acstk.size$; acstk.unit$; acstk.suplr$; acstk.active$; acstk.dgflag$; acstk.search$
      END IF
      COLOR 3, 0
      LOCATE 4 + lin%, 2 + 46
      PRINT USING "\  \"; acstk.suplr$
      LOCATE 4 + lin%, 2
      PRINT USING "####"; acstk.no%
      COLOR 2, 0
      COLOR 10, 0: LOCATE 4 + lin%, 41: PRINT bc$; : COLOR 2, 0'BC

      lin% = lin% + 1
      IF lin% = 1 THEN s% = rec%
      E% = rec%

    CASE "missed"
      missed% = missed% + 1
    END SELECT

  bad% = 0
  tmp$ = acstk.suplr4stdcost$ + acstk.search4stdcost
  FOR i% = 1 TO LEN(tmp$)
    IF MID$(tmp$, i%, 1) < " " THEN bad% = -1: EXIT FOR
    IF MID$(tmp$, i%, 1) > "~" THEN bad% = -1: EXIT FOR
  NEXT
  IF bad% THEN
    acstk.suplr4stdcost$ = SPACE$(5)
    acstk.search4stdcost$ = SPACE$(10)
    PUT #3, rec%, acstk
  END IF

  GET #3, , acstk: rec% = rec% + 1
  LOOP


  'IF missed% > 400 THEN
  '  LOCATE , 2: PRINT "More than 400 records searched without an active record being found."; CHR$(FNE)
  '  lin% = lin% + 1
  'END IF
  FOR i% = lin% + 1 TO maxpag%: LOCATE 3 + i%, 2: PRINT SPACE$(78): NEXT


  GOTO accBROWSE.A   '***** Get next REC%ord to browse from

X.accbrowse:
'END SUB

