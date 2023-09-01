import copy
import os
from dataclasses import dataclass
from typing import List, Union

import cv2
import numpy as np
from PIL import Image

import insightface
import onnxruntime

from modules.face_restoration import FaceRestoration
from modules.upscaler import UpscalerData
from modules.shared import state
from modules.paths_internal import models_path
from scripts.reactor_logger import logger

import warnings

np.warnings = warnings
np.warnings.filterwarnings('ignore')

providers = onnxruntime.get_available_providers()


@dataclass
class UpscaleOptions:
    do_restore_first: bool = True
    scale: int = 1
    upscaler: UpscalerData = None
    upscale_visibility: float = 0.5
    face_restorer: FaceRestoration = None
    restorer_visibility: float = 0.5


def cosine_distance(vector1: np.ndarray, vector2: np.ndarray) -> float:
    vec1 = vector1.flatten()
    vec2 = vector2.flatten()

    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    cosine_distance = 1 - (dot_product / (norm1 * norm2))
    return cosine_distance


def cosine_similarity(test_vec: np.ndarray, source_vecs: List[np.ndarray]) -> float:
    cos_dist = sum(cosine_distance(test_vec, source_vec) for source_vec in source_vecs)
    average_cos_dist = cos_dist / len(source_vecs)
    return average_cos_dist


MESSAGED_STOPPED = False
MESSAGED_SKIPPED = False

def reset_messaged():
    global MESSAGED_STOPPED, MESSAGED_SKIPPED
    if not state.interrupted:
        MESSAGED_STOPPED = False
    if not state.skipped:
        MESSAGED_SKIPPED = False

def check_process_halt(msgforced: bool = False):
    global MESSAGED_STOPPED, MESSAGED_SKIPPED
    if state.interrupted:
        if not MESSAGED_STOPPED or msgforced:
            logger.info("Stopped by User")
            MESSAGED_STOPPED = True
        return True
    if state.skipped:
        if not MESSAGED_SKIPPED or msgforced:
            logger.info("Skipped by User")
            MESSAGED_SKIPPED = True
        return True
    return False


FS_MODEL = None
CURRENT_FS_MODEL_PATH = None

ANALYSIS_MODEL = None


def getAnalysisModel():
    global ANALYSIS_MODEL
    if ANALYSIS_MODEL is None:
        ANALYSIS_MODEL = insightface.app.FaceAnalysis(
            name="buffalo_l", providers=providers, root=os.path.join(models_path, "insightface") # note: allowed_modules=['detection', 'genderage']
        )
    return ANALYSIS_MODEL


def getFaceSwapModel(model_path: str):
    global FS_MODEL
    global CURRENT_FS_MODEL_PATH
    if CURRENT_FS_MODEL_PATH is None or CURRENT_FS_MODEL_PATH != model_path:
        CURRENT_FS_MODEL_PATH = model_path
        FS_MODEL = insightface.model_zoo.get_model(model_path, providers=providers)

    return FS_MODEL


def upscale_image(image: Image, upscale_options: UpscaleOptions):
    result_image = image
    
    if check_process_halt(msgforced=True):
        return result_image
    
    if upscale_options.do_restore_first:
        if upscale_options.face_restorer is not None:
            original_image = result_image.copy()
            logger.info("Restoring the face with %s", upscale_options.face_restorer.name())
            numpy_image = np.array(result_image)
            numpy_image = upscale_options.face_restorer.restore(numpy_image)
            restored_image = Image.fromarray(numpy_image)
            result_image = Image.blend(
                original_image, restored_image, upscale_options.restorer_visibility
            )
        if upscale_options.upscaler is not None and upscale_options.upscaler.name != "None":
            original_image = result_image.copy()
            logger.info(
                "Upscaling with %s scale = %s",
                upscale_options.upscaler.name,
                upscale_options.scale,
            )
            result_image = upscale_options.upscaler.scaler.upscale(
                original_image, upscale_options.scale, upscale_options.upscaler.data_path
            )
            if upscale_options.scale == 1:
                result_image = Image.blend(
                    original_image, result_image, upscale_options.upscale_visibility
                )
    else:
        if upscale_options.upscaler is not None and upscale_options.upscaler.name != "None":
            original_image = result_image.copy()
            logger.info(
                "Upscaling with %s scale = %s",
                upscale_options.upscaler.name,
                upscale_options.scale,
            )
            result_image = upscale_options.upscaler.scaler.upscale(
                image, upscale_options.scale, upscale_options.upscaler.data_path
            )
            if upscale_options.scale == 1:
                result_image = Image.blend(
                    original_image, result_image, upscale_options.upscale_visibility
                )
        if upscale_options.face_restorer is not None:
            original_image = result_image.copy()
            logger.info("Restoring the face with %s", upscale_options.face_restorer.name())
            numpy_image = np.array(result_image)
            numpy_image = upscale_options.face_restorer.restore(numpy_image)
            restored_image = Image.fromarray(numpy_image)
            result_image = Image.blend(
                original_image, restored_image, upscale_options.restorer_visibility
            )

    return result_image


