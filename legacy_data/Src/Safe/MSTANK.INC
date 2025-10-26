'SUB height.in.tank (updwn%, seq%, Ltrs.in!, Height.from.btm!, Height.from.top!) STATIC

'//////////////////////////////////////////////////
'/////   HEIGHT IN TANK
'//////////////////////////////////////////////////
height.in.tank.0:
	 in$ = ""
	 d = 0
	 FOR i% = seq% TO 1 STEP -1
		IF rm.tanksize!(i%) > 0 THEN
			c = rm.tanksize!(i%)
			d = rm.tankltmm!(i%)
			EXIT FOR
		END IF
	 NEXT

	 IF c = 0 THEN updwn% = 0: GOTO x.height.in.tank:

	 '>-c=Total size, d= LT/MM
	 
	 IF c = 85 THEN d = .1157        '1118
	 IF c = 219 THEN d = .2489    '2489
	 IF c = 309 THEN d = .2896    '2893
	 IF c = 486 THEN d = .452     '4555
	 'IF c = 700 THEN d = .6553    'new
	 IF c = 700 THEN d = .6491    '6553
	 IF c = 1071 THEN d = .8925   '8925
	 IF c = 1089 THEN d = .8926   '8926
	 IF c = 1100 THEN d = .8912   'new
	 IF c = 1400 THEN d = 1.1255  'new
	 IF c = 1422 THEN d = 1.1655  '1.1655
	 IF c = 1430 THEN d = 1.1456  'NEW
	 IF c = 1460 THEN d = 1.167   'NEW
	 IF c = 1695 THEN d = 1.169   '1.169
	 IF c = 1700 THEN d = 1.177   'NEW

	 IF c = 1300 THEN d = 1.0513
	 IF c = 800 THEN d = .55


	 IF d = 0 THEN
		CALL sndmsg("Now tank height information for " + STR$(c))
		GOTO x.height.in.tank
	 END IF

	'>>> Find litres
	 Height.from.top! = (c - Ltrs!) / d
	 Height.from.btm! = Ltrs! / d
	 Height.from.top! = (c - Ltrs.in!) / d
	 Height.from.btm! = Ltrs.in! / d

	 CALL ROUND(Height.from.top!, .5)
	 CALL ROUND(Height.from.btm!, .5)


x.height.in.tank:

'END SUB

