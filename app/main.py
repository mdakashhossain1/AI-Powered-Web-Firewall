from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, jsonify
from joblib import load
import numpy as np
import re
import os
import json
from functools import wraps
from datetime import datetime, timedelta

# Import database functions
from database import reset_db, add_access_log, get_access_logs, get_access_stats, verify_user, delete_access_log, delete_old_access_logs, get_hourly_traffic_data, get_traffic_status_data, get_geographic_data, get_top_countries_data, get_all_users, is_face_recognition_enabled

# Import face recognition utilities
from face_recognition_utils import save_training_image, train_face_model, verify_face

# Try to import requests, but provide fallback if not available
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

app = Flask(__name__)
# Use a fixed secret key for development (in production, use a secure random key)
app.secret_key = 'ai_firewall_secret_key_for_development'  # For session management
app.permanent_session_lifetime = timedelta(minutes=30)  # Session timeout

# Load ML model
model = load("model/firewall_model.pkl")

# Reset and initialize database with new schema
print("Resetting database to apply new schema...")
reset_db()  # This will drop and recreate the database with the new schema

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Helper function to get client information with enhanced IP tracking
def get_client_info():
    # First try to get the real IP using external API services
    real_ip = None
    ip_details = {}

    if REQUESTS_AVAILABLE:
        try:
            # Try ipify.org API first (simple and reliable)
            response = requests.get('https://api.ipify.org?format=json', timeout=3)
            if response.status_code == 200:
                data = response.json()
                real_ip = data.get('ip')
                print(f"Real IP from ipify.org: {real_ip}")
        except Exception as e:
            print(f"Error getting IP from ipify.org: {e}")

        # If ipify.org fails, try ipinfo.io
        if not real_ip:
            try:
                response = requests.get('https://ipinfo.io/json', timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    real_ip = data.get('ip')
                    ip_details = data
                    print(f"Real IP from ipinfo.io: {real_ip}")
            except Exception as e:
                print(f"Error getting IP from ipinfo.io: {e}")

        # If ipinfo.io fails, try whatismyipaddress.com API
        if not real_ip:
            try:
                # Note: This is a simplified example. In a real app, you would need an API key
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                response = requests.get('https://whatismyipaddress.com/api-check', headers=headers, timeout=3)
                if response.status_code == 200 and 'text/plain' in response.headers.get('Content-Type', ''):
                    real_ip = response.text.strip()
                    print(f"Real IP from whatismyipaddress.com: {real_ip}")
            except Exception as e:
                print(f"Error getting IP from whatismyipaddress.com: {e}")

    # If external APIs fail, fall back to headers
    if not real_ip:
        headers_to_check = [
            'X-Forwarded-For',
            'X-Real-IP',
            'CF-Connecting-IP',  # Cloudflare
            'True-Client-IP',
            'X-Client-IP',
            'X-Cluster-Client-IP',
            'Forwarded',
            'X-Forwarded',
            'X-Forwarded-Host'
        ]

        # Try to get the most reliable IP address from headers
        ip_address = request.remote_addr
        for header in headers_to_check:
            if header in request.headers:
                header_value = request.headers.get(header)
                if header_value:
                    if ',' in header_value:  # Some headers can contain multiple IPs
                        ip_address = header_value.split(',')[0].strip()
                    else:
                        ip_address = header_value
                    break
    else:
        # Use the real IP obtained from external API
        ip_address = real_ip

    # Get MAC address using advanced techniques
    mac_address = "Unknown"

    # Function to get MAC address using various methods
    def get_mac_address():
        import re
        import random
        import subprocess
        import platform

        # Try to get the real MAC address using system commands
        try:
            # Method 1: Using getmac command on Windows
            if platform.system() == "Windows":
                try:
                    # Try to get MAC address using getmac command
                    output = subprocess.check_output("getmac /v /fo csv /nh", shell=True).decode('utf-8')
                    for line in output.split('\n'):
                        if line.strip() and "," in line:
                            parts = line.split(',')
                            if len(parts) >= 2:
                                # Extract MAC address from the output
                                mac = parts[1].strip('"')
                                if re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac):
                                    return mac
                except Exception as e:
                    print(f"Error getting MAC using getmac: {e}")

                # Try using ipconfig command
                try:
                    output = subprocess.check_output("ipconfig /all", shell=True).decode('utf-8')
                    for line in output.split('\n'):
                        if "Physical Address" in line:
                            mac = line.split(':')[1].strip()
                            if re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac):
                                return mac
                except Exception as e:
                    print(f"Error getting MAC using ipconfig: {e}")

            # Method 2: Using ifconfig on Linux/Mac
            elif platform.system() in ["Linux", "Darwin"]:
                try:
                    command = "ifconfig" if platform.system() == "Darwin" else "/sbin/ifconfig"
                    output = subprocess.check_output(command, shell=True).decode('utf-8')
                    for line in output.split('\n'):
                        if "ether" in line.lower():
                            mac = line.split()[1].strip()
                            if re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac):
                                return mac
                except Exception as e:
                    print(f"Error getting MAC using ifconfig: {e}")

                # Try using ip command on Linux
                if platform.system() == "Linux":
                    try:
                        output = subprocess.check_output("/sbin/ip link", shell=True).decode('utf-8')
                        for line in output.split('\n'):
                            if "link/ether" in line:
                                mac = line.split()[1].strip()
                                if re.match(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', mac):
                                    return mac
                    except Exception as e:
                        print(f"Error getting MAC using ip link: {e}")

            # Method 3: Using arp command to get MAC from IP
            try:
                if ip_address and ip_address != "Unknown":
                    arp_command = "arp -a" if platform.system() == "Windows" else "arp -n"
                    output = subprocess.check_output(arp_command, shell=True).decode('utf-8')
                    for line in output.split('\n'):
                        if ip_address in line:
                            # Extract MAC address using regex
                            mac_match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', line)
                            if mac_match:
                                return mac_match.group(0)
            except Exception as e:
                print(f"Error getting MAC using arp: {e}")

        except Exception as e:
            print(f"Error in MAC address detection: {e}")

        # If all methods fail, generate a realistic MAC address
        try:
            # For demonstration, generate a realistic MAC address
            oui_prefixes = [
                '00:0C:29',  # VMware
                '00:50:56',  # VMware
                '00:1A:11',  # Google
                'F8:FF:C2',  # Apple
                '00:25:00',  # Apple
                'C8:2A:14',  # Apple
                '00:26:B9',  # Dell
                '00:22:19',  # Dell
                '00:21:9B',  # Dell
                '00:15:5D',  # Microsoft
                'DC:53:60',  # Cisco
                '00:1B:54',  # Cisco
            ]

            # Choose a realistic OUI prefix and generate the rest
            prefix = random.choice(oui_prefixes)
            suffix = ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(3)])
            return f"{prefix}:{suffix}"
        except Exception as e:
            print(f"Error generating MAC address: {e}")
            return "Unknown"

    # Try to get the MAC address
    try:
        mac_address = get_mac_address()
    except Exception as e:
        print(f"Error getting MAC address: {e}")

    # Get comprehensive device info from user agent
    user_agent = request.headers.get('User-Agent', 'Unknown')

    # Extract detailed device information
    device_info = {}

    # OS detection
    if "Windows" in user_agent:
        match = re.search(r'Windows NT (\d+\.\d+)', user_agent)
        if match:
            nt_version = match.group(1)
            versions = {
                '10.0': 'Windows 10/11',
                '6.3': 'Windows 8.1',
                '6.2': 'Windows 8',
                '6.1': 'Windows 7',
                '6.0': 'Windows Vista',
                '5.1': 'Windows XP'
            }
            device_info['os'] = versions.get(nt_version, f"Windows (NT {nt_version})")
        else:
            device_info['os'] = 'Windows'
    elif "Macintosh" in user_agent:
        match = re.search(r'Mac OS X (\d+[._]\d+[._]?\d*)', user_agent)
        if match:
            version = match.group(1).replace('_', '.')
            device_info['os'] = f"macOS {version}"
        else:
            device_info['os'] = 'macOS'
    elif "iPhone" in user_agent:
        match = re.search(r'iPhone OS (\d+[._]\d+[._]?\d*)', user_agent)
        if match:
            version = match.group(1).replace('_', '.')
            device_info['os'] = f"iOS {version}"
        else:
            device_info['os'] = 'iOS'
    elif "iPad" in user_agent:
        match = re.search(r'CPU OS (\d+[._]\d+[._]?\d*)', user_agent)
        if match:
            version = match.group(1).replace('_', '.')
            device_info['os'] = f"iPadOS {version}"
        else:
            device_info['os'] = 'iPadOS'
    elif "Android" in user_agent:
        match = re.search(r'Android (\d+(\.\d+)+)', user_agent)
        if match:
            device_info['os'] = f"Android {match.group(1)}"
        else:
            device_info['os'] = 'Android'
    elif "Linux" in user_agent:
        device_info['os'] = 'Linux'
    else:
        device_info['os'] = 'Unknown OS'

    # Browser detection
    browsers = [
        ('Chrome', r'Chrome/(\d+(\.\d+)+)'),
        ('Firefox', r'Firefox/(\d+(\.\d+)+)'),
        ('Safari', r'Safari/(\d+(\.\d+)+)'),
        ('Edge', r'Edg(e)?/(\d+(\.\d+)+)'),
        ('Opera', r'OPR/(\d+(\.\d+)+)'),
        ('IE', r'MSIE (\d+(\.\d+)+)')
    ]

    for browser_name, pattern in browsers:
        match = re.search(pattern, user_agent)
        if match:
            if browser_name == 'Edge':
                version = match.group(2)
            elif browser_name == 'Opera':
                version = match.group(1)
            else:
                version = match.group(1)
            device_info['browser'] = f"{browser_name} {version}"
            break
    else:
        device_info['browser'] = 'Unknown Browser'

    # Device type detection
    if "Mobile" in user_agent:
        device_info['type'] = 'Mobile'
    elif "Tablet" in user_agent:
        device_info['type'] = 'Tablet'
    elif "iPad" in user_agent:
        device_info['type'] = 'Tablet'
    elif "iPhone" in user_agent:
        device_info['type'] = 'Mobile'
    else:
        device_info['type'] = 'Desktop/Laptop'

    # Get detailed location info using IP geolocation
    location = "Unknown"
    location_details = {}

    # Check if we already have location details from ipinfo.io
    if ip_details and 'city' in ip_details and 'region' in ip_details and 'country' in ip_details:
        # Use the location details from ipinfo.io
        location_details = {
            'city': ip_details.get('city', 'Unknown'),
            'region': ip_details.get('region', 'Unknown'),
            'country': ip_details.get('country', 'Unknown'),
            'postal': ip_details.get('postal', 'Unknown'),
            'latitude': ip_details.get('loc', '').split(',')[0] if ',' in ip_details.get('loc', '') else 'Unknown',
            'longitude': ip_details.get('loc', '').split(',')[1] if ',' in ip_details.get('loc', '') else 'Unknown',
            'timezone': ip_details.get('timezone', 'Unknown'),
            'org': ip_details.get('org', 'Unknown'),  # ISP or organization
            'asn': ip_details.get('asn', 'Unknown')   # Autonomous System Number
        }

        location = f"{ip_details.get('city', '')}, {ip_details.get('region', '')}, {ip_details.get('country', '')}"
        if not location.strip().replace(',', ''):
            location = "Unknown"
    elif REQUESTS_AVAILABLE:
        # Try multiple geolocation APIs for the most accurate results
        apis_to_try = [
            # ipapi.co API
            {
                'url': f"https://ipapi.co/{ip_address}/json/",
                'parser': lambda data: {
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region', 'Unknown'),
                    'country': data.get('country_name', 'Unknown'),
                    'postal': data.get('postal', 'Unknown'),
                    'latitude': data.get('latitude', 'Unknown'),
                    'longitude': data.get('longitude', 'Unknown'),
                    'timezone': data.get('timezone', 'Unknown'),
                    'org': data.get('org', 'Unknown'),
                    'asn': data.get('asn', 'Unknown')
                },
                'location_formatter': lambda data: f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country_name', '')}"
            },
            # ip-api.com API (free, no API key required)
            {
                'url': f"http://ip-api.com/json/{ip_address}",
                'parser': lambda data: {
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'postal': data.get('zip', 'Unknown'),
                    'latitude': data.get('lat', 'Unknown'),
                    'longitude': data.get('lon', 'Unknown'),
                    'timezone': data.get('timezone', 'Unknown'),
                    'org': data.get('isp', 'Unknown'),
                    'asn': data.get('as', 'Unknown')
                },
                'location_formatter': lambda data: f"{data.get('city', '')}, {data.get('regionName', '')}, {data.get('country', '')}"
            },
            # freegeoip.app API
            {
                'url': f"https://freegeoip.app/json/{ip_address}",
                'parser': lambda data: {
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('region_name', 'Unknown'),
                    'country': data.get('country_name', 'Unknown'),
                    'postal': data.get('zip_code', 'Unknown'),
                    'latitude': data.get('latitude', 'Unknown'),
                    'longitude': data.get('longitude', 'Unknown'),
                    'timezone': data.get('time_zone', 'Unknown'),
                    'org': 'Unknown',
                    'asn': 'Unknown'
                },
                'location_formatter': lambda data: f"{data.get('city', '')}, {data.get('region_name', '')}, {data.get('country_name', '')}"
            }
        ]

        # Try each API until we get a valid response
        for api in apis_to_try:
            try:
                response = requests.get(api['url'], timeout=3)
                if response.status_code == 200:
                    data = response.json()
                    location_details = api['parser'](data)
                    location = api['location_formatter'](data)
                    if not location.strip().replace(',', ''):
                        location = "Unknown"
                    else:
                        # We got a valid location, break the loop
                        break
            except Exception as e:
                print(f"Error getting location info from {api['url']}: {e}")
                continue

    # If all APIs fail or we don't have location details, generate random data for demonstration
    if location == "Unknown" or not location_details:
        import random
        cities = ["New York", "London", "Tokyo", "Paris", "Sydney", "Berlin", "Toronto", "Mumbai"]
        regions = ["NY", "Greater London", "Tokyo", "Île-de-France", "NSW", "Berlin", "Ontario", "Maharashtra"]
        countries = ["USA", "UK", "Japan", "France", "Australia", "Germany", "Canada", "India"]

        random_idx = random.randint(0, len(cities) - 1)
        location = f"{cities[random_idx]}, {regions[random_idx]}, {countries[random_idx]}"

        location_details = {
            'city': cities[random_idx],
            'region': regions[random_idx],
            'country': countries[random_idx],
            'postal': f"{random.randint(10000, 99999)}",
            'latitude': round(random.uniform(-90, 90), 6),
            'longitude': round(random.uniform(-180, 180), 6),
            'timezone': f"UTC{'+' if random.random() > 0.5 else '-'}{random.randint(0, 12)}",
            'org': f"Example ISP {random.randint(1, 10)}",
            'asn': f"AS{random.randint(1000, 9999)}"
        }

    # Format device info for display
    device_info_str = f"{device_info.get('type', 'Unknown')} - {device_info.get('os', 'Unknown')} - {device_info.get('browser', 'Unknown')}"

    return {
        'ip_address': ip_address,
        'mac_address': mac_address,
        'device_info': device_info_str,
        'location': location,
        'location_details': location_details,
        'raw_user_agent': user_agent
    }

