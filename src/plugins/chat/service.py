from collections import defaultdict
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split, ParameterGrid
from sklearn.metrics import precision_score, recall_score, f1_score
from scipy.stats import ks_2samp
import pandas as pd
from datetime import timedelta
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import warnings
from statsmodels.tsa.arima.model import ARIMA
import os
import warnings

warnings.filterwarnings("ignore")

CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")

import pandas as pd
def data_fetch(features,):
    """
    Fetches data for the specified KPIs (features) and returns a DataFrame containing
    only the specified features along with 'time' and 'asset_id'.

    Returns:
    pd.DataFrame: A DataFrame containing 'time', 'asset_id', and the specified features.
    """
    # Load the data
    df = pd.read_csv("dataset/smart_app_data.csv")
    # Check if the required columns are present in the dataset
    if 'average_cycle_time' in features:
        required_columns= ['time', 'asset_id', 'kpi', 'avg']
    else :
        required_columns = ['time', 'asset_id', 'kpi', 'sum']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"The dataset must contain the following columns: {required_columns}")

    # Filter for the specified features in the 'kpi' column
    filtered_df = df[df['kpi'].isin(features)]

    # Pivot the data so that each KPI becomes a column, preserving KPI names
    if 'average_cycle_time' in features:
            pivoted_df = filtered_df.pivot_table(
            index=['time', 'asset_id'],  # Use 'time' and 'machine_id' as the index
            columns='kpi',                # Pivot 'kpi' values into columns
            values='avg',                 # Use 'sum' values as data
            aggfunc='first'               # Handle duplicates by taking the first value
        ).reset_index()


    else:

        pivoted_df = filtered_df.pivot_table(
            index=['time', 'asset_id'],  # Use 'time' and 'machine_id' as the index
            columns='kpi',                # Pivot 'kpi' values into columns
            values='sum',                 # Use 'sum' values as data
            aggfunc='first'               # Handle duplicates by taking the first value
        ).reset_index()

    # Rename columns to preserve KPI names
    pivoted_df.columns.name = None  # Remove the column hierarchy name
    pivoted_df.rename_axis(None, axis=1, inplace=True)


    # pivoted_df.fillna(0, inplace=True)

    return pivoted_df


import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler

