# Compatible with Python3
# -*- coding: utf-8 -*-

import json
import base64
import os
import hashlib
import requests
from PIL import Image, ImageDraw


class Symmetry:
    def __init__(self, api_key, save_dir, logger):
        if not api_key and not save_dir and not logger:
            raise ValueError("必要な引数が不足しています。")
        self.api_key = api_key
        self.save_dir = save_dir
        self.logger = logger

    def do(self, url):  # シンメトリー実行関数
        self.logger.info("対象URL: {}".format(url))
        hashed_url = hashlib.md5(url.encode()).hexdigest()
        original_path = os.path.join(self.save_dir, f"{hashed_url}.jpg")
        with requests.get(url) as r:
            with open(original_path, "wb") as f:
                f.write(r.content)
            body = {
                "requests": [
                    {
                        "image": {
                            "content": base64.b64encode(r.content).decode()
                        },
                        "features": [
                            {
                                "type": "FACE_DETECTION",
                                "maxResults": 10
                            }
                        ]
                    }
                ]
            }

        api_uri = "https://vision.googleapis.com/v1/images:annotate"

        apireq = requests.post(api_uri, headers={"Content-Type": "application/json"}, params={"key": self.api_key}, data=json.dumps(body))
        apireq.raise_for_status()

        try:
            faces = apireq.json()["responses"][0]["faceAnnotations"]
        except KeyError:
            return []

        result = []

        if len(faces):
            with Image.open(original_path, "r") as original:
                original_width = original.size[0]
                original_height = original.size[1]
                rectangle_img = original
                draw_img = ImageDraw.Draw(rectangle_img)
                img_height = original_height + 20

                for count, face in enumerate(faces):
                    self.logger.info("{}個目の顔を処理しています。".format(count+1))

                    box = [(v.get('x', 0.0), v.get('y', 0.0))
                           for v in face['fdBoundingPoly']['vertices']]
                    draw_img.line(box + [box[0]], width=1, fill='#FFF')

                    x = [v.get('x', 0.0) for v in face['fdBoundingPoly']['vertices']]
                    coord = int((max(x) + min(x))/2)

                    img1_width = coord * 2 + 20
                    img1 = Image.new('RGB', (img1_width, img_height), (255, 255, 255))

                    img1_left = original.crop((0, 0, coord, original_height))
                    img1.paste(img1_left, (10, 10))

                    img1_right = img1_left.transpose(Image.FLIP_LEFT_RIGHT)
                    img1.paste(img1_right, (coord+10, 10))

                    img1_filename = os.path.join(self.save_dir, "{}_{}_left.jpg".format(hashed_url, count))
                    img1.save(img1_filename, 'JPEG', quality=80, optimize=True)

                    img2_width = (original_width - coord) * 2 + 20
                    img2 = Image.new('RGB', (img2_width, img_height), (255, 255, 255))

                    img2_left = original.crop((coord, 0, original_width, original_height))
                    img2_size = original_width - coord
                    img2.paste(img2_left, (img2_size+10, 10))

                    img2_right = img2_left.transpose(Image.FLIP_LEFT_RIGHT)
                    img2.paste(img2_right, (10, 10))

                    img2_filename = os.path.join(self.save_dir, "{}_{}_right.jpg".format(hashed_url, count))
                    img2.save(img2_filename, 'JPEG', quality=80, optimize=True)

                    imgs = [
                        original_path,
                        img1_filename,
                        img2_filename
                    ]

                    result.append(imgs)

                rectangle_img.save(original_path, 'JPEG', quality=80, optimize=True)

            return result

        else:
            self.logger.info("顔は見つかりませんでした。処理を終了します。")
            os.remove(original_path)
            return False
