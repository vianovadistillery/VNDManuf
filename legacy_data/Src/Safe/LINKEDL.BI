'SUB linkedlist (rrn%(), n%, firstrec%, ord%, chd%) STATIC
'.dc - Complete
	'The first record is a header.
	'DRRN points to the start of the nul linked list. (deleted records)
	'DSEQ points to the end of the nul linked list.
	'rrn%() will be a list of allocated records
	'       This routine will load, off file, or allocate new records the
	'       array from a linked list.
	'       It will totally maintain the orddet.ORD,~.SEQ & ~.RRN$
	'n% can be passed in or passed back. If its -1 then value will be returned.

	FOR i% = 1 TO UBOUND(rrn%): rrn%(i%) = 0: NEXT

	reclength% = 32
	nextrec% = LOF(49) / reclength% + 1
	IF n% < 0 THEN upd% = 0 ELSE upd% = -1

	'>- Empty file, Setup header record
	IF nextrec% = 1 THEN 'New file
		nextrec% = 2
		orddet.dord% = 32767
		orddet.dseq% = 0
		orddet.drrn% = 0
		IF upd% THEN PUT #chd%, 1, orddet
		END IF
	LOCK #chd%, 1
	GET #chd%, 1, orddet
	record1.dseq% = orddet.dseq%
	record1.drrn% = orddet.drrn%

	'>- Detemine the first record for a group.
	'   1. It may be passed into this routine
	'   2. If it is passed as 0. A New on is created.
	IF firstrec% > 0 THEN
		GET #chd%, firstrec%, orddet
		IF orddet.dord% <> ord% THEN
			firstrec% = 0
			drec% = 1
			GET #chd%, drec%, orddet
			DO WHILE NOT EOF(49)
				IF orddet.dord% = ord% AND orddet.dseq% = 1 THEN firstrec% = drec%: EXIT DO
				GET #chd%, , orddet: drec% = drec% + 1: IF drec% = 32767 THEN EXIT DO
				LOOP
			END IF
		END IF

	orddet.drrn% = firstrec%'Pointer to next record
	IF n% < 0 THEN n% = 32767

	'>- Where 0=hdr file, 1 to n% is the sequence of the detail file.
	FOR i% = 0 TO n%
		 IF i% > UBOUND(rrn%) THEN
			 CALL SNDMSG("Error in detail file, Please rebuild. (1)"): SLEEP 1
			 previous.drrn% = 0
			 n% = UBOUND(rrn%)
			 EXIT FOR
			 END IF

		IF orddet.drrn% = 0 THEN 'Create a new record
			SELECT CASE record1.drrn%
			CASE 0: newrec% = nextrec%: nextrec% = nextrec% + 1
			CASE ELSE:
				newrec% = record1.drrn%
				GET #chd%, record1.drrn%, orddet
				IF i% < n% THEN record1.drrn% = orddet.drrn%
			END SELECT
			newflag% = -1
			ELSE
			newrec% = orddet.drrn%
			newflag% = 0
			END IF

		IF i% > 0 THEN 'Update previous node in list
			GET #chd%, drec%, orddet
			previous.drrn% = orddet.drrn%
			IF orddet.dord% = -1 THEN previous.drrn% = 0
			wrkord% = ord%
			IF orddet.dord% > 0 AND orddet.dord <> ord% THEN
				CALL SNDMSG("Error in detail file, Please rebuild. (2)"): SLEEP 1
				wrkord% = orddet.dord%
				END IF
			orddet.dord% = ord%
			orddet.dseq% = i%
			orddet.drrn% = newrec%
			IF i% = n% THEN
				orddet.drrn% = 0 'Update the last record to be the end of the list
				END IF

			IF orddet.drrn% = drec% THEN
				CALL SNDMSG("Error in detail file, Please rebuild. (3)"): SLEEP 1
				END IF
			IF orddet.drrn% = drec% THEN orddet.drrn% = 0'??
			IF upd% THEN PUT #chd%, drec%, orddet
			rrn%(i%) = drec%
			END IF

		drec% = newrec%
		GET #chd%, drec%, orddet
		IF newflag% THEN orddet.drrn% = 0
		IF newflag% AND n% = 32767 THEN n% = i%: EXIT FOR

		NEXT

		IF n% = 0 THEN previous.drrn% = firstrec%
		'>- Delete any unused part of the list.
		IF previous.drrn% <> 0 THEN
			drec% = previous.drrn%
			shit% = 0
			DO WHILE drec% > 0
					shit% = shit% + 1
					IF shit% > 99 THEN
					CALL SNDMSG("Error in detail file, Please rebuild. (4)"): SLEEP 1
					EXIT DO
					END IF
				GET #chd%, drec%, orddet
				previous.drrn% = orddet.drrn%
				orddet.dord% = -1
				orddet.dseq% = 0
				orddet.drrn% = 0
				'THESE THREE LINES ADDED BY PD TO CLEAR OVERTYPE PRICE IN DFILLER
				orddet.dotprice$ = SPACE$(1)
				orddet.dpicked% = 0
				orddet.dfiller$ = SPACE$(9)
				orddet.dbo$ = SPACE$(1)
				previous.nul.dseq% = record1.dseq%
				record1.dseq% = drec%
				IF record1.drrn% = 0 THEN record1.drrn% = drec%
				IF upd% THEN PUT #chd%, drec%, orddet
				IF orddet.drrn% = drec% THEN
					CALL SNDMSG("Error in detail file, Please rebuild. (5)"): SLEEP 1
					END IF
				'Go back and update the previos node in the null Link
				IF previous.nul.dseq% > 0 THEN
					GET #chd%, previous.nul.dseq%, orddet
					orddet.drrn% = drec%
					IF upd% THEN PUT #chd%, previous.nul.dseq%, orddet
					IF orddet.drrn% = previous.nul.dseq% THEN
						CALL SNDMSG("Error in detail file, Please rebuild. (6)"): SLEEP 1
						END IF

					END IF

				drec% = previous.drrn%
				LOOP


			END IF


	'>- Update the header record.
	GET #chd%, 1, orddet
	orddet.dseq% = record1.dseq%
	orddet.drrn% = record1.drrn%
	IF orddet.drrn% = 0 THEN orddet.dseq% = 0
	IF upd% THEN PUT #chd%, 1, orddet

	UNLOCK #chd%, 1

'END SUB
