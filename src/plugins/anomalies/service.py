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

CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")

import pandas as pd
def data_fetch(features):
    """
    Fetches data for the specified KPIs (features) and returns a DataFrame containing
    only the specified features along with 'time' and 'asset_id'.

    Args:
    features (list): A list of KPIs (features) to fetch.

    Returns:
    pd.DataFrame: A DataFrame containing 'time', 'asset_id', and the specified features.
    """
    # Load the data
    df = pd.read_csv(CSV_FILE_PATH)

    # Check if the required columns are present in the dataset
    required_columns = ['time', 'asset_id', 'kpi', 'sum']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"The dataset must contain the following columns: {required_columns}")

    # Filter for the specified features in the 'kpi' column
    filtered_df = df[df['kpi'].isin(features)]

    # Pivot the data so that each KPI becomes a column, preserving KPI names
    pivoted_df = filtered_df.pivot_table(
        index=['time', 'asset_id'],  # Use 'time' and 'machine_id' as the index
        columns='kpi',                # Pivot 'kpi' values into columns
        values='sum',                 # Use 'sum' values as data
        aggfunc='first'               # Handle duplicates by taking the first value
    ).reset_index()

    # Rename columns to preserve KPI names
    pivoted_df.columns.name = None  # Remove the column hierarchy name
    pivoted_df.rename_axis(None, axis=1, inplace=True)

    pivoted_df.fillna(0, inplace=True)

    return pivoted_df

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler

def preprocessor(df):
    """
    Accepts a DataFrame and returns the preprocessed DataFrame.

    Steps:
    1. Handle missing data using a Linear Regression model.
    2. Normalize data column-wise (KPI-wise).
    3. Perform consistency checking and remove rows where `min > max`.

    Args:
    df (pd.DataFrame): The input DataFrame with columns ['time', 'asset_id', KPIs...].

    Returns:
    pd.DataFrame: The preprocessed DataFrame.
    """
    # Step 1: Handle missing data
    def handle_missing_data(df):
        # Ensure the 'time' column is in datetime format
        df['time'] = pd.to_datetime(df['time'])

        # Handle missing data for each KPI column
        kpi_columns = [col for col in df.columns if col not in ['time', 'asset_id']]
        for kpi in kpi_columns:
            # Prepare training data for the Linear Regression model
            training_data = df.dropna(subset=[kpi])
            if len(training_data) > 1:  # Ensure there is sufficient data for training
                # Convert time to numeric (e.g., Unix timestamp)
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

# Train the model and save it
def train_and_save_model(data, kpi_columns, model_path, contamination=0.01):
    # Prepare features
    # Encode machine-specific IDs
    # data['asset_id'] = LabelEncoder().fit_transform(data['asset_id'])
    # features = data[kpi_columns]
    features = data[kpi_columns + ['encoded_asset_id']]

    # Train Isolation Forest n_estimators=200, contamination=0.001
    iso_forest = IsolationForest(n_estimators=200, contamination=contamination, random_state=42)
    iso_forest.fit(features)

    # Save the trained model
    joblib.dump(iso_forest, model_path)
    # print(f"Model saved to {model_path}")
    # data['asset_id'] = LabelEncoder().inverse_transform(data['asset_id'])

    return iso_forest

# Load the saved model
def load_model(model_path):
    iso_forest = joblib.load(model_path)
    # print(f"Model loaded from {model_path}")
    return iso_forest

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

# Retrain the model and save it if drift is detected
def retrain_and_save_model(data, kpi_columns, model_path, reference_date, months=6, contamination=0.01):
    # Filter data for the last 6 months
    recent_data = data[data['time'] >= reference_date - pd.DateOffset(months=months)]
    #features = data[kpi_columns + ['encoded_asset_id']]#.columns#recent_data[kpi_columns + ['encoded_asset_id']]

    features = data[kpi_columns + ['encoded_asset_id']]
    # Retrain the model

    iso_forest = IsolationForest(n_estimators=200, contamination=contamination, random_state=42)
    iso_forest.fit(features)

    # Save the retrained model
    joblib.dump({'model': iso_forest, 'kpi_columns': kpi_columns}, model_path)
    # print(f"Retrained model saved to {model_path}")
    return iso_forest

