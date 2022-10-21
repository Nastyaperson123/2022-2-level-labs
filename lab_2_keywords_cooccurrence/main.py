"""
Lab 2
Extract keywords based on co-occurrence frequency
"""
from pathlib import Path
from string import punctuation
from typing import Optional, Sequence, Mapping

KeyPhrase = tuple[str, ...]
KeyPhrases = Sequence[KeyPhrase]


def extract_phrases(text: str) -> Optional[Sequence[str]]:
    """
    Splits the text into separate phrases using phrase delimiters
    :param text: an original text
    :return: a list of phrases

    In case of corrupt input arguments, None is returned
    """
    if not isinstance(text, str) or not text:
        return None

    for i in text:
        if i in punctuation + '.;:¡!¿?…⋯‹›«»\\"“”[]()⟨⟩}{&|-–~—':
            text = text.replace(i, ',')
    list_split = text.split(',')
    return [token.strip() for token in list_split if token.strip()]


def extract_candidate_keyword_phrases(phrases: Sequence[str], stop_words: Sequence[str]) -> Optional[KeyPhrases]:
    """
    Creates a list of candidate keyword phrases by splitting the given phrases by the stop words
    :param phrases: a list of the phrases
    :param stop_words: a list of the stop words
    :return: the candidate keyword phrases for the text

    In case of corrupt input arguments, None is returned
    """
    if not isinstance(phrases, list):
        return None
    if not isinstance(stop_words, list):
        return None
    if stop_words == [] or phrases == []:
        return None
    for element in phrases:
        if not isinstance(element, str):
            return None
    for element in stop_words:
        if not isinstance(element, str):
            return None

    possible_phrases = []
    for phrase in phrases:
        phrase_split = phrase.lower().split()
        without_stop_words = []
        for el in phrase_split:
            if el not in stop_words:
                without_stop_words.append(el)
            elif without_stop_words:
                possible_phrases.append(tuple(without_stop_words))
                without_stop_words.clear()
        if without_stop_words:
            possible_phrases.append(tuple(without_stop_words))
    return possible_phrases



def calculate_frequencies_for_content_words(candidate_keyword_phrases: KeyPhrases) -> Optional[Mapping[str, int]]:
    """
    Extracts the content words from the candidate keyword phrases list and computes their frequencies
    :param candidate_keyword_phrases: a list of the candidate keyword phrases
    :return: a dictionary with the content words and corresponding frequencies

    In case of corrupt input arguments, None is returned
    """
    if not (isinstance(candidate_keyword_phrases, list) and candidate_keyword_phrases != []):
        return None

    freq_dict = {}
    for phrase in candidate_keyword_phrases:
        for word in phrase:
            freq_dict[word] = freq_dict.get(word, 0) + 1
    return freq_dict





def calculate_word_degrees(candidate_keyword_phrases: KeyPhrases,
                           content_words: Sequence[str]) -> Optional[Mapping[str, int]]:
    """
    Calculates the word degrees based on the candidate keyword phrases list
    Degree of a word is equal to the total length of all keyword phrases the word is found in

    :param content_words: the content words from the candidate keywords
    :param candidate_keyword_phrases: the candidate keyword phrases for the text
    :return: the words and their degrees

    In case of corrupt input arguments, None is returned
    """
    if not isinstance(candidate_keyword_phrases, list) or candidate_keyword_phrases == []:
        return None
    if not isinstance(content_words, list) or content_words == []:
        return None

    word_degrees = {}
    for word in content_words:
        word_degrees[word] = 0
        for phrase in candidate_keyword_phrases:
            if word in phrase:
                word_degrees[word] += len(phrase)
    return word_degrees





def calculate_word_scores(word_degrees: Mapping[str, int],
                          word_frequencies: Mapping[str, int]) -> Optional[Mapping[str, float]]:
    """
    Calculate the word score based on the word degree and word frequency metrics

    :param word_degrees: a mapping between the word and the degree
    :param word_frequencies: a mapping between the word and the frequency
    :return: a dictionary with {word: word_score}

    In case of corrupt input arguments, None is returned
    """
    if not isinstance(word_degrees, dict) or word_degrees == {}:
        return None
    if not isinstance(word_frequencies, dict) or word_frequencies == {}:
        return None

    word_scores = {}
    for el in word_degrees.keys():
        if el not in word_frequencies.keys():
            return None
        word_scores[el] = word_degrees[el] / word_frequencies[el]
    return word_scores




