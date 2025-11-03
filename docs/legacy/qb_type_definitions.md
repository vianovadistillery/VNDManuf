# QuickBASIC TYPE Definitions

## RcdFmtacmgn
Source: ACMGN.inc
Fields: 2

- mcode: STRING * 1
- margin: STRING * 4

## RcdFmtacmgn
Source: ACMGN01.inc
Fields: 2

- mcode: STRING * 1
- margin: STRING * 4

## RcdFmtacstk
Source: ACSTK.INC
Fields: 52

- no: INTEGER
- search: STRING * 10
- ean13: CURRENCY
- desc1: STRING * 25
- desc2: STRING * 10
- suplr: STRING * 5
- size: STRING * 3
- unit: STRING * 2
- pack: INTEGER
- dgflag: STRING * 1
- form: STRING * 4
- pkge: INTEGER
- label: INTEGER
- manu: INTEGER
- active: STRING * 1
- taxinc: STRING * 1
- salestaxcde: STRING * 1
- purcost: SINGLE
- purtax: SINGLE
- wholesalecost: SINGLE
- disccdeone: STRING * 1
- disccdetwo: STRING * 1
- wholesalecde: STRING * 1
- retailcde: STRING * 1
- countercde: STRING * 1
- tradecde: STRING * 1
- contractcde: STRING * 1
- industrialcde: STRING * 1
- distributorcde: STRING * 1
- retail: SINGLE
- counter: SINGLE
- trade: SINGLE
- contract: SINGLE
- industrial: SINGLE
- distributor: SINGLE
- suplr4stdcost: STRING * 5
- search4stdcost: STRING * 10
- cogs: SINGLE
- gpc: SINGLE
- rmc: SINGLE
- gpr: SINGLE
- soh: INTEGER
- sohv: SINGLE
- sip: INTEGER
- soo: INTEGER
- sold: INTEGER
- date: STRING * 8
- bulk: SINGLE
- lid: INTEGER
- pbox: INTEGER
- boxlbl: INTEGER
- filler: STRING * 69

## RcdFmtacstk
Source: ACSTKX.INC
Fields: 47

- no: INTEGER
- search: STRING * 10
- desc1: STRING * 25
- desc2: STRING * 10
- suplr: STRING * 5
- size: STRING * 3
- unit: STRING * 2
- pack: INTEGER
- dgflag: STRING * 1
- taxinc: STRING * 1
- salestaxcde: STRING * 1
- purcost: SINGLE
- purtax: SINGLE
- disccdeone: STRING * 1
- disccdetwo: STRING * 1
- wholesalecost: SINGLE
- filler4: STRING * 4
- tax: SINGLE
- retailcde: STRING * 1
- countercde: STRING * 1
- tradecde: STRING * 1
- contractcde: STRING * 1
- industrialcde: STRING * 1
- distributorcde: STRING * 1
- retail: SINGLE
- counter: SINGLE
- trade: SINGLE
- contract: SINGLE
- industrial: SINGLE
- distributor: SINGLE
- suplr4stdcost: STRING * 5
- search4stdcost: STRING * 10
- filler9: STRING * 7
- tax: SINGLE
- tax: SINGLE
- tax: SINGLE
- tax: SINGLE
- tax: SINGLE
- tax: SINGLE
- soo: INTEGER
- soh: INTEGER
- active: STRING * 1
- sold: INTEGER
- date: STRING * 8
- wholesalecde: STRING * 1
- ean13: CURRENCY
- filler: STRING * 4

## RcdFmtacstkx
Source: ACSTKX.INC
Fields: 49

- no: INTEGER
- search: STRING * 10
- ean13: CURRENCY
- desc1: STRING * 25
- desc2: STRING * 10
- suplr: STRING * 5
- size: STRING * 3
- unit: STRING * 2
- pack: INTEGER
- dgflag: STRING * 1
- form: STRING * 4
- pkge: INTEGER
- label: INTEGER
- manu: INTEGER
- active: STRING * 1
- taxinc: STRING * 1
- salestaxcde: STRING * 1
- purcost: SINGLE
- purtax: SINGLE
- wholesalecost: SINGLE
- disccdeone: STRING * 1
- disccdetwo: STRING * 1
- wholesalecde: STRING * 1
- retailcde: STRING * 1
- countercde: STRING * 1
- tradecde: STRING * 1
- contractcde: STRING * 1
- industrialcde: STRING * 1
- distributorcde: STRING * 1
- retail: SINGLE
- counter: SINGLE
- trade: SINGLE
- contract: SINGLE
- industrial: SINGLE
- distributor: SINGLE
- suplr4stdcost: STRING * 5
- search4stdcost: STRING * 10
- cogs: SINGLE
- gpc: SINGLE
- rmc: SINGLE
- gpr: SINGLE
- soh: INTEGER
- sohv: SINGLE
- sip: INTEGER
- soo: INTEGER
- sold: INTEGER
- date: STRING * 8
- bulk: SINGLE
- filler: STRING * 75

## RcdFmttypes
Source: ACTYP01.inc
Fields: 22

- dftype: STRING * 1
- dfdesc: STRING * 25
- x1: STRING * 1
- x2: STRING * 1
- x3: STRING * 1
- x4: STRING * 1
- x5: STRING * 1
- x6: STRING * 1
- x7: STRING * 1
- x8: STRING * 1
- x9: STRING * 1
- x10: STRING * 1
- x11: STRING * 1
- x12: STRING * 1
- x13: STRING * 1
- x14: STRING * 1
- x15: STRING * 1
- x16: STRING * 1
- x17: STRING * 1
- x18: STRING * 1
- x19: STRING * 1
- x20: STRING * 1

## RcdFmtasarcit
Source: ASARCIT.inc
Fields: 10

