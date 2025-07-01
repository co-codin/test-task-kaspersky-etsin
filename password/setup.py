import os

def install_requirements():
    exit_code = os.system("pip3 install -r requirements.txt")
    return exit_code == 0

def main():
    if not install_requirements():
        print("\n[!] Failed to install Python packages")
        exit(1)

if __name__ == "__main__":
    main()