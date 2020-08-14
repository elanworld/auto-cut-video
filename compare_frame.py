import cv2
import numpy as np


class CompareFrame:
    def calculate(self, img1, img2):

        hist1 = cv2.calcHist([img1], [0], None, [256], [0.0, 255.0])
        hist2 = cv2.calcHist([img2], [0], None, [256], [0.0, 255.0])
        degree = 0
        for i in range(len(hist1)):
            if hist1[i] != hist2[i]:
                degree = degree + (
                        1 - abs(hist1[i] - hist2[i]) / max(hist1[i], hist2[i])
                )
            else:
                degree = degree + 1
        degree = degree / len(hist1)
        return degree

    def classify_hist_with_split(self, img1, img2):

        sub_img1 = cv2.split(img1)
        sub_img2 = cv2.split(img2)
        sub_data = 0
        for im1, im2 in zip(sub_img1, sub_img2):
            sub_data += self.calculate(im1, im2)
        sub_data = sub_data / 3
        print(sub_data)
        if sub_data > 0.7:
            return True
        else:
            return False

    def classify_aHash(self, image1, image2, boundary=19):

        image1 = cv2.resize(image1, (8, 8))
        image2 = cv2.resize(image2, (8, 8))
        gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)
        hash1 = getHash(gray1)
        hash2 = getHash(gray2)
        return self.Hamming_distance(hash1, hash2)

    def classify_pHash(self, image1, image2):
        image1 = cv2.resize(image1, (32, 32))
        image2 = cv2.resize(image2, (32, 32))
        gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

        dct1 = cv2.dct(np.float32(gray1))
        dct2 = cv2.dct(np.float32(gray2))

        dct1_roi = dct1[0:8, 0:8]
        dct2_roi = dct2[0:8, 0:8]
        hash1 = self.getHash(dct1_roi)
        hash2 = self.getHash(dct2_roi)
        return self.Hamming_distance(hash1, hash2)

    def getHash(self, image):

        avreage = np.mean(image)
        hash = []
        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                if image[i, j] > avreage:
                    hash.append(1)
                else:
                    hash.append(0)
        return hash

    def Hamming_distance(self, hash1, hash2):
        num = 0
        for index in range(len(hash1)):
            if hash1[index] != hash2[index]:
                num += 1
        print(num)
        return num
