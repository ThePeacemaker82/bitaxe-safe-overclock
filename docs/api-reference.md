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
- `POST /api/system` - Update system settings

### Error Handling

#### SafetyException
Custom exception raised when safety limits are exceeded:

```python
class SafetyException(Exception):
    """Custom exception for safety-related issues"""
    pass
```

### Example Usage

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