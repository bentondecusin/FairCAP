#!/usr/bin/bash
pkill -f ssh
python ../run_experiment.py german_credit/two_layer/gc_two_layer.json gc/remote_full.json




