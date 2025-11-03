'////////////////////////////////////////////////////////////////////
'>>>>>>>>>>>>>>>>>>>>>> RAW MATERIAL FILE <<<<<<<<<<<<<<<<<<<<<<<<<<<
'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

'//////// Old Record Format \\\\\\\\\\\\\\

	TYPE RcdFmtmsrmat
		no AS INTEGER
		Desc1 AS STRING * 25
		Desc2 AS STRING * 25
		purqty AS INTEGER  'New rmat# for the crossover
		Search AS STRING * 5
		Sg AS SINGLE
		PurCost AS SINGLE
		PurUnit AS STRING * 2
		UseCost AS SINGLE
		UseUnit AS STRING * 2
		DealCost AS SINGLE
		SupUnit AS STRING * 2
		Group AS INTEGER
		Active AS STRING * 1
		Volsolid AS SINGLE
		Solidsg AS SINGLE
		Wtsolid AS SINGLE
		Notes AS STRING * 25
		soh AS SINGLE
		Osoh AS SINGLE
		Date AS STRING * 8
		hazard AS STRING * 1
		cond AS STRING * 1
		altno(1 TO 5) AS INTEGER
		msdsflag AS STRING * 1
		searchs AS STRING * 8
		soo AS INTEGER
	END TYPE

'\\\\\\\ NEW RECORD FORMAT ////////////////////
	TYPE RcdFmtmsrmatx
		no AS INTEGER
		Desc1 AS STRING * 25
		Desc2 AS STRING * 25
		purqty AS INTEGER  'New rmat# for the crossover
		Search AS STRING * 5
		Sg AS SINGLE
		PurCost AS SINGLE
		PurUnit AS STRING * 2
		UseCost AS SINGLE
		UseUnit AS STRING * 2
		Dealcost AS SINGLE
		SupUnit AS STRING * 2
		Group AS INTEGER
		Active AS STRING * 1
		Volsolid AS SINGLE
		Solidsg AS SINGLE
		Wtsolid AS SINGLE
		Notes AS STRING * 25
		soh AS SINGLE
		Osoh AS SINGLE
		Date AS STRING * 8
		hazard AS STRING * 1
		cond AS STRING * 1
		altno(1 TO 5) AS INTEGER
		msdsflag AS STRING * 1
		searchs AS STRING * 8
		soo AS INTEGER
		sip AS SINGLE
		sohv AS SINGLE
		restock AS SINGLE
		used AS SINGLE
		ean13 AS CURRENCY
		filler as STRING * 72
	END TYPE



	DIM SHARED msrmat AS RcdFmtmsrmat
	DIM SHARED msrmatx AS RcdFmtmsrmatx


	OPEN "MSRMNEW.MSF" FOR RANDOM SHARED AS #38 LEN = LEN(msrmat)
	OPEN "MSRMNEW.MSX" FOR RANDOM SHARED AS #88 LEN = LEN(msrmatx)


