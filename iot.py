import network
import time
import machine
import urequests
import ujson

# WiFi Configuration
WIFI_SSID = "Alex"
WIFI_PASSWORD = "Alexan101"

# Sensor Configuration
PIR_PIN = 25
pir = machine.Pin(PIR_PIN, machine.Pin.IN)

# Servo Configuration
servos = [
     {"pwm": machine.PWM(machine.Pin(32), freq=50), "name": "Servo 1 (GPIO 32)"},
     {"pwm": machine.PWM(machine.Pin(33), freq=50), "name": "Servo 2 (GPIO 33)"},
     {"pwm": machine.PWM(machine.Pin(12), freq=50), "name": "Servo 3 (GPIO 12)"},
#      {"pwm": machine.PWM(machine.Pin(26), freq=50), "name": "Servo 4 (GPIO 26)"}
]


# Flask Server Configuration
API_URL = "http://172.20.10.3:5000/run"  # Make sure this is the correct IP
 
# Duty cycle bounds (16-bit: 0-65535)
COUNT_LOW = 1638    # ~1ms pulse (0° position)
COUNT_HIGH = 8192   # ~2ms pulse (180° position)

def spin_servos(loc):
    """Move only the selected servo forward and backward with status messages."""
    if loc < 0 or loc >= len(servos):
        print(f"Invalid servo index: {loc}. Must be between 0 and {len(servos)-1}")
        return

    servo = servos[loc]
    print(f"\n--- Starting movement for {servo['name']} ---")

    print(f"Moving {servo['name']} to 90°")
    for duty in range(COUNT_LOW, (COUNT_LOW + COUNT_HIGH) // 2, 100):
        servo["pwm"].duty_u16(duty)
        time.sleep_ms(20)
    time.sleep(2)

    # Move backward (90° → 0°)
    print(f"Returning {servo['name']} to 0°")
    for duty in range((COUNT_LOW + COUNT_HIGH) // 2, COUNT_LOW, -100):
        servo["pwm"].duty_u16(duty)
        time.sleep_ms(20)
    time.sleep(2)



    print(f"{servo['name']} movement complete!\n")

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Connecting to WiFi...")
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        for _ in range(20):  # Timeout after 20 seconds
            if wlan.isconnected():
                print("Connected to Wi-Fi:", wlan.ifconfig())
                return True
            time.sleep(1)
        
        print("Failed to connect to Wi-Fi")
        return False
    return True

def check_db():
    try:
        response = urequests.get(
            'http://172.20.10.3:5000'
        )
        print("Response:", response.text)
        response.close()
        return True
    except Exception as e:
        print("Error Receive data:", e)
        return False
    

def send_sensor_data():
    data = {
        "value": pir.value()  # Changed from "motion" to "value"
    }
    
    try:
        headers = {'Content-Type': 'application/json'}
        response = urequests.post(
            API_URL,
            data=ujson.dumps(data),
            headers=headers
        )
        print("Response:", response.text)
        if response.text == "Servo_paper":
            spin_servos(0)
        elif response.text == "Servo_plastic":
            spin_servos(1)
#         elif response.text == "Servo_plastic":
#         spin_servos(2)
#         else:
#             print(response.text)
        response.close()
        return True
    except Exception as e:
        print("Error sending data:", e)
        return False

# Main execution
if connect_wifi():
    check_db()
    while True:
        print("Current motion:", pir.value())
        if(pir.value()):
#             print(pir.value())
            send_sensor_data()
        time.sleep(2)
else:
    print("Could not initialize WiFi connection")
