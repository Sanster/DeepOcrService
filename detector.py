#!/usr/env/bin python3

import os
import sys
import math
import numpy as np
import tensorflow as tf

from helper import utils

this_dir = os.path.dirname(__file__)
lib_path = os.path.join(this_dir, 'tf_ctpn', 'lib')
sys.path.insert(0, lib_path)
from tf_ctpn.lib.text_connector import TextDetector
from tf_ctpn.lib.model.test import _get_blobs, _clip_boxes
from tf_ctpn.lib.layer_utils.generate_anchors import generate_anchors_pre
from tf_ctpn.lib.layer_utils.proposal_layer import proposal_layer


class Detector:
    FEET_STRIDE = 16
    NUM_ANCHORS = 10
    ANCHOR_WIDTH = 16
    H_RADIO_STEP = 0.7

    def __init__(self, ckpt):
        """
        :param ckpt: ckpt 目录或者 pb 文件
        """
        self.textdetector = TextDetector(False)

        self.sess, graph = utils.load_ckpt(ckpt)

        input_name = 'input:0'
        rpn_output_score_name = "RPN/rpn_cls_prob_reshape:0"
        rpn_output_bbox_name = "RPN/rpn_bbox_pred/Conv2D:0"

        if os.path.isfile(ckpt) and ckpt.endswith('.pb'):
            prefix = 'import/'
            input_name = prefix + input_name
            rpn_output_score_name = prefix + rpn_output_score_name
            rpn_output_bbox_name = prefix + rpn_output_bbox_name

        # Print all node name in graph
        # input_graph_def = graph.as_graph_def()
        # for node in input_graph_def.node:
        #     print(node.name)

        self.input = graph.get_tensor_by_name(input_name)
        self.rpn_score = graph.get_tensor_by_name(rpn_output_score_name)
        self.rpn_bbox = graph.get_tensor_by_name(rpn_output_bbox_name)

    def detect(self, img):
        """
        :param img: RGB
        :return:  text_lines point order: left-top, right-top, left-bottom, right-bottom
        """

        blobs, im_scales = _get_blobs(img)
        im_blob = blobs['data']
        im_info = np.array([im_blob.shape[1], im_blob.shape[2], im_scales[0]], dtype=np.float32)

        fetches = [self.rpn_bbox, self.rpn_score]
        feed_dict = {self.input: im_blob}

        rpn_bbox_pred, rpn_cls_prob = self.sess.run(fetches, feed_dict=feed_dict)
        print("rpn_cls_prob shape: %s" % str(rpn_cls_prob.shape))
        print("rpn_bbox_pred shape: %s" % str(rpn_bbox_pred.shape))

        cnn_height = math.ceil(im_info[0] / np.float32(Detector.FEET_STRIDE))
        cnn_width = math.ceil(im_info[1] / np.float32(Detector.FEET_STRIDE))

        print("cnn_width: %d, cnn_height: %d" % (cnn_width, cnn_height))

        anchors, _ = generate_anchors_pre(cnn_height, cnn_width,
                                          Detector.FEET_STRIDE,
                                          Detector.NUM_ANCHORS,
                                          Detector.ANCHOR_WIDTH,
                                          Detector.H_RADIO_STEP)

        rois, _ = proposal_layer(rpn_cls_prob, rpn_bbox_pred, im_info, 'TEST', anchors, Detector.NUM_ANCHORS)

        boxes = rois[:, 1:5]
        boxes = _clip_boxes(boxes, im_blob.shape[1:3])
        scores = rois[:, 0]

        text_lines = self.textdetector.detect(boxes, scores[:, np.newaxis], im_blob.shape[1:3])
        text_lines = self.get_line_boxes(text_lines)

        text_lines = self.recover_scale(text_lines, im_scales[0])
        print("detect %d text lines" % len(text_lines))

        text_lines = _clip_boxes(text_lines, img.shape)

        return text_lines.tolist()

    def recover_scale(self, boxes, scale):
        """
        :param boxes: [(x1, y1, x2, y2)]
        :param scale: image scale
        :return:
        """
        tmp_boxes = []
        for b in boxes:
            tmp_boxes.append([int(x / scale) for x in b])
        return np.asarray(tmp_boxes)

    def get_line_boxes(self, boxes, scale=1):
        """
        Get bounding boxes from four point
        :param boxes: (x1, y1, x2, y2, x3, y3, x4, y4)
        :param scale: scale returned by resize_im
        :return
            [(min_x, min_y, max_x, max_y), ...]
        """
        ret = []
        for box in boxes:
            min_x = min(int(box[0] / scale), int(box[2] / scale),
                        int(box[4] / scale), int(box[6] / scale))
            min_y = min(int(box[1] / scale), int(box[3] / scale),
                        int(box[5] / scale), int(box[7] / scale))
            max_x = max(int(box[0] / scale), int(box[2] / scale),
                        int(box[4] / scale), int(box[6] / scale))
            max_y = max(int(box[1] / scale), int(box[3] / scale),
                        int(box[5] / scale), int(box[7] / scale))

            ret.append([min_x, min_y, max_x, max_y])

        return ret


if __name__ == "__main__":
    detector = Detector('./data/models/ctpn.pb')