def preprocessor(df):
    """
    Accepts a DataFrame and returns the preprocessed DataFrame.

   This function:
    1. Handles missing data using a Linear Regression model.
    2. Normalize data column-wise (KPI-wise).
    3. Perform consistency checking and remove rows where `min > max`.
    4. Adds important features

    Args:
    df (pd.DataFrame): The input DataFrame with columns ['time', 'asset_id', KPIs...].
    """
    # Handlling missing data
    def handle_missing_data(df):
        # Ensure the 'time' column is in datetime format
        df['time'] = pd.to_datetime(df['time'])

        # Handle missing data for each KPI column
        kpi_columns = [col for col in df.columns if col not in ['time', 'asset_id']]
        for kpi in kpi_columns:
            # Prepare training data for the Linear Regression model
            training_data = df.dropna(subset=[kpi])
            if len(training_data) > 1:  # Ensure there is sufficient data for training
                # Convert time to numeric
                X_train = training_data[['time']].apply(lambda x: x.astype('int64') // 10**9)
                y_train = training_data[kpi]

                # Train Linear Regression model
                model = LinearRegression()
                model.fit(X_train, y_train)

                # Predict missing values
                missing_data = df[df[kpi].isnull()]
                if not missing_data.empty:
                    X_missing = missing_data[['time']].apply(lambda x: x.astype('int64') // 10**9)
                    df.loc[missing_data.index, kpi] = model.predict(X_missing)
            else:
                # Fallback: Fill missing values with the mean of the column
                df[kpi].fillna(df[kpi].mean(), inplace=True)
        # print("Missing data imputed.")
        return df

    df = handle_missing_data(df)

    # Normalization of data column-wise (KPI-wise normalization)
    def normalize_kpi_wise(df):
        scaler = MinMaxScaler()
        kpi_columns = [col for col in df.columns if col not in ['time', 'asset_id']]
        df[kpi_columns] = scaler.fit_transform(df[kpi_columns])
        # print("Data normalization complete.")
        return df

    df = normalize_kpi_wise(df)

    # Consistency checking (min > max)
    def consistency_check(data, min_col='min', max_col='max'):
        """
        Checks for consistency in the data where 'min' should not be greater than 'max'.
        Removes rows where this condition is violated.
        It accepts:
        - data (pd.DataFrame): Input DataFrame.
        - min_col (str): Name of the column representing the minimum value.
        - max_col (str): Name of the column representing the maximum value.

        It returns:
        - pd.DataFrame: DataFrame with inconsistent rows removed.
        """
    # Filter out rows where min > max
        consistent_data = data[data[min_col] <= data[max_col]]
        print(f"Removed {len(data) - len(consistent_data)} inconsistent rows where {min_col} > {max_col}.")
        return consistent_data

    return df


    #Feature addition
    #
def feature_engineering(data, value_col, window=7):
    """
    Adds time-based features to the dataset, including rolling mean and expanding mean.

    It accepts :
    - data (pd.DataFrame): Input DataFrame with a time column and a value column.
    - value_col (str): The column for which features will be calculated.
    - window (int): The window size for the rolling mean.

    Returns:
    - pd.DataFrame: DataFrame with new time-based features added.
    """
    # Ensure 'time' column is in datetime format and sorted
    data['time'] = pd.to_datetime(data['time'])
    data = data.sort_values('time')

    # Calculate 7-day rolling mean
    data[f'{value_col}_rolling_mean_{window}'] = data[value_col].rolling(window=window).mean()

    # Calculate expanding mean (cumulative mean)
    data[f'{value_col}_expanding_mean'] = data[value_col].expanding().mean()

    # print(f"Added 7-day rolling mean and expanding mean features for {value_col}.")
    return data

    # Step 2: Normalize data column-wise (KPI-wise normalization)
    def normalize_kpi_wise(df):
        scaler = MinMaxScaler()
        kpi_columns = [col for col in df.columns if col not in ['time', 'asset_id']]
        df[kpi_columns] = scaler.fit_transform(df[kpi_columns])
        # print("Data normalization complete.")
        return df

    df = normalize_kpi_wise(df)

    # Step 3: Consistency checking (  logic for min > max here)
    #---To be included

    return df

# Detect drift in data
def detect_drift(data, kpi_columns, current_date, threshold=1):
    current_month_data = data[(data['time'] >= current_date - pd.DateOffset(months=1)) & (data['time'] < current_date)]
    previous_month_data = data[(data['time'] >= current_date - pd.DateOffset(months=2)) & (data['time'] < current_date - pd.DateOffset(months=1))]

    drift_detected = False
    for column in kpi_columns:
        stat, p_value = ks_2samp(previous_month_data[column], current_month_data[column])
        if p_value < threshold:
            # print(f"Drift detected in {column}: p-value = {p_value:.16f}")
            drift_detected = True

    return drift_detected

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_squared_error
import joblib
import os

def train_cost_kpi_forecasting_model(data, kpi_name, output_path="models/cost_kpi_forecasting_models/", sequence_length=30):
    """
    Train, validate, and save the best LSTM models for cost KPI forecasting for each machine.

    Args:
    - data (pd.DataFrame): Preprocessed and feature-engineered data.
    - kpi_name (str): The name of the KPI to forecast (e.g., 'cost').
    - output_path (str): Directory to save the models and scalers.
    - sequence_length (int): Number of time steps for LSTM input sequences.

    Returns:
    - None: Models and scalers are saved to the specified directory.
    """
    os.makedirs(output_path, exist_ok=True)

    # Prepare a dictionary to store scalers for each machine
    scalers = {}
    target_column = kpi_name
    feature_columns = [kpi_name, f"{kpi_name}_expanding_mean"]

    machines = data['asset_id'].unique()

    for machine in machines:
        print(f"Training and selecting the best LSTM model for Machine: {machine}")

        # Filter data for the current machine
        machine_data = data[data['asset_id'] == machine].copy()
        machine_data = machine_data.dropna(subset=feature_columns)

        # Scale the features and target
        scaler = MinMaxScaler()
        machine_data[feature_columns] = scaler.fit_transform(machine_data[feature_columns])
        scalers[machine] = scaler

        # Create sequences
        def create_sequences(data, sequence_length):
            X, y = [], []
            for i in range(len(data) - sequence_length):
                X.append(data[feature_columns].iloc[i:i + sequence_length].values)
                y.append(data[target_column].iloc[i + sequence_length])
            return np.array(X), np.array(y)

        X, y = create_sequences(machine_data, sequence_length)

        # Split into training and validation sets
        split_index = int(len(X) * 0.8)
        X_train, y_train = X[:split_index], y[:split_index]
        X_val, y_val = X[split_index:], y[split_index:]
        epochs = 20
        batch_sizes = 16

        # Define hyperparameters to test
        lstm_units = [50, 100]
        dropout_rates = [0.2, 0.3]


        best_model = None
        best_score = np.inf
        best_params = None

        # Hyperparameter search
        for units in lstm_units:
            for dropout in dropout_rates:
                        epoch = 20
                        batch_size = 16
                        print(f"Testing LSTM(units={units}, dropout={dropout}, epochs={epoch}, batch_size={batch_size}) for Machine: {machine}")
                        try:
                            # Build the LSTM model
                            model = Sequential([
                                LSTM(units, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2])),
                                Dropout(dropout),
                                Dense(50, activation='relu'),
                                Dense(1)
                            ])
                            model.compile(optimizer='adam', loss='mean_squared_error')

                            # Train the model
                            model.fit(X_train, y_train, epochs=epoch, batch_size=batch_size, validation_data=(X_val, y_val), verbose=0)

                            # Validate the model
                            val_predictions = model.predict(X_val)
                            mse = mean_squared_error(y_val, val_predictions)

                            print(f"LSTM(units={units}, dropout={dropout}, epochs={epoch}, batch_size={batch_size}) - Validation MSE: {mse:.4f}")

                            # Update the best model if this one is better
                            if mse < best_score:
                                best_score = mse
                                best_model = model
                                best_params = (units, dropout, epoch, batch_size)
                        except Exception as e:
                            print(f"Failed with LSTM(units={units}, dropout={dropout}, epochs={epoch}, batch_size={batch_size}): {e}")

        # Save the best model and scaler
        if best_model:
            model_file = os.path.join(output_path, f"{machine}_lstm.h5")
            scaler_file = os.path.join(output_path, f"{machine}_scaler.pkl")
            best_model.save(model_file)
            joblib.dump(scaler, scaler_file)
            print(f"Best model for Machine {machine} (LSTM{best_params}) saved at {model_file} with MSE: {best_score:.4f}")
        else:
            print(f"No valid model found for Machine {machine}.")

