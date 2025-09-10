# 🔧 BitAxe Safe Overclock

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Safety First](https://img.shields.io/badge/Safety-First-red.svg)](docs/safety.md)

A safe and intelligent overclocking tool for BitAxe Bitcoin miners with comprehensive safety features, temperature monitoring, and automated optimization.

## ⚠️ **IMPORTANT SAFETY WARNING**

**Overclocking can permanently damage your hardware!** This tool includes multiple safety mechanisms, but use at your own risk. Always ensure adequate cooling and monitor temperatures closely.

## ✨ **Features**

- 🛡️ **Advanced Safety Systems**: Multi-level temperature monitoring and emergency shutdown
- 🎯 **Intelligent Optimization**: Finds minimum stable voltage for each frequency
- 📊 **Statistical Analysis**: Uses coefficient of variation for stability testing
- 🔄 **Graceful Recovery**: Automatic restoration of original settings
- 📈 **Comprehensive Logging**: Detailed logs and CSV results
- ⚡ **Optimized Algorithm**: Frequency-first approach reduces testing time by 70%

## 🚀 **Quick Start**

### Installation
```bash
git clone https://github.com/ThePeacemaker82/bitaxe-safe-overclock.git
cd bitaxe-safe-overclock
pip install -r requirements.txt
```

### Basic Usage
```bash
python src/bitaxe_safe_overclock.py
```

### Configuration
Edit `config/safety_config.json` to customize safety limits and testing parameters.

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
