'/////////////////////////////////////////////////////////////////////////////
'>>>> A-F  recipe headers index
'/////////////////////////////////////////////////////////////////////////////
parm3$ = ENVIRON$("PARM3$")

SELECT CASE parm3$
CASE "BRI": OPEN "BRIhedx.asf" FOR RANDOM SHARED AS #63 LEN = 5994
CASE "HEN": OPEN "HENhedx.asf" FOR RANDOM SHARED AS #63 LEN = 5994
CASE "HIC": OPEN "HIChedx.asf" FOR RANDOM SHARED AS #63 LEN = 5994
CASE "JOT": OPEN "JOThedx.asf" FOR RANDOM SHARED AS #63 LEN = 5994
CASE "RED": OPEN "REDhedx.asf" FOR RANDOM SHARED AS #63 LEN = 5994
CASE "SIC": OPEN "SIChedx.asf" FOR RANDOM SHARED AS #63 LEN = 5994
CASE "WAG": OPEN "WAGhedx.asf" FOR RANDOM SHARED AS #63 LEN = 5994
CASE "WAT": OPEN "WAThedx.asf" FOR RANDOM SHARED AS #63 LEN = 5994
CASE ELSE:  OPEN "forhedx.asf" FOR RANDOM SHARED AS #63 LEN = 5994
END SELECT

'DIM SHARED tnthedx AS RcdFmttnthedx
