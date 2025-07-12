from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
# Flask-Admin import commented out temporarily due to installation issues
# from flask_admin import Admin, BaseView, expose
# from flask_admin.contrib.sqla import ModelView
import sqlite3
from datetime import datetime, date
import os
from functools import wraps
import hashlib
import json

# Chart libraries
try:
    import plotly.graph_objects as go
    import plotly.express as px
    import plotly.utils
    import pandas as pd
    PLOTLY_AVAILABLE = True
    print("✅ Plotly and Pandas imported successfully!")
except ImportError as e:
    PLOTLY_AVAILABLE = False
    print(f"❌ Warning: Plotly/Pandas not available. Error: {e}")
    print("Charts will be disabled.")

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Database configuration
DATABASE = 'automotive_service.db'

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    """Decorator to require login for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'customer_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin access for certain routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Simple admin check - in production, implement proper admin authentication
        if 'admin_authenticated' not in session:
            flash('Admin access required.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_customer():
    """Get current logged in customer"""
    if 'customer_id' not in session:
        return None
    
    conn = get_db_connection()
    customer = conn.execute(
        'SELECT * FROM customers WHERE id = ?', 
        (session['customer_id'],)
    ).fetchone()
    conn.close()
    return customer

# Authentication Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Customer login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        customer = conn.execute(
            'SELECT * FROM customers WHERE email = ? AND password = ?',
            (email, hash_password(password))
        ).fetchone()
        conn.close()
        
        if customer:
            session['customer_id'] = customer['id']
            session['customer_name'] = f"{customer['first_name']} {customer['last_name']}"
            flash(f'Welcome back, {customer["first_name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Customer registration"""
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        phone = request.form['phone']
        address = request.form.get('address', '')  # Optional field, default to empty string
        
        # Validation
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        conn = get_db_connection()
        
        # Check if email already exists
        existing_customer = conn.execute(
            'SELECT id FROM customers WHERE email = ?', (email,)
        ).fetchone()
        
        if existing_customer:
            flash('Email already registered. Please use a different email.', 'error')
            conn.close()
            return render_template('register.html')
        
        try:
            conn.execute('''
                INSERT INTO customers (first_name, last_name, email, password, phone, address)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (first_name, last_name, email, hash_password(password), phone, address))
            conn.commit()
            
            # Auto-login after registration
            customer = conn.execute(
                'SELECT * FROM customers WHERE email = ?', (email,)
            ).fetchone()
            
            session['customer_id'] = customer['id']
            session['customer_name'] = f"{customer['first_name']} {customer['last_name']}"
            
            flash('Registration successful! Welcome to our service center.', 'success')
            return redirect(url_for('dashboard'))
            
        except sqlite3.Error as e:
            flash('Registration failed. Please try again.', 'error')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Customer logout"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))

# Main Routes
@app.route('/')
def index():
    """Home page - public"""
    conn = get_db_connection()
    
    # Get available services for display
    services = conn.execute(
        'SELECT * FROM services WHERE is_active = 1 ORDER BY name'
    ).fetchall()
    
    conn.close()
    
    # Check if user is logged in
    current_customer = get_current_customer()
    
    return render_template('index.html', 
                         services=services,
                         current_customer=current_customer)

@app.route('/dashboard')
@login_required
def dashboard():
    """Customer dashboard - shows only logged in customer's data"""
    customer_id = session['customer_id']
    conn = get_db_connection()
    
    # Get customer's vehicles
    vehicles = conn.execute(
        'SELECT * FROM vehicles WHERE customer_id = ? ORDER BY year DESC, make, model',
        (customer_id,)
    ).fetchall()
    
    # Get customer's appointments
    appointments = conn.execute('''
        SELECT a.*, v.make, v.model, v.year, s.name as service_name, s.price
        FROM appointments a
        JOIN vehicles v ON a.vehicle_id = v.id
        JOIN services s ON a.service_id = s.id
        WHERE a.customer_id = ?
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
    ''', (customer_id,)).fetchall()
    
    # Get upcoming appointments
    upcoming_appointments = conn.execute('''
        SELECT a.*, v.make, v.model, v.year, s.name as service_name, s.price
        FROM appointments a
        JOIN vehicles v ON a.vehicle_id = v.id
        JOIN services s ON a.service_id = s.id
        WHERE a.customer_id = ? AND a.appointment_date >= date('now')
        ORDER BY a.appointment_date ASC, a.appointment_time ASC
    ''', (customer_id,)).fetchall()
    
    conn.close()
    
    current_customer = get_current_customer()
    
    return render_template('dashboard.html',
                         current_customer=current_customer,
                         vehicles=vehicles,
                         appointments=appointments,
                         upcoming_appointments=upcoming_appointments)

# Vehicle Routes (Customer-specific)
@app.route('/my-vehicles')
@login_required
def my_vehicles():
    """List customer's vehicles only"""
    customer_id = session['customer_id']
    conn = get_db_connection()
    vehicles = conn.execute(
        'SELECT * FROM vehicles WHERE customer_id = ? ORDER BY year DESC, make, model',
        (customer_id,)
    ).fetchall()
    conn.close()
    
    current_customer = get_current_customer()
    return render_template('vehicles.html', vehicles=vehicles, current_customer=current_customer)

@app.route('/vehicles/add', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    """Add vehicle for logged in customer"""
    if request.method == 'POST':
        customer_id = session['customer_id']
        make = request.form['make']
        model = request.form['model']
        year = int(request.form['year'])
        vin = request.form['vin']
        license_plate = request.form['license_plate']
        color = request.form['color']
        mileage = int(request.form['mileage']) if request.form['mileage'] else None
        
        conn = get_db_connection()
        try:
            conn.execute('''
                INSERT INTO vehicles (customer_id, make, model, year, vin, license_plate, color, mileage)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (customer_id, make, model, year, vin, license_plate, color, mileage))
            conn.commit()
            flash('Vehicle added successfully!', 'success')
            return redirect(url_for('my_vehicles'))
        except sqlite3.Error as e:
            flash('Error adding vehicle. Please check your input.', 'error')
        finally:
            conn.close()
    
    current_customer = get_current_customer()
    return render_template('add_vehicle.html', current_customer=current_customer)

