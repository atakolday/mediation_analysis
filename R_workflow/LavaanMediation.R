library(lavaan)
library(glue)
library(corrr)
library(FactoMineR)
library(ggcorrplot)

data <- read.csv('UPDATED_DATA.csv')

variables <- list('Brf_P_Init_T',
                  'Brf_P_PlnOrg_T',
                  'ADHD_Inattention_Composite_Score',
                  'WISC_PSI_Processing_Speed_Index',
                  'WMem_Composite_Score',
                  'WISC4_PRI_Perceptual_Reasoning_Index',
                  'WISC_FSIQ',
                  'PKT_Total_Correct',
                  'Social_Motivation_Composite_Score',
                  'SRS_P_2_Restricted_Interest_and_Repetitive_Behavior_T_Score',
                  'Motor_Composite_Score')

all_vars = c(variables, list('PrimaryDx_ASD'))

mediation_analysis <- function(m, x='PrimaryDx_ASD', y='PercentAccuracy_GTI', 
                               dt=data, n=2000) {

  # Define the SEM model
  sem_model = glue('
    # Path a 
    {m} ~ a*{x}
  
    # Path b 
    {y} ~ b*{m}
    
    # Path c
    {y} ~ c*{x}
    
    # Define the indirect, direct, and total effects
    indirect := a*b
    direct := c
    total := a*b + c
    ')
  
  # Fit the model
  model_sem = suppressWarnings(sem(sem_model, data=dt, se='boot', bootstrap=n))
  
  return(model_sem)
}

# # Output the summary

mediation_percentage <- function(var, model){
  params <- parameterEstimates(model)
  indirect_eff <- params$est[7]
  total_eff <- params$est[9]
  
  if (all(params$pvalue[7:9] < 0.001)) {
    sig = '***' 
    } else if (all(params$pvalue[7:9] < 0.01)) {
    sig = '**' 
    } else if (all(params$pvalue[7:9] < 0.05)) {
    sig = '*'
    } else {
    sig = ''
    }
  percent <- glue(">>> {sig}{var} - Percent Effect: {round(100 * indirect_eff / total_eff, 2)}%{sig}")
  indirect_sig <- glue("  - Indirect effect: p={round(params$pvalue[7], 3)}")
  direct_sig <- glue("  - Direct effect: p={round(params$pvalue[8], 3)}")
  total_sig <- glue("  - Total effect: p={round(params$pvalue[9], 3)}")
  
  print(percent)
  print(indirect_sig)
  print(direct_sig)
  print(total_sig)
  cat("\n")
}

calculate_mediation <- function(x='PrimaryDx_ASD', y='PercentAccuracy_GTI', 
                                vars=variables, dt=data, n=2000) {
    for (var in vars) {
      m <- mediation_analysis(var, x=x, y=y, dt=dt, n=n)
      mediation_percentage(var, m)
    }
}

calculate_mediation(vars=variables, dt=data)


############################################################

calculate_mediation(y='Gesture_Residuals', vars=c('Total_PANESS'), dt=data_hfa)
calculate_mediation(vars=c('WMem_PC'), dt=data_hfa)

model <- mediation_analysis('WISC_FSIQ', dt=data_hfa)
params <- parameterEstimates(model)
params

############################################################

mabc_md <- mediation_analysis('mABC_2_Manual_Dexterity_Component_Standard_Score')
params <- parameterEstimates(mabc_md)
indirect_sig <- glue("  - Indirect effect: p={round(params$pvalue[7], 3)}")
direct_sig <- glue("  - Direct effect: p={round(params$pvalue[8], 3)}")
total_sig <- glue("  - Total effect: p={round(params$pvalue[9], 3)}")

### ABAS COMMUNICATION ###
calculate_mediation(y='ABAS_P_Communication_Scaled', vars=c('PercentAccuracy_GTI', 'PercentAccuracy_GTC'), dt=data_hfa)

### ABAS COMMUNITY USE ###
calculate_mediation(y='ABAS_P_Community_Use_Scaled')

### GTI -> SRS ###
model5_variables <- list('Brf_P_Init_T',
                  'Brf_P_WMem_T',
                  'Brf_P_PlnOrg_T',
                  'ADHD_numeric',
                  'WISC_PSI_Processing_Speed_Index',
                  'WISC_WMI_Working_Memory_Index',
                  'WISC4_PRI_Perceptual_Reasoning_Index',
                  'WISC_FSIQ',
                  'PKT_Total_Correct',
                  'Total_PANESS',
                  'mABC_2_Aiming_and_Catching_Component_Standard_Score',
                  'mABC_2_Balance_Component_Standard_Score',
                  'mABC_2_Manual_Dexterity_Component_Standard_Score',
                  'mABC_2_Total_Test_Score',
                  'mABC_2_Total_Standard_Score',
                  'mABC_2_Total_Percentile_Rank',
                  'PercentAccuracy_GTC')


###########

calculate_mediation(y='mABC_2_Aiming_and_Catching_Component_Standard_Score', vars=c('WISC_PSI_Processing_Speed_Index'), dt=construct_data, n=1000)

calculate_mediation(y='mABC_2_Balance_Component_Standard_Score', vars=c('WISC_PSI_Processing_Speed_Index'), dt=construct_data, n=1000)

calculate_mediation(y='mABC_2_Manual_Dexterity_Component_Standard_Score', vars=c('WISC_PSI_Processing_Speed_Index'), dt=construct_data, n=1000)
