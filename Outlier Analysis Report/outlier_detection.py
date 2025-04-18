# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Set a nice style for our plots
plt.style.use('seaborn-v0_8-whitegrid')

# Create a directory for our plots if it doesn't exist
import os
if not os.path.exists('plots'):
    os.makedirs('plots')

# Load the cleaned dataset
print("Loading the cleaned dataset...")
try:
    # Use the cleaned dataset from the previous task
    file_path = "Student Depression Dataset - Cleaned.csv"
    df = pd.read_csv(file_path)
    print("Dataset loaded successfully!")
    
    # Display basic information
    print(f"\nDataset shape: {df.shape} (rows, columns)")
    print("\nSample of the dataset:")
    print(df.head())
    
    # Brief summary of numerical columns
    print("\nNumerical data summary:")
    print(df.describe())
    
except FileNotFoundError:
    print("Error: Cleaned file not found. Make sure the CSV file is in the correct location.")
except Exception as e:
    print(f"An error occurred: {e}")

# Split columns into numerical and categorical
numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

print(f"\nNumerical columns for outlier detection: {numerical_cols}")
print(f"\nCategorical columns (no outlier detection needed): {categorical_cols}")

# Function to detect outliers using Z-score method
def detect_outliers_zscore(df, column, threshold=3):
    """
    Detect outliers using Z-score method.
    Returns a boolean series where True indicates an outlier.
    """
    z_scores = np.abs(stats.zscore(df[column].dropna()))
    return pd.Series(z_scores > threshold, index=df[column].dropna().index)

# Function to detect outliers using IQR method
def detect_outliers_iqr(df, column, k=1.5):
    """
    Detect outliers using Interquartile Range (IQR) method.
    Returns a boolean series where True indicates an outlier.
    """
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - k * iqr
    upper_bound = q3 + k * iqr
    
    return ((df[column] < lower_bound) | (df[column] > upper_bound))

# Function to create boxplots
def create_boxplot(df, column, outliers_mask=None):
    """
    Create a boxplot for a numerical column.
    If outliers_mask is provided, highlight the outliers.
    """
    plt.figure(figsize=(10, 6))
    
    # If outliers mask is provided, plot outliers in a different color
    if outliers_mask is not None:
        # Create a copy of the dataframe
        temp_df = df.copy()
        # Add outlier flag
        temp_df['outlier'] = False
        temp_df.loc[outliers_mask.index[outliers_mask], 'outlier'] = True
        
        # Plot boxplot
        sns.boxplot(x=column, data=temp_df)
        
        # Overlay points, with outliers in red
        sns.stripplot(x=column, y='outlier', data=temp_df, 
                     hue='outlier', palette={False: 'gray', True: 'red'},
                     size=4, alpha=0.6)
    else:
        # Simple boxplot
        sns.boxplot(x=column, data=df)
    
    plt.title(f'Boxplot of {column}')
    plt.tight_layout()
    plt.savefig(f'plots/boxplot_{column.replace("/", "_")}.png')
    plt.close()

# Function to create histograms
def create_histogram(df, column, outliers_mask=None):
    """
    Create a histogram for a numerical column.
    If outliers_mask is provided, highlight the outliers.
    """
    plt.figure(figsize=(10, 6))
    
    # Plot histogram
    if outliers_mask is not None:
        # Plot normal values
        sns.histplot(df.loc[~outliers_mask, column], color='blue', alpha=0.5, label='Normal Values')
        # Plot outliers
        sns.histplot(df.loc[outliers_mask, column], color='red', alpha=0.5, label='Outliers')
        plt.legend()
    else:
        sns.histplot(df[column], kde=True)
    
    plt.title(f'Histogram of {column}')
    plt.xlabel(column)
    plt.tight_layout()
    plt.savefig(f'plots/histogram_{column.replace("/", "_")}.png')
    plt.close()

print("\n--- OUTLIER DETECTION ---")

# Dictionary to store outlier information
outlier_info = {}

# Create a copy of the original dataframe to track changes
df_original = df.copy()

