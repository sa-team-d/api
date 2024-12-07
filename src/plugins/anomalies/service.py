import joblib
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import train_test_split, ParameterGrid
from sklearn.metrics import precision_score, recall_score, f1_score
from scipy.stats import ks_2samp
import pandas as pd
from datetime import timedelta
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
import warnings

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