# Gin Machine Instrumentation Specification

## Liquid Heat Exchanger
- TC1: Jacket temperature (110–112 °C normal)
- FT1: Flow transmitter (≥3 L/min for heat permissive)
- PT1: Pressure transmitter
- Liquid-Hex Pump
- Liquid-Hex Heater

## Vapor Heat Exchanger
- TC2: Jacket temperature (~89 °C)
- FT2: Flow transmitter
- PT2: Pressure transmitter
- Vapor-Hex Pump
- Vapor-Hex Heater

## Boiler System
- TC4: Boiler temperature
- PT3: Boiler pressure
- LIT1: Boiler level (185 mm setpoint)
- V1: Boiler inlet valve
- V2: Boiler outlet valve
- P1: Feed pump (PID-controlled)
- P1ST: Pump release signal

## Liquid Sections (A/B)
- LIT2: Liquid level in A-side liquid section
- TC8: B-side liquid-section vapor-out temperature
- V3: Liquid drain valve
- V8: Vapor splitter valve (nominal 40%)

## Vapor Sections (A/B)
- V4A/V4B: Vapor chamber inlet valves
- V5A/V5B: Vapor chamber outlet valves (system high point)
- TC9: A-side vapor chamber temperature
- TC10: B-side vapor chamber temperature

## Copper Banks
- V6A/V6B → Copper chambers → V7A/V7B
- No active sensors in copper chambers

## Condenser
- TC5: Chiller-water inlet temperature
- TC6: Chiller-water outlet temperature (<20 °C required)
- FIT2: Cooling-water flow rate (≥3 L/min required)

## Product/Feed Drums
- WIT1: Feed drum load cell
- WIT2: Product drum load cell
