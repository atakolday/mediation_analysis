import argparse
from math import floor, ceil
from time import sleep
from os import getcwd, system, makedirs

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from termcolor import colored

from MediationAnalyzer import MediationAnalyzer

# Argument Parser
parser = argparse.ArgumentParser(description="Run mediation analysis.")
parser.add_argument("--test", action="store_true", help="Run one mediator variable for output.")
parser.add_argument("--testall", action="store_true", help="Run all mediator variables individually.")
parser.add_argument("--pc-all", action="store_true", help="Check percent mediated by all variable.")
parser.add_argument("--pc", action="store", help="Check percent mediated by one variable.")
parser.add_argument("--bs", action="store_true", help="Bootstrap sample general info")
parser.add_argument("--bsplot", action="store_true", help="Plot a histogram based on bootstrap results and save .png")
parser.add_argument("-m", action="store", default="md", choices=["sm", "r", "md"],
                    help="Which model to use for running mediation analysis: sm (Stats Models), r (Semopy Inspect), "
                         "md (Semopy Markdown). (DEFAULT: Semopy Markdown)")
parser.add_argument("-d", action="store", default="data", choices=["data", "ados"],
                    help="Choose data source: data (full data), ados (ados data). (DEFAULT: full data)")

parser.add_argument("--stats", action="store_true")

args = parser.parse_args()

