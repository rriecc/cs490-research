from Resnet.resenet_model import Net
from preprocess import Preprocess


import numpy as np
import cv2
from matplotlib import pyplot as plt
import pandas as pd

# from __future__ import print_function
import torch  # pip3 install torch torchvision
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import torch.optim as optim
from torchsummary import summary  # pip3 install torch-summary

from torchvision import datasets, transforms

import os
import re
import pickle
import time
from tqdm import tqdm
import sys
from PIL import Image


d = {'0': 0, '1': 1, '10': 2, '11': 3, '12': 4, '13': 5, '14': 6, '15': 7, '16': 8, '17': 9, '18': 10, '2': 11, '3': 12, '4': 13, '5': 14, '6': 15, '7': 16, '8': 17, '9': 18}
m = {str(value):int(key) for key, value in d.items()}

def get_predicted_label(img, device, model):  # numpy array get from the previous
    with torch.no_grad():
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img, "RGB")
        data_transform = transforms.Compose([
            transforms.Resize((48, 48)),
            transforms.ToTensor(),
            transforms.Normalize((0.3394, 0.3081, 0.3161), (0.2753, 0.2631, 0.2685))
        ])
        data = data_transform(img)
        data = data.unsqueeze(0)
        data = data.to(device)
        output = model(data)
        pred = output.data.max(1, keepdim=True)[1]
        r = m[str(pred.item())]
        return r


def main():
    v_list = pickle.load(open("generated/V_list", "rb"))
    condition_list = pickle.load(open("generated/condition_list", "rb"))
    # v = np.array([[1.0000, 0.0595, -0.1429],
    #               [0.0588, 1.0000, -0.1324],
    #               [-0.2277, -0.0297, 1.0000]])
    epsilons = [0, 0.05, 0.1, 0.15, 0.2]
    '''
    # MNIST Test dataset and dataloader declaration
    test_loader = torch.utils.data.DataLoader(
    datasets.MNIST('../data', train=False, download=True, transform=transforms.Compose([
            transforms.ToTensor(),
            ])),
        batch_size=1, shuffle=True)
    '''

    use_cuda = True
    # Decide whether to use GPU or CPU

    # print("CUDA Available: ", torch.cuda.is_available())
    device = torch.device("cuda" if (use_cuda and torch.cuda.is_available()) else "cpu")

    # Load the pretrained model
    model = Net(l=512)
    model = model.to(device)
    model.load_state_dict(torch.load('/home/lu677/cs490/cs490-research/Resnet/epochs/model_150.pth'))

    model.eval()

    # g = os.walk(r"./Test")
    folder = "./Test/" + sys.argv[1]
    g = os.walk(folder)
    # df = pd.DataFrame(columns=["original image name", "actual label for processed",
    #                   "predicted label for processed", "v", "alpha", "condition number"])
    # total = 0
    # correct = 0
    dict_list = []
    for path, dir_list, file_list in g:
        for file_name in tqdm(file_list, desc=folder):
            path_file = os.path.join(path, file_name)
            original_label = path.split("/")[-1]
            for v, con_num in zip(v_list, condition_list):
                for alpha in epsilons:
                    x_new = Preprocess.preprocess_image_gaussian(path_file, v, alpha)
                    # y, x, y_new, x_new = Preprocess.preprocess_image(path_file, v, alpha)
                    # output_label_y = get_predicted_label(y, device, model)
                    # output_label_x = get_predicted_label(x, device, model)
                    # output_label_y_new = get_predicted_label(y_new, device, model)
                    output_label_x_new = get_predicted_label(x_new, device, model)
                    # prob = prob_list[0][int(original_label)].item()
                    # total += 1
                    # if (int(output_label_x_new) == 10):
                    #     correct += 1
                    # df.loc[len(df.index)] = [file_name, int(original_label), int(output_label_y), np.identity(3), 0]
                    # df.loc[len(df.index)] = [path_file, int(original_label), int(output_label_y_new), np.identity(3), alpha]
                    # df.loc[len(df.index)] = [file_name, int(original_label), int(output_label_x), v, 0]
                    dict_data = {
                        "original image name": path_file,
                        "actual label for processed": int(original_label),
                        "predicted label for processed": int(output_label_x_new),
                        "v": v,
                        "alpha": alpha,
                        "condition number": con_num,
                        # "probability": prob
                    }
                    dict_list.append(dict_data)
                    # df.loc[len(df.index)] = [path_file, int(original_label), int(output_label_x_new), v, alpha, con_num]
                # print(f'output_label_y: {output_label_y}')
                # print(f'output_label_x: {output_label_x}')
                # print(f'output_label_y_new: {output_label_y_new}')
                # print(f'output_label_x_new: {output_label_x_new}')
    df = pd.DataFrame.from_dict(dict_list)
    save_name = sys.argv[2] + "/unmerged_result/changed_v_result_" + sys.argv[1]
    pickle.dump(df, open(save_name, "wb"))
    # print(correct / total)


main()