def initialize_label_encoder(data):
    label_encoder = LabelEncoder()
    # Use the instance of LabelEncoder to call fit_transform
    data['encoded_asset_id'] = label_encoder.fit_transform(data['asset_id'])
    return label_encoder

def weekly_anomaly_detection(model, data, kpi_columns, current_date, label_encoder):
    # Filter data for the last 1 week
    weekly_data = data[(data['time'] >= current_date - pd.Timedelta(weeks=1)) & (data['time'] < current_date)]

    # Predict anomalies
    weekly_data['anomaly'] = model.predict(weekly_data[kpi_columns + ['encoded_asset_id']])

    # Decode asset IDs for user-facing results
    weekly_data['decoded_asset_id'] = label_encoder.inverse_transform(weekly_data['encoded_asset_id'])

    # Aggregate results
    anomaly_summary = (
        weekly_data[weekly_data['anomaly'] == -1]
        .groupby('decoded_asset_id')
        .agg(
            number_of_anomalies=('time', 'count'),
            timestamps=('time', lambda x: list(x))
        )
        .reset_index()
    )
    return anomaly_summary

def Energy_Consumption_Anomaly(kpi_columns, model_path, current_date, drift_threshold=0.005):
    """
    Anomaly detection workflow for API integration.

    Args:
    - kpi_columns (list): List of KPIs to process and analyze.
    - model_path (str): Path to save or load the Isolation Forest model.
    - current_date (pd.Timestamp): The current date for drift detection and anomaly processing.
    - drift_threshold (float): The p-value threshold for detecting drift.

    Returns:
    - pd.DataFrame: A summary of anomalies detected (asset_id, number_of_anomalies, timestamps).
    """
    # Step 1: Fetch and preprocess the data
    data = data_fetch(kpi_columns)#
    data = preprocessor(data)
    label_encoder = initialize_label_encoder(data)

    # features = data[kpi_columns + ['encoded_asset_id']]
    # print(features)
    # Step 2: Check for drift and retrain the model if necessary
    drift_detected = detect_drift(data, kpi_columns, current_date, drift_threshold)
    if drift_detected:
        iso_forest = retrain_and_save_model(data, kpi_columns, model_path, reference_date=current_date)
    else:
        iso_forest = load_model(model_path)

    # Step 3: Perform weekly anomaly detection
    anomaly_summary = weekly_anomaly_detection(iso_forest, data, kpi_columns, current_date, label_encoder)



    # Return the anomaly summary
    return anomaly_summary


def analyze_energy_anomalies():
    """
    Analyze anomalies and return total anomalies and grouped anomalies by machine categories.
    Uses the provided Name_Id mapping for grouping machines.

    Returns:
    - total_anomalies (int): Total number of anomalies detected in the week.
    - anomalies_by_group (dict): Dictionary of anomalies grouped by machine category.
    """
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

    # Grouping Machines by Category
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


    model_path = "models/isolation_forest_model_Energy_Consumption_Anomaly.pkl"
    kpi_columns = ['consumption', 'working_time', 'cycles']
    current_date = pd.Timestamp('2024-10-09 00:00:00').tz_localize('UTC')


    anomaly_summary=Energy_Consumption_Anomaly(kpi_columns, model_path, current_date, drift_threshold=0.005)


    # Step 1: Calculate total anomalies
    total_anomalies = anomaly_summary['number_of_anomalies'].sum()

    # Step 2: Calculate anomalies by group
    anomalies_by_group = {}
    for group, machine_ids in machine_id_mapping.items():
        # Filter anomaly_summary for machines in the current group
        group_anomalies = anomaly_summary[anomaly_summary['decoded_asset_id'].isin(machine_ids)]
        anomalies_by_group[group] = group_anomalies['number_of_anomalies'].sum()

    # Return results
    return total_anomalies, anomalies_by_group

