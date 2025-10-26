
  WRITE #97, "DI-ID", "Debtor Invoice"
  WRITE #97, "BLANK", "cus.sname$, cus.search$, cus.stype$, cus.sno, cus.saddr$, cus.saddr2$, cus.suburb$, cus.spcode$, pickup.pname1$, pickup.pname2$, pickup.pname3$, pickup.pname4$"
  WRITE #97, "DIHED", RTRIM$(cus.sname$), RTRIM$(cus.search$), RTRIM$(cus.stype$), cus.sno, RTRIM$(cus.saddr$), RTRIM$(cus.saddr2$), RTRIM$(cus.suburb$), RTRIM$(cus.spcode$), RTRIM$(PICKUP.pname1$), RTRIM$(PICKUP.pname2$), RTRIM$(PICKUP.pname3$),  _
RTRIM$(PICKUP.pname4$)'??
  WRITE #97, "BLANK", "ordhed.hreford$, ordhed.linvnum$, FNDYY$(ordhed.hdate$), ordhed.htaxe$, DATE$, ordhed.hpname1$, ordhed.hpname2$,ordhed.hpname3$, ordhed.hpname4$"
  WRITE #97, "DIINF", RTRIM$(ordhed.hreford$), ordhed.linvnum$, FNDYY$(ordhed.hdate$), ordhed.htaxe$, MID$(DATE$, 4, 2) + "/" + MID$(DATE$, 1, 2) + "/" + MID$(DATE$, 9, 2), RTRIM$(ordhed.hpname1$), RTRIM$(ordhed.hpname2$), RTRIM$(ordhed.hpname3$),  _
RTRIM$(ordhed.hpname4$)

  WRITE #97, "BLANK", "invmsg1$, invmsg2$, invmsg3$, invmsg4$"
  WRITE #97, "DIMSG", invmsg1$, invmsg2$, invmsg3$, invmsg4$
  WRITE #97, "BLANK", "tot.ltinv, tot.ord, Rate!, tot.ext, depos!, tot.depos!, advalue - tot.depos, advalue, (tot.ext / tot.cogs - 1)"
  WRITE #97, "DITOT", tot.ltinv, tot.ord, Rate!, tot.ext, depos!, tot.depos!, advalue - tot.depos, advalue, (tot.ext / tot.cogs - 1)

writeexternal2:
WRITE #97, "DIDET", dlinvq%, acstk.size$, acstk.unit$, ditem%, acstk.desc1$, acstk.desc2$, acstk.offspec$, acstk.prodtype$, dprice, dtax, ext!, acstk.totalcogs, (dprice / acstk.totalcogs - 1)

