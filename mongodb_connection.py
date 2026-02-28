# mongodb_connection.py - CLEANED VERSION (NO DUPLICATES)
from pymongo import MongoClient
from datetime import datetime
import pandas as pd
import json
from bson import ObjectId
import os
from dotenv import load_dotenv
import streamlit as st
import hashlib
import secrets

# Load environment variables
load_dotenv()

class MongoDBConnection:
    """MongoDB connection and operations manager for B12 Assistant"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.connected = False
        
        # Use your MongoDB Atlas connection string
        self.connection_string = os.getenv(
            'MONGODB_URI',
            'mongodb+srv://b12predictor:B12Predictor2024@b12-cluster.3k2zvtx.mongodb.net/b12_predictor?retryWrites=true&w=majority&appName=b12-cluster'
        )
        
        self.db_name = 'b12_predictor'
        self.connect()
    
    def connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.db_name]
            
            # Test connection
            self.client.admin.command('ping')
            self.connected = True
            
            # Create indexes
            self._create_indexes()
            
            print(f"✅ Connected to MongoDB Atlas: {self.db_name}")
            return True
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.connected = False
            return False
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Indexes for users collection
            if 'users' in self.db.list_collection_names():
                self.db.users.create_index([("email", 1)], unique=True)
                self.db.users.create_index([("username", 1)], unique=True)
            
            print("✅ Database indexes created/verified")
        except Exception as e:
            print(f"⚠️ Could not create indexes: {e}")
    
    def get_collection(self, collection_name):
        """Get a collection from the database"""
        if not self.connected:
            if not self.connect():
                raise ConnectionError("Cannot connect to MongoDB")
        
        if not hasattr(self.db, collection_name):
            # Create collection if it doesn't exist
            self.db.create_collection(collection_name)
        
        return self.db[collection_name]
    
    def _hash_password(self, password):
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${hashed}"
    
    def _verify_password(self, password, stored_hash):
        """Verify password against stored hash"""
        try:
            if not stored_hash or '$' not in stored_hash:
                return False
            salt, hashed = stored_hash.split('$')
            test_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return hashed == test_hash
        except:
            return False
    
    # ==================== AUTHENTICATION METHODS ====================
    
    def register_user(self, username, email, password, full_name="", age=None):
        """Register a new user"""
        try:
            users = self.get_collection('users')
            
            # Check if user already exists
            existing_user = users.find_one({
                "$or": [
                    {"email": email},
                    {"username": username}
                ]
            })
            
            if existing_user:
                return {"success": False, "message": "User already exists"}
            
            # Create user document
            user_doc = {
                'username': username,
                'email': email,
                'password_hash': self._hash_password(password),
                'full_name': full_name,
                'age': age if age else None,
                'created_at': datetime.now(),
                'last_login': datetime.now(),
                'is_active': True,
                'role': 'user',
                'profile_completed': False,
                'assessments_count': 0,
                'lab_reports_count': 0
            }
            
            # Insert user
            result = users.insert_one(user_doc)
            
            if result.inserted_id:
                # Create user profile
                profile_doc = {
                    'user_id': result.inserted_id,
                    'username': username,
                    'email': email,
                    'medical_history': {},
                    'diet_preferences': {},
                    'settings': {},
                    'created_at': datetime.now()
                }
                
                # Make sure user_profiles collection exists
                user_profiles = self.get_collection('user_profiles')
                user_profiles.insert_one(profile_doc)
                
                return {
                    "success": True,
                    "user_id": str(result.inserted_id),
                    "message": "Registration successful"
                }
            
            return {"success": False, "message": "Registration failed"}
            
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return {"success": False, "message": f"Registration error: {str(e)}"}
    
    def login_user(self, username_or_email, password):
        """Authenticate user"""
        try:
            users = self.get_collection('users')
            
            # Find user by username or email
            user = users.find_one({
                "$or": [
                    {"username": username_or_email},
                    {"email": username_or_email}
                ]
            })
            
            if not user:
                return {"success": False, "message": "User not found"}
            
            # Verify password
            if not self._verify_password(password, user.get('password_hash', '')):
                return {"success": False, "message": "Incorrect password"}
            
            if not user.get('is_active', True):
                return {"success": False, "message": "Account is inactive"}
            
            # Update last login
            users.update_one(
                {"_id": user['_id']},
                {"$set": {"last_login": datetime.now()}}
            )
            
            # Get user profile
            user_profiles = self.get_collection('user_profiles')
            profile = user_profiles.find_one({"user_id": user['_id']})
            
            user_data = {
                'user_id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'full_name': user.get('full_name', ''),
                'age': user.get('age'),
                'created_at': user['created_at'].isoformat() if isinstance(user['created_at'], datetime) else str(user['created_at']),
                'role': user.get('role', 'user'),
                'profile_completed': user.get('profile_completed', False),
                'assessments_count': user.get('assessments_count', 0),
                'lab_reports_count': user.get('lab_reports_count', 0)
            }
            
            if profile:
                user_data['profile'] = {
                    'medical_history': profile.get('medical_history', {}),
                    'diet_preferences': profile.get('diet_preferences', {}),
                    'settings': profile.get('settings', {})
                }
            
            return {
                "success": True,
                "user": user_data,
                "message": "Login successful"
            }
            
        except Exception as e:
            print(f"❌ Login error: {e}")
            return {"success": False, "message": f"Login error: {str(e)}"}
    
    def update_user_profile(self, user_id, profile_data):
        """Update user profile"""
        try:
            users = self.get_collection('users')
            user_profiles = self.get_collection('user_profiles')
            
            # Update basic user info
            update_data = {}
            if 'full_name' in profile_data:
                update_data['full_name'] = profile_data['full_name']
            if 'age' in profile_data:
                update_data['age'] = profile_data['age']
            
            if update_data:
                users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": update_data}
                )
            
            # Update profile
            profile_update = {
                "medical_history": profile_data.get('medical_history', {}),
                "diet_preferences": profile_data.get('diet_preferences', {}),
                "settings": profile_data.get('settings', {}),
                "updated_at": datetime.now()
            }
            
            user_profiles.update_one(
                {"user_id": ObjectId(user_id)},
                {"$set": profile_update},
                upsert=True
            )
            
            # Mark profile as completed
            users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"profile_completed": True}}
            )
            
            return {"success": True, "message": "Profile updated successfully"}
            
        except Exception as e:
            print(f"❌ Profile update error: {e}")
            return {"success": False, "message": f"Profile update error: {str(e)}"}
    
    def change_password(self, user_id, current_password, new_password):
        """Change user password"""
        try:
            users = self.get_collection('users')
            
            # Get user
            user = users.find_one({"_id": ObjectId(user_id)})
            
            if not user:
                return {"success": False, "message": "User not found"}
            
            # Verify current password
            if not self._verify_password(current_password, user.get('password_hash', '')):
                return {"success": False, "message": "Current password is incorrect"}
            
            # Update password
            new_hash = self._hash_password(new_password)
            users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"password_hash": new_hash}}
            )
            
            return {"success": True, "message": "Password changed successfully"}
            
        except Exception as e:
            print(f"❌ Password change error: {e}")
            return {"success": False, "message": f"Password change error: {str(e)}"}
    
    def reset_password_request(self, email):
        """Request password reset"""
        try:
            users = self.get_collection('users')
            
            user = users.find_one({"email": email})
            if not user:
                return {"success": False, "message": "Email not found"}
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            reset_expiry = datetime.now().timestamp() + 3600  # 1 hour
            
            # Store reset token
            users.update_one(
                {"_id": user['_id']},
                {"$set": {
                    "reset_token": reset_token,
                    "reset_expiry": reset_expiry
                }}
            )
            
            return {
                "success": True,
                "message": "Password reset requested",
                "reset_token": reset_token,  # For demo only - in production, send email
                "user_id": str(user['_id'])
            }
            
        except Exception as e:
            print(f"❌ Password reset error: {e}")
            return {"success": False, "message": f"Password reset error: {str(e)}"}
    
    def reset_password(self, user_id, reset_token, new_password):
        """Reset password with token"""
        try:
            users = self.get_collection('users')
            
            user = users.find_one({"_id": ObjectId(user_id)})
            
            if not user:
                return {"success": False, "message": "Invalid reset token"}
            
            # Verify token and expiry
            if (user.get('reset_token') != reset_token or 
                user.get('reset_expiry', 0) < datetime.now().timestamp()):
                return {"success": False, "message": "Invalid or expired reset token"}
            
            # Update password
            new_hash = self._hash_password(new_password)
            users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {
                    "password_hash": new_hash,
                    "reset_token": None,
                    "reset_expiry": None
                }}
            )
            
            return {"success": True, "message": "Password reset successfully"}
            
        except Exception as e:
            print(f"❌ Password reset error: {e}")
            return {"success": False, "message": f"Password reset error: {str(e)}"}
    
    def get_user_by_id(self, user_id):
        """Get user by ID"""
        try:
            users = self.get_collection('users')
            user = users.find_one({"_id": ObjectId(user_id)})
            
            if user:
                return {
                    'user_id': str(user['_id']),
                    'username': user['username'],
                    'email': user['email'],
                    'full_name': user.get('full_name', ''),
                    'age': user.get('age'),
                    'created_at': user['created_at'],
                    'role': user.get('role', 'user'),
                    'assessments_count': user.get('assessments_count', 0),
                    'lab_reports_count': user.get('lab_reports_count', 0)
                }
            return None
            
        except Exception as e:
            print(f"❌ Get user error: {e}")
            return None
    
    # ==================== DATA METHODS ====================
    
    def save_user_assessment(self, user_data, risk_score, risk_level, recommendations, ml_prediction=None, user_id=None, session_id=None):
        """Save user assessment to MongoDB"""
        try:
            assessments = self.get_collection('assessments')
            
            # Prepare assessment document
            assessment_doc = {
                'timestamp': datetime.now(),
                'user_id': ObjectId(user_id) if user_id else None,
                'session_id': session_id or str(datetime.now().timestamp()),
                'user_data': user_data,
                'risk_score': float(risk_score),
                'risk_level': risk_level,
                'recommendations': recommendations,
                'ml_prediction': ml_prediction if ml_prediction else {},
                'has_conflicts': ml_prediction.get('has_conflicts', False) if ml_prediction else False,
                'conflict_count': ml_prediction.get('conflict_count', 0) if ml_prediction else 0,
                'data_quality': ml_prediction.get('data_quality', {}) if ml_prediction else {}
            }
            
            # Insert into database
            result = assessments.insert_one(assessment_doc)
            
            # Update user's assessment count
            if user_id:
                users = self.get_collection('users')
                users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$inc": {"assessments_count": 1}}
                )
            
            print(f"✅ Assessment saved with ID: {result.inserted_id}")
            
            # Also save to user history
            self._save_to_user_history(assessment_doc, result.inserted_id, user_id)
            
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error saving assessment: {e}")
            return None
    
    def _save_to_user_history(self, assessment_doc, assessment_id, user_id=None):
        """Save to user history collection"""
        try:
            history = self.get_collection('user_history')
            
            history_doc = {
                'assessment_id': assessment_id,
                'user_id': ObjectId(user_id) if user_id else None,
                'timestamp': assessment_doc['timestamp'],
                'session_id': assessment_doc['session_id'],
                'age': assessment_doc['user_data'].get('age'),
                'gender': assessment_doc['user_data'].get('gender'),
                'diet_type': assessment_doc['user_data'].get('diet_type'),
                'bmi': assessment_doc['user_data'].get('bmi'),
                'b12_level': assessment_doc['user_data'].get('b12_level'),
                'lab_b12_level': assessment_doc['user_data'].get('lab_b12_level'),
                'symptoms_count': assessment_doc['user_data'].get('symptoms_count'),
                'risk_level': assessment_doc['risk_level'],
                'risk_score': assessment_doc['risk_score'],
                'has_conflicts': assessment_doc['has_conflicts'],
                'data_source': assessment_doc['user_data'].get('b12_source', 'assessment')
            }
            
            history.insert_one(history_doc)
            print("✅ User history saved")
            
        except Exception as e:
            print(f"❌ Error saving user history: {e}")
    
    def save_lab_report(self, lab_data, user_data=None, user_id=None, session_id=None):
        """Save lab report analysis to MongoDB"""
        try:
            lab_reports = self.get_collection('lab_reports')
            
            lab_doc = {
                'timestamp': datetime.now(),
                'user_id': ObjectId(user_id) if user_id else None,
                'session_id': session_id or str(datetime.now().timestamp()),
                'lab_data': lab_data,
                'user_info': user_data if user_data else {},
                'b12_value': lab_data.get('b12_value'),
                'status': lab_data.get('status'),
                'filename': lab_data.get('filename', 'manual_entry'),
                'source': 'uploaded' if lab_data.get('filename') != 'manual_entry' else 'manual'
            }
            
            result = lab_reports.insert_one(lab_doc)
            
            # Update user's lab report count
            if user_id:
                users = self.get_collection('users')
                users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$inc": {"lab_reports_count": 1}}
                )
            
            print(f"✅ Lab report saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error saving lab report: {e}")
            return None
    
    def save_conflict_analysis(self, conflict_data, user_id=None, session_id=None):
        """Save conflict analysis to MongoDB"""
        try:
            conflicts = self.get_collection('data_conflicts')
            
            conflict_doc = {
                'timestamp': datetime.now(),
                'user_id': ObjectId(user_id) if user_id else None,
                'session_id': session_id or str(datetime.now().timestamp()),
                'analysis': conflict_data,
                'has_conflicts': bool(conflict_data.get('data_quality', {}).get('issues', [])),
                'conflict_count': len(conflict_data.get('data_quality', {}).get('issues', [])),
                'data_quality_score': conflict_data.get('data_quality', {}).get('score', 100),
                'data_quality_grade': conflict_data.get('data_quality', {}).get('grade', 'A')
            }
            
            result = conflicts.insert_one(conflict_doc)
            print(f"✅ Conflict analysis saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
            
        except Exception as e:
            print(f"❌ Error saving conflict analysis: {e}")
            return None
    
    def get_user_assessments(self, user_id=None, session_id=None, limit=10):
        """Get user assessments from MongoDB"""
        try:
            assessments = self.get_collection('assessments')
            
            query = {}
            if user_id:
                query['user_id'] = ObjectId(user_id)
            elif session_id:
                query['session_id'] = session_id
            
            cursor = assessments.find(query).sort('timestamp', -1).limit(limit)
            results = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for doc in results:
                doc['_id'] = str(doc['_id'])
                if 'user_id' in doc and doc['user_id']:
                    doc['user_id'] = str(doc['user_id'])
                if 'timestamp' in doc:
                    doc['timestamp'] = doc['timestamp'].isoformat() if isinstance(doc['timestamp'], datetime) else str(doc['timestamp'])
            
            return results
            
        except Exception as e:
            print(f"❌ Error retrieving assessments: {e}")
            return []
    
    def get_user_history(self, user_id=None, session_id=None, limit=20):
        """Get user history from MongoDB"""
        try:
            history = self.get_collection('user_history')
            
            query = {}
            if user_id:
                query['user_id'] = ObjectId(user_id)
            elif session_id:
                query['session_id'] = session_id
            
            cursor = history.find(query).sort('timestamp', -1).limit(limit)
            results = list(cursor)
            
            # Convert for display
            for doc in results:
                doc['_id'] = str(doc['_id'])
                if 'user_id' in doc and doc['user_id']:
                    doc['user_id'] = str(doc['user_id'])
                if 'timestamp' in doc:
                    doc['timestamp'] = doc['timestamp'].isoformat() if isinstance(doc['timestamp'], datetime) else str(doc['timestamp'])
            
            return results
            
        except Exception as e:
            print(f"❌ Error retrieving user history: {e}")
            return []
    
    def get_lab_reports(self, user_id=None, session_id=None, limit=10):
        """Get lab reports from MongoDB"""
        try:
            lab_reports = self.get_collection('lab_reports')
            
            query = {}
            if user_id:
                query['user_id'] = ObjectId(user_id)
            elif session_id:
                query['session_id'] = session_id
            
            cursor = lab_reports.find(query).sort('timestamp', -1).limit(limit)
            results = list(cursor)
            
            for doc in results:
                doc['_id'] = str(doc['_id'])
                if 'user_id' in doc and doc['user_id']:
                    doc['user_id'] = str(doc['user_id'])
                if 'timestamp' in doc:
                    doc['timestamp'] = doc['timestamp'].isoformat() if isinstance(doc['timestamp'], datetime) else str(doc['timestamp'])
            
            return results
            
        except Exception as e:
            print(f"❌ Error retrieving lab reports: {e}")
            return []
    
    def get_conflict_analyses(self, user_id=None, session_id=None, limit=10):
        """Get conflict analyses from MongoDB"""
        try:
            conflicts = self.get_collection('data_conflicts')
            
            query = {}
            if user_id:
                query['user_id'] = ObjectId(user_id)
            elif session_id:
                query['session_id'] = session_id
            
            cursor = conflicts.find(query).sort('timestamp', -1).limit(limit)
            results = list(cursor)
            
            for doc in results:
                doc['_id'] = str(doc['_id'])
                if 'user_id' in doc and doc['user_id']:
                    doc['user_id'] = str(doc['user_id'])
                if 'timestamp' in doc:
                    doc['timestamp'] = doc['timestamp'].isoformat() if isinstance(doc['timestamp'], datetime) else str(doc['timestamp'])
            
            return results
            
        except Exception as e:
            print(f"❌ Error retrieving conflict analyses: {e}")
            return []
    
    def get_dashboard_stats(self, user_id=None):
        """Get dashboard statistics from MongoDB"""
        try:
            stats = {}
            
            # Build query based on user_id
            user_query = {}
            if user_id:
                user_query['user_id'] = ObjectId(user_id)
            
            # Get counts from each collection
            assessments = self.get_collection('assessments')
            lab_reports = self.get_collection('lab_reports')
            conflicts = self.get_collection('data_conflicts')
            user_history = self.get_collection('user_history')
            users = self.get_collection('users')
            
            stats['total_assessments'] = assessments.count_documents(user_query)
            stats['total_lab_reports'] = lab_reports.count_documents(user_query)
            stats['total_conflicts'] = conflicts.count_documents(user_query)
            stats['total_users'] = users.count_documents({}) if not user_id else 1
            
            # Get risk level distribution
            pipeline = []
            if user_id:
                pipeline.append({"$match": {"user_id": ObjectId(user_id)}})
            pipeline.append({"$group": {"_id": "$risk_level", "count": {"$sum": 1}}})
            
            try:
                risk_distribution = user_history.aggregate(pipeline)
                stats['risk_distribution'] = {doc['_id']: doc['count'] for doc in risk_distribution}
            except:
                stats['risk_distribution'] = {}
            
            # Get average B12 level
            avg_b12_pipeline = []
            if user_id:
                avg_b12_pipeline.append({"$match": {"user_id": ObjectId(user_id)}})
            avg_b12_pipeline.append({"$match": {"b12_level": {"$ne": None}}})
            avg_b12_pipeline.append({"$group": {"_id": None, "avg_b12": {"$avg": "$b12_level"}}})
            
            try:
                avg_b12 = user_history.aggregate(avg_b12_pipeline)
                avg_result = list(avg_b12)
                stats['avg_b12_level'] = avg_result[0]['avg_b12'] if avg_result else 0
            except:
                stats['avg_b12_level'] = 0
            
            # Get conflict percentage
            try:
                if user_id:
                    user_conflicts = conflicts.count_documents({"user_id": ObjectId(user_id), "has_conflicts": True})
                    user_assessments = max(stats['total_assessments'], 1)
                    stats['conflict_percentage'] = (user_conflicts / user_assessments) * 100
                else:
                    all_conflicts = conflicts.count_documents({"has_conflicts": True})
                    all_assessments = max(stats['total_assessments'], 1)
                    stats['conflict_percentage'] = (all_conflicts / all_assessments) * 100
            except:
                stats['conflict_percentage'] = 0
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting dashboard stats: {e}")
            return {
                'total_assessments': 0,
                'total_lab_reports': 0,
                'total_conflicts': 0,
                'total_users': 0,
                'risk_distribution': {},
                'avg_b12_level': 0,
                'conflict_percentage': 0
            }
    
    def export_user_data(self, user_id=None, session_id=None, format='json'):
        """Export user data in specified format"""
        try:
            # Get all data for user/session
            assessments = self.get_user_assessments(user_id, session_id, limit=1000)
            lab_reports = self.get_lab_reports(user_id, session_id, limit=1000)
            history = self.get_user_history(user_id, session_id, limit=1000)
            conflicts = self.get_conflict_analyses(user_id, session_id, limit=1000)
            
            data = {
                'assessments': assessments,
                'lab_reports': lab_reports,
                'history': history,
                'conflicts': conflicts
            }
            
            if format == 'csv':
                # Convert to CSV format
                csv_data = {}
                for key, value in data.items():
                    if value:
                        df = pd.DataFrame(value)
                        csv_data[key] = df.to_csv(index=False)
                return csv_data
            elif format == 'json':
                return json.dumps(data, indent=2, default=str)
            else:
                return data
                
        except Exception as e:
            print(f"❌ Error exporting data: {e}")
            return None
    
    def clear_user_data(self, user_id):
        """Clear all data for a specific user"""
        try:
            collections = ['assessments', 'lab_reports', 'data_conflicts', 'user_history']
            deleted_count = 0
            
            for collection_name in collections:
                collection = self.get_collection(collection_name)
                result = collection.delete_many({'user_id': ObjectId(user_id)})
                deleted_count += result.deleted_count
            
            print(f"✅ Cleared {deleted_count} documents for user {user_id}")
            return deleted_count
            
        except Exception as e:
            print(f"❌ Error clearing user data: {e}")
            return 0
    
    def delete_user_account(self, user_id):
        """Delete user account and all associated data"""
        try:
            # Delete from all collections
            collections = ['users', 'user_profiles', 'assessments', 'lab_reports', 'data_conflicts', 'user_history']
            deleted_count = 0
            
            for collection_name in collections:
                collection = self.get_collection(collection_name)
                if collection_name == 'users' or collection_name == 'user_profiles':
                    result = collection.delete_many({'_id': ObjectId(user_id)} if collection_name == 'users' else {'user_id': ObjectId(user_id)})
                else:
                    result = collection.delete_many({'user_id': ObjectId(user_id)})
                deleted_count += result.deleted_count
            
            print(f"✅ Deleted account and {deleted_count} documents for user {user_id}")
            return deleted_count
            
        except Exception as e:
            print(f"❌ Error deleting account: {e}")
            return 0
    
    def backup_database(self, backup_path='mongodb_backup'):
        """Create a backup of the database"""
        try:
            import os
            os.makedirs(backup_path, exist_ok=True)
            
            collections = self.db.list_collection_names()
            backup_info = {
                'backup_date': datetime.now().isoformat(),
                'collections': []
            }
            
            for collection_name in collections:
                collection = self.get_collection(collection_name)
                documents = list(collection.find({}))
                
                # Save to JSON file
                backup_file = os.path.join(backup_path, f"{collection_name}.json")
                with open(backup_file, 'w') as f:
                    json.dump(documents, f, indent=2, default=str)
                
                backup_info['collections'].append({
                    'name': collection_name,
                    'count': len(documents),
                    'file': backup_file
                })
            
            # Save backup info
            info_file = os.path.join(backup_path, 'backup_info.json')
            with open(info_file, 'w') as f:
                json.dump(backup_info, f, indent=2)
            
            print(f"✅ Database backup created at {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return None
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            self.connected = False
            print("🔌 MongoDB disconnected")
    
    # ==================== TRACKER METHODS ====================
    
    def save_tracker_entry(self, user_id, tracker_data, session_id):
        """Save a single tracker entry to MongoDB"""
        try:
            tracker_data['user_id'] = user_id
            tracker_data['session_id'] = session_id
            tracker_data['timestamp'] = datetime.now()
            
            # Check if entry for this date already exists
            existing = self.db.tracker_entries.find_one({
                'user_id': user_id,
                'date': tracker_data['date']
            })
            
            if existing:
                # Update existing
                result = self.db.tracker_entries.update_one(
                    {'_id': existing['_id']},
                    {'$set': tracker_data}
                )
                return result.modified_count > 0
            else:
                # Insert new
                result = self.db.tracker_entries.insert_one(tracker_data)
                return result.inserted_id
        except Exception as e:
            print(f"Error saving tracker entry: {e}")
            return None
    
    def get_tracker_data(self, user_id, limit=30):
        """Get tracker data for a user"""
        try:
            cursor = self.db.tracker_entries.find(
                {'user_id': user_id}
            ).sort('date', -1).limit(limit)
            
            data = list(cursor)
            # Convert ObjectId to string for JSON serialization
            for item in data:
                if '_id' in item:
                    item['_id'] = str(item['_id'])
            return data
        except Exception as e:
            print(f"Error getting tracker data: {e}")
            return []
    
    def save_user_streak(self, user_id, streak):
        """Save user's current streak"""
        try:
            self.db.user_streaks.update_one(
                {'user_id': user_id},
                {'$set': {
                    'streak': streak,
                    'last_updated': datetime.now()
                }},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Error saving streak: {e}")
            return False
    
    def get_user_streak(self, user_id):
        """Get user's current streak from cloud"""
        try:
            record = self.db.user_streaks.find_one({'user_id': user_id})
            return record.get('streak', 0) if record else 0
        except Exception as e:
            print(f"Error getting streak: {e}")
            return 0
    
    def save_all_tracker_data(self, user_id, tracker_data):
        """Save all tracker data to cloud"""
        try:
            # Delete existing data
            self.db.tracker_entries.delete_many({'user_id': user_id})
            
            # Insert all data
            entries_to_insert = []
            for entry in tracker_data:
                entry_copy = entry.copy()
                entry_copy['user_id'] = user_id
                entry_copy['timestamp'] = datetime.now()
                entries_to_insert.append(entry_copy)
            
            if entries_to_insert:
                result = self.db.tracker_entries.insert_many(entries_to_insert)
                return len(result.inserted_ids) > 0
            
            return True
        except Exception as e:
            print(f"Error saving all tracker data: {e}")
            return False
    
    # ==================== MIGRATION METHODS ====================
    
    def migrate_temp_logs_to_mongodb(self, user_id, temp_logs):
        """Migrate temporary logs to MongoDB for a logged-in user"""
        try:
            if not temp_logs:
                return {'success': True, 'count': 0, 'message': 'No logs to migrate'}
            
            migrated_count = 0
            for log in temp_logs:
                # Add user_id to the log
                log['user_id'] = user_id
                log['migrated_at'] = datetime.now()
                
                # Determine collection based on activity type
                collection_name = self._get_collection_for_log_type(log.get('type', 'activity'))
                
                # Insert into appropriate collection
                self.db[collection_name].insert_one(log)
                migrated_count += 1
            
            return {
                'success': True,
                'count': migrated_count,
                'message': f'Migrated {migrated_count} logs to your account'
            }
        except Exception as e:
            return {
                'success': False,
                'count': 0,
                'message': f'Migration error: {str(e)}'
            }
    
    def _get_collection_for_log_type(self, log_type):
        """Helper method to determine collection name for log type"""
        collection_map = {
            'assessment': 'assessment_logs',
            'symptom': 'symptom_logs',
            'food': 'food_logs',
            'supplement': 'supplement_logs',
            'lab_report': 'lab_logs',
            'tracker_entry': 'tracker_entries',
            'quick_check': 'activity_logs',
            'assessment_fallback': 'activity_logs',
            'lab_report_manual': 'lab_logs',
            'export_pdf': 'activity_logs',
            'export_json': 'activity_logs',
            'ai_recommendations': 'activity_logs'
        }
        return collection_map.get(log_type, 'activity_logs')

# Initialize global MongoDB connection
try:
    mongodb = MongoDBConnection()
    print(f"🌐 MongoDB initialized: {mongodb.connected}")
except Exception as e:
    print(f"❌ Failed to initialize MongoDB: {e}")
    mongodb = None

# Helper function for Streamlit
def get_mongodb_connection():
    """Get MongoDB connection for Streamlit"""
    return MongoDBConnection()

if __name__ == "__main__":
    # Test the MongoDB connection
    print("Testing MongoDB Connection...")
    
    db = MongoDBConnection()
    
    if db.connected:
        print("Connection successful!")
        
        # Test creating a user
        print("\nTesting User Registration...")
        result = db.register_user(
            username="testuser",
            email="test@example.com",
            password="TestPass123",
            full_name="Test User"
        )
        
        if result['success']:
            print(f"User registration: {result['message']}")
            
            # Test login
            print("\n Testing User Login...")
            login_result = db.login_user("testuser", "TestPass123")
            print(f"User login: {login_result['message']}")
            
            if login_result['success']:
                user_id = login_result['user']['user_id']
                
                # Clean up test user
                print("\n Cleaning up test data...")
                db.delete_user_account(user_id)
                print("Test cleanup complete")
        
        db.disconnect()
    else:
        print("Connection failed!")