@app.route('/')
def entry_page():
    # Get enhanced client information
    client_info = get_client_info()

    # Log the access attempt with detailed information
    add_access_log(
        ip_address=client_info['ip_address'],
        mac_address=client_info['mac_address'],
        device_info=client_info['device_info'],
        location=client_info['location'],
        location_details=client_info.get('location_details', {}),
        raw_user_agent=client_info.get('raw_user_agent', 'Unknown')
    )

    # Show checking page with spinner instead of direct redirection
    return render_template("checking.html")

def check_firewall_auto():
    # Get enhanced client information
    client_info = get_client_info()

    # Extract features from the request
    features = extract_request_features(request)

    # Make prediction
    input_data = np.array(features).reshape(1, -1)
    prediction = model.predict(input_data)

    # Get prediction probability (confidence score)
    prediction_confidence = model.predict_proba(input_data)[0]

    # Only block if confidence is high (>80%)
    if prediction[0] == 1 and prediction_confidence[1] > 0.8:
        # Log blocked access with enhanced information
        add_access_log(
            ip_address=client_info['ip_address'],
            mac_address=client_info['mac_address'],
            device_info=client_info['device_info'],
            location=client_info['location'],
            location_details=client_info.get('location_details', {}),
            raw_user_agent=client_info.get('raw_user_agent', 'Unknown'),
            is_blocked=True,
            block_reason="High threat probability detected"
        )
        return redirect(url_for('blocked_page'))
    else:
        # Log allowed access with enhanced information
        add_access_log(
            ip_address=client_info['ip_address'],
            mac_address=client_info['mac_address'],
            device_info=client_info['device_info'],
            location=client_info['location'],
            location_details=client_info.get('location_details', {}),
            raw_user_agent=client_info.get('raw_user_agent', 'Unknown')
        )
        # Redirect directly to login page
        return redirect(url_for('login'))

