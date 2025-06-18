import sqlite3
import os
import hashlib
from datetime import datetime

# Ensure the database directory exists
db_dir = os.path.join('app', 'database')
os.makedirs(db_dir, exist_ok=True)

# Database file path
DB_PATH = os.path.join(db_dir, 'firewall.db')

def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def reset_db():
    """Drop and recreate the database with the new schema"""
    # Check if database file exists and delete it
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
            print(f"Deleted existing database: {DB_PATH}")
        except Exception as e:
            print(f"Error deleting database: {e}")

    # Create a new database with the updated schema
    init_db(force_recreate=True)
    print("Database reset complete with new schema")

def init_db(force_recreate=False):
    """Initialize the database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # If force_recreate is True, drop existing tables
    if force_recreate:
        try:
            cursor.execute("DROP TABLE IF EXISTS access_logs")
            cursor.execute("DROP TABLE IF EXISTS users")
            cursor.execute("DROP TABLE IF EXISTS face_images")
            print("Dropped existing tables")
        except Exception as e:
            print(f"Error dropping tables: {e}")

    # Create users table for admin authentication
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin BOOLEAN NOT NULL DEFAULT 0,
        face_recognition_enabled BOOLEAN NOT NULL DEFAULT 0,
        face_encoding TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create access_logs table to track access attempts with enhanced location tracking
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS access_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ip_address TEXT,
        mac_address TEXT,
        device_info TEXT,
        location TEXT,
        city TEXT,
        region TEXT,
        country TEXT,
        postal_code TEXT,
        latitude TEXT,
        longitude TEXT,
        timezone TEXT,
        isp TEXT,
        asn TEXT,
        raw_user_agent TEXT,
        access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_blocked BOOLEAN DEFAULT 0,
        block_reason TEXT
    )
    ''')

    # Create face_images table to store training images for face recognition
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS face_images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        image_data BLOB NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    ''')

    # Check if default admin user exists, if not create one
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        # Create default admin user (username: admin, password: admin123)
        hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
        cursor.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
            ('admin', hashed_password, True)
        )

    conn.commit()
    conn.close()

def add_access_log(ip_address, mac_address='Unknown', device_info='Unknown', location='Unknown',
                location_details=None, raw_user_agent='Unknown', is_blocked=False, block_reason=None):
    """Add a new access log entry with enhanced location tracking"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if this is from the hacker portal by examining the user agent
    if 'hacker_portal' in raw_user_agent.lower() or 'attack_simulator' in raw_user_agent.lower():
        is_blocked = True
        if not block_reason:
            block_reason = "Traffic from hacker portal"

    # Set default location details if not provided
    if location_details is None:
        location_details = {
            'city': 'Unknown',
            'region': 'Unknown',
            'country': 'Unknown',
            'postal': 'Unknown',
            'latitude': 'Unknown',
            'longitude': 'Unknown',
            'timezone': 'Unknown',
            'org': 'Unknown',
            'asn': 'Unknown'
        }

    cursor.execute(
        """INSERT INTO access_logs (
            ip_address, mac_address, device_info, location,
            city, region, country, postal_code, latitude, longitude,
            timezone, isp, asn, raw_user_agent, is_blocked, block_reason
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            ip_address, mac_address, device_info, location,
            location_details.get('city', 'Unknown'),
            location_details.get('region', 'Unknown'),
            location_details.get('country', 'Unknown'),
            location_details.get('postal', 'Unknown'),
            location_details.get('latitude', 'Unknown'),
            location_details.get('longitude', 'Unknown'),
            location_details.get('timezone', 'Unknown'),
            location_details.get('org', 'Unknown'),
            location_details.get('asn', 'Unknown'),
            raw_user_agent, is_blocked, block_reason
        )
    )

    conn.commit()
    conn.close()

def get_access_logs(limit=100):
    """Get recent access logs"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM access_logs ORDER BY access_time DESC LIMIT ?", (limit,))
    logs = cursor.fetchall()

    conn.close()
    return logs

def get_access_stats():
    """Get statistics about access attempts"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total access attempts
    cursor.execute("SELECT COUNT(*) as total FROM access_logs")
    total_attempts = cursor.fetchone()['total']

    # Blocked attempts
    cursor.execute("SELECT COUNT(*) as blocked FROM access_logs WHERE is_blocked = 1")
    blocked_attempts = cursor.fetchone()['blocked']

    # Unique IPs
    cursor.execute("SELECT COUNT(DISTINCT ip_address) as unique_ips FROM access_logs")
    unique_ips = cursor.fetchone()['unique_ips']

    # Recent activity (last 24 hours)
    cursor.execute("SELECT COUNT(*) as recent FROM access_logs WHERE access_time >= datetime('now', '-1 day')")
    recent_activity = cursor.fetchone()['recent']

    conn.close()

    return {
        'total_attempts': total_attempts,
        'blocked_attempts': blocked_attempts,
        'unique_ips': unique_ips,
        'recent_activity': recent_activity
    }

def get_hourly_traffic_data():
    """Get hourly traffic data for the last 24 hours"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get hourly counts for the last 24 hours
    cursor.execute("""
        SELECT
            strftime('%H', access_time) as hour,
            COUNT(*) as count
        FROM access_logs
        WHERE access_time >= datetime('now', '-1 day')
        GROUP BY hour
        ORDER BY hour
    """)

    hourly_data = cursor.fetchall()

    # Initialize all hours with 0 count
    hours = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11',
             '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']
    counts = [0] * 24

    # Fill in actual counts
    for row in hourly_data:
        hour_index = int(row['hour'])
        counts[hour_index] = row['count']

    conn.close()

    return {
        'hours': hours,
        'counts': counts
    }

