# Testing Commands for GitHub Changes

## Quick Start

### 1. Navigate to Test Worktree
```powershell
cd ../kpi_pipeline_test
```

### 2. Activate Virtual Environment
```powershell
.venv\Scripts\Activate.ps1
```

### 3. Run Basic Pipeline Test (Default CSV Format)
```powershell
python main.py --env dev --save-tables
```

**Expected Result:**
- Pipeline runs successfully
- Output message shows: "Saving output tables (csv format)..."
- 7 CSV files created in `data/output/tables/` with `.csv` extension

### 4. Verify CSV Files Are Readable
```powershell
python -c "import pandas as pd; from pathlib import Path; csv_files = list(Path('data/output/tables').glob('*.csv')); print(f'Found {len(csv_files)} CSV files'); [print(f'  {f.name}: {len(pd.read_csv(f))} rows') for f in sorted(csv_files)[-7:]]"
```

### 5. Test Parquet Override (Verify Backward Compatibility)
```powershell
python main.py --env dev --save-tables --tables-format parquet
```

**Expected Result:**
- Pipeline runs successfully
- Output message shows: "Saving output tables (parquet format)..."
- 7 Parquet files created with `.parquet` extension

### 6. Run Existing Tests
```powershell
# Run geographic analysis tests
python tests/test_geographic_analysis.py

# Run CSV export test
python -m pytest tests/test_analysis_output.py::test_save_output_tables_csv -v
```

### 7. Verify Default Format is CSV
```powershell
# Check the default in main.py
Select-String -Path main.py -Pattern "default.*csv" -Context 0,2
```

**Expected:** Should show `default='csv'` in the argument parser

### 8. Compare CSV vs Parquet Outputs
```powershell
python -c "import pandas as pd; df_csv = pd.read_csv('data/output/tables/geographic_summary_20251201_112946.csv'); df_parquet = pd.read_parquet('data/output/tables/geographic_summary_20251201_113013.parquet'); print(f'CSV: {len(df_csv)} rows, {len(df_csv.columns)} cols'); print(f'Parquet: {len(df_parquet)} rows, {len(df_parquet.columns)} cols'); print(f'Columns match: {list(df_csv.columns) == list(df_parquet.columns)}')"
```

## Full Test Checklist

- [ ] Default format is CSV (no --tables-format flag)
- [ ] CSV files are created and readable
- [ ] Parquet override works (--tables-format parquet)
- [ ] All 7 output tables generated correctly
- [ ] Geographic analysis tests pass
- [ ] CSV export test passes
- [ ] Excel reports still generate correctly

## Cleanup

When done testing, remove the worktree:
```powershell
cd ../kpi_pipeline
git worktree remove ../kpi_pipeline_test
```

