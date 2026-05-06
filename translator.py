import os
import logging
from typing import List, Tuple, Optional
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer
import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ArabicTranslator:
    """
    A robust, offline-capable translator for Arabic-to-English text processing.
    
    Attributes:
        device (str): The hardware device (cpu or cuda) being used for inference.
        tokenizer (PreTrainedTokenizer): The NLLB tokenizer.
        model (PreTrainedModel): The NLLB Seq2Seq model.
    """
    
    def __init__(self, model_path: str = config.MODEL_PATH):
        """
        Initializes the translator and loads the model from the local file system.
        
        Args:
            model_path (str): The local directory path containing the model and tokenizer files.
        """
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing ArabicTranslator on {self.device}")
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
            self.tokenizer.src_lang = config.SRC_LANG
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_path, local_files_only=True).to(self.device)
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load model from {model_path}: {e}")
            raise

    def translate_batch(self, texts: List[str]) -> List[Tuple[str, str, str]]:
        """
        Translates a batch of Arabic strings to English in a single forward pass.
        
        Args:
            texts (List[str]): A list of Arabic strings to be translated.
            
        Returns:
            List[Tuple[str, str, str]]: A list of tuples containing (translated_text, status, error_message).
        """
        if not texts:
            return []
            
        valid_texts: List[str] = []
        original_indices: List[int] = []
        # Pre-populate with placeholders
        results: List[Optional[Tuple[str, str, str]]] = [None] * len(texts)
        
        for i, text in enumerate(texts):
            if not isinstance(text, str) or not text.strip():
                results[i] = (config.ERR_BAD_INPUT, "ERROR", "Missing or invalid input text")
            else:
                valid_texts.append(text)
                original_indices.append(i)
        
        if not valid_texts:
            return results  # type: ignore

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
                
            return results  # type: ignore
            
        except torch.cuda.OutOfMemoryError:
            logger.error("GPU Out of Memory encountered during batch inference.")
            error_res = (config.ERR_SYSTEM, "ERROR", "GPU Out of Memory")
            return [error_res if r is None else r for r in results] # type: ignore
        except Exception as e:
            logger.error(f"Unexpected error during batch translation: {e}")
            error_res = (config.ERR_TRANS_FAILED, "ERROR", str(e))
            return [error_res if r is None else r for r in results] # type: ignore

    def translate(self, text: str) -> Tuple[str, str, str]:
        """
        Single string translation wrapper for translate_batch.
        
        Args:
            text (str): The Arabic text to translate.
            
        Returns:
            Tuple[str, str, str]: (translated_text, status, error_message).
        """
        results = self.translate_batch([text])
        return results[0]
