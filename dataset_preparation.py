# dataset_preparation.py - UPDATED TO USE YOUR REAL DATA
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import pickle
import os

def prepare_real_nhanes_dataset():
    """
    Load and prepare your REAL NHANES dataset
    """
    print("📊 Loading REAL NHANES dataset...")
    
    try:
        # Load your REAL dataset
        df = pd.read_csv('Nhanes_cvd_raw.csv')
        
        print(f"✅ Real dataset loaded: {len(df)} samples")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Check basic stats
        print("\n📊 Dataset Statistics:")
        print(f"   Age range: {df['age'].min()} to {df['age'].max()} years")
        print(f"   BMI range: {df['bmi'].min():.1f} to {df['bmi'].max():.1f}")
        print(f"   B12 range: {df['b12_level'].min():.0f} to {df['b12_level'].max():.0f} pg/mL")
        
        # Calculate deficiency rate
        deficiency_rate = df['b12_deficient'].mean()
        print(f"📈 B12 Deficiency rate: {deficiency_rate:.1%}")
        
        # Show distribution
        print(f"📊 Deficiency distribution:")
        print(f"   Normal (0): {len(df[df['b12_deficient'] == 0]):,} samples")
        print(f"   Deficient (1): {len(df[df['b12_deficient'] == 1]):,} samples")
        
        # Check B12 levels by deficiency status
        if deficiency_rate > 0:
            deficient_b12 = df[df['b12_deficient'] == 1]['b12_level']
            normal_b12 = df[df['b12_deficient'] == 0]['b12_level']
            print(f"\n🔬 B12 Levels Analysis:")
            print(f"   Deficient mean B12: {deficient_b12.mean():.1f} pg/mL")
            print(f"   Normal mean B12: {normal_b12.mean():.1f} pg/mL")
            print(f"   Deficiency threshold: <200 pg/mL")
        
        # Save a copy for reference
        df.to_csv('nhanes_real_processed.csv', index=False)
        print("💾 Processed data saved as 'nhanes_real_processed.csv'")
        
        return df
        
    except Exception as e:
        print(f"❌ Error loading real dataset: {e}")
        print("Creating synthetic data as fallback...")
        return prepare_synthetic_dataset()

def prepare_synthetic_dataset():
    """
    Fallback: Create synthetic data if real data fails
    """
    print("⚠️ Creating synthetic data as fallback...")
    
    np.random.seed(42)
    n_samples = 5000
    
    # Generate synthetic data
    data = {
        'age': np.random.randint(18, 80, n_samples),
        'gender': np.random.choice([0, 1], n_samples),
        'bmi': np.random.uniform(18, 40, n_samples),
        'systolic_bp': np.random.randint(90, 180, n_samples),
        'diastolic_bp': np.random.randint(60, 120, n_samples),
        'cholesterol': np.random.randint(150, 300, n_samples),
        'hdl': np.random.randint(30, 80, n_samples),
        'ldl': np.random.randint(70, 200, n_samples),
        'glucose': np.random.randint(70, 200, n_samples),
        'smoker': np.random.choice([0, 1], n_samples),
        'diabetic': np.random.choice([0, 1], n_samples),
        'diet_score': np.random.randint(1, 10, n_samples),
        'b12_level': np.random.randint(100, 600, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Create target variable
    df['b12_deficient'] = (df['b12_level'] < 200).astype(int)
    
    # Add risk factor
    df['risk_factor'] = (
        (df['age'] > 50).astype(int) * 2 +
        (df['bmi'] > 30).astype(int) * 1 +
        (df['diet_score'] < 4).astype(int) * 3 +
        df['smoker'] * 1 +
        df['diabetic'] * 2
    )
    
    print(f"✅ Synthetic dataset created: {len(df)} samples")
    
    return df

def load_and_preprocess_data(filepath='Nhanes_cvd_raw.csv'):
    """
    Load and preprocess the dataset for ML
    """
    print(f"📂 Loading dataset from: {filepath}")
    
    try:
        # Try to load real data first
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            print(f"✅ Loaded REAL dataset: {len(df)} samples")
            
            # Verify required columns exist
            required_columns = ['age', 'gender', 'bmi', 'b12_level', 'b12_deficient']
            missing = [col for col in required_columns if col not in df.columns]
            
            if missing:
                print(f"⚠️ Missing columns in real data: {missing}")
                print("   Using synthetic data instead...")
                df = prepare_synthetic_dataset()
        else:
            print(f"⚠️ File not found: {filepath}")
            df = prepare_synthetic_dataset()
            
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        print("   Using synthetic data...")
        df = prepare_synthetic_dataset()
    
    # Define features for prediction (based on your dataset)
    feature_columns = [
        'age', 'gender', 'bmi', 'systolic_bp', 'diastolic_bp',
        'cholesterol', 'hdl', 'ldl', 'glucose', 'smoker',
        'diabetic', 'diet_score', 'risk_factor'
    ]
    
    # Ensure all columns exist
    available_features = [col for col in feature_columns if col in df.columns]
    
    print(f"\n🔧 Using {len(available_features)} features:")
    for feature in available_features:
        print(f"   • {feature}")
    
    # Separate features and target
    X = df[available_features]
    y = df['b12_deficient']
    
    print(f"\n🎯 Target variable 'b12_deficient':")
    print(f"   Normal (0): {len(y[y==0]):,} samples")
    print(f"   Deficient (1): {len(y[y==1]):,} samples")
    print(f"   Deficiency rate: {y.mean():.1%}")
    
    return X, y, available_features, df

if __name__ == "__main__":
    # Test the dataset preparation
    print("=" * 60)
    print("🧪 TESTING DATASET PREPARATION")
    print("=" * 60)
    
    X, y, features, df = load_and_preprocess_data()
    
    print(f"\n📋 Feature columns: {features}")
    print(f"📐 X shape: {X.shape}, y shape: {y.shape}")
    
    # Show correlation with B12 deficiency
    print("\n🔗 Feature correlations with B12 deficiency:")
    correlations = {}
    for feature in features:
        if feature in df.columns:
            corr = df[feature].corr(df['b12_deficient'])
            correlations[feature] = abs(corr)
    
    # Sort by absolute correlation
    sorted_correlations = sorted(correlations.items(), key=lambda x: x[1], reverse=True)
    
    for feature, corr in sorted_correlations[:10]:  # Top 10
        print(f"   {feature:15s}: {corr:.3f}")
    
    print("\n✅ Dataset preparation complete!")