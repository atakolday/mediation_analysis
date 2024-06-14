library(effsize)
library(glue)

data <- read.csv('UPDATED_DATA.csv')

group1 <- subset(data, PrimaryDx_ASD == 1)
group2 <- subset(data, PrimaryDx_ASD == 0)


tasks <- list('Brf_P_Init_T',
                  'Brf_P_WMem_T',
                  'Brf_P_PlnOrg_T',
                  'WISC_PSI_Processing_Speed_Index',
                  'WISC_WMI_Working_Memory_Index',
                  'WISC4_PRI_Perceptual_Reasoning_Index',
                  'WISC_FSIQ',
                  'PKT_Total_Correct',
                  'SRS_Social_Awareness_T_Score',
                  'SRS_Social_Motivation_T_Score',
                  'SRS_P_2_Restricted_Interest_and_Repetitive_Behavior_T_Score',
                  'Total_PANESS',
                  'mABC_2_Aiming_and_Catching_Component_Standard_Score',
                  'mABC_2_Balance_Component_Standard_Score',
                  'mABC_2_Manual_Dexterity_Component_Standard_Score',
                  'PercentAccuracy_GTC',
                  'PercentAccuracy_GTI')

construct <- list('Brf_P_Init_T',
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

for (var in construct){
  asd <- na.omit(group1[var])[,1]
  non_asd <- na.omit(group2[var])[,1]
  d <- cohen.d(asd, non_asd)
  print(glue("{var} --> d = {round(d$estimate, 3)}"))
}