def get_traffic_status_data():
    """Get traffic status data (allowed, blocked, suspicious)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get allowed and blocked counts
    cursor.execute("""
        SELECT
            is_blocked,
            COUNT(*) as count
        FROM access_logs
        GROUP BY is_blocked
    """)

    status_data = cursor.fetchall()

    # Initialize with zeros
    allowed = 0
    blocked = 0

    # Fill in actual counts
    for row in status_data:
        if row['is_blocked'] == 0:
            allowed = row['count']
        else:
            blocked = row['count']

    conn.close()

    return {
        'allowed': allowed,
        'blocked': blocked
    }

def get_geographic_data():
    """Get geographic distribution of access attempts"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get counts by region (using country as proxy)
    cursor.execute("""
        SELECT
            CASE
                WHEN country IN ('United States', 'Canada', 'Mexico') THEN 'North America'
                WHEN country IN ('Brazil', 'Argentina', 'Chile', 'Colombia', 'Peru', 'Venezuela') THEN 'South America'
                WHEN country IN ('United Kingdom', 'France', 'Germany', 'Italy', 'Spain', 'Russia') THEN 'Europe'
                WHEN country IN ('China', 'India', 'Japan', 'South Korea', 'Indonesia', 'Thailand') THEN 'Asia'
                WHEN country IN ('Australia', 'New Zealand') THEN 'Australia'
                WHEN country IN ('Egypt', 'South Africa', 'Nigeria', 'Kenya') THEN 'Africa'
                ELSE 'Other'
            END as region,
            COUNT(*) as count
        FROM access_logs
        WHERE country != 'Unknown'
        GROUP BY region
        ORDER BY count DESC
    """)

    region_data = cursor.fetchall()

    # Initialize regions and counts
    regions = ['North America', 'Europe', 'Asia', 'South America', 'Africa', 'Australia', 'Other']
    counts = [0] * 7

    # Fill in actual counts
    for row in region_data:
        region = row['region']
        count = row['count']

        if region == 'North America':
            counts[0] = count
        elif region == 'Europe':
            counts[1] = count
        elif region == 'Asia':
            counts[2] = count
        elif region == 'South America':
            counts[3] = count
        elif region == 'Africa':
            counts[4] = count
        elif region == 'Australia':
            counts[5] = count
        else:
            counts[6] = count

    conn.close()

    return {
        'regions': regions,
        'counts': counts
    }

def get_top_countries_data():
    """Get top countries by access attempts"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get top 5 countries by count
    cursor.execute("""
        SELECT
            CASE WHEN country = 'Unknown' THEN 'Other' ELSE country END as country,
            COUNT(*) as count
        FROM access_logs
        GROUP BY country
        ORDER BY count DESC
        LIMIT 6
    """)

    country_data = cursor.fetchall()

    # Extract countries and counts
    countries = []
    counts = []

    for row in country_data:
        countries.append(row['country'])
        counts.append(row['count'])

    # If we have fewer than 6 countries, add "Other" with 0 count
    if len(countries) < 6:
        countries.append('Other')
        counts.append(0)

    conn.close()

    return {
        'countries': countries,
        'counts': counts
    }

def verify_user(username, password):
    """Verify user credentials"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Hash the provided password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()

    conn.close()
    return user

def delete_access_log(log_id):
    """Delete a specific access log entry by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM access_logs WHERE id = ?", (log_id,))

    conn.commit()
    conn.close()

def delete_old_access_logs(days=30):
    """Delete access logs older than the specified number of days"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM access_logs WHERE access_time < datetime('now', ?)", (f'-{days} days',))
    deleted_count = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted_count

def save_face_image(user_id, image_data):
    """Save a face image for training"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO face_images (user_id, image_data) VALUES (?, ?)",
        (user_id, image_data)
    )

    conn.commit()
    conn.close()

def get_face_images(user_id):
    """Get all face images for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM face_images WHERE user_id = ?", (user_id,))
    images = cursor.fetchall()

    conn.close()
    return images

def save_face_encoding(user_id, face_encoding):
    """Save face encoding for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Convert numpy array to string for storage
    encoding_str = ','.join(map(str, face_encoding)) if face_encoding is not None else None

    cursor.execute(
        "UPDATE users SET face_encoding = ?, face_recognition_enabled = 1 WHERE id = ?",
        (encoding_str, user_id)
    )

    conn.commit()
    conn.close()

def get_face_encoding(user_id):
    """Get face encoding for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT face_encoding FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()

    conn.close()

    if result and result['face_encoding']:
        # Convert string back to numpy array
        return [float(x) for x in result['face_encoding'].split(',')]
    return None

def is_face_recognition_enabled(user_id):
    """Check if face recognition is enabled for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT face_recognition_enabled FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()

    conn.close()
    return result and result['face_recognition_enabled'] == 1

def get_all_users():
    """Get all users"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    conn.close()
    return users

