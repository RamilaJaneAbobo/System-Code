import numpy as np
import pandas as pd
from collections import Counter

# Dictionary to store the original ID mappings for unmasking purposes
id_map = {}
name_map = {}

# Load and Preprocess Data
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
        unique_diseases = sensitive_data_masked['Disease'].unique()
        disease_mapping = {disease: f"Condition-{i+1}" for i, disease in enumerate(unique_diseases)}
        sensitive_data_masked['Disease'] = sensitive_data_masked['Disease'].map(disease_mapping)
    return sensitive_data_masked

def mask_id(original_id):
    masked_id = '***-**-' + str(original_id)[-4:]
    id_map[masked_id] = original_id
    return masked_id

def mask_name(original_name):
    masked_name = 'Person-' + str(hash(original_name) % 10000)
    name_map[masked_name] = original_name
    return masked_name

# Unmask data
def unmask_identifiers(masked_data):
    unmasked_data = masked_data.copy()
    if 'ID' in unmasked_data.columns:
        unmasked_data['ID'] = unmasked_data['ID'].apply(lambda x: id_map.get(x, x))
    if 'NAME' in unmasked_data.columns:
        unmasked_data['NAME'] = unmasked_data['NAME'].apply(lambda x: name_map.get(x, x))
    return unmasked_data

# Enforce l-diversity
def enforce_l_diversity(df, quasi_identifiers, sensitive_attribute, l):
    partitions = []
    df_sorted = df.sort_values(by=quasi_identifiers)
    current_partition = pd.DataFrame(columns=df.columns)

    for _, row in df_sorted.iterrows():
        current_partition = pd.concat([current_partition, pd.DataFrame([row])])
        
        # Check if partition satisfies l-diversity
        if is_l_diverse(current_partition, sensitive_attribute, l):
            partitions.append(current_partition)
            current_partition = pd.DataFrame(columns=df.columns)
    
    # Combine remaining rows if final partition doesn't satisfy l-diversity
    if not current_partition.empty:
        if len(partitions) > 0:
            partitions[-1] = pd.concat([partitions[-1], current_partition])
        else:
            partitions.append(current_partition)

    return partitions

# Check l-diversity for each partition
def is_l_diverse(partition, sensitive_attr, l):
    counts = Counter(partition[sensitive_attr])
    return len([count for count in counts.values() if count >= 1]) >= l

# Anonymize Data with l-diversity
def anonymize_data(id_data, qi_data, sensitive_data, l):
    qi_generalized = generalize_data(qi_data)
    sensitive_suppressed = suppress_data(sensitive_data)
    id_masked = mask_identifiers(id_data)
    sensitive_masked = mask_disease(sensitive_suppressed)
    combined_data = pd.concat([qi_generalized, sensitive_masked], axis=1)
    
    partitions = enforce_l_diversity(combined_data, list(qi_generalized.columns), 'DISEASE', l)

    anonymized_data = pd.concat([id_masked] + partitions, axis=1)
    return anonymized_data

# Example Usage
if __name__ == "__main__":
    file_path = 'data.csv'
    df = load_data(file_path)
    
    identifiers = ['NAME', 'ID']
    quasi_identifiers = ['AGE', 'GENDER', 'ZIP CODE']
    sensitive_attributes = ['DISEASE', 'SALARY']

    id_data, qi_data, sensitive_data = preprocess_data(df, identifiers, quasi_identifiers, sensitive_attributes)
    anonymized_data = anonymize_data(id_data, qi_data, sensitive_data, l=2)
    
    print("Anonymized Data:\n", anonymized_data)

    unmasked_data = unmask_identifiers(anonymized_data)
    print("\nUnmasked Data:\n", unmasked_data)
