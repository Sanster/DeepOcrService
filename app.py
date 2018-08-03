import io
import os
import time

import cv2
import numpy as np
from flask import Flask, Response, json, request, g, send_from_directory
from flask_cors import CORS

from detector import Detector
from recoer import Recoer

detector = Detector('./data/models/ctpn.pb')
recoer = Recoer('./tf_crnn/data/chars/chn.txt', './data/models/raw_crnn.pb')

app = Flask(__name__, static_folder='web/build')
CORS(app)


def responseJson(data):
    return Response(json.dumps(data), mimetype='application/json')


def get_cv_img(r):
    f = r.files['img']
    in_memory_file = io.BytesIO()
    f.save(in_memory_file)
    nparr = np.fromstring(in_memory_file.getvalue(), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


@app.before_request
def before_request():
    g.request_start_time = time.time()


@app.after_request
def after_request(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    print("request time: {:.03f}s".format(time.time() - g.request_start_time))
    return r


@app.route("/ocr", methods=['POST'])
def ocr():
    img = get_cv_img(request)

    print('Image size: {}x{}'.format(img.shape[1], img.shape[0]))

    res = process(img)

    return responseJson(res)


# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists("web/build/" + path):
        return send_from_directory('web/build', path)
    else:
        return send_from_directory('web/build', 'index.html')


def process(img):
    start_time = time.time()
    rois = detector.detect(img)
    print("CTPN time: %.03fs" % (time.time() - start_time))

    start_time = time.time()
    ocr_result = recoer.recognize(rois, img)
    print("CRNN time: %.03fs" % (time.time() - start_time))

    sorted_data = sorted(zip(rois, ocr_result), key=lambda x: x[0][1] + x[0][3] / 2)
    rois, ocr_result = zip(*sorted_data)

    res = {"results": []}

    for i in range(len(rois)):
        res["results"].append({
            'position': rois[i],
            'text': ocr_result[i]
        })

    return res


if __name__ == "__main__":
    app.run(host='0.0.0.0')
