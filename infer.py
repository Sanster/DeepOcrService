# -*- coding: UTF-8 -*-
from __future__ import print_function

import glob
import os
import argparse
import time

import cv2

from detector import Detector
from recoer import Recoer

detector = Detector('./data/models/ctpn.pb')
recoer = Recoer('./tf_crnn/data/chars/chn.txt', './data/models/crnn.pb')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_dir', default='/home/cwq/data/ICDAR13/Challenge2_Test_Task12_Images')
    parser.add_argument('--output_dir', default='./output')
    parser.add_argument('--viz', action='store_true', default=False)
    args = parser.parse_args()

    if not os.path.exists(args.img_dir):
        print("img_dir not exists")
        exit(-1)

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    return args


def main(args):
    exts = ['*.jpg', '*.png', '*.jpeg']
    im_files = []
    for ext in exts:
        im_files.extend(glob.glob(args.img_dir + "/" + ext))

    for im_file in im_files:
        process(im_file, args.output_dir, args.viz)


def save_txt_results(output_dir, im_name, rois, texts):
    f_path = os.path.join(output_dir, im_name.split('.')[0] + '.txt')
    with open(f_path, 'w', encoding='utf-8') as f:
        for i, roi in enumerate(rois):
            # xmin,ymin,xmax,ymax,text
            f.write('%d,%d,%d,%d,%s\n' % (roi[0], roi[1], roi[2], roi[3], texts[i]))


def process(im_file, output_dir, viz=False):
    img = cv2.imread(im_file)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    ctpn_start_time = time.time()
    rois = detector.detect(img)
    print("CTPN time: %.03fs" % (time.time() - ctpn_start_time))

    crnn_start_time = time.time()
    texts = recoer.recognize(rois, img)
    print("CRNN time: %.03fs" % (time.time() - crnn_start_time))
    print("Total time: %.03fs" % (time.time() - ctpn_start_time))

    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    img = draw_roi(img, rois)

    im_name = im_file.split('/')[-1]
    img_path = os.path.join(output_dir, im_name)
    cv2.imwrite(img_path, img)

    save_txt_results(output_dir, im_name, rois, texts)

    if viz:
        viz_result(img, rois, texts)


def viz_result(img, rois, texts):
    for i, text in enumerate(texts):
        x = rois[i][0]
        y = rois[i][1]
        cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0))

    cv2.namedWindow('result', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('result', 800, 800)
    cv2.imshow('result', img)
    k = cv2.waitKey()
    if k == 27:  # ESC
        exit(-1)


def draw_roi(img, rois):
    color = (0, 150, 0)
    for roi in rois:
        roi = [int(x) for x in roi]
        p1 = (roi[0], roi[1])
        p2 = (roi[2], roi[1])
        p3 = (roi[2], roi[3])
        p4 = (roi[0], roi[3])
        img = cv2.line(img, p1, p2, color, 2)
        img = cv2.line(img, p2, p3, color, 2)
        img = cv2.line(img, p3, p4, color, 2)
        img = cv2.line(img, p4, p1, color, 2)
    return img


if __name__ == "__main__":
    args = parse_args()
    main(args)