- adrec: STRING * 2
- addate: STRING * 8
- adtype: STRING * 2
- adsname: STRING * 30
- adcust: STRING * 5
- addocnum: STRING * 8
- adfiller: STRING * 8
- advalue: STRING * 4
- adglacc: STRING * 4
- adtext: STRING * 17

## RcdFmtAudit
Source: ASAUDIT.INC
Fields: 13

- adrec: INTEGER
- addate: STRING * 8
- adtype: STRING * 2
- adsname: STRING * 30
- adcust: STRING * 5
- addocnum: STRING * 8
- advalue: CURRENCY
- adglacc: SINGLE
- adtext: STRING * 16
- adpaid: STRING * 1
- adtax: SINGLE
- adactive: STRING * 1
- adfiller: STRING * 3

## RcdFmtclobal
Source: ASCLOBAL.inc
Fields: 12

- rec: INTEGER
- mth: STRING * 4
- cust: STRING * 5
- ocur: SINGLE
- o30: SINGLE
- o60: SINGLE
- o90: SINGLE
- cur: SINGLE
- c30: SINGLE
- c60: SINGLE
- c90: SINGLE
- filler: STRING * 5

## RcdFmtcurbal
Source: ASCURBAL.inc
Fields: 12

- rec: INTEGER
- mth: STRING * 4
- cust: STRING * 5
- ocur: SINGLE
- o30: SINGLE
- o60: SINGLE
- o90: SINGLE
- cur: SINGLE
- c30: SINGLE
- c60: SINGLE
- c90: SINGLE
- filler: STRING * 5

## RcdFmtopnbal
Source: ASOPNBAL.inc
Fields: 12

- rec: INTEGER
- mth: STRING * 4
- cust: STRING * 5
- ocur: SINGLE
- o30: SINGLE
- o60: SINGLE
- o90: SINGLE
- cur: SINGLE
- c30: SINGLE
- c60: SINGLE
- c90: SINGLE
- filler: STRING * 5

## RcdFmtassets
Source: ASSETS.inc
Fields: 12

- no: INTEGER
- key: STRING * 4
- name: STRING * 35
- desc: STRING * 35
- suplr: STRING * 35
- purdate: STRING * 8
- purcost: SINGLE
- finance: STRING * 35
- depreciation: SINGLE
- calibreq: STRING * 1
- disposaldate: STRING * 8
- date: STRING * 8

## RcdFmtcashsal
Source: CASHSAL.inc
Fields: 5

- cno: STRING * 2
- cupdrec: STRING * 2
- csize: STRING * 3
- csearch: STRING * 10
- cqtysold: STRING * 2

## RcdFmtcolbase
Source: COLBASE.inc
Fields: 3

- bscode: STRING * 1
- bdesc: STRING * 12
- bperc: STRING * 2

## RcdFmtcolcard
Source: COLCARD.inc
Fields: 1

- ccdesc: STRING * 22

## RcdFmtcolcard
Source: COLCHTX1.inc
Fields: 12

- sno: STRING * 2
- sname: STRING * 30
- saddr: STRING * 20
- spcode: STRING * 4
- sacode: STRING * 3
- sphone: STRING * 7
- sdate: STRING * 8
- scont: STRING * 20
- suburb: STRING * 20
- spbox: STRING * 6
- sdist: STRING * 1
- sret: STRING * 1

## RcdFmtcolcard2
Source: COLCHTX1.inc
Fields: 11

- places: STRING * 122
- spaddr: STRING * 20
- spsub: STRING * 20
- scur: STRING * 4
- s30: STRING * 4
- s60: STRING * 4
- s90: STRING * 4
- stype: STRING * 1
- sdays: STRING * 2
- sterms: STRING * 4
- search: STRING * 4

## RcdFmtcolcard3
Source: COLCHTX1.inc
Fields: 21

- places: STRING * 189
- daysmax: STRING * 2
- sacode1: STRING * 3
- sphone1: STRING * 7
- opn: STRING * 4
- opn30: STRING * 4
- opn60: STRING * 4
- opn90: STRING * 4
- agent: STRING * 2
- account: STRING * 4
- finvn: STRING * 2
- fpayn: STRING * 2
- climit: STRING * 4
- taxe: STRING * 10
- fcrnn: STRING * 2
- spname: STRING * 30
- scont1: STRING * 1
- scont2: STRING * 1
- sunpoz: STRING * 2
- smlpoz: STRING * 4
- filler: STRING * 12

## RcdFmtcolcard4
Source: COLCHTX1.inc
Fields: 3

- wcde: STRING * 4
- wtyp: STRING * 1
- wrrn: STRING * 2

## RcdFmtcolcard5
Source: COLCHTX1.inc
Fields: 3

- bscode: STRING * 1
- bdesc: STRING * 12
- bperc: STRING * 2

## RcdFmtcolcard6
Source: COLCHTX1.inc
Fields: 1

- ccdesc: STRING * 22

## RcdFmtcompany
Source: COMPANY.inc
Fields: 2

- cono: STRING * 2
- codesc: STRING * 40

## RcdFmtcomplnt
Source: COMPLNT.inc
Fields: 22

- no: INTEGER
- Name: STRING * 30
- Addr: STRING * 25
- sub: STRING * 20
- pcode: STRING * 4
- phone: STRING * 12
- fax: STRING * 12
- cName: STRING * 30
- cAddr: STRING * 25
- csub: STRING * 20
- cpcode: STRING * 4
- cphone: STRING * 12
- cfax: STRING * 12
- opened: STRING * 8
- closed: STRING * 8
- type: STRING * 10
- product: STRING * 10
- colour: STRING * 10
- batch: STRING * 10
- report: STRING * 10
- text(1 TO 12): STRING * 78
- filler: STRING * 150

## RcdFmtcsorder
Source: CSORDER.inc
Fields: 4

- no: STRING * 5
- bar: STRING * 1
- text: STRING * 80
- cr: STRING * 1

