'/////////////////////////////////////////////////////////////////////////////
'>>>> Tint recipe details
'/////////////////////////////////////////////////////////////////////////////
'OPEN "tntdet.asf" FOR RANDOM SHARED AS #55 LEN = 32
'OPEN "tntdetx.asf" FOR RANDOM SHARED AS #56 LEN = 40
OPEN "fordet.asf" FOR RANDOM SHARED AS #65 LEN = 32
OPEN "fordetx.asf" FOR RANDOM SHARED AS #66 LEN = 32

TYPE RcdFmttntdet
	tnt AS INTEGER
	rmat AS INTEGER
	qty AS SINGLE
	cmt AS INTEGER
	cmtqty AS SINGLE
END TYPE



TYPE RcdFmttntdetx
	tnt AS LONG
	rmat AS INTEGER
	qty AS SINGLE
	cmt AS INTEGER
	cmtqty AS SINGLE
	ltkg AS STRING * 1
	tfiller AS STRING * 15
END TYPE

DIM SHARED tntdet AS RcdFmttntdet
DIM SHARED tntdetx AS RcdFmttntdetx
DIM SHARED fordet AS RcdFmttntdet
DIM SHARED fordetx AS RcdFmttntdetx
