# 🏌️ Golf Swing Analyzer

An AI-powered computer vision system that analyzes golf swing mechanics to prevent injuries and improve performance. This system provides real-time feedback on swing sequencing, identifying the most common fault(s) that can lead to joint damage, chronic pain, and diminished athletic ability.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## 👥 Development Team

**Project Lead:** Tim Yarosh - Single Digit Handicap Golfer & Domain Expert

**Core Contributors:**

- Tim Yarosh
- Roy Kim
- Victor Ho

_This is a collaborative student project for CIS5810 - Computer Vision and Computational Photography at The University of Pennsylvania_

## 🎯 Project Overview

This project was developed as part of academic coursework in computer vision, with the goal of creating a practical tool that helps golfers maintain proper form and technique. The system focuses on detecting the most common swing fault in golf:

- **Over-the-Top**: Outside-in swing path that causes slices

## ✨ Features

- 🎥 **Video-Based Analysis**: Upload swing videos for comprehensive analysis
- 🤖 **AI Pose Estimation**: Uses MediaPipe for accurate body tracking
- 📊 **Multi-Fault Detection**: Identifies three common swing faults simultaneously
- 📈 **Visual Feedback**: Annotated videos with skeleton overlay and measurements
- 📋 **Detailed Reports**: Comprehensive analysis with scores and recommendations
- 🖥️ **User-Friendly Interface**: Web-based UI built with Streamlit (_Coming Soon_)
- 🔄 **Batch Processing**: Analyze multiple swings for progress tracking (_Coming Soon_)

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher.
- Webcam or video files of golf swings
- Recommended: 60fps video for best results

### Getting Started (Mac specific)

1. **Fork and clone the repository**

   - Fork this repository by clicking the "Fork" button at the top right of this page
   - Clone your forked repository:

```bash
   git clone https://github.com/YOUR-USERNAME/golf-swing-analyzer.git
   cd golf-swing-analyzer
```

2. **Create a virtual environment**

```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
```

4. **Install the package**

```bash
   pip install -e .
```

### Running the Application

**Command Line Interface**

```bash
golf-analyzer --video path/to/swing.mp4 --output results/
```

## 📁 Project Structure

```
golf-swing-analyzer/
├── app
│   └── __init__.py
├── COLLABORATION.md
├── data                   # Data directory for storing videos and outputs
│   ├── outputs
│   ├── reference_swings
│   └── test_swings
├── docs                   # Documentation files
│   ├── meeting-notes
│   ├── presentations
│   └── progress-reports
├── LICENSE
├── notebooks
├── README.md
├── requirements.txt       # Project dependencies
├── setup.py               # Package setup file
├── src
│   ├── __init__.py
│   ├── __pycache__
│   ├── analysis           # Fault detection algorithms
│   ├── config             # Configuration files and thresholds
│   ├── core               # Core processing (video, pose estimation, segmentation)
│   ├── models             # ML models (if any)
│   ├── utils              # Utility functions
│   └── visualization      # Video annotation and report generation
└── tests                  # Test suite
    ├── __init__.py
    └── initialAppTest.py
```

## 🎥 Video Recording Best Practices

For optimal analysis results:

**Camera Setup:**

- Use **face-on view** (perpendicular to target line) for detecting early extension and weight shift
- Alternatively, use **down-the-line view** (behind golfer) for swing plane analysis
- Position camera 10-15 feet away to capture full body
- Use tripod for stable footage

**Video Settings:**

- Minimum 30fps, recommended 60fps or higher
- 1080p resolution or higher
- Ensure entire body is in frame from address through finish
- Good lighting (outdoor practice ideal)
- Avoid shadows or backlighting

## 🔬 Technical Details

### Computer Vision Pipeline

1. **Pose Estimation**: MediaPipe Pose extracts 33 body landmarks per frame
2. **Swing Segmentation**: Identifies key phases (address, top, impact, finish)
3. **Fault Analysis**: Three parallel analyzers process swing mechanics
4. **Scoring**: Rule-based algorithms generate 0-10 scores for each fault
5. **Visualization**: Annotated videos with skeleton overlay and measurements

### Fault Detection Algorithms

