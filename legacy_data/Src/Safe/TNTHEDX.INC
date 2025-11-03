'/////////////////////////////////////////////////////////////////////////////
'>>>> Tint recipe headers index
'/////////////////////////////////////////////////////////////////////////////
parm3$ = ENVIRON$("PARM3$")

SELECT CASE parm3$
CASE "BASF":  OPEN ".\BASF\tnthedx.asf" FOR RANDOM SHARED AS #53 LEN = 5994
CASE "C   ":  OPEN ".\BASF\tnthedx.asf" FOR RANDOM SHARED AS #53 LEN = 5994
CASE "d   ":  OPEN ".\BASF\tnthedx.asf" FOR RANDOM SHARED AS #53 LEN = 5994
CASE "e   ":  OPEN ".\BASF\tnthedx.asf" FOR RANDOM SHARED AS #53 LEN = 5994
CASE "f   ":  OPEN ".\BASF\tnthedx.asf" FOR RANDOM SHARED AS #53 LEN = 5994
CASE "g   ":  OPEN ".\BASF\tnthedx.asf" FOR RANDOM SHARED AS #53 LEN = 5994
CASE "h   ":  OPEN ".\BASF\tnthedx.asf" FOR RANDOM SHARED AS #53 LEN = 5994
CASE "i   ":  OPEN ".\BASF\tnthedx.asf" FOR RANDOM SHARED AS #53 LEN = 5994
CASE "j   ":  OPEN ".\BASF\tnthedx.asf" FOR RANDOM SHARED AS #53 LEN = 5994
CASE "k   ":  OPEN ".\BASF\tnthedx.asf" FOR RANDOM SHARED AS #53 LEN = 5994
CASE "l   ":  OPEN ".\BASF\tnthedx.asf" FOR RANDOM SHARED AS #53 LEN = 5994
CASE "m   ":  OPEN ".\BASF\tnthedx.asf" FOR RANDOM SHARED AS #53 LEN = 5994
CASE "WAGON": OPEN ".\WAGON\tnthedx.asf" FOR RANDOM SHARED AS #53 LEN = 5994
CASE ELSE: OPEN "tnthedx.asf" FOR RANDOM SHARED AS #53 LEN = 5994
END SELECT



TYPE RcdFmttnthedx
	tnta(1 TO 999) AS STRING * 4
	rrn(1 TO 999) AS INTEGER
END TYPE

DIM SHARED tnthedx AS RcdFmttnthedx
