import pandas as pd
import os
import subprocess
import sys
import config

def test_integration_full_run():
    """Test the main script with a CSV containing random IDs and failure modes."""
    input_csv = "tests/test_data_random_ids.csv"
    output_csv = "tests/test_output.csv"
    
    if os.path.exists(output_csv):
        os.remove(output_csv)
    if os.path.exists(output_csv + config.CHECKPOINT_SUFFIX):
        os.remove(output_csv + config.CHECKPOINT_SUFFIX)

    # Run main.py
    # We use subprocess to test the actual CLI interface
    result = subprocess.run([
        sys.executable, "main.py", 
        "--input", input_csv, 
        "--output", output_csv
    ], capture_output=True, text=True)
    
    assert result.returncode == 0
    assert os.path.exists(output_csv)
    
    df = pd.read_csv(output_csv)
    
    # Check if IDs are preserved
    assert 999 in df[config.ID_COLUMN].values
    assert 42 in df[config.ID_COLUMN].values
    
    # Check failure modes in CSV
    row_42 = df[df[config.ID_COLUMN] == 42].iloc[0]
    assert row_42[config.STATUS_COLUMN] == "ERROR"
    assert row_42[config.TRANSLATED_COLUMN] == config.ERR_BAD_INPUT
    
    row_999 = df[df[config.ID_COLUMN] == 999].iloc[0]
    assert row_999[config.STATUS_COLUMN] == "SUCCESS"
    assert len(str(row_999[config.TRANSLATED_COLUMN])) > 0

def test_checkpoint_resume():
    """Test that the system can resume from a checkpoint."""
    input_csv = "tests/test_data_random_ids.csv"
    output_csv = "tests/test_resume_output.csv"
    checkpoint_csv = output_csv + config.CHECKPOINT_SUFFIX
    
    if os.path.exists(output_csv):
        os.remove(output_csv)
    
    # Create a fake checkpoint where the first row is already done
    df_input = pd.read_csv(input_csv)
    df_checkpoint = df_input.copy()
    for col in [config.TRANSLATED_COLUMN, config.STATUS_COLUMN, config.ERROR_COLUMN]:
        df_checkpoint[col] = None
        
    df_checkpoint.at[0, config.TRANSLATED_COLUMN] = "Already Done"
    df_checkpoint.at[0, config.STATUS_COLUMN] = "SUCCESS"
    df_checkpoint.to_csv(checkpoint_csv, index=False)
    
    # Run main.py
    result = subprocess.run([
        sys.executable, "main.py", 
        "--input", input_csv, 
        "--output", output_csv
    ], capture_output=True, text=True)
    
    assert result.returncode == 0, f"Process failed with stderr: {result.stderr}"
    
    # Verify the first row was skipped (kept our 'Already Done' text)
    assert os.path.exists(output_csv), f"Output file {output_csv} was not created. Stderr: {result.stderr}"
    df_final = pd.read_csv(output_csv)
    assert df_final.at[0, config.TRANSLATED_COLUMN] == "Already Done"
    assert df_final.at[1, config.STATUS_COLUMN] == "ERROR" # Row 42 was empty
