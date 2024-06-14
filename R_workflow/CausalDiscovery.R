library(bnlearn)
library(Rgraphviz)
library(igraph)
library(dplyr)
library(mediation)

allVars <- c('PrimaryDx_ASD', 
                'Brf_P_Init_T',
                  'Brf_P_WMem_T',
                  'Brf_P_PlnOrg_T',
                  'ADHD_Inattention_Composite_Score',
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
                  'PercentAccuracy_GTI')

composite_vars <- c('PrimaryDx_ASD',
                    'Brf_P_Init_T',
                    'WMem_Composite_Score',
                    'Brf_P_PlnOrg_T',
                    'ADHD_Inattention_Composite_Score',
                    'WISC_PSI_Processing_Speed_Index',
                    'WISC4_PRI_Perceptual_Reasoning_Index',
                    'WISC_FSIQ',
                    'PKT_Total_Correct',
                    'Social_Motivation_Composite_Score',
                    'SRS_P_2_Restricted_Interest_and_Repetitive_Behavior_T_Score',
                    'Motor_Composite_Score',
                    'PercentAccuracy_GTI')

model_data <- data[composite_vars]
model_all_data <- data[allVars]

model_data$PrimaryDx_ASD <- as.factor(model_data$PrimaryDx_ASD)
model_all_data$PrimaryDx_ASD <- as.factor(model_all_data$PrimaryDx_ASD)

############ FUNCTIONS ############ 

generate_blacklist <- function(data, IV, DV) {
  all_vars <- colnames(data)
  blacklist_to <- cbind(all_vars[all_vars != IV], IV)
  
  blacklist_from <- cbind(DV, all_vars[all_vars != DV])
  
  model_blacklist <- rbind(blacklist_to, blacklist_from)
  
  return(model_blacklist)
}

generate_bn <- function(data, IV, DV, model="hc") {
  model_fn <- match.fun(model)
  blacklist = generate_blacklist(data, IV, DV)
  data <- na.omit(data)
  bn_model <- model_fn(data, blacklist=blacklist)
  return(bn_model)
}

has_indirect_path <- function(graph, from, to) {
  paths <- all_simple_paths(graph, from = from, to = to)
  # Check if there's any path with more than 2 nodes (indicating indirect path)
  any(sapply(paths, length) > 2)
}

prune_redundant_arcs <- function(bn) {
  graph <- as.igraph(bn)
  arcs <- arcs(bn)
  for (i in 1:nrow(arcs)) {
    from <- arcs[i, 1]
    to <- arcs[i, 2]
    # Check for indirect path
    if (has_indirect_path(graph, from, to)) {
      bn <- drop.arc(bn, from, to)
    }
  }
  return(bn)
}

####### 1: ASD --> GTI (ALL VARIABLES) ####### 

model_all_bn <- generate_bn(model_all_data, 'PrimaryDx_ASD', 'PercentAccuracy_GTI', model='tabu')
graphviz.plot(model_all_bn, shape='ellipse', fontsize=12)

pruned_all_bn <- prune_redundant_arcs(model_bn)
graphviz.plot(pruned_all_bn, shape='ellipse', fontsize=12)

####### 2: ASD --> GTI (CONSTRUCT VARIABLES) ####### 

model_bn <- generate_bn(model_data, 'PrimaryDx_ASD', 'PercentAccuracy_GTI', model='tabu')
graphviz.plot(model_bn, shape='ellipse', fontsize=12)

pruned_bn <- prune_redundant_arcs(model_bn)
graphviz.plot(pruned_bn, shape='ellipse', fontsize=12)
