import cv2
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN
import torch
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
import albumentations as A
from keras import backend as K
import os



# initialize and configure gpu and Model for face Detection
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
mtcnn = MTCNN(margin=20, post_process=False, device=device)




transform = A.Compose([
    A.Blur(blur_limit=3),
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.2),
])

def extract_fast_face(filename, required_size=(224,224)):
    img = cv2.imread(filename)
    img_rgb = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    pixels = np.asarray(img_rgb)
    boxes, _ = mtcnn.detect(pixels)
    if _[0] is not None:
        if len(_) <= 2:
            for c, i in enumerate(_):
                if i > 0.95:
                    box = boxes[c]
                    f = img_rgb.crop((box[0], box[1], box[2], box[3]))
                    image = f.resize(required_size)
                    return np.asarray(image)
        else:
            return [None, "Multiple Faces is not allowed"]
    else:
        return [None, "No face detected"]

def get_embeddings(model,faces):
    # convert into an array of samples
    samples = faces.astype('float32')
    samples = np.expand_dims(samples, axis=0)
    # prepare the face for the model, e.g. center pixels
    samples = preprocess_input(samples, version=2)
    # perform prediction
    yhat = model.predict(samples)
    return yhat[0]

def findCosineDistance(source_representation, test_representation):
    a = np.matmul(np.transpose(source_representation), test_representation)
    b = np.sum(np.multiply(source_representation, source_representation))
    c = np.sum(np.multiply(test_representation, test_representation))
    return 1 - (a / (np.sqrt(b) * np.sqrt(c)))

def run(originalName:str, fps:int):
    isFind = False
    K.clear_session()
    model = VGGFace(model='resnet50', include_top=False, input_shape=(224, 224, 3), pooling='avg')
    # load data
    data = np.load('VGGFaceModelData/faceEmbeddings.npz')
    trainX, trainy = data['arr_0'], data['arr_1']
    capture = cv2.VideoCapture("data/start.mp4")
    cosine_similarity = None
    new_trainX = list()
    for i in range(0, len(trainy)):
        if trainy[i] == originalName:
            new_trainX.append(trainX[i])

    new_trainX = np.asarray(new_trainX)

    sec = 1
    min = 0
    while True:
        _, frames = capture.read()
        print(sec, min)
        if sec % (60*fps) == 0:
            min = min + 1 
            sec = 0
        sec = sec + 1
        if frames is None:
            break
        _ = np.asarray(frames)
        frames = Image.fromarray(cv2.cvtColor(frames, cv2.COLOR_BGR2RGB))
        boxes, _ = mtcnn.detect(frames)
        required_size=(224,224)
        name = None
        conf = 0.96
        epsilon = 0.35
        if _[0] is not None:
            for c, i in enumerate(_):
                if i > conf:
                    box = boxes[c]
                    f = frames.crop((box[0], box[1], box[2], box[3]))
                    image = f.resize(required_size)
                    data = get_embeddings(model, np.asarray(image))
                    for i, d in enumerate(new_trainX):
                        cosine_similarity = findCosineDistance(data, d)
                        # name = trainy[i]
                        if cosine_similarity < epsilon:
                            print(cosine_similarity, originalName)
                            # if name == originalName:
                            isFind = True
                            break
                if isFind:
                    break
        if isFind:
            break
    K.clear_session()
    if isFind:
        return [originalName, min]
    return [None]
                        

def  last(originalName:str, fps:int):
    isFind = False
    # initialize Model object
    K.clear_session()
    model = VGGFace(model='resnet50', include_top=False, input_shape=(224, 224, 3), pooling='avg')
    # load data
    data = np.load('VGGFaceModelData/faceEmbeddings.npz')
    trainX, trainy = data['arr_0'], data['arr_1']
    capture = cv2.VideoCapture("data/end.mp4")
    frames = capture.get(cv2.CAP_PROP_FRAME_COUNT)
    frame_index = frames-250
    cosine_similarity = None
    new_trainX = list()
    for i in range(0, len(trainy)):
        if trainy[i] == originalName:
            new_trainX.append(trainX[i])

    new_trainX = np.asarray(new_trainX)

    sec = 1
    min = 0
    # 5 seconds error
    while(frame_index!=0):
        capture.set(cv2.CAP_PROP_POS_FRAMES, int(frame_index))
        _, frames = capture.read()
        print(sec, min)
        if sec % (60*fps) == 0:
            print(min)
            min = min + 1 
            sec = 0
        sec = sec + 1
        if frames is None:
            break
        _ = np.asarray(frames)
        frames = Image.fromarray(cv2.cvtColor(frames, cv2.COLOR_BGR2RGB))
        boxes, _ = mtcnn.detect(frames)
        required_size=(224,224)
        name = None
        conf = 0.96
        epsilon = 0.35
        frame_index = frame_index - 1
        if _[0] is not None:
            for c, i in enumerate(_):
                if i > conf:
                    box = boxes[c]
                    f = frames.crop((box[0], box[1], box[2], box[3]))
                    image = f.resize(required_size)
                    data = get_embeddings(model, np.asarray(image))
                    for i, d in enumerate(new_trainX):
                        cosine_similarity = findCosineDistance(data, d)
                        # name = trainy[i]
                        if cosine_similarity < epsilon:
                            print(cosine_similarity, originalName)
                            # if name == originalName:
                            isFind = True
                            break
                if isFind:
                    break
        if isFind:
            break
    K.clear_session()
    if isFind:
        return [originalName, min]
    return [None]
                            



def train(path,Name:str):
    K1 = 90
    # load data
    data = np.load('VGGFaceModelData/faceEmbeddings.npz')
    trainX, trainy= data['arr_0'], data['arr_1']
    K.clear_session()
    # initialize Model object
    model = VGGFace(model='resnet50', include_top=False, input_shape=(224, 224, 3), pooling='avg')
    faces=[]
    newTrainX = list()
    arr = extract_fast_face(path)
    if len(arr) >= 2:
        for i in range(K1):
            transformed = transform(image=arr)
            faces.append(transformed['image'])
        labels = [Name for _ in range(len(faces))]
        for face_pixels in faces:
            embedding = get_embeddings(model,face_pixels)
            newTrainX.append(embedding)
        newTrainX = np.asarray(newTrainX)
        trainX = np.append(trainX, newTrainX,0)
        trainy = np.append(trainy, labels, 0)
        K.clear_session()
        np.savez_compressed('VGGFaceModelData/faceEmbeddings.npz', trainX, trainy)
        return [True]
    else:
        K.clear_session()
        return arr
    
    
    
    