def train_downtime_anomaly_model(data, output_path="models/downtime_arima_models/"):
    """
    Train ARIMA models for downtime anomalies and save the models for each machine.

    Args:
    - data (pd.DataFrame): Preprocessed data with columns ['time', 'asset_id', 'offline_time'].
    - output_path (str): Directory to save ARIMA models for each machine.

    Returns:
    - None: Models are saved to the specified directory.
    """
    # Create the output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)

    # Ensure 'time' column is in datetime format
    data['time'] = pd.to_datetime(data['time'])

    # Group by machine
    machines = data['asset_id'].unique()
    # print(f"Training ARIMA model for the Machines: ...")
    for machine in machines:


        # Filter data for the current machine
        machine_data = data[data['asset_id'] == machine]
        machine_grouped = machine_data.set_index('time')['offline_time']  # Set time as index for ARIMA

        # Ensure time is sorted for ARIMA model
        machine_grouped = machine_grouped.sort_index()

        # Fit ARIMA model
        try:
            model = ARIMA(machine_grouped, order=(1, 1, 1))
            model_fit = model.fit()

            # Save the model
            model_file = os.path.join(output_path, f"{machine}_arima.pkl")
            joblib.dump(model_fit, model_file)
            # print(f"Model for Machine {machine} saved at {model_file}")
        except Exception as e:
            print(f"Failed to train ARIMA model for Machine {machine}: {e}")

def detect_downtime_anomalies(data, current_date, model_path="models/downtime_arima_models/", drift_threshold=0.005):
    """
    Detect downtime anomalies for the past week using ARIMA models.

    Args:
    - data (pd.DataFrame): Preprocessed data with 'time', 'asset_id', and 'offline_time'.
    - current_date (pd.Timestamp): Current date for anomaly detection.
    - model_path (str): Directory where ARIMA models are saved.
    - drift_threshold (float): Threshold for drift detection.

    Returns:
    - pd.DataFrame: Summary of anomalies detected for each machine.
    """
    # Ensure 'time' column is in datetime format
    data['time'] = pd.to_datetime(data['time'])

    # Step 1: Check for drift
    drift_detected = detect_drift(data, ['offline_time'], current_date, drift_threshold)
    if drift_detected:
        # print("Drift detected. Retraining models...")
        train_downtime_anomaly_model(data, output_path=model_path)
    else:
        # print("No drift detected. Using existing models.")
         pass

    # Step 2: Group by machine and detect anomalies
    summary_table = []
    for machine in data['asset_id'].unique():
        # Filter data for the current machine
        machine_data = data[data['asset_id'] == machine]
        machine_grouped = machine_data.set_index('time')['offline_time']  # Use 'offline_time'

        # Ensure time is sorted for ARIMA predictions
        machine_grouped = machine_grouped.sort_index()

        # Load the model
        model_file = os.path.join(model_path, f"{machine}_arima.pkl")
        if not os.path.exists(model_file):
            # print(f"Model for Machine {machine} not found. Skipping...")
            continue
        model_fit = joblib.load(model_file)

        # Predict and calculate residuals
        predictions = model_fit.predict(start=0, end=len(machine_grouped) - 1, dynamic=False)
        residuals = machine_grouped - predictions

        # Detect anomalies
        threshold = 6 * residuals.std()
        anomalies = residuals[residuals > threshold]

        # Append results to summary table
        if len(anomalies) > 0:
            summary_table.append({
                'Machine ID': machine,
                'Number of Anomalies': len(anomalies),
                'Timestamps': list(anomalies.index.strftime('%Y-%m-%d'))
            })

    # Return the summary as a DataFrame
    if summary_table:
        return pd.DataFrame(summary_table)
    else:
        # print("No anomalies detected for any machine.")
        return pd.DataFrame(columns=['Machine ID', 'Number of Anomalies', 'Timestamps'])