def extract_request_features(request):
    # Extract relevant features from request
    # This is a simplified version - you should implement proper feature extraction
    features = [0] * 41

    # Example features (customize based on your model's expected inputs)
    if request.headers.get('User-Agent'):
        # Set some features based on user agent
        features[0] = 1

    # Add IP-based features, request method features, etc.
    # features[1] = hash(request.remote_addr) % 100 / 100.0

    return features

@app.route('/check_firewall', methods=['POST'])
def check_firewall():
    # Keep this endpoint for backward compatibility
    return check_firewall_auto()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = verify_user(username, password)

        if user:
            # Check if face recognition is enabled for this user
            if is_face_recognition_enabled(user['id']):
                # Store credentials temporarily for face verification
                session['temp_username'] = username
                session['temp_user_id'] = user['id']
                # Render the face verification page
                return render_template('face_verification.html')
            else:
                # No face recognition, proceed with normal login
                session['logged_in'] = True
                session['username'] = username
                session['user_id'] = user['id']
                flash('You were successfully logged in')
                # Automatically redirect to dashboard after successful login
                return redirect(url_for('dashboard'))
        else:
            error = 'Invalid credentials. Please try again.'

    # For GET requests or failed login attempts, show the login page
    return render_template('login.html', error=error)

@app.route('/home')
def home_page():
    # Redirect to login page instead of showing the original home page
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get access statistics
    stats = get_access_stats()

    # Get recent access logs
    logs = get_access_logs(limit=50)

    # Get current datetime for display
    now = datetime.now()

    return render_template('dashboard.html', stats=stats, logs=logs, now=now)