def get_face_gender(
        face,
        face_index,
        gender_condition,
        operated: str
):
    gender = [
        x.sex
        for x in face
    ]
    gender.reverse()
    face_gender = gender[face_index]
    logger.info("%s Face %s: Detected Gender -%s-", operated, face_index, face_gender)
    if (gender_condition == 1 and face_gender == "F") or (gender_condition == 2 and face_gender == "M"):
        logger.info("OK - Detected Gender matches Condition")
        try:
            return sorted(face, key=lambda x: x.bbox[0])[face_index], 0
        except IndexError:
            return None, 0
    else:
        logger.info("WRONG - Detected Gender doesn't match Condition")
        return sorted(face, key=lambda x: x.bbox[0])[face_index], 1


def reget_face_single(img_data, det_size, face_index):
    det_size_half = (det_size[0] // 2, det_size[1] // 2)
    return get_face_single(img_data, face_index=face_index, det_size=det_size_half)


def get_face_single(img_data: np.ndarray, face_index=0, det_size=(640, 640), gender_source=0, gender_target=0):
    face_analyser = copy.deepcopy(getAnalysisModel())
    face_analyser.prepare(ctx_id=0, det_size=det_size)
    face = face_analyser.get(img_data)

    buffalo_path = os.path.join(models_path, "insightface/models/buffalo_l.zip")
    if os.path.exists(buffalo_path):
        os.remove(buffalo_path)

    if gender_source != 0:
        if len(face) == 0 and det_size[0] > 320 and det_size[1] > 320:
            return reget_face_single(img_data, det_size, face_index)
        return get_face_gender(face,face_index,gender_source,"Source")

    if gender_target != 0:
        if len(face) == 0 and det_size[0] > 320 and det_size[1] > 320:
            return reget_face_single(img_data, det_size, face_index)
        return get_face_gender(face,face_index,gender_target,"Target")
    
    if len(face) == 0 and det_size[0] > 320 and det_size[1] > 320:
        return reget_face_single(img_data, det_size, face_index)

    try:
        return sorted(face, key=lambda x: x.bbox[0])[face_index], 0
    except IndexError:
        return None, 0


def swap_face(
    source_img: Image.Image,
    target_img: Image.Image,
    model: Union[str, None] = None,
    source_faces_index: List[int] = [0],
    faces_index: List[int] = [0],
    upscale_options: Union[UpscaleOptions, None] = None,
    gender_source: int = 0,
    gender_target: int = 0,
):
    result_image = target_img
    
    if check_process_halt():
        return result_image
    
    if model is not None:

        if isinstance(source_img, str):  # source_img is a base64 string
            import base64, io
            if 'base64,' in source_img:  # check if the base64 string has a data URL scheme
                # split the base64 string to get the actual base64 encoded image data
                base64_data = source_img.split('base64,')[-1]
                # decode base64 string to bytes
                img_bytes = base64.b64decode(base64_data)
            else:
                # if no data URL scheme, just decode
                img_bytes = base64.b64decode(source_img)
            
            source_img = Image.open(io.BytesIO(img_bytes))
            
        source_img = cv2.cvtColor(np.array(source_img), cv2.COLOR_RGB2BGR)
        target_img = cv2.cvtColor(np.array(target_img), cv2.COLOR_RGB2BGR)

        source_face, wrong_gender = get_face_single(source_img, face_index=source_faces_index[0], gender_source=gender_source)

        if len(source_faces_index) != 0 and len(source_faces_index) != 1 and len(source_faces_index) != len(faces_index):
            logger.info("Source Faces must have no entries (default=0), one entry, or same number of entries as target faces.")
        elif source_face is not None:
            
            result = target_img
            face_swapper = getFaceSwapModel(model)

            source_face_idx = 0

            swapped = 0

            for face_num in faces_index:
                if len(source_faces_index) > 1 and source_face_idx > 0:
                    source_face, wrong_gender = get_face_single(source_img, face_index=source_faces_index[source_face_idx], gender_source=gender_source)
                source_face_idx += 1

                if source_face is not None and wrong_gender == 0:
                    target_face, wrong_gender = get_face_single(target_img, face_index=face_num, gender_target=gender_target)
                    if target_face is not None and wrong_gender == 0:
                        result = face_swapper.get(result, target_face, source_face)
                        swapped += 1
                    elif wrong_gender == 1:
                        wrong_gender = 0
                        if source_face_idx == len(source_faces_index):
                            result_image = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
                            if upscale_options is not None:
                                result_image = upscale_image(result_image, upscale_options)
                            return result_image
                    else:
                        logger.info(f"No target face found for {face_num}")
                elif wrong_gender == 1:
                    wrong_gender = 0
                    if source_face_idx == len(source_faces_index):
                        result_image = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
                        if upscale_options is not None:
                            result_image = upscale_image(result_image, upscale_options)
                        return result_image
                else:
                    logger.info(f"No source face found for face number {source_face_idx}.")

            result_image = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
            if upscale_options is not None and swapped > 0:
                result_image = upscale_image(result_image, upscale_options)

        else:
            logger.info("No source face(s) found")
    return result_image
