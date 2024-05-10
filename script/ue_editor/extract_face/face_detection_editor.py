import os

import cv2

folder = 'editor/'

list_names = ["ada", "amelia", "aoi", "bernice", "bes", "bryan",
              "chandra", "cooper", "danielle", "dax", "dhruv", "emanuel",
              "emory", "erno", "ettore", "farrukh", "fei", "gavin",
              "glenda", "hadley", "hana", "hudson", "irene", "jesse",
              "kai", "keiji", "kellan", "kendra", "kioko", "koda",
              "kristopher", "kwame", "lena", "lexi", "lucian", "malika",
              "maria", "myles", "nasim", "natalia", "neema", "omar",
              "orla", "oskar", "payton", "pia", "robin", "rosemary",
              "roux", "rowan", "sadhil", "seneca", "skye", "sook_ja",
              "stephane", "taro", "tori", "trey", "valerie", "vincent",
              "vivan", "wallace", "yuri", "zakari", "zeva", "zhen"]

for k, filename in enumerate(os.listdir(folder)):
    filepath = os.path.join(folder, filename)
    img = cv2.imread(filepath)
    face_classifier = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    )
    face = face_classifier.detectMultiScale(
        img, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
    )
    
    bbox = []
    for (x, y, w, h) in face:
        center_x = x + w//2
        center_y = y + h//2
        if center_x < 900 and center_y > 500 and w <= 120:
            p0 = (center_x-50, center_y-60)
            p1 = (center_x+ 50, center_y + 60)
            bbox.append((p0, p1))

    
    if len(bbox) == 4:
        sorted(bbox, key=lambda x:x[1])

        profile_0, profile_1 = bbox[0], bbox[1]
        if profile_0[0] > profile_1[0]:
            profile_0 = bbox[1]
            profile_1 = bbox[0]
        profile_2, profile_3 = bbox[2], bbox[3]
        if profile_2[0] > profile_3[0]:
            profile_2 = bbox[3]
            profile_3 = bbox[2]
        
        profiles = [profile_0, profile_1, profile_2, profile_3]
        profile_names = list_names[:4]
        for ((x0, y0), (x1,y1)), name in zip(profiles, profile_names):
            cv2.imwrite(f"export_editor/{name}.png", img[y0:y1, x0:x1])
    else:
        for i, ((x0, y0), (x1,y1)) in enumerate(bbox):
            cv2.imwrite(f"export_editor/untitled_{k}_{i}.png", img[y0:y1, x0:x1])
    list_names = list_names[4:]