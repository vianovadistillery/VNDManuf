'.dc - Complete
	'************************************************************************
	'****     V A R I A B L E     K E Y     L E N G H T    I N D E X     ****
	'************************************************************************
	'CALLED  BY "$INCLUDE: '\tpmanuf\src\index.INC'"
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ                   I N D E X    R O U T I N E                          บ
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
	'               Q$ = OPTION
	'               QF%= ERROR INDICATOR
	'               QK$= KEY OF FILE
	'               CH%= CHANNEL OF FILE
	'             KEYL%= KEY LENGTH
	'
	SUB INDEX(Q$,QF%,QK$,CH%,KEYL%) STATIC
	IF Q$<>"OPEN " THEN
IF NOT typefields% THEN 		FIELD #CH%,2 AS QR$,2 AS QD$,2 AS QM$

TYPE RcdFmtPRE
	qr AS STRING * 2
	qd AS STRING * 2
	qm AS STRING * 2
END TYPE 
DIM SHARED PRE AS RcdFmtPRE
IF NOT typefields% THEN 		FIELD #CH%,2 AS LNUM$,2 AS RNUM$,2 AS QBAL$,1 AS QDEL$,KEYL% AS QKEY$

TYPE RcdFmtPRE2
	lnum AS STRING * 2
	rnum AS STRING * 2
	qbal AS STRING * 2
	qdel AS STRING * 1
	qkey AS STRING * 00
END TYPE 
DIM SHARED PRE2 AS RcdFmtPRE2
		END IF
	DIM Q%(500)

	' DEBUG OPTIONS IF =1
	' DEBUG OPTIONS AND STOP FOR INPUT IF =2
	DEBUG%=0
	QF%=0
	OLDK$=QKEY$:OLDK1$=QKEY$:OLDK2$=QKEY$
	OLDL$=LNUM$:OLDL1$=LNUM$:OLDL2$=LNUM$
	OLDR$=RNUM$:OLDR1$=RNUM$:OLDR2$=RNUM$

	SELECT CASE Q$
	CASE "OPEN ":GOSUB IOPEN
	CASE "CHAIN":GOSUB ICHAIN
	CASE "WRITE":GOSUB IWRITE
	CASE "DUMP ":GOSUB IDUMP
	CASE "FIRST":GOSUB IFIRST
	CASE "READ ":GOSUB IREAD
	CASE "READP":GOSUB IREADP
	CASE "DELET":GOSUB IDELET
	CASE ELSE   :LSET Q$="ERROR"
	END SELECT

	LSET QK$=QKEY$
	'>> If no error reutrn record number in indicator
	IF Q$="READ " OR Q$="READP" OR Q$="CHAIN" OR Q$="FIRST" THEN
	IF KEYL%>1  THEN
		A$=RIGHT$(QK$,2):SFX$="  "
		MID$(SFX$,1,1)=MID$(A$,2,1):MID$(SFX$,2,1)=MID$(A$,1,1)
		IF QF%=-1 THEN QF%=0-CVI(SFX$) ELSE QF%=CVI(SFX$)
		END IF
		END IF

	IF DEBUG%>0 THEN LOCATE 25,40:PRINT Q$;
	IF DEBUG%=2 THEN X$=INPUT$(1)
	EXIT SUB
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ        O P E N   A    F I L E                                         บ
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
IOPEN:
	IF DEBUG%>0 THEN LOCATE 25,1:PRINT "ฎ--O P E N  --ฏ";
	IF DEBUG%=2 THEN X$=INPUT$(1)
	OPEN QK$ FOR RANDOM SHARED AS #CH% LEN=KEYL%+7
IF NOT typefields% THEN 	FIELD #CH%,2 AS QR$,2 AS QD$,2 AS QM$

TYPE RcdFmtPRE3
	qr AS STRING * 2
	qd AS STRING * 2
	qm AS STRING * 2
