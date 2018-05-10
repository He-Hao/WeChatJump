#!/usr/bin/python
# -*- coding: UTF-8 -*-

import aircv as ac


def match_img(img_src, img_obj, confidence=0.5):  # img_src=原始图像，img_obj=待查找的图片
    im_src = ac.imread(img_src)
    im_obj = ac.imread(img_obj)

    match_result = ac.find_template(im_src, im_obj, confidence)
    # {
    #  'confidence': 0.5435812473297119,
    #  'rectangle': ((394, 384), (394, 416), (450, 384), (450, 416)),
    #  'result': (422.0, 400.0)
    # }
    if match_result is not None:
        match_result['shape'] = (im_src.shape[1], im_src.shape[0])  # 0为高，1为宽
    return match_result
