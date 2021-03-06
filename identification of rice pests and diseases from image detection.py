import cv2
import os
import numpy as np
import glob
import mahotas as mt
from matplotlib import pyplot as plt
from sklearn import preprocessing
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import plot_confusion_matrix, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, plot_roc_curve


def mean(image):
    img_arr = image.reshape(-1)
    img_arr = np.array(img_arr)
    m = img_arr[img_arr != 0].mean()
    return m/255


def std_deviation(image):
    img_arr = image.reshape(-1)
    img_arr = np.array(img_arr)
    s = img_arr[img_arr != 0].std()
    return s/255


train_imgs = []
train_labels = []
features = []
for directory_path in glob.glob("images/train/*"):
    label = directory_path.split("\\")[-1]
    for img_path in glob.glob(os.path.join(directory_path, "*.jpg")):
        img = cv2.imread(img_path)
        img = cv2.resize(img, (128, 128))
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        binary = cv2.threshold(
            gray, 70, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        r, g, b = img[:, :, 0], img[:, :, 1], img[:, :, 2]
        h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]
        l, a, b = lab[:, :, 0], lab[:, :, 1], lab[:, :, 2]

        contours, hierarchy = cv2.findContours(
            binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cnt = contours[0]
        M = cv2.moments(cnt)
        area = cv2.contourArea(cnt)
        perimeter = cv2.arcLength(cnt, True)

        textures = mt.features.haralick(gray)
        ht_mean = textures.mean(axis=0)
        contrast = ht_mean[1]
        correlation = ht_mean[2]
        homogeneity = ht_mean[4]
        entropy = ht_mean[8]

        ftr = np.hstack([mean(r), mean(b), mean(g), mean(h), mean(s), mean(v), mean(l), mean(a), mean(b), std_deviation(
            r), std_deviation(b), std_deviation(g), area, perimeter, contrast, correlation, homogeneity, entropy])
        train_imgs.append(img)
        train_labels.append(label)
        features.append(ftr)

train_imgs = np.array(train_imgs)
train_labels = np.array(train_labels)
features = np.array(features)
print(features)

le = preprocessing.LabelEncoder()
le.fit(train_labels)
train_labels_encoded = le.transform(train_labels)
print(train_labels_encoded)

scaler = preprocessing.MinMaxScaler(feature_range=(0, 1))
rescaled_features = scaler.fit_transform(features)
print(rescaled_features)

(x_train, x_test, y_train, y_test) = train_test_split(
    rescaled_features, train_labels_encoded, test_size=0.3, random_state=42)

RF_model = RandomForestClassifier(n_estimators=50, random_state=42)
RF_model.fit(x_train, y_train)
prediction_RF = RF_model.predict(x_test)
#prediction_RF = le.inverse_transform(prediction_RF)
accuracy = accuracy_score(y_test, prediction_RF)
print('Accuracy: %f' % accuracy)
