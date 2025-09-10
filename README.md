# 🔧 BitAxe Safe Overclock

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Safety First](https://img.shields.io/badge/Safety-First-red.svg)](docs/safety.md)

A safe and intelligent overclocking tool for BitAxe Bitcoin miners with comprehensive safety features, temperature monitoring, automated optimization, and **optimal settings application**.

## ⚠️ **IMPORTANT SAFETY WARNING**

**Overclocking can permanently damage your hardware!** This tool includes multiple safety mechanisms, but use at your own risk. Always ensure adequate cooling and monitor temperatures closely.

## ✨ **Features**

- 🛡️ **Advanced Safety Systems**: Multi-level temperature monitoring and emergency shutdown
- 🎯 **Intelligent Optimization**: Finds minimum stable voltage for each frequency
- 📊 **Statistical Analysis**: Uses coefficient of variation for stability testing
- 🔄 **Graceful Recovery**: Automatic restoration of original settings
- 📈 **Comprehensive Logging**: Detailed logs and CSV results
- ⚡ **Optimized Algorithm**: Frequency-first approach reduces testing time by 70%
- 🎯 **Smart Application**: Apply best settings found during sweep or from previous results
- 📋 **Results Management**: Load and apply optimal settings from CSV files

## 🚀 **Quick Start**

### Installation
```bash
git clone https://github.com/ThePeacemaker82/bitaxe-safe-overclock.git
cd bitaxe-safe-overclock
pip install -r requirements.txt
```

### Basic Usage
```bash
# Run full optimization sweep
python src/bitaxe_safe_overclock.py

# Apply best settings from previous results
python3 apply_best_from_csv.py bitaxe_safe_tuning_results_YYYYMMDD_HHMMSS.csv
```

### Configuration
Edit `config/safety_config.json` to customize safety limits and testing parameters.

## 🎯 **New: Optimal Settings Application**

### During Sweep
After completing the optimization sweep, you'll be prompted to:
1. **Apply best settings found** - Automatically applies the optimal frequency/voltage combination
2. **Restore original settings** - Returns to pre-sweep configuration

### From Previous Results
Apply optimal settings from any previous sweep:
```bash
python3 apply_best_from_csv.py your_results_file.csv
```

### Features:
- 🔍 **Automatic Analysis**: Finds highest hashrate with stable operation
- ✅ **User Confirmation**: Requires explicit approval before applying settings
- 🔒 **Safety Verification**: Validates settings before application
- 📊 **Performance Preview**: Shows expected hashrate and temperature

## 📖 **Documentation**

- [Installation Guide](docs/installation.md)
- [Usage Instructions](docs/usage.md)
- [Safety Guidelines](docs/safety.md)
- [API Reference](docs/api-reference.md)

## 🤝 **Contributing**

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on contributing to this project.

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ **Disclaimer**

This software is provided "as is" without warranty. Overclocking can void warranties and damage hardware. Users assume all risks.
