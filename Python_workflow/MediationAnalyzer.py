import numpy as np
from scipy.stats import pearsonr
from semopy import Model
import pandas as pd
from time import sleep
import statsmodels.api as sm
from statsmodels.stats.mediation import Mediation
from tqdm import tqdm

data = pd.read_csv('UPDATED_DATA.csv')
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

class Correlations:
    data = data.copy()
    # asd_data = asd_data.copy()

    def __init__(self, IV: str, DV: list, dt=data):
        self.X = IV
        self.Y = DV
        self.data = dt.loc[:, self.Y + [self.X]]
        self.data.dropna(inplace=True)

    def descriptive_statistics(self):
        print(f"\nCorrelations for {self.X} (n = {len(self.data.index)}):")
        for var in self.Y:
            corr = pearsonr(self.data[self.X], self.data[var])
            if corr[1] < 0.001:
                sig = '***'
            elif corr[1] < 0.01:
                sig = '**'
            elif corr[1] < 0.05:
                sig = '*'
            else:
                sig = ''
            print(f">>> {self.X} vs. {var}: r = {round(corr[0], 3)}, p = {round(corr[1], 3)}{sig}")


class MediationAnalyzer:
    data = data.copy()
    # asd_data = asd_data.copy()

    def __init__(self, M, M2=None, M3=None, X='PrimaryDx_ASD', Y='PercentAccuracy_GTI', sample=data):
        self.M = M
        self.M2 = M2
        self.M3 = M3
        self.X = X
        self.Y = Y
        self.data = sample[[self.X, self.Y, self.M]]

        # to be revised later when there are multiple mediators
        self.bootstrap_pval = None
        self.bootstrap_estimates = None

    def __repr__(self):
        return f"Analysis for {self.M} (IV: {self.X}, DV: {self.Y})"

    @classmethod
    def get_data(cls):
        return cls.data

    def clean_data(self, info=True):
        df = self.data.copy()
        df.dropna(inplace=True)

        if info:
            sleep(1)
            print(f">>> {self.data.shape[0] - df.shape[0]} rows dropped for invalid results on {self.M}.")
            sleep(1)
            print(f">>> New number of subjects for this analysis: {df.shape[0]}")
            print("_________________")

        check_list = [df[var].isnull().any() for var in [self.M, self.M2, self.M3, self.X, self.Y] if var is not None]

        if sum(check_list) == 0:
            sleep(1)
            self.data = df

        else:
            print(f'Uh oh! Number of valid values for {df[self.M]}: {df[self.M].shape[0]}')
            print(f'Expected: {df[self.X].shape[0]}.')
            sleep(1)
            print('Go back and fix the problem!')

    def corr(self):
        corr1 = pearsonr(self.data[self.X], self.data[self.M])
        corr2 = pearsonr(self.data[self.M], self.data[self.Y])
        print('')
        print("Correlations:")
        print(f">>> {self.X} vs. {self.M}: r = {round(corr1[0], 3)}, p = {round(corr1[1], 3)}")
        print(f">>> {self.M} vs. {self.Y}: r = {round(corr2[0], 3)}, p = {round(corr2[1], 3)}")
        print('')

    def descriptive_stats(self):
        # ASD Sample Statistics
        asd = self.data.loc[self.data[self.X] == 1]
        m_asd, std_asd = np.mean(asd[self.M]), np.std(asd[self.M], ddof=1)
        n_asd = len(asd.index)

        # Non-ASD Sample Statistics
        non_asd = self.data.loc[self.data[self.X] == 0]
        m_non_asd, std_non_asd = np.mean(non_asd[self.M]), np.std(non_asd[self.M], ddof=1)
        n_non_asd = len(non_asd.index)

        def cohens_d():
            nonlocal n_asd, n_non_asd
            dof = n_asd + n_non_asd - 2
            return (m_asd - m_non_asd) / np.sqrt(
                ((n_asd - 1) * std_asd ** 2 + (n_non_asd - 1) * std_non_asd ** 2) / dof)

        for group in [asd, non_asd]:
            print(f"{self.M} Scores for {[k for k, v in locals().items() if v is group][0].upper()} "
                  f"(n = {len(group.index)}):")
            mean, sd = np.mean(group[self.M]), np.std(group[self.M])
            print(f">>> Mean = {round(mean, 3)}")
            print(f">>> SD = {round(sd, 3)}")
            print('')
        print(f">>> Cohen's d = {round(cohens_d(), 3)}\n")

    def analyze(self, model, bootstrap=False):
        if model == 'sm':
            # Outcome model: Outcome ~ Mediator + Predictor
            outcome_model = sm.OLS.from_formula(f"{self.Y} ~ {self.M} + {self.X}", data=self.data)

            # Mediator model: Mediator ~ Predictor
            mediator_model = sm.OLS.from_formula(f"{self.M} ~ {self.X}", data=self.data)

            # Mediation: includes both the mediator and outcome model
            med = Mediation(outcome_model, mediator_model, f"{self.X}", f"{self.M}")

            # Arguments include number of bootstrap samples and confidence intervals
            med_result = med.fit(n_rep=2000, method='bootstrap')

            # Print the result
            print(med_result.summary())

        elif model == 'r':
            model_spec = f"""
                        # Direct effects
                        {self.Y} ~ c*{self.X}
                        {self.M} ~ a*{self.X}

                        # Indirect effects
                        {self.Y} ~ b*{self.M}
                        """

            model = Model(model_spec)
            if bootstrap:
                # np.random.seed(42)
                bootstrap_samples = 2000

                # A list to store the results of each bootstrap sample
                bootstrap_estimates = []
                bootstrap_pvals = []
                print(f'>>> Running boostrap for {self.M}:')
                sleep(1)
                print('')
                for _ in tqdm(range(bootstrap_samples), desc=' > Getting bootstrapped results...  '):
                    # Generate a bootstrap sample (a sample with replacement from your data)
                    bootstrap_data = self.data.sample(n=len(self.data), replace=True)

                    # Fit the SEM to the bootstrap sample
                    model.fit(bootstrap_data)

                    # Store the parameter estimates
                    results = model.inspect()
                    # if all(results.Estimate[0:3]) < 100:
                    bootstrap_estimates.append(results.Estimate[0:3])  # 0: A Path, 1: C Path, 2: B Path
                    bootstrap_pvals.append(results['p-value'][0:3])  # 0: A Path, 1: C Path, 2: B Path

                self.bootstrap_pval = bootstrap_pvals
                self.bootstrap_estimates = bootstrap_estimates

            else:
                model.fit(self.data)

                return model.inspect()  # use with variable assignment to access values

        elif model == 'md':
            model_spec = f"""
                        # Direct effects
                        {self.Y} ~ c*{self.X}
                        {self.M} ~ a*{self.X}

                        # Indirect effects
                        {self.Y} ~ b*{self.M}
                    """

            model = Model(model_spec)
            model.fit(self.data)

            # DataFrame to access results for markdown
            model_df = model.inspect()

            for i in range(3):
                sleep(1)
                print('')
                print(f"{model_df.iloc[i]['rval']} --> {model_df.iloc[i]['lval']}")
                print(
                    f"Estimate: {round(model_df.iloc[i]['Estimate'], 3)} (p = {round(model_df.iloc[i]['p-value'], 3)})")
            print('______________')
            print('')

    @staticmethod
    def percent_mediated(df):
        if 'Estimate' in df.columns:
            vals = df.Estimate
            a, b, c_ = vals.iloc[0], vals.iloc[2], vals.iloc[1]
            indirect_effect = a * b
            total_effect = c_ + a * b
            percent_eff = abs(indirect_effect / total_effect) * 100
            return f">>> {round(percent_eff, 3)}% of effect mediated by {(df.lval[0]).replace('_', ' ')}"

        else:
            for col in df.columns:
                vals = df[col]
                a, b, c_ = vals.iloc[0], vals.iloc[1], vals.iloc[2]
                indirect_effect = a * b
                total_effect = c_ + a * b
                percent_eff = abs(indirect_effect / total_effect) * 100
                print(f"- At {col}, {round(percent_eff, 3)}% of effect mediated.")

    @staticmethod
    def mediation_percentage(s):
        a, b, c_ = s[0], s[2], s[1]
        indirect_effect = a * b
        total_effect = c_ + a * b
        percent_eff = abs(indirect_effect / total_effect)

        return percent_eff