## RcdFmtCUSX
Source: CUSX.inc
Fields: 2

- wcde: STRING * 5
- wrrn: STRING * 2

## RcdFmtdevelop
Source: DEVELOP.inc
Fields: 15

- no: INTEGER
- Name: STRING * 30
- Addr: STRING * 25
- sub: STRING * 20
- pcode: STRING * 4
- phone: STRING * 10
- fax: STRING * 10
- opened: STRING * 8
- closed: STRING * 8
- type: STRING * 10
- product: STRING * 10
- colour: STRING * 10
- batch: STRING * 10
- report: STRING * 10
- text(1 TO 14): STRING * 78

## RcdFmtExposure
Source: EXPOSURE.inc
Fields: 13

- no: INTEGER
- rack: STRING * 1
- row: STRING * 1
- col: STRING * 1
- desc1: STRING * 25
- desc2: STRING * 10
- Supplier: STRING * 5
- tnta: STRING * 4
- exposed: STRING * 8 'Date
- year(1 TO 7): STRING * 2
- test(1 TO 7, 1 TO 10): SINGLE
- Date: STRING * 8
- filler: STRING * 665

## RcdFmtfmhisth1
Source: FMHIST.inc
Fields: 12

- form: INTEGER
- cost: STRING * 1
- rev: INTEGER
- seq: INTEGER
- rel: INTEGER
- desc: STRING * 25
- type: STRING * 1
- class: INTEGER
- yld: SINGLE
- visl: SINGLE
- vish: SINGLE
- hdate: STRING * 8

## RcdFmtfmhisth2
Source: FMHIST.inc
Fields: 4

- form: INTEGER
- cost: STRING * 1
- rev: INTEGER
- seq: INTEGER

## RcdFmtfmhisth3
Source: FMHIST.inc
Fields: 5

- form: INTEGER
- cost: STRING * 1
- rev: INTEGER
- seq: INTEGER
- text: STRING * 55

## RcdFmtfmhistd1
Source: FMHIST.inc
Fields: 9

- form: INTEGER
- cost: STRING * 1
- rev: INTEGER
- seq: INTEGER
- desc: STRING * 25
- qty: SINGLE
- unit: STRING * 2
- cmtqty: INTEGER
- cmt: STRING * 22

## RcdFmtorddet
Source: IGADET.INC
Fields: 12

- dord: INTEGER
- dseq: INTEGER
- drrn: INTEGER
- ditem: STRING * 2
- dprice: STRING * 4
- dordq: STRING * 2
- dinvq: STRING * 2
- dtax: STRING * 4
- dlinvq: STRING * 2
- dBo: STRING * 1 '
- dcogs: STRING * 4
- dfiller: STRING * 5

## RcdFmtordhed
Source: IGAHED.INC
Fields: 26

- hord: STRING * 2
- hrrn: STRING * 2
- hfiller: STRING * 2
- hdate: STRING * 8
- hordq: STRING * 4
- hdollar: STRING * 4
- hinvq: STRING * 4
- hitems: STRING * 2
- horgq: STRING * 4
- htaxe: STRING * 8
- fillera: STRING * 1
- hreford: STRING * 15
- linvnum: STRING * 12
- ldisc: STRING * 4
- hsup: STRING * 5
- hnote1: STRING * 42
- hnote2: STRING * 42
- hinitials: STRING * 3
- hpname1: STRING * 30
- hpname2: STRING * 30
- hpname3: STRING * 30
- hpname4: STRING * 25
- hdeposit: STRING * 4  ' total amount on deposit
- ldepnum: STRING * 12
- hdepnew: STRING * 4  ' new amount
- filler: STRING * 21

## RcdFmtIprice
Source: IPRICE.INC
Fields: 7

- no: INTEGER
- item: INTEGER
- search: STRING * 5
- iprice: SINGLE
- date: STRING * 8
- notes: STRING * 50
- filler: STRING * 57

## ArrayFmtIprice
Source: IPRICE.INC
Fields: 3

- no: INTEGER
- item: INTEGER
- price: SINGLE

## RcdFmtmsmisc
Source: MISC01.inc
Fields: 29

- qtyf: STRING * 2
- bchno: STRING * 2
- bchoff: STRING * 2
- cc: STRING * 40
- ccde: STRING * 6
- max1: STRING * 2
- max2: STRING * 2
- max3: STRING * 2
- max4: STRING * 2
- max5: STRING * 2
- max6: STRING * 2
- max7: STRING * 2
- max8: STRING * 2
- max9: STRING * 2
- max10: STRING * 2
- oldate: STRING * 10
- version: STRING * 2
- special: STRING * 1
- inside: STRING * 1
- bchist: STRING * 2
- trdisc: STRING * 1
- sysunt: STRING * 2
- sysnum: STRING * 2
- prthi: STRING * 1
- prtdb: STRING * 1
- prtsub: STRING * 1
- prtsup: STRING * 1
- prthi1: STRING * 1
- filler: STRING * 20

## RcdFmtbatch
Source: MSBATCH.INC
Fields: 64

