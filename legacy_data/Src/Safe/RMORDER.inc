'///////////////////////////////////////////////////////////////////
'/////  A S S E T    R E G I S T E R
'///////////////////////////////////////////////////////////////////////
Notes:
     OPEN "RMORDER.dat" FOR RANDOM SHARED AS #81 LEN = 80

TYPE RcdFmtRMORDER
    text AS STRING * 78
    cr AS STRING * 1
    lf AS STRING * 1
END TYPE
DIM SHARED Notes AS RcdFmtRMORDER



