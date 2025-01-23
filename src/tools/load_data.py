import json
import os
from pathlib import Path
import sys

SRC_PATH = Path(__file__).parent.parent
sys.path.append(os.path.join(SRC_PATH, "tools"))
sys.path.append(os.path.join(SRC_PATH, "algorithms"))
sys.path.append(os.path.join(SRC_PATH, "algorithms", "metrics"))

import logging
from typing import Any, Tuple
import pandas as pd
import pygraphviz as pgv
from prescription import Prescription, PrescriptionList
from utility_functions import CATE


def load_data(
    datatable_path: str, dag_path: str, prune: bool = False
) -> Tuple[pd.DataFrame, Any]:
    """
    Load data from a CSV file into a pandas DataFrame.

    Args:
        datatable_path (str): Path to the CSV file.
        dag_path(str): Path to the dot file.

    Returns:
        pd.DataFrame: Loaded data
        DAG
    """

    logging.debug(f"Loading data from {datatable_path}")
    df = pd.read_csv(datatable_path)
    df = df.drop(["Unnamed: 0"], axis=1, errors="ignore")
    logging.debug(f"Loaded {len(df)} rows and {len(df.columns)} columns")
    DAG = pgv.AGraph(dag_path, directed=True)
    DAG_str = DAG.to_string().replace(DAG.get_name(), " ")
    # When pruning is switched on, discard attributes that is not in the causal graph
    if prune:
        df = df.drop(set(df.columns).difference(DAG.nodes()), axis=1)
    return df, DAG_str


def load_rules(rule_path: str):
    with open(rule_path) as f:
        data = json.load(f)
        rxCandidates = []
        for rule in data:
            rxCandidates.append(
                Prescription(
                    rule["condition"],
                    rule["treatment"],
                    set(rule["coverage"]),
                    set(rule["protected_coverage"]),
                    rule["utility"],
                    rule["protected_utility"],
                    rule["unprotected_utility"],
                )
            )
        return rxCandidates


def load_rules(
    rule_path: str, datatable_path: str, dag_path: str, tgtO: str, attrP: str, valP: str
):
    df, DAG_str = load_data(datatable_path, dag_path)

    df_p = df[(df[attrP] == valP)]
    df_u = df[(df[attrP] != valP)]

    idx_p = set(df_p.index)
    idx_all = set(df.index)
    with open(rule_path) as f:
        data = json.load(f)
        rxCandidates = []
        for rule in data:
            condition = eval(rule["condition"])
            treatment = eval(rule["treatment"])
            mask = (df[condition.keys()] == condition.values()).all(axis=1)
            df_g = df.loc[mask]
            # drop grouping attributes
            df_g = df_g.drop(condition.keys(), axis=1)
            cate_all, pv_all = CATE(df_g, DAG_str, treatment, {}, tgtO)
            df_gp = df_g.loc[df_g.index.intersection(idx_p)]
            df_gu = df_g.loc[df_g.index.difference(idx_p)]
            cate_protec, pv_p = CATE(df_gp, DAG_str, treatment, None, tgtO)
            cate_unprotec, pv_u = CATE(df_gu, DAG_str, treatment, None, tgtO)
            covered_idx = set(df_g.index)
            covered_idx_p = set(idx_p) & covered_idx
            rxCandidates.append(
                Prescription(
                    condition=condition,
                    treatment=treatment,
                    covered_idx=covered_idx,
                    covered_idx_p=covered_idx_p,
                    utility=cate_all,
                    utility_p=cate_protec,
                    utility_u=cate_unprotec,
                    pvals=pv_all,
                )
            )

        return PrescriptionList(rxCandidates, idx_all, idx_p)
