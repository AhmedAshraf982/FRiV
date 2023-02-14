import cv2
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN
import torch
from keras.models import load_model


device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(margin=20, post_process=False, device=device)

def get_embedding(model, face_pixels):
    # scale pixel values
    face_pixels = face_pixels.astype('float32')
    #standardize pixel values across channesl (global)
    mean, std = face_pixels.mean(), face_pixels.std()
    face_pixels = (face_pixels-mean)/std
    # transform face into one sample
    samples = np.expand_dims(face_pixels, axis=0)
    # make prediction to get embedding
    yhat = model.predict(samples)
    return yhat[0]

def findCosineDistance(source_representation, test_representation):
    a = np.matmul(np.transpose(source_representation), test_representation)
    b = np.sum(np.multiply(source_representation, source_representation))
    c = np.sum(np.multiply(test_representation, test_representation))
    return 1 - (a / (np.sqrt(b) * np.sqrt(c)))

def run():
    face_embedded_model = load_model("FaceNetModelData/facenet_keras.h5")
    data = np.load('FaceNetModelData/faceEmbeddings.npz')
    trainX, trainy,_,_ = data['arr_0'], data['arr_1'], data['arr_2'], data['arr_3']

    capture = cv2.VideoCapture("data/destination.mp4")
    cosine_similarity = None

    while True:
        _, frames = capture.read()
        if frames is None:
            break
        _ = np.asarray(frames)
        frames = Image.fromarray(cv2.cvtColor(frames, cv2.COLOR_BGR2RGB))
        boxes, _ = mtcnn.detect(frames)
        required_size=(160,160)
        name = None
        conf = 0.96
        epsilon = 0.35
        if _[0] is not None:
            for c, i in enumerate(_):
                if i > conf:
                    box = boxes[c]
                    f = frames.crop((box[0], box[1], box[2], box[3]))
                    image = f.resize(required_size)
                    data = get_embedding(face_embedded_model, np.asarray(image))
                    for i, d in enumerate(trainX):
                        cosine_similarity = findCosineDistance(data, d)
                        name = trainy[i]
                        if cosine_similarity < epsilon:
                            print(cosine_similarity, name)
                            if name == 'Dr. Atif':
                                return ["Dr. Atif"]
    return ["NONE"]
                        



                            





