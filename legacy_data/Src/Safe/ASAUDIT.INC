	'>>>>>>- AUDIT FILE RECORD LAYOUT -<<<<<
	'///////////////////////////////////////////////////////////////////////
	'////    ACCOUNTING AUDIT FILE RECORD TYPES
	'///////////////////////////////////////////////////////////////////////
	'///     CI - Creditors invoice
	'///     CC + Creditors credit note
	'///     CP + Creditors payment
	'///     CD + Creditors discount taken
	'///     CT - Credit sales tax (Portion of invoice)
	'///
	'///     DI + Debtors invoice
	'///     DC - Debtors credit note
	'///     DP - Debtors payment
	'///     DD - Debtors discount given
	'///     DT + Debtors sales tax (Portion of invoice)
	'///
	'///     LC - Ledger Credit
	'///     LD + Ledger Debit
	'///
	'///     CJ ? Credit journal entry
	'///     DJ ? Debit journal entry
	'///     PE = Period end
	'///     XX = Zero balance. to be deleted.
	'///////////////////////////////////////////////////////////////////////
	'///     Paid flag
	'///     U= UnPaid
	'///     P= Paid
	'///     I= Installment
	'///     A= Allocated
	'///////////////////////////////////////////////////////////////////////
GOTO X.OPEN.AUDIT
OPEN.AUDIT:
	'>>>>>>- FOR NORMAL SALES  AND CASH SALES <<<<<<<
	SELECT CASE cashonly$
	CASE "N": auditname$ = auditfile$(naudit%): BEEP: BEEP: BEEP: BEEP
	CASE "Y": auditname$ = "csaudit.asf"
	CASE "M": 'Manual auditname is set outside
	END SELECT

	OPEN auditname$ FOR RANDOM SHARED AS #8 LEN = 92
	'-- for NORMAL records --

TYPE RcdFmtAudit
	adrec AS INTEGER
	addate AS STRING * 8
	adtype AS STRING * 2
	adsname AS STRING * 30
	adcust AS STRING * 5
	addocnum AS STRING * 8
	advalue AS CURRENCY
	adglacc AS SINGLE
	adtext AS STRING * 16
	adpaid AS STRING * 1
	adtax AS SINGLE
	adactive AS STRING * 1
	adfiller AS STRING * 3
	END TYPE
DIM SHARED Audit AS RcdFmtAudit

RETURN

X.OPEN.AUDIT:
