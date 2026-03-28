# GitRepoStats - Technical Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Module Reference](#module-reference)
3. [Data Models](#data-models)
4. [Core Algorithms](#core-algorithms)
5. [Configuration System](#configuration-system)
6. [Important Notes & Design Patterns](#important-notes--design-patterns)

---

## Architecture Overview

### High-Level Workflow

```
User Input (GUI)
    ↓
RepoManagement (Orchestrator)
    ├→ Git Repository Analysis (GitPython)
    ├→ Code Complexity Analysis (Lizard)
    ├→ Duplication Detection (SimHash)
    ├→ Ownership Calculation (Author Attribution)
    └→ Trend Analysis (Time-Series Aggregation)
    ↓
Plot (Visualization)
    ↓
Dashboard (HTML Generation)
    ↓
repo_stats.html (Output)
```

### Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **GUI** | CustomTkinter | 5.2.2 | Modern cross-platform desktop UI |
| **Git Integration** | GitPython | 3.1.45 | Repository interaction & analysis |
| **Complexity Analysis** | Lizard | 1.18.0 | Static code metrics (CCN, NLOC) |
| **Duplication Detection** | SimHash | - | Similarity hashing for code blocks |
| **Visualization** | Plotly | 6.3.0 | Interactive HTML charts |
| **Data Processing** | Pandas | 2.3.3 | Data manipulation & aggregation |
| **Numerical Ops** | NumPy | ≥1.24.0 | Mathematical calculations |
| **Code Quality** | Ruff | - | Python linting & formatting |
| **Pre-commit Hooks** | pre-commit | - | Git hook automation |

---

## Module Reference

### 1. **gitrepostats.py** (Entry Point)
- **Purpose**: Application launcher
- **Key Functions**:
  - Instantiates the GUI (CustomTkinter window)
  - Manages application lifecycle
- **Dependencies**: `gui.py`, `tkinter`

```python
if __name__ == "__main__":
    app = CustomTkinterApp()
    app.mainloop()
```

---

### 2. **gui.py** (User Interface)
- **Purpose**: Modern CustomTkinter-based GUI
- **Key Components**:
  - **Workspace Path Input**: Text field for repository path
  - **Date Range Selectors**: Start/End date pickers for filtering
  - **Analysis Checkboxes**: Toggle modules (Author Stats, Complexity, Duplication, etc.)
  - **Log Display**: Real-time analysis logging with color coding
  - **Get Stats Button**: Triggers analysis in background thread
  
- **Threading**: Long-running analyses executed in daemon threads to prevent UI freezing
- **Key Methods**:
  - `on_get_stats_clicked()`: Event handler for analysis button
  - `update_log_display()`: Receives log messages from analysis thread
  - `open_report()`: Auto-opens generated HTML report

- **Important Notes**:
  - GUI remains responsive during analysis via thread delegation
  - Preferences persist via `.preferences` configuration
  - Window size and position saved to config

---

### 3. **repo_management.py** (Core Orchestrator)
- **Purpose**: Coordinates all analysis modules
- **Key Responsibilities**:
  - Git repository navigation and extraction
  - Delegates to specialized analysis modules
  - Aggregates results into unified report structure
  - Handles error recovery and logging

- **Key Methods**:
  - `analyze_repository()`: Main orchestration entry point
  - `extract_commit_history()`: Uses GitPython to get commits
  - `analyze_code_complexity()`: Calls Lizard analyzer
  - `detect_code_duplication()`: Runs SimHash comparison
  - `calculate_code_ownership()`: Determines bus factor
  - `analyze_complexity_trends()`: Time-series aggregation

- **Workflow**:
  1. Validate repository path and access
  2. Load preferences from `config/preferences.yaml`
  3. Parse commit history with date filtering
  4. Execute enabled analyses in parallel where possible
  5. Aggregate results
  6. Generate visualizations via `plot.py`
  7. Create HTML dashboard via `dashboard.py`

---

### 4. **dashboard.py** (HTML Report Generator)
- **Purpose**: Generates interactive HTML dashboard
- **Output Structure**:
  - Fixed navbar with GitHub links and donate button
  - Tab-based navigation system
  - Embedded CSS and JavaScript (self-contained)
  - DataTables.js integration for sortable/filterable tables
  - Plotly.js for interactive charts

- **Report Tabs**:
  1. **Authors Tab**: Per-developer metrics (commits, insertions, deletions, files modified)
  2. **Files Tab**: File-level statistics with ownership breakdown
  3. **Code Analysis Tab**: Complexity ratings, duplication pairs, trends
  4. **Metrics Summary**: Key performance indicators and high-level overview

- **Key Features**:
  - Responsive design for multiple screen sizes
  - Export buttons for CSV data
  - Sortable columns with search/filter
  - Hover tooltips on charts
  - Mobile-friendly tables

- **Important Notes**:
  - Single HTML file (no external dependencies required)
  - Auto-opens in default browser after generation
  - File location: `repo_stats.html` in project root

---

### 5. **plot.py** (Visualization Layer)
- **Purpose**: Creates Plotly visualizations
- **Chart Types**:
  - **Stacked Bar Charts**: Contributions by author, files by extension
  - **Line Graphs**: Trends over time (complexity, commits)
  - **Pie Charts**: Distribution metrics (ownership percentages)
  - **Scatter Plots**: Complexity vs. file size
  - **Dual-Axis Charts**: CCN + NLOC trends

- **Key Functions**:
  - `create_author_stats_chart()`: Stacked contributions
  - `create_complexity_status_chart()`: Health status breakdown
  - `create_duplication_table()`: Similarity score display
  - `create_trend_chart()`: Polynomial-fit trend lines (degree=1)

- **Customization**:
  - Colors configurable via theme constants
  - Chart sizes responsive to data volume
  - Hover text formatted for readability
  - X/Y axis labels contextualized

---

### 6. **preference_reader.py** (Configuration Management)
- **Purpose**: Reads and validates `config/preferences.yaml`
- **Key Functions**:
  - `load_preferences()`: Parses YAML file
  - `validate_config()`: Ensures required fields exist
  - `get_preference()`: Type-safe preference retrieval
  - `merge_with_defaults()`: Fills missing values with sensible defaults

- **Configuration Categories**:
  1. **AuthorStats**: Extensions to exclude from author analysis
  2. **CodeComplexity**: Thresholds, excluded functions/extensions
  3. **CodeDuplication**: Similarity threshold, window size, Hamming distance
  4. **CodeOwnership**: Ownership display thresholds
  5. **ComplexityTrend**: Time granularity (day/week/month/quarter)
  6. **UI**: Window sizes, font preferences

- **Runtime Behavior**:
  - Reads YAML at analysis start (not cached)
  - Allows on-the-fly configuration changes without restart
  - Graceful fallback to defaults if YAML is malformed

---

### 7. **logger.py** (Logging System)
- **Purpose**: Unified logging across application
- **Output Destinations**:
  1. **File**: `logs.log` with auto-rotation
  2. **Console**: Color-coded terminal output
  3. **GUI**: Real-time textbox updates

- **Log Levels**:
  - `INFO`: Standard operation messages
  - `DEBUG`: Detailed diagnostic information
  - `WARNING`: Potentially problematic situations
  - `ERROR`: Error conditions requiring attention

- **Features**:
  - Auto-rotation after 10,000 lines (keeps last 3,000)
  - Color coding by severity (GREEN=info, YELLOW=warn, RED=error)
  - Timestamps for all entries
  - Thread-safe logging

- **Key Methods**:
  - `log_info()`, `log_warning()`, `log_error()`, `log_debug()`
  - `set_gui_callback()`: Register GUI textbox for updates

---

## Data Models

### Core Entities (in `/entities/` directory)

#### **Author**
```python
@dataclass
class Author:
    email: str                  # Primary email address
    name: str                   # Developer name
    aliases: List[str]          # Alternative emails/usernames
```

#### **AuthorStats**
```python
@dataclass
class AuthorStats:
    author: Author
    commits: int
    insertions: int
    deletions: int
    files_modified: int
    extensions_stats: Dict[str, int]  # Files per extension
```

#### **FileStats**
```python
@dataclass
class FileStats:
    path: str
    language: str
    changes: int
    authors_count: int
    owner_percentage: Dict[str, float]  # % ownership per author
```

#### **CommitStats**
```python
@dataclass
class CommitStats:
    hash: str
    date: datetime
    author: Author
    message: str
    insertions: int
    deletions: int
```

#### **LizardData** (Complexity Metrics)
```python
@dataclass
class LizardData:
    function_name: str
    file_path: str
    nloc: int                           # Lines of code (non-comment)
    ccn: int                            # Cyclomatic complexity number
    token_count: int
    parameter_count: int
    status: str                         # "HEALTHY" | "NEEDS_ATTENTION" | "AT_RISK"
```

#### **DuplicationData**
```python
@dataclass
class DuplicationData:
    function_1: str
    function_2: str
    file_1: str
    file_2: str
    similarity_score: float             # 0-10 scale
```

#### **BusFactorData** (Code Ownership)
```python
@dataclass
class BusFactorData:
    file_path: str
    ownership: Dict[str, float]         # Author -> % ownership
    total_authors: int
    risk_level: str                     # "LOW" | "MEDIUM" | "HIGH"
```

#### **ComplexityTrendData**
```python
@dataclass
class ComplexityTrendData:
    period: str                         # Date or "Week 1", "Month 1", etc.
    avg_ccn: float
    avg_nloc: float
    total_functions: int
```

#### **ReportConfig** (Analysis Selection)
```python
@dataclass
class ReportConfig:
    include_author_stats: bool
    include_commits: bool
    include_complexity: bool
    include_duplication: bool
    include_ownership: bool
    include_trends: bool
```

---

## Core Algorithms

### 1. Cyclomatic Complexity (CCN) Status Calculation

**Algorithm**: Multi-criteria evaluation

```
Input: LizardData (NLOC, CCN, tokens, params)

Status Determination:
  IF CCN ≤ 5 AND NLOC ≤ 50:
    Status = HEALTHY ✅
  ELSE IF CCN ≤ 15 AND NLOC ≤ 100:
    Status = NEEDS_ATTENTION ⚠️
  ELSE:
    Status = AT_RISK ❌

Output: Status string + risk indicator
```

**Configurable Thresholds** in `preferences.yaml`:
- `HealthyThreshold`: CCN limit for healthy functions
- `WarningThreshold`: CCN limit for warning zone
- `ErrorThreshold`: Beyond this = at risk

---

### 2. Code Duplication Detection (SimHash)

**Algorithm**: Locality-sensitive hashing with structural similarity

```
Input: All functions in repository

Preprocessing:
  1. Extract function tokens (normalized AST)
  2. Generate short fingerprint (64-bit SimHash)
  3. Group similar fingerprints (Hamming distance < threshold)

For Each Pair:
  IF Hamming Distance ≤ MaxHammingDiff (default: 10):
    Calculate Similarity Score = (WindowSize - Distance) / WindowSize * 10
  
  IF Similarity Score ≥ Threshold (default: 5.0):
    Flag as duplication candidate

Output: List of DuplicationData with similarity scores
```

**Configurable Parameters**:
- `Threshold`: Minimum similarity to report (0-10)
- `WindowSize`: Functions to compare
- `MaxHammingDiff`: Maximum bit difference before filtering

---

### 3. Bus Factor / Code Ownership

**Algorithm**: Author attribution and risk calculation

```
Input: All commits and file modifications

For Each File:
  1. Group commits by author
  2. Calculate modification percentage per author
  3. Rank authors by contribution
  
  Risk Calculation:
    IF Top Author > 80%: Risk = HIGH
    ELSE IF Top Author > 60%: Risk = MEDIUM
    ELSE: Risk = LOW

Output: BusFactorData with ownership % and risk level
```

**Key Features**:
- Handles multiple email aliases per author
- Weighted by recency (recent changes count more)
- Includes unidentified authors as "Unknown"

---

### 4. Complexity Trend Analysis

**Algorithm**: Time-series aggregation and polynomial fitting

```
Input: All commits with complexity metrics (from git + lizard)

Time Bucketing:
  Granularity = Preference (day/week/month/quarter)
  For Each Bucket:
    Average CCN = Mean(all_functions_ccn)
    Average NLOC = Mean(all_functions_nloc)
    Total Functions = Count(functions)

Trend Fitting:
  Fit polynomial degree=1 (linear) through data points
  Generate trend line for visualization

Output: List of ComplexityTrendData points + trend line
```

**Visualization**:
- Dual-axis chart: CCN (left) + NLOC (right)
- Trend line overlaid with polynomial fit
- Color coding: Green (improving) / Red (degrading)

---

## Configuration System

### preferences.yaml Structure

```yaml
# Author Statistics Configuration
AuthorStats:
  ExcludeExtensions: 
    - png
    - svg
    - jpg
    - exe
    - dll

# Code Complexity Configuration
CodeComplexity:
  ExcludeExtensions:
    - js
    - json
  ExcludeFunctions:
    - "(anonymous)"
    - ""
  HealthyThreshold: 5        # CCN limit for healthy
  WarningThreshold: 15       # CCN limit for warning
  ErrorThreshold: 25         # Beyond this = at risk

# Code Duplication Configuration
CodeDuplication:
  Threshold: 5.0             # Similarity score threshold (0-10)
  WindowSize: 5              # Functions to compare
  MaxHammingDiff: 10         # Max bit difference
  MaxNlocDiff: 100           # Max NLOC difference allowed

# Code Ownership Configuration
CodeOwnership:
  ExcludeExtensions:
    - png
    - svg
    - jpg
  ShowZeroPercentAuthorsIfLessThan: 5  # Show all if ≤ 5 authors

# Complexity Trend Configuration
ComplexityTrend:
  Enabled: true
  Granularity: month         # day, week, month, quarter

# UI Configuration
UI:
  WindowWidth: 800
  WindowHeight: 600
  DefaultFontSize: 10
```

### Configuration Loading Priority

1. **Load from file**: `config/preferences.yaml`
2. **Validate syntax**: YAML parsing
3. **Merge with defaults**: Fill missing fields
4. **Type coercion**: Convert strings to appropriate types
5. **Apply to analysis**: Use loaded config

---

## Important Notes & Design Patterns

### 1. **GUI Threading Model**
- **Problem**: Long analyses freeze the UI
- **Solution**: Analyses run in daemon threads
- **Implementation**:
  ```python
  analysis_thread = threading.Thread(
      target=repo_management.analyze_repository(),
      daemon=True
  )
  analysis_thread.start()
  ```

### 2. **Real-Time Configuration**
- **Problem**: Configuration changes require restart
- **Solution**: Read YAML at analysis time (not cached)
- **Benefit**: Modify thresholds mid-session without restart

### 3. **Status-Based Quality Indicators**
- **Three-tier system**: ✅ Healthy | ⚠️ Warning | ❌ At Risk
- **Multi-criteria**: CCN + NLOC + tokens + parameters
- **Configurable**: All thresholds in `preferences.yaml`

### 4. **Email Alias Deduplication**
- **Problem**: Same author uses multiple emails
- **Solution**: `AuthorStats` tracks primary + aliases
- **Implementation**: Merge commits with same author across aliases

### 5. **Period-Based Filtering**
- **Start/End dates**: Filter analysis to specific timeframe
- **Use case**: Recent performance assessment, sprint analysis
- **Implementation**: Filter commits before analysis begins

### 6. **Self-Contained HTML Output**
- **Problem**: External dependencies complicate sharing
- **Solution**: Embed all CSS, JS, and data in single HTML file
- **Result**: `repo_stats.html` is fully standalone

### 7. **Extensible Analysis Framework**
- **Design**: Each analysis type is modular
- **Addition**: New analyses can be added by:
  1. Creating new entity in `/entities/`
  2. Adding analysis function to `repo_management.py`
  3. Adding checkbox to `gui.py`
  4. Adding visualization to `plot.py`
  5. Adding report section to `dashboard.py`

### 8. **Color-Coded Logging**
- **Purpose**: Visual debugging and progress tracking
- **Levels**: INFO (green) | WARNING (yellow) | ERROR (red)
- **Destinations**: File + Console + GUI

---

## Performance Considerations

### Optimization Strategies

1. **Parallel Analysis Where Possible**
   - Complexity and duplication detection run independently
   - Results aggregated after both complete

2. **Commit History Caching**
   - First-time analysis extracts all commits (slow)
   - Subsequent analyses can incrementally add new commits

3. **Configurable Granularity**
   - Trend analysis grouping by day vs. month affects memory
   - Larger granularity = faster processing

4. **Extension-Based Filtering**
   - Skip binary files, images, configs early
   - Reduces processing time for large repos

### Performance Tips

- **Large Projects**: Apply date range filters (e.g., last 6 months)
- **Slow Analyses**: Increase granularity (month vs. day)
- **Duplication Detection**: Disable if not needed, it's computationally expensive
- **Exclude Binary**: Configure file extensions to skip

---

## Error Handling

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Repository not found | Invalid path | Verify absolute path and permissions |
| Git not installed | GitPython can't find git | Install Git and add to PATH |
| Analysis hangs | Large repo or network issues | Set date range, increase timeout |
| Preferences not loading | YAML syntax error | Validate YAML at [yamllint.com](https://www.yamllint.com) |
| No output generated | Analysis module disabled | Check report config checkboxes |

---

## Future Enhancement Opportunities

- [ ] Support for remote repositories (GitHub API)
- [ ] Team-based views and comparisons
- [ ] Export to multiple formats (PDF, CSV, JSON)
- [ ] Incremental updates (only analyze new commits)
- [ ] Machine learning for code quality predictions
- [ ] Integration with CI/CD pipelines
- [ ] Real-time dashboard updates
- [ ] Custom metrics and plugins
