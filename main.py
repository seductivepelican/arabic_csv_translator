import pandas as pd
import argparse
import sys
import os
import logging
from tqdm import tqdm
from typing import List, Optional
from translator import ArabicTranslator
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("translation_session.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def get_checkpoint_path(output_path: str) -> str:
    """Generates the checkpoint file path for a given output path."""
    return output_path + config.CHECKPOINT_SUFFIX

def process_csv(input_path: str, output_path: str, resume: bool = True) -> None:
    """
    Orchestrates the batch translation of a CSV file with checkpointing support.
    
    Args:
        input_path (str): Path to the source CSV file.
        output_path (str): Path to save the translated CSV.
        resume (bool): Whether to attempt resuming from an existing checkpoint.
    """
    checkpoint_path = get_checkpoint_path(output_path)
    
    # 1. Load Data
    logger.info(f"Loading input file: {input_path}")
    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        logger.error(f"Critical Error: Could not read input CSV: {e}")
        return

    if config.TEXT_COLUMN not in df.columns:
        logger.error(f"Critical Error: Required column '{config.TEXT_COLUMN}' missing from CSV.")
        return

    # 2. Check for Resume/Checkpoint
    start_index = 0
    if resume and os.path.exists(checkpoint_path):
        logger.info(f"Checkpoint detected at {checkpoint_path}. Attempting to resume...")
        try:
            df_checkpoint = pd.read_csv(checkpoint_path)
            if config.STATUS_COLUMN in df_checkpoint.columns:
                start_index = df_checkpoint[config.STATUS_COLUMN].notna().sum()
                logger.info(f"Resuming from row {start_index} of {len(df)}.")
                df = df_checkpoint
            else:
                logger.warning("Checkpoint file is malformed. Starting from row 0.")
        except Exception as e:
            logger.error(f"Error reading checkpoint: {e}. Starting from row 0.")

    # 3. Initialize Translator
    try:
        translator = ArabicTranslator()
    except Exception as e:
        logger.error(f"Fatal: Translator initialization failed: {e}")
        sys.exit(1)

    # 4. Processing Loop
    logger.info(f"Processing {len(df) - start_index} records using batch size {config.INFERENCE_BATCH_SIZE}")
    
    # Ensure columns exist and have appropriate dtype
    for col in [config.TRANSLATED_COLUMN, config.STATUS_COLUMN, config.ERROR_COLUMN]:
        if col not in df.columns:
            df[col] = None
        df[col] = df[col].astype(object)

    try:
        # Process using tqdm progress bar
        with tqdm(total=len(df), initial=start_index, desc="Translating", unit="row") as pbar:
            for i in range(start_index, len(df), config.INFERENCE_BATCH_SIZE):
                end_idx = min(i + config.INFERENCE_BATCH_SIZE, len(df))
                batch_texts = df.loc[i:end_idx-1, config.TEXT_COLUMN].tolist()
                
                # Perform batch inference
                batch_results = translator.translate_batch(batch_texts)
                
                # Update DataFrame with results
                for j, (result, status, error_msg) in enumerate(batch_results):
                    current_idx = i + j
                    df.at[current_idx, config.TRANSLATED_COLUMN] = result
                    df.at[current_idx, config.STATUS_COLUMN] = status
                    df.at[current_idx, config.ERROR_COLUMN] = error_msg

                # Update progress bar
                pbar.update(len(batch_texts))

                # 5. Incremental Checkpoint saving
                if (i // config.CHECKPOINT_BATCH_SIZE) < (end_idx // config.CHECKPOINT_BATCH_SIZE):
                    df.to_csv(checkpoint_path, index=False)

    except KeyboardInterrupt:
        logger.info("\nSession interrupted by user. Persisting current progress to checkpoint...")
        df.to_csv(checkpoint_path, index=False)
        logger.info(f"Checkpoint saved. Re-run command to resume from row {df[config.STATUS_COLUMN].notna().sum()}.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected runtime error during processing loop: {e}")
        df.to_csv(checkpoint_path, index=False)
        logger.info("Emergency checkpoint saved.")
        raise

    # 6. Final Save & Cleanup
    logger.info(f"Batch processing complete. Saving final results to {output_path}")
    df.to_csv(output_path, index=False)
    
    if os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)
    logger.info("Cleaned up checkpoint files. Task finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Professional Offline Arabic to English Translation Framework")
    parser.add_argument("--input", required=True, help="Input CSV file path")
    parser.add_argument("--output", required=True, help="Output CSV file path")
    parser.add_argument("--no-resume", action="store_false", dest="resume", help="Disable auto-resume from checkpoint")
    
    args = parser.parse_args()
    
    if not os.path.exists(config.MODEL_PATH):
        logger.error(f"Model assets not found at {config.MODEL_PATH}.")
        logger.info("Run './venv/bin/python scripts/download_model.py' to download required model files.")
        sys.exit(1)

    process_csv(args.input, args.output, resume=args.resume)
