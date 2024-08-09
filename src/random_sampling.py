import os
import time
import random
from typing import List
from logger_config import setup_logging

# Set up logging
rlogger = setup_logging(log_file='logs/hi/rdtok.log')

def count_lines_in_file(file_path: str) -> int:
    """
    Count the number of lines in a text file.

    Args:
        file_path (str): Path to the file.

    Returns:
        int: Number of lines in the file.

    Raises:
        FileNotFoundError: If the file is not found.
        IOError: If there is an error reading the file.
    """
    line_count = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for _ in file:
                line_count += 1
    except (FileNotFoundError, IOError) as e:
        rlogger.error(f"Error reading file {file_path}: {e}")
        raise
    return line_count

def generate_random_indices(limit: int, num_indices: int, seed: int = None) -> List[int]:
    """
    Generate a sorted list of unique random indices.

    Args:
        limit (int): The upper bound for the random indices.
        num_indices (int): Number of random indices to generate.
        seed (int, optional): Seed for the random number generator.

    Returns:
        List[int]: Sorted list of random indices.

    Raises:
        ValueError: If num_indices is larger than limit.
    """
    if num_indices > limit:
        raise ValueError("num_indices cannot be larger than limit")
    
    random.seed(seed)
    indices = sorted(random.sample(range(limit), num_indices))
    rlogger.info(f'Generated {len(indices)} random indices')
    return indices

def extract_sentences(file_path: str, indices: List[int], out_file_path: str) -> bool:
    """
    Extract specific lines from a file based on given indices and write them to an output file.

    Args:
        file_path (str): Path to the input file.
        indices (List[int]): List of line indices to extract.
        out_file_path (str): Path to the output file.

    Returns:
        bool: True if extraction completed successfully, False if EOF was reached.

    Raises:
        FileNotFoundError: If the input file is not found.
        IOError: If there is an error processing the files.
    """
    extracted_count = 0
    current_index = 0
    eof_reached = False

    try:
        with open(file_path, 'r', encoding='utf-8') as file, open(out_file_path, 'a', encoding='utf-8') as out_file:
            rlogger.info('Opened both files!')

            for line_number, line in enumerate(file, start=1):
                if line_number == indices[current_index]:
                    
                    out_file.write(line.strip() + '\n')
                    extracted_count += 1
                    current_index += 1

                    if extracted_count % 100000 == 0:
                        rlogger.info(f'Added {extracted_count} segments')

                    if current_index >= len(indices):
                        rlogger.info(f'Finished extracting {extracted_count} sentences to {out_file_path}')
                        eof_reached = True
                        break

    except (FileNotFoundError, IOError) as e:
        rlogger.error(f"Error processing file {file_path}: {e}")
        raise
    
    return eof_reached

def main(ifile_name: str, seed: int):
    """
    Main function to count lines, generate random indices, and extract sentences.

    Args:
        ifile_name (str): Path to the input file.
        seed (int): Seed for random number generation.
    """
    out_file_path = 'outputs/hi/rand/selected_sentences_50L_1.txt'

    # Generate random indices for extraction
    rlist = generate_random_indices(8800000, 5000000, seed=seed)
    
    # Extract sentences based on generated indices
    if extract_sentences(ifile_name, rlist, out_file_path):
        print('Done')

# 
