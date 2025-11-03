'////////////////////////////////////////////////////////////////////
'>>>>>> Quality System Extra file 1
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
OPEN "Qextra1.DAT" FOR RANDOM SHARED AS #76 LEN = 3008

TYPE RcdFmtExtra
    no AS INTEGER
    name AS STRING * 25
    opened AS STRING * 8
    closed AS STRING * 8
    duedate AS STRING * 8
    type AS STRING * 10
    report AS STRING * 10
    text(1 TO 36) AS STRING * 78
    filler AS STRING * 129
END TYPE
DIM SHARED Extra AS RcdFmtExtra
IF LEN(Extra) <> 3008 THEN STOP

DIM SHARED Qextra1 AS RcdFmtExtra
