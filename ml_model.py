# ml_model.py - UPDATED FOR DATASET-ONLY TRAINING

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                           f1_score, roc_auc_score, confusion_matrix, 
                           classification_report, roc_curve)
import pickle
import json
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class B12DeficiencyPredictor:
    """
    ML model for predicting B12 deficiency from NHANES dataset ONLY
    """
    
    def __init__(self, model_type='random_forest'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.model_metrics = {}
        self.training_data_info = {}
        
        # Model selection - optimized for medical data
        self.models = {
            'random_forest': RandomForestClassifier(
                n_estimators=200,        # More trees for better accuracy
                max_depth=15,            # Deeper trees for complex patterns
                min_samples_split=10,    # Prevent overfitting
                min_samples_leaf=5,
                random_state=42,
                class_weight='balanced',  # Handle imbalanced data
                n_jobs=-1                # Use all CPU cores
            ),
            'gradient_boosting': GradientBoostingClassifier(
                n_estimators=150,
                learning_rate=0.05,      # Slower learning for better generalization
                max_depth=7,
                min_samples_split=15,
                random_state=42,
                subsample=0.8            # Stochastic gradient boosting
            ),
            'logistic_regression': LogisticRegression(
                max_iter=1000,
                random_state=42,
                class_weight='balanced',
                penalty='l2',            # L2 regularization
                C=1.0,                   # Regularization strength
                solver='lbfgs'
            ),
            'svm': SVC(
                probability=True,
                random_state=42,
                class_weight='balanced',
                kernel='rbf',            # Radial basis function kernel
                C=1.0,
                gamma='scale'
            )
        }
    
    def train(self, X, y, test_size=0.2, random_state=42):
        """
        Train the ML model on NHANES dataset ONLY
        """
        print(f"🚀 Training {self.model_type} model on NHANES dataset...")
        
        # Store dataset information
        self.training_data_info = {
            'n_samples': len(X),
            'n_features': X.shape[1],
            'deficiency_rate': y.mean(),
            'feature_names': list(X.columns),
            'training_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        print(f"   Training samples: {len(X_train):,}")
        print(f"   Testing samples: {len(X_test):,}")
        print(f"   Deficiency rate in training: {y_train.mean():.2%}")
        print(f"   Deficiency rate in testing: {y_test.mean():.2%}")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Get model
        self.model = self.models.get(self.model_type, self.models['random_forest'])
        
        # Train with progress indication
        print("   Training in progress...", end='', flush=True)
        self.model.fit(X_train_scaled, y_train)
        print(" Done!")
        
        # Evaluate
        train_score = self.model.score(X_train_scaled, y_train)
        test_score = self.model.score(X_test_scaled, y_test)
        
        # Predictions
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        
        # Calculate comprehensive metrics
        self.model_metrics = {
            'model_type': self.model_type,
            'train_accuracy': float(train_score),
            'test_accuracy': float(test_score),
            'precision': float(precision_score(y_test, y_pred, zero_division=0)),
            'recall': float(recall_score(y_test, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y_test, y_pred, zero_division=0)),
            'roc_auc': float(roc_auc_score(y_test, y_pred_proba)),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
            'feature_importance': self.get_feature_importance(X.columns),
            'classification_report': classification_report(y_test, y_pred, output_dict=True),
            'training_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'n_samples': int(len(X)),
            'class_distribution': {
                '0': int((y == 0).sum()),
                '1': int((y == 1).sum())
            },
            'dataset_info': self.training_data_info,
            'test_set_distribution': {
                'test_samples': len(y_test),
                'test_deficient': int(y_test.sum()),
                'test_normal': int(len(y_test) - y_test.sum())
            }
        }
        
        # Print detailed results
        print(f"\n✅ Training complete!")
        print(f"📊 Dataset used: {self.training_data_info['n_samples']:,} NHANES samples")
        print(f"📊 Train Accuracy: {train_score:.3f}")
        print(f"📊 Test Accuracy: {test_score:.3f}")
        print(f"🎯 Precision: {self.model_metrics['precision']:.3f}")
        print(f"🎯 Recall: {self.model_metrics['recall']:.3f}")
        print(f"🎯 F1 Score: {self.model_metrics['f1_score']:.3f}")
        print(f"📈 ROC AUC: {self.model_metrics['roc_auc']:.3f}")
        
        # Feature importance
        if self.model_metrics['feature_importance']:
            print("\n🔍 Top 10 Most Important Features (from dataset):")
            for feature, importance in sorted(self.model_metrics['feature_importance'].items(), 
                                           key=lambda x: x[1], reverse=True)[:10]:
                print(f"   {feature:20s}: {importance:.4f}")
        
        # Save visualization
        self._save_training_visualizations(X_test_scaled, y_test, y_pred, y_pred_proba)
        
        return self.model_metrics
    
    def predict(self, features_dict):
        """
        Predict B12 deficiency for a single person using dataset features ONLY
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")
        
        if self.feature_names is None:
            raise ValueError("Feature names not set. Train model first.")
        
        # Verify all required features are present
        missing_features = [f for f in self.feature_names if f not in features_dict]
        if missing_features:
            raise ValueError(f"Missing dataset features: {missing_features}")
        
        # Create feature vector in correct order
        feature_vector = [features_dict[feature] for feature in self.feature_names]
        
        # Scale features
        feature_vector_scaled = self.scaler.transform([feature_vector])
        
        # Make prediction
        probability = self.model.predict_proba(feature_vector_scaled)[0]
        prediction = self.model.predict(feature_vector_scaled)[0]
        
        # Get detailed feature contributions
        contributions = self.get_prediction_explanation(feature_vector_scaled[0])
        
        # Compare with dataset statistics
        dataset_comparison = self._compare_with_dataset(feature_vector)
        
        return {
            'deficient_probability': float(probability[1]),
            'prediction': int(prediction),
            'prediction_label': 'Deficient' if prediction == 1 else 'Normal',
            'confidence': float(max(probability)),
            'contributions': contributions,
            'dataset_comparison': dataset_comparison,
            'model_source': 'NHANES Dataset Model',
            'training_info': self.training_data_info,
            'features_used': {f: features_dict[f] for f in self.feature_names}
        }
    
    def get_feature_importance(self, feature_names):
        """Get feature importance scores"""
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            # Convert numpy floats to Python floats
            importance_dict = {feature: float(importance) 
                             for feature, importance in zip(feature_names, importances)}
            
            # Normalize to 0-100%
            total = sum(importance_dict.values())
            if total > 0:
                importance_dict = {k: (v/total)*100 for k, v in importance_dict.items()}
            
            return importance_dict
        return {}
    
    def get_prediction_explanation(self, scaled_features):
        """Explain prediction with feature contributions"""
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            explanations = {}
            
            for i, (feature, importance) in enumerate(zip(self.feature_names, importances)):
                # Contribution based on dataset patterns
                contribution = importance * scaled_features[i]
                
                explanations[feature] = {
                    'importance': float(importance),
                    'contribution': float(contribution),
                    'scaled_value': float(scaled_features[i]),
                    'impact': 'Increases risk' if contribution > 0 else 'Decreases risk'
                }
            
            return explanations
        return {}
    
    def _compare_with_dataset(self, feature_vector):
        """Compare input with dataset statistics"""
        comparison = {}
        
        # This would require access to the original dataset
        # For now, return basic comparison
        comparison['message'] = "Based on NHANES dataset patterns"
        comparison['dataset_samples'] = self.training_data_info.get('n_samples', 0)
        comparison['dataset_features'] = self.training_data_info.get('feature_names', [])
        
        return comparison
    
    def _save_training_visualizations(self, X_test, y_test, y_pred, y_pred_proba):
        """Save training visualizations"""
        try:
            # Create visualizations directory
            os.makedirs('model_visualizations', exist_ok=True)
            
            # 1. ROC Curve
            fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
            plt.figure(figsize=(10, 8))
            plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {self.model_metrics["roc_auc"]:.3f})')
            plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title('ROC Curve - NHANES B12 Deficiency Prediction')
            plt.legend(loc="lower right")
            plt.grid(True, alpha=0.3)
            plt.savefig('model_visualizations/roc_curve.png', dpi=150, bbox_inches='tight')
            plt.close()
            
            # 2. Feature Importance Plot
            if self.model_metrics['feature_importance']:
                importance_df = pd.DataFrame({
                    'Feature': list(self.model_metrics['feature_importance'].keys()),
                    'Importance': list(self.model_metrics['feature_importance'].values())
                })
                importance_df = importance_df.sort_values('Importance', ascending=False).head(15)
                
                plt.figure(figsize=(12, 8))
                bars = plt.barh(importance_df['Feature'], importance_df['Importance'])
                plt.xlabel('Importance (%)')
                plt.title('Top 15 Most Important Features (NHANES Dataset)')
                plt.gca().invert_yaxis()
                
                # Add value labels
                for bar in bars:
                    width = bar.get_width()
                    plt.text(width + 0.5, bar.get_y() + bar.get_height()/2, 
                            f'{width:.1f}%', ha='left', va='center')
                
                plt.grid(True, alpha=0.3, axis='x')
                plt.savefig('model_visualizations/feature_importance.png', dpi=150, bbox_inches='tight')
                plt.close()
            
            # 3. Confusion Matrix Heatmap
            cm = confusion_matrix(y_test, y_pred)
            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                       xticklabels=['Normal', 'Deficient'],
                       yticklabels=['Normal', 'Deficient'])
            plt.xlabel('Predicted')
            plt.ylabel('Actual')
            plt.title('Confusion Matrix - NHANES Dataset')
            plt.savefig('model_visualizations/confusion_matrix.png', dpi=150, bbox_inches='tight')
            plt.close()
            
            print(f"📊 Visualizations saved to 'model_visualizations/' folder")
            
        except Exception as e:
            print(f"Note: Could not save visualizations: {e}")
    
    def save_model(self, filename='b12_deficiency_model.pkl'):
        """Save trained model to file"""
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'model_type': self.model_type,
            'feature_names': self.feature_names,
            'metrics': self.model_metrics,
            'training_data_info': self.training_data_info,
            'model_params': self.model.get_params() if hasattr(self.model, 'get_params') else {}
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(model_data, f)
        
        # Save metrics as JSON
        with open('model_metrics.json', 'w') as f:
            json.dump(self.model_metrics, f, indent=2, default=str)
        
        # Save dataset info
        with open('dataset_info.json', 'w') as f:
            json.dump(self.training_data_info, f, indent=2, default=str)
        
        print(f"💾 Model saved to {filename}")
        print(f"📊 Metrics saved to model_metrics.json")
        print(f"📋 Dataset info saved to dataset_info.json")
        print(f"📈 Visualizations saved to model_visualizations/")
    
    def load_model(self, filename='b12_deficiency_model.pkl'):
        """Load trained model from file"""
        with open(filename, 'rb') as f:
            model_data = pickle.load(f)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.model_type = model_data['model_type']
        self.feature_names = model_data['feature_names']
        self.model_metrics = model_data['metrics']
        self.training_data_info = model_data.get('training_data_info', {})
        
        print(f"📂 Model loaded from {filename}")
        print(f"   Trained on: {self.training_data_info.get('n_samples', 0):,} NHANES samples")
        print(f"   Accuracy: {self.model_metrics.get('test_accuracy', 0):.1%}")
        
        return self
    
    def evaluate_model(self, X, y):
        """Evaluate model on new data"""
        X_scaled = self.scaler.transform(X)
        y_pred = self.model.predict(X_scaled)
        y_pred_proba = self.model.predict_proba(X_scaled)[:, 1]
        
        metrics = {
            'accuracy': float(accuracy_score(y, y_pred)),
            'precision': float(precision_score(y, y_pred, zero_division=0)),
            'recall': float(recall_score(y, y_pred, zero_division=0)),
            'f1_score': float(f1_score(y, y_pred, zero_division=0)),
            'roc_auc': float(roc_auc_score(y, y_pred_proba)),
            'classification_report': classification_report(y, y_pred, output_dict=True)
        }
        
        return metrics

def compare_models(X, y):
    """
    Compare different ML models on NHANES dataset
    """
    print("🔬 Comparing ML models on NHANES dataset...")
    print(f"📊 Dataset size: {len(X):,} samples, {X.shape[1]} features")
    print(f"🎯 Deficiency rate: {y.mean():.2%}")
    
    models_to_test = ['random_forest', 'gradient_boosting', 'logistic_regression', 'svm']
    results = []
    
    for model_type in models_to_test:
        print(f"\n📋 Testing {model_type}...")
        predictor = B12DeficiencyPredictor(model_type)
        
        # Set feature names before training
        predictor.feature_names = list(X.columns)
        
        metrics = predictor.train(X, y)
        metrics['model'] = model_type
        results.append(metrics)
    
    # Create comparison DataFrame
    results_df = pd.DataFrame(results)
    print("\n" + "="*60)
    print("🏆 MODEL COMPARISON RESULTS (NHANES DATASET)")
    print("="*60)
    
    # Display comparison
    comparison_cols = ['model', 'test_accuracy', 'precision', 'recall', 'f1_score', 'roc_auc']
    print(results_df[comparison_cols].to_string(index=False, float_format=lambda x: f"{x:.3f}"))
    
    # Find best model
    best_idx = results_df['roc_auc'].idxmax()
    best_model = results_df.loc[best_idx, 'model']
    best_score = results_df.loc[best_idx, 'roc_auc']
    
    print(f"\n🎯 Best model: {best_model} (ROC AUC: {best_score:.3f})")
    
    return results_df, best_model

if __name__ == "__main__":
    # Test the ML model with REAL NHANES data
    from dataset_preparation import load_and_preprocess_data
    
    print("="*70)
    print("🧠 B12 DEFICIENCY PREDICTION MODEL - NHANES DATASET TRAINING")
    print("="*70)
    
    # Load REAL NHANES data
    X, y, features, df = load_and_preprocess_data('Nhanes_cvd_raw.csv')
    
    print(f"\n📋 Dataset Overview:")
    print(f"   Total samples: {len(df):,}")
    print(f"   Features: {len(features)}")
    print(f"   B12 Deficiency rate: {df['b12_deficient'].mean():.2%}")
    print(f"   B12 Level range: {df['b12_level'].min():.0f} - {df['b12_level'].max():.0f} pg/mL")
    
    # Compare models
    results_df, best_model = compare_models(X, y)
    
    # Train best model
    print(f"\n🚀 Training final model: {best_model}")
    final_predictor = B12DeficiencyPredictor(best_model)
    final_predictor.feature_names = features
    final_predictor.train(X, y)
    
    # Save the model
    final_predictor.save_model('b12_deficiency_model.pkl')
    
    # Test prediction with sample from dataset
    print("\n🧪 Testing prediction with dataset sample...")
    
    # Get a real sample from the dataset
    sample_idx = 0
    sample_features = {}
    for feature in features:
        if feature in df.columns:
            sample_features[feature] = float(df.iloc[sample_idx][feature])
    
    actual_b12 = float(df.iloc[sample_idx]['b12_level'])
    actual_status = int(df.iloc[sample_idx]['b12_deficient'])
    
    prediction = final_predictor.predict(sample_features)
    
    print(f"\n📊 Prediction for dataset sample #{sample_idx}:")
    print(f"   Actual B12 Level: {actual_b12:.0f} pg/mL")
    print(f"   Actual Status: {'Deficient' if actual_status == 1 else 'Normal'}")
    print(f"   Predicted Probability: {prediction['deficient_probability']:.1%}")
    print(f"   Predicted Status: {prediction['prediction_label']}")
    print(f"   Confidence: {prediction['confidence']:.1%}")
    print(f"   Model Source: {prediction['model_source']}")
    
    # Show top contributing features
    if prediction.get('contributions'):
        print(f"\n🔍 Top contributing features:")
        contributions = prediction['contributions']
        sorted_contribs = sorted(contributions.items(), 
                               key=lambda x: abs(x[1]['contribution']), 
                               reverse=True)[:5]
        
        for feature, data in sorted_contribs:
            impact = data.get('impact', 'Neutral')
            print(f"   • {feature}: {data['contribution']:.4f} ({impact})")
    
    print("\n✅ ML Backend training complete!")
    print("   The model now predicts EXCLUSIVELY based on NHANES dataset patterns.")