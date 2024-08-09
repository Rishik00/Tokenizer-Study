import warnings
warnings.filterwarnings('ignore')

import time
import csv
from typing import List, Any
import plyvel as pl

# Local imports
from ur_normalize import URDU_ALL_CHARACTERS_UNICODE as urdu_chars
from logger_config import setup_logging

ur_log_files: List[str] = ['logs/ur/db.log', 'logs/ur/checkdb.log', 'logs/ur/fulldb.log']
zh_log_files: List[str] = ['logs/zh/db.log', 'logs/zh/checkdb.log', 'logs/zh/fulldb.log']
hi_log_files: List[str] = ['logs/hi/db.log', 'logs/hi/checkdb.log', 'logs/hi/fulldb.log']
dblogger = setup_logging('logs/ur/dummydb.log')

log_results: bool = False

class LevelDB:

    def __init__(self, path: str):

        self._path: str = path
        self.db = pl.DB(self._path, create_if_missing=True)
        self.db_closed: bool = False
        dblogger.info(f"Created database at {path}")

    def add_batch(self, words: List[tuple]):
        with self.db.write_batch() as batch:
            for key, value in words:
                batch.put(key.encode('utf-8'), value.encode('utf-8'))

    def check(self, key):
        try:
            return self.db.get(key.encode('utf-8')) is None
        
        except pl.Error as e:
            dblogger.error(f"Error checking key '{key}': {e}")
            raise e

    def find_size(self) -> Any:
        db_size, db_length = 0, 0

        try:
            for key, value in self.db:
                db_length += 1
                db_size += len(key) + len(value)
        
        except pl.Error as e:
            dblogger.error(f"Error iterating over database: {e}")
        
        return db_size, db_length

    def show_db(self) -> None:
        dblogger.info(f"Contents of db at: {self._path}")
        
        try:
            for key, value in self.db.iterator():
                dblogger.info(f"{key.decode('utf-8')} - {value.decode('utf-8')}")
        
        except pl.Error as e:
            dblogger.error(f"Error showing database: {e}")

    def close(self) -> None:
        if not self.db_closed:
            try:
                self.db.close()
                self.db_closed = True
                dblogger.info("Closed db!")
        
            except pl.Error as e:
                dblogger.error(f"Error closing database: {e}")

    def destroy_db(self) -> None:
        try:
            pl.destroy_db(self._path)
        
        except pl.Error as e:
            dblogger.error(f"Error destroying database: {e}")
            raise e
        
        dblogger.warning("Destroyed db!")

    def dump_to_csv(self, csv_file: str) -> None:
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
        try:
            with open(txt_file, 'a', encoding='utf-8') as txtfile:
                txtfile.write('Words\n')
                for key, value in self.db.iterator():
                    # Only tokens have to be appended as keys
                    if only_tokens:
                        txtfile.write(key.decode('utf-8') + '\n')
                    # Both keys and values will be dumped
                    else:
                        txtfile.write(key.decode('utf-8') + ',' + value.decode('utf-8') + '\n')
                        
            dblogger.info(f"Successfully dumped database contents to file: {txt_file}")
        
        except Exception as e:
            dblogger.error(f"Error dumping database contents to TXT file: {e}")
            raise e
        
    def recover_db_from_txt(self, txt_file: str) -> None:
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
        for char in word:
            if char not in urdu_chars:
                return False
        return True

    def check_for_ur_unicode(self, if_remove: bool = True) -> int:
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

                for word in set(non_urdu_words):
                    if if_remove:
                        self.db.delete(word.encode('utf-8'))
            else:
                dblogger.info("No non-Urdu words found in the database.")
        
        except pl.Error as e:
            dblogger.error(f"Error iterating over database: {e}")

        return len(non_urdu_words)
    
    def get_word_lengths(self, csvname: str) -> None:
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
        _backupdb = LevelDB(bdb_path)
        for key, value in self.db.iterator():
            _backupdb.add_batch([(key.decode('utf-8'), value.decode('utf-8'))])
        
        dblogger.info(f"Backup created for {self._path}. Check path: {bdb_path}")

# if __name__ == "__main__":
#     try:
#         start_time = time.time()
#         sampledb = LevelDB('/tmp/dummydb/')
#         # sampledb.dump_to_txt('outputs/hi/ground_truth/hindi.txt')

#         sampledb.recover_db_from_txt('outputs/zh/ground_truth/cedict.txt')
#         # # sampledb.check_for_ur_unicode()
#         sampledb.get_word_lengths('outputs/zh/ground_truth/truth.csv')

#         sampledb.close()
#         sampledb.destroy_db()
#         dblogger.info("Database closed.")

#     except Exception as e:
#         dblogger.error(f"Exception during database operation: {e}")

#     end_time = time.time()
#     dblogger.info(f"Total execution time: {end_time - start_time} seconds")
