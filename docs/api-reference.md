# 🔌 API Reference

## BitAxeSafeOverclock Class

### Constructor
```python
class BitAxeSafeOverclock:
    def __init__(self)
```
Initializes the overclock manager with safety systems.

### Core Methods

#### get_current_state() → Optional[MinerState]
Retrieves current miner status including temperature, hashrate, and settings.

**Returns:**
- `MinerState` object with current parameters
- `None` if communication fails

#### apply_settings(frequency: int, core_voltage: int) → bool
Applies new frequency and voltage settings to the miner.

**Parameters:**
- `frequency`: Target frequency in MHz
- `core_voltage`: Target voltage in mV

**Returns:**
- `True` if settings applied successfully
- `False` if operation failed

#### test_stability(frequency: int, core_voltage: int) → Tuple[bool, List[float], float]
Tests stability of given settings over multiple samples.

**Parameters:**
- `frequency`: Frequency to test in MHz
- `core_voltage`: Voltage to test in mV

**Returns:**
- `(is_stable, hashrate_samples, average_hashrate)`

#### check_safety_limits(state: MinerState) → bool
Verifies if current state is within safety parameters.

**Parameters:**
- `state`: Current miner state

**Returns:**
- `True` if safe
- `False` if safety limits exceeded

#### backup_original_settings() → bool
Saves current miner settings for restoration.

**Returns:**
- `True` if backup successful
- `False` if backup failed

#### restore_original_settings() → bool
Restores previously backed up settings.

**Returns:**
- `True` if restoration successful
- `False` if restoration failed

### 🎯 New: Optimal Settings Management

#### find_best_settings() → Optional[Dict]
Analyzes sweep results to find the optimal stable configuration.

**Returns:**
- Dictionary with best settings:
  ```python
  {
      'frequency': int,        # Optimal frequency (MHz)
      'core_voltage': int,     # Optimal voltage (mV)
      'hashrate': float,       # Expected hashrate (GH/s)
      'temperature': float     # Expected temperature (°C)
  }
  ```
- `None` if no stable results found

**Algorithm:**
- Filters only stable results from sweep
- Selects configuration with highest hashrate
- Ensures temperature and voltage are within safe limits

#### apply_best_settings() → bool
Applies the optimal settings found during the sweep.

**Returns:**
- `True` if best settings applied successfully
- `False` if no optimal settings found or application failed

**Process:**
1. Calls `find_best_settings()` to identify optimal configuration
2. Requests user confirmation with performance preview
3. Applies settings using `apply_settings()`
4. Verifies application with 30-second stabilization period
5. Falls back to original settings if application fails

#### save_results() → str
Saves sweep results to timestamped CSV file.

**Returns:**
- Filename of saved results file

**Enhanced functionality:**
- Now returns filename for use by `apply_best_from_csv.py`
- Maintains backward compatibility

### Data Classes

#### MinerState
```python
@dataclass
class MinerState:
    frequency: int          # Current frequency (MHz)
    core_voltage: int       # Current voltage (mV)
    temperature: float      # Current temperature (°C)
    hashrate: float        # Current hashrate (GH/s)
    power: float           # Current power consumption (W)
    timestamp: datetime    # Measurement timestamp
    stable: bool = False   # Stability flag
```

### Configuration Constants

#### SAFETY_CONFIG
Main safety configuration dictionary:

```python
SAFETY_CONFIG = {
    # Temperature limits (°C)
    "max_temp_warning": 65,
    "max_temp_critical": 70,
    "max_temp_absolute": 75,
    
    # Voltage limits (mV)
    "cv_start": 1100,
    "cv_max": 1300,
    "cv_step": 25,
    
    # Frequency limits (MHz)
    "freq_start": 525,
    "freq_end": 650,
    "freq_step": 25,
    
    # Stability parameters
    "stability_samples": 10,
    "stability_interval": 30,
    "max_cv_variation": 0.15
}
```

### API Endpoints

The script communicates with BitAxe via HTTP API:

- `GET /api/system/info` - System information
- `POST /api/system/restart` - Restart system
- `GET /api/system/stats` - Performance statistics
- `PATCH /api/system` - Update system settings (frequency, voltage)

### Error Handling

#### SafetyException
Custom exception raised when safety limits are exceeded:

```python
class SafetyException(Exception):
    """Custom exception for safety-related issues"""
    pass
```

### Example Usage

#### Basic Operations
```python
from src.bitaxe_safe_overclock import BitAxeSafeOverclock

# Initialize overclock manager
overclocker = BitAxeSafeOverclock()

# Get current state
state = overclocker.get_current_state()
print(f"Current temp: {state.temperature}°C")

# Test specific settings
is_stable, samples, avg_hashrate = overclocker.test_stability(575, 1150)
if is_stable:
    print(f"Settings stable at {avg_hashrate:.1f} GH/s")

# Apply new settings
if overclocker.apply_settings(575, 1150):
    print("Settings applied successfully")
```

#### 🎯 New: Optimal Settings Workflow
```python
from src.bitaxe_safe_overclock import BitAxeSafeOverclock

# Initialize and run sweep
overclocker = BitAxeSafeOverclock()
overclocker.run_overclock_sweep()

# Find and apply best settings
best_settings = overclocker.find_best_settings()
if best_settings:
    print(f"Best: {best_settings['frequency']}MHz @ {best_settings['core_voltage']}mV")
    print(f"Expected: {best_settings['hashrate']:.1f} GH/s @ {best_settings['temperature']:.1f}°C")
    
    # Apply with user confirmation
    if overclocker.apply_best_settings():
        print("✅ Optimal settings applied successfully!")
else:
    print("❌ No stable settings found")
```

#### External CSV Processing
```python
import csv
from src.bitaxe_safe_overclock import BitAxeSafeOverclock

def apply_from_csv(filename):
    # Read and analyze CSV results
    stable_results = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['stable'] == 'True':
                stable_results.append({
                    'frequency': int(row['frequency_mhz']),
                    'core_voltage': int(row['core_voltage_mv']),
                    'hashrate': float(row['hashrate_ghs'])
                })
    
    # Find best result
    if stable_results:
        best = max(stable_results, key=lambda x: x['hashrate'])
        
        # Apply settings
        overclocker = BitAxeSafeOverclock()
        return overclocker.apply_settings(best['frequency'], best['core_voltage'])
    
    return False
```

### 🔄 Workflow Integration

The enhanced API supports two main workflows:

1. **Interactive Sweep**: Run `run_overclock_sweep()` and choose to apply best settings at completion
2. **Batch Processing**: Use `apply_best_from_csv.py` to apply settings from previous results

Both workflows maintain full safety features and user confirmation requirements.