END TYPE 
DIM SHARED PRE3 AS RcdFmtPRE3

	GET#CH%,1:QR%=CVI(QR$):QD%=CVI(QD$):QM%=CVI(QM$)
	IF MID$(QR$,1,1)=CHR$(0) THEN
		QR%=1:QM%=0:QD%=0:LSET QR$=MKI$(QR%)
		LSET QM$=MKI$(QM%):LSET QD$=MKI$(QD%)
		LSET QDEL$=" "
		PUT#CH%,1
		IF DEBUG%>0 THEN LOCATE 25,1:PRINT "ฎ--F I R S T--ฏ";
		IF DEBUG%=2 THEN X$=INPUT$(1)
		END IF
	RETURN
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ   C H A I N    O U T   T O   I N D E X   F O R   L I K E   K E Y
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
ICHAIN:
	IF DEBUG%>0 THEN  LOCATE 25,1:PRINT "ฎ--C H A I N--ฏ";
	IF DEBUG%=2 THEN X$=INPUT$(1)
	Q%=2:QL%=0:QF%=-2
	IF QR%=1 THEN
		QF%=-1:QL%=1:Q%(QL%)=0

	ELSE
	DO WHILE QF%=-2
		QL%=QL%+1:Q%(QL%)=Q%
		GET#CH%,Q%
		IF QK$=QKEY$ THEN QF%=0:EXIT DO
			IF QK$<QKEY$ THEN
				'๐๐๐๐๐ LOW END OF SEARCH
				LNUM%=CVI(LNUM$)
				IF LNUM%=0 THEN QF%=-1 ELSE Q%=LNUM%
			ELSE
				'๐๐๐๐๐ HIGH END OF SEARCH
				RNUM%=CVI(RNUM$)
				IF RNUM%=0 THEN QF%=-1 ELSE Q%=RNUM%
			END IF
		LOOP
	END IF

	IF QDEL$="D" AND Q$<>"WRITE" THEN QF%=-1 'Logical delete
	IF QL%>1 AND Q$<>"WRITE" AND Q$<>"DELET" THEN QL%=QL%-1

	RETURN
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ        A D D    R E C O R D S   T O   T  H E   I N D E X              บ
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
IWRITE:
	IF DEBUG%>0 THEN LOCATE 25,1:PRINT "ฎ--W R I T E--ฏ";
	IF DEBUG%=2 THEN X$=INPUT$(1)
	GOSUB ICHAIN

	ADD%=1:DEL%=0:DEEPER%=0

	IF QF%=0 THEN  '>> Search found
		IF QDEL$="D" THEN
			GET#CH%,Q%
			LSET QDEL$=" "
			PUT#CH%,Q%
			DEL%=-1
			QF%=0

		ELSE
			Q$="EXISTS":QF%=-1
			ADD%=0
			END IF

	ELSE  '>> Search not found, add new node
		IF QR%=1 THEN
		BAL%=0:DEEPER%=1

		ELSE
		'๐๐๐๐๐ SET PREVIOUS INDEX RECORD
		GET#CH%,Q%
		IF CVI(LNUM$)=0 AND CVI(RNUM$)=0 THEN DEEPER%=1
		BAL%=1
		QBAL%=CVI(QBAL$)
		IF QK$<QKEY$ THEN
			LSET LNUM$=MKI$(QR%+1)
			IF CVI(RNUM$)<>0 THEN LSET QBAL$=MKI$(QBAL%-1):BAL%=0
			END IF
		IF QK$>QKEY$ THEN
			LSET RNUM$=MKI$(QR%+1)
			IF CVI(LNUM$)<>0 THEN LSET QBAL$=MKI$(QBAL%+1):BAL%=0
			END IF

		PUT#CH%,Q%
		'๐๐๐๐๐ SET NEW INDEX RECORD
		END IF
	Q%=QR%+1
	LSET LNUM$=MKI$(0):LSET RNUM$=MKI$(0)
	LSET QKEY$=QK$
	LSET QBAL$=MKI$(0)
	OLDQ%=Q%:OLDK$=QKEY$:OLDL$=LNUM$:OLDR$=RNUM$
	LSET QDEL$=" "
	PUT#CH%,Q%:QF%=0
	'๐๐๐๐๐ WALK BACK UP TREE AND BALANCE
	WHILE BAL%
		OLDQ2%=OLDQ%:OLDK2$=OLDK$:OLDL2$=OLDL$:OLDR2$=OLDR$
		OLDQ%=Q%:OLDK$=QKEY$:OLDL$=LNUM$:OLDR$=RNUM$
		Q%=Q%(QL%)
		GET#CH%,Q%
		IF CVI(LNUM$)=OLDQ% THEN ADJ%=-1
		IF CVI(RNUM$)=OLDQ% THEN ADJ%=+1
		QBAL%=CVI(QBAL$)+ADJ%

		SELECT CASE QBAL%
		CASE IS <-1
			GOSUB RRIGHT:DEEPER%=0
		CASE IS >+1
			GOSUB RLEFT:DEEPER%=0
		CASE ELSE
			LSET QBAL$=MKI$(QBAL%)
			PUT#CH%,Q%
			QL%=QL%-1:IF QL%<1 THEN BAL%=0
		END SELECT

		WEND
	END IF

	'๐๐๐๐๐ UPDATE HEADER RECORD
	LNUM%=CVI(LNUM$):RNUM%=CVI(RNUM$)
	GET#CH%,1
	QR%=CVI(QR$):QM%=CVI(QM$):QD%=CVI(QD$)
	QR%=QR%+ADD%
	QD%=QD%+DEL%
	QM%=QM%+DEEPER%
	BAL%=0:ADD%=0:DEEPER%=0
	LSET QR$=MKI$(QR%):LSET QM$=MKI$(QM%):LSET QD$=MKI$(QD%)
	PUT#CH%,1

