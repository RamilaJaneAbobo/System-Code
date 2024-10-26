import numpy as np
import pandas as pd

# --- Data Processing Code ---

# Load the raw data from the file
def load_data(file_path):
    return pd.read_csv(file_path)

# Preprocess the data to separate identifiers, quasi-identifiers, and sensitive attributes
def preprocess_data(df, identifiers, quasi_identifiers, sensitive_attributes):
    df_clean = df.dropna()
    id_data = df_clean[identifiers]
    qi_data = df_clean[quasi_identifiers]
    sensitive_data = df_clean[sensitive_attributes]
    return id_data, qi_data, sensitive_data

# --- Data Masking Code ---

# Generalization for Quasi-Identifiers (QI)
def generalize_data(qi_data):
    qi_generalized = qi_data.copy()

    # Generalize Age into ranges
    if 'AGE' in qi_generalized.columns:
        qi_generalized['AGE'] = pd.cut(qi_generalized['AGE'], 
                                       bins=[0, 18, 30, 40, 50, 60, 100], 
                                       labels=['0-19', '20-29', '30-39', '40-49', '50-60', '60+'])

    # Generalize Zipcode by showing only the first 3 digits
    if 'ZIP CODE' in qi_generalized.columns:
        qi_generalized['ZIP CODE'] = qi_generalized['ZIP CODE'].apply(lambda x: str(x)[:3] + 'XX')
    
    return qi_generalized

# Suppression for Sensitive Data
def suppress_data(sensitive_data, suppression_threshold=2):
    sensitive_suppressed = sensitive_data.copy()
    
    for col in sensitive_suppressed.columns:
        value_counts = sensitive_suppressed[col].value_counts()
        to_suppress = value_counts[value_counts < suppression_threshold].index
        sensitive_suppressed[col] = sensitive_suppressed[col].apply(lambda x: 'Suppressed' if x in to_suppress else x)
    
    return sensitive_suppressed

# Data Masking for Identifiers (ID)
def mask_identifiers(id_data):
    masked_id_data = id_data.copy()

    # Mask ID with asterisks
    if 'ID' in masked_id_data.columns:
        masked_id_data['ID'] = masked_id_data['ID'].apply(lambda x: '***-**-' + str(x)[-4:])
    
    # Mask Name with a generic placeholder
    if 'NAME' in masked_id_data.columns:
        masked_id_data['NAME'] = masked_id_data['NAME'].apply(lambda x: 'Person-' + str(hash(x) % 10000))
    
    return masked_id_data

# Data Masking for Disease
def mask_disease(sensitive_data):
    sensitive_data_masked = sensitive_data.copy()
    
    if 'Disease' in sensitive_data_masked.columns:
        # Generate unique labels for each disease
        unique_diseases = sensitive_data_masked['Disease'].unique()
        disease_mapping = {disease: f"Condition-{i+1}" for i, disease in enumerate(unique_diseases)}
        
        # Apply the mapping to mask the Disease column
        sensitive_data_masked['Disease'] = sensitive_data_masked['Disease'].map(disease_mapping)
    
    return sensitive_data_masked

# --- Combined Function to Anonymize Data ---

def anonymize_data(id_data, qi_data, sensitive_data):
    # Step 1: Generalize Quasi-Identifiers
    qi_generalized = generalize_data(qi_data)
    
    # Step 2: Suppress sensitive attributes where necessary
    sensitive_suppressed = suppress_data(sensitive_data)
    
    # Step 3: Mask Identifiers
    id_masked = mask_identifiers(id_data)

     # Step 4: Mask Disease
    sensitive_masked = mask_disease(sensitive_suppressed)
    
    # Combine the data into one anonymized DataFrame
    anonymized_data = pd.concat([id_masked, qi_generalized, sensitive_masked], axis=1)
    
    return anonymized_data

# --- Example Usage ---

if __name__ == "__main__":
    
    # Define the file path
    file_path = 'data.csv'

    # Load the data
    df = load_data(file_path)
    
    # Define the columns for identifiers, quasi-identifiers, and sensitive attributes
    identifiers = ['NAME', 'ID']
    quasi_identifiers = ['AGE', 'GENDER', 'ZIP CODE']
    sensitive_attributes = ['DISEASE', 'SALARY']

    # Step 1: Preprocess the data
    id_data, qi_data, sensitive_data = preprocess_data(df, identifiers, quasi_identifiers, sensitive_attributes)

    # Step 2: Anonymize the data
    anonymized_data = anonymize_data(id_data, qi_data, sensitive_data)
    
    # Step 3: Output the anonymized data
    print("Anonymized Data:\n", anonymized_data)
    
    # Step 4: Unmask the data to get the original values
    unmasked_data = unmask_identifiers(anonymized_data)

    # Step 5: Output the unmasked data
    print("\nUnmasked Data:\n", unmasked_data)
    

