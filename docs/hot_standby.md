# Gin Machine — Hot Standby Mode

## Purpose
Maintains heat exchanger temperatures but isolates boiler and vapor flow.

## Conditions
- Jacket heaters ON
- Jacket pumps ON
- Boiler Heat OFF
- V1 CLOSED
- V2 CLOSED
- V5A/V5B CLOSED
- No vapor production
- Safe for long periods

## Usage
- Used between botanical changeovers
- Used overnight if system finishes late
- System ready for immediate restart

## Transition Out of Hot Standby
- User loads botanicals
- User sets Fresh flags
- Execute "Release to Production"
