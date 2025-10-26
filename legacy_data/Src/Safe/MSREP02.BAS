'****************************************************************************
'>>>>>>>>>>>>>>>  M S R E P 0 2 - Raw material file listing.  <<<<<<<<<<<<<<<
'****************************************************************************
	DECLARE SUB searchindex (keyin$, chi%, found%)
	'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
	apgm$ = "MSMENU"
	''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	db.or.cr$ = "CR"
	typefields% = -1
	'$INCLUDE: '\tpmanuf\src\whof.INC'
	'$INCLUDE: '\tpmanuf\src\MSRMat.INC'
	'$INCLUDE: '\tpmanuf\src\MSMISC.INC'
	'$INCLUDE: '\tpmanuf\src\sup.INC'
	'$INCLUDE: '\tpmanuf\src\supx.INC'
	'$INCLUDE: '\tpmanuf\src\cusx.INC'
	stdout$ = "C:\TPEXE\MSREP03.PRN"
	
	GET #36, 1, msmisc
	maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
	IF SCREEN(1, 60) = 81 THEN maxrmat% = 100 ' "QBX" mode
	DIM k%(maxrmat%), r$(maxrmat%), h%(15)
	dito$ = " " + CHR$(34) + "    " + CHR$(34) + "   "
200 CALL setup("REPORT RAW MATERIAL FILE")
	COLOR 0, 3: LOCATE 25, 4: PRINT "F1-Exit"; : COLOR 2, 0
	LOCATE 6, 20: PRINT "1...Print full raw material list."
	LOCATE 7, 20: PRINT "2...Print raw materials by group."
	LOCATE 8, 20: PRINT "3...Print raw materials by supplier."
	LOCATE 9, 20: PRINT "4...Update activity flag."
	LOCATE 10, 20: PRINT "5...Print active materials only."
	LOCATE 11, 20: PRINT "6...Print suspended materials only."
	LOCATE 12, 20: PRINT "7...Print redundant materials only."
	LOCATE 13, 20: PRINT "8...Print miscellanious materials only."
	LOCATE 14, 20: PRINT "9...Create full raw material extract."
	LOCATE 15, 20: PRINT "10..Active raw materials by name."
	LOCATE 16, 20: PRINT "11..Suspended raw materials by name."

	IF sort% = 1 THEN COLOR 7: LOCATE 18, 28: PRINT "** FILE SORTED **": COLOR 2
	IF sort% = 2 THEN COLOR 7: LOCATE 18, 28: PRINT "** SORTED BY ALPHA **": COLOR 2
270 LOCATE 19, 28: PRINT "Option..> "; CHR$(FNH);
	CALL inpnew(a$, 2!, updwn%, "13,59" + ALT$): GOSUB ALT
	IF updwn% = 59 THEN CLOSE : CALL EXITPGM(apgm$): CHAIN apgm$
	b$ = "  ": LSET b$ = a$: opt% = VAL(b$): sel% = 0
	IF opt% = 1 THEN sel% = 1
	IF opt% = 2 THEN GOSUB 1210: sel% = 1'* Get group%
	IF opt% = 3 THEN GOSUB 1430: sel% = 1'* Get supplier%
	IF opt% = 4 THEN CLOSE : bpgm$ = "msupd09": CALL EXITPGM(bpgm$): CHAIN bpgm$
	IF opt% = 5 THEN sel% = 1
	IF opt% = 6 THEN sel% = 1
	IF opt% = 7 THEN sel% = 1
	IF opt% = 8 THEN sel% = 1
	IF opt% = 9 THEN sel% = 1
	IF opt% = 10 THEN sel% = 1
	IF opt% = 11 THEN sel% = 1
	IF sel% = 0 THEN 200
'*****************************************************************************
	s$ = SPACE$(15): page = 0: lin = 0
	IF opt% = 1 THEN GOSUB load.and.sort'* Sort all
	IF opt% = 2 THEN GOSUB 1280'* Select one group
	IF opt% = 3 THEN GOSUB 1500'* Select one supplier
	IF opt% = 5 THEN GOSUB load.and.sort'* Sort all
	IF opt% = 6 THEN GOSUB load.and.sort'* Sort all
	IF opt% = 7 THEN GOSUB load.and.sort'* Sort all
	IF opt% = 8 THEN GOSUB load.and.sort'* Sort all
	IF opt% = 9 THEN GOSUB load.and.sort'* Sort all
	IF opt% = 10 THEN GOSUB load.and.sort'* Sort all
	IF opt% = 11 THEN GOSUB load.and.sort'* Sort all

	IF n = 0 THEN COLOR 10: LOCATE 22, 1: PRINT "No r/m found for this group.": COLOR 2: GOTO 270
	IF stdout$ = "CON" THEN CLS

