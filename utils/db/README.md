# Database Utilities

**Backup db.json before using these scripts**

## Shrink DB

### [trim_monkey_db.py](trim_monkey_db.py) 

This deletes unused Gitadora and IIDX non-best scores, which can drastically reduce the size of db.json in a multiuser environment

Example:
`python utils\db\trim_monkey_db.py`

## Score Import

Instructions:

1. Enable `EA Automap` and `EA Netdump` in spicecfg

1. Boot the game on the source network to export

1. Card in on the source profile to export (all the way to music select menu)

1. Exit the game

1. Disable `EA Automap` and `EA Netdump` in spicecfg

1. Run the corresponding import script

### [import_ddr_spice_automap.py](import_ddr_spice_automap.py)

Example: `python utils\db\import_ddr_spice_automap.py --automap_xml automap_0.xml --version 19 --monkey_db db.json --ddr_id 12345678`

- `--version` 19 for A20P or 20 for A3

- `--ddr_id` destination profile in db.json

### [import_iidx_spice_automap.py](import_iidx_spice_automap.py)

Example: `python utils\db\import_iidx_spice_automap.py --automap_xml automap_0.xml --version 30 --monkey_db db.json --iidx_id 12345678`

- `--version` must match the source export version (27+ supported)

- `--iidx_id` destination profile in db.json