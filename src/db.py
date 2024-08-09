import warnings
warnings.filterwarnings('ignore')

import time
import csv
from typing import List, Any
import plyvel as pl

# Local imports
from ur_normalize import URDU_ALL_CHARACTERS_UNICODE as urdu_chars
from logger_config import setup_logging

dblogger = setup_logging()

log_results: bool = False

class LevelDB:
    """
    A class to interact with a LevelDB database, providing methods for database operations 
    such as adding data, checking contents, dumping data, and recovering data from files.
    """

    def __init__(self, path: str):
        """
        Initialize the LevelDB instance and open the database.

        Args:
            path (str): Path to the LevelDB database.
        """
        self._path: str = path
        self.db = pl.DB(self._path, create_if_missing=True)
        self.db_closed: bool = False
        dblogger.info(f"Created database at {path}")

    def add_batch(self, words: List[tuple]) -> None:
        """
        Add a batch of key-value pairs to the database.

        Args:
            words (List[tuple]): A list of tuples where each tuple contains a key and a value.
        """
        with self.db.write_batch() as batch:
            for key, value in words:
                batch.put(key.encode('utf-8'), value.encode('utf-8'))

    def check(self, key: str) -> bool:
        """
        Check if a key exists in the database.

        Args:
            key (str): The key to check in the database.

        Returns:
            bool: True if the key does not exist, False otherwise.
        """
        try:
            return self.db.get(key.encode('utf-8')) is None
        except pl.Error as e:
            dblogger.error(f"Error checking key '{key}': {e}")
            raise e

    def find_size(self) -> tuple:
        """
        Calculate the total size and number of entries in the database.

        Returns:
            tuple: A tuple containing the total size in bytes and the number of entries.
        """
        db_size, db_length = 0, 0
        try:
            for key, value in self.db:
                db_length += 1
                db_size += len(key) + len(value)
        except pl.Error as e:
            dblogger.error(f"Error iterating over database: {e}")
        return db_size, db_length

    def show_db(self) -> None:
        """
        Log the contents of the database.
        """
        dblogger.info(f"Contents of db at: {self._path}")
        try:
            for key, value in self.db.iterator():
                dblogger.info(f"{key.decode('utf-8')} - {value.decode('utf-8')}")
        except pl.Error as e:
            dblogger.error(f"Error showing database: {e}")

    def close(self) -> None:
        """
        Close the database.
        """
        if not self.db_closed:
            try:
                self.db.close()
                self.db_closed = True
                dblogger.info("Closed db!")
            except pl.Error as e:
                dblogger.error(f"Error closing database: {e}")

    def destroy_db(self) -> None:
        """
        Destroy the database, deleting all its contents.
        """
        try:
            pl.destroy_db(self._path)
        except pl.Error as e:
            dblogger.error(f"Error destroying database: {e}")
            raise e
        dblogger.warning("Destroyed db!")

    def dump_to_csv(self, csv_file: str) -> None:
        """
        Dump the database contents to a CSV file.

        Args:
            csv_file (str): Path to the CSV file where the database contents will be written.
        """
        try:
            with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['Words'])
                for key, value in self.db.iterator():
                    csv_writer.writerow([key.decode('utf-8')])
            dblogger.info(f"Successfully dumped database contents to CSV file: {csv_file}")
        except Exception as e:
            dblogger.error(f"Error dumping database contents to CSV file: {e}")
            raise e
    
    def dump_to_txt(self, txt_file: str, only_tokens: bool = True) -> None:
        """
        Dump the database contents to a TXT file.

        Args:
            txt_file (str): Path to the TXT file where the database contents will be written.
            only_tokens (bool): If True, only keys (tokens) are written. If False, both keys and values are written.
        """
        try:
            with open(txt_file, 'a', encoding='utf-8') as txtfile:
                txtfile.write('Words\n')
                for key, value in self.db.iterator():
                    if only_tokens:
                        txtfile.write(key.decode('utf-8') + '\n')
                    else:
                        txtfile.write(key.decode('utf-8') + ',' + value.decode('utf-8') + '\n')
            dblogger.info(f"Successfully dumped database contents to file: {txt_file}")
        except Exception as e:
            dblogger.error(f"Error dumping database contents to TXT file: {e}")
            raise e

    def recover_db_from_txt(self, txt_file: str) -> None:
        """
        Recover the database from a TXT file.

        Args:
            txt_file (str): Path to the TXT file containing the data to recover.
        """
        try:
            with open(txt_file, 'r', encoding='utf-8') as txtfile:
                file_reader = txtfile.readlines()
                for word in file_reader:
                    word = word.strip()
                    self.db.put(word.encode('utf-8'), word.encode('utf-8'))
            dblogger.info(f"Successfully recovered database from TXT file: {txt_file}")
        except Exception as e:
            dblogger.error(f"Error recovering database from TXT file: {e}")
            raise e
        
    def recover_from_csv(self, csv_file: str) -> None:
        """
        Recover the database from a CSV file.

        Args:
            csv_file (str): Path to the CSV file containing the data to recover.
        """
        try:
            with open(csv_file, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if row:
                        word = row[0].strip()
                        self.db.put(word.encode('utf-8'), word.encode('utf-8'))
            dblogger.info(f"Successfully recovered database from CSV file: {csv_file}")
        except Exception as e:
            dblogger.error(f"Error recovering database from CSV file: {e}")
            raise e

    def unicode_helper(self, word: str) -> bool:
        """
        Check if a word contains only Urdu characters.

        Args:
            word (str): The word to check.

        Returns:
            bool: True if the word contains only Urdu characters, False otherwise.
        """
        for char in word:
            if char not in urdu_chars:
                return False
        return True

    def check_for_ur_unicode(self, if_remove: bool = True) -> int:
        """
        Check for and optionally remove non-Urdu words from the database.

        Args:
            if_remove (bool): If True, non-Urdu words will be removed from the database.

        Returns:
            int: The number of non-Urdu words found.
        """
        dblogger.info('Checking for non-Urdu words')
        non_urdu_words: List[str] = []

        try:
            for key, value in self.db.iterator():
                decoded_key: str = key.decode('utf-8')

                if not self.unicode_helper(decoded_key):
                    non_urdu_words.append(decoded_key)

            if non_urdu_words:
                dblogger.info(f'{len(non_urdu_words)} non-Urdu words found!')
                dblogger.info(f'{len(set(non_urdu_words))} number of unique words found')

                if if_remove:
                    for word in set(non_urdu_words):
                        self.db.delete(word.encode('utf-8'))
            else:
                dblogger.info("No non-Urdu words found in the database.")
        
        except pl.Error as e:
            dblogger.error(f"Error iterating over database: {e}")

        return len(non_urdu_words)
    
    def get_word_lengths(self, csvname: str) -> None:
        """
        Calculate and dump the lengths of words to a CSV file.

        Args:
            csvname (str): Path to the CSV file where word lengths will be written.
        """
        dblogger.info('Checking for word lengths')

        try:
            with open(csvname, 'a', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['Word', 'lengths'])

                for key, value in self.db.iterator():
                    dkey: str = key.decode('utf-8')
                    words = dkey.split(' ')

                    if len(words) > 1:
                        dblogger.info(f'Word length is greater than one for this word: {dkey}')
                    else:
                        csv_writer.writerow([dkey, len(dkey)])

            dblogger.info('CSV file created!')
        except Exception as e:
            dblogger.error(f"Error processing database for word lengths: {e}")
            raise e

    def backup_db(self, bdb_path: str) -> None:
        """
        Create a backup of the current database.

        Args:
            bdb_path (str): Path to the backup LevelDB database.
        """
        _backupdb = LevelDB(bdb_path)
        for key, value in self.db.iterator():
            _backupdb.add_batch([(key.decode('utf-8'), value.decode('utf-8'))])
        
        dblogger.info(f"Backup created for {self._path}. Check path: {bdb_path}")