DOLIST:
	OPEN stdout$ FOR OUTPUT AS #99
	WIDTH #99, 128
	GOSUB heading
	
	FOR i% = 1 TO n
	IF stdout$ <> "CON" THEN
		LOCATE 20, 25: PRINT "Printing record "; i%; " out of "; n; CHR$(FNE)
		END IF
	GET #38, k%(i%), msrmat
	IF msrmat.desc1$ = s$ THEN 660
460
	Sg = msrmat.Sg
	PurCost = msrmat.PurCost
	UseCost = msrmat.UseCost
	accnum% = msrmat.Group
'>>>>>>>>>>>>>>>>>>  L 1   B R E A K   P R O C E S S I N G  <<<<<<<<<<<<<<<<<
	IF sav.msrmat.search$ <> msrmat.search$ THEN
		sav.msrmat.search$ = msrmat.search$
		keyin$ = msrmat.search$: chi% = 45
		CALL searchindex(keyin$, chi%, found%)
		supno% = CVI(supx.wrrn$)
		IF supno% < 1 OR supno% > maxsup% THEN supno% = 1
		GET #44, supno%, sup
		IF opt% <> 10 AND opt% <> 11 THEN fetch% = -1
	END IF
'>>>>>>>>>>>>>>>>>>>>>>>>  End level break processing  <<<<<<<<<<<<<<<<<<<<<<
	prtflg% = 0
	IF opt% < 5 THEN prtflg% = 1
	IF opt% = 5 AND msrmat.Active$ = "A" THEN prtflg% = 1
	IF opt% = 6 AND msrmat.Active$ = "S" THEN prtflg% = 1
	IF opt% = 7 AND msrmat.Active$ = "R" THEN prtflg% = 1
	IF opt% = 8 AND msrmat.Active$ = "M" THEN prtflg% = 1
	IF opt% = 10 AND msrmat.Active$ = "A" THEN prtflg% = 1
	IF opt% = 11 AND msrmat.Active$ = "S" THEN prtflg% = 1

	IF opt% = 9 THEN
		IF NOT open98% THEN
			OPEN "Rawmat.PSI" FOR OUTPUT AS #98
			WRITE #98, "No:", "Desc.  :", "Account:", "Active?:", "SG     :", "Purcase:", "Use Cost", "Notes  :"
			open98% = -1
		END IF
		WRITE #98, k%(i%), msrmat.desc1$, accnum%, msrmat.Active$, Sg, STR$(PurCost) + msrmat.PurUnit$, STR$(UseCost) + msrmat.UseUnit$, msrmat.Notes$
	END IF

	IF prtflg% = 1 THEN

		IF fetch% THEN
			PRINT #99, STRING$(79, "-")
			PRINT #99, USING "!& & &!"; CHR$(15); sup.sname$; sup.scont$; sup.sphone$; CHR$(18)'dmr
			lin = lin + 2
			fetch% = 0
		END IF

		IF Sg <> 0 THEN PRINT #99, USING "#### \                       \ ###! #.### ####.##\\###.##\\  ! \              \"; k%(i%); msrmat.desc1$; accnum%; msrmat.Active$; Sg; PurCost; msrmat.PurUnit$; UseCost; msrmat.UseUnit$; msrmat.hazard$; msrmat. _
Notes$
		IF Sg = 0 THEN PRINT #99, USING "#### \                       \ ###!  N/A  ####.##\\###.##\\  ! \              \"; k%(i%); msrmat.desc1$; accnum%; msrmat.Active$; PurCost; msrmat.PurUnit$; UseCost; msrmat.UseUnit$; msrmat.hazard$; msrmat.Notes$
		lin = lin + 1
		IF lin > 50 THEN PRINT #99, CHR$(12); : GOSUB heading
	END IF

	
660 NEXT
	PRINT #99, CHR$(12);
	CLOSE #99
	shella$ = "Copy " + stdout$ + " LPT1"
	SHELL shella$


	GOTO 200
'*****************************************************************************
heading:
	PRINT #99, ; TAB(1); CHR$(14); msmisc.cc$
	PRINT #99, "#msrep02"; TAB(70); DATE1$
	PRINT #99, : PRINT #99, TAB(20); "R A W    M A T E R I A L   F I L E   L I S T "
	page = page + 1
	IF opt% = 5 THEN PRINT #99, "(Active only)";
	IF opt% = 6 THEN PRINT #99, "(Suspended only)";
	IF opt% = 7 THEN PRINT #99, "(Redundant only)";
	IF opt% = 8 THEN PRINT #99, "(Miscellanious only)";
	IF opt% = 10 THEN PRINT #99, "(Active only)";
	IF opt% = 11 THEN PRINT #99, "(Suspended only)";
	PRINT #99, TAB(70); "Page: "; page
	PRINT #99, STRING$(79, "=")
	PRINT #99, "No. DESCRIPTION                Gr.A S/G.. Pur/Cost. U/Cost. Haz Notes........."
	lin = 0: supa% = 32767
	IF opt% <> 10 AND opt% <> 11 THEN fetch% = -1
	RETURN