import os
import numpy as np
import pandas as pd
import joblib
from tensorflow.keras.models import load_model
from fpdf import FPDF
from collections import defaultdict

def Cost_KPI_Forecasting(
    data_fetch, preprocessor, feature_engineering, detect_drift,
    Name_Id, machine_id_mapping, kpi_name, model_folder="models/cost_kpi_forecasting_models/",
    sequence_length=30, retrain_function=None, drift_threshold=0.05, pdf_output="predictions/forecast_summary.pdf"
):
    """
    Perform cost KPI forecasting for the next 30 days, with drift detection and model retraining.

    Args:
    - data_fetch (function): Function to fetch the data.
    - preprocessor (function): Function to preprocess the data.
    - feature_engineering (function): Function to add engineered features.
    - detect_drift (function): Function to check for drift in the data.
    - Name_Id (dict): Mapping of machine names to their respective IDs.
    - machine_id_mapping (dict): Mapping of machine IDs to their groups.
    - kpi_name (str): The name of the KPI to forecast (e.g., 'cost').
    - model_folder (str): Directory where the models and scalers are saved.
    - sequence_length (int): Number of time steps for LSTM input sequences.
    - retrain_function (function): Function to retrain the model if drift is detected.
    - drift_threshold (float): P-value threshold for drift detection.
    - pdf_output (str): Filename for the output PDF.

    Returns:
    - dict: Machine groups with their average daily cost predictions as values.
    - str: Path to the generated PDF file.
    """
    # Step 1: Fetch and preprocess the data
    data = data_fetch([kpi_name])
    data = preprocessor(data)

    # Step 2: Apply feature engineering
    data = feature_engineering(data, value_col=kpi_name, window=7)
    #train_cost_kpi_forecasting_model(data, kpi_name='cost', output_path="cost_kpi_forecasting_models/", sequence_length=30)


    # Prepare a dictionary for average daily costs grouped by machine group
    group_average_daily_costs = defaultdict(list)

    # Prepare a list for the summary table
    summary_table = []

    # Iterate through each machine for forecasting
    for asset_id in data['asset_id'].unique():
        # Filter the data for the current machine
        machine_data = data[data['asset_id'] == asset_id]
        machine_data = machine_data.dropna(subset=[kpi_name, f"{kpi_name}_expanding_mean"])

        # Detect drift
        current_data = machine_data[[kpi_name]].tail(sequence_length)
        current_date_ = pd.Timestamp('2024-10-09 00:00:00').tz_localize('UTC')

        # Load the model and scaler
        model_file = os.path.join(model_folder, f"{asset_id}_lstm.h5")
        scaler_file = os.path.join(model_folder, f"{asset_id}_scaler.pkl")

        # suppress warnings
        warnings.filterwarnings("ignore")
        model = load_model(model_file)
        scaler = joblib.load(scaler_file)

        # Extract the last sequence for predictions
        sequence_input = machine_data[-sequence_length:][[kpi_name, f"{kpi_name}_expanding_mean"]].values
        sequence_input = scaler.transform(sequence_input)  # Scale the input

        # Future predictions
        future_predictions = []
        for _ in range(30):  # Predict the next 30 days
            sequence_input_reshaped = sequence_input.reshape(1, sequence_input.shape[0], sequence_input.shape[1])
            next_prediction = model.predict(sequence_input_reshaped, verbose=0)[0, 0]
            future_predictions.append(next_prediction)

            # Update the sequence for the next prediction
            next_feature_row = np.zeros(sequence_input.shape[1])
            next_feature_row[0] = next_prediction
            next_feature_row[1] = sequence_input[:, 1].mean()  # Expanding mean
            sequence_input = np.vstack([sequence_input[1:], next_feature_row])

        # Inverse transform the predictions
        future_predictions_rescaled = scaler.inverse_transform(
            np.concatenate((np.array(future_predictions).reshape(-1, 1), np.zeros((30, 1))), axis=1)
        )[:, 0]

        # Aggregate statistics for the summary table
        machine_name = next(
            (name for name, id_ in Name_Id.items() if id_ == asset_id), "Unknown Machine"
        )
        summary_table.append({
            "Machine": machine_name,
            "Average Forecasted Cost": np.mean(future_predictions_rescaled),
            "Minimum Forecasted Cost": np.min(future_predictions_rescaled),
            "Maximum Forecasted Cost": np.max(future_predictions_rescaled),
            "Standard Deviation": np.std(future_predictions_rescaled)
        })

        # Map asset_id to its group and add the average daily cost
        group = next(
            (group for group, ids in machine_id_mapping.items() if asset_id in ids), "Unknown Group"
        )
        group_average_daily_costs[group].append(np.mean(future_predictions_rescaled))

    # Calculate group-wise averages
    group_average_daily_costs = {group: np.mean(costs) for group, costs in group_average_daily_costs.items()}

    # Generate the PDF summary table
    generate_pdf_summary(pd.DataFrame(summary_table), pdf_output)

    # Return the group averages and the PDF path
    return group_average_daily_costs, pdf_output


