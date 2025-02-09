# Tokenizer-Study
Tokenizer study is the result of my work at the center for AI and Robotics, DRDO. The project is an empirical study analysing the performance of various word level tokenizers on three languages: 
1. Urdu (From parso arabic family)
2. Simplified Chinese (From logographic)
3. Hindi (From indic)

**Primary Objectives**
1. To establish a proper benchmark for the performance of tokenizers across different languages
2. To build a reliable text processing pipeline that can be reused for processing text from the above mentioned languages when required.

**Libraries used**: `LevelDB, regex, nltk, spacy, stanza, jieba` (Entire project was done using python).  You can refer to `Tokenizer-Study/docs/docs.py` for more information about how individual components work. 

The data taken for this study was from the popular CC-100 corpus, which is a family of multilingual text corpuses that has been collected using crawlers. The text has been preprocessed appropriately keeping the language's rules and unicode was leveraged for efficiently removing noisy data from other languages (primarily noticed was english). The cleaning was done using python's `regex` library by writing custom wrappers for each language separately. 

**Results**
It is to be noted that the metric used here to determine the quality of tokenization is the hit ratio of tokens to a particular ground truth set of words. Matchinng was done and the results were aggregated for a set of 5 million individual sentences. 

**Running the pipeline**
I really appreciate the thought :) 
You are more than welcome to run the pipeline for your own amusement or if you need any kind of a base for something you are building. I would also heavily welcome and appreciate any kind of contributions in docs or in the actual code itself, I understand there are lots of things that can be improved. 

Currently, you can do the following:
1. You can use `loader.py` for loading text from CC-100. Note that you have to download the file from their [website](https://data.statmt.org/cc-100/)
2. In the loader, please set the proper config for the language of your choice.
3. Once loader runs, the output file will contain the text separated by \n 