- bno: INTEGER
- year: STRING * 2
- form: STRING * 4
- revision: INTEGER
- SorW: STRING * 1
- class: INTEGER
- yld: SINGLE
- ayld: SINGLE
- date: STRING * 8
- name: STRING * 30
- Resinvar: SINGLE ' actual kg
- Solventvar: SINGLE ' filled volume
- Thickenervar: SINGLE ' filled cost
- Rheomodifier: SINGLE 'actual SG
- Stainer1var: SINGLE ' waste volume
- Stainer2var: SINGLE ' YIELD" %
- Stainer3var: SINGLE ' waste $
- hord: INTEGER
- thisbatch: STRING * 8
- perltr: SINGLE ' actual cost
- datereq: STRING * 8
- dateman: STRING * 8
- manby: STRING * 3
- fltnt: STRING * 1
- flstk: STRING * 1
- flqc: STRING * 1
- yield: SINGLE
- ltr: SINGLE
- kg: SINGLE
- visc1h: SINGLE
- visc1l: SINGLE
- visc2h: SINGLE
- visc2l: SINGLE
- alccost: SINGLE ' actual cost
- rawcost: SINGLE
- filter: INTEGER
- grind: SINGLE
- ph: SINGLE
- sg: SINGLE
- Vsol: SINGLE
- Wsol: SINGLE
- pvc: SINGLE
- pbr: SINGLE
- gloss: SINGLE
- Hazard: STRING * 1
- asRmat: INTEGER
- CostPer: STRING * 2
- qcnote1: STRING * 25
- qcnote2: STRING * 25
- qcnote3: STRING * 25
- qcnote4: STRING * 25
- qcvsol: SINGLE
- qcwsol: SINGLE
- qcpvc: SINGLE
- qcpbr: SINGLE
- qcvisc1: SINGLE
- qcvisc2: SINGLE
- qcph: SINGLE
- qcgloss: SINGLE
- qcsg: SINGLE
- priority: INTEGER
- tnt: INTEGER
- dateform: STRING * 8
- Filler: STRING * 166

## RcdFmtbatch
Source: MSBATCHx.INC
Fields: 21

- bno: INTEGER
- year: STRING * 2
- form: STRING * 4
- revision: INTEGER
- SorW: STRING * 1
- class: INTEGER
- yld: SINGLE
- ayld: SINGLE
- date: STRING * 8
- name: STRING * 30
- Resinvar: SINGLE
- Solventvar: SINGLE
- Thickenervar: SINGLE
- Rheomodifier: SINGLE
- Stainer1var: SINGLE
- Stainer2var: SINGLE
- Stainer3var: SINGLE
- hord: INTEGER
- thisbatch: STRING * 8
- perltr: SINGLE
- Filler: STRING * 27

## RcdFmtbatchx
Source: MSBATCHx.INC
Fields: 21

- bno: INTEGER
- year: STRING * 2
- form: STRING * 4
- revision: INTEGER
- SorW: STRING * 1
- class: INTEGER
- yld: SINGLE
- ayld: SINGLE
- date: STRING * 8
- name: STRING * 30
- Resinvar: SINGLE
- Solventvar: SINGLE
- Thickenervar: SINGLE
- Rheomodifier: SINGLE
- Stainer1var: SINGLE
- Stainer2var: SINGLE
- Stainer3var: SINGLE
- hord: INTEGER
- thisbatch: STRING * 8
- perltr: SINGLE
- Filler: STRING * 411

## RcdFmtMSbchBK
Source: MSBCHBK.inc
Fields: 13

- bno: STRING * 2
- bfno: STRING * 2
- bccost: STRING * 1
- brev: STRING * 2
- btype: STRING * 1
- bclass: STRING * 2
- byld: STRING * 2
- bayld: STRING * 2
- bdate: STRING * 8
- bdesc: STRING * 25
- bvisl: STRING * 4
- bvish: STRING * 4
- bavis: STRING * 4

## RcdFmtmsbchhd
Source: MSBCHHD.inc
Fields: 2

- bchlow: STRING * 2
- bchhi: STRING * 2

## RcdFmtmsclass
Source: MSCLASS.inc
Fields: 5

- cldesc: STRING * 25
- clya: STRING * 8
- clyt: STRING * 8
- clyay: STRING * 8
- clyty: STRING * 8

## RcdFmtmscomt
Source: MSCOMT.inc
Fields: 1

- spk: STRING * 22

## RcdFmtmscomt2
Source: MSCOMT.inc
Fields: 1

- spkno: STRING * 2

## RcdFmtmshist
Source: MSHIST.inc
Fields: 5

- hdesc1: STRING * 15
- hq: STRING * 4
- hunit: STRING * 4
- hd: STRING * 2
- hc: STRING * 22

## RcdFmtmshisth
Source: MSHISTH.inc
Fields: 12

- hform: STRING * 2
- hcost: STRING * 1
- hrev: STRING * 2
- hrel: STRING * 2
- hdesc: STRING * 25
- htype: STRING * 1
- hclass: STRING * 2
- hyld: STRING * 4
- hvisl: STRING * 4
- hvish: STRING * 4
- hfirstdet: INTEGER
- hlastdet: INTEGER

## RcdFmtmsmisc
Source: MSMISC.INC
Fields: 34

- qtyf: STRING * 2
- bchno: STRING * 2
- bchoff: STRING * 2
- cc: STRING * 40
- ccde: STRING * 6
- max1: STRING * 2
- max2: STRING * 2
- max3: STRING * 2
- max4: STRING * 2
- max5: STRING * 2
- max6: STRING * 2
- max7: STRING * 2
- max8: STRING * 2
- max9: STRING * 2
- max10: STRING * 2
- oldate: STRING * 10
- version: STRING * 2
- special: STRING * 1
- inside: STRING * 1
- bchist: STRING * 2
- trdisc: STRING * 1
- sysunt: STRING * 2
- sysnum: STRING * 2
- prthi: STRING * 1
- prtdb: STRING * 1
- prtsub: STRING * 1
- prtsup: STRING * 1
- prthi1: STRING * 1
- DBmonth: STRING * 4
- CRmonth: STRING * 4
- cansidx: INTEGER
- labelidx: INTEGER
- labouridx: INTEGER
- filler: STRING * 16

## RcdFmtmsmkp
Source: MSMKP.inc
Fields: 3

- mk: STRING * 4
- mm: STRING * 30
- mkon: STRING * 2

## RcdFmtmsrmat
Source: MSRMAT.INC
Fields: 34

