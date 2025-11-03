'/////////////////////////////////////////////////////////////////////////////
'>>>> A-F  recipe headers
'/////////////////////////////////////////////////////////////////////////////
parm3$ = ENVIRON$("PARM3$")
CONST setsD$ = "BRISTOL,HENKEL,HICHEM,JOTUN,REDIC,SICPA,WAGON,WATTYL"
CONST setsk$ = ",BRI,HEN,HIC,JOT,RED,SIC,WAG,WAT"

SELECT CASE parm3$
CASE "BRI": OPEN "BRIhed.asf" FOR RANDOM SHARED AS #64 LEN = 160
CASE "HEN": OPEN "HENhed.asf" FOR RANDOM SHARED AS #64 LEN = 160
CASE "HIC": OPEN "HIChed.asf" FOR RANDOM SHARED AS #64 LEN = 160
CASE "JOT": OPEN "JOThed.asf" FOR RANDOM SHARED AS #64 LEN = 160
CASE "RED": OPEN "REDhed.asf" FOR RANDOM SHARED AS #64 LEN = 160
CASE "SIC": OPEN "SIChed.asf" FOR RANDOM SHARED AS #64 LEN = 160
CASE "WAG": OPEN "WAGhed.asf" FOR RANDOM SHARED AS #64 LEN = 160
CASE "WAT": OPEN "WAThed.asf" FOR RANDOM SHARED AS #64 LEN = 160
CASE ELSE:  OPEN "forhed.asf" FOR RANDOM SHARED AS #64 LEN = 160
END SELECT

'DIM SHARED tnthed AS RcdFmttnthed
