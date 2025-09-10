# 🤝 Contributing to BitAxe Safe Overclock

Thank you for your interest in contributing! This project aims to provide safe and reliable overclocking tools for the BitAxe community.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- BitAxe hardware for testing
- Basic understanding of overclocking principles

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/bitaxe-safe-overclock.git`
3. Install dependencies: `pip install -r requirements.txt`
4. Run tests: `python -m pytest tests/`

## 📋 How to Contribute

### Reporting Bugs
- Use the GitHub issue tracker
- Include BitAxe model, firmware version, and error logs
- Provide steps to reproduce the issue

### Suggesting Features
- Open an issue with the "enhancement" label
- Describe the use case and expected behavior
- Consider safety implications

### Code Contributions
1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

## 🛡️ Safety Guidelines

### Critical Requirements
- **Never bypass safety limits** without explicit user confirmation
- **Always include temperature monitoring** in new features
- **Test thoroughly** on multiple hardware configurations
- **Document potential risks** clearly

### Code Standards
- Follow PEP 8 style guidelines
- Include comprehensive docstrings
- Add type hints for all functions
- Handle errors gracefully

## 🧪 Testing

### Test Categories
- **Unit tests**: Individual function testing
- **Integration tests**: API communication testing
- **Safety tests**: Emergency shutdown and limit testing
- **Hardware tests**: Real device validation

### Running Tests
```bash
# All tests
python -m pytest tests/

# Specific test file
python -m pytest tests/test_safety.py

# With coverage
python -m pytest --cov=src tests/
```

## 📝 Documentation

- Update relevant documentation for any changes
- Include code examples for new features
- Update API reference for new methods
- Add safety warnings where appropriate

## 🏷️ Pull Request Process

1. **Description**: Clearly describe what your PR does
2. **Testing**: Include test results and hardware tested
3. **Safety**: Confirm no safety features were compromised
4. **Documentation**: Update docs if needed
5. **Review**: Address feedback promptly

## 📞 Community

- Join discussions in GitHub issues
- Share testing results and findings
- Help other users with questions
- Report successful overclocking configurations

## ⚠️ Disclaimer

Contributors acknowledge that:
- Overclocking can damage hardware
- Users assume all risks
- Safety features may not prevent all damage
- Thorough testing is essential

Thank you for helping make BitAxe overclocking safer for everyone! 🙏