**Over-the-Top Analyzer**

- Analyzes shoulder plane angle at top of backswing
- Tracks hand path during transition and downswing
- Compares to proper "slot" position

## 📊 Performance Metrics

Current system performance (based on testing):

- swing_path_degrees: Actual measurement in degrees
- swing_path_description: Standard golf terminology
- vs_tour_average: Comparison to tour professionals
- severity_level: Clear assessment category

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
python tests/initialAppTest.py
```

## 🛠️ Development

**Code Formatting**

```bash
black src/ app/ tests/
```

**Linting**

```bash
flake8 src/ app/ tests/
```

**Type Checking**

```bash
mypy src/
```

**Communication Channels:**

- 💬 **Slack**: Daily updates and quick questions
- 🎥 **Weekly Meetings**: Video call for coordination

### Pre-commit Hooks (Recommended)

Install pre-commit hooks to ensure code quality:

```bash
pip install pre-commit
pre-commit install
```

This will automatically run linters and formatters before each commit.

## 📈 Future Enhancements

Planned features for post-course development:

- Web GUI or mobile based application
- Percentile Rankings
- Drill Library
- Visual Overlays
- Club-Specific Analysis
- Comparison Mode
- Export Reports
- Interactive Mode
- Robust Cloud Storage
- Launch monitor software integration

## 🤝 Contributing

### For Team Members (Direct Access)

We use a **branch-based workflow** for team collaboration:

1. **Create a feature branch** from `develop`

   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit frequently

   ```bash
   git add .
   git commit -m "feat: descriptive message following conventional commits"
   ```

3. **Keep your branch updated**

   ```bash
   git fetch origin
   git rebase origin/develop
   ```

4. **Push and create Pull Request**

   ```bash
   git push origin feature/your-feature-name
   # Open PR on GitHub: feature/your-feature-name → develop
   ```

5. **Code Review**
   - At least one team member must review
   - Address feedback and update PR
   - Once approved, squash and merge

**Branch Naming Convention:**

- `feature/` - New features (e.g., `feature/reverse-pivot-analyzer`)
- `fix/` - Bug fixes (e.g., `fix/pose-detection-crash`)
- `docs/` - Documentation updates
- `test/` - Test additions/improvements
- `refactor/` - Code refactoring

**Commit Message Format:**

```
type(scope): subject

body (optional)

footer (optional)
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example: `feat(analyzer): implement early extension detection algorithm`

### For External Contributors (Post-Course)

After course completion, external contributions are welcome:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes following our conventions
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request to our `develop` branch

### Development Guidelines

- **Write tests** for new features
- **Update documentation** as you code
- **Run linters** before committing: `black . && flake8`
- **Keep PRs focused** - one feature/fix per PR
- **Communicate early** - open draft PRs to discuss approach

## 🐛 Known Issues

- Pose detection may fail in low-light conditions
- Baggy clothing can affect landmark accuracy
- Side-view (45-degree) angles not currently supported
- Real-time analysis not yet implemented

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Course Instructors**: Professor Shi for guidance and feedback
- **Teaching Assistants**: for technical support

## 📧 Contact

**Team Lead**: Tim Yarosh - yarosh11@seas.upenn.edu

**Issues & Support**: Use GitHub Issues for bug reports and feature requests

## 📝 Citation

If you use this project in your research, teaching, or other projects, please cite:

```bibtex
@software{golf_swing_analyzer,
  author = {[Team Member Names]},
  title = {Golf Swing Analyzer: AI-Powered Swing Analysis System},
  year = {2025},
  organization = {[University Name]},
  course = {[Course Number and Name]},
  url = {https://github.com/your-organization/golf-swing-analyzer}
}
```

## 📚 Academic Context

**Course**: CIS5810 - Computer Vision and Computational Photography \
**Institution**: University of Pennsylvania \
**Semester**: Fall/2025 \
**Instructors**: Professor Shi

**Project Objectives:**

- Apply computer vision techniques to real-world problems
- Develop end-to-end working prototype
- Develop Critical analysis of existing CV algorithms and APIs
- Design Comprehensive documentation and presentation
- Collaborative software development experience

---
