# MonkeyBusiness

experimental local testing server

## Usage

Run [start.bat (Windows)](start.bat) or [start.sh (Linux)](start.sh)

[web interface](https://github.com/drmext/BounceTrippy/releases), [score import](utils/db)

## Troubleshooting

- Delete [or fix](start.bat#L9) `/.venv` if the server folder is moved or python is upgraded

- DRS, GD, and NOST require mdb xml copied to the server folder

- **URL Slash 1 (On)** [may still be required in rare cases](modules/__init__.py#L46)
