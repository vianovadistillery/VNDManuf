	'////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>>> COLOUR CHART INDEX 2 <<<<<<<<<<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
	'>>>>>>>>>>>>                    KEY MAPS                   <<<<<<<<<
	'>>>>> In all cases the supplier comes fisrt and the TNO$ is last <<<
	'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	' The key lenght is the lenght of the record + 6
	'>>>> KEY MAP 2
	'          KFLD       SEARCH$    4A   1  Supplier search code
	'          KFLD       SNO$       2I   5  Supplier # (High byte, Low byte)
	'          KFLD       TSUPID$    8A   7  Supplier ID
	'          KFLD       TNO$       2I   9  Tint number (High byte, Low byte)

	OPEN "colchtx2.dat" FOR RANDOM SHARED AS #1 LEN = 78
