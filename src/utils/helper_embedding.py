import pandas as pd
import numpy as np
import swifter  # noqa: F401


def reshape_df(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    """
    Reshapes dataframe so it is in a 'nice'/relatively 'tidy' format

    :param df: Dataframe to reshape.
    :param col_name: Name to give the embedding column.
    :return: Reshaped dataframe for easy storing/using.
    """
    try:
        df = df.transpose()
        df[col_name] = df.values.tolist()
        df = df.rename_axis('word').reset_index()
        return df[['word', col_name]]
    except Exception as error:
        print(f"Cause: {error}")


def calculate_cosine_similarity(a: list, b: list) -> float:
    """
    Computes the cosine-similarity of a word with each word in a dataframe.

    :param a: List of first vector to compute cosine-similarity.
    :param b: List of second vector to compute cosine-similarity.
    :return: Float of the cosine-similarity between a and b.
    """
    try:
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return dot_product / (norm_a * norm_b)
    except ValueError:
        print('Error!'
              'Possible reason is that the two vectors are not of the same length.\n'
              'Please pass in vectors of the same length.')
        raise
    except TypeError:
        print('Error!'
              'Possible reason is that at least one of the vectors has None in.\n'
              'Please pass in vectors with int or floats in them only.')
        raise


def extract_cosine_similarity(df: pd.DataFrame, word: str, col_embedding: str) -> pd.Series:
    """
    Computes the cosine-similarity for a given word against a column of word-embeddings.

    :param df: Dataframe to use.
    :param word: String to get cosine-similarity of.
    :param col_embedding: String of word-embedding column in dataframe.
    :return: Series of each string and its associated cosine-similarity score to word.
    """
    # get embedding associated with word
    df = df.set_index(keys='word')
    word_embedding = df.at[word, col_embedding]

    # compute cosine-similarity of selected word against all other embeddings
    cosine_similarity = df[col_embedding].swifter.apply(calculate_cosine_similarity,
                                                        b=word_embedding)

    return cosine_similarity


def get_embedding_synonyms(df: pd.DataFrame,
                           word: str,
                           col_embedding: str,
                           threshold: float) -> list:
    """
    Get the set of synonyms of a word according whether it is above a cosine-similarity threshold.

    :param df: Dataframe to use.
    :param word: String to get cosine-similarity of.
    :param col_embedding: String of word-embedding column in dataframe.
    :param threshold: Float of the cosine-similarity score that a word must exceed to be
                      considered a synonym.
    :return: List of synonyms that are above a threshold for similarity.
    """
    cosine_similarity = extract_cosine_similarity(df=df,
                                                  word=word,
                                                  col_embedding=col_embedding)

    # remove word from Series (this will have cosine-similarity of 1)
    cosine_similarity = cosine_similarity.drop(labels=word)

    # turn Series to DataFrame
    cosine_similarity = cosine_similarity.reset_index()

    # filter to values above threshold
    cosine_similarity = cosine_similarity[cosine_similarity[col_embedding] >= threshold]

    # get words with cosine-similarity above threshold
    synonyms = cosine_similarity['word'].tolist()

    return synonyms
