import cv2
import cvlib as cv
import numpy as np
import streamlit as st
from PIL import Image, ImageEnhance
from scipy.interpolate import UnivariateSpline


def face_detect(our_image):
    new_image = np.array(our_image.convert('RGB'))
    faces, confidences = cv.detect_face(new_image)
    for face, conf in zip(faces, confidences):
        (startX, startY) = face[0], face[1]
        (endX, endY) = face[2], face[3]
        cv2.rectangle(new_image, (startX, startY),
                      (endX, endY), (0, 255, 0), 2)
    return new_image


def gender_detect(our_img):
    img = np.array(our_img.convert('RGB'))
    face, conf = cv.detect_face(img)
    padding = 20
    for f in face:
        (startX, startY) = max(0, f[0]-padding), max(0, f[1]-padding)
        (endX, endY) = min(img.shape[1]-1, f[2] +
                           padding), min(img.shape[0]-1, f[3]+padding)

        # draw rectangle over face
        cv2.rectangle(img, (startX, startY), (endX, endY), (0, 255, 0), 2)

        face_crop = np.copy(img[startY:endY, startX:endX])

        # apply gender detection
        (label, confidence) = cv.detect_gender(face_crop)

        idx = np.argmax(confidence)
        label = label[idx]

        label = "{}: {:.2f}%".format(label, confidence[idx] * 100)

        Y = startY - 10 if startY > 20 else startY + 10

        cv2.putText(img, label, (startX, Y),  cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 255, 0), 2)
    return img


def object_detect(our_image):
    image = np.array(our_image.convert('RGB'))
    bbox, label, conf = cv.detect_common_objects(image)
    return cv.object_detection.draw_bbox(image, bbox, label, conf)


def LookupTable(x, y):
    spline = UnivariateSpline(x, y)
    return spline(range(256))


def cannize_image(our_image):
    new_img = np.array(our_image.convert('RGB'))
    img = cv2.cvtColor(new_img, 1)
    img = cv2.GaussianBlur(img, (11, 11), 0)
    return cv2.Canny(img, 100, 150)


def sepia_effect(our_image):
    # converting to float to prevent loss
    img_sepia = np.array(our_image.convert('RGB'))
    img_sepia = cv2.transform(img_sepia, np.matrix([[0.272, 0.534, 0.131],
                                                    [0.349, 0.686, 0.168],
                                                    [0.393, 0.769, 0.189]]))  # multipying image with special sepia matrix
    # normalizing values greater than 255 to 255
    img_sepia[np.where(img_sepia > 255)] = 255
    img_sepia = np.array(img_sepia, dtype=np.uint8)
    return img_sepia


def winter_effect(our_image):
    img = np.array(our_image.convert('RGB'))
    increaseLookupTable = LookupTable([0, 64, 128, 256], [0, 80, 160, 256])
    decreaseLookupTable = LookupTable([0, 64, 128, 256], [0, 50, 100, 256])
    blue_channel, green_channel, red_channel = cv2.split(img)
    red_channel = cv2.LUT(red_channel, increaseLookupTable).astype(np.uint8)
    blue_channel = cv2.LUT(blue_channel, decreaseLookupTable).astype(np.uint8)
    return cv2.merge((blue_channel, green_channel, red_channel))


def summer_effect(our_image):
    img = np.array(our_image.convert('RGB'))
    increaseLookupTable = LookupTable([0, 64, 128, 256], [0, 80, 160, 256])
    decreaseLookupTable = LookupTable([0, 64, 128, 256], [0, 50, 100, 256])
    blue_channel, green_channel, red_channel = cv2.split(img)
    red_channel = cv2.LUT(red_channel, decreaseLookupTable).astype(np.uint8)
    blue_channel = cv2.LUT(blue_channel, increaseLookupTable).astype(np.uint8)
    return cv2.merge((blue_channel, green_channel, red_channel))


