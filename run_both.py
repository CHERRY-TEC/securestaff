import subprocess
import time

print("Starting Company App on port 5000...")
company = subprocess.Popen(['python', 'company_app/app.py'])

print("Starting Client App on port 5001...")
time.sleep(2)
client = subprocess.Popen(['python', 'client_app/app.py'])

print("\n=== Both apps running ===")
print("Company: http://127.0.0.1:5000")
print("Client:  http://127.0.0.1:5001")
print("\nCompany Login: admin@company.com / admin123")
print("Press Ctrl+C to stop both apps\n")

try:
    company.wait()
except KeyboardInterrupt:
    company.terminate()
    client.terminate()
    print("\nBoth apps stopped.")
