import yaml
import pickle
from processing import DataManager, DataSetUtils, BasicManager

# Important note from Mina:
#     ----> function only works with ".data" files, which were in the original workflow already through the FE!


def get_probability(model, file_path):

    # load config file
    config_path = "files/config.yaml"
    with open(config_path, 'r') as ymlfile:
        config = yaml.load(ymlfile, Loader=yaml.FullLoader)

    # load embeddings
    embedding_path = "files/word.dict"
    embedding_dict = pickle.load(open(embedding_path, "rb"))

    # load datamanager and utils to turn features into embeddings for the model -> from processing.py!
    dataManager = DataManager()
    utils = DataSetUtils(config['max_feature_count'])
    input_dict, filename, all_labels = dataManager.save_record_contents(file_path, labels=None, single_file=True)
    matrix = utils.use_embeddings(filename, input_dict, embedding_dict)

    # calculating the probability for class malware
    pred_malware = model.predict_proba(matrix)
    # calculating the probabibility for class benign
    pred_benign = 1 - pred_malware
    # set both to float
    pred_malware = float(pred_malware)
    pred_benign = float(pred_benign)

    # save probabilities in a dict of type {"str": float}
    proba_dict = {"BENIGN": pred_benign, "MALWARE": pred_malware}

    # return probability results as dict
    return proba_dict


if __name__ == "__main__":
    get_probability("models/model", "tests/Malware.apk")
