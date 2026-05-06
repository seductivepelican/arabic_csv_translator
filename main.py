import pandas as pd
import argparse
import sys
import os
import time
from translator import ArabicTranslator
import config

def get_checkpoint_path(output_path):
    return output_path + config.CHECKPOINT_SUFFIX

def process_csv(input_path, output_path, resume=True):
    checkpoint_path = get_checkpoint_path(output_path)
    
    # 1. Load Data
    print(f"Reading input file: {input_path}")
    try:
        # For 1M+ rows, reading entire CSV might be heavy but usually fits in RAM on a good laptop.
        # If RAM is an issue, we could switch to chunk-based reading.
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    if config.TEXT_COLUMN not in df.columns:
        print(f"Error: Column '{config.TEXT_COLUMN}' not found in CSV.")
        return

    # 2. Check for Resume/Checkpoint
    start_index = 0
    if resume and os.path.exists(checkpoint_path):
        print(f"Checkpoint found at {checkpoint_path}. Resuming...")
        df_checkpoint = pd.read_csv(checkpoint_path)
        
        # Identify where we left off based on the presence of the translated column
        # and checking for non-null values in the status column.
        if config.STATUS_COLUMN in df_checkpoint.columns:
            start_index = df_checkpoint[config.STATUS_COLUMN].notna().sum()
            print(f"Skipping already processed {start_index} rows.")
            df = df_checkpoint # Use the checkpointed data as the base
        else:
            print("Checkpoint invalid (no status column). Starting from beginning.")

    # 3. Initialize Translator
    try:
        translator = ArabicTranslator()
    except Exception as e:
        print(f"Fatal: Could not initialize translator. {e}")
        sys.exit(1)

    # 4. Processing Loop
    print(f"Processing {len(df) - start_index} remaining rows (Total: {len(df)})...")
    print(f"Using inference batch size: {config.INFERENCE_BATCH_SIZE}")
    
    # Ensure columns exist in df and have object (string-friendly) dtype
    for col in [config.TRANSLATED_COLUMN, config.STATUS_COLUMN, config.ERROR_COLUMN]:
        if col not in df.columns:
            df[col] = None
        df[col] = df[col].astype(object)

    try:
        # Process in batches
        for i in range(start_index, len(df), config.INFERENCE_BATCH_SIZE):
            end_idx = min(i + config.INFERENCE_BATCH_SIZE, len(df))
            batch_texts = df.loc[i:end_idx-1, config.TEXT_COLUMN].tolist()
            
            # Simple progress logging
            if i % 100 == 0:
                print(f"Row {i}/{len(df)} ({(i/len(df)*100):.2f}%)")

            # Translate batch
            batch_results = translator.translate_batch(batch_texts)
            
            # Update DataFrame
            for j, (result, status, error_msg) in enumerate(batch_results):
                current_idx = i + j
                df.at[current_idx, config.TRANSLATED_COLUMN] = result
                df.at[current_idx, config.STATUS_COLUMN] = status
                df.at[current_idx, config.ERROR_COLUMN] = error_msg

            # 5. Checkpoint saving
            # We save every CHECKPOINT_BATCH_SIZE rows
            if (i // config.CHECKPOINT_BATCH_SIZE) < (end_idx // config.CHECKPOINT_BATCH_SIZE):
                df.to_csv(checkpoint_path, index=False)

    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Saving checkpoint...")
        df.to_csv(checkpoint_path, index=False)
        print(f"Progress saved to {checkpoint_path}. Run again to resume.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error during processing: {e}")
        df.to_csv(checkpoint_path, index=False)
        print(f"Progress saved to {checkpoint_path}.")
        raise

    # 6. Final Save
    print(f"Translation complete. Saving final results to {output_path}")
    df.to_csv(output_path, index=False)
    
    # Cleanup checkpoint
    if os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)
    print("Done!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Offline Arabic to English Translator (Batch Mode)")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    parser.add_argument("--no-resume", action="store_false", dest="resume", help="Do not resume from checkpoint")
    
    args = parser.parse_args()
    
    if not os.path.exists(config.MODEL_PATH):
        print(f"Error: Model not found at {config.MODEL_PATH}.")
        print("Please run 'python scripts/download_model.py' first while online.")
        sys.exit(1)

    process_csv(args.input, args.output, resume=args.resume)
