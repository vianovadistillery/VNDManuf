	'////////////////////////////////////////////////////////////////////
	'>>>>>>>>>>>>>>>>>>>>>>> COLOUR CHART INDEX 3 <<<<<<<<<<<<<<<<<<<<<<<
	'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
	'>>>>>>>>>>>>                  KEY MAPS                 <<<<<<<<<<<<
	'>>>>> In all cases the supplier comes fisrt and the TNO$ is last <<<<<<
	'>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
	' The key lenght is the lenght of the record + 6

	'>>>> KEY MAP 3
	'          KFLD       SEARCH$    4A   1  Supplier search code
	'          KFLD       SNO$       2I   5  Supplier # (High byte, Low byte)
	'          KFLD       CCDESC$   22A   7  Colour card description
	'          KFLD       TCNO$      2I  29  Colour card # (High byte, Low byte)
	'          KFLD       TDESC$    30A  39  Tint desciption
	'          KFLD       TNO$       2I  41  Tint number (High byte, Low byte)

	OPEN "colchtx3.dat" FOR RANDOM SHARED AS #1 LEN = 78
