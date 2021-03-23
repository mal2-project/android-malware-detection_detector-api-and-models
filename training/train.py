import yaml
import time
import argparse
import numpy as np
import pickle

# Comment out for local training
# import tensorflow as tf
# tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

from tensorflow import keras
from keras import optimizers
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers.embeddings import Embedding
from keras.callbacks import CSVLogger

import processing, verify
from processing import *

# Uncomment for GPU training
#sess = tf.Session(config=tf.ConfigProto(log_device_placement=True))
#tf.test.is_gpu_available(
#    cuda_only=False, min_cuda_compute_capability=None
#)



def main(gooddir, maldir, config):
    with open(config, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    dm = DataManager()
    du = DataSetUtils(cfg['max_feature_count'])
    bm = BasicManager()
    
    # Load feature files
    start = time.time()
    input_dict, all_filenames, all_labels = dm.save_record_contents([gooddir, maldir], cfg['labels'])
    print("Loaded feature files in: " + bm.time_it(start))

    # Get list of file names and labels for [train, val, and test] datasets
    start = time.time()
    filenames_train, filenames_val, filenames_test, labels_train, labels_val, labels_test = du.train_test_split(all_filenames, all_labels)
    print("Got file names and labels in: " + bm.time_it(start))
        
    # Create list of embedding sequences for each file. E.g. 
    # first element: <embeddings for 1 word>, <embeddings for 2 word>...
    start = time.time()
    train_matrix, validation_matrix, vocab_size, word_to_id_dict = du.create_embeddings([filenames_train, filenames_val], input_dict)
    test_matrix = du.use_embeddings(filenames_test, input_dict, word_to_id_dict)
    print("Finished embeddings in: " + bm.time_it(start))

    # Modelling #################################
    start = time.time()

    # define the model
    k_model = Sequential()
    k_model.add(Embedding(vocab_size, cfg['embedding_vector_len'], input_length=cfg['max_feature_count']))
    k_model.add(Flatten(input_shape=(len(filenames_train), cfg['max_feature_count'])))
    k_model.add(Dense(cfg['dense_units1'], activation='sigmoid'))
    k_model.add(Dense(cfg['dense_units2'], activation='sigmoid'))
    k_model.add(Dense(1, activation='sigmoid'))

    # compile the model
    adam = optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.0)
    k_model.compile(optimizer=adam, loss='binary_crossentropy', metrics=['acc'])

    # summarize the model
    #print(k_model.summary())

    validation_matrix_with_labels = (validation_matrix, labels_val)

    # log the loss per epoch in a csv file
    csv_logger = CSVLogger("files/log.csv", append=True, separator=";")
    # fit the model
    k_model.fit(train_matrix, labels_train, epochs=5, verbose=1, validation_split=0.5, validation_data=validation_matrix_with_labels, callbacks=[csv_logger])
    print("Training time: " + bm.time_it(start))

    # evaluate the model
    #pred_train = np.ndarray.flatten(k_model.predict_classes(train_matrix))
    pred_train = np.ndarray.flatten(k_model.predict(train_matrix))
    table = bm.metrics(labels_train, pred_train, None, "train")

    #pred_val = np.ndarray.flatten(k_model.predict_classes(validation_matrix))
    print(validation_matrix)
    pred_val = np.ndarray.flatten(k_model.predict(validation_matrix))
    print(pred_val)
    table = bm.metrics(labels_val, pred_val, table, "validation")

    #pred_test = np.ndarray.flatten(k_model.predict_classes(test_matrix))
    pred_test = np.ndarray.flatten(k_model.predict(test_matrix))
    table = bm.metrics(labels_test, pred_test, table, "test")

    print(table)
    print("All plots, models, etc. will be saved in the 'files' directory")

    bm.roc_prob_plot(labels_test, pred_test) 
    print("ROC probability plot was saved as 'roc_prob_plot.png'")
    bm.roc_plot(labels_test, pred_test)
    print("ROC plot was saved as 'roc_plot.png'")

    # Mina: changed it to normal model since h5. models cannot be re-trained with the current setup!
    k_model.save('files/model')
    pickle.dump(word_to_id_dict, open("files/word.dict", "wb"))
    print("Embedding was saved as 'word.dict'")



def check_nn_classifier():
    return "ok"


if __name__ == "__main__":

    Args = argparse.ArgumentParser(description="Training of Malware Finding Model")
    Args.add_argument("-g", "--goodware", help="Path to directory containing safe apps")
    Args.add_argument("-m", "--malware", help="Path to directory containing malware apps")
    Args.add_argument("-c", "--config", default="files/config.yaml", help="Path to config file")
    args = Args.parse_args()

    main(args.goodware, args.malware, args.config)

    
