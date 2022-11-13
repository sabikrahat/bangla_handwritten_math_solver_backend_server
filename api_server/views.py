
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from keras.models import load_model
from tkinter import *
from tkinter.ttk import *
import cv2
import imutils
from imutils.contours import sort_contours
import numpy as np
import matplotlib.pyplot as plt
import base64
import io
import PIL.Image as Image


# Create your views here.
@api_view(['GET', 'POST'])
def check(request):
    response_data = {'status': True,
                     'message': 'Connected Successfully...!', 'data': None, }
    if request.method == 'GET':
        return Response(response_data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'POST'])
def equation_solve(request):
    if request.method == 'GET':
        response_data = {
            'status': True, 'message': 'Equation Solve Function executed without any data...!', 'data': None, }
        return Response(response_data, status=status.HTTP_200_OK)

    elif request.method == 'POST':
        # print("::::::::::::::::::::::::::", request.data)
        try:
            img_equ = request.data['img_equ']
            img_ans = request.data['img_ans']

            res = get_equation_and_solve(img_equ, img_ans)

            response_data = {"success": True,
                             "message": "Successfully solved the equation",
                             "result": res}

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            response_data = {"success": False,
                             "message": "Data not found..! " + str(e),
                             "result": None}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


def get_equation_and_solve(img_equ, img_ans):
    # print(":::::::: Equation ::::::::", img_equ)
    img_equ = Image.open(io.BytesIO(base64.b64decode(img_equ)))
    # img_equ.show()
    img_equ.save('outputs/equ/1_equ_canvas_from_app_.png')
    print(":::::::: Equation Image Saved ::::::::")

    # print(":::::::: Answer ::::::::", img_ans)
    img_ans = Image.open(io.BytesIO(base64.b64decode(img_ans)))
    # img_ans.show()
    img_ans.save('outputs/ans/1_ans_canvas_from_app_.png')
    print(":::::::: Answer Image Saved ::::::::")

    res_equ = get_predict_equation(
        'outputs/equ/1_equ_canvas_from_app_.png', 'equ')
    print(":::::::: Equation Predicted ::::::::", res_equ)

    res_ans = get_predict_equation(
        'outputs/ans/1_ans_canvas_from_app_.png', 'ans')
    print(":::::::: Answer Predicted ::::::::", res_ans)

    return res_equ + '_backend_server_' + res_ans

# Function for solving the prediction


def get_predict_equation(path, name):
    print('::::: Solving the equation...' + path + ':::::')
    model = load_model('trained_model/math_symbol_and_digit_recognition.h5')
    chars = []

    img = cv2.imread(path)

    ##### removing noise #####
    # convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #
    (_, blackAndWhiteImage) = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    # blur
    blur = cv2.GaussianBlur(blackAndWhiteImage, (0, 0), sigmaX=33, sigmaY=33)
    # divide
    divide = cv2.divide(blackAndWhiteImage, blur, scale=255)
    # otsu threshold
    thresh = cv2.threshold(
        divide, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    # apply morphology
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    # write result to disk
    cv2.imwrite("outputs/" + name + "/2_gray_noise_remove.jpg", gray)
    cv2.imwrite("outputs/" + name +
                "/3_black_and_white_noise_remove.jpg", blackAndWhiteImage)
    cv2.imwrite("outputs/" + name + "/4_blur_noise_remove.jpg", blur)
    cv2.imwrite("outputs/" + name + "/5_divide_noise_remove.jpg", divide)
    cv2.imwrite("outputs/" + name + "/6_thresh_noise_remove.jpg", thresh)
    cv2.imwrite("outputs/" + name + "/7_morph_noise_remove.jpg", morph)

    # img = thresh
    # img = cv2.imread("output/5_thresh_noise_remove.jpg")
    # img = cv2.imread("output/6_morph_noise_remove.jpg")

    # img = cv2.resize(img, (self.canvas_width, self.canvas_height))
    img_gray = gray
    # img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    print("::::: I\'m here :::::")
    edged = cv2.Canny(img_gray, 30, 150)
    cv2.imwrite("outputs/" + name + "/8_all_canny_detect.jpg", edged)
    contours = cv2.findContours(
        edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(contours)
    print('Number of contours found: ', len(contours))
    contours = sort_contours(contours, method="left-to-right")[0]
    labels = ['0', '1', '2', '3', '4', '5', '6',
              '7', '8', '9', 'add', 'div', 'mul', 'sub']

    for i, c in enumerate(contours):
        print('Processing the image...: ', str(i+1))
        (x, y, w, h) = cv2.boundingRect(c)
        print('x: ', x, 'y: ', y, 'w: ', w, 'h: ', h)
        if x > 0 and y > 0 and w > 20:  # cheaking weather any garbage value detecting
            roi = img[y:y+h, x:x+w]
            roi = img_gray[y:y+h, x:x+w]
            thresh = cv2.threshold(
                roi, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
            (th, tw) = thresh.shape
            if tw > th:
                thresh = imutils.resize(thresh, width=32)
            if th > tw:
                thresh = imutils.resize(thresh, height=32)
            (th, tw) = thresh.shape
            dx = int(max(0, 32 - tw)/2.0)
            dy = int(max(0, 32 - th) / 2.0)
            padded = cv2.copyMakeBorder(
                thresh, top=dy, bottom=dy, left=dx, right=dx, borderType=cv2.BORDER_CONSTANT, value=(0, 0, 0))
            padded = cv2.resize(padded, (32, 32))
            padded = np.array(padded)
            padded = padded/255.
            padded = np.expand_dims(padded, axis=0)
            padded = np.expand_dims(padded, axis=-1)
            pred = model.predict(padded)
            pred = np.argmax(pred, axis=1)
            label = labels[pred[0]]
            print('>>>>The {} no word is : {}'.format(i, label))
            chars.append(label)
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
            cv2.putText(img, label, (x-5, y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))

    plt.figure(figsize=(10, 10))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cv2.imwrite("outputs/" + name + "/9_system_prediction.jpg", img)
    # plt.imshow(img)
    plt.savefig("outputs/" + name + "/10_with_axis.png")
    plt.axis('off')
    plt.savefig("outputs/" + name + "/10_without_axis.png")

    try:
        e = ''
        print('Equation: {}', chars)
        for i in chars:
            if i == 'add':
                e += '+'
            elif i == 'sub':
                e += '-'
            elif i == 'mul':
                e += '*'
            elif i == 'div':
                e += '/'
            else:
                e += i
        v = eval(e)
        print('V Result: {}', v)
        print('E Result: {}', e)

        print('Value of the expression {} : {}'.format(e, v))
        return '{}={}'.format(e, v)

    except Exception as e:
        print('Error: {}'.format(e))
        return 'Error: {}'.format(e)