# Analyze each numerical column
for col in numerical_cols:
    print(f"\nAnalyzing {col} for outliers:")
    
    # Skip ID column
    if col.lower() == 'id':
        print(f"  - Skipping {col} as it's an identifier")
        continue
    
    # Skip categorical columns encoded as numbers
    if col.lower() == 'depression' and df[col].nunique() < 10:
        print(f"  - Skipping {col} as it appears to be a categorical target variable")
        continue
    
    # Summary statistics
    print(f"  - Min: {df[col].min()}, Max: {df[col].max()}, Mean: {df[col].mean():.2f}, Median: {df[col].median():.2f}")
    
    # Detect outliers using Z-score
    z_outliers = detect_outliers_zscore(df, col)
    z_count = z_outliers.sum()
    
    # Detect outliers using IQR
    iqr_outliers = detect_outliers_iqr(df, col)
    iqr_count = iqr_outliers.sum()
    
    print(f"  - Z-score method: {z_count} outliers detected ({z_count/len(df)*100:.2f}%)")
    print(f"  - IQR method: {iqr_count} outliers detected ({iqr_count/len(df)*100:.2f}%)")
    
    # Choose method based on which one is more conservative 
    # (unless the difference is extreme)
    if 0 < z_count <= iqr_count * 0.5:  # Z-score is much more conservative
        outliers = z_outliers
        method = "Z-score"
        print(f"  - Selected Z-score method as it's more conservative")
    else:  # Default to IQR as it's generally more robust
        outliers = iqr_outliers
        method = "IQR"
        print(f"  - Selected IQR method")
    
    # Create visualizations
    create_boxplot(df, col, outliers)
    create_histogram(df, col, outliers)
    
    # Store outlier information
    outlier_info[col] = {
        'count': outliers.sum(),
        'percentage': outliers.sum() / len(df) * 100,
        'method': method,
        'indices': df.index[outliers].tolist()
    }
    
    print(f"  - Boxplot and histogram saved to plots/ directory")

print("\n--- OUTLIER TREATMENT ---")

# Make a copy of the original dataframe for treatment
df_treated = df.copy()

# Dictionary to track treatment methods
treatment_info = {}

# Function to recommend outlier treatment
def recommend_treatment(col, outlier_percentage):
    """
    Recommend treatment method based on column name and outlier percentage.
    """
    if outlier_percentage <= 1:
        return "remove"  # Remove rows if very few outliers
    elif outlier_percentage <= 5:
        if "pressure" in col.lower() or "satisfaction" in col.lower() or "stress" in col.lower():
            return "cap"  # Cap for subjective ratings
        else:
            return "remove"  # Remove for objective measures with moderate outliers
    else:
        return "cap"  # Cap if many outliers to preserve data

# Treat outliers in each column
for col, info in outlier_info.items():
    if info['count'] == 0:
        print(f"No outliers to treat in {col}")
        continue
    
    outlier_percentage = info['percentage']
    print(f"\nTreating outliers in {col} ({info['count']} outliers, {outlier_percentage:.2f}%):")
    
    # Get recommended treatment
    treatment = recommend_treatment(col, outlier_percentage)
    
    if treatment == "remove":
        # Count rows before removal
        before_count = len(df_treated)
        
        # Remove rows with outliers in this column
        df_treated = df_treated[~df_treated.index.isin(info['indices'])]
        
        # Count rows after removal
        removed_count = before_count - len(df_treated)
        
        print(f"  - Removed {removed_count} rows with outliers")
        treatment_info[col] = {
            'method': 'remove',
            'count': removed_count
        }
    
    elif treatment == "cap":
        # Calculate capping values
        q1 = df_treated[col].quantile(0.25)
        q3 = df_treated[col].quantile(0.75)
        iqr = q3 - q1
        lower_bound = max(q1 - 1.5 * iqr, 0)  # Ensure non-negative for appropriate columns
        upper_bound = q3 + 1.5 * iqr
        
        # Count before capping
        lower_count = (df_treated[col] < lower_bound).sum()
        upper_count = (df_treated[col] > upper_bound).sum()
        
        # Apply capping
        df_treated.loc[df_treated[col] < lower_bound, col] = lower_bound
        df_treated.loc[df_treated[col] > upper_bound, col] = upper_bound
        
        print(f"  - Capped {lower_count} values at lower bound ({lower_bound:.2f})")
        print(f"  - Capped {upper_count} values at upper bound ({upper_bound:.2f})")
        
        treatment_info[col] = {
            'method': 'cap',
            'lower_count': lower_count,
            'upper_count': upper_count,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound
        }