- no: INTEGER
- Desc1: STRING * 25
- Desc2: STRING * 25
- purqty: INTEGER  'New rmat# for the crossover
- Search: STRING * 5
- Sg: SINGLE
- PurCost: SINGLE
- PurUnit: STRING * 2
- UseCost: SINGLE
- UseUnit: STRING * 2
- Dealcost: SINGLE
- SupUnit: STRING * 2
- Group: INTEGER
- Active: STRING * 1
- Volsolid: SINGLE
- Solidsg: SINGLE
- Wtsolid: SINGLE
- Notes: STRING * 25
- soh: SINGLE
- Osoh: SINGLE
- Date: STRING * 8
- hazard: STRING * 1
- cond: STRING * 1
- altno(1 TO 5): INTEGER
- msdsflag: STRING * 1
- searchs: STRING * 8
- soo: INTEGER
- sip: SINGLE
- sohv: SINGLE
- restock: SINGLE
- used: SINGLE
- ean13: CURRENCY
- lastpur: STRING * 8
- supqty: SINGLE

## RcdFmtmsrmat
Source: MSRMATX.INC
Fields: 27

- no: INTEGER
- Desc1: STRING * 25
- Desc2: STRING * 25
- purqty: INTEGER  'New rmat# for the crossover
- Search: STRING * 5
- Sg: SINGLE
- PurCost: SINGLE
- PurUnit: STRING * 2
- UseCost: SINGLE
- UseUnit: STRING * 2
- DealCost: SINGLE
- SupUnit: STRING * 2
- Group: INTEGER
- Active: STRING * 1
- Volsolid: SINGLE
- Solidsg: SINGLE
- Wtsolid: SINGLE
- Notes: STRING * 25
- soh: SINGLE
- Osoh: SINGLE
- Date: STRING * 8
- hazard: STRING * 1
- cond: STRING * 1
- altno(1 TO 5): INTEGER
- msdsflag: STRING * 1
- searchs: STRING * 8
- soo: INTEGER

## RcdFmtmsrmatx
Source: MSRMATX.INC
Fields: 32

- no: INTEGER
- Desc1: STRING * 25
- Desc2: STRING * 25
- purqty: INTEGER  'New rmat# for the crossover
- Search: STRING * 5
- Sg: SINGLE
- PurCost: SINGLE
- PurUnit: STRING * 2
- UseCost: SINGLE
- UseUnit: STRING * 2
- Dealcost: SINGLE
- SupUnit: STRING * 2
- Group: INTEGER
- Active: STRING * 1
- Volsolid: SINGLE
- Solidsg: SINGLE
- Wtsolid: SINGLE
- Notes: STRING * 25
- soh: SINGLE
- Osoh: SINGLE
- Date: STRING * 8
- hazard: STRING * 1
- cond: STRING * 1
- altno(1 TO 5): INTEGER
- msdsflag: STRING * 1
- searchs: STRING * 8
- soo: INTEGER
- sip: SINGLE
- sohv: SINGLE
- restock: SINGLE
- used: SINGLE
- ean13: CURRENCY

## RcdFmtmsrmgp
Source: MSRMGP.inc
Fields: 3

- id: STRING * 5  '1.1.1'
- rmgroup: STRING * 22
- filler: STRING * 37

## FILE
Source: MTYPES.inc
Fields: 23

- SHARED: #56 LEN = 80
- dftype: STRING * 1
- dfdesc: STRING * 25
- x1: STRING * 1
- x2: STRING * 1
- x3: STRING * 1
- x4: STRING * 1
- x5: STRING * 1
- x6: STRING * 1
- x7: STRING * 1
- x8: STRING * 1
- x9: STRING * 1
- x10: STRING * 1
- x11: STRING * 1
- x12: STRING * 1
- x13: STRING * 1
- x14: STRING * 1
- x15: STRING * 1
- x16: STRING * 1
- x17: STRING * 1
- x18: STRING * 1
- x19: STRING * 1
- x20: STRING * 1

## RcdFmtnoncon
Source: NONCON.inc
Fields: 16

- no: INTEGER
- Name: STRING * 30
- Addr1: STRING * 25
- Addr2: STRING * 25
- sub: STRING * 20
- pcode: STRING * 4
- opened: STRING * 8
- closed: STRING * 8
- atext1: STRING * 78
- atext2: STRING * 78
- atext3: STRING * 78
- atext4: STRING * 78
- btext1: STRING * 78
- btext2: STRING * 78
- btext3: STRING * 78
- btext4: STRING * 78

## RcdFmtNotes
Source: NOTES.inc
Fields: 3

- text: STRING * 78
- cr: STRING * 1
- lf: STRING * 1

## RcdFmtorddet
Source: ORDDET.INC
Fields: 13

- dord: INTEGER
- dseq: INTEGER
- drrn: INTEGER
- ditem: STRING * 2
- dprice: STRING * 4
- dordq: STRING * 2
- dinvq: STRING * 2
- dtax: STRING * 4
- dlinvq: STRING * 2
- dBo: STRING * 1 '
- dotprice: STRING * 1
- dpicked: INTEGER
- dfiller: STRING * 6

## RcdFmtordhed
Source: ORDHED.INC
Fields: 22

- hord: STRING * 2
- hrrn: STRING * 2
- hfiller: STRING * 2
- hdate: STRING * 8
- hordq: STRING * 4
- hdollar: STRING * 4
- hinvq: STRING * 4
- hitems: STRING * 2
- horgq: STRING * 4
- htaxe: STRING * 12
- hreford: STRING * 12
- linvnum: STRING * 12
- ldisc: STRING * 4
- hsup: STRING * 5
- hnote1: STRING * 42
- hnote2: STRING * 42
- hinitials: STRING * 3
- hscheduled: STRING * 8
- hstatus: STRING * 2
- hupdated: STRING * 8
- hgp: STRING * 4
- filler: STRING * 70

