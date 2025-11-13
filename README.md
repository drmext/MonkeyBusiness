# MonkeyBusiness

Experimental e-amuse server intended for testing hacks, also usable by players

## Usage

Run [start.bat (Windows)](start.bat) or [start.sh (Linux, MacOS)](start.sh)

[web interface](https://github.com/drmext/BounceTrippy/releases), [score import](utils/db)

## Playable Games
- IIDX 18-20, 29-33 (Online Arena/BPL support)
- DDR A20P, A3 (OmniMIX support w/ DAN & pfree score saving hack)
- GD 6-10 DELTA (Battle Mode support)
- DRS
- NOST 3
- SDVX 6

**Note**: Playable means settings/scores *should* save and load. Events are not implemented.

## Troubleshooting

- Delete [or fix](start.bat#L9) `/.venv` if the server folder is moved or python is upgraded

- DRS, GD, and NOST require mdb xml files copied to the server folder

- **URL Slash 1 (On)** [may still be required in rare cases](modules/__init__.py#L46)

- When initially creating a DDR profile, complete an entire credit without pfree hacks
