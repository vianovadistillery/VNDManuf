
	'>>>>>>>>>>>>>>>>>>>> ACMGN01 - Accessory margin maintenance <<<<<<<<<<<<<
		OPEN "acmgn.acf"  FOR RANDOM SHARED AS #2  LEN=5

IF NOT typefields% THEN  FIELD #2,1  AS MCODE$,			4  AS MARGIN$

TYPE RcdFmtacmgn
	mcode AS STRING * 1 
	margin AS STRING * 4 
END TYPE 
DIM SHARED acmgn AS RcdFmtacmgn