## RcdFmtordprt
Source: ORDPRT.INC
Fields: 28

- hord: INTEGER
- hopt: INTEGER
- hcash: INTEGER
- hchginv: DOUBLE
- hchginvrrn: INTEGER
- hinvnum: DOUBLE
- hinvnumrec: INTEGER
- hthissup: STRING * 5
- hnorders: INTEGER
- hMode: STRING * 3
- hTaxRate: DOUBLE   '10 = 10%
- hDiscRate: DOUBLE   '0.20  = 20c in the dollar
- hnote1: STRING * 42
- hnote2: STRING * 42
- hNameOvertyped: STRING * 35
- hAddrOvertyped: STRING * 20
- hSuburbOvertyped: STRING * 20
- gsno: INTEGER
- gtaxin: STRING * 1
- gtender: STRING * 1
- gdoctype: STRING * 11    'TAX INVOICE'
- gformtype: STRING * 14  '
- gexdisc: DOUBLE
- gvdisc: DOUBLE
- gadvalue: CURRENCY
- gadtax: CURRENCY
- gOSCurrency: STRING * 3
- hfiller: STRING * 156

## RcdFmtSearch
Source: PHONEX.inc
Fields: 18

- key: STRING * 5
- type: STRING * 2
- company: STRING * 30
- compnum: STRING * 5
- name: STRING * 20
- sPhone: STRING * 20
- sPhone1: STRING * 20
- pstncc: STRING * 3
- email: STRING * 40
- www: STRING * 40
- ContactFirstName(6): STRING * 16
- ContactSurName(6): STRING * 20
- ContactTitle(6): STRING * 20
- ContactPhone(6): STRING * 18 '+61 xxx3 9xxx xxxx
- contactmobile(6): STRING * 18'+61 x419 x338 x450
- ContactFax(6): STRING * 18   '+61 x419 x338 x450
- Contactemail(6): STRING * 40
- crlf: STRING * 1

## RcdFmtPICKUP
Source: PICKUP.inc
Fields: 8

- pno: STRING * 2
- pname1: STRING * 30
- pname2: STRING * 30
- pname3: STRING * 30
- pname4: STRING * 25
- pactive: STRING * 1
- pphone1: STRING * 13
- pphone2: STRING * 13

## RcdFmtPICKUPX
Source: PICKUPX.inc
Fields: 2

- pxcde: STRING * 14
- pxrrn: STRING * 2

## RcdFmtorddet
Source: PORDDET.INC
Fields: 13

- dord: INTEGER
- dseq: INTEGER
- drrn: INTEGER
- ditem: STRING * 2
- dprice: STRING * 4
- dordq: STRING * 2
- dinvq: STRING * 2
- dtax: STRING * 4
- dlinvq: STRING * 2
- dBo: STRING * 1 '
- dotprice: STRING * 1
- dpicked: INTEGER
- dfiller: STRING * 6

## RcdFmtordhed
Source: PORDHED.INC
Fields: 23

- hord: STRING * 2
- hrrn: STRING * 2
- hfiller: STRING * 2
- hdate: STRING * 8
- hordq: STRING * 4
- hdollar: STRING * 4
- hinvq: STRING * 4
- hitems: STRING * 2
- horgq: STRING * 4
- htaxe: STRING * 8
- hstatus: STRING * 1
- hreford: STRING * 15
- linvnum: STRING * 12
- ldisc: STRING * 4
- hsup: STRING * 5
- hnote1: STRING * 42
- hnote2: STRING * 42
- hinitials: STRING * 3
- hdocket: STRING * 10
- hdddate: STRING * 8
- hinvdate: STRING * 8
- hdolrecd: STRING * 4
- filler: STRING * 62

## RcdFmtordprt
Source: PORDPRT.INC
Fields: 28

- hord: INTEGER
- hopt: INTEGER
- hcash: INTEGER
- hchginv: DOUBLE
- hchginvrrn: INTEGER
- hinvnum: DOUBLE
- hinvnumrec: INTEGER
- hthissup: STRING * 5
- hnorders: INTEGER
- hMode: STRING * 3
- hTaxRate: DOUBLE   '10 = 10%
- hDiscRate: DOUBLE   '0.20  = 20c in the dollar
- hnote1: STRING * 42
- hnote2: STRING * 42
- hNameOvertyped: STRING * 35
- hAddrOvertyped: STRING * 20
- hSuburbOvertyped: STRING * 20
- gsno: INTEGER
- gtaxin: STRING * 1
- gtender: STRING * 1
- gdoctype: STRING * 11    'TAX INVOICE'
- gformtype: STRING * 14  '
- gexdisc: DOUBLE
- gvdisc: DOUBLE
- gadvalue: CURRENCY
- gadtax: CURRENCY
- gOSCurrency: STRING * 3
- hfiller: STRING * 156

## RcdFmtlbl
Source: PRODUCT.inc
Fields: 9

- Desc1: STRING * 40
- Desc2: STRING * 40
- Haz1: STRING * 1
- Haz2: STRING * 1
- Un: STRING * 4
- Con1: STRING * 28
- Con2: STRING * 28
- Con3: STRING * 28
- Col: STRING * 2

## RcdFmtproject
Source: PROJECT.inc
Fields: 9

- no: INTEGER
- name: STRING * 25
- opened: STRING * 8
- closed: STRING * 8
- duedate: STRING * 8
- type: STRING * 10
- report: STRING * 10
- text(1 TO 18): STRING * 78
- filler: STRING * 125

## RcdFmtExtra
Source: QEXTRA1.inc
Fields: 9

- no: INTEGER
- name: STRING * 25
- opened: STRING * 8
- closed: STRING * 8
- duedate: STRING * 8
- type: STRING * 10
- report: STRING * 10
- text(1 TO 36): STRING * 78
- filler: STRING * 129

