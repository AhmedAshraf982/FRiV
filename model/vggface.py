import cv2
import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN
import torch
from keras_vggface.vggface import VGGFace
from keras_vggface.utils import preprocess_input
import albumentations as A
from keras import backend as K


CONF = 0.96
EPSILON = 0.45
JUMP = 8

class FaceRecognition:
    def __init__(self) -> None:
        # initialize and configure gpu and Model for face Detection
        self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
        self.mtcnn = MTCNN(margin=20, post_process=False, device=self.device)
        self.transform = A.Compose([
                    A.Blur(blur_limit=3),
                    A.HorizontalFlip(p=0.5),
                    A.RandomBrightnessContrast(p=0.2),
                ])
        self.model = VGGFace(model='resnet50', include_top=False, input_shape=(224, 224, 3), pooling='avg')
        # load data
        data = np.load('VGGFaceModelData/faceEmbeddings.npz')
        self.trainX, self.trainy = data['arr_0'], data['arr_1']
        self.new_trainX = list()


    def extract_fast_face(self, filename, required_size=(224,224)):
        img = cv2.imread(filename)
        img_rgb = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        pixels = np.asarray(img_rgb)
        boxes, _ = self.mtcnn.detect(pixels)
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
        
    def get_embeddings(self,faces):
        # convert into an array of samples
        samples = faces.astype('float32')
        samples = np.expand_dims(samples, axis=0)
        # prepare the face for the model, e.g. center pixels
        samples = preprocess_input(samples, version=2)
        # perform prediction
        yhat = self.model.predict(samples)
        return yhat[0]
    



    def findCosineDistance(self,source_representation, test_representation):
        a = np.matmul(np.transpose(source_representation), test_representation)
        b = np.sum(np.multiply(source_representation, source_representation))
        c = np.sum(np.multiply(test_representation, test_representation))
        return 1 - (a / (np.sqrt(b) * np.sqrt(c)))




    def run(self,originalName:str, fps:int, duration:float):
        threshold = fps*60
        cosine_similarity = None
        self.new_trainX = list()
        sec = 1
        min = 0
        total_frames = duration * fps
        frames = 0
        frame_index = 1

        K.clear_session()

        capture = cv2.VideoCapture("data/start.mp4")
        
        
        for i in range(0, len(self.trainy)):
            if self.trainy[i] == originalName:
                self.new_trainX.append(self.trainX[i])
        self.new_trainX = np.asarray(self.new_trainX)
        
        if len(self.new_trainX) == 0:
            return f"Faculty {originalName} Face Data is not exist in our database."

        print(len(self.new_trainX), originalName)

        while frame_index<total_frames:
            capture.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            _, frames = capture.read()
            print(sec, min)
            if sec > threshold:
                min = min + 1 
                sec = 1
            sec = sec + JUMP
            if frames is None:
                break
            _ = np.asarray(frames)
            frames = Image.fromarray(cv2.cvtColor(frames, cv2.COLOR_BGR2RGB))
            boxes, _ = self.mtcnn.detect(frames)
            required_size=(224,224)
            
            frame_index = frame_index + JUMP
            if _[0] is not None:
                for c, i in enumerate(_):
                    if i > CONF:
                        box = boxes[c]
                        f = frames.crop((box[0], box[1], box[2], box[3]))
                        image = f.resize(required_size)
                        data = self.get_embeddings(np.asarray(image))
                        for d in range(0,len(self.new_trainX)-1,2):
                            cosine_similarity = self.findCosineDistance(data, self.new_trainX[d])
                            
                            # name = trainy[i]
                            if cosine_similarity < EPSILON:
                                print(cosine_similarity, originalName)
                                return [originalName, min]
        K.clear_session()
        return [None]




    def train(self,path,Name:str):
        K1 = 90

        K.clear_session()
        faces=[]
        newTrainX = list()
        arr = self.extract_fast_face(path)
        if len(arr) >= 2:
            for i in range(K1):
                transformed = self.transform(image=arr)
                faces.append(transformed['image'])
            labels = [Name for _ in range(len(faces))]
            for face_pixels in faces:
                embedding = self.get_embeddings(face_pixels)
                newTrainX.append(embedding)
            newTrainX = np.asarray(newTrainX)
            self.trainX = np.append(self.trainX, newTrainX,0)
            self.trainy = np.append(self.trainy, labels, 0)
            K.clear_session()
            np.savez_compressed('VGGFaceModelData/faceEmbeddings.npz', self.trainX, self.trainy)
            return [True]
        else:
            K.clear_session()
            return arr
        

    


    def  last(self,originalName:str, fps:int):
        threshold = (fps*60)
        cosine_similarity = None
        sec = 1
        min = 0
        K.clear_session()
        
        capture = cv2.VideoCapture("data/end.mp4")
        frames = capture.get(cv2.CAP_PROP_FRAME_COUNT)
        frame_index = frames-100

        # 5 seconds error
        while frame_index!=0:
            capture.set(cv2.CAP_PROP_POS_FRAMES, int(frame_index))
            _, frames = capture.read()
            if sec > threshold:
                min = min + 1 
                sec = 1
            sec = sec + JUMP
            if frames is None:
                break
            _ = np.asarray(frames)
            frames = Image.fromarray(cv2.cvtColor(frames, cv2.COLOR_BGR2RGB))
            boxes, _ = self.mtcnn.detect(frames)
            required_size=(224,224)
           
            frame_index = frame_index - JUMP
            if _[0] is not None:
                for c, i in enumerate(_):
                    if i > CONF:
                        box = boxes[c]
                        f = frames.crop((box[0], box[1], box[2], box[3]))
                        image = f.resize(required_size)
                        data = self.get_embeddings(np.asarray(image))
                        for d in range(0,len(self.new_trainX)-1,2):
                            cosine_similarity = self.findCosineDistance(data, self.new_trainX[d])
                            # name = trainy[i]
                            if cosine_similarity < EPSILON:
                                print(cosine_similarity, originalName)
                                return [originalName, min]          

        K.clear_session()
        return [None]














                        


                            




    
    
    
    