if __name__ == "__main__":
    print('')
    print('Running all checks...')
    print('')
    sleep(1)

    variables = ['Brf_P_Init_T',
                 'Brf_P_PlnOrg_T',
                 'ADHD_Inattention_Composite_Score',
                 'WISC_PSI_Processing_Speed_Index',
                 'WMem_Composite_Score',
                 'WISC4_PRI_Perceptual_Reasoning_Index',
                 'WISC_FSIQ',
                 'PKT_Total_Correct',
                 'Social_Motivation_Composite_Score',
                 'SRS_P_2_Restricted_Interest_and_Repetitive_Behavior_T_Score',
                 'Motor_Composite_Score']

    if args.d == 'ados':
        sample = MediationAnalyzer.data
    else:
        sample = MediationAnalyzer.data

    if args.test:
        # DataFrame check for variables
        for v in variables:
            try:
                sample[v]
            except KeyError:
                print(f'!!!! {v} does not exist !!!!')
            finally:
                print(f'CLEAR: {v}')
        print('')
        variable = input(
            "Which mediator variable(s) would you like to test? (separate with \", \" if multiple variables) ")
        variableList = variable.split(', ')
        print('')
        for var in variableList:
            m = MediationAnalyzer(var, sample=sample)
            m.clean_data()

            if args.m in ['sm', 'md', 'r']:
                print(f'Results for {var}:')
                m.analyze(model=args.m)
            else:
                model_choice = str(input('Which model would you like to use? [sm, r, md]  '))
                print(f'Results for {var}:')
                m.analyze(model=model_choice)

    if args.testall:
        for v in variables:
            try:
                m = MediationAnalyzer(v, sample=sample)
                print('#' * (len(v) + 8))
                print(f'### {v.upper()} ###')
                print('#' * (len(v) + 8))
                print('')
                m.clean_data()
                print('')
                print(f'Results for {v}:')
                m.analyze(model=args.m)
            except SyntaxError:
                print(f'!!!! SYNTAX ERROR ON {v} !!!!')

    if args.pc_all:
        for v in variables:
            try:
                m = MediationAnalyzer(v, sample=sample)
                m.clean_data(info=False)

                mediation_df = m.analyze(model='r')
                for value in mediation_df['p-value'][0:3]:
                    if value < 0.05:
                        print(colored(
                            f"***{MediationAnalyzer.percent_mediated(mediation_df)} "
                            f"(n = {m.data.shape[0]}, p = {value})***",
                            attrs=['bold']))
                    else:
                        print(f"{MediationAnalyzer.percent_mediated(mediation_df)} "
                              f"(n = {m.data.shape[0]}, p = {value})")
            except SyntaxError:
                print(f'!!!! SYNTAX ERROR ON {v} !!!!')
        print('')

    if args.pc:
        if args.pc is not None:
            var = args.pc

            m = MediationAnalyzer(var, sample=sample)
            m.clean_data(info=False)

            mediation_df = m.analyze(model='r')

            if all(value < 0.05 for value in mediation_df['p-value'][0:3]):
                print(
                    colored(f"***{MediationAnalyzer.percent_mediated(mediation_df)} "
                            f"(Data count: {m.data.shape[0]})***",
                            attrs=['bold']))
            else:
                print(f"{MediationAnalyzer.percent_mediated(mediation_df)} "
                      f"(Data count: {m.data.shape[0]})")
            print('')

        else:
            # DataFrame check for variables
            for v in variables:
                try:
                    sample[v]
                except KeyError:
                    print(f'!!!! {v} does not exist !!!!')
                finally:
                    print(f"CLEAR: {v}")
            print('')
            variable = input(
                "Which mediator variable would you like to test? (separate with \", \" if multiple variables) ")
            variableList = variable.split(', ')
            print('')
            for var in variableList:
                m = MediationAnalyzer(var, sample=sample)
                m.clean_data(info=False)

                mediation_df = m.analyze(model='r')

                if all(value < 0.05 for value in mediation_df['p-value'][0:3]):
                    print(
                        colored(f"***{MediationAnalyzer.percent_mediated(mediation_df)} "
                                f"(Data count: {m.data.shape[0]})***",
                                attrs=['bold']))
                else:
                    print(f"{MediationAnalyzer.percent_mediated(mediation_df)} "
                          f"(Data count: {m.data.shape[0]})")
            print('')

    if args.bs:
        for v in variables:
            try:
                sample[v]
            except KeyError:
                print(f'!!!! {v} does not exist !!!!')
            finally:
                print(f"CLEAR: {v}")
        print('')
        variable = input(
            "Which mediator variable would you like to test? (separate with \", \" if multiple variables) ")
        variableList = variable.split(', ')
        print('')
        for var in variableList:
            m = MediationAnalyzer(var, sample=sample)
            m.clean_data(info=False)

            bootstrap_results = m.analyze(model='r', bootstrap=True)

            # Convert the list of results to a DataFrame
            bootstrap_estimates_df = pd.DataFrame(m.bootstrap_estimates)
            bootstrap_pvals_df = pd.DataFrame(m.bootstrap_pval)

            # Compute the lower and upper bounds of the 95% confidence interval for each parameter
            ci_lower = bootstrap_estimates_df.quantile(0.025)
            ci_upper = bootstrap_estimates_df.quantile(0.975)

            # Combine the lower and upper bounds into a single DataFrame for easy viewing
            ci_df = pd.DataFrame({'Lower Bound': ci_lower, 'Upper Bound': ci_upper}).reindex([0, 2, 1])
            ci_df.set_index(pd.Index(['A Path -->', 'B Path -->', 'C Path -->']), inplace=True)
            print('')
            print(
                f'>> {colored(var.replace("_", " "), attrs=["bold"])} Bootstrapped Regression Estimates:')
            sleep(1)
            print(ci_df)
            print('** 95% confidence interval')
            print('')
            sleep(1)
            print(">> Percentage of bootstrapped p-values within 95% confidence interval:")
            p_sig_prop = (bootstrap_pvals_df < 0.05).mean()

            sleep(1)
            print(f'A Path --> {round(p_sig_prop[0] * 100, 2)}%')
            print(f'B Path --> {round(p_sig_prop[2] * 100, 2)}%')
            print(f'C Path --> {round(p_sig_prop[1] * 100, 2)}%')
            print('')

            print(f'>> {var.replace("_", " ")} Mediation Strength (95% confidence interval):')
            print(f'** Data count: {m.data.shape[0]} **')
            MediationAnalyzer.percent_mediated(ci_df)
            print('')

    if args.bsplot:
        # DataFrame check for variables
        for v in variables:
            try:
                sample[v]
            except KeyError:
                print(f'!!!! {v} does not exist !!!!')
            finally:
                print(f"CLEAR: {v}")
        print('')
        
        global X, Y
        X, Y = "PrimaryDx_ASD", "PercentAccuracy_GTI"

        variable = input(
            ">>> Which mediator variable would you like to test? (separate with \", \" if multiple variables) ")
        if variable == 'all':  # create bootstrapped histograms for all variables
            variableList = [var for var in variables if var not in [X, Y]]
        else:  # create bootstrapped histograms for the desired variable(s)
            variableList = variable.split(', ')
        print('')

        for var in variableList:
            m = MediationAnalyzer(var, X=X, Y=Y, sample=sample)
            m.clean_data(info=False)

            # Initialize bootstrapping
            m.analyze(model='r', bootstrap=True)

            est_lst = []  # list of percent effects from bootstrapped estimates (n=5000)
            for i in range(2000):
                estimate = MediationAnalyzer.mediation_percentage(m.bootstrap_estimates[i])
                est_lst.append(estimate)

            # Setting the strings for p-value information to be written on the text box
            bootstrap_pvals_df = pd.DataFrame(m.bootstrap_pval) * len(variableList) # adjusting for multiple comparisons
            p_sig_prop = (bootstrap_pvals_df < 0.05).mean()
            box_title2 = 'Percentage of Significant\nBootstrapped Estimates**: \n  ** (p < 0.05)'
            p1 = f'- A Path --> {round(p_sig_prop[0] * 100, 2)}%'
            p2 = f'- B Path --> {round(p_sig_prop[2] * 100, 2)}%'
            p3 = f'- C Path --> {round(p_sig_prop[1] * 100, 2)}%'

            info_p = f"{box_title2}\n\n{p1}\n{p2}\n{p3}"  # p-value text box string

            # Set the strings for your information
            box_title1 = "Percent Effect of Mediation: \n"
            l1 = f'- Lower Bound: {round(min(est_lst) * 100, 2)}%'
            l2 = f'- Upper Bound: {round(max(est_lst) * 100, 2)}%'
            l3 = f'- Mean: {round(np.mean(est_lst) * 100, 2)}%'
            l4 = f'- Median: {round(np.median(est_lst) * 100, 2)}%'
            l5 = f'  (SD: ±{round(np.std(est_lst) * 100, 2)})'

            # Define the information string
            info = f"{box_title1}\n\n{l1}\n{l2}\n\n{l3}\n{l4}\n{l5}"  # bounds, mean, and median text box string

            # Creating the plot
            my_series = pd.Series(est_lst) * 100
            ceiling = ceil(max(my_series.values / 10)) * 10  # if max(my_series.values / 10) < 100 else 100
            xlim = (floor(min(my_series.values)), ceiling)
            # xlim = (floor(min(my_series.values)), 300)

            fig, ax = plt.subplots(figsize=(16, 9))

            my_series.plot.hist(bins=15, xlim=xlim, ax=ax,
                                title=f'{m.M.replace("_", " ")} Mediation Effect (%) - {m.X} -> {m.Y}',
                                density=True)

            # Calculate the mean_value and the standard deviation of the regression estimates
            mean_val = np.mean(my_series)
            sd_val = np.std(my_series)

            # Calculate bounds of shaded area
            lower_bound = mean_val - sd_val if mean_val - sd_val >= 0 else 0
            upper_bound = mean_val + sd_val

            # Draw a dashed line on the histogram where the mean value is
            plt.axvline(mean_val, color='red', linestyle='dashed', linewidth=2)

            # Shade the area within one standard deviation of the mean
            plt.axvspan(lower_bound, upper_bound, color='red', alpha=0.2)

            # Set a threshold for 'closeness'
            threshold = 0.2 * (max(est_lst) - min(est_lst))

            # Get the current x-ticks
            current_ticks = ax.get_xticks()

            # Filter out ticks that are too close to the mean or mean ± SD
            filtered_ticks = [tick for tick in current_ticks if not (abs(tick - mean_val) < threshold or
                                                                     abs(tick - (mean_val - sd_val)) < threshold or
                                                                     abs(tick - (mean_val + sd_val)) < threshold)]

            # Add mean and SD ticks
            special_ticks = [mean_val, mean_val - sd_val, mean_val + sd_val]
            final_ticks = sorted(set(filtered_ticks + special_ticks))

            # Set the x-ticks
            ax.set_xticks(final_ticks)

            # Custom labels for the mean and SD ticks
            tick_labels = [f"{tick:.2f}" if tick in special_ticks else f"{tick:.0f}" for tick in final_ticks]
            ax.set_xticklabels(tick_labels)

            # Rotate labels for mean and SD ticks
            for label in ax.get_xticklabels():
                if label.get_text() in [f"{mean_val:.2f}", f"{mean_val - sd_val:.2f}", f"{mean_val + sd_val:.2f}"]:
                    label.set_rotation(45)
                    label.set_color('red')

            # Place text box in bottom right and top right. The coordinates are in figure space.
            plt.figtext(0.75, 0.6, info_p, ha='left', va='top', fontsize=11,
                        bbox=dict(facecolor='none', edgecolor='black'))
            plt.figtext(0.75, 0.85, info, ha='left', va='top', fontsize=11,
                        bbox=dict(facecolor='none', edgecolor='black'))

            sleep(1)
            print('')
            makedirs("Model_Histograms", exist_ok=True)
            print(f">>> Saving histogram for {m.M} to {getcwd()}/Model_Histograms ...")
            sleep(1)
            # Save the plot
            plt.savefig(f'{getcwd()}/Model_Histograms/{m.M} Percent Mediation ({m.X} vs. {m.Y}).png')

            print(f">>> Histogram for {m.M} successfully saved!")
            plt.close()
            print('')
        go_to_path = input("Would you like to view the plot? [y/n]  ")
        if go_to_path == 'y':
            system(f'open {getcwd()}/Model_Histograms')
