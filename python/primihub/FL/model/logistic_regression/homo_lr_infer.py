import pickle
import numpy as np
import pandas as pd
import primihub as ph
import logging


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def predict_prob(weights, bias, x):
    prob = sigmoid(np.dot(x, weights)+bias)
    return prob


def predict(model, x):
    bias = model[-1]
    weights = model[:-1]
    prob = predict_prob(weights, bias, x)
    return (prob > 0.5).astype('int')


class ModelInfer:
    def __init__(self, model_path, input_path, model_type="Homo-LR") -> None:
        model_f = open(model_path, 'rb')
        self.model = np.array(pickle.load(model_f))
        self.arr = pd.read_csv(input_path, header=None).values
        self.type = model_type

    def infer(self):
        if self.type == "Homo-LR":
            preds = predict(self.model, self.arr)
        return preds


@ph.context.function(role='host', protocol='lr-infer', datasets=['breast_1'], port='8020', task_type="lr-regression")
def run_infer():
    logging.info("Start machine learning inferring.")
    predict_file_path = ph.context.Context.get_predict_file_path()
    model_file_path = ph.context.Context.get_model_file_path()

    mli = ModelInfer(model_file_path, predict_file_path)

    preds = mli.infer()

    logging.info(
        f"Finish machine learning inferring. And the result is {preds}")
