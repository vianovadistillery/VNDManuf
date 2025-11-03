	'>>>>>>>>>>>>>>>>>> RTCOL03  - Tint formula print <<<<<<<<<<<<<<<<<<<<<<
	'>>>>>>>>>>>>                    KEY MAPS                   <<<<<<<<<<<<
	'>>>>> In all cases the supplier comes fisrt and the TNO$ is last <<<<<<
	'////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>>>>>> COLOUR INDEX 4 <<<<<<<<<<<<<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
	' The key lenght is the lenght of the record + 6
	'//
	'>>>> KEY MAP 4
	'          KFLD       SEARCH$    4A   1  Supplier search code
	'          KFLD       SNO$       2I   5  Supplier # (High byte, Low byte)
	'          KFLD       CCDESC$   22A   7  Colour card description
	'          KFLD       TCNO$      2I  29  Colour card # (High byte, Low byte)
	'          KFLD       TSUPID$    8A  31  Supplier ID
	'          KFLD       TNO$       2I  39  Tint number (High byte, Low byte)

	OPEN "colchtx4.dat" FOR RANDOM SHARED AS #1 LEN = 78
