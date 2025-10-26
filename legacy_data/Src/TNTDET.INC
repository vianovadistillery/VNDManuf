'/////////////////////////////////////////////////////////////////////////////
'>>>> Tint recipe details
'/////////////////////////////////////////////////////////////////////////////
OPEN "tntdet.asf" FOR RANDOM SHARED AS #55 LEN = 32

TYPE RcdFmttntdet
	tnt AS LONG
	rmat AS INTEGER
	qty AS SINGLE
	cmt AS INTEGER
	cmtqty AS SINGLE
	ltkg AS STRING * 1
	tfiller AS STRING * 15
END TYPE
DIM SHARED tntdet AS RcdFmttntdet

