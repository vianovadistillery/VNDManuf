'SUB calcusecost
   '* Calculate use cost from SG & cost price
  ab$ = msrmat.PurUnit$ + "-" + msrmat.UseUnit$
  SELECT CASE ab$
  CASE "KG-LT": msrmat.UseCost = msrmat.purcost * msrmat.Sg
  CASE "KG-ML": msrmat.UseCost = msrmat.purcost * msrmat.Sg / 1000
  CASE "LT-KG"
        IF msrmat.Sg <> 0 THEN msrmat.UseCost = msrmat.purcost / msrmat.Sg
        IF msrmat.Sg = 0 THEN msrmat.UseCost = msrmat.purcost
  CASE "LT-GM"
        IF msrmat.Sg <> 0 THEN msrmat.UseCost = msrmat.purcost / msrmat.Sg * 1000
        IF msrmat.Sg = 0 THEN msrmat.UseCost = msrmat.purcost / 1000
  CASE "/M-EA": msrmat.UseCost = msrmat.purcost / 1000
  CASE "/H-EA": msrmat.UseCost = msrmat.purcost / 100
  CASE "MT-KG": msrmat.UseCost = msrmat.purcost / 1000
  CASE "MT-GM": msrmat.UseCost = msrmat.purcost / 1000 / 1000
  CASE "MT-LT": msrmat.UseCost = msrmat.purcost * msrmat.Sg / 1000
  CASE "MT-ML": msrmat.UseCost = msrmat.purcost * msrmat.Sg / 1000000
  CASE "LT-OZ": msrmat.UseCost = msrmat.purcost / 26.7
  CASE "LT-UT": msrmat.UseCost = msrmat.purcost / 26.7 / 48
  CASE "LT-ML": msrmat.UseCost = msrmat.purcost / 1000
  CASE "KG-GM": msrmat.UseCost = msrmat.purcost / 1000
  CASE "GM-LT": msrmat.UseCost = msrmat.purcost * msrmat.Sg / 1000
  CASE "ML-LT": msrmat.UseCost = msrmat.purcost * 1000
  CASE "TK": msrmat.UseCost = msrmat.purcost
  CASE ELSE: msrmat.UseCost = msrmat.purcost
  END SELECT
  '* Round to 2 decimal plmsrmat.activees UP ie 3.0001 = 3.01
  CALL ROUND(msrmat.UseCost, 2.5)


'END SUB
