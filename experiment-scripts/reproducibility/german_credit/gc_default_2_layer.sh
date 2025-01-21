#!/usr/bin/bash
pkill -f ssh
python ../run_experiment.py german_credit/default_dag/default_2_layer.json gc/remote_full.json




