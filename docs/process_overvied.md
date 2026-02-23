# Gin Machine — Process Overview (Engineering Manual)

## 1. System Description
The Gin Machine is a continuous distillation and botanical extraction system consisting of:
- Boiler generating ethanol–water vapor
- A/B liquid sections with jacket heating
- A/B vapor chambers with jacket heating
- Copper catalytic banks
- Condenser and parrot
- Feed drum on WIT1
- Product drum on WIT2

## 2. Core Subsystems
- Liquid Heat Exchanger (Liquid-Hex)
- Vapor Heat Exchanger (Vapor-Hex)
- Boiler system with PID-controlled feed
- Botanical extraction chambers (A/B)
- Copper catalytic banks (A/B)
- Condenser and chiller system
- Sequencers (botanical + copper)

## 3. Operating Modes
- Startup
- Running / Production
- Hot Standby
- Shutdown
- Cleaning/Flush Cycle

## 4. Safety Philosophy
Heating is only allowed when:
- Condenser cooling is proven active
- Heat exchanger flows are adequate
- Botanical chambers are properly flagged
- Boiler is isolated unless explicitly commanded
