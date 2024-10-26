import numpy as np
import pandas as pd

# Dictionary to store the original ID mappings for unmasking purposes

id_map = {}
name_map = {}

# Data Processing Code

def load_data(file_path):
    return pd.read_csv(file_path)

def preprocess_data(df, identifiers, quasi_identifiers, sensitive_attributes):
    df_clean = df.dropna()
    id_data = df_clean[identifiers]
    qi_data = df_clean[quasi_identifiers]
    sensitive_data = df_clean[sensitive_attributes]
    return id_data, qi_data, sensitive_data

# Generalization for Quasi-Identifiers (QI)

def generalize_data(qi_data):
    qi_generalized = qi_data.copy()
    if 'AGE' in qi_generalized.columns:
        qi_generalized['AGE'] = pd.cut(qi_generalized['AGE'], 
                                       bins=[0, 18, 30, 40, 50, 60, 100], 
                                       labels=['0-19', '20-29', '30-39', '40-49', '50-60', '60+'])
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
    if 'ID' in masked_id_data.columns:
        masked_id_data['ID'] = masked_id_data['ID'].apply(lambda x: mask_id(x))
    if 'NAME' in masked_id_data.columns:
        masked_id_data['NAME'] = masked_id_data['NAME'].apply(lambda x: mask_name(x))
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

def mask_id(original_id):
    masked_id = '***-**-' + str(original_id)[-4:]
    id_map[masked_id] = original_id  # Store the mapping
    return masked_id

def mask_name(original_name):
    masked_name = 'Person-' + str(hash(original_name) % 10000)
    name_map[masked_name] = original_name  # Store the mapping
    return masked_name

# Function to unmask data using the stored mappings

def unmask_identifiers(masked_data):
    unmasked_data = masked_data.copy()
    if 'ID' in unmasked_data.columns:
        unmasked_data['ID'] = unmasked_data['ID'].apply(lambda x: id_map.get(x, x))
    if 'NAME' in unmasked_data.columns:
        unmasked_data['NAME'] = unmasked_data['NAME'].apply(lambda x: name_map.get(x, x))
    return unmasked_data

# Enforce k-anonymity

def enforce_k_anonymity(qi_data, k):
    qi_anonymized = qi_data.copy()
    unique_counts = qi_anonymized.groupby(list(qi_anonymized.columns)).size()

    # Loop to generalize quasi-identifiers until k-anonymity is achieved
    while (unique_counts < k).any():
        for col in qi_anonymized.columns:
            # Apply further generalization to columns that don't meet k-anonymity
            if col == 'AGE':
                # Generalize Age by widening the ranges
                qi_anonymized['AGE'] = pd.cut(qi_anonymized['AGE'].cat.codes,
                                              bins=[-1, 1, 3, 5, qi_anonymized['AGE'].cat.codes.max()],
                                              labels=['0-30', '31-50', '51+'])
            elif col == 'ZIP CODE':
                # Generalize ZIP Code by reducing precision further
                qi_anonymized['ZIP CODE'] = qi_anonymized['ZIP CODE'].apply(lambda x: x[:2] + 'XX')
        
        # Recalculate unique combinations and check if k-anonymity is satisfied
        unique_counts = qi_anonymized.groupby(list(qi_anonymized.columns)).size()

    return qi_anonymized

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


# Example Usage

if __name__ == "__main__":
    
    file_path = 'data.csv'
    df = load_data(file_path)
    
    identifiers = ['NAME', 'ID']
    quasi_identifiers = ['AGE', 'GENDER', 'ZIP CODE']
    sensitive_attributes = ['DISEASE', 'SALARY']

    id_data, qi_data, sensitive_data = preprocess_data(df, identifiers, quasi_identifiers, sensitive_attributes)
    anonymized_data = anonymize_data(id_data, qi_data, sensitive_data, k=3)
    
    print("Anonymized Data:\n", anonymized_data)
    
    # Unmask the data
    unmasked_data = unmask_identifiers(anonymized_data)
    print("\nUnmasked Data:\n", unmasked_data)



