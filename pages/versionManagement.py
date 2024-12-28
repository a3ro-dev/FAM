import streamlit as st
import paramiko
import platform
import subprocess
import os
from pathlib import Path

st.set_page_config(page_title="Web Terminal", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #1e1e1e;
        color: #fff;
    }
    .terminal-container {
        background-color: #000;
        border-radius: 10px;
        padding: 20px;
        margin: 10px;
        border: 1px solid #333;
    }
    </style>
""", unsafe_allow_html=True)

def create_ssh_client(host, user, pwd=None, key_file=None):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(host, username=user, password=pwd, key_filename=key_file)
        return client
    except Exception as e:
        st.error(f"Connection failed: {e}")
        return None

def get_shell_command():
    system = platform.system().lower()
    if system == "windows":
        return ["cmd.exe", "/c"]
    return ["/bin/bash", "-c"]

def get_project_root():
    """Get the project root directory dynamically"""
    if os.path.exists('/home/pi/FAM'):
        return '/home/pi/FAM'
    # Dynamically find project root (looks for FAM directory)
    current = Path(__file__).resolve().parent
    while current.name != 'FAM' and current.parent != current:
        current = current.parent
    return str(current)

def run_local_command(command):
    try:
        shell_cmd = get_shell_command()
        full_command = shell_cmd + [command]
        project_root = get_project_root()
        process = subprocess.Popen(
            full_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            cwd=project_root  # Set working directory
        )
        output, error = process.communicate()
        return f"Working directory: {project_root}\n" + output + error
    except Exception as e:
        return f"Error executing command: {str(e)}"

def run_ssh_command(client, command):
    try:
        # Change to project directory before running command
        stdin, stdout, stderr = client.exec_command(f"cd /home/pi/FAM && {command}")
        return stdout.read().decode() + stderr.read().decode()
    except Exception as e:
        return f"SSH Error: {str(e)}"

# Sidebar
with st.sidebar:
    st.title("Connection Settings")
    st.info(f"Project root: {get_project_root()}")
    conn_type = st.selectbox("Type", ["Local Shell", "SSH"])
    if conn_type == "SSH":
        hostname = st.text_input("Host")
        username = st.text_input("User")
        auth_method = st.radio("Auth", ["Password", "Key File"])
        if auth_method == "Password":
            password = st.text_input("Password", type="password")
            key_filename = None
        else:
            key_filename = st.text_input("Key File Path")
            password = None
        if st.button("Connect"):
            client = create_ssh_client(hostname, username, password, key_filename)
            if client:
                st.session_state.ssh_client = client
    if conn_type == "Local Shell":
        st.info(f"Running on: {platform.system()}")

st.title("Web Terminal")
with st.container():
    st.markdown('<div class="terminal-container">', unsafe_allow_html=True)
    
    # Add command history in session state
    if 'command_history' not in st.session_state:
        st.session_state.command_history = []

    command = st.text_input("Enter command", key="command_input")
    col1, col2 = st.columns([1, 5])
    
    with col1:
        if st.button("Run"):
            if command:
                st.session_state.command_history.append(command)
                if conn_type == "Local Shell":
                    output = run_local_command(command)
                else:
                    if "ssh_client" in st.session_state:
                        output = run_ssh_command(st.session_state.ssh_client, command)
                    else:
                        output = "Not connected to SSH server"
                if 'terminal_output' not in st.session_state:
                    st.session_state.terminal_output = ""
                st.session_state.terminal_output += f"\n$ {command}\n{output}"
    
    # Display terminal output with history
    st.text_area("Output", 
                 value=st.session_state.get('terminal_output', ''), 
                 height=400,
                 key="output_area")
    
    st.markdown('</div>', unsafe_allow_html=True)
