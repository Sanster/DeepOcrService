#!/usr/env/bin python3

import os
import sys

import cv2
import numpy as np

from helper import utils

this_dir = os.path.dirname(__file__)
lib_path = os.path.join(this_dir, 'tf_crnn')
sys.path.insert(0, lib_path)
from tf_crnn.libs.label_converter import LabelConverter


# noinspection PyMethodMayBeStatic
class Recoer:
    IMG_HEIGHT = 32

    def __init__(self, chars_file, ckpt):
        """
        :param ckpt: ckpt 目录或者 pb 文件
        """
        self.converter = LabelConverter(chars_file)
        self.sess, graph = utils.load_ckpt(ckpt)

        input_name = 'inputs:0'
        is_training_name = 'is_training:0'
        output_name = 'output:0'

        if os.path.isfile(ckpt) and ckpt.endswith('.pb'):
            prefix = 'import/'
            input_name = prefix + input_name
            is_training_name = prefix + is_training_name
            output_name = prefix + output_name

        self.inputs = graph.get_tensor_by_name(input_name)
        self.is_training = graph.get_tensor_by_name(is_training_name)
        self.output = graph.get_tensor_by_name(output_name)

    def remove_padding(self, ocr_results):
        # roi 图片 padding 以后，识别结果中末尾会有多余的字符，目前多余的字符都是 `;` ，这里临时性地将它移除
        out = []

        for result in ocr_results:
            r = result.rstrip(';；')
            out.append(r)
        return out

    def recognize(self, rois, img):
        img_rois = self.get_roi_imgs(rois, img)

        batch_imgs = self.get_batch_imgs(img_rois)

        predicts = self.sess.run(self.output, feed_dict={self.inputs: batch_imgs, self.is_training: False})

        ocr_results = self.decode(predicts)
        ocr_results = self.remove_padding(ocr_results)

        return ocr_results

    def decode(self, predicts):
        decoded_predicts = self.converter.decode_list(predicts, invalid_index=-1)
        ocr_results = [''.join(x) for x in decoded_predicts]
        return ocr_results

    def get_batch_imgs(self, img_rois):
        max_width = max(img_rois, key=lambda x: x.shape[1]).shape[1]
        # print("max width %d" % max_width)
        batch_imgs = []
        for roi_img in img_rois:
            if roi_img.shape[0] < max_width:
                new_img = np.ones((roi_img.shape[0], max_width, 1), np.float32)
                new_img[:roi_img.shape[0], :roi_img.shape[1], :] = roi_img
                batch_imgs.append(new_img)
            else:
                batch_imgs.append(roi_img)
        return batch_imgs

    def get_roi_imgs(self, rois, ori_img):
        ret = []
        img = (cv2.cvtColor(ori_img, cv2.COLOR_BGR2GRAY).astype(np.float32) - 128.) / 128.
        for rect in rois:
            cropd_img = img[rect[1]:rect[3], rect[0]:rect[2]]
            scale = cropd_img.shape[0] / Recoer.IMG_HEIGHT
            scaled_width = int(cropd_img.shape[1] / scale)
            cropd_img = cv2.resize(cropd_img, (scaled_width, Recoer.IMG_HEIGHT), interpolation=cv2.INTER_AREA)
            cropd_img = np.reshape(cropd_img, (cropd_img.shape[0], cropd_img.shape[1], 1))
            ret.append(cropd_img)
        return ret


if __name__ == "__main__":
    recoer = Recoer('./tf_crnn/data/chars/chn.txt', './data/models/raw_crnn.pb')
