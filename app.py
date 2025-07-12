from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from datetime import datetime
import json
from functools import wraps
from werkzeug.security import check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'amm'  # Change this to a secure secret key

# Firebase configuration
try:
    # Initialize Firebase Admin SDK
    if not firebase_admin._apps:
        # For development, use service account key file
        # Download your service account key from Firebase Console
        cred = credentials.Certificate('firebase-service-account.json')
        firebase_admin.initialize_app(cred)
    
    # Initialize Firestore
    db = firestore.client()
except Exception as e:
    print(f"Firebase initialization error: {e}")
    db = None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Admin access required')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Home page - Display public profiles
@app.route('/')
def index():
    try:
        if db:
            # Get public profiles from Firestore
            users_ref = db.collection('users')
            query = users_ref.where('profile_visibility', '==', 'public').limit(20)
            users = query.stream()
            
            profiles = []
            for user in users:
                user_data = user.to_dict()
                user_data['id'] = user.id
                profiles.append(user_data)
        else:
            profiles = []
            
        return render_template('index.html', profiles=profiles)
    except Exception as e:
        print(f"Error loading profiles: {e}")
        return render_template('index.html', profiles=[])

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate input
        if not name or not email or not password:
            flash('All fields are required')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long')
            return render_template('register.html')
        
        try:
            if db:
                # Check if user already exists
                existing_user = db.collection('users').where('email', '==', email).limit(1).stream()
                if any(existing_user):
                    flash('Email already registered')
                    return render_template('register.html')
                
                # Create new user profile
                user_data = {
                    'name': name,
                    'email': email,
                    'password': password,  # In production, hash this password
                    'location': '',
                    'skills_offered': '',
                    'skills_wanted': '',
                    'availability': 'weekends',
                    'profile_visibility': 'public',
                    'created_at': datetime.now(),
                    'rating': 0,
                    'rating_count': 0,
                    'status': 'active',
                    'role': 'user'
                }
                
                # Add user to Firestore
                doc_ref = db.collection('users').add(user_data)
                print(f"Debug: doc_ref type: {type(doc_ref)}")
                print(f"Debug: doc_ref content: {doc_ref}")
                print(f"Debug: doc_ref length: {len(doc_ref)}")
                
                # Try to get the document reference - typically it's the first element
                document_ref = doc_ref[1]
                print(f"Debug: document_ref type: {type(document_ref)}")
                print(f"Debug: document_ref: {document_ref}")
                
                user_id = document_ref.id
                print(f"Debug: user_id: {user_id}")
                
                # Log user in automatically
                session['user_id'] = user_id
                session['email'] = email
                session['role'] = 'user'
                session['name'] = name
                
                flash('Registration successful! Welcome to Skill Swap Platform.')
                return redirect(url_for('profile'))
            else:
                # Demo mode - just add to session
                session['user_id'] = email.split('@')[0]
                session['email'] = email
                session['role'] = 'user'
                session['name'] = name
                
                flash('Registration successful! (Demo Mode)')
                return redirect(url_for('profile'))
                
        except Exception as e:
            import traceback
            print(f"Registration error: {e}")
            print(f"Full traceback: {traceback.format_exc()}")
            flash('Registration failed. Please try again.')
    
    return render_template('register.html')

# Login page


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        try:
            demo_users = {
                'user@demo.com': {
                    'password': 'password123',
                    'role': 'user',
                    'name': 'Demo User',
                    'status': 'active'  # or 'banned'
                },
                'admin@demo.com': {
                    'password': 'admin123',
                    'role': 'admin',
                    'name': 'Admin User',
                    'status': 'active'
                }
            }

            #  Handle demo users (hardcoded)
            if email in demo_users:
                user = demo_users[email]

                if user.get('status') == 'banned':
                    flash("Your account is banned.", "danger")
                    return render_template('login.html')

                if password == user['password']:
                    session['user_id'] = email.split('@')[0]
                    session['email'] = email
                    session['role'] = user['role']
                    session['name'] = user['name']

                    flash("Login successful!", "success")
                    return redirect(url_for('admin_dashboard' if session['role'] == 'admin' else 'index'))
                else:
                    flash("Invalid demo password", "danger")
                    return render_template('login.html')

            #  Handle real users from Firestore
            if db:
                user_docs = db.collection('users').where('email', '==', email).limit(1).stream()
                user_doc = next(user_docs, None)

                if user_doc:
                    user_data = user_doc.to_dict()

                    #  Check user status
                    if user_data.get('status') == 'banned':
                        flash("Your account is banned. Please contact support.", "danger")
                        return render_template('login.html')

                    if (user_data['password'], password):
                        session['user_id'] = user_doc.id
                        session['email'] = email
                        session['role'] = user_data.get('role', 'user')
                        session['name'] = user_data.get('name', 'User')

                        flash("Login successful!", "success")
                        return redirect(url_for('admin_dashboard' if session['role'] == 'admin' else 'index'))
                    else:
                        flash("Incorrect password", "danger")
                        return render_template('login.html')
                else:
                    flash("User not found", "warning")
                    return render_template('login.html')
            else:
                flash("Database connection error", "danger")
                return render_template('login.html')

        except Exception as e:
            print("Login error:", e)
            flash("An error occurred. Please try again.", "danger")
            return render_template('login.html')

    return render_template('login.html')


# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# User profile page
@app.route('/profile')
@login_required
def profile():
    try:
        if db:
            user_ref = db.collection('users').document(session['user_id'])
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
            else:
                # Create new user profile
                user_data = {
                    'name': session.get('name', ''),
                    'email': session.get('email', ''),
                    'location': '',
                    'skills_offered': '',
                    'skills_wanted': '',
                    'availability': 'weekends',
                    'profile_visibility': 'public',
                    'created_at': datetime.now(),
                    'rating': 0,
                    'rating_count': 0
                }
                user_ref.set(user_data)
        else:
            user_data = {}
            
        return render_template('profile.html', user_data=user_data)
    except Exception as e:
        print(f"Profile error: {e}")
        return render_template('profile.html', user_data={})

# Update profile
@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    try:
        if db:
            user_data = {
                'name': request.form['name'],
                'location': request.form['location'],
                'skills_offered': request.form['skills_offered'],
                'skills_wanted': request.form['skills_wanted'],
                'availability': request.form['availability'],
                'profile_visibility': request.form['profile_visibility'],
                'updated_at': datetime.now()
            }
            
            user_ref = db.collection('users').document(session['user_id'])
            user_ref.update(user_data)
            
            flash('Profile updated successfully!')
        else:
            flash('Database not available')
            
    except Exception as e:
        print(f"Update profile error: {e}")
        flash('Error updating profile')
    
    return redirect(url_for('profile'))

# Public profile view
@app.route('/public_profile/<user_id>')
def public_profile(user_id):
    try:
        if db:
            user_ref = db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                user_data['id'] = user_id
                
                # Get feedback for this user
                feedback_ref = db.collection('feedback').where('to_user', '==', user_id).limit(5)
                feedback_docs = feedback_ref.stream()
                
                feedback_list = []
                for feedback in feedback_docs:
                    feedback_data = feedback.to_dict()
                    feedback_list.append(feedback_data)
                
                user_data['feedback'] = feedback_list
            else:
                user_data = None
        else:
            user_data = None
            
        return render_template('public_profile.html', user_data=user_data)
    except Exception as e:
        print(f"Public profile error: {e}")
        return render_template('public_profile.html', user_data=None)

# Send swap request
@app.route('/send_request', methods=['POST'])
@login_required
def send_request():
    try:
        if db:
            request_data = {
                'from_user': session['user_id'],
                'to_user': request.form['to_user'],
                'my_skill': request.form['my_skill'],
                'their_skill': request.form['their_skill'],
                'message': request.form['message'],
                'status': 'pending',
                'created_at': datetime.now()
            }
            
            db.collection('swap_requests').add(request_data)
            return jsonify({'success': True, 'message': 'Request sent successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Database not available'})
            
    except Exception as e:
        print(f"Send request error: {e}")
        return jsonify({'success': False, 'message': 'Error sending request'})

