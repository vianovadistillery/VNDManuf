'/////////////////////////////////////////////////////////////////////////////
'>>>> A-F  recipe details
'/////////////////////////////////////////////////////////////////////////////
parm3$ = ENVIRON$("PARM3$")

SELECT CASE parm3$
CASE "BRI": OPEN "BRIdet.asf" FOR RANDOM SHARED AS #65 LEN = 32
CASE "HEN": OPEN "HENdet.asf" FOR RANDOM SHARED AS #65 LEN = 32
CASE "HIC": OPEN "HICdet.asf" FOR RANDOM SHARED AS #65 LEN = 32
CASE "JOT": OPEN "JOTdet.asf" FOR RANDOM SHARED AS #65 LEN = 32
CASE "RED": OPEN "REDdet.asf" FOR RANDOM SHARED AS #65 LEN = 32
CASE "SIC": OPEN "SICdet.asf" FOR RANDOM SHARED AS #65 LEN = 32
CASE "WAG": OPEN "WAGdet.asf" FOR RANDOM SHARED AS #65 LEN = 32
CASE "WAT": OPEN "WATdet.asf" FOR RANDOM SHARED AS #65 LEN = 32
CASE ELSE:  OPEN "fordet.asf" FOR RANDOM SHARED AS #65 LEN = 32
END SELECT

'DIM SHARED tntdet AS RcdFmttntdet
