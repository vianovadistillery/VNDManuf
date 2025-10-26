DECLARE SUB getdt (OSCurrency$, updwn%)
DECLARE SUB accbrowse (rec%)
DECLARE SUB add.bo.msg (updwn%)
DECLARE SUB add.up.order (tot.ltact!, tot.ord!, tot.ext!)
DECLARE SUB addmessage (invmsg1$, invmsg2$, invmsg3$, invmsg4$)
DECLARE SUB cf8 (l%, d.elem%, newdata$)
DECLARE SUB change.disc (discovr!)
DECLARE SUB chglin (ln%, l%, d.elem%, updwn%)
DECLARE SUB delOrder (hord%, n%, clr%, autodel$, thissup$, norders%)
DECLARE SUB dsply (sno%, norders%)
DECLARE SUB dsplyLine (l%, d.elem%)
DECLARE SUB dsporders (dspstart%, norders%, custin$)
DECLARE SUB ean13 (in$, dind%)
DECLARE SUB findnext (hord%, norders%, ok%)
DECLARE SUB findorders (thissup$, norders%, hord%)
DECLARE FUNCTION funclimit$ (climit!)
DECLARE SUB get.order.vs (hord%, updwn%)
DECLARE SUB getname (tender$, updwn%)
DECLARE SUB limit.warn (s90!, s60!, s30!, scur!, climit!, updwn%, allow$)
DECLARE SUB linkedl (rrn%(), n%, firstrec%, ord%, chd%)
DECLARE SUB loadLine (m%, il%, ditem%, ordqty%, Invqty%, price!, otprice$)
DECLARE SUB open.cash.drawer ()
DECLARE SUB openpslip (opt%)
DECLARE SUB parse (hord%, opt%, cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, invmsg1$, invmsg2$)
DECLARE SUB prtinv (hord%, opt%, cash%, chginv#, chginv.rrn%, invnum#, invnumrec%, thissup$, norders%, OSCurrency$)
DECLARE SUB prtjobslip (hord%, opt%, thissup$, sno%)
DECLARE SUB prtpslip (hord%, opt%, discovr!)
DECLARE SUB rightprice (price!)
DECLARE SUB search.month (rec%, begyymd$)
DECLARE SUB searchindex (keyin$, chi%, found%)
DECLARE SUB setaudit (n%)
DECLARE SUB UpdateOrder (hord%, updwn%)
COMMON SHARED maxsup%, maxform%, maxrmat%, maxacc%, maxtypes, maxcus%, maxord%

'////////////////////////////////////////////////////////////////////////
'////    F U L L     D E B T O R S    I N V O I C I N G
'////////////////////////////////////////////////////////////////////////
'$INCLUDE: '\tpmanuf\src\pgmhead.inc'
''$INCLUDE: '\tpmanuf\src\pgmerr.inc'
	
	DIM SHARED auditfile$(15), naudit%, acstkf$

	typefields% = -1
	acstkf$ = "..."
	parm$ = ENVIRON$("PARM$")
	IF VAL(parm$) > 0 THEN pass.getcust% = -1: custin$ = parm$: updwn% = 13

	parm2$ = ENVIRON$("PARM2$")
	IF parm2$ = "PRE..." THEN acstkf$ = "PRE"

	

	'$INCLUDE: '\tpmanuf\src\whof.inc'
	'$INCLUDE: '\tpmanuf\src\cusx.inc'
	'$INCLUDE: '\tpmanuf\src\supx.inc'
	'$INCLUDE: '\tpmanuf\src\cus.inc'
	'$INCLUDE: '\tpmanuf\src\ACSTK.INC'
	'$INCLUDE: '\tpmanuf\src\ASAUDIT.INC'
	'$INCLUDE: '\tpmanuf\src\ordhed.inc'
	'$INCLUDE: '\tpmanuf\src\orddet.inc'
	keyl% = 20: qk$ = SPACE$(keyl%): rep$ = SPACE$(keyl% - 2)

	SELECT CASE acstkf$
	CASE "PRE": CALL index("OPEN ", ind%, "acstkx3.pre", 7, keyl%)
	CASE ELSE: CALL index("OPEN ", ind%, "acstkx3.acf", 7, keyl%)
	END SELECT
	'$INCLUDE: '\tpmanuf\src\msmisc.inc'
	'$INCLUDE: '\tpmanuf\src\pickup.INC'
'  GET #36, 1, msmisc
'  maxsup% = CVI(msmisc.max1$): maxform% = CVI(msmisc.max2$): maxrmat% = CVI(msmisc.max3$)
'  maxacc% = CVI(msmisc.max5$): maxtypes% = CVI(msmisc.max6$): maxcus% = CVI(msmisc.max7$)
'  maxord% = 999

	DIM SHARED C%(8), in$(maxlines%, 15), rrn%(maxlines%)
	'1=qty%,2=size,3=unit,4=itm,5=desc,6=price,7=SOH,8=ext
	'9=tax flag,10=ordqty%,11=Invqty,12=BoFlag,13=save qty
	'14=Save item, 15=Overtyped price

	

SUB accbrowse (rec%) STATIC
'$INCLUDE: '\tpmanuf\src\accbrow.bi'
END SUB

