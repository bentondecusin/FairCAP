#!/usr/bin/bash
pkill -f ssh
python ../run_experiment.py stackoverflow/config_lo_attrM.json so/remote_lo_attrM.json &
python ../run_experiment.py stackoverflow/config_md_attrM.json so/remote_md_attrM.json 





