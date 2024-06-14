
# Mediation Analysis (Python Workflow)

This project includes two Python scripts, `main.py` and `MediationAnalyzer.py`, designed to perform mediation analysis on given datasets. The project uses various libraries such as `numpy`, `pandas`, `scipy`, `statsmodels`, and `semopy`.

## Files

- `main.py`: This script serves as the entry point for the project. It sets up the environment, loads data, and initiates the mediation analysis.
- `MediationAnalyzer.py`: This script contains the core logic for performing mediation analysis, including data processing and statistical computations.
- `UPDATED_DATA.csv`: The dataset required for the workflow.

## Installation

### Prerequisites

- Python 3.6 or higher
- pip (Python package installer)
- virtualenv (optional but recommended)

### Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/atakolday/mediation_analysis.git
   cd mediation_analysis/Python_workflow
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv env
   ```

3. Activate the virtual environment:

   - On Windows:

     ```bash
     .\env\Scripts\activate
     ```

   - On macOS/Linux:

     ```bash
     source env/bin/activate
     ```

4. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Analysis

1. Ensure you have your data files ready and placed in the appropriate directory.
2. Run the `main.py` script:

   ```bash
   python main.py [argument]
   ```

### Arguments

The `main.py` script accepts the following arguments:

- `--test`: Run one mediator variable for output.
- `--testall`: Run all mediator variables individually.
- `--pc-all`: Check percent mediated by all variable.
- `--pc`: Check percent mediated by one variable.
- `--bs`: Bootstrap sample general info.
- `--bsplot`: Plot a histogram based on bootstrap results and save as a .png file.
- `-m`: Specify the model type (default: "md"). Choices: ["sm", "r", "md"].

   #### Example Use:
   - Checking the percent mediation of one variable:
   ```bash
   python main.py --pc Total_PANESS
   ```

   - Generating bootstrap histograms and saving them in a new directory `Model_Histograms`:
   ```bash
   python main.py --bsplot
   ```

### Script Details

- `main.py`: This script handles the following tasks:
  - Setting up the environment
  - Loading and preprocessing data
  - Initiating the mediation analysis using the functions defined in `MediationAnalyzer.py`

- `MediationAnalyzer.py`: This script includes functions and classes to:
  - Perform data processing
  - Conduct mediation analysis using various statistical methods
  - Output the results

## Dependencies

The project requires the following Python packages:

- `numpy`
- `pandas`
- `scipy`
- `statsmodels`
- `semopy`
- `matplotlib`
- `argparse`
- `termcolor`
- `tqdm`

These packages are listed in the `requirements.txt` file and can be installed using the provided installation steps.
