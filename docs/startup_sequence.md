# Gin Machine — Startup Sequence (Engineering)

## Step 1 — Enable Condenser Cooling
- Turn on chiller (Linbell DLSB)
- Confirm TC6 < 20 °C
- Confirm FIT2 ≥ 3 L/min
- Heat disabled unless condenser is functional

## Step 2 — Start Heat Exchanger Pumps
- Liquid-Hex Pump ON
- Vapor-Hex Pump ON
- Verify FT1 > 0 and FT2 > 0

## Step 3 — Enable Jacket Heating
- Turn on Liquid-Hex Heater (when FT1 ≥ 3 L/min)
- Turn on Vapor-Hex Heater
- Wait for setpoints (TC1 ≈ 110–112 °C, TC2 ≈ 89 °C)

## Step 4 — Power Feed Pump
- P1 power ON (PID armed)

## Step 5 — Enable Boiler Heating
- Boiler Heat ON
- TC4 rising toward ~85–95 °C indicates vapor formation

## Step 6 — Open Boiler Valves
- V1 OPEN (feed)
- V2 OPEN (vapor outlet)
- When V1 opens, enable P1ST

## Step 7 — Set System Valves
- V8 = 40%
- V3 CLOSED

## Step 8 — System in Production Mode
- Vapor routing to A/B chambers controlled by botanical sequencer
