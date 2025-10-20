import subprocess
import re

class BluetoothManager:
    def __init__(self):
        pass

    @staticmethod
    def connect_jbl(device_keyword="JBL"):
        # Step 1: Ensure Bluetooth is on
        subprocess.run(["blueutil", "--power", "1"])

        # Step 2: Fetch paired devices
        paired_output = subprocess.check_output(["blueutil", "--paired"]).decode(errors="ignore")

        # Step 3: Find JBL device line
        device_line = None
        for line in paired_output.splitlines():
            if device_keyword.lower() in line.lower():
                device_line = line.strip()
                break

        if not device_line:
            print(f"⚠️ No paired device found with keyword: '{device_keyword}'")
            return False

        # Step 4: Extract MAC address
        match = re.search(r'address:\s*([0-9A-Fa-f:-]+)', device_line)
        if not match:
            print(f"⚠️ Could not extract MAC address from line:\n{device_line}")
            return False

        mac_address = match.group(1)
        print(f"🔍 Found device → {device_line}")
        print(f"🔗 MAC Address: {mac_address}")

        # Step 5: Attempt to connect
        try:
            result = subprocess.run(["blueutil", "--connect", mac_address], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Successfully connected to JBL ({mac_address})")
                return True
            else:
                print(f"⚠️ Connection command returned:\n{result.stderr or result.stdout}")
                return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

if __name__ == "__main__":
    BluetoothManager.connect_jbl()


