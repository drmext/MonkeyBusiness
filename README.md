# MonkeyBusiness

e-amusement server using [FastAPI](https://github.com/tiangolo/fastapi) and [TinyDB](https://github.com/msiemens/tinydb)

for experimental local testing and playing

**don't host it publicly as-is**

## Instructions

1. Install [python](https://www.python.org/ftp/python/3.11.3/python-3.11.3-amd64.exe) with "Add python.exe to PATH" checked

1. Run [start.bat (Windows)](start.bat) or [start.sh (Linux)](start.sh)

1. Edit prop/ea3-config.xml services *url* and url_slash *1*

## Playable Games

- DDR A20 PLUS
- DDR A3

- DRS

- GITADORA 5 Matixx
- GITADORA 6 EXCHAIN
- GITADORA 7 NEX+AGE
- GITADORA 8 HIGH-VOLTAGE
- GITADORA 9 FUZZ-UP

- IIDX 18 Resort Anthem
- IIDX 19 Lincle
- IIDX 20 tricoro
- IIDX 29 CastHour
- IIDX 30 RESIDENT

- NOSTALGIA Op.3

- SDVX 6 EXCEED GEAR

## Troubleshooting

- **URL Slash 1 (On)** must be enabled in tools or ea3-config

- GITADORA requires `mdb_*.xml` copied to the server folder

- NOSTALGIA requires `music_list.xml` copied to the server folder

- DRS requires `music-info-base.xml` copied to the server folder

## Score Import

Scores can be [imported](utils/db) from any network

- DDR

- IIDX

## Web Interface

Extract [BounceTrippy](https://github.com/drmext/BounceTrippy/releases) webui to the server folder

- DDR
