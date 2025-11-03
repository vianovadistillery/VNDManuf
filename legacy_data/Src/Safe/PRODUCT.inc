'/////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>>> PRODUCT LABELS
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

TYPE RcdFmtlbl
    Desc1 AS STRING * 40
    Desc2 AS STRING * 40
    Haz1 AS STRING * 1
    Haz2 AS STRING * 1
    Un AS STRING * 4
    Con1 AS STRING * 28
    Con2 AS STRING * 28
    Con3 AS STRING * 28
    Col AS STRING * 2
END TYPE
DIM SHARED lbl AS RcdFmtlbl

    OPEN "PRODUCT.DAT" FOR RANDOM AS #1 LEN = LEN(lbl)
