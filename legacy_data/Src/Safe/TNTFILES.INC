'/////////////////////////////////////////////////////////////////////////////
'>>>> Set the channel of the Tint/Formulation/Company files.
'/////////////////////////////////////////////////////////////////////////////
SELECT CASE mode$
CASE "A - F": ch.hedx% = 63: ch.hed% = 64: ch.det% = 65: Modedesc$ = "A - F"
CASE "Tints": ch.hedx% = 53: ch.hed% = 54: ch.det% = 55: Modedesc$ = "Tints"
CASE "JOT..": ch.hedx% = 81: ch.hed% = 54: ch.det% = 55: Modedesc$ = "Jot.."
CASE "BRI..": ch.hedx% = 82: ch.hed% = 54: ch.det% = 55: Modedesc$ = "bri.."
CASE "WAT..": ch.hedx% = 83: ch.hed% = 54: ch.det% = 55: Modedesc$ = "abc.."
CASE "DEF..": ch.hedx% = 84: ch.hed% = 54: ch.det% = 55: Modedesc$ = "def.."
CASE "GHI..": ch.hedx% = 84: ch.hed% = 54: ch.det% = 55: Modedesc$ = "ghi.."
CASE ELSE: ch.hedx% = 63: ch.hed% = 64: ch.det% = 65: Modedesc$ = "A - F": mode$ = "A - F"
END SELECT