## RcdFmtRMORDER
Source: RMORDER.inc
Fields: 3

- text: STRING * 78
- cr: STRING * 1
- lf: STRING * 1

## RcdFmtSearch
Source: SEARCH.inc
Fields: 12

- key: STRING * 5
- type: STRING * 2
- company: STRING * 25
- compnum: STRING * 5
- name: STRING * 20
- phone1: STRING * 7
- area1: STRING * 3
- phone2: STRING * 7
- area2: STRING * 3
- phone3: STRING * 7
- area3: STRING * 3
- crlf: STRING * 1

## RcdFmtsizes
Source: SIZES.inc
Fields: 7

- skey: STRING * 2
- sdesc: STRING * 15
- short: STRING * 5
- cst(1 TO 10): STRING * 2
- prcret: STRING * 4
- prctrd: STRING * 4
- prcdst: STRING * 4

## RcdFmtsupx
Source: SUPX.inc
Fields: 2

- wcde: STRING * 5
- wrrn: STRING * 2

## RcdFmttntdet
Source: TNTDET.INC
Fields: 7

- tnt: LONG
- rmat: INTEGER
- qty: SINGLE
- cmt: INTEGER
- cmtqty: SINGLE
- ltkg: STRING * 1
- tfiller: STRING * 15

## RcdFmttntdet
Source: TNTDETX.INC
Fields: 5

- tnt: INTEGER
- rmat: INTEGER
- qty: SINGLE
- cmt: INTEGER
- cmtqty: SINGLE

## RcdFmttntdetx
Source: TNTDETX.INC
Fields: 7

- tnt: LONG
- rmat: INTEGER
- qty: SINGLE
- cmt: INTEGER
- cmtqty: SINGLE
- ltkg: STRING * 1
- tfiller: STRING * 15

## RcdFmttnthed
Source: TNTHED.INC
Fields: 31

- tnt: INTEGER
- tnta: STRING * 4
- revision: INTEGER
- name: STRING * 30
- desc: STRING * 30
- cust: STRING * 5
- SorW: STRING * 1
- class: INTEGER
- yield: SINGLE
- ltr: SINGLE
- kg: SINGLE
- visc1h: SINGLE
- visc1l: SINGLE
- visc2h: SINGLE
- visc2l: SINGLE
- alccost: SINGLE
- rawcost: SINGLE
- filter: INTEGER
- grind: SINGLE
- ph: SINGLE
- sg: SINGLE
- Vsol: SINGLE
- Wsol: SINGLE
- pvc: SINGLE
- pbr: SINGLE
- gloss: SINGLE
- Hazard: STRING * 1
- date: STRING * 8
- asRmat: INTEGER
- CostPer: STRING * 2
- filler: STRING * 1

## RcdFmttnthedx
Source: TNTHEDX.INC
Fields: 2

- tnta(1 TO 999): STRING * 4
- rrn(1 TO 999): INTEGER

## FILE
Source: TYPES.inc
Fields: 25

- SHARED: #42 LEN = 80
- 1: dftype$, 25 AS dfdesc$, 1 AS x1$, 1 AS x2$, 1 AS x3$, 1 AS x4$, 1 AS x5$, 1 AS x6$, 1 AS x7$, 1 AS x8$, 1 AS x9$, 1 AS x10$, 1 AS x11$, 1 AS x12$, 1 AS x13$, 1 AS x14$, 1 AS x15$, 1 AS x16$, 1 AS x17$, 1 AS  _
- 1: x19$, 1 AS x20$
- dftype: STRING * 1
- dfdesc: STRING * 25
- x1: STRING * 1
- x2: STRING * 1
- x3: STRING * 1
- x4: STRING * 1
- x5: STRING * 1
- x6: STRING * 1
- x7: STRING * 1
- x8: STRING * 1
- x9: STRING * 1
- x10: STRING * 1
- x11: STRING * 1
- x12: STRING * 1
- x13: STRING * 1
- x14: STRING * 1
- x15: STRING * 1
- x16: STRING * 1
- x17: STRING * 1
- x18: STRING * 1
- x19: STRING * 1
- x20: STRING * 1

## RcdFmtwhoext
Source: WHOEXT.inc
Fields: 11

- no: INTEGER
- search: STRING * 5
- names(3): STRING * 25
- phone1(3): STRING * 20
- phone2(3): STRING * 20
- addr: STRING * 25
- sub: STRING * 20
- pcode: STRING * 4
- machine(5): STRING * 8
- text(13): STRING * 77
- filler: STRING * 67

## RcdFmtwho
Source: WHOF.inc
Fields: 83

