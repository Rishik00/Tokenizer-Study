import re
import nltk
import spacy
import stanza
import warnings
import unicodedata
from typing import Any, List
from indicnlp.tokenize import indic_tokenize
from spacy.lang.ur import Urdu

# Local imports
from ur_normalize import normalize_urdu_text

warnings.filterwarnings('ignore')

class UrduTextCleaner:
    """
    A class to clean and normalize Urdu text.
    
    Attributes:
        text (str): The text to be cleaned and normalized.
        language (str): Language code (default is 'ur').
    """
    
    def __init__(self, text: str, language: str = 'ur'):
        """
        Initialize the UrduTextCleaner with the text to be processed.
        
        Args:
            text (str): The text to be cleaned.
            language (str): The language code (default is 'ur').
        """
        self.text: str = text
        self.language: str = language

        self._numbers = {
            'urdu': ['۶', '۴', '۵', '۸', '۲', '۰', '۷', '۹', '۳', '۱'],
            'english': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
        }
        self._emoji_patterns = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # Emoticons
            u"\U0001F300-\U0001F5FF"  # Symbols and Pictographs
            u"\U0001F680-\U0001F6FF"  # Transport and Map Symbols
            u"\U0001F1E0-\U0001F1FF"  # Regional Indicator Symbols
            u"\U00002702-\U000027B0"  # Dingbats
            u"\U000024C2-\U0001F251"  # Enclosed Characters
            "]+",
            flags=re.UNICODE,
        )   

    def normalize(self) -> None:
        """
        Normalize the Urdu text using a specified normalization function.
        """
        self.text = normalize_urdu_text(self.text)

    def remove_special_characters(self) -> None:
        """
        Remove non-Uurdu characters and emojis from the text.
        """
        self.text = re.sub(r'[^\u0600-\u06FF\s]', '', self.text)  # Remove non-Urdu characters
        self.text = self._emoji_patterns.sub(r'', self.text)  # Remove emojis

    def rem_word_punct_diac(self) -> None:
        """
        Remove punctuation and diacritical marks from the text.
        """
        self.text = re.sub(r'[؟,۔.,-_*%?!#@=+|(){}[\]\'\"“”‘’]', ' ', self.text)

    def remove_nums(self) -> None:
        """
        Remove both Urdu and English numerals from the text.
        """
        for num in self._numbers['urdu'] + self._numbers['english']:
            self.text = self.text.replace(num, '')

    def clean_data(self) -> str:
        """
        Perform the complete text cleaning process including removing special characters,
        punctuation, numbers, and normalizing the text.
        
        Returns:
            str: The cleaned and normalized text.
        """
        self.remove_special_characters()
        self.rem_word_punct_diac() 
        self.remove_nums()
        self.normalize()

        return self.text