# Check how many rows were removed in total
rows_removed = len(df) - len(df_treated)
print(f"\nTotal rows removed: {rows_removed} ({rows_removed/len(df)*100:.2f}% of original data)")

print("\n--- VERIFICATION AND SAVING ---")

# Verify the dataset still has enough data for analysis
print(f"Original dataset shape: {df.shape}")
print(f"Treated dataset shape: {df_treated.shape}")

# Check if we have enough data
if len(df_treated) < 0.9 * len(df):
    print("Warning: More than 10% of data was removed during outlier treatment.")
    print("Consider using more conservative outlier detection or treatment methods.")

# Compare statistical properties before and after
print("\nComparison of key statistics before and after treatment:")
for col in numerical_cols:
    if col in outlier_info and outlier_info[col]['count'] > 0:
        print(f"\n{col}:")
        print(f"  Before - Mean: {df[col].mean():.2f}, Std: {df[col].std():.2f}, Min: {df[col].min():.2f}, Max: {df[col].max():.2f}")
        print(f"  After  - Mean: {df_treated[col].mean():.2f}, Std: {df_treated[col].std():.2f}, Min: {df_treated[col].min():.2f}, Max: {df_treated[col].max():.2f}")

# Save the treated dataset
treated_file_path = "Student Depression Dataset - Outlier Treated.csv"
df_treated.to_csv(treated_file_path, index=False)
print(f"\nOutlier treated dataset saved to: {treated_file_path}")

print("\n--- DOCUMENTATION ---")

