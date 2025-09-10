#!/usr/bin/env python3
"""
Safe BitAxe Overclock Script
Improved version with comprehensive safety features and hardware protection

Author: Enhanced Safety Version
License: MIT
Warning: Use at your own risk. Overclocking can damage hardware.
"""

import requests
import time
import csv
import json
import logging
import statistics
import sys
import signal
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# ==================== CONFIGURATION ====================

# CRITICAL: Update this with your BitAxe IP address
MINER_IP = "192.168.1.97"  # Example: "192.168.1.100"

# Safety Limits (CONSERVATIVE DEFAULTS)
SAFETY_CONFIG = {
    # Temperature limits (Celsius) - Updated based on community data
    "max_temp_warning": 65,      # Warning threshold (was 55)
    "max_temp_critical": 70,     # Emergency shutdown (was 60) 
    "max_temp_absolute": 75,     # Absolute maximum (was 65)
    
    # Voltage limits (mV) - Conservative for Gamma 601
    "cv_start": 1100,            # Starting core voltage
    "cv_max": 1300,              # Maximum safe voltage
    "cv_step": 25,               # Voltage increment
    "cv_danger_threshold": 1250, # Requires confirmation above this
    
    # Frequency limits (MHz)
    "freq_start": 525,           # Starting frequency (stock frequency)
    "freq_end": 650,             # Maximum frequency
    "freq_step": 25,             # Frequency increment
    
    # Stability and timing
    "stability_samples": 10,     # Samples for stability check
    "stability_interval": 30,    # Seconds between samples
    "settle_time": 60,           # Seconds to settle after change
    "max_cv_variation": 0.15,    # Maximum coefficient of variation
    "min_hashrate_threshold": 50, # Minimum acceptable hashrate (GH/s)
    
    # Safety delays
    "emergency_cooldown": 300,   # Cooldown after emergency stop
    "confirmation_timeout": 30,  # Timeout for user confirmations
}

# Logging configuration
LOGGING_CONFIG = {
    "level": logging.INFO,
    "format": "%(asctime)s - %(levelname)s - %(message)s",
    "file": "bitaxe_safe_overclock.log"
}

@dataclass
class MinerState:
    """Represents the current state of the miner"""
    frequency: int
    core_voltage: int
    temperature: float
    hashrate: float
    power: float
    timestamp: datetime
    stable: bool = False
    
class SafetyException(Exception):
    """Custom exception for safety-related issues"""
    pass

