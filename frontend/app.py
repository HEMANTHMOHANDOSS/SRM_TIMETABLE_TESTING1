"""
Flask Frontend Application for SRM Timetable Management System
Provides web interface for all timetable management operations
"""

import os
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv

load_dotenv()

class User(UserMixin):
    """User class for Flask-Login"""
    def __init__(self, user_data):
        self.id = user_data['id']
        self.email = user_data['email']
        self.name = user_data['name']
        self.user_type = user_data['user_type']
        self.token = user_data.get('token')
        
        # Staff-specific attributes
        if self.user_type == 'staff':
            self.role = user_data.get('role')
            self.department_id = user_data.get('department_id')
            self.department_name = user_data.get('department_name')
            self.is_department_admin = user_data.get('is_department_admin', False)
            self.max_subjects = user_data.get('max_subjects', 1)

def create_flask_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key')
    
    # Configure Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # API Base URL
    API_BASE_URL = f"http://{os.getenv('FASTAPI_HOST', '127.0.0.1')}:{os.getenv('FASTAPI_PORT', 8000)}/api"
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user for Flask-Login"""
        if 'user_data' in session:
            return User(session['user_data'])
        return None
    
    def make_api_request(endpoint, method='GET', data=None, token=None):
        """Make API request to FastAPI backend"""
        url = f"{API_BASE_URL}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=data)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            
            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            else:
                return {'error': response.json().get('detail', 'API request failed')}
        except Exception as e:
            return {'error': str(e)}
    
    # Routes
    @app.route('/')
    def index():
        """Home page"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page"""
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            user_type = request.form.get('user_type', 'staff')
            
            # Make login request to API
            response = make_api_request('/auth/login', 'POST', {
                'email': email,
                'password': password,
                'user_type': user_type
            })
            
            if 'error' in response:
                flash(response['error'], 'error')
            else:
                # Store user data in session
                user_data = response['user']
                user_data['token'] = response['access_token']
                session['user_data'] = user_data
                
                # Login user
                user = User(user_data)
                login_user(user)
                
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
        
        return render_template('login.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """Registration page"""
        departments = []
        
        # Get departments for dropdown
        dept_response = make_api_request('/departments')
        if 'error' not in dept_response:
            departments = dept_response
        
        if request.method == 'POST':
            data = {
                'name': request.form['name'],
                'email': request.form['email'],
                'password': request.form['password'],
                'role': request.form['role'],
                'department_id': int(request.form['department_id'])
            }
            
            response = make_api_request('/auth/register', 'POST', data)
            
            if 'error' in response:
                flash(response['error'], 'error')
            else:
                flash('Registration successful! Please login.', 'success')
                return redirect(url_for('login'))
        
        return render_template('register.html', departments=departments)
    
    @app.route('/logout')
    @login_required
    def logout():
        """Logout"""
        logout_user()
        session.clear()
        flash('You have been logged out.', 'info')
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Dashboard page"""
        # Get dashboard statistics
        stats = {}
        
        if current_user.user_type == 'main_admin':
            # Get all departments, staff, subjects
            departments = make_api_request('/departments', token=current_user.token)
            staff = make_api_request('/staff', token=current_user.token)
            subjects = make_api_request('/subjects', token=current_user.token)
            
            stats = {
                'total_departments': len(departments) if 'error' not in departments else 0,
                'total_staff': len(staff) if 'error' not in staff else 0,
                'total_subjects': len(subjects) if 'error' not in subjects else 0,
                'assigned_subjects': len([s for s in subjects if s.get('assigned_staff_id')]) if 'error' not in subjects else 0
            }
        else:
            # Get department-specific stats
            dept_staff = make_api_request(f'/staff?department_id={current_user.department_id}', token=current_user.token)
            dept_subjects = make_api_request(f'/subjects?department_id={current_user.department_id}', token=current_user.token)
            my_subjects = make_api_request(f'/staff/{current_user.id}/subjects', token=current_user.token)
            
            stats = {
                'department_staff': len(dept_staff) if 'error' not in dept_staff else 0,
                'department_subjects': len(dept_subjects) if 'error' not in dept_subjects else 0,
                'my_subjects': len(my_subjects) if 'error' not in my_subjects else 0,
                'max_subjects': current_user.max_subjects
            }
        
        return render_template('dashboard.html', stats=stats)
    
    @app.route('/departments')
    @login_required
    def departments():
        """Departments management page"""
        if current_user.user_type != 'main_admin':
            flash('Access denied. Main admin only.', 'error')
            return redirect(url_for('dashboard'))
        
        departments = make_api_request('/departments', token=current_user.token)
        if 'error' in departments:
            departments = []
            flash(departments['error'], 'error')
        
        return render_template('departments.html', departments=departments)
    
    @app.route('/staff')
    @login_required
    def staff():
        """Staff management page"""
        # Get staff based on user permissions
        if current_user.user_type == 'main_admin':
            staff_list = make_api_request('/staff', token=current_user.token)
        else:
            staff_list = make_api_request(f'/staff?department_id={current_user.department_id}', token=current_user.token)
        
        if 'error' in staff_list:
            staff_list = []
            flash(staff_list['error'], 'error')
        
        # Get departments for dropdown
        departments = make_api_request('/departments', token=current_user.token)
        if 'error' in departments:
            departments = []
        
        return render_template('staff.html', staff_list=staff_list, departments=departments)
    
    @app.route('/subjects')
    @login_required
    def subjects():
        """Subjects management page"""
        # Get subjects based on user permissions
        if current_user.user_type == 'main_admin':
            subjects_list = make_api_request('/subjects', token=current_user.token)
        else:
            subjects_list = make_api_request(f'/subjects?department_id={current_user.department_id}', token=current_user.token)
        
        if 'error' in subjects_list:
            subjects_list = []
            flash(subjects_list['error'], 'error')
        
        # Get departments and staff for dropdowns
        departments = make_api_request('/departments', token=current_user.token)
        staff_list = make_api_request('/staff', token=current_user.token)
        
        if 'error' in departments:
            departments = []
        if 'error' in staff_list:
            staff_list = []
        
        return render_template('subjects.html', 
                             subjects=subjects_list, 
                             departments=departments, 
                             staff_list=staff_list)
    
    @app.route('/timetable')
    @login_required
    def timetable():
        """Timetable management page"""
        # Get departments for dropdown
        if current_user.user_type == 'main_admin':
            departments = make_api_request('/departments', token=current_user.token)
        else:
            # Get only user's department
            dept_response = make_api_request(f'/departments/{current_user.department_id}', token=current_user.token)
            departments = [dept_response] if 'error' not in dept_response else []
        
        if 'error' in departments:
            departments = []
        
        return render_template('timetable.html', departments=departments)
    
    @app.route('/my-subjects')
    @login_required
    def my_subjects():
        """My subjects page for staff"""
        if current_user.user_type == 'main_admin':
            flash('This page is for staff members only.', 'error')
            return redirect(url_for('dashboard'))
        
        subjects = make_api_request(f'/staff/{current_user.id}/subjects', token=current_user.token)
        if 'error' in subjects:
            subjects = []
            flash(subjects['error'], 'error')
        
        return render_template('my_subjects.html', subjects=subjects)
    
    @app.route('/my-timetable')
    @login_required
    def my_timetable():
        """My timetable page for staff"""
        if current_user.user_type == 'main_admin':
            flash('This page is for staff members only.', 'error')
            return redirect(url_for('dashboard'))
        
        timetable = make_api_request(f'/timetable?staff_id={current_user.id}', token=current_user.token)
        if 'error' in timetable:
            timetable = []
            flash(timetable['error'], 'error')
        
        return render_template('my_timetable.html', timetable=timetable)
    
    # API endpoints for AJAX requests
    @app.route('/api/generate-timetable', methods=['POST'])
    @login_required
    def api_generate_timetable():
        """Generate timetable via AJAX"""
        data = request.get_json()
        response = make_api_request('/timetable/generate', 'POST', data, current_user.token)
        return jsonify(response)
    
    @app.route('/api/export-timetable')
    @login_required
    def api_export_timetable():
        """Export timetable to Excel"""
        department_id = request.args.get('department_id')
        semester = request.args.get('semester')
        section = request.args.get('section')
        
        # Make request to FastAPI export endpoint
        url = f"{API_BASE_URL}/timetable/export"
        params = {
            'department_id': department_id,
            'semester': semester,
            'section': section
        }
        headers = {'Authorization': f'Bearer {current_user.token}'}
        
        try:
            response = requests.get(url, params=params, headers=headers)
            if response.status_code == 200:
                return send_file(
                    BytesIO(response.content),
                    as_attachment=True,
                    download_name=f'timetable_{department_id}_{semester}_{section}.xlsx',
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            else:
                flash('Failed to export timetable', 'error')
                return redirect(url_for('timetable'))
        except Exception as e:
            flash(f'Export error: {str(e)}', 'error')
            return redirect(url_for('timetable'))
    
    return app

if __name__ == "__main__":
    app = create_flask_app()
    app.run(debug=True)