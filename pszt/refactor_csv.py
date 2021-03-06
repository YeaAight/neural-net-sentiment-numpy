import csv
import numpy as np
import re


def refactor(csv_path, new_csv_path):
    """ Extract sentiment and text into new csv file.

    Args:
        csv_path: File path to the csv file.
        new_csv_path: File path to the new csv file.
    """

    # Open the original csv file.
    with open(csv_path, encoding="ISO-8859-1") as csv_file:
        # Create reader object used to iterate over every row in the file.
        csv_content = csv.reader(csv_file, delimiter=',')

        # Create/replace and write new csv file.
        with open(new_csv_path, mode='w', encoding='utf-8', newline='') as new_csv_path:
            # Create writer object used to write rows in new csv file.
            csv_writer = csv.writer(new_csv_path, delimiter=',')

            for row in csv_content:
                # Write every 'sentiment' and 'text' to new row.
                if row[5] != 'not_relevant':
                    csv_writer.writerow([row[5], row[11]])


def vectorize_dataset(csv_path, x_train_path, y_train_path,
                      ignore_words=None, tfidf=False):
    """ Vectorize dataset using bag-of-words algorithm and one-hot encoding

    Args:
        csv_path: Path to csv file with dataset.
        x_train_path: Path to file to save x_train array.
        y_train_path: Path to file to save y_train array.
        ignore_words: List of words to not include in x_train.
    """
    # List of words in the dataset.
    dataset_words = []

    # List of sentences in the dataset.
    dataset_sentences = []

    # List of sentiments in the dataset.
    dataset_sentiments = []

    # List of words to be skipped.
    if ignore_words is None:
        ignore_words = []

    # count = 0
    # Open csv dataset.
    with open(csv_path) as csv_file:
        # Create reader object used to iterate over every row in the file.
        csv_content = csv.reader(csv_file, delimiter=',')

        # Helper variable to skip first row which contains labels of csv.
        first_row = True

        for row in csv_content:

            # Skip first row of csv file.
            if first_row:
                first_row = False
                continue

            # Replace every non-alphanumeric character with space
            # and split into list.
            words = re.sub("\W", " ",  row[1]).split()

            # Clean words.
            words_cleaned = [w.lower() for w in words if w.lower() not in ignore_words]

            # Change sentiments to one-hot vector.
            one_hot = _create_onehot(row[0])

            dataset_words.extend(words_cleaned)
            dataset_sentences.append(words_cleaned)
            dataset_sentiments.append(one_hot)

    # Transform into set to avoid duplicates and create sorted list.
    dataset_words = sorted(list(set(dataset_words)))

    len_dataset_words = len(dataset_words)

    # Perform bag of words on the dataset.
    for i, sentence in enumerate(dataset_sentences):
        # Numpy array that will represent every sentence with frequencies
        # of used words.
        bag = np.zeros(len_dataset_words)

        for word_s in sentence:
            for j, word_w in enumerate(dataset_words):
                if word_w == word_s:
                    bag[j] += 1

        # bag = np.reshape(bag, (len_dataset_words, 1))
        dataset_sentences[i] = bag

    # Transform dataset_sentences list into numpy array.
    x_train = np.array(dataset_sentences)

    # Create numpy array of y_train.
    y_train = np.array(dataset_sentiments)

    # Wheter to change current bag-of-words model to TFIDF.
    if tfidf:
        # Calculate TF(Term Frequency) for every sentence.
        for i in range(len(x_train)):
            # Calculate sum of occurings in sentence.
            sum_of_terms = np.sum(x_train[i])

            # Divide x_train element-wise by sum_of_terms.
            x_train[i] /= sum_of_terms

        # Number of documents in the corpus.
        D = x_train.shape[0]

        # IDF (Inverse Document Frequency) vector populated with zeros.
        # Number of documents where the term t apppears
        total_occurings = np.zeros(x_train.shape[1])

        for sentence in x_train:
            # Find indexes of non zero values.
            non_zero_indexes = np.nonzero(sentence)

            # Append vector d at non_zero_indexes resulting in number
            # of documents where term t appears.
            for idx in non_zero_indexes:
                total_occurings[idx] += 1

        # Calculate final idf vector.
        idf = np.divide(D, total_occurings)
        idf = np.log(idf)

        # Multiply TF by IDF.
        x_train *= idf

    # Save numpy arrays to disk.
    np.save(x_train_path, x_train)
    np.save(y_train_path, y_train)


def _create_onehot(labels):
    one_hot = np.zeros(3)

    if int(labels) == 1:
        one_hot[0] = 1
    elif int(labels) == 3:
        one_hot[1] = 1
    elif int(labels) == 5:
        one_hot[2] = 1

    return one_hot