# Appointment Routes (Customer-specific)
@app.route('/my-appointments')
@login_required
def my_appointments():
    """List customer's appointments only"""
    customer_id = session['customer_id']
    conn = get_db_connection()
    
    appointments = conn.execute('''
        SELECT a.*, v.make, v.model, v.year, s.name as service_name, s.price, s.estimated_duration
        FROM appointments a
        JOIN vehicles v ON a.vehicle_id = v.id
        JOIN services s ON a.service_id = s.id
        WHERE a.customer_id = ?
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
    ''', (customer_id,)).fetchall()
    
    conn.close()
    
    current_customer = get_current_customer()
    return render_template('appointments.html', appointments=appointments, current_customer=current_customer)

@app.route('/appointments/add', methods=['GET', 'POST'])
@login_required
def add_appointment():
    """Add appointment for logged in customer"""
    customer_id = session['customer_id']
    conn = get_db_connection()
    
    if request.method == 'POST':
        vehicle_id = int(request.form['vehicle_id'])
        service_id = int(request.form['service_id'])
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        notes = request.form.get('notes', '')  # Optional field, default to empty string
        
        # Verify vehicle belongs to customer
        vehicle = conn.execute(
            'SELECT * FROM vehicles WHERE id = ? AND customer_id = ?',
            (vehicle_id, customer_id)
        ).fetchone()
        
        if not vehicle:
            flash('Invalid vehicle selection.', 'error')
            conn.close()
            return redirect(url_for('add_appointment'))
        
        try:
            conn.execute('''
                INSERT INTO appointments (customer_id, vehicle_id, service_id, appointment_date, appointment_time, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (customer_id, vehicle_id, service_id, appointment_date, appointment_time, notes))
            conn.commit()
            flash('Appointment scheduled successfully!', 'success')
            return redirect(url_for('my_appointments'))
        except sqlite3.Error as e:
            flash('Error scheduling appointment. Please try again.', 'error')
        finally:
            conn.close()
    
    # Get customer's vehicles and available services
    vehicles = conn.execute(
        'SELECT * FROM vehicles WHERE customer_id = ? ORDER BY make, model',
        (customer_id,)
    ).fetchall()
    
    # Check if customer has any vehicles
    if not vehicles:
        flash('You need to add a vehicle first before scheduling an appointment.', 'warning')
        conn.close()
        return redirect(url_for('add_vehicle'))
    
    services = conn.execute(
        'SELECT * FROM services WHERE is_active = 1 ORDER BY name'
    ).fetchall()
    
    conn.close()
    
    current_customer = get_current_customer()
    return render_template('add_appointment.html', 
                         vehicles=vehicles, 
                         services=services,
                         current_customer=current_customer)

@app.route('/appointments/cancel/<int:appointment_id>', methods=['POST'])
@login_required
def cancel_appointment(appointment_id):
    """Cancel customer's appointment"""
    customer_id = session['customer_id']
    conn = get_db_connection()
    
    try:
        # Verify appointment belongs to customer and can be cancelled
        appointment = conn.execute(
            'SELECT * FROM appointments WHERE id = ? AND customer_id = ?',
            (appointment_id, customer_id)
        ).fetchone()
        
        if not appointment:
            flash('Appointment not found.', 'error')
            return redirect(url_for('my_appointments'))
        
        if appointment['status'] == 'cancelled':
            flash('Appointment is already cancelled.', 'warning')
            return redirect(url_for('my_appointments'))
        
        if appointment['status'] == 'completed':
            flash('Cannot cancel completed appointment.', 'warning')
            return redirect(url_for('my_appointments'))
        
        # Update appointment status to cancelled
        conn.execute(
            'UPDATE appointments SET status = ? WHERE id = ?',
            ('cancelled', appointment_id)
        )
        conn.commit()
        flash('Appointment cancelled successfully.', 'success')
        
    except sqlite3.Error as e:
        flash('Error cancelling appointment. Please try again.', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('my_appointments'))

@app.route('/appointments/edit/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def edit_appointment(appointment_id):
    """Edit customer's appointment"""
    customer_id = session['customer_id']
    conn = get_db_connection()
    
    # Verify appointment belongs to customer
    appointment = conn.execute(
        'SELECT * FROM appointments WHERE id = ? AND customer_id = ?',
        (appointment_id, customer_id)
    ).fetchone()
    
    if not appointment:
        flash('Appointment not found.', 'error')
        conn.close()
        return redirect(url_for('my_appointments'))
    
    if appointment['status'] != 'scheduled':
        flash('Only scheduled appointments can be edited.', 'warning')
        conn.close()
        return redirect(url_for('my_appointments'))
    
    if request.method == 'POST':
        vehicle_id = int(request.form['vehicle_id'])
        service_id = int(request.form['service_id'])
        appointment_date = request.form['appointment_date']
        appointment_time = request.form['appointment_time']
        notes = request.form.get('notes', '')
        
        # Verify vehicle belongs to customer
        vehicle = conn.execute(
            'SELECT * FROM vehicles WHERE id = ? AND customer_id = ?',
            (vehicle_id, customer_id)
        ).fetchone()
        
        if not vehicle:
            flash('Invalid vehicle selection.', 'error')
            conn.close()
            return redirect(url_for('edit_appointment', appointment_id=appointment_id))
        
        try:
            conn.execute('''
                UPDATE appointments 
                SET vehicle_id = ?, service_id = ?, appointment_date = ?, appointment_time = ?, notes = ?
                WHERE id = ? AND customer_id = ?
            ''', (vehicle_id, service_id, appointment_date, appointment_time, notes, appointment_id, customer_id))
            conn.commit()
            flash('Appointment updated successfully!', 'success')
            return redirect(url_for('my_appointments'))
        except sqlite3.Error as e:
            flash('Error updating appointment. Please try again.', 'error')
        finally:
            conn.close()
    
    # Get customer's vehicles and available services for the form
    vehicles = conn.execute(
        'SELECT * FROM vehicles WHERE customer_id = ? ORDER BY make, model',
        (customer_id,)
    ).fetchall()
    
    services = conn.execute(
        'SELECT * FROM services WHERE is_active = 1 ORDER BY name'
    ).fetchall()
    
    conn.close()
    
    current_customer = get_current_customer()
    return render_template('edit_appointment.html', 
                         appointment=appointment,
                         vehicles=vehicles, 
                         services=services,
                         current_customer=current_customer)

# Profile Routes
@app.route('/profile')
@login_required
def profile():
    """View customer profile"""
    current_customer = get_current_customer()
    return render_template('profile.html', current_customer=current_customer)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit customer profile"""
    customer_id = session['customer_id']
    
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone = request.form['phone']
        address = request.form['address']
        
        conn = get_db_connection()
        try:
            conn.execute('''
                UPDATE customers 
                SET first_name = ?, last_name = ?, phone = ?, address = ?
                WHERE id = ?
            ''', (first_name, last_name, phone, address, customer_id))
            conn.commit()
            
            # Update session name
            session['customer_name'] = f"{first_name} {last_name}"
            
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        except sqlite3.Error as e:
            flash('Error updating profile. Please try again.', 'error')
        finally:
            conn.close()
    
    current_customer = get_current_customer()
    return render_template('edit_profile.html', current_customer=current_customer)

# Services Route (Public)
@app.route('/services')
def services():
    """List all available services"""
    conn = get_db_connection()
    services = conn.execute(
        'SELECT * FROM services WHERE is_active = 1 ORDER BY name'
    ).fetchall()
    conn.close()
    
    current_customer = get_current_customer()
    return render_template('services.html', services=services, current_customer=current_customer)

# API Routes for AJAX (Customer-specific)
@app.route('/api/my-vehicles')
@login_required
def api_my_vehicles():
    """API endpoint to get customer's vehicles"""
    customer_id = session['customer_id']
    conn = get_db_connection()
    vehicles = conn.execute(
        'SELECT * FROM vehicles WHERE customer_id = ? ORDER BY make, model',
        (customer_id,)
    ).fetchall()
    conn.close()
    
    return jsonify([dict(vehicle) for vehicle in vehicles])

# API Routes for Admin Charts
@app.route('/admin/api/chart-data')
@admin_required
def admin_chart_data():
    """API endpoint to get chart data for admin dashboard"""
    conn = get_db_connection()
    
    # Monthly appointments trend (last 12 months)
    monthly_appointments = conn.execute('''
        SELECT 
            strftime('%Y-%m', appointment_date) as month,
            COUNT(*) as appointment_count,
            SUM(s.price) as revenue
        FROM appointments a
        JOIN services s ON a.service_id = s.id
        WHERE a.appointment_date >= date('now', '-12 months')
        GROUP BY strftime('%Y-%m', appointment_date)
        ORDER BY month
    ''').fetchall()
    
    # Service popularity
    service_popularity = conn.execute('''
        SELECT 
            s.name,
            COUNT(a.id) as appointment_count,
            SUM(CASE WHEN a.status = 'completed' THEN s.price ELSE 0 END) as revenue
        FROM services s
        LEFT JOIN appointments a ON s.id = a.service_id
        GROUP BY s.id, s.name
        ORDER BY appointment_count DESC
        LIMIT 10
    ''').fetchall()
    
    # Appointment status distribution
    appointment_status = conn.execute('''
        SELECT 
            status,
            COUNT(*) as count
        FROM appointments
        GROUP BY status
        ORDER BY count DESC
    ''').fetchall()
    
    # Top customers by spending
    top_customers = conn.execute('''
        SELECT 
            c.first_name || ' ' || c.last_name as customer_name,
            COUNT(a.id) as appointment_count,
            SUM(CASE WHEN a.status = 'completed' THEN s.price ELSE 0 END) as total_spent
        FROM customers c
        LEFT JOIN appointments a ON c.id = a.customer_id
        LEFT JOIN services s ON a.service_id = s.id
        GROUP BY c.id, c.first_name, c.last_name
        HAVING total_spent > 0
        ORDER BY total_spent DESC
        LIMIT 10
    ''').fetchall()
    
    # Vehicle make distribution
    vehicle_makes = conn.execute('''
        SELECT 
            make,
            COUNT(*) as count
        FROM vehicles
        GROUP BY make
        ORDER BY count DESC
        LIMIT 10
    ''').fetchall()
    
    # Daily appointment hours distribution
    appointment_hours = conn.execute('''
        SELECT 
            strftime('%H', appointment_time) as hour,
            COUNT(*) as count
        FROM appointments
        GROUP BY strftime('%H', appointment_time)
        ORDER BY hour
    ''').fetchall()
    
    # Weekly appointment trends
    weekly_appointments = conn.execute('''
        SELECT 
            CASE strftime('%w', appointment_date)
                WHEN '0' THEN 'Sunday'
                WHEN '1' THEN 'Monday'
                WHEN '2' THEN 'Tuesday'
                WHEN '3' THEN 'Wednesday'
                WHEN '4' THEN 'Thursday'
                WHEN '5' THEN 'Friday'
                WHEN '6' THEN 'Saturday'
            END as day_of_week,
            COUNT(*) as count
        FROM appointments
        GROUP BY strftime('%w', appointment_date)
        ORDER BY strftime('%w', appointment_date)
    ''').fetchall()
    
    conn.close()
    
    return jsonify({
        'monthly_appointments': [dict(row) for row in monthly_appointments],
        'service_popularity': [dict(row) for row in service_popularity],
        'appointment_status': [dict(row) for row in appointment_status],
        'top_customers': [dict(row) for row in top_customers],
        'vehicle_makes': [dict(row) for row in vehicle_makes],
        'appointment_hours': [dict(row) for row in appointment_hours],
        'weekly_appointments': [dict(row) for row in weekly_appointments]
    })

# Chart Generation Functions
def create_monthly_revenue_chart(data):
    """Create monthly revenue line chart"""
    if not PLOTLY_AVAILABLE:
        return None
    
    if not data:
        # Create empty chart with sample data
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            y=[0, 0, 0, 0, 0, 0],
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ))
        fig.update_layout(
            title='Monthly Revenue Trend',
            xaxis_title='Month',
            yaxis_title='Revenue ($)',
            template='plotly_white',
            height=400
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    df = pd.DataFrame(data)
    fig = px.line(df, x='month', y='revenue', 
                  title='Monthly Revenue Trend',
                  markers=True)
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Revenue ($)',
        template='plotly_white',
        height=400
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_service_popularity_chart(data):
    """Create service popularity bar chart"""
    if not PLOTLY_AVAILABLE:
        return None
    
    if not data:
        # Create empty chart with sample data
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Oil Change', 'Brake Service', 'Tire Rotation'],
            y=[0, 0, 0],
            marker_color=['#ff7f0e', '#2ca02c', '#d62728']
        ))
        fig.update_layout(
            title='Most Popular Services',
            xaxis_title='Service',
            yaxis_title='Number of Appointments',
            template='plotly_white',
            height=400
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    df = pd.DataFrame(data)
    fig = px.bar(df, x='name', y='appointment_count',
                 title='Most Popular Services',
                 color='appointment_count',
                 color_continuous_scale='viridis')
    fig.update_layout(
        xaxis_title='Service',
        yaxis_title='Number of Appointments',
        template='plotly_white',
        height=400
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_appointment_status_chart(data):
    """Create appointment status pie chart"""
    if not PLOTLY_AVAILABLE:
        return None
        
    if not data:
        # Create empty chart with sample data
        fig = go.Figure(data=[go.Pie(
            labels=['Scheduled', 'Completed', 'Cancelled'],
            values=[1, 1, 1],
            hole=0.3
        )])
        fig.update_layout(
            title='Appointment Status Distribution',
            template='plotly_white',
            height=400
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    df = pd.DataFrame(data)
    fig = px.pie(df, values='count', names='status',
                 title='Appointment Status Distribution',
                 hole=0.3,
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_layout(
        template='plotly_white',
        height=400
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_vehicle_makes_chart(data):
    """Create vehicle makes donut chart"""
    if not PLOTLY_AVAILABLE:
        return None
        
    if not data:
        # Create empty chart with sample data
        fig = go.Figure(data=[go.Pie(
            labels=['Toyota', 'Honda', 'Ford', 'BMW'],
            values=[1, 1, 1, 1],
            hole=0.4
        )])
        fig.update_layout(
            title='Customer Vehicle Brands',
            template='plotly_white',
            height=400
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    df = pd.DataFrame(data)
    fig = px.pie(df, values='count', names='make',
                 title='Customer Vehicle Brands',
                 hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_layout(
        template='plotly_white',
        height=400
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_appointment_hours_chart(data):
    """Create appointment hours bar chart"""
    if not PLOTLY_AVAILABLE:
        return None
        
    if not data:
        # Create empty chart with sample data
        hours = ['09', '10', '11', '12', '13', '14', '15', '16', '17']
        counts = [1, 2, 3, 4, 5, 4, 3, 2, 1]
        fig = go.Figure(data=[go.Bar(x=hours, y=counts)])
        fig.update_layout(
            title='Busiest Hours of the Day',
            xaxis_title='Hour',
            yaxis_title='Number of Appointments',
            template='plotly_white',
            height=400
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    df = pd.DataFrame(data)
    fig = px.bar(df, x='hour', y='count',
                 title='Busiest Hours of the Day',
                 color='count',
                 color_continuous_scale='blues')
    fig.update_layout(
        xaxis_title='Hour',
        yaxis_title='Number of Appointments',
        template='plotly_white',
        height=400
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_weekly_appointments_chart(data):
    """Create weekly appointments radar chart"""
    if not PLOTLY_AVAILABLE:
        return None
        
    if not data:
        # Create empty chart with sample data
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        counts = [10, 12, 15, 18, 20, 8, 5]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=counts,
            theta=days,
            fill='toself',
            name='Appointments'
        ))
        fig.update_layout(
            title='Weekly Appointment Pattern',
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(counts)]
                )),
            template='plotly_white',
            height=400
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    df = pd.DataFrame(data)
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=df['count'],
        theta=df['day_of_week'],
        fill='toself',
        name='Appointments',
        line_color='rgb(32, 201, 151)'
    ))
    fig.update_layout(
        title='Weekly Appointment Pattern',
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, df['count'].max() if len(df) > 0 else 10]
            )),
        template='plotly_white',
        height=400
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def create_top_customers_chart(data):
    """Create top customers horizontal bar chart"""
    if not PLOTLY_AVAILABLE:
        return None
        
    if not data:
        # Create empty chart with sample data
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[100, 200, 300],
            y=['Customer A', 'Customer B', 'Customer C'],
            orientation='h',
            marker_color='lightblue'
        ))
        fig.update_layout(
            title='Top Customers by Spending',
            xaxis_title='Total Spent ($)',
            yaxis_title='Customer',
            template='plotly_white',
            height=400
        )
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    df = pd.DataFrame(data)
    fig = px.bar(df, x='total_spent', y='customer_name',
                 title='Top Customers by Spending',
                 orientation='h',
                 color='total_spent',
                 color_continuous_scale='greens')
    fig.update_layout(
        xaxis_title='Total Spent ($)',
        yaxis_title='Customer',
        template='plotly_white',
        height=400
    )
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    """Admin analytics dashboard with beautiful charts"""
    if not PLOTLY_AVAILABLE:
        flash('Charts are not available. Please install plotly and pandas.', 'warning')
        return redirect(url_for('admin_dashboard'))
    
    conn = get_db_connection()
    
    # Get data for all charts
    # Service popularity
    service_popularity = conn.execute('''
        SELECT 
            s.name,
            COUNT(a.id) as appointment_count,
            SUM(CASE WHEN a.status = 'completed' THEN s.price ELSE 0 END) as revenue
        FROM services s
        LEFT JOIN appointments a ON s.id = a.service_id
        WHERE s.is_active = 1
        GROUP BY s.id, s.name
        ORDER BY appointment_count DESC
        LIMIT 10
    ''').fetchall()
    
    # Vehicle make distribution
    vehicle_makes = conn.execute('''
        SELECT 
            make,
            COUNT(*) as count
        FROM vehicles
        GROUP BY make
        ORDER BY count DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    # Convert to list of dicts
    service_popularity_data = [dict(row) for row in service_popularity]
    vehicle_makes_data = [dict(row) for row in vehicle_makes]
    
    # Create charts
    popularity_chart = create_service_popularity_chart(service_popularity_data)
    makes_chart = create_vehicle_makes_chart(vehicle_makes_data)
    
    return render_template('admin_analytics.html',
                         popularity_chart=popularity_chart,
                         makes_chart=makes_chart,
                         plotly_available=PLOTLY_AVAILABLE)

# Admin Authentication Routes
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Simple admin login - replace with proper authentication in production"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Simple hardcoded admin credentials - CHANGE IN PRODUCTION
        if username == 'admin' and password == 'admin123':
            session['admin_authenticated'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials.', 'error')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_authenticated', None)
    flash('Admin logged out successfully.', 'info')
    return redirect(url_for('index'))

# Admin Dashboard Routes
@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard with overview statistics"""
    conn = get_db_connection()
    
    # Get statistics
    stats = {}
    
    # Customer statistics
    customer_stats = conn.execute('''
        SELECT 
            COUNT(*) as total_customers,
            COUNT(CASE WHEN created_at >= date('now', '-30 days') THEN 1 END) as new_customers_30_days
        FROM customers
    ''').fetchone()
    stats['customers'] = dict(customer_stats)
    
    # Vehicle statistics
    vehicle_stats = conn.execute('''
        SELECT COUNT(*) as total_vehicles FROM vehicles
    ''').fetchone()
    stats['vehicles'] = dict(vehicle_stats)
    
    # Appointment statistics
    appointment_stats = conn.execute('''
        SELECT 
            COUNT(*) as total_appointments,
            COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled,
            COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress,
            COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
            COUNT(CASE WHEN status = 'cancelled' THEN 1 END) as cancelled
        FROM appointments
    ''').fetchone()
    stats['appointments'] = dict(appointment_stats)
    
    # Service statistics
    service_stats = conn.execute('''
        SELECT COUNT(*) as total_services FROM services WHERE is_active = 1
    ''').fetchone()
    stats['services'] = dict(service_stats)
    
    # Recent appointments
    recent_appointments = conn.execute('''
        SELECT 
            a.id,
            a.appointment_date,
            a.appointment_time,
            a.status,
            c.first_name,
            c.last_name,
            v.make,
            v.model,
            v.year,
            s.name as service_name
        FROM appointments a
        JOIN customers c ON a.customer_id = c.id
        JOIN vehicles v ON a.vehicle_id = v.id
        JOIN services s ON a.service_id = s.id
        ORDER BY a.created_at DESC
        LIMIT 10
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         stats=stats, 
                         recent_appointments=recent_appointments)

@app.route('/admin/customers')
@admin_required
def admin_customers():
    """Admin view of all customers"""
    conn = get_db_connection()
    
    customers = conn.execute('''
        SELECT 
            c.*,
            COUNT(DISTINCT v.id) as vehicle_count,
            COUNT(DISTINCT a.id) as appointment_count,
            MAX(a.appointment_date) as last_appointment
        FROM customers c
        LEFT JOIN vehicles v ON c.id = v.customer_id
        LEFT JOIN appointments a ON c.id = a.customer_id
        GROUP BY c.id
        ORDER BY c.last_name, c.first_name
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_customers.html', customers=customers)

@app.route('/admin/customers/delete/<int:customer_id>', methods=['POST'])
@admin_required
def admin_delete_customer(customer_id):
    """Admin hard delete customer and all related data"""
    conn = get_db_connection()
    
    try:
        # Get customer info for confirmation message
        customer = conn.execute(
            'SELECT first_name, last_name FROM customers WHERE id = ?',
            (customer_id,)
        ).fetchone()
        
        if not customer:
            flash('Customer not found.', 'error')
            return redirect(url_for('admin_customers'))
        
        # Delete all related data in correct order (due to foreign key constraints)
        # 1. Delete appointments first
        conn.execute('DELETE FROM appointments WHERE customer_id = ?', (customer_id,))
        
        # 2. Delete vehicles
        conn.execute('DELETE FROM vehicles WHERE customer_id = ?', (customer_id,))
        
        # 3. Finally delete customer
        conn.execute('DELETE FROM customers WHERE id = ?', (customer_id,))
        
        conn.commit()
        flash(f'Customer {customer["first_name"]} {customer["last_name"]} and all related data deleted successfully.', 'success')
        
    except sqlite3.Error as e:
        conn.rollback()
        flash('Error deleting customer. Please try again.', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin_customers'))

@app.route('/admin/vehicles')
@admin_required
def admin_vehicles():
    """Admin view of all vehicles"""
    conn = get_db_connection()
    
    vehicles = conn.execute('''
        SELECT 
            v.*,
            c.first_name,
            c.last_name,
            c.email,
            COUNT(a.id) as appointment_count
        FROM vehicles v
        JOIN customers c ON v.customer_id = c.id
        LEFT JOIN appointments a ON v.id = a.vehicle_id
        GROUP BY v.id
        ORDER BY c.last_name, c.first_name, v.year DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_vehicles.html', vehicles=vehicles)

@app.route('/admin/vehicles/delete/<int:vehicle_id>', methods=['POST'])
@admin_required
def admin_delete_vehicle(vehicle_id):
    """Admin hard delete vehicle and all related appointments"""
    conn = get_db_connection()
    
    try:
        # Get vehicle info for confirmation message
        vehicle = conn.execute(
            'SELECT v.make, v.model, v.year, c.first_name, c.last_name FROM vehicles v JOIN customers c ON v.customer_id = c.id WHERE v.id = ?',
            (vehicle_id,)
        ).fetchone()
        
        if not vehicle:
            flash('Vehicle not found.', 'error')
            return redirect(url_for('admin_vehicles'))
        
        # Delete all related appointments first
        conn.execute('DELETE FROM appointments WHERE vehicle_id = ?', (vehicle_id,))
        
        # Then delete the vehicle
        conn.execute('DELETE FROM vehicles WHERE id = ?', (vehicle_id,))
        
        conn.commit()
        flash(f'Vehicle {vehicle["year"]} {vehicle["make"]} {vehicle["model"]} (owned by {vehicle["first_name"]} {vehicle["last_name"]}) and all related appointments deleted successfully.', 'success')
        
    except sqlite3.Error as e:
        conn.rollback()
        flash('Error deleting vehicle. Please try again.', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin_vehicles'))

@app.route('/admin/appointments')
@admin_required
def admin_appointments():
    """Admin view of all appointments"""
    conn = get_db_connection()
    
    appointments = conn.execute('''
        SELECT 
            a.*,
            c.first_name,
            c.last_name,
            c.email,
            c.phone,
            v.make,
            v.model,
            v.year,
            v.license_plate,
            s.name as service_name,
            s.description as service_description,
            s.estimated_duration,
            s.price
        FROM appointments a
        JOIN customers c ON a.customer_id = c.id
        JOIN vehicles v ON a.vehicle_id = v.id
        JOIN services s ON a.service_id = s.id
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_appointments.html', appointments=appointments)

@app.route('/admin/services')
@admin_required
def admin_services():
    """Admin view of all services"""
    conn = get_db_connection()
    
    services = conn.execute('''
        SELECT 
            s.*,
            COUNT(a.id) as appointment_count,
            SUM(CASE WHEN a.status = 'completed' THEN s.price ELSE 0 END) as total_revenue
        FROM services s
        LEFT JOIN appointments a ON s.id = a.service_id
        GROUP BY s.id
        ORDER BY s.name
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin_services.html', services=services)

# Flask-Admin Setup (commented out due to installation issues)
# Will be implemented once Flask-Admin is properly installed

# Customer Authentication Routes

if __name__ == '__main__':
    # Check if database exists, if not run setup
    if not os.path.exists(DATABASE):
        print("Database not found. Please run setup.py first!")
        print("Run: python setup.py")
        exit(1)
    
    # Get port from environment variable for deployment
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
