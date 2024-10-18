# Greedy Fair Prescription Rules Algorithm

This project implements a greedy algorithm for generating fair prescription rules. It aims to balance utility and fairness in decision-making processes, particularly focusing on protected groups.

# Table of Contents
1. [Overview](#overview) 
2. [Setup](#setup)   
3. [Running Experiments](#experiments)  
   3.a [Data configuration]()   
   3.b [Experiment and variants configuration]()
6. [Replication](#experiments)

## Overview  <a name="overview"></a> 

In this project, we implement 3-step algorithms that generate prescriptions(rules) to increase/decrease the value of an attribute while protecting a specified group. The algorithm can be broken down into 3 steps: group mining, treatment mining and rule selection. The details can be found in the [paper]()

## Setup <a name="setup"></a>
1. Clone this repository:
```
git clone https://github.com/USERNAME/FairPrescriptionRules
cd FairPrescriptionRules
```
You can run the algorithm either locally or **remotely(recommended)**
### Local Setup (Skip to Remote setup if you wish to run the experiment on cloudlab)
Linux:
```
sudo apt-get update
sudo apt-get install virtualenv
sudo apt-get install graphviz-dev
virtualenv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

Macintosh:
```
pip3 install virtualenv
brew install graphviz
virtualenv venv
source ./venv/bin/activate
pip install -r requirements.txt
```
#### After installing dependencies. Run the sanity test to verify the result
```
cd reproducibility
sh local_sanity_check.sh
```

Expected output:
```
coverage constr: {'variant': 'rule', 'threshold': 0.8, 'threshold_p': 0.8}
fairness constr: None
Elapsed time for group mining: 0.0587611198425293 seconds. 3 groups are found
Elapsed time for treatment mining: 10.959924936294556 seconds. 3 rules are found
Elapsed time for Selection: 0.38343214988708496 seconds
```
Under the `FairPrescriptionRules/output/Local\ Sanity\ Test/greedy` directory, the following files can be found:
- selected_rules.json: rules generated from treatment mining
- mined_rules.json: rules selected by greedy algorithm
- experiment_results_greedy.csv: information inlcluding expected utilty, coverage and fairness during the selection process

## Data & Experiment Specification
### Data
The datasets we use for evaluations are `German credit` and `StackOverflow`. They can be found in the `data` directory. 

To run the experiment, we need both **data configuration** and **experiment configuration**.
### A **data configuration** is json file that contains the following field
1. `_dataset_path`: home path to the dataset and data configurations
2. `_datatable_path`: local path to the dataframe (in .csv format)
3. `_dag_path`: path to the causal directed acyclic graph (in .dot format)
4. `_immutable_attributes`, `_mutable_attributes`: immutbale and mutable (mutally exclusive to immutbale) attributes
5. `_protected_attributes`, `_protected_values`: protected group, i.e. the individuals whose protected_attributes = protected_values
6. `_target_outcome`, targeted attributes that the algorithm aims to maxize
### A **experiment configuration** is json file that contains the following field
1. `_is_remote`: flag that indicates whether the experiment runs remotely
2. `_expmt_title`: experiment tile
3. `_cloudlab_user`, `_cloudlab_postfix`: cloudlab configuration
4. `_cloudlab_nodes`: array of node names on cloudlab
5. `_models`: array of models that contains model name, starting script and variants if there is any

### A model contains the following fields
1. `_name` (required): name of the model, used in the output directory
2. `_start` (required): starting script 
3. `_coverage_constraint` (optional): contains name of the variant (group or rule), threshold, and protected threshold
3. `_fairness_constraint` (optional): contains name of the variant (group_sp, individual_sp, grouo_bgl, individual_bgl) and threshold

See examples of configuration [here](https://github.com/USERNAME/FairPrescriptionRules/tree/master/experiment-scripts/experiment-configs/sanity)
## Running the Algorithms

Locate to the script directory
```
cd FairPrescriptionRules/experiment-scripts
```
Then run `run_experiment.py` in the following semantics:  
```
python run_experiment.py PATH_TO_DATA_CONFIGURATION PATH_TO_EXPERIMENT_CONFIGURATION
``` 
See the section above regarding the specification of data configuration and experiment configuration
### To reproduce the result from the paper
```
cd FairPrescriptionRules/reproducibility
```
And execute the corresponding script
e.g. `sh stackoverflow/so_full.sh`


## Output

Both algorithms will generate output files with their results:

- The greedy algorithm outputs to `experiment_results_greedy.csv`
- The CauSumX algorithm outputs to `experiment_results_causumx.csv`

These files contain detailed information about the selected rules, their fairness scores, and other relevant metrics.

