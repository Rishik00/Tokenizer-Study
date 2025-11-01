import re
import nltk
import jieba
import spacy
import stanza
import unicodedata
from typing import List, Dict, Any

## Local imports

class ChineseTextCleaner:
    """
    A class to clean and normalize Chinese text.
    
    Attributes:
        text (str): The text to be cleaned and normalized.
    """
    
    def __init__(self, text: str):
        """
        Initialize the ChineseTextCleaner with the text to be processed.
        
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
            'chinese': ['一', '二', '三', '四', '五', '六', '七', '八', '九', '零'],
            'english': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        }
        self._zh = re.compile(r'[^\u4e00-\u9fff]', flags=re.UNICODE)

    def remove_punctuation(self):
        """
        Remove non-Chinese characters and common punctuation marks from the text.
        """
        self.text = re.sub(self._zh, ' ', self.text)
        self.text = re.sub(r'[.,-_*%?!#@=+|(){}[\]\'\"“”‘’]', ' ', self.text)
    
    def remove_numbers(self):
        """
        Remove both English and Chinese numerals from the text.
        """
        self.text = re.sub(r'\d+', ' ', self.text)
        self.text = re.sub(r'[一二三四五六七八九零]', ' ', self.text)
    
    def remove_redundant_spaces(self):
        """
        Replace multiple spaces with a single space and strip leading/trailing spaces.
        """
        self.text = re.sub(r'\s+', ' ', self.text).strip()

    def remove_dates_html_tags(self):
        """
        Remove HTML tags and date patterns from the text.
        """
        self.text = re.sub(r'<.*?>', '', self.text)  # Remove HTML tags
        self.text = re.sub(r'[0-9]{2}/[09]{2}/[0-9]{4}', '', self.text)  # Remove dates

    def clean(self):
        """
        Perform the complete text cleaning process including removing punctuation, 
        numbers, redundant spaces, and HTML tags.
        
        Returns:
            str: The cleaned text.
        """
        self.remove_punctuation()
        self.remove_numbers()
        self.remove_redundant_spaces()
        # Uncomment the following line if you want to remove dates and HTML tags
        # self.remove_dates_html_tags()

        return self.text

## Tokenizer class - jieba left to use
class ChineseTokenizer:
    """
    A class to tokenize Chinese text using different tokenization methods.
    
    Attributes:
        token_list (List[str]): The list of tokens extracted from the text.
        tokenizer (str): The tokenization method to use ('jieba', 'spacy', 'stanza').
        jieba_tokenizer: Jieba tokenizer function.
        spacy_tokenizer: SpaCy tokenizer for Chinese.
        stanza_tokenizer: Stanza tokenizer for Chinese.
        _zh_unicode_ranges (List[Tuple[int, int]]): Unicode ranges for Chinese characters.
    """
    
    def __init__(self, language: str = 'zh', tokenizer: str = 'jieba'):
        """
        Initialize the ChineseTokenizer with the specified tokenization method.
        
        Args:
            language (str): The language code (default is 'zh').
            tokenizer (str): The tokenization method to use ('jieba', 'spacy', 'stanza').
        """
        self.token_list: List[str] = []
        self.tokenizer = tokenizer
        
        if self.tokenizer == 'jieba':
            self.jieba_tokenizer = jieba.cut

        elif self.tokenizer == 'spacy':
            self.spacy_tokenizer = spacy.load('zh_core_web_sm', disable=['parser', 'ner', 'tagger'])

        elif self.tokenizer == 'stanza':
            self.stanza_tokenizer = stanza.Pipeline(processors='tokenize', lang='zh-hans')

        self._zh_unicode_ranges = [
            (0x4E00, 0x9FFF),  # CJK Unified Ideographs
            (0x3400, 0x4DBF),  # CJK Unified Ideographs Extension A
            (0x2A700, 0x2B73F) # CJK Ideographs Extension B
        ]

    def _tokenize_with_jieba(self, text: str, is_unique: bool = True):
        """
        Tokenize the text using Jieba's tokenizer.
        
        Args:
            text (str): The text to tokenize.
            is_unique (bool): Whether to return unique tokens.
        
        Returns:
            Tuple[int, int, List[str]]: Number of tokens, number of unique tokens, and list of tokens.
        """
        res = self.jieba_tokenizer(text)
        res = ' '.join(res)
        tokens = res.split()

        if is_unique:
            words = list(set(tokens))
        else:
            words = tokens
        
        return len(tokens), len(words), words

    def _tokenize_with_spacy(self, text: str, is_unique: bool = True):
        """
        Tokenize the text using SpaCy's Chinese tokenizer.
        
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
        
        return len(tokens), len(words), words

    def _tokenize_with_stanza(self, text: str, is_unique: bool = True):
        """
        Tokenize the text using Stanza's Chinese tokenizer.
        
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
        
        return len(tokens), len(words), words

    def helper(self, word: str) -> bool:
        """
        Check if a word contains Chinese characters.
        
        Args:
            word (str): The word to check.
        
        Returns:
            bool: True if the word contains Chinese characters, False otherwise.
        """
        for char in word:
            if unicodedata.category(char) == 'Lo':
                char_code = ord(char)
                if any(start <= char_code <= end for start, end in self._zh_unicode_ranges):
                    return True
        return False

    def remove_non_zh_tokens(self):
        """
        Remove tokens that do not contain Chinese characters.
        """
        if self.token_list is not None:
            self.token_list = [word for word in self.token_list if self.helper(word)]

    def tokenize(self, text, is_unique: bool = True):
        """
        Tokenize the text using the specified tokenization method and filter Chinese tokens.
        
        Args:
            text (str): The text to tokenize.
            is_unique (bool): Whether to return unique tokens.
        
        Returns:
            Tuple[int, int, List[str]]: Number of tokens, number of filtered tokens, and list of tokens.
        """
        self.token_list: List[str] = []

        if not is_unique:
            print('The output will not contain unique words')

        if self.tokenizer == 'spacy':
            num_tokens, num_unique_tokens, self.token_list = self._tokenize_with_spacy(text, is_unique) 

        elif self.tokenizer == 'stanza':
            num_tokens, num_unique_tokens, self.token_list = self._tokenize_with_stanza(text, is_unique)

        else:
            num_tokens, num_unique_tokens, self.token_list = self._tokenize_with_jieba(text, is_unique)

        self.remove_non_zh_tokens()
        return num_tokens, len(self.token_list), self.token_list
