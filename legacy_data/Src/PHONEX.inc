    TYPE RcdFmtSearch
        key AS STRING * 5
        type  AS STRING * 2
        company AS STRING * 30
        compnum  AS STRING * 5
        name AS STRING * 20
        sPhone AS STRING * 20
        sPhone1 AS STRING * 20
        pstncc AS STRING * 3
        email AS STRING * 40
        www AS STRING * 40
        'Personal details
        ContactFirstName(6) AS STRING * 16
        ContactSurName(6) AS STRING * 20
        ContactTitle(6) AS STRING * 20
        ContactPhone(6) AS STRING * 18 '+61 xxx3 9xxx xxxx
        contactmobile(6) AS STRING * 18'+61 x419 x338 x450
        ContactFax(6) AS STRING * 18   '+61 x419 x338 x450
        Contactemail(6) AS STRING * 40
        crlf AS STRING * 1

        END TYPE
    DIM SHARED phonex AS RcdFmtSearch

    OPEN "phonex.who" FOR RANDOM SHARED AS #52 LEN = LEN(phonex)