# Create documentation file
doc_file = "Outlier_Detection_Documentation.md"
with open(doc_file, "w") as f:
    f.write("# Outlier Detection and Treatment Documentation\n\n")
    f.write(f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n\n")
    
    f.write("## Dataset Information\n")
    f.write(f"- Original Dataset: Student Depression Dataset - Cleaned.csv\n")
    f.write(f"- Number of Rows (Before Treatment): {len(df)}\n")
    f.write(f"- Number of Rows (After Treatment): {len(df_treated)}\n")
    f.write(f"- Number of Columns: {len(df.columns)}\n\n")
    
    f.write("## Outlier Detection Summary\n")
    for col, info in outlier_info.items():
        if info['count'] > 0:
            f.write(f"- {col}: {info['count']} outliers ({info['percentage']:.2f}%) detected using {info['method']} method\n")
    
    f.write("\n## Outlier Treatment Methods\n")
    for col, info in treatment_info.items():
        if info['method'] == 'remove':
            f.write(f"- {col}: Removed {info['count']} rows with outlier values\n")
        elif info['method'] == 'cap':
            f.write(f"- {col}: Capped {info['lower_count']} values at lower bound ({info['lower_bound']:.2f}) and {info['upper_count']} values at upper bound ({info['upper_bound']:.2f})\n")
    
    f.write(f"\n## Total Impact\n")
    f.write(f"- Total rows removed: {rows_removed} ({rows_removed/len(df)*100:.2f}% of original data)\n")
    
    f.write("\n## Statistical Impact\n")
    for col in numerical_cols:
        if col in outlier_info and outlier_info[col]['count'] > 0:
            f.write(f"\n### {col}:\n")
            f.write(f"- Before Treatment: Mean = {df[col].mean():.2f}, Std = {df[col].std():.2f}, Min = {df[col].min():.2f}, Max = {df[col].max():.2f}\n")
            f.write(f"- After Treatment: Mean = {df_treated[col].mean():.2f}, Std = {df_treated[col].std():.2f}, Min = {df_treated[col].min():.2f}, Max = {df_treated[col].max():.2f}\n")
    
    f.write("\n## Additional Notes\n")
    f.write("- Generated visualizations of outliers using boxplots and histograms\n")
    f.write("- Treatment methods were selected based on percentage of outliers and domain context\n")
    f.write("- Special attention was given to preserve data integrity where possible\n")
    
    f.write("\n## Output Files\n")
    f.write(f"- Treated Dataset: {treated_file_path}\n")
    f.write("- Visualizations: Saved in the 'plots' folder\n")

print(f"Documentation saved to: {doc_file}")

print("\n--- OUTLIER DETECTION AND TREATMENT COMPLETED SUCCESSFULLY ---")

# Create a detailed analysis report
report_file = "Outlier_Analysis_Report.md"
with open(report_file, "w") as f:
    f.write("# Outlier Analysis Report: Student Depression Dataset\n\n")
    f.write(f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n\n")
    
    f.write("## Executive Summary\n\n")
    f.write(f"This report details the outlier detection and treatment process for the Student Depression Dataset. ")
    f.write(f"Out of {len(df)} records, {sum([info['count'] for _, info in outlier_info.items()])} outliers were identified across various features. ")
    f.write(f"After treatment, {rows_removed} records were removed, and several values were capped to appropriate bounds. ")
    f.write(f"The treated dataset maintains {len(df_treated)} records ({len(df_treated)/len(df)*100:.2f}% of original data) for subsequent analysis.\n\n")
    
    f.write("## Outlier Detection Methodology\n\n")
    f.write("Two standard methods were employed for outlier detection:\n\n")
    f.write("1. **Z-score Method**: Identifies data points that are more than 3 standard deviations away from the mean\n")
    f.write("2. **Interquartile Range (IQR) Method**: Identifies data points that fall below Q1 - 1.5×IQR or above Q3 + 1.5×IQR\n\n")
    f.write("For each feature, the most appropriate method was selected based on data distribution and context.\n\n")
    
    f.write("## Detailed Findings\n\n")
    
    for col, info in outlier_info.items():
        if info['count'] > 0:
            f.write(f"### {col}\n\n")
            f.write(f"- **Detection Method**: {info['method']}\n")
            f.write(f"- **Outliers Found**: {info['count']} ({info['percentage']:.2f}% of data)\n")
            
            if col in treatment_info:
                t_info = treatment_info[col]
                if t_info['method'] == 'remove':
                    f.write(f"- **Treatment**: Removed {t_info['count']} rows\n")
                elif t_info['method'] == 'cap':
                    f.write(f"- **Treatment**: Capped values to range [{t_info['lower_bound']:.2f}, {t_info['upper_bound']:.2f}]\n")
                    f.write(f"  - {t_info['lower_count']} values capped at lower bound\n")
                    f.write(f"  - {t_info['upper_count']} values capped at upper bound\n")
            
            f.write(f"- **Impact on Statistics**:\n")
            f.write(f"  - Before: Mean = {df[col].mean():.2f}, Std = {df[col].std():.2f}, Min = {df[col].min():.2f}, Max = {df[col].max():.2f}\n")
            f.write(f"  - After: Mean = {df_treated[col].mean():.2f}, Std = {df_treated[col].std():.2f}, Min = {df_treated[col].min():.2f}, Max = {df_treated[col].max():.2f}\n\n")
            
            f.write(f"![Boxplot of {col}](plots/boxplot_{col.replace('/', '_')}.png)\n\n")
            f.write(f"![Histogram of {col}](plots/histogram_{col.replace('/', '_')}.png)\n\n")
    
    f.write("## Recommendations\n\n")
    f.write("Based on the outlier analysis, we recommend:\n\n")
    f.write("1. Using the treated dataset for all subsequent analyses\n")
    f.write("2. Paying special attention to features with high outlier percentages in modeling\n")
    f.write("3. Consider the potential impact of outlier treatment on model interpretation\n")
    
    f.write("\n## Next Steps\n\n")
    f.write("1. Proceed with feature engineering (T7)\n")
    f.write("2. Verify overall data quality (T8)\n")
    f.write("3. Begin exploratory data analysis (T9, T10, T11)\n")

print(f"Analysis report saved to: {report_file}")