def sketch(our_image):
    # reading image in raw array format
    image = np.array(our_image.convert("RGB"))
    grey_img = cv2.cvtColor(
        image, cv2.COLOR_RGB2GRAY
    )  # Using cvtColor method to Convert RGB to Gray colorscale
    # Using bitwise_not method to invert the greyscale `image
    invert = cv2.bitwise_not(grey_img)
    blur = cv2.GaussianBlur(
        invert, (21, 21), 0
    )  # Using GaussianBlur method to blur the inverted image
    invertedblur = cv2.bitwise_not(
        blur
    )  # Again using bitwise_not method to invert the blurred image
    return cv2.divide(
        grey_img, invertedblur, scale=256.0
    )  # performing bit-wise division between the grayscale image and the inverted-blurred image to obtain sketch image.


def main():
    st.header("Image Detector & Convertor App")
    st.text("Build with Streamlit, OpenCV and CVlib")
    activities = ["Detection", "Filters"]
    choice = st.sidebar.selectbox("Select Activity", activities)
    image_file = st.file_uploader(
        "Upload Image", type=['jpg', 'png', 'jpeg'])

    if choice == 'Detection':
        task = ["Face Detection", "Gender Detection",
                "Object Detection"]

        feature_choice = st.sidebar.selectbox("Find Features", task)

        if image_file is not None:
            our_image = Image.open(image_file)
            st.text("Original Image")
            st.image(our_image)

            if st.button("Process"):

                if feature_choice == "Face Detection":
                    result_img = face_detect(our_image)
                    st.image(result_img)

                elif feature_choice == "Gender Detection":
                    result_img = gender_detect(our_image)
                    st.image(result_img)

                elif feature_choice == "Object Detection":
                    result_img = object_detect(our_image)
                    st.image(result_img)

    elif choice == 'Filters':
        enhance_type = st.sidebar.radio(
            "Enhance Type", ["Gray-Scale", "Pencil Effect",
                             "Sepia Effect", "Invert Effect",
                             "Summer Effect", "Winter Effect",
                             "Contrast", "Brightness", "Blurring"])

        if image_file is not None:
            our_image = Image.open(image_file)
            st.text("Original Image")
            st.image(our_image)

            if enhance_type == 'Gray-Scale':
                st.text("Filtered Image")
                new_img = np.array(our_image.convert('RGB'))
                img = cv2.cvtColor(new_img, 1)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                st.image(gray)

            elif enhance_type == 'Cannize Effect':
                st.text("Filtered image")
                result_img = cannize_image(our_image)
                st.image(result_img)

            elif enhance_type == 'Pencil Effect':
                st.text("Filtered Image")
                result_img = sketch(our_image)
                st.image(result_img)

            elif enhance_type == 'Sepia Effect':
                st.text("Filtered Image")
                result_img = sepia_effect(our_image)
                st.image(result_img)

            elif enhance_type == 'Summer Effect':
                st.text("Filtered Image")
                result_img = summer_effect(our_image)
                st.image(result_img)

            elif enhance_type == 'Winter Effect':
                st.text("Filtered Image")
                result_img = winter_effect(our_image)
                st.image(result_img)

            elif enhance_type == 'Invert Effect':
                st.text("Filtered Image")
                image = np.array(our_image.convert('RGB'))
                result_img = cv2.bitwise_not(image)
                st.image(result_img)

            elif enhance_type == 'Contrast':
                st.text("Filtered Image")
                c_rate = st.sidebar.slider("Contrast", 0.5, 3.5, 3.00)
                enhancer = ImageEnhance.Contrast(our_image)
                img_output = enhancer.enhance(c_rate)
                st.image(img_output)

            elif enhance_type == 'Brightness':
                st.text("Filtered Image")
                c_rate = st.sidebar.slider("Brightness", 0.5, 3.5, 2.50)
                enhancer = ImageEnhance.Brightness(our_image)
                img_output = enhancer.enhance(c_rate)
                st.image(img_output)

            elif enhance_type == 'Blurring':
                st.text("Filtered Image")
                new_img = np.array(our_image.convert('RGB'))
                blur_rate = st.sidebar.slider("Blurring", 0.5, 3.5, 1.75)
                img = cv2.cvtColor(new_img, 1)
                blur_img = cv2.GaussianBlur(img, (11, 11), blur_rate)
                st.image(blur_img)


if __name__ == '__main__':
    main()
