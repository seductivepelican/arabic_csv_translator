import os
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import config

class ArabicTranslator:
    def __init__(self, model_path=config.MODEL_PATH):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading model on {self.device} from {model_path}...")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
            self.tokenizer.src_lang = config.SRC_LANG
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path, local_files_only=True).to(self.device)
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise

    def translate_batch(self, texts):
        """Translates a list of strings in one forward pass."""
        if not texts:
            return []
            
        # Pre-process: handle empty/invalid inputs
        valid_texts = []
        original_indices = []
        results = [None] * len(texts)
        
        for i, text in enumerate(texts):
            if not isinstance(text, str) or not text.strip():
                results[i] = (config.ERR_BAD_INPUT, "ERROR", "Missing or invalid input text")
            else:
                valid_texts.append(text)
                original_indices.append(i)
        
        if not valid_texts:
            return results

        try:
            # Tokenize batch
            inputs = self.tokenizer(
                valid_texts, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=config.MAX_LENGTH
            ).to(self.device)
            
            # Generate batch
            translated_tokens = self.model.generate(
                **inputs, 
                forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(config.TGT_LANG),
                max_length=config.MAX_LENGTH
            )
            
            # Decode batch
            decoded_results = self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)
            
            # Re-map results to original order
            for idx, translation in zip(original_indices, decoded_results):
                results[idx] = (translation, "SUCCESS", "")
                
            return results
            
        except torch.cuda.OutOfMemoryError:
            error_res = (config.ERR_SYSTEM, "ERROR", "GPU Out of Memory")
            return [error_res if r is None else r for r in results]
        except Exception as e:
            error_res = (config.ERR_TRANS_FAILED, "ERROR", str(e))
            return [error_res if r is None else r for r in results]

    def translate(self, text):
        if not isinstance(text, str) or not text.strip():
            return config.ERR_BAD_INPUT, "ERROR", "Missing or invalid input text"
        
        try:
            # Tokenize
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=config.MAX_LENGTH).to(self.device)
            
            # Generate
            translated_tokens = self.model.generate(
                **inputs, 
                forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(config.TGT_LANG),
                max_length=config.MAX_LENGTH
            )
            
            # Decode
            result = self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]
            return result, "SUCCESS", ""
            
        except torch.cuda.OutOfMemoryError:
            return config.ERR_SYSTEM, "ERROR", "GPU Out of Memory"
        except Exception as e:
            return config.ERR_TRANS_FAILED, "ERROR", str(e)
