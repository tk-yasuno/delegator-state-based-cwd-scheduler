# 🚀 Delegator v5.2.1 QuickStart Guide

Quick startup guide for large-scale scalable condition-based maintenance planning system

## ⚡ Get Started in 30 Seconds

### 1. Prerequisites Check
```powershell
# Check Python version (3.8+ required)
python --version

# Install required packages
pip install pandas numpy streamlit plotly psutil joblib
```

### 2. File Verification
```powershell
# Verify required files exist
ls delegator_v5_2_1.py
ls streamlit_app_v5_2_1.py
ls input_park_playequipment*.csv
ls inspectionList_parkEquipment*.csv
```

### 3. Instant Execution
```powershell
# Launch Streamlit UI (recommended)
streamlit run streamlit_app_v5_2_1.py
```

🎉 **Done!** Access `http://localhost:8501` in your browser

---

## 📊 Dataset Selection Guide

### Scale-based Recommended Usage

| Dataset | Equipment Count | Purpose | Execution Time | Memory Usage |
|---------|----------------|---------|----------------|--------------|
| **Small-scale (5 equipment)** | 5 | 🔰 Initial test & operation check | 1.2s | 1.3MB |
| **Medium-scale (100 equipment)** | 100 | 📚 Feature learning & demo | 0.071s | 0.1MB |
| **Large-scale (457 equipment)** | 457 | 🏢 Practical scale testing | < 5s | < 10MB |
| **Ultra-large-scale (1331 equipment)** | 1331 | 🌟 Production operation & performance verification | 1.946s | 0.9MB |

### Recommended Learning Path
1. **Small-scale** for operation check → 2. **Medium-scale** for feature understanding → 3. **Large-scale** for practical testing → 4. **Ultra-large-scale** for production operation

---

## 🎯 5-Minute Quick Tour

### Step 1: Launch and Setup (1 minute)
```powershell
streamlit run streamlit_app_v5_2_1.py
```
- Select "Medium-scale data (100 equipment)" in sidebar
- Annual budget: 4 million yen (default)
- Annual construction capacity: 20 tasks (default)

### Step 2: Data Review (1 minute)
- Click **"📊 Equipment Status"** tab
- Check degradation state distribution
- Review statistical summary

### Step 3: Optimization Execution (1 minute)
- Click **"🚀 Execute Schedule"** in sidebar
- Run automatic optimization (completes in ~0.1 seconds)
- Check results in **"📅 Schedule Results"** tab

### Step 4: Visualization Review (1 minute)
- Visualize schedule in **"📈 Gantt Chart"** tab
- Check color coding by degradation judgment
- Review performance metrics in **"⚡ Performance"** tab

### Step 5: Result Output (1 minute)
- Export data in **"📋 Detailed Report"** tab
- Download in CSV/JSON format
- Check system information

🎉 **Complete!** Full understanding of basic functions

---

## 🔧 Command Line Usage

### Basic Execution
```python
from delegator_v5_2_1 import OptSeqSchedulerScalable

# Initialize scheduler
scheduler = OptSeqSchedulerScalable(2025, 2040, max_equipment=100)

# Load data
scheduler.load_equipment_data(
    'input_park_playequipment_100.csv',
    'inspectionList_parkEquipment_100.csv'
)

# Execute optimization
result = scheduler.solve_parallel('greedy_priority')

# Display results
print(f"Success rate: {result['statistics']['scheduling_ratio']*100:.1f}%")
print(f"Total cost: ¥{result['statistics']['total_cost']:,.0f}")
print(f"Execution time: {result['performance']['solve_time']:.3f}s")
```

### Large-scale Data Execution
```python
# Support for 1331 equipment
scheduler = OptSeqSchedulerScalable(2025, 2040, max_equipment=1500)

scheduler.load_equipment_data(
    'input_park_playequipment_241.csv',
    'inspectionList_parkEquipment_1331.csv'
)

result = scheduler.solve_parallel()
# Processes 1331 equipment in approximately 2 seconds
```

---

## 🛠️ Customization Settings

### Budget & Capacity Adjustment
```python
# Custom constraint conditions
annual_budget = 10000000      # 10 million yen
annual_capacity = 50          # 50 tasks/year

# Can also be adjusted directly in sidebar
```

### Period Settings
```python
scheduler = OptSeqSchedulerScalable(
    start_year=2025,    # Start year
    end_year=2050,      # End year (25-year plan)
    max_equipment=1500  # Maximum equipment count
)
```

### Strategy Selection
```python
# Optimization strategies
strategies = [
    "greedy_priority",      # Priority-first (recommended)
    "cost_optimal",         # Cost optimization
    "penalty_minimization"  # Penalty minimization
]

result = scheduler.solve_parallel(strategy="greedy_priority")
```

---

## 🔍 Troubleshooting

### Common Issues and Solutions

#### 1. Launch Error
**Error**: `ModuleNotFoundError: No module named 'streamlit'`
```powershell
# Solution
pip install streamlit plotly pandas numpy psutil joblib
```

