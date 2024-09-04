import random
from dowhy import CausalModel
import warnings
warnings.filterwarnings('ignore')
from itertools import chain, combinations
from itertools import product
import ast
import copy
from z3 import *
import logging

"""
This module contains utility functions for causal inference and treatment effect estimation.
It provides tools for generating and evaluating treatments, calculating conditional average
treatment effects (CATE), and solving optimization problems related to set coverage.
"""

THRESHOLD = 0.1

def getRandomTreatment(atts, df):
    """
    Generate a random treatment from the given attributes and dataframe.

    Args:
        atts (list): List of attribute names to consider for treatment.
        df (pd.DataFrame): The input dataframe.

    Returns:
        tuple: A tuple containing the treatment dictionary and the updated dataframe,
               or None if no valid treatment is found.
    """
    ans = {}
    k = random.randrange(1, len(atts))
    selectedAtts = random.sample(atts, k)

    for a in selectedAtts:
        val = random.choice(list(set(df[a].tolist())))
        ans[a] = val
    df['TempTreatment'] = df.apply(lambda row: addTempTreatment(row, ans), axis=1)
    logging.info(f"TempTreatment value counts: {df['TempTreatment'].value_counts()}")
    valid = list(set(df['TempTreatment'].tolist()))
    # no tuples in treatment group
    if len(valid) < 2:
        return None
    return ans, df

def getAllTreatments(atts, df):
    """
    Generate all possible treatments from the given attributes and dataframe.

    Args:
        atts (list): List of attribute names to consider for treatment.
        df (pd.DataFrame): The input dataframe.

    Returns:
        list: A list of all valid treatment dictionaries.
    """
    ans = []
    atts_vals = getAttsVals(atts,df)

    for selectedAtts in chain.from_iterable(combinations(atts, r) for r in range(len(atts)+1)):
        if len(selectedAtts) == 0:
            continue
        dict_you_want = {your_key: atts_vals[your_key] for your_key in selectedAtts}
        keys, values = zip(*dict_you_want.items())
        permutations_dicts = [dict(zip(keys, v)) for v in product(*values)]
        for p in permutations_dicts:
            df['TempTreatment'] = df.apply(lambda row: addTempTreatment(row, p), axis=1)
            valid = list(set(df['TempTreatment'].tolist()))
            # no tuples in treatment group
            if len(valid) < 2:
                continue
            ans.append(p)
    logging.info(f"Number of patterns to consider: {len(ans)}")
    return ans

def countHighLow(df, bound, att):
    """
    Count the number of high and low values in a dataframe column based on a bound.

    Args:
        df (pd.DataFrame): The input dataframe.
        bound (float): The threshold value.
        att (str): The name of the attribute (column) to count.

    Returns:
        tuple: A tuple containing the count of high values and low values.
    """
    vals = df[att].tolist()

    high = 0
    low = 0
    for v in vals:
        if v >= bound:
            high = high + 1
        else:
            low = low + 1
    return high,low

def getAttsVals(atts,df):
    """
    Get unique values for each attribute in the dataframe.

    Args:
        atts (list): List of attribute names.
        df (pd.DataFrame): The input dataframe.

    Returns:
        dict: A dictionary with attribute names as keys and lists of unique values as values.
    """
    ans = {}
    for a in atts:
        vals = list(set(df[a].tolist()))
        ans[a] = vals
    return ans

def getNextLeveltreatments(treatments_cate, df_g, ordinal_atts, high, low, dag, target):
    """
    Generate next level treatments based on the current treatments and their effects.

    Args:
        treatments_cate (dict): Dictionary of treatments and their effects.
        df_g (pd.DataFrame): The input dataframe.
        ordinal_atts (dict): Dictionary of ordinal attributes and their ordered values.
        high (bool): Flag to include high treatments.
        low (bool): Flag to include low treatments.
        dag (list): The causal graph represented as a list of edges.
        target (str): The target variable name.

    Returns:
        list: A list of next level treatment dictionaries.
    """
    logging.debug(f"getNextLeveltreatments input: treatments_cate={treatments_cate}, high={high}, low={low}")
    treatments = []

    positives = getTreatmeants(treatments_cate, 'positive', df_g, dag, ordinal_atts, target)
    treatments = getCombTreatments(df_g, positives, treatments, ordinal_atts)
    logging.debug(f"getNextLeveltreatments output: treatments={treatments}")
    return treatments