def analyze_downtime_anomalies():
    """
    Final usage function for downtime anomaly detection.
    Internally calls all the necessary steps and returns the final results.

    Returns:
    - total_anomalies (int): Total anomalies detected across all machines for the week.
    - anomalies_by_group (dict): Dictionary of anomalies grouped by machine categories.
    """
    # Step 1: Fetch the raw data
    kpi_columns = ['offline_time']

    data = data_fetch(kpi_columns)  # Fetching data using the prebuilt function
    # print(data.columns)
    # Step 2: Define the machine name-to-ID mapping
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

    # Step 3: Define current date for usage
    current_date = pd.Timestamp('2024-10-19').tz_localize('UTC')

    # Step 4: Detect anomalies (this function handles preprocessing, drift detection, and retraining)
    anomaly_summary = detect_downtime_anomalies(data, current_date)

    # Step 5: Aggregate results
    if anomaly_summary.empty:
        return 0, {group: 0 for group in machine_id_mapping.keys()}

    # Calculate total anomalies
    total_anomalies = anomaly_summary['Number of Anomalies'].sum()

    # Calculate anomalies by machine group
    anomalies_by_group = {}
    for group, machine_ids in machine_id_mapping.items():
        group_anomalies = anomaly_summary[anomaly_summary['Machine ID'].isin(machine_ids)]
        anomalies_by_group[group] = group_anomalies['Number of Anomalies'].sum()

    # Return results
    return total_anomalies, anomalies_by_group

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

def train_cycle_quality_anomaly_model(data, output_path="models/cycle_quality_models/"):
    """
    Train DBSCAN models for cycle quality anomaly detection and save them.

    Args:
    - data (pd.DataFrame): Preprocessed data with columns ['time', 'asset_id', 'bad_cycles', 'good_cycles'].
    - output_path (str): Directory to save DBSCAN models for each machine.

    Returns:
    - None: Models are saved to the specified directory.
    """
    os.makedirs(output_path, exist_ok=True)

    # Preprocess data
    data['good_to_bad_ratio'] = data['good_cycles'] / (data['bad_cycles'] + 1e-6)  # Avoid division by zero

    # Define ratio threshold for outlier removal
    ratio_threshold = data['good_to_bad_ratio'].quantile(0.98)
    data = data[data['good_to_bad_ratio'] <= ratio_threshold]

    for machine in data['asset_id'].unique():
        # print(f"Training DBSCAN model for Machine: {machine}")

        # Filter data for the current machine
        machine_data = data[data['asset_id'] == machine]

        # Normalize features
        scaler = StandardScaler()
        machine_data[['bad_cycles_scaled', 'ratio_scaled']] = scaler.fit_transform(
            machine_data[['bad_cycles', 'good_to_bad_ratio']]
        )

        # Train DBSCAN
        dbscan = DBSCAN(eps=1.5, min_samples=3)
        dbscan.fit(machine_data[['bad_cycles_scaled', 'ratio_scaled']])

        # Save the model and scaler
        model_file = os.path.join(output_path, f"{machine}_dbscan.pkl")
        scaler_file = os.path.join(output_path, f"{machine}_scaler.pkl")
        joblib.dump(dbscan, model_file)
        joblib.dump(scaler, scaler_file)
        # print(f"Model for Machine {machine} saved at {model_file}")

