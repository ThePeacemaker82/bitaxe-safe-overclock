from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bitaxe-safe-overclock",
    version="1.0.0",
    author="ThePeacemaker82",
    author_email="ThePeacemaker82@gmail.com",
    description="Safe overclocking tool for BitAxe Bitcoin miners",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ThePeacemaker82/bitaxe-safe-overclock",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
    ],
    entry_points={
        "console_scripts": [
            "bitaxe-overclock=src.bitaxe_safe_overclock:main",
        ],
    },
)