- sno: STRING * 2
- search: STRING * 4
- stype: STRING * 1
- sname: STRING * 35
- filler1: STRING * 5
- saddr: STRING * 35
- filler2: STRING * 5
- saddr2: STRING * 35
- filler3: STRING * 5
- suburb: STRING * 20
- state: STRING * 20
- spcode: STRING * 8
- spbox: STRING * 8
- spboxsub: STRING * 20
- spboxpcode: STRING * 8
- slevel: SINGLE
- ytd: SINGLE
- p1: SINGLE
- email: STRING * 40
- www: STRING * 40
- pstnCC: STRING * 3
- scontTitle: STRING * 3
- scont: STRING * 40
- sphone: STRING * 18
- sphone1: STRING * 18   ' Fax
- taxe: STRING * 10
- sgl: STRING * 4
- rep: STRING * 1
- callfreq: STRING * 1
- sdays: STRING * 2
- sterms: STRING * 4
- daysmax: STRING * 2
- scur: STRING * 4
- s0: STRING * 4
- s30: STRING * 4
- s60: STRING * 4
- s90: STRING * 4
- opn: STRING * 4
- opn30: STRING * 4
- opn60: STRING * 4
- opn90: STRING * 4
- account: STRING * 4
- advalue: STRING * 4
- climit: STRING * 4
- spnum: STRING * 2
- spname: STRING * 30
- spsub: STRING * 40
- sdist: STRING * 1
- sret: STRING * 1
- countercde: STRING * 1
- tradecde: STRING * 1
- contractcde: STRING * 1
- industrialcde: STRING * 1
- scont1: STRING * 1
- scont2: STRING * 1
- wholesalecde: STRING * 1
- addocnum: STRING * 8
- addate: STRING * 8
- sdate: STRING * 8
- Active: STRING * 1
- ContactFirstName(6): STRING * 16
- ContactSurName(6): STRING * 20
- ContactTitle(6): STRING * 20
- ContactPhone(6): STRING * 18 '+61 xxx3 9xxx xxxx
- ContactMobile(6): STRING * 18'+61 x419 x338 x450
- ContactFax(6): STRING * 18   '+61 x419 x338 x450
- Contactemail(6): STRING * 40
- BO: STRING * 1
- abn: STRING * 16
- bankcde: STRING * 3
- bankacct: STRING * 16
- p2: SINGLE
- p3: SINGLE
- p4: SINGLE
- p5: SINGLE
- p6: SINGLE
- p7: SINGLE
- p8: SINGLE
- p9: SINGLE
- p10: SINGLE
- p11: SINGLE
- p12: SINGLE
- filler5: STRING * 3

## RcdFmtWHOold
Source: WHOF.inc
Fields: 64

- sno: STRING * 2
- search: STRING * 4
- stype: STRING * 1
- sname: STRING * 40
- saddr: STRING * 40
- saddr2: STRING * 40
- suburb: STRING * 20
- state: STRING * 20
- spcode: STRING * 8
- spbox: STRING * 8
- spboxsub: STRING * 40
- email: STRING * 40
- www: STRING * 40
- pstnCC: STRING * 3
- scontTitle: STRING * 3
- scont: STRING * 40
- sphone: STRING * 12
- sphone1: STRING * 12   ' Fax
- mobile: STRING * 12
- ServiceTitle: STRING * 3
- ServiceName: STRING * 30
- Servicephone: STRING * 12
- ServiceFax: STRING * 12
- taxe: STRING * 10
- sgl: STRING * 4
- rep: STRING * 1
- callfreq: STRING * 1
- sdays: STRING * 2
- sterms: STRING * 4
- daysmax: STRING * 2
- scur: STRING * 4
- s0: STRING * 4
- s30: STRING * 4
- s60: STRING * 4
- s90: STRING * 4
- opn: STRING * 4
- opn30: STRING * 4
- opn60: STRING * 4
- opn90: STRING * 4
- account: STRING * 4
- advalue: STRING * 4
- climit: STRING * 4
- spnum: STRING * 2
- spname: STRING * 30
- spsub: STRING * 40
- sdist: STRING * 1
- sret: STRING * 1
- countercde: STRING * 1
- tradecde: STRING * 1
- contractcde: STRING * 1
- industrialcde: STRING * 1
- scont1: STRING * 1
- scont2: STRING * 1
- wholesalecde: STRING * 1
- addocnum: STRING * 8
- addate: STRING * 8
- sunpoz: STRING * 2
- smlpoz: STRING * 4
- sdate: STRING * 8
- Active: STRING * 1
- filler1: STRING * 1
- filler2: STRING * 1
- filler4: STRING * 6
- filler5: STRING * 166

## RcdFmtWHOnew
Source: WHOF.inc
Fields: 69

- sno: STRING * 2
- search: STRING * 4
- stype: STRING * 1
- sname: STRING * 40
- saddr: STRING * 40
- saddr2: STRING * 40
- suburb: STRING * 20
- state: STRING * 20
- spcode: STRING * 8
- spbox: STRING * 8
- spboxsub: STRING * 40
- email: STRING * 40
- www: STRING * 40
- pstnCC: STRING * 3
- scontTitle: STRING * 3
- scont: STRING * 40
- sphone: STRING * 12
- sphone1: STRING * 12   ' Fax
- mobile: STRING * 12
- ServiceTitle: STRING * 3
- ServiceName: STRING * 30
- Servicephone: STRING * 12
- ServiceFax: STRING * 12
- taxe: STRING * 10
- sgl: STRING * 4
- rep: STRING * 1
- callfreq: STRING * 1
- sdays: STRING * 2
- sterms: STRING * 4
- daysmax: STRING * 2
- scur: STRING * 4
- s0: STRING * 4
- s30: STRING * 4
- s60: STRING * 4
- s90: STRING * 4
- opn: STRING * 4
- opn30: STRING * 4
- opn60: STRING * 4
- opn90: STRING * 4
- account: STRING * 4
- advalue: STRING * 4
- climit: STRING * 4
- spnum: STRING * 2
- spname: STRING * 30
- spsub: STRING * 40
- sdist: STRING * 1
- sret: STRING * 1
- countercde: STRING * 1
- tradecde: STRING * 1
- contractcde: STRING * 1
- industrialcde: STRING * 1
- scont1: STRING * 1
- scont2: STRING * 1
- wholesalecde: STRING * 1
- addocnum: STRING * 8
- addate: STRING * 8
- sunpoz: STRING * 2
- smlpoz: STRING * 4
- sdate: STRING * 8
- Active: STRING * 1
- filler1: STRING * 1
- filler2: STRING * 1
- filler4: STRING * 6
- filler5: STRING * 166
- ContactName(10): STRING * 20
- ContactTitle(10): STRING * 20
- ContactPhone(10): STRING * 20
- ContactMobile(10): STRING * 20
- Contactemail(10): STRING * 40

## RcdFmtwhox
Source: WHOX.inc
Fields: 2

- wcde: STRING * 5
- wrrn: STRING * 2
