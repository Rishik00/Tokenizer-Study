import time
import mmap
import logging
from typing import List, Any, Dict

# Local imports
from ur_utils import UrduTokenizer
from zh_utils import ChineseTokenizer
from hi_utils import HindiTokenizer
from logger_config import setup_logging
from db import LevelDB

# Set up logger configuration

tok_logger = setup_logging('logs/hi/indic_spacy.log')
TNAME: str = 'spacy' # Select which tokenizer to be used
LANG_ID = 'hi' # select the target language   

if LANG_ID == 'ur': tok: UrduTokenizer = UrduTokenizer(tokenizer=TNAME)
elif LANG_ID == 'zh': tok: ChineseTokenizer = ChineseTokenizer(tokenizer=TNAME)
elif LANG_ID == 'hi': tok: HindiTokenizer = HindiTokenizer(tokenizer=TNAME)
else: tok_logger.error('Choose your langauge from hindi(hi), urdu(ur) and simplified chinese(zh)')

def main_fn(ifile_name:str, db: LevelDB, ofile_name: str):
    
    batch_size: int = 100000         # Batches of batch_size words will be added to db
    segment_limit: int = 100000      # Seegment limit, set it appropriately for logging 
    num_segments, temp = 0, 0        # number of segments, and temp is only a display variable

    tok_logger.info(f'{ifile_name} is being processed by using {TNAME}')

    try:
        with open(ifile_name, 'r+b') as file:

            num_total_tokens: int = 0
            m = mmap.mmap(file.fileno(), 0, prot=mmap.PROT_READ)
            
            for segment in iter(m.readline, b""):
                segment = segment.strip().decode('utf-8')
                unique_words = []

                num_tokens, num_words, tokens = tok.tokenize(segment, is_unique=True)
                
                temp += num_tokens
                num_segments += 1
                num_total_tokens += num_tokens

                if num_segments % segment_limit == 0:
                    tok_logger.info(f'Processed {num_segments} segments, tokens per {segment_limit} segments: {temp}')
                    temp = 0

                for token in tokens:
                    if db.check(token):
                        unique_words.append((token, token))

                    if len(unique_words) >= batch_size:
                        db.add_batch(unique_words)
                        unique_words = []

                if unique_words:
                    db.add_batch(unique_words)
                    unique_words = []

    except Exception as e:
        tok_logger.error(f'Error in main_fn: {e}')
        raise e
    
    finally:
        db.dump_to_txt(ofile_name, only_tokens=True)
        size, lent = db.find_size()
        tok_logger.info(f'Database size: {size} bytes, Number of tokens: {num_total_tokens}, Number of unique words: {lent} words, number of segments processed: {num_segments}')
        db.close()

# if __name__ == "__main__":

#     # Instantiating DB
#     zh_db_path = '/tmp/zh6db/'
#     zh_db = LevelDB(zh_db_path)

#     # Input and output files
#     # int_file = 'int/ur/int_ur_big.txt'
#     int_file = 'outputs/hi/rand/selected_sentences_50L.txt'
#     output_file = 'outputs/hi/rand/words_spacy_50L_1.txt'

#     # Logic
#     start_time = time.time()

#     try:
#         main_fn(int_file, zh_db, output_file)

#     except Exception as e:
#         tok_logger.error(f"Exception occurred in main: {e}")

#     finally:
#         end_time = time.time()
#         time_elapsed = end_time - start_time
#         tok_logger.info(f"Script execution completed in {time_elapsed:.2f} seconds.")