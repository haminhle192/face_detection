from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import time
import src.detection as detection
from scipy import misc

def main():
    start_time = time.time()
    detector = detection.Detection()
    for i in range(0, 1):
        img = misc.imread(os.path.dirname(__file__) + "/../data/" + str(i) + ".png")
        result = detector.find_faces(img)
        print(result[0].bounding_box)
    print("Detection time : %s" % str(time.time() - start_time))

if __name__ == '__main__':
    main()
