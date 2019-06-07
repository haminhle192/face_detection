from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import time
import src.detection as detection
from scipy import misc
import tensorflow as tf
import cv2
import numpy as np

def main():
    # Testing detection images
    start_time = time.time()
    detector = detection.Detection()
    for i in range(0, 3):
        img = misc.imread(os.path.dirname(__file__) + "/../data/" + str(i) + ".png")
        result = detector.find_faces(img)
        print(result[0].bounding_box)
    print("Detection time : %s" % str(time.time() - start_time))

    # Testing resize tf and cv2 and scypi
    # img = misc.imread(os.path.dirname(__file__) + "/../data/0.png")
    # img = img[:, :, 0:3]
    #
    # img1 = cv2.resize(img, (160, 160), interpolation=cv2.INTER_LINEAR)
    #
    # img2 = misc.imresize(img, (160, 160), interp='bilinear')
    #
    # image_tf = tf.placeholder(tf.float32, shape=(None, None, None, 3))
    # resize_tf = tf.image.resize(image_tf, [160, 160], method=tf.image.ResizeMethod.BILINEAR)
    # img = np.array([img])
    # with tf.Session() as sess:
    #     img3 = sess.run(resize_tf, feed_dict={image_tf: img})
    #     img3 = img3[0]
    #
    # print(np.mean(np.equal(img1, img2)))
    # print(np.mean(np.equal(img2, img3)))
    # print(np.mean(np.equal(img3, img1)))

if __name__ == '__main__':
    main()
