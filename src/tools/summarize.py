# %%
import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


variants_sp = [
    "greedy_no_constraint",
    "greedy+group_coverage",
    "greedy+rule_coverage",
    "greedy+group_sp",
    "greedy+individual_sp",
    "greedy+group_coverage+group_sp",
    "greedy+rule_coverage+group_sp",
    "greedy+group_coverage+individual_sp",
    "greedy+rule_coverage+individual_sp",
]
variants_bgl = [
    "0greedy_no_constraint",
    "1greedy+group_coverage",
    "2greedy+rule_coverage",
    "3greedy+group_bgl",
    "4greedy+individual_bgl",
    "5greedy+group_coverage+group_bgl",
    "6greedy+rule_coverage+group_bgl",
    "7greedy+group_coverage+individual_bgl",
    "8greedy+rule_coverage+individual_bgl",
]


def expUtitVsK(path):
    variants = []
    for f in os.listdir(path):
        if "greedy" in f:
            variants.append(f)
    variants.sort()
    i = 0
    plt.figure(figsize=(20, 20))
    plt.subplots_adjust(hspace=0.5)
    for v in variants:
        i += 1
        if "cov" in v or "cvrg" in v or "fair" in v:
            plt.subplot(len(variants) // 2, 2, i)
        else:
            plt.subplot(3, 3, i)
        plt.title(v)
        plt.xlabel("k")
        plt.ylabel("ExpUtil")
        plt.legend()
        try:
            df = pd.read_csv(f"{path}/{v}/experiment_results_greedy.csv")
            plt.plot(df["k"], df["expected_utility"], label="Expected")
            plt.plot(
                df["k"],
                df["unprotected_expected_utility"],
                label="Unprotected Expected",
            )
            plt.plot(
                df["k"], df["protected_expected_utility"], label="Protected Expected"
            )
            if "bgl" in v:
                plt.hline(y=0.1, color="b", linestyle="-", label="BGL threshold")

            plt.legend(loc="best")
        except:
            pass

    plt.plot()


def execTimeBreakDown(path):
    variants = []
    for f in os.listdir(path):
        if "greedy" in f:
            variants.append(f)
    variants.sort()
    i = 0
    plt.figure(figsize=(20, 20))
    breakdown = []
    for v in variants:
        with open(f"{path}/{v}/stdout.log") as f:
            matches = re.findall(r"([\d:,.]+) seconds?", f.read())
        breakdown.append(matches)
    stages = ["Group Mining", "Treatment Mining", "Rule Selection"]

    df = pd.DataFrame(breakdown, index=variants, columns=stages, dtype="float")
    ttl_time = np.sum(df, axis=1)
    sorted_idx = np.argsort(ttl_time)
    df = df.iloc[sorted_idx]

    base = pd.Series([0.0 for i in range(len(variants))], index=df.index)
    for s in stages:
        p = plt.barh(df.index, df[s], label=s, left=base)
        base += df[s]
    plt.legend(loc="best")
    plt.title("Runtime decomposition")
    plt.show()


def print_table(path):
    variants = []
    for f in os.listdir(path):
        if "sp" in f:
            variants = variants_sp
            break
        if "bgl" in f:
            variants = variants_bgl
            break
    i = 0
    fields = [
        " # rules ",
        " coverage ",
        " coverage pro ",
        " exp utility ",
        " exp utility non-pro",
        "exp utility pro ",
        "unfairness",
    ]
    table = []
    for v in variants:
        i += 1
        row = []

        df = pd.read_csv(f"{path}/{v}/experiment_results_greedy.csv")

        k = min(20, max(df["k"]))

        rec = df.loc[k - 1]

        row.append(k)
        row.append(rec["coverage_rate"])
        row.append(rec["protected_coverage_rate"])
        row.append(round(float(rec["expected_utility"]), 2))
        row.append(round(float(rec["unprotected_expected_utility"]), 2))
        row.append(round(float(rec["protected_expected_utility"]), 2))
        row.append(
            round(
                float(
                    rec["unprotected_expected_utility"]
                    - rec["protected_expected_utility"]
                ),
                2,
            )
        )
        row = [str(i).replace("%", "\\%") for i in row]
        table.append("& ".join(row))

    t = table
    print(
        f"""\midrule 
No constraints  & {t[0]} \\\\
Group coverage &{t[1]} \\\\
Rule coverage  & {t[2]}\\\\
Group fairness  & {t[3]} \\\\
Individual fairness   & {t[4]} \\\\
Group coverage, Group fairness  & {t[5]} \\\\
Rule coverage, Group fairness  & {t[6]}\\\\
Group coverage, Individual fairness  & {t[7]}\\\\
Rule coverage, Individual fairness  &{t[8]} \\\\
        """
    )


# %%


def print_so_cvrg(path):
    variants = os.listdir(path)
    variants.sort()
    i = 0
    fields = [
        " # rules ",
        " coverage ",
        " coverage pro ",
        " exp utility ",
        " exp utility non-pro",
        "exp utility pro ",
        "unfairness",
    ]
    table = []

    for v in variants:
        i += 1
        row = []

        df = pd.read_csv(f"{path}/{v}/experiment_results_greedy.csv")

        k = min(20, max(df["k"]))

        rec = df.loc[k - 1]

        row.append(k)
        row.append(rec["coverage_rate"])
        row.append(rec["protected_coverage_rate"])
        row.append(round(float(rec["expected_utility"]), 2))
        row.append(round(float(rec["unprotected_expected_utility"]), 2))
        row.append(round(float(rec["protected_expected_utility"]), 2))
        row.append(
            round(
                float(
                    rec["unprotected_expected_utility"]
                    - rec["protected_expected_utility"]
                ),
                2,
            )
        )
        row = [str(i).replace("%", "\\%") for i in row]
        table.append("& ".join(row))

    t = table
    print(
        f"""\midrule 
Rule coverage (25\\%) & {t[0]} \\\\
Rule coverage (50\\%) &{t[1]} \\\\
Rule coverage (75\\%)  & {t[2]}\\\\
Rule coverage (90\\%)  & {t[3]} \\\\
Group coverage (25\\%)  & {t[4]} \\\\
Group coverage (50\\%) & {t[5]} \\\\
Group coverage (75\\%) & {t[6]}\\\\
Group coverage (90\\%) & {t[7]}\\\\
        """
    )


output_path = "/Users/bcyl/FairPrescriptionRules/output/so_gdp/so_coverage_analysis"

print_so_cvrg(output_path)

# %%


def print_gc_cvrg(path):
    variants = os.listdir(path)
    variants.sort()
    i = 0
    fields = [
        " # rules ",
        " coverage ",
        " coverage pro ",
        " exp utility ",
        " exp utility non-pro",
        "exp utility pro ",
        "unfairness",
    ]
    table = []
    for v in variants:
        i += 1
        row = []

        df = pd.read_csv(f"{path}/{v}/experiment_results_greedy.csv")

        k = min(20, max(df["k"]))
        if k != 0:
            rec = df.loc[k - 1]
        else:
            rec = df.loc[0]
        row.append(k)
        row.append(rec["coverage_rate"])
        row.append(rec["protected_coverage_rate"])
        row.append(round(float(rec["expected_utility"]), 2))
        row.append(round(float(rec["unprotected_expected_utility"]), 2))
        row.append(round(float(rec["protected_expected_utility"]), 2))
        row.append(
            round(
                float(
                    rec["unprotected_expected_utility"]
                    - rec["protected_expected_utility"]
                ),
                2,
            )
        )
        row = [str(i).replace("%", "\\%") for i in row]
        table.append("& ".join(row))

    t = table
    print(
        f"""\midrule 
Rule coverage (25\\%) & {t[0]} \\\\
Rule coverage (50\\%) &{t[1]} \\\\
Rule coverage (75\\%)  & {t[2]}\\\\
Rule coverage (90\\%)  & {t[3]} \\\\
Group coverage (25\\%)  & {t[4]} \\\\
Group coverage (50\\%) & {t[5]} \\\\
Group coverage (75\\%) & {t[6]}\\\\
Group coverage (90\\%) & {t[7]}\\\\
        """
    )


output_path = (
    "/Users/bcyl/FairPrescriptionRules/output/gc_single_female/gc_coverage_analysis"
)
print_gc_cvrg(output_path)


# %%
print_table("/Users/bcyl/FairPrescriptionRules/output/so_gdp/so_full")
# %%


def print_so_fair(path):
    variants = os.listdir(path)
    variants.sort()
    i = 0
    fields = [
        " # rules ",
        " coverage ",
        " coverage pro ",
        " exp utility ",
        " exp utility non-pro",
        "exp utility pro ",
        "unfairness",
    ]
    table = []

    for v in variants:
        i += 1
        row = []

        df = pd.read_csv(f"{path}/{v}/experiment_results_greedy.csv")
        if len(df) == 0:
            row.append(0)
            row.append("0%")
            row.append("0%")
            row.append(0)
            row.append(0)
            row.append(0)
            row.append(0)
        else:
            k = min(20, max(df["k"]))

            rec = df.loc[k - 1]

            row.append(k)
            row.append(rec["coverage_rate"])
            row.append(rec["protected_coverage_rate"])
            row.append(round(float(rec["expected_utility"]), 2))
            row.append(round(float(rec["unprotected_expected_utility"]), 2))
            row.append(round(float(rec["protected_expected_utility"]), 2))
            row.append(
                round(
                    float(
                        rec["unprotected_expected_utility"]
                        - rec["protected_expected_utility"]
                    ),
                    2,
                )
            )
        row = [str(i).replace("%", "\\%") for i in row]
        table.append("& ".join(row))

    t = table
    print(
        f"""\midrule 
Group SP (0) &  {t[0]} \\\\
Group SP (2500)  &{t[1]} \\\\
Group SP (5000)  & {t[2]}\\\\
Group SP (20000) & {t[3]} \\\\
Individual SP (0) & {t[4]} \\\\
Individual SP (2500) & {t[5]} \\\\
Individual SP (5000)  & {t[6]}\\\\
Individual SP (20000) & {t[7]}\\\\
        """
    )


output_path = "/Users/bcyl/FairPrescriptionRules/output/so_gdp/so_fairness_analysis"

print_so_fair(output_path)


# %%


def print_gc_fair(path):
    variants = os.listdir(path)
    variants.sort()
    i = 0
    fields = [
        " # rules ",
        " coverage ",
        " coverage pro ",
        " exp utility ",
        " exp utility non-pro",
        "exp utility pro ",
        "unfairness",
    ]
    table = []

    for v in variants:
        i += 1
        row = []

        df = pd.read_csv(f"{path}/{v}/experiment_results_greedy.csv")
        if len(df) == 0 or not df.loc[min(20, max(df["k"])) - 1]["fairness_met"]:
            row.append(0)
            row.append("0%")
            row.append("0%")
            row.append(0)
            row.append(0)
            row.append(0)
            row.append(0)
        else:
            k = min(20, max(df["k"]))

            rec = df.loc[k - 1]

            row.append(k)
            row.append(rec["coverage_rate"])
            row.append(rec["protected_coverage_rate"])
            row.append(round(float(rec["expected_utility"]), 2))
            row.append(round(float(rec["unprotected_expected_utility"]), 2))
            row.append(round(float(rec["protected_expected_utility"]), 2))
            row.append(
                round(
                    float(
                        rec["unprotected_expected_utility"]
                        - rec["protected_expected_utility"]
                    ),
                    2,
                )
            )
        row = [str(i).replace("%", "\\%") for i in row]
        table.append("& ".join(row))

    t = table
    print(
        f"""\midrule 
Group BGL (0.10) &  {t[0]} \\\\
Group BGL (0.25)  &{t[1]} \\\\
Group BGL (0.30)  & {t[2]}\\\\
Group BGL (0.35) & {t[3]} \\\\
Individual BGL (0.10) & {t[4]} \\\\
Individual BGL (0.25) & {t[5]} \\\\
Individual BGL (0.30)  & {t[6]}\\\\
Individual BGL (0.35) & {t[7]}\\\\
        """
    )


output_path = "/Users/bcyl/FairPrescriptionRules/output/gc_fairness_analysis"

print_gc_fair(output_path)


# %%
font = {"size": 10}
import matplotlib

matplotlib.rc("font", **font)
matplotlib.rc("axes", titlesize=16)


def execTimeVsSize(path):
    variants = []
    names = []
    for f in os.listdir(path + "/so_full"):
        if "greedy" in f:
            variants.append(f)
    variants.sort()
    for f in variants:
        tokens = f.split("+")
        cvrg_fair = []
        for t in tokens:
            if "cov" in t:
                cvrg = t.split("_")

                cvrg_fair.append(f"{cvrg[0]} cov")
            if "sp" in t:
                fair = t.split("_")
                cvrg_fair.append(f"{fair[0].replace('individual', 'indi')} fair ")

        if cvrg_fair:
            name = f"{' & '.join(cvrg_fair)}"
        else:
            name = "No constraint"
        names.append(name)
    dirs = os.listdir(path)
    size_variants = {}
    for d in dirs:
        if "qua" in d:
            size_variants[1] = d
        if "half" in d:
            size_variants[2] = d
        if "tri" in d:
            size_variants[3] = d
        if "full" in d:
            size_variants[4] = d
    f = plt.figure(figsize=(10, 5))
    sizes = ["25%", "50%", "75%", "100%"]
    i = 0
    markers = ["o", "v", "s", "x", "d", "p", ">", "<", "^"]
    plt.ylabel("Time (Seconds)")
    plt.xlabel("Proportion of the Stack Overflow dataset")
    for v in variants:
        exec_time = [0] * 4
        for s, m in size_variants.items():
            df = pd.read_csv(f"{path}/{m}/{v}/experiment_results_greedy.csv")
            exec_time[s - 1] = df["execution_time"].iloc[-1]
        print(v, exec_time)
        plt.plot(sizes, exec_time, marker=markers[i], label=names[i])
        i += 1

    plt.legend(loc="best")
    f.savefig("time_v_size.pdf", bbox_inches="tight")


# Define output path
# Path should include full, triquarter, half, and quarter sized dateset
output_path = "/Users/bcyl/FairPrescriptionRules/output/so_gdp_new"
# Analyze effect of dataset size on execution time
execTimeVsSize(output_path)
# %%
font = {"size": 17}
import matplotlib
from matplotlib import pyplot as plt
import pandas as pd

matplotlib.rc("font", **font)


def execTimeVsNumAttr(path, sizes, im, p):
    fnames = os.listdir(path)
    cnames = ["No constraint", "Group fairness", "Indi fairness"]
    # row: time_attr x
    # col: fair_var y
    df = [[] for _ in range(len(cnames))]
    for f in fnames:
        idx = 0
        if "group" in f:
            idx = 1
        elif "ind" in f:
            idx = 2
        df[idx].append(f)
    for i in range(len(cnames)):
        df[i].sort()
    markers = ["o", "v", "s", "^", "+", "p"]

    for x in range(len(df)):
        exec_time = []
        for y in range(len(sizes)):
            data = pd.read_csv(f"{path}/{df[x][y]}/experiment_results_greedy.csv")
            if len(df) == 0:
                exec_time.append(0)
            else:
                exec_time.append(data["execution_time"].iloc[-1])
        p.plot(sizes, exec_time, marker=markers[x], label=cnames[x])
        # p.bar(sizes[1:], exec_time[1:], label=names[i])
    p.legend(loc="best")
    # f.savefig("time_v_num_attr_bar.pdf", bbox_inches='tight')


fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(12, 6), tight_layout=False)
ax1.set_ylabel("Total Execution Time (Seconds)")
fig.supxlabel("Number of attributes")

output_path = "/Users/bcyl/FairPrescriptionRules/output/so_gdp/so_attrM_analysis"
sizes = [
    "10 imm\n2 mut",
    "10 imm\n3 mut",
    "10 imm\n4 mut",
    "10 imm\n5 mut",
    "10 imm\n6 mut",
]
execTimeVsNumAttr(output_path, sizes, "mutable", ax1)

output_path = "/Users/bcyl/FairPrescriptionRules/output/so_gdp/so_attrI_analysis"
sizes = [
    "5 imm\n6 mut",
    "6 imm\n6 mut",
    "7 imm\n6 mut",
    "8 imm\n6 mut",
    "9 imm\n6 mut",
    "10 imm\n6 mut",
]
execTimeVsNumAttr(output_path, sizes, "immutable", ax2)
fig.savefig(f"time_v_num_attr_line.pdf", bbox_inches="tight")

# Analyze effect of dataset size on execution time

# %%
