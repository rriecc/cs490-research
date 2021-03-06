from model import TrafficNet
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


def get_predicted_label(img, device, model):  # numpy array get from the previous
    # Load the image
    image = np.zeros((3, 32, 32))  # (rgb, width, height) guess:)

    # add global.py code

    # temp = cv.imread('ISO_400.png')
    temp = img
    temp = cv2.resize(temp, (32, 32))  # resize the input image
    temp = temp[0:32, 0:32, :]

    temp = temp.astype('float64') / 255
    temp = temp[:, :, [2, 1, 0]]

    image[0, :, :] = temp[:, :, 0]
    image[1, :, :] = temp[:, :, 1]
    image[2, :, :] = temp[:, :, 2]

    # Convert the image to tensor
    data = torch.tensor(image)
    data = data.float()
    data = data.to(device)

    # Normalize the image
    data[0, :, :] = (data[0, :, :] - 0.485) / 0.229
    data[1, :, :] = (data[1, :, :] - 0.456) / 0.224
    data[2, :, :] = (data[2, :, :] - 0.406) / 0.225

    data = data.unsqueeze(0)

    data.requires_grad = False

    # Classify the image
    output = model(data)
    # print(torch.argmax(output))

    # Print output
    return torch.argmax(output).item(), torch.exp(output)  # predicted label for the image and probability


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
    model = TrafficNet()
    model = model.to(device)
    model.load_state_dict(torch.load('Traffic_sign_new/Checkpoints/epoch_999.pth'))

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
                    x_new = Preprocess.preprocess_image_speckle(path_file, v, alpha)
                    # y, x, y_new, x_new = Preprocess.preprocess_image(path_file, v, alpha)
                    # output_label_y = get_predicted_label(y, device, model)
                    # output_label_x = get_predicted_label(x, device, model)
                    # output_label_y_new = get_predicted_label(y_new, device, model)
                    output_label_x_new, prob_list = get_predicted_label(x_new, device, model)
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
