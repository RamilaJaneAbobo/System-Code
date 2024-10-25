import numpy as np
import pandas as pd

#Extracting Raw Data 
def load_data(file_path):
    return pd.read_csv(file_path)

# Identify and preprocess columns into Identifiers, Quasi-Identifiers, and Sensitive Attributes
def preprocess_data(df, identifiers, quasi_identifiers, sensitive_attributes):
    # Drop rows with missing values (optional based on the use-case)
    df_clean = df.dropna()

    # Separate the columns based on their role
    id_data = df_clean[identifiers]
    qi_data = df_clean[quasi_identifiers]
    sensitive_data = df_clean[sensitive_attributes]
    
    # Combine all the data into one DataFrame
    combined_data = pd.concat([id_data, qi_data, sensitive_data], axis=1)
    
    return combined_data

# Example usage 
if __name__ == "__main__":
    
    file_path = 'data.csv'

    # Load the data
    df = load_data(file_path)
    
    # Define the columns
    identifiers = ['NAME', 'ID']  # Example of identifiers
    quasi_identifiers = ['AGE', 'GENDER', 'ZIP CODE']  # Example of quasi-identifiers
    sensitive_attributes = ['DISEASE', 'SALARY']  # Example of sensitive attributes

     # Preprocess the data
    processed_data = preprocess_data(df, identifiers, quasi_identifiers, sensitive_attributes)
    
    # Output the processed data
    print("Processed Data with All Attributes:\n", processed_data)