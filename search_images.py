import zipfile
from PIL import Image
import pytesseract
import cv2 as cv
import math
import numpy as np




# Global list of dictionaries to store the processed data gained from the given zip file
list_page_infos = []




# searches given string keyWord in text portion of pages included in zip_imgs
# and displays face pictures of the related page if search is successful
def search_img(zip_imgs, keyWord):
    for page in list_page_infos:
        if keyWord in page['txt']:
            print('Results found in file {}'.format(page['name']))
            if len(page['faces']) == 0:
                print('But there were no faces in that file!')
            else:
                display(page['contact_sheet'])
        


# Creates a contact sheet from given list of images
def create_conSheet(img_list):    
    if len(img_list) == 0:
        return None
    img_width, img_height = (110, 110)
    n_col = 5
    n_row = int(math.ceil(len(img_list) / n_col))
    first_img = img_list[0]
    contact_sheet = Image.new(first_img.mode, (img_width * n_col, img_height * n_row))
    x, y = (0, 0)
    for im in img_list:
        im.thumbnail((img_width, img_height))
        contact_sheet.paste(im, (x, y))
        if x+img_width == contact_sheet.width:
            x = 0
            y += img_height
        else:
            x += img_width
                
    return contact_sheet


# Iterates through each page image in the given zip folder and
# stores the name, text, face images related to each page in the
# global list - list_page_infos
def preprocess_zip(zip_imgs):
    new_img = 'new_img.png'
    # loading the face detection classifier
    face_cascade = cv.CascadeClassifier('readonly/haarcascade_frontalface_default.xml')
    with zipfile.ZipFile(zip_imgs) as imgs:
        for img_name in imgs.namelist():
            page_info = {'name': img_name, 'txt': '', 'faces': [], 'contact_sheet': None}
            img = Image.open(imgs.open(img_name))
            img.save(new_img)
            txt = pytesseract.image_to_string(new_img)
            page_info['txt'] = txt
            img_cv = cv.imread(new_img)
            gray = cv.cvtColor(img_cv, cv.COLOR_BGR2GRAY)
            recs = face_cascade.detectMultiScale(gray, 1.35)
            pil_img = Image.open(new_img)
            pil_img = pil_img.convert('RGB')
            for rec in recs:
                face_box = (rec[0], rec[1], rec[0]+rec[2], rec[1]+rec[3])
                page_info['faces'].append (pil_img.crop(face_box))
            
            page_info['contact_sheet'] = create_conSheet(page_info['faces'])
            list_page_infos.append(page_info)
            


###################################################################################################
# testing the search_img() function with "readonly/images.zip" provided in Jupyter notebook
zip_imgs = 'readonly/images.zip'


preprocess_zip(zip_imgs)


keyWord = 'Christopher'
print('You can enter 0 to finish the search process.')


while True:
    keyWord = input("Please, Enter the keyword: ")
    if keyWord == '0':
        break


    print('Searching for {} ...'.format(keyWord))
    search_img(zip_imgs, keyWord)


###################################################################################################
