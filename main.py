import subprocess
import time
from flask import Flask, redirect, url_for
import threading
import os
import secrets

# Step 1: Download the rclone binary using Python
def download_rclone():
    url = "https://gitlab.com/developeranaz/git-hosts/-/raw/main/rclone/rclone"
    output = "rclone"
    subprocess.run(["curl", "-L", url, "-o", output])
    subprocess.run(["chmod", "+x", output])

# Step 2: Configure rclone with your MEGA credentials
def configure_rclone(cloud_name, username, password):
    config_commands = [
        ["./rclone", "config", "create", cloud_name, "mega", "user", username, "pass", password]
    ]
    for command in config_commands:
        subprocess.run(command)

# Step 3: Serve the MEGA directory with rclone
def serve_rclone(cloud_name, port):
    serve_command = [
        "./rclone", "serve", "http", f"{cloud_name}:", "--addr", f":{port}",
        "--buffer-size", "256M", "--dir-cache-time", "12h",
        "--vfs-read-chunk-size", "256M", "--vfs-read-chunk-size-limit", "2G", "--vfs-cache-mode", "writes"
    ]
    subprocess.Popen(serve_command)  # Run in the background

# Download rclone
download_rclone()

# Configure rclone (replace with your credentials)
cloud_name = "CLOUDNAME"
username = os.environ['username']
password = os.environ['password']
configure_rclone(cloud_name, username, password)

# Serve the MEGA directory
port = 8080
serve_rclone(cloud_name, port)

# Initialize Flask app
app = Flask(__name__)

# Generate random secret code
def generate_secret():
    return secrets.token_urlsafe(9)  # 12 characters (approximately)

# Function to start the Flask server
def start_flask():
    app.run(port=5000)

# Start the Flask server in a separate thread
flask_thread = threading.Thread(target=start_flask)
flask_thread.start()

# Allow some time for the servers to start
time.sleep(5)

# Define base URL
base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
print("Servers are running.")
print(f"Access the Flask server at {base_url}")

@app.route('/')
def index():
    return 'Welcome to the MEGA file streaming service!'

@app.route('/file/<path:filename>')
def stream_file(filename):
    secret = generate_secret()
    # Redirect to a URL with the base URL and random secret code
    return redirect(url_for('stream_with_secret', filename=filename, secret=secret))

@app.route('/<secret>/<path:filename>')
def stream_with_secret(secret, filename):
    # Verify secret here if needed
    streaming_url = f"{base_url}/{secret}/{filename}"
    return redirect(streaming_url)
