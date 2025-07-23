# -*- coding: utf-8 -*-

# pip install opencv-python==4.9.0.80
# pip install numpy==1.26
# pip install tensorflow tflite_runtime matplotlib keras scipy

# Check versions: python -m pip list | grep -E 'numpy|opencv'

import cv2  
import numpy as np
import tflite_runtime.interpreter as tflite
#import tflite
import time
import operator
import os
import scipy


def main():
    # Get current directory and set it as root directory
    root_directory = os.path.dirname(os.path.abspath(__file__))
    # get parent directory
    root_directory = os.path.dirname(root_directory)
    print(f"Root Directory: {root_directory}")
    file_w_path = root_directory + '/data/model/vc_model.tflite'
    if not os.path.exists(file_w_path):
        print(f"File {file_w_path} do not exits, exits")
        return False
    interpreter = tflite.Interpreter(model_path=file_w_path)
    labels = ["divide" , "eight","five","four","min","mul","nine","one","plus","seven","six","three","two"]
    integer_labels = [operator.floordiv ,8 , 5 , 4 , operator.sub, operator.mul , 9, 1 ,operator.add , 7 ,6 ,3,2]
    input_details   = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    video_feed = cv2.VideoCapture(0)
    if not video_feed.isOpened():
        print("Error: Could not open video feed")
        return False
    video_feed.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    video_feed.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    current_prediction  = 0
    previous_prediction = 0
    prediction_array = [14]
    equation_array = []

    while True:
        ok,frame = video_feed.read()
        if not ok:
            print("Failed to read frame from camera")
            break
        gray_scaled = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        # Draw rectangle to about center and about 30% of height
        #print(f"Frame Shape: {gray_scaled.shape}")
        box_height = int(gray_scaled.shape[0] * 0.3)
        box_top_left = (int(gray_scaled.shape[1] * 0.5)-box_height//2, int(gray_scaled.shape[0] * 0.5)-box_height//2)
        box_bottom_right = (int(gray_scaled.shape[1] * 0.5)+box_height//2, int(gray_scaled.shape[0] * 0.5)+box_height//2)
        cv2.rectangle(gray_scaled, box_top_left, box_bottom_right, (255,0,0), 2)
        #cv2.rectangle(gray_scaled, (350,100),(550,300), (255,0,0), 2)
        # sqaure_region = gray_scaled[100:300,350:550]
        sqaure_region = gray_scaled[box_top_left[1]:box_bottom_right[1],box_top_left[0]:box_bottom_right[0]]
        cv2.imshow("Full Frame", gray_scaled)
        cv2.waitKey(1)
        circle_location = cv2.HoughCircles(sqaure_region , cv2.HOUGH_GRADIENT,1.2,20)

        if circle_location is not None:
            circle_location = np.round(circle_location[0, :]).astype("int")

            for i in circle_location:
                center_x = i[0];center_y = i[1];radius = i[2]
                x=center_x - radius ;y=center_y - radius
                h=2*radius;w=2*radius
            if y>0 and x>0:

                cropped_circle = sqaure_region[y:y+h , x:x+h]
                cropped_circle_resize = cv2.resize(cropped_circle , (500,500))
                roi = cropped_circle_resize[90:410 , 90:410]

                input_image = cv2.resize(roi,(128,128))
                input_image = np.expand_dims(input_image,axis=2)
                input_image = np.expand_dims(input_image,axis=0)
                input_image = input_image.astype(np.float32)
#

                interpreter.allocate_tensors()
                interpreter.set_tensor(input_details[0]['index'] , input_image)
                interpreter.invoke()
                current_prediction = interpreter.get_tensor(output_details[0]['index'])
                current_prediction = np.argmax(current_prediction)

                if current_prediction == previous_prediction:
                    if( prediction_array[len(prediction_array)-1] != current_prediction):
                        prediction_array.append(current_prediction)
                        equation_array.append(labels[current_prediction])

                    else:
                        print("Skipping Same Entry")

                previous_prediction = current_prediction

                print("Prediction Array ", prediction_array)
                print("Equation Array ", equation_array)

                if (len(prediction_array) >=4):
                    ele_a     = integer_labels[prediction_array[1]]
                    operation = integer_labels[prediction_array[2]]
                    ele_b     = integer_labels[prediction_array[3]]

                    print(" Equation Result -> " , operation(ele_a,ele_b))


                cv2.imshow("Region of Interest", roi)
                cv2.waitKey(1)


if __name__ == '__main__':
    main()



