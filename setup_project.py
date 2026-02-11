import sys
import subprocess
import os
import shutil
import importlib.util

def print_step(step):
    print(f"\n{'='*50}")
    print(f"STEP: {step}")
    print(f"{'='*50}")

def check_python_version():
    print_step("Checking Python Version")
    version = sys.version_info
    print(f"Current Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("ERROR: Python 3.8 or higher is required.")
        sys.exit(1)
    print("Python version is compatible.")

def install_requirements():
    print_step("Installing Dependencies")
    req_file = "requirements.txt"
    if not os.path.exists(req_file):
        print(f"ERROR: {req_file} not found.")
        sys.exit(1)
    
    print(f"Installing packages from {req_file}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies. {e}")
        sys.exit(1)

def check_env_file():
    print_step("Checking Environment Configuration")
    env_file = ".env"
    sample_env = "sample.env"
    
    if os.path.exists(env_file):
        print(f"Found existing {env_file}.")
    else:
        print(f"{env_file} not found.")
        if os.path.exists(sample_env):
            print(f"Creating {env_file} from {sample_env}...")
            shutil.copy(sample_env, env_file)
            print(f"Created {env_file}. PLEASE EDIT IT with your actual API keys!")
        else:
            print(f"WARNING: {sample_env} not found. Please create {env_file} manually.")

def init_database():
    print_step("Initializing Database")
    db_script = "database.py"
    if os.path.exists(db_script):
        print(f"Running {db_script}...")
        try:
            subprocess.check_call([sys.executable, db_script])
            print("Database initialized successfully.")
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to initialize database. {e}")
            # Don't exit, maybe just a warning if DB is locked or something
    else:
        print(f"ERROR: {db_script} not found.")

def verify_imports():
    print_step("Verifying Installations")
    modules = ["flask", "dotenv", "requests", "google.generativeai", "waitress"]
    all_good = True
    for module in modules:
        if importlib.util.find_spec(module) is None:
            print(f"ERROR: Module '{module}' is not installed.")
            all_good = False
        else:
            print(f"Module '{module}' found.")
    
    if all_good:
        print("\nSUCCESS: All dependencies appear to be installed correctly.")
    else:
        print("\nWARNING: Some dependencies are missing.")

def main():
    print("Starting Project Setup...")
    check_python_version()
    install_requirements()
    check_env_file()
    init_database()
    verify_imports()
    
    print("\n" + "="*50)
    print("SETUP COMPLETE")
    print("To run the application, use: python main.py")
    print("Make sure to update .env with your API keys first!")
    print("="*50)

if __name__ == "__main__":
    main()
