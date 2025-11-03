DECLARE SUB movedata ()
	'$INCLUDE: '\tpmanuf\src\pgmhead.INC'


	CALL setup("COPY ORDHED to new format")
	'$INCLUDE: '\tpmanuf\src\ordhed.inc'

'\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
'>>>>>>>>>>>>>>>>>>>  LEADS FILE
'//////////////////////////////////////////////////////////////////
TYPE RcdFmtold
	oall  AS STRING * 128
END TYPE
TYPE RcdFmtnew
	nall  AS STRING * 256
END TYPE

DIM SHARED ordhedo AS RcdFmtold
DIM SHARED ordhedn AS RcdFmtnew

	CLOSE
	OPEN "ordhed.old" FOR RANDOM AS #1 LEN = 128
	OPEN "ordhed.acf" FOR OUTPUT AS #2: CLOSE #2
	OPEN "ordhed.acf" FOR RANDOM AS #2 LEN = 256

	rec% = 1
	GET #1, rec%, ordhedo
	DO WHILE NOT EOF(1)
		ordhedn.nall = ordhedo.oall
		PUT #2, rec%, ordhedn

		LOCATE 10, 10: PRINT rec%; "  "


		GET #1, , ordhedo: rec% = rec% + 1
	LOOP
ENDPGM:
CLOSE

END
