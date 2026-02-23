# Gin Machine — Sequencer Logic

## Botanical Sequencer
- Uses WIT2 to count product mass
- Exposure limit: 2.5 kg per chamber
- States:
  - Fresh → In-Process → Spent
- Prerequisite: Chamber must be flagged Fresh to be opened
- Automatic switch at 2.5 kg
- Provides depletion warnings

## Copper Sequencer
- Uses WIT2 mass tracking
- Exposure limit: ~10 kg per copper bank
- Offline banks require copper replacement
- Sequencer isolates spent bank

## Integration
- Botanical sequencer controls V4/V5 exposure
- Copper sequencer controls V6/V7
