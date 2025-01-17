import mmap
import time
import logging
from typing import List
from tqdm import tqdm

# Local imports
from ur_utils import UrduTextCleaner
from hi_utils import HindiTextCleaner
from zh_utils import ChineseTextCleaner
from logger_config import setup_logging

# Set up logger configuration

loader_log = setup_logging()

LANG_ID = 'hi' # select the target language   

def read_segments(file_name: str, int_file: str) -> None:
    """
    Read segments from a file and process them into sentences based on specific delimiters. 

    Args:
        file_name (str): Path to the input file to read segments from.
        int_file (str): Path to the output file where processed segments will be written.

    Raises:
        Exception: If there is an error reading the file or processing segments.
    """
    segments, current_segment = [], []
    BATCH_SIZE: int = 100000
    
    try:
        with open(file_name, 'r+b') as file:
            mfile = mmap.mmap(file.fileno(), 0, prot=mmap.PROT_READ)
            
            for segment in iter(mfile.readline, b""):                
                segment = segment.strip().decode('utf-8')
                # loader_log.info(f'Uncleaned: {segment}')
                
                if not segment:
                    continue

                temp_segment = ''
                for char in segment:
                    
                    if char in ('।', '!'):
                        
                        if temp_segment:
                            current_segment.append(temp_segment.strip())
                            segments.append(' '.join(current_segment))

                            if len(segments) >= BATCH_SIZE:
                                writefn(int_file, segments)
                                segments = []

                            current_segment = []
                            temp_segment = ''
                    else:
                        temp_segment += char

                if temp_segment:
                    current_segment.append(temp_segment.strip())

        if current_segment:
            segments.append(' '.join(current_segment))

    except Exception as e:
        loader_log.error(f"Error in read_segments: {e}")
        raise e

    finally:
        mfile.close()

def writefn(int_file_name: str, segments: List[str]) -> None:
    """
    Write processed segments to a file, cleaning each segment and logging progress.

    Args:
        int_file_name (str): Path to the output file where cleaned segments will be written.
        segments (List[str]): List of segments to write to the file.

    Raises:
        Exception: If there is an error writing to the file or processing segments.
    """
    try:
        total_segments = len(segments)

        with tqdm(total=total_segments, unit="segment") as pbar:

            for segment in segments:
                start_time = time.time()

                cleaned_segment = HindiTextCleaner(segment).clean()
                # loader_log.info(f'segment: {cleaned_segment}')

                with open(int_file_name, 'a', encoding='utf-8') as int_file:
                    int_file.write(cleaned_segment + '\n')

                pbar.update(1)

                end_time = time.time()
        time_el = end_time - start_time
        loader_log.info(f'Added {len(segments)} segments in {time_el:.2f} seconds')

    except Exception as e:
        loader_log.error(f"Error writing to {int_file_name}: {e}")
        raise e
    

def main(ifile_name: str, int_file: str) -> None:
    """
    Main function to read segments from an input file and write processed segments to an output file.

    Args:
        ifile_name (str): Path to the input file to read segments from.
        int_file (str): Path to the output file where processed segments will be written.

    Raises:
        FileNotFoundError: If the input file is not found.
    """
    try:
        read_segments(ifile_name, int_file)
        
    except FileNotFoundError as fe:
        loader_log.error(f"File not found error: {fe}")
        raise fe
    
    finally:
        loader_log.info(f'Written {ifile_name} to {int_file}')
