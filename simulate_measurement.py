import requests
import json
import datetime
import random

# Configuration
EDGE_URL = "http://127.0.0.1:5000/OnControl/parameters"
DEVICE_ID = "smart-band-001"
API_KEY = "test-api-key"

def simulate_measurement(scenario="normal"):
    """
    Simulates a measurement and sends it to the Edge.
    Scenario can be 'normal' or 'critical'.
    """
    print(f"\n--- Simulating {scenario.upper()} measurement ---")
    
    if scenario == "critical":
        # Generate risky values (e.g., High BPM or Fever)
        bpm = random.uniform(110, 140)
        temp = random.uniform(38.0, 39.5)
        spo2 = random.uniform(85, 92)
    else:
        # Generate normal values
        bpm = random.uniform(60, 90)
        temp = random.uniform(36.0, 37.0)
        spo2 = random.uniform(96, 99)

    payload = {
        "device_id": DEVICE_ID,
        "bpm": round(bpm, 1),
        "temp": round(temp, 1),
        "spo2": round(spo2, 1),
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    
    headers = {
        "X-API-Key": "test-api-key-123",
        "Content-Type": "application/json"
    }

    try:
        print(f"Sending data: BPM={payload['bpm']}, Temp={payload['temp']}, SpO2={payload['spo2']}")
        response = requests.post(EDGE_URL, json=payload, headers=headers)
        
        if response.status_code == 201:
            data = response.json()
            print("✅ Data received by Edge.")
            
            # Check for Actuator Command
            actuator = data.get("actuator_command", {})
            if actuator.get("alarm"):
                print("\n🚨 ACTUATOR TRIGGERED: ALARM ON! 🚨")
                print("(Reason: Abnormal health parameters detected)")
            else:
                print("\n🟢 Actuator Status: Normal (Alarm OFF)")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to Edge Service. Is it running?")

if __name__ == "__main__":
    print("Select scenario to simulate:")
    print("1. Normal Health")
    print("2. Critical Health (Trigger Alarm)")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == "2":
        simulate_measurement("critical")
    else:
        simulate_measurement("normal")
