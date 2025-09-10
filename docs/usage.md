# 📖 Usage Instructions

## 🚀 Quick Start

### 1. Configuration
Before running the script, update the miner IP address:

```python
# In src/bitaxe_safe_overclock.py, line 23
MINER_IP = "192.168.1.97"  # Replace with your BitAxe IP
```

### 2. Safety Profiles
Choose a safety profile in `config/safety_config.json`:

- **Conservative**: Max 55°C, 1200mV, 600MHz
- **Moderate**: Max 60°C, 1300mV, 650MHz  
- **Aggressive**: Max 65°C, 1400mV, 700MHz

### 3. Basic Usage
```bash
python src/bitaxe_safe_overclock.py
```

## ⚙️ Advanced Configuration

### Temperature Limits
- `max_temp_warning`: 65°C (warning threshold)
- `max_temp_critical`: 70°C (emergency shutdown)
- `max_temp_absolute`: 75°C (absolute maximum)

### Voltage Settings
- `cv_start`: 1100mV (starting voltage)
- `cv_max`: 1300mV (maximum safe voltage)
- `cv_step`: 25mV (voltage increment)

### Frequency Settings
- `freq_start`: 525MHz (starting frequency)
- `freq_end`: 650MHz (maximum frequency)
- `freq_step`: 25MHz (frequency increment)

### Stability Testing
- `stability_samples`: 10 (number of samples)
- `stability_interval`: 30s (time between samples)
- `max_cv_variation`: 0.15 (coefficient of variation limit)

## 🛡️ Safety Features

### Emergency Stop
Press `Ctrl+C` to trigger emergency shutdown and restore original settings.

### Automatic Protections
- Temperature monitoring every 30 seconds
- Automatic rollback on instability
- Hardware-specific voltage limits
- Confirmation required for dangerous settings

## 📊 Results

Results are saved to:
- `bitaxe_overclock_results.csv` - Detailed test data
- `bitaxe_safe_overclock.log` - Complete operation log

## 🔧 Hardware Profiles

### BitAxe Gamma 601
- Recommended max voltage: 1300mV
- Recommended max frequency: 650MHz

### BitAxe Supra
- Recommended max voltage: 1250mV
- Recommended max frequency: 600MHz

### BitAxe Ultra
- Recommended max voltage: 1200mV
- Recommended max frequency: 550MHz

## ⚠️ Important Notes

1. **Always ensure adequate cooling** before overclocking
2. **Monitor temperatures closely** during testing
3. **Start with conservative settings** and gradually increase
4. **Use at your own risk** - overclocking can damage hardware
5. **Keep original firmware backup** for recovery