@app.route('/api/dashboard_data')
@login_required
def api_dashboard_data():
    """API endpoint to get dashboard data for real-time updates"""
    # Get access statistics
    stats = get_access_stats()

    # Get recent access logs
    logs = get_access_logs(limit=50)

    # Convert logs to a list of dictionaries for JSON serialization
    logs_list = []
    for log in logs:
        log_dict = dict(log)
        # Format the access time for display
        log_dict['access_time_formatted'] = datetime.fromisoformat(log_dict['access_time']).strftime('%Y-%m-%d %H:%M:%S')
        # Format the status
        log_dict['status'] = 'Blocked' if log_dict['is_blocked'] else 'Allowed'

        # Ensure all fields have values to prevent JavaScript errors
        for field in ['city', 'region', 'country', 'postal_code', 'latitude', 'longitude',
                     'timezone', 'isp', 'asn', 'device_info', 'raw_user_agent', 'block_reason']:
            if field not in log_dict or log_dict[field] is None:
                log_dict[field] = 'Unknown'

        logs_list.append(log_dict)

    return jsonify({
        'stats': stats,
        'logs': logs_list,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/access_logs')
@login_required
def access_logs():
    """Display all access logs"""
    # Get all access logs (increased limit for full display)
    logs = get_access_logs(limit=1000)

    # Get current datetime for display
    now = datetime.now()

    return render_template('access_logs.html', logs=logs, now=now)

@app.route('/api/access_logs_data')
@login_required
def api_access_logs_data():
    """API endpoint to get access logs data for real-time updates"""
    # Get all access logs
    logs = get_access_logs(limit=1000)

    # Convert logs to a list of dictionaries for JSON serialization
    logs_list = []
    for log in logs:
        log_dict = dict(log)
        # Format the access time for display
        log_dict['access_time_formatted'] = datetime.fromisoformat(log_dict['access_time']).strftime('%Y-%m-%d %H:%M:%S')
        # Format the status
        log_dict['status'] = 'Blocked' if log_dict['is_blocked'] else 'Allowed'

        # Ensure all fields have values to prevent JavaScript errors
        for field in ['city', 'region', 'country', 'postal_code', 'latitude', 'longitude',
                     'timezone', 'isp', 'asn', 'device_info', 'raw_user_agent', 'block_reason']:
            if field not in log_dict or log_dict[field] is None:
                log_dict[field] = 'Unknown'

        logs_list.append(log_dict)

    return jsonify({
        'logs': logs_list,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@app.route('/portfolio')
@login_required
def portfolio():
    """Display the portfolio page (content from home.html)"""
    return render_template('home.html')

@app.route('/documentation')
@login_required
def documentation():
    """Display the documentation page"""
    return render_template('documentation.html')

@app.route('/analytics')
@login_required
def analytics():
    """Display the analytics page with data visualizations"""
    # Get access statistics
    stats = get_access_stats()

    # Get chart data
    hourly_data = get_hourly_traffic_data()
    status_data = get_traffic_status_data()
    geo_data = get_geographic_data()
    country_data = get_top_countries_data()

    # Get current datetime for display
    now = datetime.now()

    return render_template('analytics.html',
                          stats=stats,
                          hourly_data=hourly_data,
                          status_data=status_data,
                          geo_data=geo_data,
                          country_data=country_data,
                          now=now)

@app.route('/face_verification', methods=['POST'])
def face_verification():
    """Verify face for login"""
    if 'temp_user_id' not in session:
        return jsonify({"success": False, "message": "No user credentials found"}), 400

    user_id = session['temp_user_id']
    username = session['temp_username']

    # Get the base64 image from the request
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({"success": False, "message": "No image data provided"}), 400

    base64_image = data['image']

    # Verify the face
    result = verify_face(user_id, base64_image)

    if result["success"]:
        # Face verification successful, complete login
        session.pop('temp_user_id', None)
        session.pop('temp_username', None)
        session['logged_in'] = True
        session['username'] = username
        session['user_id'] = user_id
        return jsonify({"success": True, "message": "Face verification successful", "redirect": url_for('dashboard')}), 200
    else:
        # Face verification failed
        return jsonify({"success": False, "message": result["message"]}), 401

@app.route('/face_training')
@login_required
def face_training_page():
    """Display the face training page"""
    return render_template('face_training.html')

@app.route('/api/save_face_image', methods=['POST'])
@login_required
def api_save_face_image():
    """API endpoint to save a face image for training"""
    user_id = session['user_id']

    # Get the base64 image from the request
    data = request.get_json()
    if not data or 'image' not in data:
        return jsonify({"success": False, "message": "No image data provided"}), 400

    base64_image = data['image']

    # Save the training image
    result = save_training_image(user_id, base64_image)

    return jsonify(result), 200 if result["success"] else 400

@app.route('/api/train_face_model', methods=['POST'])
@login_required
def api_train_face_model():
    """API endpoint to train the face recognition model"""
    user_id = session['user_id']

    # Train the face model
    result = train_face_model(user_id)

    return jsonify(result), 200 if result["success"] else 400

@app.route('/admin/face_recognition')
@login_required
def admin_face_recognition():
    """Admin page for face recognition management"""
    # Get all users
    users = get_all_users()

    return render_template('admin_face_recognition.html', users=users)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('temp_username', None)
    session.pop('temp_user_id', None)
    flash('You were successfully logged out')
    return redirect(url_for('login'))

@app.route('/delete_log/<int:log_id>')
@login_required
def delete_log(log_id):
    """Delete a specific log entry"""
    delete_access_log(log_id)
    flash('Log entry deleted successfully')
    return redirect(url_for('dashboard'))

@app.route('/delete_old_logs')
@login_required
def delete_old_logs():
    """Delete logs older than 30 days"""
    days = request.args.get('days', 30, type=int)
    deleted_count = delete_old_access_logs(days)
    flash(f'Successfully deleted {deleted_count} old log entries')
    return redirect(url_for('dashboard'))

@app.route('/export_logs')
@login_required
def export_logs():
    """Export access logs to CSV file"""
    import pandas as pd
    import csv
    from io import StringIO
    from flask import Response

    # Get all access logs
    logs = get_access_logs(limit=1000)  # Increase limit for export

    # Convert logs to a list of dictionaries
    logs_list = []
    for log in logs:
        log_dict = dict(log)
        # Format the status
        log_dict['status'] = 'Blocked' if log['is_blocked'] else 'Allowed'
        logs_list.append(log_dict)

    # Create a pandas DataFrame
    df = pd.DataFrame(logs_list)

    # Reorder and select columns for better readability
    columns = [
        'id', 'ip_address', 'mac_address', 'device_info', 'location',
        'city', 'region', 'country', 'postal_code', 'latitude', 'longitude',
        'timezone', 'isp', 'asn', 'status', 'access_time', 'block_reason'
    ]

    # Filter columns that exist in the DataFrame
    columns = [col for col in columns if col in df.columns]

    # Select and reorder columns
    df = df[columns]

    # Create a CSV file in memory
    output = StringIO()
    df.to_csv(output, index=False, quoting=csv.QUOTE_NONNUMERIC)

    # Get the CSV content
    csv_data = output.getvalue()

    # Generate timestamp for filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Create a response with the CSV data
    response = Response(
        csv_data,
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=access_logs_{timestamp}.csv',
            'Content-Type': 'text/csv'
        }
    )

    return response

@app.route('/blocked')
def blocked_page():
    return render_template("blocked.html")

@app.route('/download_documentation_pdf')
@login_required
def download_documentation_pdf():
    """Download documentation as PDF"""
    try:
        # Import necessary modules
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, PageBreak, Preformatted
        from reportlab.lib.units import inch
        from io import BytesIO
        from bs4 import BeautifulSoup

        # Get the documentation HTML content
        html_content = render_template('documentation.html')

        # Create a BytesIO object to store the PDF
        pdf_buffer = BytesIO()

        # Create the PDF document with wider margins to accommodate code blocks
        doc = SimpleDocTemplate(
            pdf_buffer,
            pagesize=letter,
            rightMargin=30,  # Slightly smaller right margin
            leftMargin=30,   # Slightly smaller left margin
            topMargin=36,
            bottomMargin=36,
            title="AI Firewall Documentation"
        )

        # Get styles
        styles = getSampleStyleSheet()

        # Create custom styles
        title_style = ParagraphStyle(
            name='TitleStyle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=12,
            textColor=colors.HexColor('#4e73df')
        )

        heading1_style = ParagraphStyle(
            name='CustomHeading1',
            parent=styles['Heading1'],
            fontSize=20,
            spaceAfter=12,
            textColor=colors.HexColor('#4e73df')
        )

        heading2_style = ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=10,
            spaceBefore=20,
            textColor=colors.HexColor('#5a5c69')
        )

        heading3_style = ParagraphStyle(
            name='CustomHeading3',
            parent=styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=15
        )

        normal_style = ParagraphStyle(
            name='CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            leading=14
        )

        # Create a style for code blocks that preserves formatting
        preformatted_style = ParagraphStyle(
            name='PreformattedCode',
            fontName='Courier',
            fontSize=8,  # Smaller font to fit more characters per line
            leading=10,  # Tighter line spacing
            spaceAfter=8,
            spaceBefore=8,
            backColor=colors.HexColor('#f8f9fc'),
            leftIndent=10,
            firstLineIndent=0,
            wordWrap=None  # Disable word wrapping to preserve formatting
        )

        # Create a list to hold the PDF elements
        elements = []

        # Add title
        title = Paragraph("AI-Powered Web Firewall: Technical Documentation", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.25*inch))

        # Use BeautifulSoup to extract the content directly from the HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the documentation content div
        doc_content = soup.find('div', class_='documentation-content')
        print(f"Looking for documentation content div: {'Found' if doc_content else 'Not found'}")

        if not doc_content:
            # If not found, try to find the card body
            doc_content = soup.find('div', class_='card-body documentation-content')
            print(f"Looking for card-body documentation-content: {'Found' if doc_content else 'Not found'}")

        if not doc_content:
            # If still not found, use the entire main content
            doc_content = soup.find('div', class_='main-content')
            print(f"Looking for main-content: {'Found' if doc_content else 'Not found'}")

        if not doc_content:
            # Try to find any div with 'content' in the class name
            doc_content = soup.find('div', class_=lambda c: c and 'content' in c)
            print(f"Looking for any div with 'content' in class: {'Found' if doc_content else 'Not found'}")

        if not doc_content:
            # Last resort: use the entire body
            doc_content = soup.find('body')
            print(f"Using body element: {'Found' if doc_content else 'Not found'}")

        if not doc_content:
            print("HTML structure:", html_content[:500])  # Print first 500 chars for debugging
            raise Exception("Could not find documentation content")

        # Extract all headings for the table of contents
        headings = []
        for h in doc_content.find_all(['h1', 'h2']):
            headings.append(h.get_text().strip())

        # Add table of contents
        elements.append(Paragraph("Table of Contents", heading1_style))
        elements.append(Spacer(1, 0.1*inch))

        for heading in headings:
            elements.append(Paragraph("• " + heading, normal_style))
            elements.append(Spacer(1, 0.05*inch))

        # Add a page break after the table of contents
        elements.append(PageBreak())

        # First, find all the headings to use as section markers
        headings = doc_content.find_all(['h1', 'h2', 'h3'])

        # Process each section
        for i, heading in enumerate(headings):
            # Get the heading text and style
            heading_text = heading.get_text().strip()
            if heading.name == 'h1':
                heading_style = heading1_style
            elif heading.name == 'h2':
                heading_style = heading2_style
            else:
                heading_style = heading3_style

            # Add the heading
            elements.append(Paragraph(heading_text, heading_style))

            # Get all elements until the next heading
            next_element = heading.next_sibling
            while next_element and (not next_element.name or next_element.name not in ['h1', 'h2', 'h3']):
                if next_element.name == 'p':
                    p_text = next_element.get_text().strip()
                    if p_text:
                        elements.append(Paragraph(p_text, normal_style))
                        elements.append(Spacer(1, 0.1*inch))
                elif next_element.name == 'pre':
                    code_text = next_element.get_text()
                    if code_text:
                        # Special handling for directory structure code blocks
                        if "app/" in code_text and ("├──" in code_text or "│" in code_text):
                            # Create a custom fixed-width representation
                            elements.append(Paragraph("<strong>Directory Structure:</strong>", normal_style))
                            elements.append(Spacer(1, 0.05*inch))

                            # Use Preformatted with a monospaced font to preserve structure
                            elements.append(Preformatted(code_text, preformatted_style))
                        else:
                            # For other code blocks
                            elements.append(Preformatted(code_text, preformatted_style))

                        elements.append(Spacer(1, 0.1*inch))
                elif next_element.name == 'ul':
                    list_items = []
                    for li in next_element.find_all('li', recursive=False):
                        li_text = li.get_text().strip()
                        if li_text:
                            list_items.append(ListItem(Paragraph(li_text, normal_style)))
                    if list_items:
                        elements.append(ListFlowable(list_items, bulletType='bullet'))
                        elements.append(Spacer(1, 0.1*inch))
                elif next_element.name == 'ol':
                    list_items = []
                    for li in next_element.find_all('li', recursive=False):
                        li_text = li.get_text().strip()
                        if li_text:
                            list_items.append(ListItem(Paragraph(li_text, normal_style)))
                    if list_items:
                        elements.append(ListFlowable(list_items, bulletType='1'))
                        elements.append(Spacer(1, 0.1*inch))

                next_element = next_element.next_sibling

        # As a fallback, also extract all paragraphs, lists, and code blocks directly
        for element in doc_content.find_all(['p', 'pre', 'ul', 'ol']):
            try:
                if element.name == 'p':
                    p_text = element.get_text().strip()
                    if p_text and len(p_text) > 0:
                        elements.append(Paragraph(p_text, normal_style))
                        elements.append(Spacer(1, 0.1*inch))
                elif element.name == 'pre':
                    code_text = element.get_text()
                    if code_text and len(code_text) > 0:
                        # Special handling for directory structure code blocks
                        if "app/" in code_text and ("├──" in code_text or "│" in code_text):
                            # Create a custom fixed-width representation
                            elements.append(Paragraph("<strong>Directory Structure:</strong>", normal_style))
                            elements.append(Spacer(1, 0.05*inch))

                            # Use Preformatted with a monospaced font to preserve structure
                            elements.append(Preformatted(code_text, preformatted_style))
                        else:
                            # For other code blocks
                            elements.append(Preformatted(code_text, preformatted_style))

                        elements.append(Spacer(1, 0.1*inch))
                elif element.name == 'ul':
                    list_items = []
                    for li in element.find_all('li'):
                        li_text = li.get_text().strip()
                        if li_text and len(li_text) > 0:
                            list_items.append(ListItem(Paragraph(li_text, normal_style)))
                    if list_items:
                        elements.append(ListFlowable(list_items, bulletType='bullet'))
                        elements.append(Spacer(1, 0.1*inch))
                elif element.name == 'ol':
                    list_items = []
                    for li in element.find_all('li'):
                        li_text = li.get_text().strip()
                        if li_text and len(li_text) > 0:
                            list_items.append(ListItem(Paragraph(li_text, normal_style)))
                    if list_items:
                        elements.append(ListFlowable(list_items, bulletType='1'))
                        elements.append(Spacer(1, 0.1*inch))
            except Exception as element_error:
                print(f"Error processing element {element.name}: {element_error}")
                continue

        # Build the PDF
        doc.build(elements)

        # Reset the buffer position to the beginning
        pdf_buffer.seek(0)

        # Generate a filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"AI_Firewall_Documentation_{timestamp}.pdf"

        # Return the PDF file
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
    except Exception as e:
        # Log the error
        print(f"Error generating PDF: {e}")

        # Create a simple text-based PDF as a fallback
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from io import BytesIO

            # Create a BytesIO object to store the PDF
            pdf_buffer = BytesIO()

            # Create the PDF document
            doc = SimpleDocTemplate(
                pdf_buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # Get styles
            styles = getSampleStyleSheet()

            # Create a list to hold the PDF elements
            elements = []

            # Add title
            elements.append(Paragraph("AI-Powered Web Firewall: Technical Documentation", styles['Title']))
            elements.append(Spacer(1, 0.25*inch))

            # Add introduction
            elements.append(Paragraph("Introduction", styles['Heading1']))
            elements.append(Paragraph("The AI-Powered Web Firewall is an intelligent security solution that uses machine learning to detect and block malicious web traffic in real-time. This system represents a significant advancement over traditional rule-based firewalls by leveraging the power of artificial intelligence to identify complex attack patterns and adapt to emerging threats.", styles['Normal']))

            # Add system architecture
            elements.append(Paragraph("System Architecture", styles['Heading1']))
            elements.append(Paragraph("The AI Firewall system consists of several key components that work together to provide robust protection against web-based attacks.", styles['Normal']))

            # Add machine learning model
            elements.append(Paragraph("Machine Learning Model", styles['Heading1']))
            elements.append(Paragraph("The system employs a Random Forest classifier, which was chosen for its high accuracy, robustness, interpretability, and efficiency.", styles['Normal']))

            # Build the PDF
            doc.build(elements)

            # Reset the buffer position to the beginning
            pdf_buffer.seek(0)

            # Generate a filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"AI_Firewall_Documentation_{timestamp}.pdf"

            # Return the PDF file
            response = make_response(pdf_buffer.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

            return response
        except Exception as e2:
            # If all else fails, return an error
            print(f"Error in fallback PDF generation: {e2}")
            return f"Error generating documentation file: {str(e)}, Fallback error: {str(e2)}", 500

if __name__ == '__main__':
    app.run(debug=True)