def getCombTreatments(df_g, positives, treatments, ordinal_atts):
    """
    Generate combined treatments from positive treatments.

    Args:
        df_g (pd.DataFrame): The input dataframe.
        positives (list): List of positive treatments.
        treatments (list): List to store the combined treatments.
        ordinal_atts (dict): Dictionary of ordinal attributes and their ordered values.

    Returns:
        list: Updated list of treatments including the new combined treatments.
    """
    for comb in combinations(positives, 2):
        t = copy.deepcopy(comb[1])
        t.update(comb[0])
        if len(t.keys()) == 2:
            df_g['TempTreatment'] = df_g.apply(lambda row: addTempTreatment(row, t, ordinal_atts), axis=1)
            valid = list(set(df_g['TempTreatment'].tolist()))
            # no tuples in treatment group
            if len(valid) < 2:
                continue
            size = len(df_g[df_g['TempTreatment'] == 1])
            # treatment group is too big or too small
            if size > 0.9 * len(df_g) or size < 0.1 * len(df_g):
                continue
            treatments.append(t)

    return treatments

def getLevel1treatments(atts, df,ordinal_atts):
    """
    Generate level 1 treatments (single attribute-value pairs).

    Args:
        atts (list): List of attribute names.
        df (pd.DataFrame): The input dataframe.
        ordinal_atts (dict): Dictionary of ordinal attributes and their ordered values.

    Returns:
        list: A list of level 1 treatment dictionaries.
    """
    ans = []
    atts_vals = getAttsVals(atts,df)

    count = 0
    for att in atts_vals:
        for val in atts_vals[att]:
            p = {att:val}
            df['TempTreatment'] = df.apply(lambda row: addTempTreatment(row, p, ordinal_atts), axis=1)
            valid = list(set(df['TempTreatment'].tolist()))
            # no tuples in treatment group
            if len(valid) < 2:
                continue
            size = len(df[df['TempTreatment'] == 1])
            count = count+1
            # treatment group is too big or too small
            if size > 0.9*len(df) or size < 0.1*len(df):
                logging.debug(f"Treatment group {p} is too big or too small: {size} out of total {len(df)}")
                continue
            ans.append(p)
    return ans

def getTreatmeants(treatments_cate, bound, df_g, DAG, ordinal_atts, target):
    """
    Get treatments based on their effects and a specified bound.

    Args:
        treatments_cate (dict or list): Treatments and their effects.
        bound (str): The bound type ('positive' or 'negative').
        df_g (pd.DataFrame): The input dataframe.
        DAG (list): The causal graph represented as a list of edges.
        ordinal_atts (dict): Dictionary of ordinal attributes and their ordered values.
        target (str): The target variable name.

    Returns:
        list: A list of treatments meeting the specified criteria.
    """
    logging.debug(f"getTreatmeants input: treatments_cate={treatments_cate}, bound={bound}")
    ans = []
    if isinstance(treatments_cate, list):
        for treatment in treatments_cate:
            if bound == 'positive':
                if getTreatmentCATE(df_g, DAG, treatment, ordinal_atts, target) > 0:
                    ans.append(treatment)
    else:
        for k,v in treatments_cate.items():
            if bound == 'positive':
                if v > 0:
                    ans.append(ast.literal_eval(k))
    logging.debug(f"getTreatmeants output: ans={ans}")
    return ans