class BitAxeSafeOverclock:
    def __init__(self):
        self.base_url = f"http://{MINER_IP}"
        self.original_settings = None
        self.emergency_stop = False
        self.results = []
        self.setup_logging()
        self.setup_signal_handlers()
        
    def setup_logging(self):
        """Configure comprehensive logging"""
        logging.basicConfig(
            level=LOGGING_CONFIG["level"],
            format=LOGGING_CONFIG["format"],
            handlers=[
                logging.FileHandler(LOGGING_CONFIG["file"]),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.emergency_shutdown)
        signal.signal(signal.SIGTERM, self.emergency_shutdown)
        
    def emergency_shutdown(self, signum=None, frame=None):
        """Emergency shutdown procedure"""
        self.logger.critical("🚨 EMERGENCY SHUTDOWN INITIATED (Ctrl+C detected)")
        self.emergency_stop = True
        
        # Don't call sys.exit() here - let the main loop handle it gracefully
        print("\n⚠️  Emergency stop requested. Cleaning up safely...")
        if self.original_settings:
            self.logger.info("Restoring original settings...")
            self.restore_original_settings()
            
        self.logger.info("Emergency shutdown complete")
        sys.exit(1)
        
    def validate_configuration(self) -> bool:
        """Validate configuration and connectivity"""
        self.logger.info("Validating configuration...")
        
        # Check IP address format
        if MINER_IP == "REPLACE_WITH_YOUR_BITAXE_IP":
            self.logger.error("Please update MINER_IP with your BitAxe IP address")
            return False
            
        # Test connectivity
        try:
            response = self.make_api_request("/api/system/info")
            if not response:
                return False
                
            self.logger.info(f"Connected to BitAxe: {response.get('ASICModel', 'Unknown')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Connectivity test failed: {e}")
            return False
            
    def make_api_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Optional[Dict]:
        """Make API request with error handling and retries"""
        url = f"http://{MINER_IP}{endpoint}"
        
        for attempt in range(3):  # 3 retry attempts
            try:
                if method == "GET":
                    response = requests.get(url, timeout=10)
                elif method == "POST":
                    response = requests.post(url, json=data, timeout=10)
                elif method == "PATCH":
                    response = requests.patch(url, json=data, timeout=10)
                else:
                    self.logger.error(f"Unsupported HTTP method: {method}")
                    return None
                
                # Log the response details for debugging
                self.logger.debug(f"Response: {response.status_code} for {method} {endpoint}")
                    
                # Accept all 2xx status codes (200-299) as successful
                if 200 <= response.status_code < 300:
                    # Handle empty responses (common with PATCH)
                    if response.text.strip():
                        try:
                            return response.json()
                        except json.JSONDecodeError:
                            self.logger.warning(f"Invalid JSON response from {endpoint}, treating as success")
                            return {}  # Treat invalid JSON as successful empty response
                    else:
                        return {}  # Return empty dict for successful empty responses
                else:
                    self.logger.error(f"HTTP error {response.status_code}: {endpoint}")
                    if attempt == 2:  # Last attempt
                        return None
                    
            except requests.exceptions.Timeout:
                self.logger.warning(f"Timeout on attempt {attempt + 1} for {endpoint}")
            except requests.exceptions.ConnectionError:
                self.logger.error(f"Connection error for {endpoint}")
                return None
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request error for {endpoint}: {e}")
                
            if attempt < 2:  # Don't sleep on last attempt
                time.sleep(1)
                
        return None
        
    def get_current_state(self) -> Optional[MinerState]:
        """Get current miner state with validation"""
        system_info = self.make_api_request("/api/system/info")
        if not system_info:
            return None
            
        try:
            state = MinerState(
                frequency=int(system_info.get('frequency', 0)),
                core_voltage=int(system_info.get('coreVoltage', 0)),
                temperature=float(system_info.get('temp', 0)),
                hashrate=float(system_info.get('hashRate', 0)),
                power=float(system_info.get('power', 0)),
                timestamp=datetime.now()
            )
            
            # Validate readings
            if state.temperature <= 0 or state.temperature > 100:
                raise SafetyException(f"Invalid temperature reading: {state.temperature}°C")
                
            if state.hashrate < 0:
                raise SafetyException(f"Invalid hashrate reading: {state.hashrate}")
                
            return state
            
        except (ValueError, KeyError) as e:
            self.logger.error(f"Error parsing miner state: {e}")
            return None
            
    def check_safety_limits(self, state: MinerState) -> bool:
        """Comprehensive safety limit checking"""
        # Critical temperature check
        if state.temperature >= SAFETY_CONFIG["max_temp_absolute"]:
            raise SafetyException(f"CRITICAL: Temperature {state.temperature}°C exceeds absolute maximum!")
            
        # Emergency temperature check
        if state.temperature >= SAFETY_CONFIG["max_temp_critical"]:
            self.logger.error(f"EMERGENCY: Temperature {state.temperature}°C exceeds critical threshold!")
            return False
            
        # Warning temperature check
        if state.temperature >= SAFETY_CONFIG["max_temp_warning"]:
            self.logger.warning(f"WARNING: Temperature {state.temperature}°C approaching limits")
            
        # Hashrate sanity check
        if state.hashrate < SAFETY_CONFIG["min_hashrate_threshold"]:
            self.logger.warning(f"Low hashrate detected: {state.hashrate} GH/s")
            
        return True
        
    def backup_original_settings(self) -> bool:
        """Backup original settings for recovery"""
        self.logger.info("Backing up original settings...")
        
        state = self.get_current_state()
        if not state:
            self.logger.error("Failed to backup original settings")
            return False
            
        self.original_settings = {
            "frequency": state.frequency,
            "core_voltage": state.core_voltage
        }
        
        self.logger.info(f"Original settings backed up: {self.original_settings}")
        return True
        
    def restore_original_settings(self) -> bool:
        """Restore original settings"""
        if not self.original_settings:
            self.logger.error("No original settings to restore")
            return False
            
        self.logger.info("Restoring original settings...")
        
        success = self.apply_settings(
            self.original_settings["frequency"],
            self.original_settings["core_voltage"]
        )
        
        if success:
            self.logger.info("Original settings restored successfully")
        else:
            self.logger.error("Failed to restore original settings")
            
        return success
        
    def apply_settings(self, frequency: int, core_voltage: int) -> bool:
        """Apply frequency and voltage settings safely"""
        self.logger.info(f"Applying settings: {frequency}MHz, {core_voltage}mV")
        
        # Apply frequency using PATCH method
        freq_data = {"frequency": frequency}
        freq_response = self.make_api_request("/api/system", "PATCH", freq_data)
        if freq_response is None:
            self.logger.error("Failed to set frequency")
            return False
            
        # Apply core voltage using PATCH method
        voltage_data = {"coreVoltage": core_voltage}
        voltage_response = self.make_api_request("/api/system", "PATCH", voltage_data)
        if voltage_response is None:
            self.logger.error("Failed to set core voltage")
            return False
            
        # Wait for settings to take effect
        time.sleep(SAFETY_CONFIG["settle_time"])
        return True
        
    def test_stability(self, frequency: int, core_voltage: int) -> Tuple[bool, List[float], float]:
        """Test stability with emergency stop checks"""
        self.logger.info(f"Testing stability: {frequency}MHz @ {core_voltage}mV")
        
        # Settle time with emergency stop checks
        settle_time = SAFETY_CONFIG["settle_time"]
        self.logger.info(f"Settling for {settle_time} seconds...")
        
        for i in range(settle_time):
            if self.emergency_stop:
                self.logger.info("Emergency stop during settle time")
                return False, [], 0.0
            time.sleep(1)
        
        hashrates = []
        samples = SAFETY_CONFIG["stability_samples"]
        interval = SAFETY_CONFIG["stability_interval"]
        
        for i in range(samples):
            if self.emergency_stop:
                self.logger.info(f"Emergency stop during stability test (sample {i+1}/{samples})")
                return False, hashrates, 0.0
                
            state = self.get_current_state()
            if not state:
                self.logger.error(f"Failed to get state for sample {i+1}")
                continue
                
            hashrates.append(state.hashrate)
            self.logger.info(f"Sample {i+1}/{samples}: {state.hashrate:.1f} GH/s, {state.temperature:.1f}°C")
            
            # Safety check
            if not self.check_safety_limits(state):
                raise SafetyException(f"Safety limits exceeded during stability test")
            
            # Sleep with emergency stop checks
            if i < samples - 1:  # Don't sleep after last sample
                for j in range(interval):
                    if self.emergency_stop:
                        self.logger.info(f"Emergency stop during interval wait")
                        return False, hashrates, 0.0
                    time.sleep(1)
        
        if not hashrates:
            return False, [], 0.0
            
        mean_hashrate = statistics.mean(hashrates)
        
        # Check minimum hashrate threshold
        if mean_hashrate < SAFETY_CONFIG["min_hashrate_threshold"]:
            self.logger.warning(f"Hashrate too low: {mean_hashrate:.1f} < {SAFETY_CONFIG['min_hashrate_threshold']} GH/s")
            return False, hashrates, mean_hashrate
        
        # Calculate coefficient of variation
        if len(hashrates) > 1:
            cv = statistics.stdev(hashrates) / mean_hashrate
            stable = cv <= SAFETY_CONFIG["max_cv_variation"]
            self.logger.info(f"Stability test: CV = {cv:.3f} ({'STABLE' if stable else 'UNSTABLE'})")
            return stable, hashrates, mean_hashrate
        else:
            return True, hashrates, mean_hashrate
        
    def require_user_confirmation(self, message: str) -> bool:
        """Require user confirmation for dangerous operations"""
        self.logger.warning(f"USER CONFIRMATION REQUIRED: {message}")
        print(f"\n⚠️  {message}")
        print("Do you want to continue? (yes/no): ", end="")
        
        try:
            response = input().strip().lower()
            return response in ['yes', 'y']
        except KeyboardInterrupt:
            self.logger.info("User cancelled operation")
            return False
            
    def save_results(self):
        """Save results to CSV with comprehensive data"""
        filename = f"bitaxe_safe_tuning_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = [
                'timestamp', 'frequency_mhz', 'core_voltage_mv', 'hashrate_ghs',
                'temperature_c', 'power_w', 'stable', 'cv', 'notes'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for result in self.results:
                writer.writerow(result)
                
        self.logger.info(f"Results saved to {filename}")
        
    def run_overclock_sweep(self):
        """Optimized overclocking sweep - finds minimum voltage for each frequency"""
        self.logger.info("Starting optimized BitAxe overclock sweep (frequency-first)")
        
        # Validation phase
        if not self.validate_configuration():
            self.logger.error("Configuration validation failed")
            return False
            
        # Backup original settings
        if not self.backup_original_settings():
            self.logger.error("Failed to backup original settings")
            return False
            
        try:
            # Optimized sweep loop - FREQUENCY FIRST
            for freq in range(SAFETY_CONFIG["freq_start"], SAFETY_CONFIG["freq_end"] + 1, SAFETY_CONFIG["freq_step"]):
                if self.emergency_stop:
                    break
                    
                self.logger.info(f"\n🎯 === Finding minimum voltage for {freq}MHz ===")
                voltage_found = False
                
                # Test voltages from lowest to highest for this frequency
                for cv in range(SAFETY_CONFIG["cv_start"], SAFETY_CONFIG["cv_max"] + 1, SAFETY_CONFIG["cv_step"]):
                    if self.emergency_stop:
                        break
                        
                    # Require confirmation for dangerous voltages
                    if cv >= SAFETY_CONFIG["cv_danger_threshold"]:
                        if not self.require_user_confirmation(
                            f"About to test potentially dangerous voltage: {cv}mV at {freq}MHz"):
                            self.logger.info("User declined dangerous voltage test")
                            break
                            
                    self.logger.info(f"Testing {freq}MHz @ {cv}mV")
                    
                    # Apply settings
                    if not self.apply_settings(freq, cv):
                        self.logger.error("Failed to apply settings, skipping")
                        continue
                        
                    # Test stability
                    stable, hashrates, mean_hashrate = self.test_stability(freq, cv)
                    
                    # Get final state
                    final_state = self.get_current_state()
                    if not final_state:
                        self.logger.error("Failed to get final state")
                        continue
                        
                    # Calculate coefficient of variation
                    cv_value = 0.0
                    if len(hashrates) > 1 and mean_hashrate > 0:
                        cv_value = statistics.stdev(hashrates) / mean_hashrate
                        
                    # Record results
                    result = {
                        'timestamp': final_state.timestamp.isoformat(),
                        'frequency_mhz': freq,
                        'core_voltage_mv': cv,
                        'hashrate_ghs': mean_hashrate,
                        'temperature_c': final_state.temperature,
                        'power_w': final_state.power,
                        'stable': stable,
                        'cv': cv_value,
                        'notes': f'stable_min_voltage' if stable else 'unstable'
                    }
                    
                    self.results.append(result)
                    
                    # Log result
                    if stable:
                        self.logger.info(f"✅ SUCCESS: {freq}MHz stable at {cv}mV - {mean_hashrate:.1f} GH/s, {final_state.temperature:.1f}°C")
                        self.logger.info(f"🎯 MINIMUM VOLTAGE FOUND for {freq}MHz: {cv}mV")
                        voltage_found = True
                        break  # Found minimum voltage, move to next frequency
                    else:
                        self.logger.info(f"❌ UNSTABLE: {freq}MHz @ {cv}mV - {mean_hashrate:.1f} GH/s, trying higher voltage")
                    
                    # Safety check after each test
                    if not self.check_safety_limits(final_state):
                        self.logger.error("Safety limits exceeded, stopping sweep")
                        self.emergency_stop = True
                        break
                        
                if not voltage_found and not self.emergency_stop:
                    self.logger.warning(f"⚠️  No stable voltage found for {freq}MHz within safe limits")
                    
        except SafetyException as e:
            self.logger.critical(f"Safety exception: {e}")
            self.emergency_shutdown()
            
        except Exception as e:
            self.logger.error(f"Unexpected error during sweep: {e}")
            
        finally:
            # Cleanup and restore
            self.logger.info("Cleaning up...")
            
            if self.emergency_stop:
                self.logger.info("🛑 Emergency stop detected - restoring settings immediately")
            
            self.restore_original_settings()
            self.save_results()
            
            if self.emergency_stop:
                self.logger.info("✅ Emergency shutdown completed safely")
                print("\n✅ Script stopped safely. Original settings restored.")
                sys.exit(0)  # Clean exit after proper cleanup
            else:
                self.logger.info("🎉 Optimized sweep completed successfully!")
                self.logger.info("📊 Results show MINIMUM VOLTAGE for each frequency")
                
        return True
        
def main():
    """Main entry point"""
    print("BitAxe Safe Overclock Script")
    print("=============================")
    print("⚠️  WARNING: Overclocking can damage your hardware!")
    print("⚠️  Use at your own risk and ensure adequate cooling.")
    print("⚠️  This script includes safety features but cannot guarantee hardware safety.")
    print()
    
    # Final user confirmation
    response = input("Do you understand the risks and want to continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Operation cancelled by user.")
        return
        
    overclocker = BitAxeSafeOverclock()
    overclocker.run_overclock_sweep()
    
if __name__ == "__main__":
    main()