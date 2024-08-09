import re
import stanza
import warnings
import unicodedata
from spacy.lang.hi import Hindi
from typing import List, Dict, Any
from indicnlp.normalize.indic_normalize import IndicNormalizerFactory
from indicnlp.tokenize import indic_tokenize
import stanza.pipeline

# local imports

class HindiTextCleaner:
    """
    A class to clean and normalize Hindi text.
    
    Attributes:
        text (str): The text to be cleaned and normalized.
    """
    
    def __init__(self, text: str) -> None:
        """
        Initialize the HindiTextCleaner with the text to be processed.
        
        Args:
            text (str): The text to be cleaned.
        """
        self.text = text
        self._emoji_patterns = re.compile("["
            u"\U0001F600-\U0001F64F"  # Emoticons
            u"\U0001F300-\U0001F5FF"  # Symbols and Pictographs
            u"\U0001F680-\U0001F6FF"  # Transport and Map Symbols
            u"\U0001F1E0-\U0001F1FF"  # Regional Indicator Symbols
            u"\U00002702-\U000027B0"  # Dingbats
            u"\U000024C2-\U0001F251"  # Enclosed Characters
            "]+",
            flags=re.UNICODE,
        )
        self._numbers = {
            'hindi': ['०', '१', '२', '३', '४', '५', '६', '७', '८', '९'],
            'english': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']      
        }
        self._hi = re.compile(r'[^\u0900-\u097F]', flags=re.UNICODE)
        self.normalizer = IndicNormalizerFactory().get_normalizer(language="hi", remove_nuktas=False)

    def normalize(self):
        """
        Normalize the Hindi text.
        """
        self.text = self.normalizer.normalize(self.text)

    def remove_punctuation(self):
        """
        Remove punctuation and non-Hindi characters from the text.
        """
        self.text = re.sub(self._hi, ' ', self.text)
        self.text = re.sub(r'[।॥.,-_*%?!#@=+|(){}[\]\'\"“”‘’]', ' ', self.text)

    def remove_numbers(self):
        """
        Remove Hindi and English numerals from the text.
        """
        for num in self._numbers['hindi'] + self._numbers['english']:
            self.text = self.text.replace(num, '')

    def remove_redundant_spaces(self):
        """
        Remove extra spaces from the text.
        """
        self.text = re.sub(r'\s+', ' ', self.text).strip()

    def clean(self):
        """
        Perform the complete text cleaning process including normalization, 
        removing punctuation, numbers, and redundant spaces.
        
        Returns:
            str: The cleaned text.
        """
        # self.normalize()  # Uncomment if normalization is needed
        self.remove_punctuation()
        self.remove_numbers()
        self.remove_redundant_spaces()
        return self.text


class HindiTokenizer:
    """
    A class to tokenize Hindi text using different tokenization methods.
    
    Attributes:
        token_list (List[str]): The list of tokens extracted from the text.
        tokenizer (str): The tokenization method to use ('spacy', 'stanza', 'indicnlp').
        spacy_tokenizer: Spacy tokenizer for Hindi.
        stanza_tokenizer: Stanza tokenizer for Hindi.
        indic_tokenizer: IndicNLP tokenizer for Hindi.
        _hi_unicode_range (List[Tuple[int, int]]): Unicode range for Hindi characters.
    """
    
    def __init__(self, tokenizer: str = 'spacy') -> None:
        """
        Initialize the HindiTokenizer with the specified tokenization method.
        
        Args:
            tokenizer (str): The tokenization method to use ('spacy', 'stanza', 'indicnlp').
        """
        self.token_list: List[str] = []
        self.tokenizer = tokenizer

        if self.tokenizer == 'spacy':
            self.spacy_tokenizer = Hindi()
        
        elif self.tokenizer == 'stanza':
            self.stanza_tokenizer = stanza.Pipeline(lang='hi', processors='tokenize')

        elif self.tokenizer == 'indicnlp':
            self.indic_tokenizer = None  # Placeholder if needed in future
        
        self._hi_unicode_range = [
            (0x0900, 0x097F)  # Unicode range for Hindi script
        ]

    def helper(self, word: str) -> bool:
        """
        Check if a word contains Hindi characters.
        
        Args:
            word (str): The word to check.
        
        Returns:
            bool: True if the word contains Hindi characters, False otherwise.
        """
        for char in word:
            if unicodedata.category(char) == 'Lo':
                char_code = ord(char)
                if any(start <= char_code <= end for start, end in self._hi_unicode_range):
                    return True
        
        return False

    def remove_non_hi_tokens(self):
        """
        Remove tokens that do not contain Hindi characters.
        """
        if self.token_list is not None:
            self.token_list = [word for word in self.token_list if self.helper(word)]

    def _tokenize_with_spacy(self, text: str, is_unique: bool = True):
        """
        Tokenize the text using SpaCy's Hindi tokenizer.
        
        Args:
            text (str): The text to tokenize.
            is_unique (bool): Whether to return unique tokens.
        
        Returns:
            Tuple[int, int, List[str]]: Number of tokens, number of unique tokens, and list of tokens.
        """
        res = self.spacy_tokenizer(text)
        tokens = [token.text for token in res]
        len_tokens = len(tokens)

        if is_unique:
            words = list(set(tokens))
        else:
            words = tokens
        
        return len_tokens, len(words), words

    def _tokenize_with_stanza(self, text: str, is_unique: bool = True):
        """
        Tokenize the text using Stanza's Hindi tokenizer.
        
        Args:
            text (str): The text to tokenize.
            is_unique (bool): Whether to return unique tokens.
        
        Returns:
            Tuple[int, int, List[str]]: Number of tokens, number of unique tokens, and list of tokens.
        """
        res = self.stanza_tokenizer(text)
        tokens = [word.text for sentence in res.sentences for word in sentence.words]
        len_tokens = len(tokens)

        if is_unique:
            words = list(set(tokens))
        else:
            words = tokens
        
        return len_tokens, len(words), words
    
    def _tokenize_with_indicnlp(self, text: str, is_unique: bool = True):
        """
        Tokenize the text using IndicNLP's tokenizer.
        
        Args:
            text (str): The text to tokenize.
            is_unique (bool): Whether to return unique tokens.
        
        Returns:
            Tuple[int, int, List[str]]: Number of tokens, number of unique tokens, and list of tokens.
        """
        tokens = indic_tokenize.trivial_tokenize(text, lang='hin')
        len_tokens = len(tokens)

        if is_unique:
            utokens = list(set(tokens))
        else:
            utokens = tokens
        
        return len_tokens, len(utokens), utokens

    def tokenize(self, text, is_unique: bool = True):
        """
        Tokenize the text using the specified tokenization method and filter Hindi tokens.
        
        Args:
            text (str): The text to tokenize.
            is_unique (bool): Whether to return unique tokens.
        
        Returns:
            Tuple[int, int, List[str]]: Number of tokens, number of filtered tokens, and list of tokens.
        """
        self.token_list: List[str] = []

        if not is_unique:
            print('The output will not have unique tokens')
        
        if self.tokenizer == 'spacy':
            num_tokens, num_unique_tokens, self.token_list = self._tokenize_with_spacy(text, is_unique)
        
        elif self.tokenizer == 'stanza':
            num_tokens, num_unique_tokens, self.token_list = self._tokenize_with_stanza(text, is_unique)

        elif self.tokenizer == 'indicnlp':
            num_tokens, num_unique_tokens, self.token_list = self._tokenize_with_indicnlp(text, is_unique)
        
        self.remove_non_hi_tokens()
        return num_tokens, len(self.token_list), self.token_list
