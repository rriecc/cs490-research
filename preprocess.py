import numpy as np
import cv2
from matplotlib import pyplot as plt
import pickle


class Preprocess():
    def im2double(im):
        min_val = np.min(im.ravel())
        max_val = np.max(im.ravel())
        out = (im.astype('float') - min_val) / (max_val - min_val)
        return out

    def preprocess_image_gaussian(img_filename, v, alpha):
        """
        processs the image with v matrix and normal noise
        input:
        img_filename: the path of an image in ppm format
        v matrix: 3 by 3 numpy array
        alpha: coefficient used for generating gaussian noise
        """
        # Comments on v matrix:
        # For some global color mixing matrix v, figure out what the input to the
        # projector should be, assuming zero illumination other than the projector.
        # Note : Not all scenes are possible for all v matrices. For some matrices
        # some scenes are not possible at all.
        if alpha == 0 and np.array_equal(v, np.identity(3)):
            return cv2.imread(img_filename)
        img = cv2.imread(img_filename)  # numpy array
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Captured Image - original #
        y = Preprocess.im2double(img)  # Convert to normalized floating point

        ss = y.shape  # (480,640,3)
        ylong = np.zeros((ss[0] * ss[1], 3))  # (307200,3)

        y1 = y[:, :, 0]  # (480,640)
        ylong[:, 0] = y1.flatten()
        y2 = y[:, :, 1]  # (480,640)
        ylong[:, 1] = y2.flatten()
        y3 = y[:, :, 2]  # (480,640)
        ylong[:, 2] = y3.flatten()

        # y1 = y[:, :, 2]  # (480,640)
        # ylong[:, 0] = y1.flatten()
        # y2 = y[:, :, 1]  # (480,640)
        # ylong[:, 1] = y2.flatten()
        # y3 = y[:, :, 0]  # (480,640)
        # ylong[:, 2] = y3.flatten()

        xlong = np.transpose(np.matmul(np.linalg.pinv(v), np.transpose(ylong)))
        xlong[xlong > 1] = 1
        xlong[xlong < 0] = 0

        # Projector input - original #
        # x = np.zeros(y.shape)
        # x[:, :, 0] = xlong[:, 0].reshape(ss[0], ss[1])
        # x[:, :, 1] = xlong[:, 1].reshape(ss[0], ss[1])
        # x[:, :, 2] = xlong[:, 2].reshape(ss[0], ss[1])

        # Now you can get any perturbed image y = v(x+\delta x)

        xlong_new = xlong + alpha * np.random.normal(0, 1, (xlong.shape[0], xlong.shape[1]))
        # Projector input - Attacked #
        # x_new = np.zeros(y.shape)
        # # x_new = np.zeros(x.shape)
        # x_new[:, :, 0] = xlong_new[:, 0].reshape(ss[0], ss[1])
        # x_new[:, :, 1] = xlong_new[:, 1].reshape(ss[0], ss[1])
        # x_new[:, :, 2] = xlong_new[:, 2].reshape(ss[0], ss[1])

        ylong_new = np.transpose(np.matmul(v, np.transpose(xlong_new)))
        # Captured Image - Attacked #
        y_new = np.zeros(y.shape)
        y_new[:, :, 0] = ylong_new[:, 0].reshape(ss[0], ss[1])
        y_new[:, :, 1] = ylong_new[:, 1].reshape(ss[0], ss[1])
        y_new[:, :, 2] = ylong_new[:, 2].reshape(ss[0], ss[1])

        # y = cv2.convertScaleAbs(y, alpha=(255.0))
        # x = cv2.convertScaleAbs(x, alpha=(255.0))
        y_new = cv2.convertScaleAbs(y_new, alpha=(255.0))
        # x_new = cv2.convertScaleAbs(x_new, alpha=(255.0))

        # x_new = cv2.cvtColor(x_new, cv2.COLOR_RGB2BGR)
        y_new = cv2.cvtColor(y_new, cv2.COLOR_RGB2BGR)
        # Captured original, Projector original, Captured attracked, Projector attacked
        return y_new
        # return y, x, y_new, x_new

    def preprocess_image_poisson(img_filename, v, alpha):
        """
            processs the image with v matrix and poisson noise
            input:
            img_filename: the path of an image in ppm format
            v matrix: 3 by 3 numpy array
            alpha: coefficient used for generating gaussian noise
            """
        if alpha == 0 and np.array_equal(v, np.identity(3)):
            return cv2.imread(img_filename)
        img = cv2.imread(img_filename)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        y = Preprocess.im2double(img)
        ss = y.shape
        ylong = np.zeros((ss[0] * ss[1], 3))
        y1 = y[:, :, 0]
        ylong[:, 0] = y1.flatten()
        y2 = y[:, :, 1]
        ylong[:, 1] = y2.flatten()
        y3 = y[:, :, 2]
        ylong[:, 2] = y3.flatten()
        xlong = np.transpose(np.matmul(np.linalg.pinv(v), np.transpose(ylong)))
        xlong[xlong > 1] = 1
        xlong[xlong < 0] = 0
        xlong_new = xlong + alpha * np.random.poisson(1, (xlong.shape[0], xlong.shape[1]))
        ylong_new = np.transpose(np.matmul(v, np.transpose(xlong_new)))
        y_new = np.zeros(y.shape)
        y_new[:, :, 0] = ylong_new[:, 0].reshape(ss[0], ss[1])
        y_new[:, :, 1] = ylong_new[:, 1].reshape(ss[0], ss[1])
        y_new[:, :, 2] = ylong_new[:, 2].reshape(ss[0], ss[1])
        y_new = cv2.convertScaleAbs(y_new, alpha=(255.0))
        y_new = cv2.cvtColor(y_new, cv2.COLOR_RGB2BGR)
        return y_new

    def preprocess_image_speckle(img_filename, v, alpha):
        """
            processs the image with v matrix and speckle noise
            input:
            img_filename: the path of an image in ppm format
            v matrix: 3 by 3 numpy array
            alpha: coefficient used for generating gaussian noise
            """
        if alpha == 0 and np.array_equal(v, np.identity(3)):
            return cv2.imread(img_filename)
        img = cv2.imread(img_filename)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        y = Preprocess.im2double(img)
        ss = y.shape
        ylong = np.zeros((ss[0] * ss[1], 3))
        y1 = y[:, :, 0]
        ylong[:, 0] = y1.flatten()
        y2 = y[:, :, 1]
        ylong[:, 1] = y2.flatten()
        y3 = y[:, :, 2]
        ylong[:, 2] = y3.flatten()
        xlong = np.transpose(np.matmul(np.linalg.pinv(v), np.transpose(ylong)))
        xlong[xlong > 1] = 1
        xlong[xlong < 0] = 0
        xlong_new = xlong + alpha * xlong * np.random.randn(xlong.shape[0], xlong.shape[1])
        ylong_new = np.transpose(np.matmul(v, np.transpose(xlong_new)))
        y_new = np.zeros(y.shape)
        y_new[:, :, 0] = ylong_new[:, 0].reshape(ss[0], ss[1])
        y_new[:, :, 1] = ylong_new[:, 1].reshape(ss[0], ss[1])
        y_new[:, :, 2] = ylong_new[:, 2].reshape(ss[0], ss[1])
        y_new = cv2.convertScaleAbs(y_new, alpha=(255.0))
        y_new = cv2.cvtColor(y_new, cv2.COLOR_RGB2BGR)
        return y_new

    def show_np_array_as_jpg(matrix, filepath):
        """store image to filepath

        Args:
            matrix (_type_): input matrix to be converted to a jpg image
            filepath (_type_): path to the saving directory
        """
        # filename = "/home/zhan3447/CS490_DSC/jpg/{actual_label}/v{v_number}/n{n_number}/{original_filename}"
        filename = f"{filepath}.jpg"
        cv2.imwrite(filename, matrix)  # does not work
        # plt.imshow(matrix)
        # plt.savefig(filename)

    def generate_v_matrix(num_condition=5, num_matrix=3, identity=True):
        """generate v matrix and condition number lists. It also saves two lists as files for future reference

        Args:
            num_condition (int, optional): number of condition numbers. Defaults to 10.
            num_matrix (int, optional): number of v matricies with each condition number. Defaults to 10.
            identity (bool, optional): true for adding an additional identity matrix. condition number for identity matrix will be -1. Defaults to True.

        Returns:
            V_list: v matrix list
            condition_list: condition number list
        """
        np.random.seed(0)
        eps_list = np.logspace(0, 2, num_condition)
        V_list = []
        condition_list = []
        for eps in eps_list:
            for i in range(0, num_matrix):
                a = np.random.normal(0, 1, size=(3, 3))  # random matrix
                C = eps
                u, s, v = np.linalg.svd(a, full_matrices=True)  # svd
                s = s[0] * (1 - ((C - 1) / C) * (s[0] - s) / (s[0] - s[-1]))  # linear stretch
                s = np.diag(s)
                V = u @ s @ v
                V_list.append(V)
                condition_list.append(eps)
        if identity:
            V_list.append(np.identity(3))
            condition_list.append(-1)
        return V_list, condition_list

    def generate_constant_v_matrix(num_condition=7, num_matrix=3, identity=True):
        """Only difference here with the generate_v_matrix is all v matricies are generated by the same random matrix

        Args:
            num_condition (int, optional): number of condition numbers. Defaults to 10.
            num_matrix (int, optional): number of v matricies with each condition number. Defaults to 10.
            identity (bool, optional): true for adding an additional identity matrix. condition number for identity matrix will be -1. Defaults to True.

        Returns:
            V_list: v matrix list
            condition_list: condition number list
        """
        np.random.seed(0)
        a = np.random.normal(0, 1, size=(3, 3))  # random matrix
        eps_list = np.logspace(0, 2, num_condition)
        V_list = []
        condition_list = []
        for eps in eps_list:
            for i in range(0, num_matrix):
                C = eps
                u, s, v = np.linalg.svd(a, full_matrices=True)  # svd
                s = s[0] * (1 - ((C - 1) / C) * (s[0] - s) / (s[0] - s[-1]))  # linear stretch
                s = np.diag(s)
                V = u @ s @ v
                V_list.append(V)
                condition_list.append(eps)
        if identity:
            # V_list.append(np.array([[0, 0, 1], [0, 1, 0], [1, 0, 0]]))
            V_list.append(np.identity(3))
            condition_list.append(-1)
        return V_list, condition_list

    def linearize_image(img_filename, v, alpha):
        """generate an one dimentional array from 3*32*32 matrix

        Args:
            img_filename (string): path to the image
            v (nparray): 3 by 3 v matrix
            alpha (float): noise strength

        Returns:
            nparray: an one dimentional array from 3*32*32 matrix
        """
        img = cv2.imread(img_filename)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        y = Preprocess.im2double(img)
        ss = y.shape
        ylong = np.zeros((ss[0] * ss[1], 3))
        y1 = y[:, :, 0]
        ylong[:, 0] = y1.flatten()
        y2 = y[:, :, 1]
        ylong[:, 1] = y2.flatten()
        y3 = y[:, :, 2]
        ylong[:, 2] = y3.flatten()
        xlong = np.transpose(np.matmul(np.linalg.pinv(v), np.transpose(ylong)))
        xlong[xlong > 1] = 1
        xlong[xlong < 0] = 0
        xlong_new = xlong + alpha * np.random.normal(0, 1, (xlong.shape[0], xlong.shape[1]))
        ylong_new = np.transpose(np.matmul(v, np.transpose(xlong_new)))
        y_new = np.zeros(y.shape)
        y_new[:, :, 0] = ylong_new[:, 0].reshape(ss[0], ss[1])
        y_new[:, :, 1] = ylong_new[:, 1].reshape(ss[0], ss[1])
        y_new[:, :, 2] = ylong_new[:, 2].reshape(ss[0], ss[1])
        y_new = cv2.convertScaleAbs(y_new, alpha=(255.0))
        y_new = cv2.cvtColor(y_new, cv2.COLOR_RGB2BGR)
        # Load the image
        image = np.zeros((3, 32, 32))  # (rgb, width, height) guess:)

        # add global.py code

        # temp = cv.imread('ISO_400.png')
        temp = y_new
        temp = cv2.resize(temp, (32, 32))  # resize the input image
        temp = temp[0:32, 0:32, :]

        temp = temp.astype('float64') / 255
        temp = temp[:, :, [2, 1, 0]]

        image[0, :, :] = temp[:, :, 0]
        image[1, :, :] = temp[:, :, 1]
        image[2, :, :] = temp[:, :, 2]
        return image.flatten()
