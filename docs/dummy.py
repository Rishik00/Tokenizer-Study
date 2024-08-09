# To run db.py


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


# To run loader.py

# if __name__ == "__main__":
#     try:
#         start_time = time.time()

#         input_file: str = 'data/hi/hi_large.txt'
#         intermediate_file: str = 'int/hi/int_hi.txt'
#         main(input_file, intermediate_file)
        
#     except Exception as e:
#         loader_log.error(f'Loader main fn error: {e}')
#         raise e
    
#     finally:
#         end_time = time.time()
#         time_taken = end_time - start_time
#         loader_log.info(f'File {input_file} parsed completely')
#         loader_log.info(f'Script execution completed in {time_taken:.4f} seconds')

# To run random_sampling.py

# if __name__ == "__main__":
#     start_time = time.time()
    
#     hi_path = 'int/hi/int_hi.txt'
#     seed = 372
#     out_file_path = 'outputs/hi/rand/selected_sentences_50L_1.txt'

#     # Ensure the output directory exists
#     os.makedirs(os.path.dirname(out_file_path), exist_ok=True)
    
#     main(ifile_name=hi_path, seed=seed)
    
#     end_time = time.time()
#     rlogger.info(f'Time taken: {end_time - start_time} seconds')


# To run tokens.py

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