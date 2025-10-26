'/////////////////////////////////////////////////////////////////////////////
'>>>> Tint recipe headers
'/////////////////////////////////////////////////////////////////////////////
parm3$ = ENVIRON$("PARM3$")

SELECT CASE parm3$
CASE "BASF":  OPEN ".\BASF\tnthed.asf" FOR RANDOM SHARED AS #54 LEN = 160
CASE "C   ":  OPEN ".\BASF\tnthed.asf" FOR RANDOM SHARED AS #54 LEN = 160
CASE "d   ":  OPEN ".\BASF\tnthed.asf" FOR RANDOM SHARED AS #54 LEN = 160
CASE "e   ":  OPEN ".\BASF\tnthed.asf" FOR RANDOM SHARED AS #54 LEN = 160
CASE "f   ":  OPEN ".\BASF\tnthed.asf" FOR RANDOM SHARED AS #54 LEN = 160
CASE "g   ":  OPEN ".\BASF\tnthed.asf" FOR RANDOM SHARED AS #54 LEN = 160
CASE "h   ":  OPEN ".\BASF\tnthed.asf" FOR RANDOM SHARED AS #54 LEN = 160
CASE "i   ":  OPEN ".\BASF\tnthed.asf" FOR RANDOM SHARED AS #54 LEN = 160
CASE "j   ":  OPEN ".\BASF\tnthed.asf" FOR RANDOM SHARED AS #54 LEN = 160
CASE "k   ":  OPEN ".\BASF\tnthed.asf" FOR RANDOM SHARED AS #54 LEN = 160
CASE "l   ":  OPEN ".\BASF\tnthed.asf" FOR RANDOM SHARED AS #54 LEN = 160
CASE "m   ":  OPEN ".\BASF\tnthed.asf" FOR RANDOM SHARED AS #54 LEN = 160
CASE "WAGON": OPEN ".\WAGON\tnthed.asf" FOR RANDOM SHARED AS #54 LEN = 160
CASE ELSE: OPEN "tnthed.asf" FOR RANDOM SHARED AS #54 LEN = 160
END SELECT



TYPE RcdFmttnthed
	tnt AS INTEGER
	tnta AS STRING * 4
	revision AS INTEGER
	name AS STRING * 30
	desc AS STRING * 30
	cust AS STRING * 5
	SorW AS STRING * 1
	class AS INTEGER
	yield AS SINGLE
	ltr AS SINGLE
	kg AS SINGLE
	visc1h AS SINGLE
	visc1l AS SINGLE
	visc2h AS SINGLE
	visc2l AS SINGLE
	alccost AS SINGLE
	rawcost AS SINGLE
	filter AS INTEGER
	grind AS SINGLE
	ph AS SINGLE
	sg AS SINGLE
	Vsol AS SINGLE
	Wsol AS SINGLE
	pvc AS SINGLE
	pbr AS SINGLE
	gloss AS SINGLE
	Hazard AS STRING * 1
	date AS STRING * 8
	asRmat AS INTEGER
	CostPer AS STRING * 2
	filler AS STRING * 1
END TYPE

DIM SHARED tnthed AS RcdFmttnthed

