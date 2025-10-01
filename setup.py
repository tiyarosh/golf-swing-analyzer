"""
Golf Swing Analyzer - Setup Configuration
A computer vision system for analyzing golf swing mechanics
Developed by a team of computer vision students
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open('requirements.txt', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#'):
            requirements.append(line)

setup(
    name="golf-swing-analyzer",
    version="0.1.0",
    
    # Multiple authors - update with actual team member names
    author="Tim Yarosh",
    author_email="yarosh11@seas.upenn.edu",  # Create a shared email or list primary contact
    maintainer="Tim Yarosh",  # Update with project lead
    maintainer_email="yarosh11@seas.upenn.edu",  # Update with lead's email
    
    description="AI-powered golf swing analysis system for injury prevention and performance improvement",
    long_description=long_description,
    long_description_content_type="text/markdown",
    
    url="https://github.com/your-organization/golf-swing-analyzer",  # Update with actual repo
    project_urls={
        "Bug Reports": "https://github.com/your-organization/golf-swing-analyzer/issues",
        "Source": "https://github.com/your-organization/golf-swing-analyzer",
        "Documentation": "https://github.com/your-organization/golf-swing-analyzer/wiki",
        "Discussions": "https://github.com/your-organization/golf-swing-analyzer/discussions",
    },
    
    packages=find_packages(where=".", exclude=["tests*", "notebooks*"]),
    
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
        "Topic :: Multimedia :: Video :: Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    
    python_requires=">=3.9",
    install_requires=requirements,
    
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "pre-commit>=3.5.0",  # Added for team consistency
        ],
        "docs": [
            "sphinx>=7.2.6",
            "sphinx-rtd-theme>=2.0.0",
        ],
    },
    
    entry_points={
        "console_scripts": [
            "golf-analyzer=app.cli:main",
        ],
    },
    
    include_package_data=True,
    keywords="golf computer-vision pose-estimation sports-analytics machine-learning collaborative-project",
    zip_safe=False,
)