def getCates(DAG, t_h,t_l,cate_h, cate_l, df_g, ordinal_atts, target, treatments):
    """
    Calculate Conditional Average Treatment Effects (CATE) for a list of treatments.

    Args:
        DAG (list): The causal graph represented as a list of edges.
        t_h (dict): The current treatment with the highest CATE.
        t_l (dict): The current treatment with the lowest CATE.
        cate_h (float): The current highest CATE value.
        cate_l (float): The current lowest CATE value.
        df_g (pd.DataFrame): The input dataframe.
        ordinal_atts (dict): Dictionary of ordinal attributes and their ordered values.
        target (str): The target variable name.
        treatments (list): List of treatments to evaluate.

    Returns:
        tuple: A tuple containing the updated treatments_cate dictionary, t_h, cate_h, t_l, and cate_l.
    """
    treatments_cate = {}
    for treatment in treatments:
        CATE = getTreatmentCATE(df_g, DAG, treatment, ordinal_atts, target)
        if CATE == 0:
            continue
        treatments_cate[str(treatment)] = CATE
        if CATE > cate_h:
            cate_h = CATE
            t_h = treatment
        if CATE < cate_l:
            cate_l = CATE
            t_l = treatment

    logging.debug(f"treatments_cate in getCates: {treatments_cate}")

    return treatments_cate, t_h, cate_h, t_l,cate_l

def getCatesGreedy(DAG, t_h, cate_h, df_g, ordinal_atts, target, treatments):
    """
    Calculate Conditional Average Treatment Effects (CATE) for a list of treatments using a greedy approach.

    Args:
        DAG (list): The causal graph represented as a list of edges.
        t_h (dict): The current treatment with the highest CATE.
        cate_h (float): The current highest CATE value.
        df_g (pd.DataFrame): The input dataframe.
        ordinal_atts (dict): Dictionary of ordinal attributes and their ordered values.
        target (str): The target variable name.
        treatments (list): List of treatments to evaluate.

    Returns:
        tuple: A tuple containing the updated treatments_cate dictionary, t_h, and cate_h.
    """
    treatments_cate = {}
    for treatment in treatments:
        CATE = getTreatmentCATE(df_g, DAG, treatment, ordinal_atts, target)
        if CATE == 0:
            continue
        treatments_cate[str(treatment)] = CATE
        if CATE > cate_h:
            cate_h = CATE
            t_h = treatment

    logging.debug(f"treatments_cate in getCatesGreedy: {treatments_cate}")

    return treatments_cate, t_h, cate_h

def getTreatmentCATE(df_g, DAG, treatment, ordinal_atts, target):
    """
    Calculate the Conditional Average Treatment Effect (CATE) for a given treatment.

    Args:
        df_g (pd.DataFrame): The input dataframe.
        DAG (list): The causal graph represented as a list of edges.
        treatment (dict): The treatment to evaluate.
        ordinal_atts (dict): Dictionary of ordinal attributes and their ordered values.
        target (str): The target variable name.

    Returns:
        float: The calculated CATE value, or 0 if the calculation fails or is insignificant.
    """
    df_g['TempTreatment'] = df_g.apply(lambda row: addTempTreatment(row, treatment, ordinal_atts), axis=1)
    DAG_ = changeDAG(DAG, treatment)
    causal_graph = """
                        digraph {
                        """
    for line in DAG_:
        causal_graph = causal_graph + line + "\n"
    causal_graph = causal_graph + "}"
    try:
        ATE, p_value = estimateATE(causal_graph, df_g, 'TempTreatment', target)
        if p_value > THRESHOLD:
            ATE = 0
    except:
        ATE = 0
        p_value = 0

    logging.debug(f"Treatment: {treatment}, ATE: {ATE}, p_value: {p_value}")

    return ATE

