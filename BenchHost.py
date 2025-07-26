import serial
import json
import time
import vehicle_config
import os

vc = vehicle_config.VehicleConfig()

# === Config ===
PUNCHCARD_FILE = "V1.jsonl"
UPDATED_FILE = "V1punchcard_tested.jsonl"

META_STATS_FILE = "meta_stats.json"
total_points = 0
complete_test_cycles=0
errors_found = 0
last_updated = time.time()

SERIAL_PORT = "/dev/ttyACM0"  # Adjust as needed
BAUDRATE = 115200

# === Gear to Solenoid Lookup (4L60E encoding) ===
solenoid_encoding = {
    1: 0b01,  # Sol A OFF, Sol B ON
    2: 0b11,  # Sol A ON,  Sol B ON
    3: 0b00,  # Sol A OFF, Sol B OFF
    4: 0b10   # Sol A ON,  Sol B OFF
}

# === Open Serial ===
ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)
#ser.write("import Bench\r\n".encode())
time.sleep(2)

# === Load and Process Punchcard ===
with open(PUNCHCARD_FILE, "r") as infile, open(UPDATED_FILE, "w") as outfile:
    lines = list(infile)  # preload lines to enable index-based control
    index = 0
    waiting_for_ready = False

    while index < len(lines):
        entry = json.loads(lines[index].strip())
        expected_gear = entry.get("expected_gear")
        entry["expected_solenoid"] = solenoid_encoding.get(expected_gear)

        if not waiting_for_ready:
            #cmd = f"{entry['load_adc']},{entry['vss_hz']:.2f}\n"
            load = entry['load_adc']
            hz   = entry['vss_hz']

            # Example: zero-padded integers and floats
            cmd = f"{load:03d},{hz:08.2f}\r\n"
            #cmd = "123,12345.12\r\n"
            # That produces exactly 3 digits for load, comma, 7 characters for float (including decimal)
            try:
                time.sleep(.05)
                ser.reset_input_buffer()  # Clears input buffer (same as flushInput())
                ser.write(cmd.encode())
                ser.flush()  # Ensure command is physically sent
                waiting_for_ready = True
            except serial.SerialException as e:
                print(f"[{index:04}] Serial write failed: {e}")
                break  # or reconnect logic

        try:
            line = ser.readline().decode(errors="ignore").strip()
            if not line:
                continue

            print(f"[RAW RESPONSE] {line}")

            if line.startswith("T"):
                parts = line.split(",")
                timestamp = int(parts[0][1:])
                sol = int(parts[1].split(":")[1])
                entry["measured_solenoid"] = sol
                entry["measured_gear"] = vc.solenoid_pattern_to_gear(sol)
                if sol == entry["expected_solenoid"]:
                    entry["error"] = None
                else:
                    entry["error"] = "Mismatch"
                    errors_found += 1
                entry["timestamp"] = timestamp
                print("[{:05}] {}".format(index, json.dumps(entry)))
                total_points = total_points + 1
                stats = {
                    "VSS_Hz": hz,
                    "Load": load,
                    "expected_gear": expected_gear,
                    "measured_gear": measured_gear,
                    "total_points": total_points,
                    "complete_test_cycles": complete_test_cycles,
                    "errors_found": errors_found,
                    "last_updated": time.time()
                }
                with open(META_STATS_FILE, "w") as f:
                    json.dump(stats, f, indent=2)

            elif line.startswith("ERR"):
                print(f"[{index:04}] Error from device: {line}")
                entry["error"] = line

            elif line == "READY":
                outfile.write(json.dumps(entry) + "\n")
                index += 1
                waiting_for_ready = False

        except Exception as e:
            print(f"[{index:04}] Host-side error: {e}")
complete_test_cycles = complete_test_cycles + 1

ser.close()