'///////////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>  S H E L L    S O R T    R O U T I N E   <<<<<<<<<<<<<<<<
'///////////////////////////////////////////////////////////////////////////
load.and.sort:
	'********** r$=record key:  k%=final sorted list
	IF sort% = 1 THEN GOTO xsort
	PRINT : LOCATE 18, 25: PRINT "Loading records for sort....": LOCATE 1, 1
	'>>-------- load sort
	n = 0
	FOR i% = 1 TO maxrmat%
	GET #38, i%, msrmat
	IF msrmat.no% = i% THEN
		b$ = STR$(i%): MID$(b$, 1, 1) = "0"
		b$ = "00000" + b$: b$ = RIGHT$(b$, 5)
		n = n + 1
		r$(n) = msrmat.search$ + b$
		IF opt% = 10 THEN r$(n) = msrmat.desc1$
		IF opt% = 11 THEN r$(n) = msrmat.desc1$
		k%(n) = i%
		END IF
	NEXT
	LOCATE 18, 25: PRINT USING "##,### records loaded for printing."; n
	ii% = 0
	h%(1) = 1
	FOR i% = 2 TO 15
	h%(i%) = 3 * h%(i% - 1) + 1: IF h%(i%) >= n THEN 1050
	NEXT i%
1050 T% = i% - 2: IF T% < 1 THEN T% = 1
	FOR s% = T% TO 1 STEP -1
	h% = h%(s%)
	FOR j% = h% + 1 TO n
	r$ = r$(j%): k% = k%(j%)
	FOR i% = j% - h% TO 1 STEP -h%
		 IF r$ >= r$(i%) THEN ii% = i%: i% = 0: GOTO 1130
		 k%(i% + h%) = k%(i%): r$(i% + h%) = r$(i%)
1130 NEXT'********** i
	IF ii% > 0 THEN i% = ii%: ii% = 0
	k%(i% + h%) = k%: r$(i% + h%) = r$
	 NEXT'********** j
	 NEXT'********** S
xsort:
	sort% = 1
	IF opt% = 10 THEN sort% = 2
	IF opt% = 10 THEN sort% = 2
	RETURN

'///////////////////////////////////////////////////////////////////////////
1210 '************************ Get group%
1220 LOCATE 15, 20: INPUT "Enter group number..>", a$
	b$ = "   ": LSET b$ = a$: b% = VAL(a$)
	IF b% < 1 OR b% > 999 THEN COLOR 14: LOCATE 22, 1: PRINT "Group number invalid.": COLOR 2: GOTO 1220
	Group% = b%
	LOCATE 22, 1: PRINT CHR$(FNE)
	RETURN
1280 '************************ Select group numbers from group%
	 i% = 1: n = 0
	 GET #38, i%, msrmat
	 IF msrmat.desc1$ = SPACE$(15) THEN 1360
	 accnum% = msrmat.Group
	 IF accnum% = Group% THEN n = n + 1: k%(n) = i%: LOCATE 17, 20: PRINT n; " Raw materials found."; CHR$(FNE)
	 '************************
1360 FOR i% = 2 TO maxrmat%
	GET #38, i%, msrmat
	IF msrmat.desc1$ = SPACE$(15) THEN 1410
	 accnum% = msrmat.Group
	 IF accnum% = Group% THEN n = n + 1: k%(n) = i%: LOCATE 17, 20: PRINT n; " Raw materials found."; CHR$(FNE)
1410    NEXT
	 RETURN
1430 '************************ Get supplier%
	DO
		LOCATE 15, 20: PRINT "Enter supplier code..>"; keyin$
								LOCATE 15, 42: CALL inpnew(keyin$, 105!, updwn%, "13,59-60")
		IF updwn% = 59 THEN EXIT DO
		IF updwn% = 60 THEN EXIT DO
			chi% = 45
			CALL searchindex(keyin$, chi%, found%)
			supno% = CVI(supx.wrrn$)
		IF NOT found% THEN CALL sndmsg("Supplier not found"): keyin$ = supx.wcde$
	LOOP UNTIL found%
		IF found% THEN
			i% = CVI(supx.wrrn$)
			GET #44, i%, sup
			supa$ = sup.search$ + sup.stype$
		END IF
	CALL sndmsg("")
RETURN
1500 '*********************** Select supplier from supplier%
	n = 0
	FOR i% = 2 TO maxrmat%
		GET #38, i%, msrmat
		accnum% = msrmat.Group
		IF msrmat.search$ = supa$ THEN n = n + 1: k%(n) = i%: LOCATE 17, 20: PRINT n; " Raw materials found."
		NEXT
RETURN

SUB searchindex (keyin$, chi%, found%) STATIC
	'$INCLUDE: '\tpmanuf\src\searchx.bi'
END SUB

