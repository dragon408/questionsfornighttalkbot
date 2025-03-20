import pytesseract
from PIL import Image
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def ocr_image(image_path, lang='eng'):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img, lang=lang)
    return text


def questions_list(text):
    questions = re.split(r'®|©|@|\d+', text)

    questions = [q.strip() for q in questions if q.strip()]
    return questions


#image_path = 'photo_2025-03-19_16-08-54.jpg'
#language = 'ukr'

#text = ocr_image(image_path, lang=language)
#print(text)

#questions = re.split(r'®|©|@|\d+', text)

#questions = [q.strip() for q in questions if q.strip()]
#print(questions)