class UrduTokenizer:
    """
    A class to tokenize Urdu text using various tokenization methods.
    
    Attributes:
        word_list (List[str]): The list of tokens extracted from the text.
        tokenizer (str): The tokenization method to use ('nltk', 'spacy', 'stanza', 'indicnlp').
        nltk_tokenizer: NLTK tokenizer function.
        spacy_tokenizer: SpaCy tokenizer for Urdu.
        stanza_tokenizer: Stanza tokenizer for Urdu.
        _urdu_unicode_range (List[Tuple[int, int]]): Unicode ranges for Urdu characters.
    """
    
    def __init__(self, language: str = 'ur', tokenizer: str = 'nltk'):
        """
        Initialize the UrduTokenizer with the specified tokenization method.
        
        Args:
            language (str): The language code (default is 'ur').
            tokenizer (str): The tokenization method to use ('nltk', 'spacy', 'stanza', 'indicnlp').
        """
        self.word_list: List[str] = []
        self.tokenizer = tokenizer

        if self.tokenizer == 'nltk':
            self.nltk_tokenizer = nltk.word_tokenize
        
        elif self.tokenizer == 'spacy':
            self.spacy_tokenizer = spacy.blank('ur')

        elif self.tokenizer == 'stanza':
            self.stanza_tokenizer = stanza.Pipeline(processors='tokenize', lang='ur')
        
        elif self.tokenizer == 'indicnlp':
            self.indic_tokenizer = None

        self._urdu_unicode_range = [
            (0x0600, 0x06FF),  # Arabic script
            (0x0750, 0x077F),  # Arabic Supplement
            (0xFB50, 0xFDFF),  # Arabic Presentation Forms-A
            (0xFE70, 0xFEFF)   # Arabic Presentation Forms-B
        ]

    def _tokenize_with_nltk(self, text: str, is_unique: bool = True):
        """
        Tokenize the text using NLTK's tokenizer.
        
        Args:
            text (str): The text to tokenize.
            is_unique (bool): Whether to return unique tokens.
        
        Returns:
            Tuple[int, int, List[str]]: Number of tokens, number of unique tokens, and list of tokens.
        """
        tokens = self.nltk_tokenizer(text)
        num_tokens = len(tokens)
        
        if is_unique:
            words = list(set(tokens))
        else:
            words = tokens
        
        return num_tokens, len(words), words
    
    def _tokenize_with_stanza(self, text: str, is_unique: bool = True):
        """
        Tokenize the text using Stanza's tokenizer.
        
        Args:
            text (str): The text to tokenize.
            is_unique (bool): Whether to return unique tokens.
        
        Returns:
            Tuple[int, int, List[str]]: Number of tokens, number of unique tokens, and list of tokens.
        """
        doc = self.stanza_tokenizer(text)
        tokens = [word.text for sentence in doc.sentences for word in sentence.words]
        len_tokens = len(tokens)

        if is_unique:
            words = list(set(tokens))
        else:
            words = tokens
        
        return len(tokens), len(words), words

    def _tokenize_with_spacy(self, text: str, is_unique: bool = True):
        """
        Tokenize the text using SpaCy's tokenizer.
        
        Args:
            text (str): The text to tokenize.
            is_unique (bool): Whether to return unique tokens.
        
        Returns:
            Tuple[int, int, List[str]]: Number of tokens, number of unique tokens, and list of tokens.
        """
        doc = self.spacy_tokenizer(text)
        tokens = [token.text for token in doc]
        len_tokens = len(tokens)
        
        if is_unique:
            words = list(set(tokens))
        else:
            words = tokens
        
        return len(tokens), len(words), words

    def _tokenize_with_indicnlp(self, text: str, is_unique: bool = True):
        """
        Tokenize the text using IndicNLP's tokenizer.
        
        Args:
            text (str): The text to tokenize.
            is_unique (bool): Whether to return unique tokens.
        
        Returns:
            Tuple[int, int, List[str]]: Number of tokens, number of unique tokens, and list of tokens.
        """
        tokens = indic_tokenize.trivial_tokenize(text, lang='urd')
        len_tokens = len(tokens)

        if is_unique:
            utokens = list(set(tokens))
        else:
            utokens = tokens
        
        return len(tokens), len(utokens), utokens

    def helper(self, word: str) -> bool:
        """
        Check if a word contains Urdu characters.
        
        Args:
            word (str): The word to check.
        
        Returns:
            bool: True if the word contains Urdu characters, False otherwise.
        """
        for char in word:
            if unicodedata.category(char) == 'Lo':
                char_code = ord(char)
                if any(start <= char_code <= end for start, end in self._urdu_unicode_range):
                    return True
        return False

    def remove_non_urdu_words(self) -> None:
        """
        Remove tokens that do not contain Urdu characters.
        """
        if self.word_list is not None:
            self.word_list = [word for word in self.word_list if self.helper(word)]

    def tokenize(self, text: str, is_unique: bool = True) -> List[str]:
        """
        Tokenize the text using the specified tokenization method and filter Urdu tokens.
        
        Args:
            text (str): The text to tokenize.
            is_unique (bool): Whether to return unique tokens.
        
        Returns:
            Tuple[int, int, List[str]]: Number of tokens, number of filtered tokens, and list of tokens.
        """
        self.word_list = []

        if not is_unique:
            print('The output will not contain unique words')

        if self.tokenizer == 'spacy':
            len_tokens, len_words, self.word_list = self._tokenize_with_spacy(text, is_unique)
        
        elif self.tokenizer == 'stanza':
            len_tokens, len_words, self.word_list = self._tokenize_with_stanza(text, is_unique)
        
        elif self.tokenizer == 'nltk':
            len_tokens, len_words, self.word_list = self._tokenize_with_nltk(text, is_unique)

        else:
            len_tokens, len_words, self.word_list = self._tokenize_with_indicnlp(text, is_unique)
        
        self.remove_non_urdu_words()
        return len_tokens, len(self.word_list), self.word_list
