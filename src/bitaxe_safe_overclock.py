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
    'max_temperature': 85,
    'max_vr_temperature': 90,
    'max_power': 40,
    'min_efficiency': 25,
    'max_voltage': 1200,
    'min_voltage': 1000,
    'max_frequency': 800,
    'min_frequency': 400,
    'stability_test_duration': 300,
    'temperature_check_interval': 30,
    'max_consecutive_failures': 3,
    'cv_start': 1100,
    'cv_end': 1200,
    'cv_step': 25,
    'cv_danger_threshold': 1150,  # Soglia di tensione pericolosa aggiunta
    'freq_start': 600,
    'freq_end': 750,
    'freq_step': 25,
    'settle_time': 5,
    'stability_samples': 10,
    'stability_interval': 30,
    'min_hashrate_threshold': 10.0,
    'max_cv_variation': 0.10  # Coefficiente di variazione massimo per stabilità (aumentato al 10%)
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
    vr_temperature: float
    hash_rate: float
    power: float
    shares_accepted: int
    shares_rejected: int
    uptime: int
    timestamp: datetime = None
    efficiency: float = 0.0
    stable: bool = False
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        self.efficiency = self.hash_rate / self.power if self.power > 0 else 0
    timestamp: datetime
    stable: bool = False
    
class SafetyException(Exception):
    """Custom exception for safety-related issues"""
    pass

class BitAxeSafeOverclock:
    def __init__(self):
        self.miner_ip = MINER_IP  # Aggiunto attributo mancante
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
        
    def get_current_state(self) -> MinerState:
        """Ottiene lo stato attuale del miner"""
        try:
            response = requests.get(f"http://{self.miner_ip}/api/system/info", timeout=10)
            response.raise_for_status()
            data = response.json()
            
            return MinerState(
                frequency=data.get('frequency', 0),
                core_voltage=data.get('coreVoltage', 0),  # Corretto nome attributo
                temperature=data.get('temp', 0),
                vr_temperature=data.get('vrTemp', 0),
                hash_rate=data.get('hashRate', 0),
                power=data.get('power', 0),
                efficiency=0,  # Calcolato in __post_init__
                shares_accepted=data.get('sharesAccepted', 0),
                shares_rejected=data.get('sharesRejected', 0),
                uptime=data.get('uptimeSeconds', 0)
                # timestamp viene impostato automaticamente in __post_init__
            )
        except Exception as e:
            self.logger.error(f"Errore nel recupero stato: {e}")
            raise
        
    def check_safety_limits(self, state: MinerState) -> bool:
        """Verifica che tutti i parametri siano entro i limiti di sicurezza"""
        if state.temperature > SAFETY_CONFIG['max_temperature']:
            self.logger.warning(f"Temperatura ASIC troppo alta: {state.temperature}°C")
            return False
        
        if state.vr_temperature > SAFETY_CONFIG['max_vr_temperature']:
            self.logger.warning(f"Temperatura VR troppo alta: {state.vr_temperature}°C")
            return False
        
        if state.power > SAFETY_CONFIG['max_power']:
            self.logger.warning(f"Potenza troppo alta: {state.power}W")
            return False
        
        if state.efficiency < SAFETY_CONFIG['min_efficiency']:
            self.logger.warning(f"Efficienza troppo bassa: {state.efficiency} GH/W")
            return False
        
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
                
            hashrates.append(state.hash_rate)  # Cambiato da state.hashrate
            self.logger.info(f"Sample {i+1}/{samples}: {state.hash_rate:.1f} GH/s, {state.temperature:.1f}°C")  # Cambiato da state.hashrate
            
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
        return filename  # Return filename for apply_best_settings

    def find_best_settings(self) -> Optional[Dict]:
        """Find the best stable settings from results"""
        if not self.results:
            self.logger.error("No results available to analyze")
            return None
            
        # Filter only stable results
        stable_results = [r for r in self.results if r['stable']]
        
        if not stable_results:
            self.logger.error("No stable results found")
            return None
            
        # Find best result based on highest hashrate
        best_result = max(stable_results, key=lambda x: x['hashrate_ghs'])
        
        self.logger.info(f"Best settings found: {best_result['frequency_mhz']}MHz @ {best_result['core_voltage_mv']}mV")
        self.logger.info(f"Performance: {best_result['hashrate_ghs']:.1f} GH/s, {best_result['temperature_c']:.1f}°C")
        
        return {
            'frequency': best_result['frequency_mhz'],
            'core_voltage': best_result['core_voltage_mv'],
            'hashrate': best_result['hashrate_ghs'],
            'temperature': best_result['temperature_c']
        }

    def apply_best_settings(self) -> bool:
        """Apply the best settings found during sweep"""
        best_settings = self.find_best_settings()
        
        if not best_settings:
            self.logger.error("Cannot apply best settings - no optimal configuration found")
            return False
            
        self.logger.info("🎯 Applying best settings found during sweep...")
        
        # Ask for user confirmation
        message = f"Apply best settings: {best_settings['frequency']}MHz @ {best_settings['core_voltage']}mV?\n"
        message += f"Expected performance: {best_settings['hashrate']:.1f} GH/s @ {best_settings['temperature']:.1f}°C"
        
        if not self.require_user_confirmation(message):
            self.logger.info("User cancelled applying best settings")
            return False
            
        # Apply the settings
        success = self.apply_settings(best_settings['frequency'], best_settings['core_voltage'])
        
        if success:
            self.logger.info("✅ Best settings applied successfully!")
            self.logger.info(f"New settings: {best_settings['frequency']}MHz @ {best_settings['core_voltage']}mV")
            
            # Verify the settings are working
            time.sleep(30)  # Wait for stabilization
            current_state = self.get_current_state()
            if current_state:
                self.logger.info(f"Current performance: {current_state.hash_rate:.1f} GH/s @ {current_state.temperature:.1f}°C")
        else:
            self.logger.error("❌ Failed to apply best settings")
            
        return success

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
                for cv in range(SAFETY_CONFIG["cv_start"], SAFETY_CONFIG["cv_end"] + 1, SAFETY_CONFIG["cv_step"]):
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
            else:
                # Ask user if they want to apply best settings or restore original
                print("\n🎯 Sweep completed successfully!")
                print("Choose an option:")
                print("1. Apply best settings found")
                print("2. Restore original settings")
                
                choice = input("Enter your choice (1 or 2): ").strip()
                
                if choice == "1":
                    if not self.apply_best_settings():
                        self.logger.info("Falling back to original settings...")
                        self.restore_original_settings()
                else:
                    self.restore_original_settings()
            
            filename = self.save_results()
            
            if self.emergency_stop:
                self.logger.info("✅ Emergency shutdown completed safely")
                print("\n✅ Script stopped safely. Original settings restored.")
                sys.exit(0)  # Clean exit after proper cleanup
            else:
                self.logger.info("🎉 Optimized sweep completed successfully!")
                self.logger.info("📊 Results show MINIMUM VOLTAGE for each frequency")
                print(f"\n📊 Results saved to: {filename}")
                
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