def addTempTreatment(row, ans, ordinal_atts):
    """
    Add a temporary treatment column to the dataframe based on the given treatment.

    Args:
        row (pd.Series): A row from the dataframe.
        ans (dict): The treatment dictionary.
        ordinal_atts (dict): Dictionary of ordinal attributes and their ordered values.

    Returns:
        int: 1 if the row satisfies the treatment conditions, 0 otherwise.
    """
    for a in ans:
        if a in ordinal_atts:
            index = ordinal_atts[a].index(ans[a])
            index_i = ordinal_atts[a].index(row[a])
            if index_i < index:
                return 0
        else:
            if not row[a] == ans[a]:
                return 0
    return 1

def changeDAG(dag, randomTreatment):
    """
    Modify the causal graph (DAG) to incorporate the treatment variable.

    Args:
        dag (list): The original causal graph represented as a list of edges.
        randomTreatment (dict): The treatment to incorporate into the DAG.

    Returns:
        list: The modified causal graph with the treatment variable incorporated.
    """
    DAG = copy.deepcopy(dag)
    toRomove = []
    toAdd = ['TempTreatment;']
    for a in randomTreatment:
        for c in DAG:
            if '->' in c:
                if a in c:
                    toRomove.append(c)
                    # left hand side
                    if c.find(a) == 0:
                        string = c.replace(a, "TempTreatment")
                        if not string in toAdd:
                            toAdd.append(string)
    for r in toRomove:
        if r in DAG:
            DAG.remove(r)
    for a in toAdd:
        if not a in DAG:
            DAG.append(a)
    
    # Ensure TempTreatment is connected to the outcome
    DAG.append('TempTreatment -> ConvertedSalary;')
    
    return list(set(DAG))

def estimateATE(causal_graph, df, T, O):
    """
    Estimate the Average Treatment Effect (ATE) using the CausalModel from DoWhy.

    Args:
        causal_graph (str): The causal graph in DOT format.
        df (pd.DataFrame): The input dataframe.
        T (str): The name of the treatment variable.
        O (str): The name of the outcome variable.

    Returns:
        tuple: A tuple containing the estimated ATE value and its p-value.
    """
    # Filter for required records
    df_filtered = df[(df[T] == 0) | (df[T] == 1)]
    
    model = CausalModel(
        data=df_filtered,
        graph=causal_graph.replace("\n", " "),
        treatment=T,
        outcome=O)

    estimands = model.identify_effect()

    causal_estimate_reg = model.estimate_effect(estimands,
                                                method_name="backdoor.linear_regression",
                                                target_units="ate",
                                                effect_modifiers = [],
                                                test_significance=True)
    return causal_estimate_reg.value, causal_estimate_reg.test_stat_significance()['p_value']

def LP_solver(sets, weights, tau, k, m):
    """
    Solve the Set Cover Problem using Linear Programming.

    Args:
        sets (dict): Dictionary of sets with their names as keys and elements as values.
        weights (dict): Dictionary of weights for each set.
        tau (float): The minimum fraction of elements that must be covered.
        k (int): The maximum number of sets that can be selected.
        m (int): The total number of elements.

    Returns:
        list: A list of selected set names that satisfy the constraints and maximize the objective.
    """
    solver = Optimize()

    # Create a boolean variable for each set
    set_vars = {name: Bool(name) for name in sets}

    # # Add the constraint that at most k sets can be selected
    solver.add(Sum([set_vars[name] for name in sets]) <= k)

    # Add the constraint that at least tau fraction of all elements must be covered
    elements = set.union(*[set(sets[name]) for name in sets])
    element_covered = [Bool(f"Element_{element}") for element in elements]
    for i, element in enumerate(elements):
        solver.add(Implies(element_covered[i], Or([set_vars[name] for name in sets if element in sets[name]])))

    solver.add(Sum(element_covered) >= (tau * m))

    # Maximize the sum of weights
    solver.maximize(Sum([set_vars[name] * weights[name] for name in sets]))

    # Check for satisfiability and retrieve the optimal solution
    if solver.check() == sat:
        model = solver.model()
        selected_sets = [name for name in sets if is_true(model[set_vars[name]])]
        return selected_sets
    else:
        logging.warning("No solution was found!")
        return []