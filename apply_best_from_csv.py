import csv
import sys
from src.bitaxe_safe_overclock import BitAxeSafeOverclock

def apply_best_from_csv(csv_filename: str):
    """Apply best settings from a CSV results file"""
    try:
        # Read CSV file
        stable_results = []
        with open(csv_filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['stable'] == 'True':
                    stable_results.append({
                        'frequency': int(row['frequency_mhz']),
                        'core_voltage': int(row['core_voltage_mv']),
                        'hashrate': float(row['hashrate_ghs']),
                        'temperature': float(row['temperature_c'])
                    })
        
        if not stable_results:
            print("❌ No stable results found in CSV file")
            return False
            
        # Find best result
        best = max(stable_results, key=lambda x: x['hashrate'])
        
        print(f"🎯 Best settings from {csv_filename}:")
        print(f"   Frequency: {best['frequency']}MHz")
        print(f"   Voltage: {best['core_voltage']}mV")
        print(f"   Expected: {best['hashrate']:.1f} GH/s @ {best['temperature']:.1f}°C")
        
        # Confirm with user
        response = input("\nApply these settings? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Operation cancelled.")
            return False
            
        # Apply settings
        overclocker = BitAxeSafeOverclock()
        success = overclocker.apply_settings(best['frequency'], best['core_voltage'])
        
        if success:
            print("✅ Settings applied successfully!")
        else:
            print("❌ Failed to apply settings")
            
        return success
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python apply_best_from_csv.py <csv_filename>")
        print("Example: python apply_best_from_csv.py bitaxe_safe_tuning_results_20250910_170544.csv")
        sys.exit(1)
        
    apply_best_from_csv(sys.argv[1])