#python -m pytest -m mark6

def calculate_cumulative_score_for_candidates(candidate_keyword_phrases: KeyPhrases,
                                              word_scores: Mapping[str, float]) -> Optional[Mapping[KeyPhrase, float]]:
    """
    Calculate cumulative score for each candidate keyword phrase. Cumulative score for a keyword phrase equals to
    the sum of the word scores of each keyword phrase's constituent

    :param candidate_keyword_phrases: a list of candidate keyword phrases
    :param word_scores: word scores
    :return: a dictionary containing the mapping between the candidate keyword phrases and respective cumulative scores

    In case of corrupt input arguments, None is returned
    """
    if not isinstance(candidate_keyword_phrases, list) or candidate_keyword_phrases == []:
        return None
    if not isinstance(word_scores, dict) or word_scores == {}:
        return None

    phrase_score = {}
    for el in candidate_keyword_phrases:
        phrase_score[el] = 0
        for word in el:
            if word not in word_scores:
                return None
            phrase_score[el] = phrase_score[el] + word_scores[word]
    return phrase_score



def get_top_n(keyword_phrases_with_scores: Mapping[KeyPhrase, float],
              top_n: int,
              max_length: int) -> Optional[Sequence[str]]:
    """
    Extracts the top N keyword phrases based on their scores and lengths

    :param keyword_phrases_with_scores: a dictionary containing the keyword phrases and their cumulative scores
    :param top_n: the number of the keyword phrases to extract
    :param max_length: maximal length of a keyword phrase to be considered
    :return: a list of keyword phrases sorted by their scores in descending order

    In case of corrupt input arguments, None is returned
    """
    if not isinstance(keyword_phrases_with_scores, dict) or not keyword_phrases_with_scores:
        return None
    if not isinstance(top_n, int) or not top_n > 0:
        return None
    if not isinstance(max_length, int) or not max_length > 0:
        return None

    sort_phr = sorted(keyword_phrases_with_scores.keys(), key=lambda x: keyword_phrases_with_scores[x], reverse=True)
    top_list = []
    for el in sort_phr:
        if len(el) <= max_length:
            top_list.append(' '.join(el))
    return top_list[:top_n]


def extract_candidate_keyword_phrases_with_adjoining(candidate_keyword_phrases: KeyPhrases,
                                                     phrases: Sequence[str]) -> Optional[KeyPhrases]:
    """
    Extracts the adjoining keyword phrases from the candidate keywords Sequence and
    builds new candidate keywords containing stop words

    Adjoining keywords: such pairs that are found at least twice in the candidate keyword phrases list one after another

    To build a new keyword phrase the following is required:
        1. Find the first constituent of the adjoining keyword phrase in the phrases followed by:
            a stop word and the second constituent of the adjoining keyword phrase
        2. Combine these three pieces in the new candidate keyword phrase, i.e.:
            new_candidate_keyword = [first_constituent, stop_word, second_constituent]

    :param candidate_keyword_phrases: a list of candidate keyword phrases
    :param phrases: a list of phrases
    :return: a list containing the pairs of candidate keyword phrases that are found at least twice together

    In case of corrupt input arguments, None is returned
    """
    pass


def calculate_cumulative_score_for_candidates_with_stop_words(candidate_keyword_phrases: KeyPhrases,
                                                              word_scores: Mapping[str, float],
                                                              stop_words: Sequence[str]) \
        -> Optional[Mapping[KeyPhrase, float]]:
    """
    Calculate cumulative score for each candidate keyword phrase. Cumulative score for a keyword phrase equals to
    the sum of the word scores of each keyword phrase's constituent except for the stop words

    :param candidate_keyword_phrases: a list of candidate keyword phrases
    :param word_scores: word scores
    :param stop_words: a list of stop words
    :return: a dictionary containing the mapping between the candidate keyword phrases and respective cumulative scores

    In case of corrupt input arguments, None is returned
    """
    pass


def generate_stop_words(text: str, max_length: int) -> Optional[Sequence[str]]:
    """
    Generates the list of stop words from the given text

    :param text: the text
    :param max_length: maximum length (in characters) of an individual stop word
    :return: a list of stop words
    """
    pass


def load_stop_words(path: Path) -> Optional[Mapping[str, Sequence[str]]]:
    """
    Loads stop word lists from the file
    :param path: path to the file with stop word lists
    :return: a dictionary containing the language names and corresponding stop word lists
    """
    pass
