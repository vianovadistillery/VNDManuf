
    TYPE RcdFmtSearch
        key AS STRING * 5
        type  AS STRING * 2
        company AS STRING * 25
        compnum  AS STRING * 5
        name AS STRING * 20
        phone1 AS STRING * 7
        area1 AS STRING * 3
        phone2 AS STRING * 7
        area2 AS STRING * 3
        phone3 AS STRING * 7
        area3 AS STRING * 3
        crlf AS STRING * 1
        END TYPE
    DIM SHARED namesearch AS RcdFmtSearch

    OPEN "phonex.who" FOR RANDOM AS #52 LEN = LEN(namesearch)

