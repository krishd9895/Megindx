import subprocess
import time
from flask import Flask
import threading
import os
import random
import string

# Initialize Flask app
app = Flask(__name__)

# Generate random secret code
def generate_secret():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))  # 12 characters

# Define base URL
base_url = os.environ.get('BASE_URL', 'http://localhost:5000')
print("Servers are running.")
print(f"Access the Flask server at {base_url}")

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

# Serve the MEGA directory (modify this according to your specific setup)
port = 8080
serve_rclone(cloud_name, port)

# Function to generate streaming URL
def get_streaming_url(secret):
    return f"{base_url}/{secret}"

# Route to serve rclone files based on secret
@app.route('/<secret>')
def serve_secret(secret):
    # Generate streaming URL
    streaming_url = get_streaming_url(secret)
    print(f"Streaming URL for secret '{secret}': {streaming_url}")
    
    # Use subprocess to serve rclone files for the secret
    serve_command = [
        "./rclone", "serve", "http", f"{cloud_name}:", "--addr", f":{port}",
        "--buffer-size", "256M", "--dir-cache-time", "12h",
        "--vfs-read-chunk-size", "256M", "--vfs-read-chunk-size-limit", "2G", "--vfs-cache-mode", "writes"
    ]
    subprocess.Popen(serve_command)  # Run in the background

    return f"Serving rclone files for secret '{secret}'."

# Start the Flask server
if __name__ == '__main__':
    app.run(port=5000)

