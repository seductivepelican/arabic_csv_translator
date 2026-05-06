import time
import subprocess
import sys
import os

def run_benchmark(filename):
    output = "results_" + filename
    print(f"\n>>> Benchmarking {filename}...")
    start_time = time.time()
    
    result = subprocess.run([
        sys.executable, "main.py",
        "--input", filename,
        "--output", output
    ], capture_output=True, text=True)
    
    end_time = time.time()
    duration = end_time - start_time
    
    if result.returncode != 0:
        print(f"Error during benchmark: {result.stderr}")
        return None
    
    # Get row count from file name or by reading it
    import pandas as pd
    rows = len(pd.read_csv(filename))
    
    avg_per_row = duration / rows
    rows_per_hour = 3600 / avg_per_row
    
    print(f"Completed {rows} rows in {duration:.2f} seconds.")
    print(f"Average: {avg_per_row:.4f} seconds/row")
    print(f"Estimated throughput: {rows_per_hour:.0f} rows/hour")
    
    # Cleanup
    if os.path.exists(output): os.remove(output)
    if os.path.exists(output + ".checkpoint"): os.remove(output + ".checkpoint")
    
    return {
        "rows": rows,
        "duration": duration,
        "avg": avg_per_row,
        "per_hour": rows_per_hour
    }

if __name__ == "__main__":
    results = []
    for f in ["benchmark_10.csv", "benchmark_100.csv", "benchmark_1000.csv"]:
        if os.path.exists(f):
            res = run_benchmark(f)
            if res: results.append(res)
    
    print("\n" + "="*40)
    print("FINAL BENCHMARK SUMMARY")
    print("="*40)
    print(f"{'Rows':<10} | {'Time (s)':<10} | {'Rows/hr':<10}")
    print("-" * 40)
    for r in results:
        print(f"{r['rows']:<10} | {r['duration']:<10.2f} | {r['per_hour']:<10.0f}")
    
    if results:
        total_1m_hours = (1_000_000 * results[-1]['avg']) / 3600
        print(f"\nEstimated time for 1,000,000 rows: {total_1m_hours:.1f} hours")