RETURN

RRIGHT:
	LNUM%=CVI(LNUM$):RNUM%=CVI(RNUM$)
	IF CVI(OLDL$)=OLDQ2% THEN
		IF DEBUG%>0 THEN LOCATE 25,1:PRINT "ฎ--ROLL RIGHT, EXTERNAL--ฏ AT "QKEY$;
		IF DEBUG%=2 THEN X$=INPUT$(1)
		LSET OLDK1$=QKEY$
		LSET QKEY$=OLDK$
		LSET OLDR$=RNUM$
		LSET RNUM$=LNUM$
		LSET LNUM$=OLDL$
		LSET QBAL$=MKI$(0)
		PUT#CH%,Q%

		GET#CH%,LNUM%
		LSET QKEY$=OLDK1$
		LSET LNUM$=RNUM$
		LSET RNUM$=OLDR$
		LSET QBAL$=MKI$(0)
		PUT#CH%,LNUM%


	ELSE
		IF DEBUG%>0 THEN LOCATE 25,1:PRINT "ฎ--ROLL RIGHT, INTERNAL--ฏ AT "QKEY$;
		IF DEBUG%=2 THEN X$=INPUT$(1)
		LSET OLDK1$=QKEY$
		LSET OLDR1$=RNUM$
		LSET QKEY$=OLDK2$
		LSET RNUM$=OLDR$
		LSET QBAL$=MKI$(0)
		PUT#CH%,Q%

		GET#CH%,OLDQ%
		LSET RNUM$=OLDL2$
		LSET QBAL$=MKI$(0)
		PUT#CH%,OLDQ%

		GET#CH%,OLDQ2%
		LSET QKEY$=OLDK1$
		LSET LNUM$=RNUM$
		LSET RNUM$=OLDR1$
		LSET QBAL$=MKI$(0)
		PUT#CH%,OLDQ2%
		END IF
	BAL%=0
	RETURN