#### 2. Data File Error
**Error**: `FileNotFoundError: input_park_playequipment.csv`
```powershell
# Check
ls *.csv

# Start with small-scale data
# Select "Small-scale data (5 equipment)" in sidebar
```

#### 3. Memory Error
**Issue**: Memory shortage with large-scale data
```python
# Solution: Adjust max_equipment
scheduler = OptSeqSchedulerScalable(max_equipment=500)  # Set limit
```

#### 4. Long Execution Time
**Issue**: Slow processing
```python
# Solution: Check parallel processing
import multiprocessing
print(f"CPU cores: {multiprocessing.cpu_count()}")

# Check "Enable parallel processing" in sidebar
```

#### 5. No Results Displayed
**Issue**: Empty schedule results
- Budget/capacity constraints may be too strict
- Increase annual budget
- Increase annual construction capacity

---

## 📈 Performance Optimization Tips

### High-speed Execution Tips
1. **Enable parallel processing**: Check in sidebar
2. **Appropriate dataset**: Choose scale based on purpose
3. **Memory monitoring**: Check in Performance tab
4. **Batch processing**: Automatically applied for large-scale data

### Memory Efficiency
```python
# Batch size adjustment (automatically executed internally)
batch_size = max(1, len(equipment) // cpu_cores)
```

### Parallel Processing Settings
```python
# Check CPU core count
import psutil
print(f"Available cores: {psutil.cpu_count()}")

# Automatic parallel degree adjustment (internal processing)
n_jobs = min(cpu_cores, equipment_count)
```

---

## 🎯 Practical Scenario Guide

### Scenario 1: Initial Evaluation & Demo
```
Purpose: System understanding & feature verification
Recommended: Medium-scale data (100 equipment)
Procedure: Launch UI → Check equipment status → Execute → Review results
Time: 5 minutes
```

### Scenario 2: Practical Scale Testing
```
Purpose: Verification assuming actual operation
Recommended: Large-scale data (457 equipment)
Procedure: Adjust constraints → Execute → Check performance → Export results
Time: 10 minutes
```

### Scenario 3: Production Operation & Performance Verification
```
Purpose: Performance verification at maximum scale
Recommended: Ultra-large-scale data (1331 equipment)
Procedure: Detailed settings → Execute → Check all functions → Generate reports
Time: 15 minutes
```

### Scenario 4: Automation & Batch Processing
```python
# Script for periodic execution
import schedule
import time

def run_optimization():
    scheduler = OptSeqSchedulerScalable(max_equipment=1500)
    scheduler.load_equipment_data('latest_data.csv', 'latest_inspection.csv')
    result = scheduler.solve_parallel()
    
    # Save results
    with open(f'result_{datetime.now().strftime("%Y%m%d")}.json', 'w') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

# Weekly execution setting
schedule.every().monday.at("09:00").do(run_optimization)
```

---

## 📚 Learning Resources

### Order for Deeper Understanding
1. **README_v5_2_1_en.md**: Overall overview & technical specifications
2. **QuickStart_v5_2_1_en.md**: This guide (practical methods)
3. **delegator_v5_2_1.py**: Core implementation (source code learning)
4. **streamlit_app_v5_2_1.py**: UI implementation (customization reference)

### Key Concepts
- **Degradation Score**: Age×0.6 + Inspection Result×0.4
- **Priority**: 5 levels based on degradation level
- **Penalty**: Delay Years × Coefficient × Cost × 0.001
- **Constraints**: Annual budget and construction capacity limits

### Algorithm Understanding
```python
# Basic flow
1. Data loading → Degradation score calculation (parallel)
2. Task generation → Priority sorting
3. Constraint satisfaction scheduling → Result output
```

---

## 🚀 Next Steps

### Development After Basic Mastery
1. **Custom data**: Test with proprietary CSV data
2. **Strategy comparison**: Compare 3 optimization strategies
3. **Constraint adjustment**: Check result changes by budget/capacity
4. **Long-term planning**: Execute with 25-year plan

### Applied Development
1. **API implementation**: REST API calls
2. **Database integration**: PostgreSQL/MySQL connection
3. **Real-time updates**: Integration with IoT data
4. **Machine learning**: Introduction of degradation prediction models

### System Integration
1. **Existing system integration**: Integration with ERP/CMS
2. **Mobile support**: App development & responsive design
3. **Cloud deployment**: Scale-out with AWS/Azure
4. **CI/CD**: Automated testing & deployment

---

## 📞 Support & Community

### Help Information
- **GitHub Issues**: Bug reports & feature requests
- **Detailed README**: README_v5_2_1_en.md
- **Source comments**: Understanding implementation details

### Contribution Methods
1. **Bug reports**: Reproduction steps and environment information
2. **Feature requests**: Specific use cases and expected values
3. **Code improvements**: Pull requests welcome
4. **Documentation**: Share usage examples & tips

---

**🎉 Efficient maintenance planning with Delegator v5.2.1!**

*With this QuickStart guide, you can run a large-scale equipment management system in 5 minutes.*

---

*Last Updated: 2025-07-25*  
*Version: v5.2.1*  
*© 2025 CWD Agent*
