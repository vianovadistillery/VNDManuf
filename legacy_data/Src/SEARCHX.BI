'SUB SEARCHINDEX (keyin$, chi%, found%) STATIC
'>>>>> Lookup index file. Passed skey$. Returns SKEY, 0 if not found. <<<<<
'>>>>> SKEY1, one after insertion place                               <<<<<
    keyin$ = UCASE$(keyin$)
    found% = 0
    max% = LOF(chi%) / 7
    s% = 0: e% = max%

SEARCHAGAIN:
    p% = (e% - s%) / 2 + s%
    IF p% = 0 THEN GOTO X.SEARCHINDEX
    GET #chi%, p%, supx
    IF CVI(supx.wrrn$) = 0 THEN
      LSET supx.wcde$ = STRING$(99, CHR$(255))
    END IF
    IF supx.wcde$ = keyin$ THEN found% = -1: GOTO X.SEARCHINDEX
    IF supx.wcde$ < keyin$ AND s% <> p% THEN s% = p%: GOTO SEARCHAGAIN
    IF supx.wcde$ > keyin$ AND e% <> p% THEN e% = p%: GOTO SEARCHAGAIN

X.SEARCHINDEX:
'END SUB