RLEFT:
	LNUM%=CVI(LNUM$):RNUM%=CVI(RNUM$)
	IF CVI(OLDR$)=OLDQ2% THEN
		IF DEBUG%>0 THEN LOCATE 25,1:PRINT "ฎ--ROLL LEFT, EXTERNAL--ฏ AT "QKEY$;
		IF DEBUG%=2 THEN X$=INPUT$(1)
		LSET OLDK1$=QKEY$
		LSET QKEY$=OLDK$
		LSET OLDL$=LNUM$
		LSET LNUM$=RNUM$
		LSET RNUM$=OLDR$
		LSET QBAL$=MKI$(0)
		PUT#CH%,Q%
		GET#CH%,RNUM%
		LSET QKEY$=OLDK1$
		LSET RNUM$=LNUM$
		LSET LNUM$=OLDL$
		LSET QBAL$=MKI$(0)
		PUT#CH%,RNUM%
	ELSE
		IF DEBUG%>0 THEN LOCATE 25,1:PRINT "ฎ--ROLL LEFT, INTERNAL--ฏ AT "QKEY$;
		IF DEBUG%=2 THEN X$=INPUT$(1)
		LSET OLDK1$=QKEY$
		LSET OLDL1$=LNUM$
		LSET QKEY$=OLDK2$
		LSET LNUM$=OLDL$
		LSET QBAL$=MKI$(0)
		PUT#CH%,Q%

		GET#CH%,OLDQ%
		LSET LNUM$=OLDR2$
		LSET QBAL$=MKI$(0)
		PUT#CH%,OLDQ%

		GET#CH%,OLDQ2%
		LSET QKEY$=OLDK1$
		LSET RNUM$=LNUM$
		LSET LNUM$=OLDL1$
		LSET QBAL$=MKI$(0)
		PUT#CH%,OLDQ2%
		END IF
	BAL%=0
	RETURN
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ        D U M P   I N D E X                                            บ
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
IDUMP:
	CLS
	prtlen%=keyl%
	if prtlen%<10 or prtlen%>40 then prtlen%=40

	GET#CH%,1:QR%=CVI(QR$):QD%=CVI(QD$):QM%=CVI(QM$)
	PRINT USING "Number of records in file:#####";QR%-1
	PRINT USING "Number of deleted records:#####";QD%
	PRINT USING "Maximum depth of treepath:#####";QM%
	PRINT
	PRINT       " Seq   Key"+SPACE$(prtlen%+4)+"lnum  Rnum    Bal  Del"
	FOR I%=2 TO QR%+QD%+2
		GET#CH%
		L$=STR$(CVI(LNUM$)-1):R$=STR$(CVI(RNUM$)-1)
		QBAL%=CVI(QBAL$)
		IF CVI(LNUM$)=0 THEN L$=SPACE$(5)
		IF CVI(RNUM$)=0 THEN R$=SPACE$(5)
		if qdel$=chr$(0) then LSET qdel$=" "
		ab$=right$(qkey$,2)
		sfx$="  ":MID$(SFX$,1,1)=MID$(Ab$,2,1):MID$(SFX$,2,1)=MID$(Ab$,1,1)
		ab=cvi(sfx$)
		aaa$=left$(qkey$,prtlen%-2)
		AAA$=AAA$+str$(ab)