def generate_pdf_summary(dataframe, output_file="forecast_summary.pdf"):
    """
    Generate a PDF file from the summary table.

    Args:
    - dataframe (pd.DataFrame): The DataFrame containing the summary data.
    - output_file (str): The filename for the PDF file.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Forecast Summary", ln=True, align='C')
    pdf.ln(10)

    # Add column headers
    pdf.set_font("Arial", style="B", size=12)
    for col in dataframe.columns:
        pdf.cell(50, 10, txt=col, border=1, align='C')
    pdf.ln()

    # Add rows
    pdf.set_font("Arial", size=12)
    for _, row in dataframe.iterrows():
        for cell in row:
            pdf.cell(50, 10, txt=str(round(cell, 2) if isinstance(cell, (float, int)) else cell), border=1, align='C')
        pdf.ln()

    pdf.output(output_file)
    print(f"Forecast summary saved as PDF: {output_file}")

import warnings
warnings.filterwarnings("ignore")

def cost_prediction():

   # Machine Name to ID Mapping
    Name_Id = {
        'Large Capacity Cutting Machine 1': 'ast-yhccl1zjue2t',
        'Riveting Machine': 'ast-o8xtn5xa8y87',
        'Medium Capacity Cutting Machine 1': 'ast-ha448od5d6bd',
        'Laser Cutter': 'ast-xpimckaf3dlf',
        'Large Capacity Cutting Machine 2': 'ast-6votor3o4i9l',
        'Medium Capacity Cutting Machine 2': 'ast-5aggxyk5hb36',
        'Testing Machine 1': 'ast-nrd4vl07sffd',
        'Testing Machine 2': 'ast-pu7dfrxjf2ms',
        'Low Capacity Cutting Machine 1': 'ast-6nv7viesiao7',
        'Medium Capacity Cutting Machine 3': 'ast-anxkweo01vv2',
        'Assembly Machine 1': 'ast-pwpbba0ewprp',
        'Laser Welding Machine 1': 'ast-hnsa8phk2nay',
        'Assembly Machine 2': 'ast-upqd50xg79ir',
        'Assembly Machine 3': 'ast-sfio4727eub0',
        'Laser Welding Machine 2': 'ast-206phi0b9v6p',
        'Testing Machine 3': 'ast-06kbod797nnp'
    }
    machine_id_mapping = {
        'Metal Cutting Machines': [
            Name_Id['Large Capacity Cutting Machine 1'],
            Name_Id['Large Capacity Cutting Machine 2'],
            Name_Id['Medium Capacity Cutting Machine 1'],
            Name_Id['Medium Capacity Cutting Machine 2'],
            Name_Id['Medium Capacity Cutting Machine 3'],
            Name_Id['Low Capacity Cutting Machine 1']
        ],
        'Laser Welding Machines': [
            Name_Id['Laser Welding Machine 1'],
            Name_Id['Laser Welding Machine 2']
        ],
        'Assembly Machines': [
            Name_Id['Assembly Machine 1'],
            Name_Id['Assembly Machine 2'],
            Name_Id['Assembly Machine 3']
        ],
        'Testing Machines': [
            Name_Id['Testing Machine 1'],
            Name_Id['Testing Machine 2'],
            Name_Id['Testing Machine 3']
        ],
        'Riveting Machine': [
            Name_Id['Riveting Machine']
        ],
        'Laser Cutter': [
            Name_Id['Laser Cutter']
        ]
    }

    # Execute the forecasting
    group_costs, pdf_path = Cost_KPI_Forecasting(
        data_fetch=data_fetch,
        preprocessor=preprocessor,
        feature_engineering=feature_engineering,
        detect_drift=detect_drift,
        machine_id_mapping=machine_id_mapping,
        Name_Id=Name_Id,
        retrain_function=train_cost_kpi_forecasting_model,
        kpi_name='cost',
        model_folder="models/cost_kpi_forecasting_models/",
        sequence_length=30,
        drift_threshold=0.05
    )

    ''' def Cost_KPI_Forecasting(
        data_fetch, preprocessor, feature_engineering, detect_drift,
        Name_Id, machine_id_mapping, kpi_name, model_folder="models/cost_kpi_forecasting_models/",
        sequence_length=30, retrain_function=None, drift_threshold=0.05, pdf_output="predictions/forecast_summary.pdf"
    ):
    ):'''

    # # Outputs
    # print("Group-wise Average Daily Costs:", group_costs)
    # print("Summary Table PDF Path:", pdf_path)

    return group_costs,pdf_path

import pandas as pd
from io import BytesIO
from datetime import timedelta

# Name_Id mapping for machine names
Name_Id = {
    'Large Capacity Cutting Machine 1': 'ast-yhccl1zjue2t',
    'Riveting Machine': 'ast-o8xtn5xa8y87',
    'Medium Capacity Cutting Machine 1': 'ast-ha448od5d6bd',
    'Laser Cutter': 'ast-xpimckaf3dlf',
    'Large Capacity Cutting Machine 2': 'ast-6votor3o4i9l',
    'Medium Capacity Cutting Machine 2': 'ast-5aggxyk5hb36',
    'Testing Machine 1': 'ast-nrd4vl07sffd',
    'Testing Machine 2': 'ast-pu7dfrxjf2ms',
    'Low Capacity Cutting Machine 1': 'ast-6nv7viesiao7',
    'Medium Capacity Cutting Machine 3': 'ast-anxkweo01vv2',
    'Assembly Machine 1': 'ast-pwpbba0ewprp',
    'Laser Welding Machine 1': 'ast-hnsa8phk2nay',
    'Assembly Machine 2': 'ast-upqd50xg79ir',
    'Assembly Machine 3': 'ast-sfio4727eub0',
    'Laser Welding Machine 2': 'ast-206phi0b9v6p',
    'Testing Machine 3': 'ast-06kbod797nnp'
}

# Invert the Name_Id mapping for quick lookup
Id_Name = {v: k for k, v in Name_Id.items()}

def utilization_analysis():
    """
    Calculate weekly machine utilization rates taking into account 'working_time', 'idle_time', 'offline_time' KPIs.
    For each machine we get the average utilization rate and rank the machines based on their utilization rates.

    Args:
    - data_fetch (function): Function to fetch the data.
    - preprocessor (function): Function to preprocess the data.
    - current_date (pd.Timestamp): The current date for determining the week of interest.

    Returns:
    - DataFrame: A summary of machine utilization rates with machine names and ranks. Grouped by machine names.
    """
    # Step 1: Fetch and preprocess data
    data = data_fetch(['working_time', 'idle_time', 'offline_time'])
    data = preprocessor(data)
    current_date=pd.Timestamp('2024-10-09 00:00:00').tz_localize('UTC')
    # Step 2: Filter data for the last 7 days
    data['time'] = pd.to_datetime(data['time'])
    start_date = current_date - timedelta(days=7)
    weekly_data = data[(data['time'] >= start_date) & (data['time'] < current_date)]

    # Step 3: Calculate Utilization Rate
    weekly_data['utilization_rate'] = (
        weekly_data['working_time'] /
        (weekly_data['working_time'] + weekly_data['idle_time'] + weekly_data['offline_time'] + 1e-6)  # Avoid division by zero
    )

    # Step 4: Calculate average utilization rate for each machine
    utilization_summary = weekly_data.groupby('asset_id')['utilization_rate'].mean().reset_index()
    utilization_summary['Machine Name'] = utilization_summary['asset_id'].map(Id_Name)  # Map asset_id to machine name
    utilization_summary.dropna(subset=['Machine Name'], inplace=True)  # Drop machines without a mapped name
    utilization_summary = utilization_summary[['Machine Name', 'utilization_rate']]

    # Step 5: Rank machines by their average utilization rate
    utilization_summary.columns = ['Machine', 'Average Utilization Rate']
    utilization_summary['Rank'] = utilization_summary['Average Utilization Rate'].rank(
        ascending=False, method='dense').astype(int)
    utilization_summary.sort_values(by='Rank', inplace=True)

    return utilization_summary

import pandas as pd
from io import BytesIO

def energy_efficency_analysis():
    """
    Generate a weekly energy efficiency report based on idle energy ratio for each machine. It use 'consumption_working', 'consumption_idle' KPIS to calculate the idle energy ratio.

    Args:
    - data_fetch (function): Function to fetch the data.
    - preprocessor (function): Function to preprocess the data.
    - machine_id_mapping (dict): Mapping of asset IDs to machine groups.

    Returns:
    - BytesIO: A BytesIO object containing the bar plot of the weekly average idle energy ratio for each machine.
    """
    # Step 1: Fetch and preprocess the data
    data = data_fetch(['consumption_working', 'consumption_idle'])
    data = preprocessor(data)

    machine_id_mapping= Name_Id


    # Filter for the last week
    data['time'] = pd.to_datetime(data['time'])
    current_date = data['time'].max()
    weekly_data = data[data['time'] >= current_date - pd.Timedelta(weeks=1)]

    # Calculate Idle Energy Ratio (Idle vs. Total Consumption)
    data['idle_energy_ratio'] = (
        data['consumption_idle'] /
        (data['consumption_idle'] + data['consumption_working'] + 1e-6)
    )

    # Weekly Average Idle Energy Ratio for each Machine
    efficiency_summary = data.groupby('asset_id')['idle_energy_ratio'].mean().reset_index()
    efficiency_summary.columns = ['Machine', 'Average Idle Energy Ratio']

    # Map asset IDs to machine names
    efficiency_summary['Machine'] = efficiency_summary['Machine'].map({
        v: k for k, v in Name_Id.items()
    })

    # Replace NaN values with "Unknown Machine" (in case of unmapped IDs)
    efficiency_summary['Machine'] = efficiency_summary['Machine'].fillna("Unknown Machine")

    # Rank machines by their Average Idle Energy Ratio
    efficiency_summary.sort_values(by='Average Idle Energy Ratio', inplace=True)

    return efficiency_summary