# Swap requests page
@app.route('/swap_requests')
@login_required
def swap_requests():
    try:
        if db:
            # Get incoming requests
            incoming_ref = db.collection('swap_requests').where('to_user', '==', session['user_id'])
            incoming_docs = incoming_ref.stream()
            
            incoming_requests = []
            for doc in incoming_docs:
                req_data = doc.to_dict()
                req_data['id'] = doc.id
                incoming_requests.append(req_data)
            
            # Get outgoing requests
            outgoing_ref = db.collection('swap_requests').where('from_user', '==', session['user_id'])
            outgoing_docs = outgoing_ref.stream()
            
            outgoing_requests = []
            for doc in outgoing_docs:
                req_data = doc.to_dict()
                req_data['id'] = doc.id
                outgoing_requests.append(req_data)
        else:
            incoming_requests = []
            outgoing_requests = []
            
        return render_template('swap_requests.html', 
                             incoming_requests=incoming_requests,
                             outgoing_requests=outgoing_requests)
    except Exception as e:
        print(f"Swap requests error: {e}")
        return render_template('swap_requests.html', 
                             incoming_requests=[],
                             outgoing_requests=[])

# Accept/Reject swap request
@app.route('/update_request', methods=['POST'])
@login_required
def update_request():
    try:
        if db:
            request_id = request.form['request_id']
            action = request.form['action']
            
            update_data = {
                'status': action,
                'updated_at': datetime.now()
            }
            
            db.collection('swap_requests').document(request_id).update(update_data)
            return jsonify({'success': True, 'message': f'Request {action} successfully!'})
        else:
            return jsonify({'success': False, 'message': 'Database not available'})
            
    except Exception as e:
        print(f"Update request error: {e}")
        return jsonify({'success': False, 'message': 'Error updating request'})

# Admin dashboard
@app.route('/admin')
@admin_required
def admin_dashboard():
    try:
        if db:
            # Get statistics
            users_count = len(list(db.collection('users').stream()))
            requests_count = len(list(db.collection('swap_requests').stream()))
            pending_count = len(list(db.collection('swap_requests').where('status', '==', 'pending').stream()))
            
            stats = {
                'total_users': users_count,
                'total_swaps': requests_count,
                'pending_swaps': pending_count,
                'avg_rating': 4.2  # Calculate from actual data
            }
        else:
            stats = {
                'total_users': 0,
                'total_swaps': 0,
                'pending_swaps': 0,
                'avg_rating': 0
            }
            
        return render_template('admin.html', stats=stats)
    except Exception as e:
        print(f"Admin dashboard error: {e}")
        return render_template('admin.html', stats={})

# API endpoints for AJAX requests
@app.route('/api/search_profiles')
def api_search_profiles():
    try:
        search_term = request.args.get('search', '')
        availability = request.args.get('availability', '')
        page = int(request.args.get('page', 1))
        per_page = 10
        
        if db:
            query = db.collection('users').where('profile_visibility', '==', 'public')
            
            if availability:
                query = query.where('availability', '==', availability)
            
            # Note: Firestore doesn't support text search natively
            # For production, consider using Algolia or implement full-text search
            users = query.limit(per_page).offset((page - 1) * per_page).stream()
            
            profiles = []
            for user in users:
                user_data = user.to_dict()
                user_data['id'] = user.id
                
                # Simple text search in skills
                if search_term:
                    skills_text = f"{user_data.get('skills_offered', '')} {user_data.get('skills_wanted', '')}".lower()
                    if search_term.lower() not in skills_text:
                        continue
                
                profiles.append(user_data)
            
            return jsonify({'profiles': profiles, 'page': page})
        else:
            return jsonify({'profiles': [], 'page': page})
            
    except Exception as e:
        print(f"Search profiles error: {e}")
        return jsonify({'profiles': [], 'page': 1})

@app.route('/api/admin/users')
@admin_required
def api_admin_users():
    try:
        if db:
            users = db.collection('users').stream()
            users_list = []
            
            for user in users:
                user_data = user.to_dict()
                user_data['id'] = user.id
                users_list.append(user_data)
            
            return jsonify({'users': users_list})
        else:
            return jsonify({'users': []})
            
    except Exception as e:
        print(f"Admin users error: {e}")
        return jsonify({'users': []})

@app.route('/api/admin/ban_user', methods=['POST'])
@admin_required
def api_ban_user():
    try:
        if db:
            user_id = request.form['user_id']
            reason = request.form['reason']
            
            update_data = {
                'status': 'banned',
                'ban_reason': reason,
                'banned_at': datetime.now(),
                'banned_by': session['user_id']
            }
            
            db.collection('users').document(user_id).update(update_data)
            return jsonify({'success': True, 'message': 'User banned successfully'})
        else:
            return jsonify({'success': False, 'message': 'Database not available'})
            
    except Exception as e:
        print(f"Ban user error: {e}")
        return jsonify({'success': False, 'message': 'Error banning user'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
