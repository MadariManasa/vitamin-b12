# check_data.py - Verify your NHANES dataset
import pandas as pd
import os

print("🔍 Checking your NHANES dataset...")
print("=" * 50)

# Check current directory
current_dir = os.getcwd()
print(f"📁 Current directory: {current_dir}")

# List all files
print("\n📂 Files in directory:")
for file in os.listdir('.'):
    if file.endswith(('.csv', '.xlsx', '.xls', '.txt', '.data')):
        print(f"  - {file}")

print("\n" + "=" * 50)

# Try to load the dataset with different possible names
possible_filenames = [
    'Nhanes_cvd_raw.csv',
    'NHANES_cvd_raw.csv',
    'nhanes_cvd_raw.csv',
    'Nhanes.csv',
    'NHANES.csv',
    'nhanes_data.csv',
    'dataset.csv',
    'data.csv'
]

found_file = None
for filename in possible_filenames:
    if os.path.exists(filename):
        found_file = filename
        print(f"✅ Found dataset: {filename}")
        break

if not found_file:
    print("❌ No dataset file found!")
    print("Please make sure your dataset is in this folder.")
    print("Supported formats: .csv, .xlsx, .xls")
    exit()

print("\n" + "=" * 50)
print(f"📊 Analyzing: {found_file}")

try:
    # Try to read based on file extension
    if found_file.endswith('.csv'):
        df = pd.read_csv(found_file)
    elif found_file.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(found_file)
    else:
        # Try CSV first, then other methods
        try:
            df = pd.read_csv(found_file)
        except:
            df = pd.read_table(found_file)  # For .txt, .data files
    
    print(f"✅ Successfully loaded dataset!")
    print(f"   Rows: {len(df):,}")
    print(f"   Columns: {len(df.columns):,}")
    print(f"   File size: {os.path.getsize(found_file):,} bytes")
    
    print("\n" + "=" * 50)
    print("📋 COLUMN NAMES:")
    print("=" * 50)
    
    # Display columns in a readable format
    columns = list(df.columns)
    for i, col in enumerate(columns, 1):
        print(f"{i:3}. {col}")
    
    print("\n" + "=" * 50)
    print("📊 DATA TYPES & SAMPLE VALUES:")
    print("=" * 50)
    
    # Show data types and first few non-null values
    for col in df.columns[:15]:  # Show first 15 columns
        dtype = str(df[col].dtype)
        non_null = df[col].notna().sum()
        
        # Get sample values (non-null)
        sample_vals = []
        for val in df[col].dropna().head(3).values:
            if isinstance(val, (int, float)):
                sample_vals.append(str(val))
            else:
                # Truncate long strings
                sample = str(val)[:30]
                if len(str(val)) > 30:
                    sample += "..."
                sample_vals.append(sample)
        
        print(f"\n{col}:")
        print(f"  Type: {dtype}")
        print(f"  Non-null: {non_null}/{len(df)} ({non_null/len(df)*100:.1f}%)")
        if sample_vals:
            print(f"  Samples: {', '.join(sample_vals)}")
    
    print("\n" + "=" * 50)
    print("🔍 LOOKING FOR B12-RELATED COLUMNS:")
    print("=" * 50)
    
    # Search for B12-related columns
    b12_keywords = ['B12', 'b12', 'B_12', 'VITB12', 'VIT_B12', 'COBALAMIN', 
                   'VITAMIN_B12', 'VITAMIN B12', 'LBDB12', 'LBD_B12']
    
    found_b12_cols = []
    for col in df.columns:
        for keyword in b12_keywords:
            if keyword in str(col).upper():
                found_b12_cols.append(col)
                break
    
    if found_b12_cols:
        print(f"✅ Found {len(found_b12_cols)} B12-related columns:")
        for col in found_b12_cols:
            # Show stats for B12 columns
            unique_vals = df[col].nunique()
            null_count = df[col].isna().sum()
            if df[col].dtype in ['int64', 'float64']:
                min_val = df[col].min()
                max_val = df[col].max()
                mean_val = df[col].mean()
                print(f"  • {col}:")
                print(f"     Type: {df[col].dtype}")
                print(f"     Range: {min_val:.1f} to {max_val:.1f}")
                print(f"     Mean: {mean_val:.1f}")
                print(f"     Null: {null_count} ({null_count/len(df)*100:.1f}%)")
            else:
                print(f"  • {col}: {df[col].dtype}, Unique: {unique_vals}")
    else:
        print("❌ No obvious B12 columns found.")
        print("   We'll need to identify which column contains B12 values.")
    
    print("\n" + "=" * 50)
    print("📈 BASIC STATISTICS:")
    print("=" * 50)
    
    # Show summary for numeric columns
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
    
    if len(numeric_cols) > 0:
        print(f"\nNumeric columns ({len(numeric_cols)}):")
        for col in numeric_cols[:10]:  # First 10 numeric columns
            stats = df[col].describe()
            print(f"\n{col}:")
            print(f"  Count: {stats['count']:.0f}")
            print(f"  Mean:  {stats['mean']:.2f}")
            print(f"  Std:   {stats['std']:.2f}")
            print(f"  Min:   {stats['min']:.2f}")
            print(f"  25%:   {stats['25%']:.2f}")
            print(f"  50%:   {stats['50%']:.2f}")
            print(f"  75%:   {stats['75%']:.2f}")
            print(f"  Max:   {stats['max']:.2f}")
    else:
        print("No numeric columns found.")
    
    print("\n" + "=" * 50)
    print("💾 SAVING COLUMN LIST FOR REFERENCE:")
    print("=" * 50)
    
    # Save column list to file
    with open('dataset_columns.txt', 'w') as f:
        f.write(f"Dataset: {found_file}\n")
        f.write(f"Rows: {len(df)}\n")
        f.write(f"Columns: {len(df.columns)}\n\n")
        f.write("COLUMNS:\n")
        f.write("=" * 50 + "\n")
        for i, col in enumerate(df.columns, 1):
            f.write(f"{i:3}. {col}\n")
    
    print(f"✅ Column list saved to: dataset_columns.txt")
    print("\n" + "=" * 50)
    print("🎯 NEXT STEPS:")
    print("=" * 50)
    print("1. Share the column names with me")
    print("2. Identify which column has B12 values")
    print("3. I'll update dataset_preparation.py to use your real data")
    print("\nRun this command to see first 5 rows:")
    print(f"python -c \"import pandas as pd; df=pd.read_csv('{found_file}'); print(df.head())\"")

except Exception as e:
    print(f"❌ Error loading dataset: {e}")
    print("\nTroubleshooting:")
    print("1. Check file format (CSV, Excel, etc.)")
    print("2. Try opening in Excel to verify format")
    print("3. File might be corrupted or wrong encoding")
    import traceback
    traceback.print_exc()