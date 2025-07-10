"""
Setup script for the Black-Scholes Model package.
"""

from setuptools import setup, find_packages

setup(
    name="backend",
    version="0.1.0",
    description="A Black-Scholes Model implementation for option pricing",
    author="Group 12",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "backend=main:main",
        ],
    },
    package_data={
        "backend": ["*.py"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
)