def detect_cycle_quality_anomalies(data, current_date, model_path="models/cycle_quality_models/", drift_threshold=0.005):
    """
    Detect cycle quality anomalies using DBSCAN models.

    Args:
    - data (pd.DataFrame): Preprocessed data with columns ['time', 'asset_id', 'bad_cycles', 'good_cycles'].
    - current_date (pd.Timestamp): Current date for anomaly detection.
    - model_path (str): Directory where DBSCAN models are saved.
    - drift_threshold (float): Threshold for drift detection.

    Returns:
    - pd.DataFrame: Summary of anomalies detected for each machine.
    """
    os.makedirs(model_path, exist_ok=True)

    # Ensure 'time' column is in datetime format
    data['time'] = pd.to_datetime(data['time'])

    # Preprocess data
    data['good_to_bad_ratio'] = data['good_cycles'] / (data['bad_cycles'] + 1e-6)

    # Check for drift
    drift_detected = detect_drift(data, ['good_to_bad_ratio'], current_date, drift_threshold)
    if drift_detected:
        # print("Drift detected. Retraining models...")
        train_cycle_quality_anomaly_model(data, output_path=model_path)
    else:
        # print("No drift detected. Using existing models.")
        pass
    # Identify anomalies for each machine
    anomalies_summary = []
    for machine in data['asset_id'].unique():
        # Load the model and scaler
        model_file = os.path.join(model_path, f"{machine}_dbscan.pkl")
        scaler_file = os.path.join(model_path, f"{machine}_scaler.pkl")
        if not os.path.exists(model_file) or not os.path.exists(scaler_file):
            # print(f"Model or scaler for Machine {machine} not found. Skipping...")
            continue
        dbscan = joblib.load(model_file)
        scaler = joblib.load(scaler_file)

        # Filter data for the current machine
        machine_data = data[data['asset_id'] == machine]

        # Normalize features
        machine_data[['bad_cycles_scaled', 'ratio_scaled']] = scaler.transform(
            machine_data[['bad_cycles', 'good_to_bad_ratio']]
        )

        # Predict anomalies
        machine_data['cluster'] = dbscan.fit_predict(machine_data[['bad_cycles_scaled', 'ratio_scaled']])
        machine_data['is_anomaly'] = machine_data['cluster'] == -1

        # Summarize anomalies
        anomalies = machine_data[machine_data['is_anomaly']]
        if not anomalies.empty:
            anomalies_summary.append({
                'Machine ID': machine,
                'Number of Anomalies': anomalies['is_anomaly'].sum(),
                'Timestamps': list(anomalies['time'].dt.strftime('%Y-%m-%d'))
            })

    # Return summary as DataFrame
    if anomalies_summary:
        return pd.DataFrame(anomalies_summary)
    else:
        # print("No anomalies detected for any machine.")
        return pd.DataFrame(columns=['Machine ID', 'Number of Anomalies', 'Timestamps'])

def analyze_cycle_quality_anomalies():
    """
    Final usage function for cycle quality anomaly detection.
    Internally calls all necessary steps and returns the final results.

    Returns:
    - total_anomalies (int): Total anomalies detected across all machines for the week.
    - anomalies_by_group (dict): Dictionary of anomalies grouped by machine categories.
    """
    # Step 1: Fetch the raw data
    kpi = ['bad_cycles', 'good_cycles']
    data = data_fetch(kpi)  # Fetch data using the prebuilt function

    # Step 2: Define the machine name-to-ID mapping
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

    # Step 3: Define current date
    current_date = pd.Timestamp('2024-10-19').tz_localize('UTC')

    # Step 4: Detect anomalies (this function handles preprocessing, drift detection, and retraining)
    anomaly_summary = detect_cycle_quality_anomalies(data, current_date)

    # Step 5: Aggregate results
    if anomaly_summary.empty:
        return 0, {group: 0 for group in machine_id_mapping.keys()}

    # Calculate total anomalies
    total_anomalies = anomaly_summary['Number of Anomalies'].sum()

    # Calculate anomalies by machine group
    anomalies_by_group = {}
    for group, machine_ids in machine_id_mapping.items():
        group_anomalies = anomaly_summary[anomaly_summary['Machine ID'].isin(machine_ids)]
        anomalies_by_group[group] = group_anomalies['Number of Anomalies'].sum()

    # Return results
    return total_anomalies, anomalies_by_group
