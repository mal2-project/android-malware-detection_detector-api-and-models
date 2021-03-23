#
# This module supports generation of features files
# for each related APK 
#

import yaml
import time
import argparse
import numpy as np
import pickle
#import tensorflow as tf
#tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
from processing import *
#from nn_model_service.processing import *


def main(gooddir, maldir, featuresdir, config):
    with open(config, 'r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

    dm = DataManager()
    du = DataSetUtils(cfg['max_feature_count'])
    bm = BasicManager()

    # Load feature files
    start = time.time()
    input_dict, all_filenames, all_labels = dm.save_record_contents([gooddir, maldir], cfg['labels'])
    print("Loaded feature files in: " + bm.time_it(start))

    # Get list of features, file names and labels for provided datasets

    for idx, filename in enumerate(input_dict):
        #print("idx=",idx,"filename=",filename,"all_filenames=",all_filenames[idx],"all_labels=",all_labels[idx])
        if all_labels[idx] == 1:
            #print("add malware idx", idx)
            with open(featuresdir+'/'+filename+'.txt','w') as ff:
                for feature in input_dict[filename]:
                    ff.write("%s\n" % feature)
    print("Created feature files in: " + bm.time_it(start))


if __name__ == "__main__":

    Args = argparse.ArgumentParser(description="Training of Malware Finding Model")
    Args.add_argument("-g", "--goodware", default="/home/mal2/data/adware/data_files_test", help="Path to directory containing safe apps")
    Args.add_argument("-m", "--malware", default="/home/mal2/data/malware/data_files_test/", help="Path to directory containing malware apps")
    Args.add_argument("-f", "--features", default="/home/mal2/drebin_FE/", help="Path to directory containing extracted features")
    Args.add_argument("-c", "--config", default="files/config.yaml", help="Path to config file")
    args = Args.parse_args()

    main(args.goodware, args.malware, args.features, args.config)
