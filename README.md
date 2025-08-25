# Form Analysis Tool

A configurable tool for analyzing Likert scale form responses with team and location categorizations.

## Project Structure

```
csv_form_analysis/
├── config.yaml                  # ⚙️  Configuration file
├── requirements.txt              # 📦 Dependencies
├── README.md                     # 📖 Documentation
├── User Categorization Form.xlsx # 📊 Sample data file
├── src/                         # 📁 Source code modules
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # 🎯 Main entry point
│   ├── config_manager.py        # Configuration handling
│   ├── data_processor.py        # Data loading & processing
│   ├── analyzer.py              # Statistical analysis
│   ├── output_generator.py      # File output generation
│   └── user_interface.py        # User interaction
└── output/                      # 📂 Generated reports
    └── [timestamped_run_folders]/
        ├── summary.json         # Analysis summary
        ├── report.txt           # Detailed report
        └── dashboard.xlsx       # Excel dashboard with charts
```

## Core Modules

### Source Code (`src/`)

- **`config_manager.py`** - YAML configuration handling, validation, and defaults
- **`data_processor.py`** - Data loading, Likert scale conversion, and data validation  
- **`analyzer.py`** - Statistical analysis, comparisons, and recommendation generation
- **`output_generator.py`** - Multi-format file output with timestamped run directories
- **`user_interface.py`** - Interactive user input and console display
- **`main.py`** - Main orchestrator script

### Configuration & Data

- **`config.yaml`** - Central configuration file for all settings
- **`requirements.txt`** - Python dependencies
- **`output/`** - Directory for all generated analysis results


## Usage

### Quick Start
```bash
# Activate virtual environment
source .venv/bin/activate

# Run the analysis tool
python src/main.py
```

### Configuration

Edit `config.yaml` to customize:

```yaml
# Data source
data_source:
  file_path: "your_data.xlsx"
  sheet_name: ""  # Optional

# Column mapping
columns:
  team_column: "Team Column Name"
  location_column: "Location Column Name"

# Question categories
categories:
  "Category Name":
    - "Question 1"
    - "Question 2"

# Output settings
output:
  include_timestamp: true
```

## Features

### 🔧 Configurable
- **Column Mapping**: Easily adapt to different data structures
- **Question Categories**: Define custom groupings via YAML
- **Output Control**: Choose formats and destination

### 📊 Interactive Analysis
- **Team/Location Selection**: Choose specific combinations or "All"
- **Detailed Statistics**: Category performance and individual responses
- **Comparison Analysis**: Compare selections against overall averages

### 📄 Organized Output Structure
- **Timestamped Run Directories**: Each analysis creates a unique folder (e.g., `20250825_143022_Engineering_London/`)
- **JSON**: Structured analysis results and metadata (`summary.json`)
- **TXT**: Human-readable comprehensive reports (`report.txt`)
- **Excel**: Interactive dashboard with charts and breakdowns (`dashboard.xlsx`)


## Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Your Data**:
   Edit `config.yaml` to match your data structure

3. **Run Analysis**:
   ```bash
   python src/main.py
   ```

The tool will guide you through team and location selection for detailed analysis.