# MonkeyBusiness

Welcome to the world of e-Amusement.
This is an experimental local testing server.

## Supported Versions

A list of games and versions based on server status.

### beatmaniaIIDX
Full support
- beatmaniaIIDX 32 (Pinky Crush)
- beatmaniaIIDX 31 (EPOLIS)
- beatmaniaIIDX 30 (RESIDENT)
- beatmaniaIIDX 29 (CastHour)

Unknown
- beatmaniaIIDX 28 (BISTROVER)
- beatmaniaIIDX 27 (HEROIC VERSE)
- beatmaniaIIDX 26 (Rootage)
- beatmaniaIIDX 25 (CANNON BALLERS)
- beatmaniaIIDX 24 (SINOBUZ)
- beatmaniaIIDX 23 (Copula)
- beatmaniaIIDX 22 (PENDUAL)
- beatmaniaIIDX 21 (SPADA)
- beatmaniaIIDX 20 (tricoro)
- beatmaniaIIDX 19 (Lincle | KDZ)
- beatmaniaIIDX 18 (Resort Anthem | JDZ)

Stubs
- beatmaniaIIDX 17 (SIRIUS | JDJ)
- beatmaniaIIDX 16 (EMPRESS | I00)
- beatmaniaIIDX 15 (DJ TROOPERS | HDD)
- beatmaniaIIDX 14 (GOLD | GLD)

Not working
- beatmaniaIIDX 13 (DistorteD | FDD)
- beatmaniaIIDX 12 (HAPPY SKY | ECO)
- beatmaniaIIDX 11 (IIDX RED | E11)
- beatmaniaIIDX 10 (10th style | D01)
- beatmaniaIIDX 9 (9th style | C02)

## Usage

Run [start.bat (Windows)](start.bat) or [start.sh (Linux)](start.sh)

[web interface](https://github.com/drmext/BounceTrippy/releases), [score import](utils/db)

## Notes

- Delete [or fix](start.bat#L9) `/.venv` if the server folder is moved or python is upgraded

- DRS, GD, and NOST require mdb xml copied to the server folder

- **URL Slash 1 (On)** [may still be required in rare cases](modules/__init__.py#L46)
