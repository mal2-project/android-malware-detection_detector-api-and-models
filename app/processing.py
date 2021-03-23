import os
import time
from datetime import timedelta

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, precision_score, recall_score, roc_curve

from prettytable import PrettyTable
import matplotlib.pyplot as plt

class DataManager:

    @staticmethod
    def read_records(path):

        # encoding='Latin-1' works
        with open(path, errors='replace') as f:
            content = f.readlines()
        # to remove whitespace characters like `\n` at the end of each line
        content = [x.strip() for x in content]

        return content

    @staticmethod
    def save_record_contents(all_paths, labels, single_file=False):
        input_dict = {}
        all_filenames = []
        all_labels = []

        if single_file:
            filename = all_paths
            res = DataManager.read_records(filename)
            input_dict[filename.split('/')[-1]] = res
            all_labels = None
            all_filenames.append(filename.split('/')[-1])
        else:
            for p in range(len(all_paths)):
                c=0
                for (dirpath, dirnames, filenames) in os.walk(all_paths[p]):
                    for filename in filenames:
                        if filename.endswith(".data"):
                            # analyse content
                            res = DataManager.read_records(dirpath + "/" + filename)
                            input_dict[filename] = res
                            c+=1
                            all_filenames.append(filename)

                if labels == "infer from array":
                    all_labels.extend([p] * c)
                elif labels in ['0', '1']:
                    all_labels = [int(labels)] * c
                elif labels is None:
                    all_labels = None

        return input_dict, all_filenames, all_labels
    

class DataSetUtils:
    
    def __init__(self, max_feature_count):

        self.max_feature_count = max_feature_count
    
    def train_test_split(self, all_filenames, all_labels):

        # split apks into test and training dfset
        filenames_train_and_val, filenames_test, labels_train_and_val, labels_test = train_test_split(all_filenames, all_labels, test_size=0.10, random_state=42)

        # split apks from training set into training and validation set
        filenames_train, filenames_val, labels_train, labels_val = train_test_split(filenames_train_and_val, labels_train_and_val, test_size=0.10, random_state=42)
        
        return [filenames_train, filenames_val, filenames_test, labels_train, labels_val, labels_test]

    
    def create_embeddings(self, train_val_filenames, input_dict):

        word_to_id_dict = {}
        feature_count = 0
        train_val_matrices = [None]*2
        # go through train(val) sections of the filename list
        for d in range(len(train_val_filenames)):
            # get how many files are in train(val)
            w = len(train_val_filenames[d])
            # initialize a matrix that is [# files in train(val)] x [# of max features we are counting]
            train_val_matrices[d]=[[0 for x in range(self.max_feature_count)] for y in range(w)]
            count_w = 0
            # go through each file in train(val)
            for filename in train_val_filenames[d]:
                count_h = 0
                # go through entire content of filename in train(val) one line (word_feature) at a time
                for word_feature in input_dict[filename]:
                    # if line is already in word_to_id_dict then the feature_count is reset
                    # if line is not in word_to_id_dict then new feature_count is saved to it
                    if word_feature not in word_to_id_dict:
                        word_to_id_dict[word_feature] = feature_count
                        feature_count = feature_count + 1
                    
                    # if line # is less than the max feature count AND
                    # file # is less than number of files in train(val) THEN
                    # train(val) matrix is populated at feature x file location with feature_count number
                    if count_h < self.max_feature_count and count_w < w:
                        train_val_matrices[d][count_w][count_h] = word_to_id_dict[word_feature]
                    count_h = count_h + 1
                count_w = count_w + 1

        np_train_matrix = np.array(train_val_matrices[0])
        np_val_matrix = np.array(train_val_matrices[1])
        
        return np_train_matrix, np_val_matrix, feature_count, word_to_id_dict

    
    def use_embeddings(self, test_dataset, input_dict, word_to_id_dict):
        
        w = len(test_dataset)
        test_matrix = [[0 for x in range(self.max_feature_count)] for y in range(w)]
        count_w = 0
        for filename in test_dataset:
            count_h = 0
            for word_feature in input_dict[filename]:
                if count_h < self.max_feature_count and count_w < w:
                    value = 0
                    if word_feature in word_to_id_dict:
                        test_matrix[count_w][count_h] = word_to_id_dict[word_feature]
                    count_h = count_h + 1
            count_w = count_w + 1

        np_test_matrix = np.array(test_matrix)
        
        return np_test_matrix


class BasicManager:

    #def get_id_vector_by_word_vector(self, word_vector):
    #    id_vector = []
    #    for word in word_vector:
    #        if word in word_to_id_dict:
    #            id_vector.append(word_to_id_dict[word])
    #    return id_vector


    def time_it(self, start):

        elapsed = time.time() - start

        return str(timedelta(seconds=elapsed))
    

    def metrics(self, true_y, float_predictions, x, dataset):

        if x is None:
            x = PrettyTable()
            x.field_names = ["dataset", "accuracy", "precision", "recall", "tn", "fp", "fn", "tp", "total samples"]

        predictions = [0 if p < 0.5 else 1 for p in float_predictions]
        acc = accuracy_score(true_y, predictions)
        pre = precision_score(true_y, predictions)
        rec = recall_score(true_y, predictions)
        if list(true_y) == predictions and sum(true_y) > 0:
            tn, fp, fn, tp = 0, 0, 0, len(true_y)
        elif list(true_y) == predictions and sum(true_y) == 0:
            tn, fp, fn, tp = len(true_y), 0, 0, 0
        else:
            tn, fp, fn, tp = confusion_matrix(true_y, predictions).ravel()

        x.add_row([dataset, acc, pre, rec, tn, fp, fn, tp, tn+fp+fn+tp])
        with open('files/metrics.txt', 'w') as f:
            f.write(x.get_string())

        return x

    def roc_prob_plot(self, true_y, predictions):
        preds1 = []
        preds0 = []
        for i in range(len(true_y)):
            if true_y[i] == 0:
                preds0.append(predictions[i])
            else:
                preds1.append(predictions[i])
        f = plt.figure()
        plt.hist(preds1, bins=50, log=True, density=True, color="r", alpha=0.5, label="Fraudulent sites")
        plt.hist(preds0, bins=50, log=True, density=True, color="g", alpha=0.5, label="Certified sites")
        plt.axvline(x=0.5, color='black', linestyle='--', linewidth=0.7)
        plt.ylabel("Normalized Count")
        plt.xlabel("Prediction")
        plt.legend(loc='upper center')
        plt.savefig("files/roc_prob_plot.png")
        plt.close(f)

    def roc_plot(self, true_y, predictions):
        fpr, tpr, thresholds = roc_curve(true_y, predictions)
        f = plt.figure()
        plt.ylabel("TPR")
        plt.xlabel("FPR")
        plt.plot(fpr, tpr, color="r", linestyle='dotted', markersize=3)
        plt.savefig("files/roc_plot.png")
        plt.close(f)
