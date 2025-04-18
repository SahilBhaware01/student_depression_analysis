# Import necessary libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# Set a nice style for our plots
plt.style.use('seaborn-v0_8-whitegrid')  # Modern looking plots

# Load the dataset
print("Attempting to load the dataset...")
try:
    # Adjust the path if your file is in a different location
    file_path = "Student Depression Dataset.csv"
    df = pd.read_csv(file_path)
    print("Dataset loaded successfully!")
    
    # Display the first 5 rows
    print("\nFirst 5 rows of the dataset:")
    print(df.head())
    
    # Check the dimensions of the dataset
    print(f"\nDataset shape: {df.shape} (rows, columns)")
    
    # Get basic information about the dataset
    print("\nDataset information:")
    print(df.info())
    
    # Get statistical summary of numerical columns
    print("\nStatistical summary of numerical columns:")
    print(df.describe())
    
    # Check column names and data types
    print("\nColumn names and data types:")
    print(df.dtypes)
    
except FileNotFoundError:
    print("Error: File not found. Make sure the CSV file is in the correct location.")
except Exception as e:
    print(f"An error occurred: {e}")


# Check for missing values
print("\n--- MISSING VALUE ANALYSIS ---")
print("Checking for missing values...")

# Count missing values in each column
missing_values = df.isnull().sum()

# Calculate percentage of missing values
missing_percentage = (missing_values / len(df)) * 100

# Create a dataframe to display the results
missing_df = pd.DataFrame({
    'Missing Values': missing_values,
    'Percentage (%)': missing_percentage
})

# Sort by percentage of missing values, descending
missing_df = missing_df.sort_values('Percentage (%)', ascending=False)

# Display only columns with missing values
missing_cols = missing_df[missing_df['Missing Values'] > 0]
if len(missing_cols) > 0:
    print("\nColumns with missing values:")
    print(missing_cols)
else:
    print("\nNo missing values found in the dataset!")

# Create a directory for our plots if it doesn't exist
import os
if not os.path.exists('plots'):
    os.makedirs('plots')

# If there are missing values, create visualizations
if len(missing_cols) > 0:
    # Create a bar chart of missing values
    plt.figure(figsize=(12, 6))
    missing_cols['Percentage (%)'].plot(kind='bar')
    plt.title('Percentage of Missing Values by Column')
    plt.xlabel('Columns')
    plt.ylabel('Missing Value Percentage')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('plots/missing_values_percentage.png')
    print("Bar chart of missing values saved to 'plots/missing_values_percentage.png'")
    
    # Create a heatmap of missing values if dataset is not too large
    if len(df) <= 1000:  # Only for reasonably sized datasets
        plt.figure(figsize=(12, 8))
        sns.heatmap(df.isnull(), cbar=False, yticklabels=False, cmap='viridis')
        plt.title('Missing Values Heatmap')
        plt.tight_layout()
        plt.savefig('plots/missing_values_heatmap.png')
        print("Heatmap of missing values saved to 'plots/missing_values_heatmap.png'")
    else:
        print("Dataset too large for full heatmap visualization")


print("\n--- HANDLING MISSING VALUES ---")

# Make a copy of the original dataframe for comparison later
df_original = df.copy()

# Split columns into numerical and categorical
numerical_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

print(f"\nNumerical columns: {numerical_cols}")
print(f"\nCategorical columns: {categorical_cols}")

# Handle missing values in numerical columns
print("\nHandling missing values in numerical columns...")
for col in numerical_cols:
    if df[col].isnull().sum() > 0:
        # Check if the distribution is skewed
        skewness = df[col].dropna().skew()
        
        # For skewed distributions, use median
        if abs(skewness) > 1:
            median_value = df[col].median()
            df[col].fillna(median_value, inplace=True)
            print(f"  - {col}: Filled {missing_values[col]} missing values with median ({median_value:.2f}) due to skewed distribution (skewness={skewness:.2f})")
        # For normal distributions, use mean
        else:
            mean_value = df[col].mean()
            df[col].fillna(mean_value, inplace=True)
            print(f"  - {col}: Filled {missing_values[col]} missing values with mean ({mean_value:.2f}) (skewness={skewness:.2f})")

