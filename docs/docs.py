# Updated as of:  02/08/2024

db_docstring = \
"""
This module's primary purpose is to interacting with the plyvel package. The plyvel package is a python wrapper over LevelDB, a NoSQL key-value store 
that is used for fast operations and reliable storage through disk. It uses SST's and LSM algorithms under the hood and is witten in C++. The key-value 
pairs are stored as byte strings, hence the inputs have to be encoded using the .encode function.

For ex: db.add(b'key', b'value')

The db.py module provides the following functions: 
    1. Creating/ closing and deleting databases.
    2. Adding/Removing key-value pair(s) in batches. 
    3. Iterating through the db to show it's contents
    4. Dumping all the db's data into a file. Supported formats - TXT/CSV.
    5. Recover from a dumped txt/csv files
    6. Check for particular ranges of unicode charecters to determine if all the entries are pure or not
    7. If the db has words, then we can also obtain each charecter's lengths 
    8. Provide a backup to the original db to another location.

Refer to plyvel's documentation: https://www.google.com/url?sa=t&source=web&rct=j&opi=89978449&url=https://plyvel.readthedocs.io/&ved=2ahUKEwjyoYujurKHAxWg2DgGHZzxCTwQFnoECBkQAQ&usg=AOvVaw07EA0lL2CV0xrfBbKJZal_

# Optional: Run the following command for generating phonemes
# phonemize outputs/dwordlist.txt -o outputs/dphonemes.txt --strip -l ur -b espeak
"""

utils_module_docstring = \
"""
Languages like urdu and other parso arabic scripts have many anomalies in them. Few of them include: 
    
    1. Unusual line spaces
    2. The way their words are written and combined.
    3. Diacritics
    4. Any kind of anomalies introduced while file was being fetched/processed (encodind related)
    5. Presence of other language scripts, such as english (most often seen)
    6. Presence of other unique unicode charecters such as emojis, numbers (urdu and non urdu) and punctuations.

Knowing and eliminating these anomalies before generating the vocab is of high importance. The cleaner.py module was implmented with an 
intent of removing as much garbage in the original text file before it can be tokenized and phonemized. Based on the above problems, the 
module has been broken into two classes:
    For Urdu: 
    1. UrduTextCleaner: This class contains all the utilities for removing diacritics, punctuations, numbers, and non-urdu charecters (such 
    as english) from urdu text. The module uses regex for pattern matching and substitutes with a '', along with the unicodedata library for 
    checking if all charcters are in unicode range. 

    2. UrduTokenizer: This class implements tokenizers from nltk.tokenize (WordPunkt), spacy, stanza (stanfordNLP) and a custom  Rule
    based tokenizer. The aim of this class is to tokenize and only return the unique urdu words (after checking their unicode range) from 
    each piece of input text. For each piece of text, it returns the following: 
        1. Length of the tokens list
        2. Length of the unique words list
        3. Words list

    For simplified chinese:  
    1. ChineseCleaner
    2. Chinese Tokenizer

"""

loader_docstring = \
"""
This module's implementation focuses on providing utilities for reading large text documents through RAM. Loading large files (>1GB)
can be expensive and can cause crashes to the system if memory is not handled carefully. The implementation uses mmap to lazy load the file into 
"segments", where each sentence is a portion of text with an arabic period (.) or a comma (,). The input file is loaded into memory using the mmap 
module, which lazily loads the file chunkwise and uses the virtual memory. Every segment is then cleaned for the following purposes:

    1. Normalising text, to remove unnecessary charecters
    2. Remove other language texts, and special charecters such as emojis, numbers, punctuation
    3. Remove diacritics

The cleaned segments are appended onto an "intermediate file", which is further used for token generation.

"""

words_docstring = \
"""
The loader module produces an intermediate, which is a cleaned and formatted version of the initial document. This module's implementation 
takes the intermediate file as input and tokenizes every segment, removes duplicates and appends them into a LevelDB instance. LevelDB was chosen 
due to it's easily accessible documentation and fast read-write operations. The option of changing the segment_batch_size, word_batch_size, and the 
type of tokenizer (nltk, spacy, stanza and rule based) is provided. 

"""

phonemize_utils_docstring = \
"""
Core utilities include the usage of phonemizer package for generating phones for each token/sentence.
"""

random_segments_docstring = \
"""
This module uses all the previous modules to tokenize random segments from a given text file. We first generate N number of random numbers within the 
segment limit of the file (which has to be found out before hand) and they are tokenized, phonemized and appended to an output file.
"""
