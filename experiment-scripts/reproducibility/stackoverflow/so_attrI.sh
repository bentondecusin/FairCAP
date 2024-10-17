#!/usr/bin/bash
pkill -f ssh
python ../run_experiment.py stackoverflow/config_lo_attrI.json so/remote_lo_attrI.json  &
python ../run_experiment.py stackoverflow/config_md_attrI.json so/remote_md_attrI.json 





