'SUB load.unpaid (cust$, startrec%, docnum$, VALUE!, updwn%) STATIC
'////////////////////////////////////////////////////////////
'///// Look for all unpaid invoices
'////////////////////////////////////////////////////////////
'.dc - Complete
    CALL setup("UNPAID INVOICES")
    LOCATE 25, 1: COLOR 0, 3: PRINT "F1- Exit          F6-Summary           F10-update";
    COLOR 6, 0: LOCATE 4, 2
    PRINT " No.    Date  Type Supplier/Customer...          Code. .. Document      Value."
    COLOR 2, 0
    cust$ = UCASE$(cust$)
    show.all% = 0

    LOCATE 3, 2
    PRINT USING "Payment number of \           \  Payment $$##,###.## "; docnum$; value!
    IF docnum$ = "" THEN
        LOCATE 3, 22: CALL inpnew(docnum$, 112!, updwn%, "13,59-60,64")
        IF updwn% = 59 THEN GOTO load.unpaid99
        IF updwn% = 60 THEN GOTO load.unpaid99
        IF updwn% = 64 THEN show.all% = -1
        LOCATE 3, 2
        PRINT USING "Payment number of \           \  Payment $$##,###.## "; docnum$; value!
        END IF

    IF value! = 0 THEN
        value$ = ""
        LOCATE 3, 45: CALL inpnew(value$, 11.2!, updwn%, "13,59-60")
        IF updwn% = 59 THEN GOTO load.unpaid99
        IF updwn% = 60 THEN GOTO load.unpaid99
        value! = VAL(value$)
        LOCATE 3, 2
        PRINT USING "Payment number of \           \  Payment $$##,###.## "; docnum$; value!
        END IF

    maxlin% = 18: maxload% = 50
    IF NOT been.here.before% THEN
        DIM lin%(maxlin%), linval!(maxlin%), sel%(maxload%), sel$(maxload%), selval!(maxload%), sel%
        been.here.before% = -1
        END IF

    IF cust$ <> oldcust$ THEN
        FOR sel% = 1 TO maxlin%: lin%(sel%) = 0: linval!(sel%) = 0: NEXT
        FOR sel% = 1 TO maxload%: sel%(sel%) = 0: sel$(sel%) = "": selval!(sel%) = 0: NEXT
        oldcust$ = cust$
        END IF

    IF startrec% < 1 THEN startrec% = 1
    rec% = startrec%

Load.unpaid0:
    IF EOF(8) THEN rec% = startrec%
    lin% = 0
    LOCATE 5, 2

    GET #8, rec%, Audit
    DO WHILE NOT EOF(8)
        IF Audit.adcust$ = cust$ THEN

        IF Audit.addocnum$ = docnum$ THEN
            sel%(1) = rec%
            sel$(1) = "P"
            END IF

        IF Audit.adpaid$ <> "P" OR show.all% THEN
        IF Audit.ADTYPE$ = "DI" OR Audit.ADTYPE$ = "DC" THEN
            LOCATE lin% + 5, 2
            PRINT USING "##### & \\ &-&    & $$##,###.##"; Audit.adrec%; FNDYY$(Audit.addate$); Audit.ADTYPE$; Audit.adsname$; Audit.adcust$; Audit.addocnum$; Audit.advalue
            lin% = lin% + 1
            lin%(lin%) = Audit.adrec%
            linval!(lin%) = Audit.advalue

            found% = 0
            FOR sel% = 1 TO maxload%
                IF sel%(sel%) = lin%(lin%) AND sel%(sel%) <> 0 THEN found% = -1: EXIT FOR
                NEXT
            IF found% THEN
                LOCATE lin% + 4, 58
                PRINT USING "!"; sel$(sel%)
                END IF

            END IF
            END IF
            END IF
        IF lin% = maxlin% THEN EXIT DO
        GET #8, , Audit: rec% = rec% + 1
        LOOP
    IF lin% = 0 THEN
            LOCATE , 2
            PRINT USING "No unpaid invoices found for \    \"; cust$
            lin% = lin% + 1
            END IF

    n.lin% = lin%

