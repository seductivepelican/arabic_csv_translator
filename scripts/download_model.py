import os
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

MODEL_NAME = "facebook/nllb-200-distilled-600M"
SAVE_DIRECTORY = "./models/nllb-200-600M"

def download_model():
    print(f"Starting download of {MODEL_NAME}...")
    
    if not os.path.exists(SAVE_DIRECTORY):
        os.makedirs(SAVE_DIRECTORY)
        
    # Download and save tokenizer
    print("Downloading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.save_pretrained(SAVE_DIRECTORY)
    
    # Download and save model
    print("Downloading model (this may take a while)...")
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
    model.save_pretrained(SAVE_DIRECTORY)
    
    print(f"\nSuccess! Model and tokenizer saved to {SAVE_DIRECTORY}")
    print("You can now run the translator in offline mode.")

if __name__ == "__main__":
    download_model()