# Handle missing values in categorical columns
print("\nHandling missing values in categorical columns...")
for col in categorical_cols:
    if df[col].isnull().sum() > 0:
        # Get most frequent value
        mode_value = df[col].mode()[0]
        
        # Impute with mode
        df[col].fillna(mode_value, inplace=True)
        print(f"  - {col}: Filled {missing_values[col]} missing values with mode ({mode_value})")

# Special handling for Sleep Duration if needed
if 'Sleep Duration' in df.columns and 'Sleep Duration' in missing_values.index and missing_values['Sleep Duration'] > 0:
    print("\nSpecial handling for Sleep Duration...")
    print("Sample Sleep Duration values:")
    print(df_original['Sleep Duration'].dropna().sample(min(5, len(df_original['Sleep Duration'].dropna()))).tolist())
    
    # For simplicity, we'll use the mode here
    # In a real project, you might need to parse and convert this field
    print("Note: Sleep Duration might need special handling based on its format.")

# Check if there are any remaining missing values
remaining_missing = df.isnull().sum()
remaining_missing_cols = remaining_missing[remaining_missing > 0]

if len(remaining_missing_cols) > 0:
    print("\nWarning: There are still some missing values:")
    print(remaining_missing_cols)
else:
    print("\nSuccess! All missing values have been handled.")

# Save the cleaned dataset
cleaned_file_path = "Student Depression Dataset - Cleaned.csv"
df.to_csv(cleaned_file_path, index=False)
print(f"\nCleaned dataset saved to: {cleaned_file_path}")

print("\n--- VERIFICATION AND DOCUMENTATION ---")

# Create a comparison report
comparison_df = pd.DataFrame({
    'Original_Missing_Count': missing_values,
    'Original_Missing_Percentage': missing_percentage,
    'Remaining_Missing_Count': remaining_missing,
    'Remaining_Missing_Percentage': (remaining_missing / len(df)) * 100
})

# Save the comparison report
comparison_file = "Missing_Values_Report.csv"
comparison_df.to_csv(comparison_file)
print(f"Missing values comparison report saved to: {comparison_file}")

# Document the process
doc_file = "Data_Cleaning_Documentation.md"
with open(doc_file, "w") as f:
    f.write("# Data Cleaning: Missing Values Documentation\n\n")
    f.write(f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}\n\n")
    f.write("## Dataset Information\n")
    f.write(f"- Original Dataset: Student Depression Dataset.csv\n")
    f.write(f"- Number of Rows: {len(df)}\n")
    f.write(f"- Number of Columns: {len(df.columns)}\n\n")
    
    f.write("## Missing Values Summary\n")
    for col in df.columns:
        original_missing = missing_values.get(col, 0)
        if original_missing > 0:
            f.write(f"- {col}: {original_missing} missing values ({missing_percentage.get(col):.2f}%)\n")
    
    f.write("\n## Imputation Methods Used\n")
    for col in numerical_cols:
        if missing_values.get(col, 0) > 0:
            skewness = df_original[col].skew()
            if abs(skewness) > 1:
                f.write(f"- {col}: Imputed with median due to skewed distribution (skewness={skewness:.2f})\n")
            else:
                f.write(f"- {col}: Imputed with mean (skewness={skewness:.2f})\n")
    
    for col in categorical_cols:
        if missing_values.get(col, 0) > 0:
            f.write(f"- {col}: Imputed with mode (most frequent value)\n")
    
    f.write("\n## Additional Notes\n")
    f.write("- Generated visualizations of missing data patterns\n")
    f.write("- Verified all missing values have been handled\n")
    
    f.write("\n## Output Files\n")
    f.write(f"- Cleaned Dataset: {cleaned_file_path}\n")
    f.write(f"- Missing Values Report: {comparison_file}\n")
    f.write("- Visualizations: Saved in the 'plots' folder\n")

print(f"Documentation saved to: {doc_file}")

print("\n--- TASK COMPLETED SUCCESSFULLY ---")