PRINT USING "####  |&|  \  \   \  \   ###   |!|"			 ;I%-1,AAA$,L$,R$,QBAL%,QDEL$
		NEXT
	PRINT:COLOR 2:PRINT "Press SPACE BAR to continue":COLOR 2
	X$="":DO UNTIL X$=" ":X$=INKEY$:LOOP
	RETURN
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ        R E A D   F I R S T   R E C O R D   I N   F I L E              บ
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
IFIRST:
	IF DEBUG%>0 THEN LOCATE 25,1:PRINT "ฎ--F I R S T--ฏ";
	IF DEBUG%=2 THEN X$=INPUT$(1)
	Q%=2:QL%=0
	GOSUB LOWESTNODE'Get lowest node
	RETURN
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ        R E A D   I N D E X   I N   O R D E R                          บ
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
IREAD:
	IF DEBUG%>0 THEN LOCATE 25,1:PRINT "ฎ--R E A D  --ฏ";
	IF DEBUG%=2 THEN X$=INPUT$(1)
	IF CVI(RNUM$)>0 THEN
			'๐๐๐๐๐ Right node found ๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐
			QL%=QL%+1:Q%(QL%)=Q%
			Q%=CVI(RNUM$)
			GOSUB LOWESTNODE'Get lowest node
		ELSE
			'๐๐๐๐๐ Left node found ๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐
			LEFTAGN:
			OLDQ%=Q%:Q%=Q%(QL%):QL%=QL%-1

			IF Q%<=0 THEN
				QF%=-1
			ELSE
				GET#CH%,Q%
				IF CVI(RNUM$)=OLDQ% THEN GOTO LEFTAGN
					END IF
		END IF

	IF QF%=0 AND QDEL$="D" THEN GOTO IREAD
XIREAD:
	RETURN
	'๐๐๐๐๐ Get lowest node in a sub tree ๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐
LOWESTNODE:
	GET#CH%,Q%
	LNUM%=CVI(LNUM$)
	WHILE LNUM%>0
		QL%=QL%+1
		Q%(QL%)=Q%
		Q%=LNUM%
		GET#CH%,Q%
		LNUM%=CVI(LNUM$)
		WEND
	RETURN
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ        R E A D P  I N D E X   I N   R E V E R S E  O R D E R          บ
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
IREADP:
	IF DEBUG%>0 THEN LOCATE 25,1:PRINT "ฎ--R E A D P--ฏ";
	IF DEBUG%=2 THEN X$=INPUT$(1)
	IF CVI(LNUM$)>0 THEN
			'๐๐๐๐๐ Left node found ๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐
			QL%=QL%+1:Q%(QL%)=Q%
			Q%=CVI(LNUM$)
			GOSUB HIGHESTNODE'Get highest node
		ELSE
			'๐๐๐๐๐ Right node found ๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐
			RIGHTAGN:
			OLDQ%=Q%:Q%=Q%(QL%):QL%=QL%-1

			IF Q%<=0 THEN
				QF%=-1
			ELSE
				GET#CH%,Q%
				IF CVI(LNUM$)=OLDQ% THEN GOTO RIGHTAGN
			END IF
		END IF

	IF QF%=0 AND QDEL$="D" THEN GOTO IREADP
XIREADP:
	RETURN
	'๐๐๐๐๐ Get highest node in a sub tree ๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐๐
HIGHESTNODE:
	GET#CH%,Q%
	RNUM%=CVI(RNUM$)
	WHILE RNUM%>0
		QL%=QL%+1
		Q%(QL%)=Q%
		Q%=RNUM%
		GET#CH%,Q%
		RNUM%=CVI(RNUM$)
		WEND
	RETURN
	'ษอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออป
	'บ     D E L E T E   A   R E C O R D                                     บ
	'ศอออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออออผ
IDELET:
	IF DEBUG%>0 THEN LOCATE 25,1:PRINT "ฎ--D E L E T E--ฏ";
	IF DEBUG%=2 THEN X$=INPUT$(1)
	GOSUB ICHAIN
	DEL%=0:ADD%=0
	IF QF%=-1 OR QDEL$="D" THEN
		Q$="NOT FOUND"

	ELSE
		LSET QDEL$="D"
		PUT#CH%,Q%:QF%=0
		DEL%=1:ADD%=-1
		END IF

	'๐๐๐๐๐ UPDATE HEADER RECORD
	LNUM%=CVI(LNUM$):RNUM%=CVI(RNUM$)
	GET#CH%,1
	QR%=CVI(QR$):QD%=CVI(QD$)
	QR%=QR%+ADD%
	QD%=QD%+DEL%
	LSET QR$=MKI$(QR%):LSET QD$=MKI$(QD%)
	PUT#CH%,1
	RETURN
END SUB
