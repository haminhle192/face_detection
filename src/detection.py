from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf
import align.detect_face as detect_face
import cv2
import io
from PIL import Image

class Face:
    def __init__(self):
        self.bounding_box = None
        self.data_image = None

class Detection:
    # face detection parameters
    minsize = 20  # minimum size of face
    threshold = [0.6, 0.7, 0.7]  # three steps's threshold
    factor = 0.709  # scale factor

    gpu_memory_fraction = 0.3

    def __init__(self, face_crop_size=160, face_crop_margin=32):
        self.pnet, self.rnet, self.onet = self._setup_mtcnn()
        self.face_crop_size = face_crop_size
        self.face_crop_margin = face_crop_margin

    def _setup_mtcnn(self):
        print('Loading detection model ...')
        with tf.Graph().as_default():
            gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=self.gpu_memory_fraction)
            sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
            with sess.as_default():
                return detect_face.create_mtcnn(sess, None)

    def find_faces(self, image):
        image = image[:, :, 0:3]
        faces = []

        bounding_boxes, _ = detect_face.detect_face(image, self.minsize, self.pnet, self.rnet, self.onet,
                                                    self.threshold, self.factor)
        for bb in bounding_boxes:
            face = Face()
            face.bounding_box = np.zeros(4, dtype=np.int32)
            img_size = np.asarray(image.shape)[0:2]
            face.bounding_box[0] = np.maximum(bb[0] - self.face_crop_margin / 2, 0)
            face.bounding_box[1] = np.maximum(bb[1] - self.face_crop_margin / 2, 0)
            face.bounding_box[2] = np.minimum(bb[2] + self.face_crop_margin / 2, img_size[1])
            face.bounding_box[3] = np.minimum(bb[3] + self.face_crop_margin / 2, img_size[0])
            cropped = image[face.bounding_box[1]:face.bounding_box[3], face.bounding_box[0]:face.bounding_box[2], :]
            # face.image = misc.imresize(cropped, (self.face_crop_size, self.face_crop_size), interp='bilinear')
            # face.image = cv2.resize(cropped, (self.face_crop_size, self.face_crop_size), interpolation=cv2.INTER_LINEAR)
            face.data_image = self.encode_jpeg(cropped)
            faces.append(face)
        return faces


    def encode_jpeg(arr):
        assert arr.dtype == np.uint8
         # simulate multi-channel array for single channel arrays
        while arr.ndim < 4:
            arr = arr[..., np.newaxis] # add channels to end of x,y,z
        reshaped = arr.T
        reshaped = np.moveaxis(reshaped, 0, -1)
        reshaped = reshaped.reshape(reshaped.shape[0], reshaped.shape[1] * reshaped.shape[2], reshaped.shape[3])
        if reshaped.shape[2] == 1:
            img = Image.fromarray(reshaped[:,:,0], mode='L')
        elif reshaped.shape[2] == 3:
            img = Image.fromarray(reshaped, mode='RGB')
        else:
            raise ValueError("Number of image channels should be 1 or 3. Got: {}".format(arr.shape[3]))
        stream = io.BytesIO()
        img.save(stream, "JPEG")
        return stream