Load.unpaid.select:
    '------------------------
    '>>> Select routine <<<<<
    '------------------------
    lin% = 1
    DO WHILE lin% <= n.lin%
        total! = 0
        FOR i% = 1 TO maxload%: total! = total! + selval!(i%): NEXT
        LOCATE 3, 60: PRINT USING "Total  $$,###,###.##"; total!


        IF lin% < 1 THEN lin% = 1
        LOCATE lin% + 4, 58
        a$ = " "
        FOR sel% = 1 TO maxload%
            IF sel%(sel%) = lin%(lin%) AND sel%(sel%) <> 0 THEN a$ = sel$(sel%): EXIT FOR
            NEXT
        CALL inpnew(a$, 101!, updwn%, "13,59,64,68,72-73,80-81")
        a$ = UCASE$(a$)

        found% = 0
        FOR sel% = 1 TO maxload%
            IF sel%(sel%) = lin%(lin%) AND sel%(sel%) <> 0 THEN found% = -1: EXIT FOR
            NEXT
        IF NOT found% THEN
            FOR sel% = 1 TO maxload%
            IF sel%(sel%) = 0 THEN found% = -1: EXIT FOR:
            NEXT
            END IF

        IF NOT found% THEN
        BEEP
        ELSE
        SELECT CASE a$
        CASE "P", "I": sel$(sel%) = a$: sel%(sel%) = lin%(lin%): selval!(sel%) = linval!(lin%)
        CASE ELSE: sel%(sel%) = 0: sel$(sel%) = "": selval!(sel%) = 0
        END SELECT
        END IF


        IF updwn% = 59 THEN GOTO load.unpaid99
        IF updwn% = 68 THEN GOTO load.unpaid99

        IF updwn% = 64 THEN GOSUB load.unpaid.summary
        IF updwn% = 72 THEN lin% = lin% - 1'up
        IF updwn% = 80 THEN lin% = lin% + 1'down
        IF updwn% = 73 THEN lin% = lin% + 99'page up
        IF updwn% = 81 THEN lin% = lin% + 99'page down
        LOOP

        IF updwn% = 13 AND n.lin% = maxlin% THEN updwn% = 81
        IF updwn% = 73 THEN rec% = 1: GOTO Load.unpaid0
        IF updwn% = 81 THEN GOTO Load.unpaid0
        GOTO Load.unpaid.select

load.unpaid99:
'////////////////////////////////////////////////////////////
'///// Update all selected invoices
'////////////////////////////////////////////////////////////
    IF updwn% = 68 AND show.all% = 0 THEN
        FOR sel% = 1 TO maxload%
            IF sel%(sel%) <> 0 THEN
                rec% = sel%(sel%)
                GET #8, rec%, Audit
                LSET Audit.adpaid$ = "P"
                LSET Audit.adtext$ = docnum$
                PUT #8, rec%, Audit
                updwn% = -1
                END IF
            NEXT
    oldcust$ = ""
    END IF

GOTO load.unpaid.summary99
'////////////////////////////////////////////////////////////////////////////////
'>>>>
'////////////////////////////////////////////////////////////////////////////////
load.unpaid.summary:
PCOPY 0, 1
    CALL BOX(1, 5, 80, 22, 7, 8, 1)
    offset% = 0

load.unpaid.summary0:
    IF offset% > (maxload% - maxlin%) THEN offset% = (maxload% - maxlin%)
    LOCATE 5, 2: COLOR 2, 0
    lin% = 0
    FOR sel% = 1 TO maxload%
        lin% = lin% + 1
        sum.rec% = sel%(sel% + offset%)
        IF sum.rec% > 0 THEN
            GET #8, sum.rec%, Audit
            LOCATE lin% + 5, 2
            PRINT USING "##### & \\ &-&  P & $$##,###.##"; Audit.adrec%; FNDYY$(Audit.addate$); Audit.ADTYPE$; Audit.adsname$; Audit.adcust$; Audit.addocnum$; Audit.advalue
            END IF
            NEXT
        FOR lin% = lin% TO maxlin%
            LOCATE , 2
            PRINT USING "&"; SPACE$(78)
            NEXT

    LOCATE 22, 2: a$ = " "
    CALL inpnew(a$, 101!, updwn%, "13,59,81,73")
    IF updwn% = 73 THEN offset% = 0
    IF updwn% = 81 THEN offset% = offset% + maxlin%
    IF updwn% <> 59 THEN GOTO load.unpaid.summary0


PCOPY 1, 0
RETURN

load.unpaid.summary99:
