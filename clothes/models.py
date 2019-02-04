from wardrobe import db
from PIL import Image
import scipy.cluster
import cv2, os
import numpy as np


class Clothes(db.Model):
    __tablename__ = 'clothes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(128))
    clth_type = db.Column(db.Integer, db.ForeignKey('clth_type.id'))
    temperature_min = db.Column(db.Integer)
    temperature_max = db.Column(db.Integer)
    file_path = db.Column(db.String(128))
    color_red = db.Column(db.Integer)
    color_green = db.Column(db.Integer)
    color_blue = db.Column(db.Integer)

    def __init__(self, user_id, name, clth_type, temperature_min, temperature_max, file_path):
        self.user_id = user_id
        self.name = name
        self.clth_type = clth_type
        self.temperature_min = temperature_min
        self.temperature_max = temperature_max
        self.file_path = file_path
        if file_path:
            clth_colors = [int(x) for x in self.get_dominant_color()[:3]]
        else:
            clth_colors = [255, 255, 255]
        self.color_red, self.color_green, self.color_blue = clth_colors

    def get_dominant_color(self):
        from config import upload_folder

        BLUR = 21
        CANNY_THRESH_1 = 10
        CANNY_THRESH_2 = 200
        MASK_DILATE_ITER = 10
        MASK_ERODE_ITER = 10
        MASK_COLOR = (1.0, 1.0, 1.0)  # In BGR format

        img = cv2.imread(f'{upload_folder}/{self.file_path}')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray, CANNY_THRESH_1, CANNY_THRESH_2)
        edges = cv2.dilate(edges, None)
        edges = cv2.erode(edges, None)

        contour_info = []
        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        for c in contours:
            contour_info.append((
                c,
                cv2.isContourConvex(c),
                cv2.contourArea(c),
            ))
        contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
        max_contour = contour_info[0]

        mask = np.zeros(edges.shape)
        cv2.fillConvexPoly(mask, max_contour[0], (255))

        mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
        mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
        mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
        mask_stack = np.dstack([mask] * 3)  # Create 3-channel alpha mask

        mask_stack = mask_stack.astype('float32') / 255.0  # Use float matrices,
        img = img.astype('float32') / 255.0  # for easy blending

        masked = (mask_stack * img) + ((1 - mask_stack) * MASK_COLOR)  # Blend
        masked = (masked * 255).astype('uint8')  # Convert back to 8-bit

        cv2.imwrite(f'{upload_folder}/short_{self.file_path}', masked)

        NUM_CLUSTERS = 2

        im = Image.open(f'{upload_folder}/short_{self.file_path}')
        im = im.resize((50, 50))  # optional, to reduce time

        ar = np.asarray(im)
        shape = ar.shape
        ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)
        codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)

        peak = [255, 255, 255]

        for one_color in codes:
            sum_color = int(one_color[0]) + int(one_color[1]) + int(one_color[2])
            if sum_color <= 250*3:
                peak = one_color

        os.remove(f'{upload_folder}/short_{self.file_path}')

        return peak

    class Types(db.Model):
        __tablename__ = 'clth_type'
        id = db.Column(db.Integer, primary_key=True)
        desc = db.Column(db.String(64))
        pos = db.Column(db.String(64))

        def __init__(self, desc, pos):
            self.desc = desc
            self.pos = pos
