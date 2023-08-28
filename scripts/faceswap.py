import os, glob
import gradio as gr
from PIL import Image

import modules.scripts as scripts
from modules.upscaler import Upscaler, UpscalerData
from modules import scripts, shared, images, scripts_postprocessing
from modules.processing import (
    StableDiffusionProcessing,
    StableDiffusionProcessingImg2Img,
)
from modules.face_restoration import FaceRestoration
from modules.paths_internal import models_path

from scripts.logger import logger
from scripts.swapper import UpscaleOptions, swap_face, check_process_halt, reset_messaged
from scripts.version import version_flag, app_title
from scripts.console_log_patch import apply_logging_patch


MODELS_PATH = None

def get_models():
    global MODELS_PATH
    models_path_init = os.path.join(models_path, "insightface/*")
    models = glob.glob(models_path_init)
    models = [x for x in models if x.endswith(".onnx") or x.endswith(".pth")]
    models_names = []
    for model in models:
        model_path = os.path.split(model)
        if MODELS_PATH is None:
            MODELS_PATH = model_path[0]
        model_name = model_path[1]
        models_names.append(model_name)
    return models_names


class FaceSwapScript(scripts.Script):
    def title(self):
        return f"{app_title}"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def ui(self, is_img2img):
        with gr.Accordion(f"{app_title}", open=False):
            with gr.Column():
                img = gr.inputs.Image(type="pil")
                enable = gr.Checkbox(False, label="Enable", info=f"The Fast and Simple \"roop-based\" FaceSwap Extension - {version_flag}")
                gr.Markdown("---")
                gr.Markdown("Source Image (above):")
                with gr.Row():
                    source_faces_index = gr.Textbox(
                        value="0",
                        placeholder="Which face(s) to use as Source (comma separated)",
                        label="Comma separated face number(s); Example: 0,2,1",
                    )
                    gender_source = gr.Radio(
                        ["No", "Female Only", "Male Only"],
                        value="No",
                        label="Gender Detection (Source)",
                        type="index",
                    )
                gr.Markdown("---")
                gr.Markdown("Target Image (result):")
                with gr.Row():
                    faces_index = gr.Textbox(
                        value="0",
                        placeholder="Which face(s) to Swap into Target (comma separated)",
                        label="Comma separated face number(s); Example: 1,0,2",
                    )
                    gender_target = gr.Radio(
                        ["No", "Female Only", "Male Only"],
                        value="No",
                        label="Gender Detection (Target)",
                        type="index",
                    )
                gr.Markdown("---")
                with gr.Row():
                    face_restorer_name = gr.Radio(
                        label="Restore Face",
                        choices=["None"] + [x.name() for x in shared.face_restorers],
                        value=shared.face_restorers[0].name(),
                        type="value",
                    )
                    face_restorer_visibility = gr.Slider(
                        0, 1, 1, step=0.1, label="Restore Face Visibility"
                    )
                restore_first = gr.Checkbox(
                    True,
                    label="1. Restore Face -> 2. Upscale (-Uncheck- if you want vice versa)",
                    info="Postprocessing Order"
                )
                upscaler_name = gr.inputs.Dropdown(
                    choices=[upscaler.name for upscaler in shared.sd_upscalers],
                    label="Upscaler",
                )
                with gr.Row():
                    upscaler_scale = gr.Slider(1, 8, 1, step=0.1, label="Scale by")
                    upscaler_visibility = gr.Slider(
                        0, 1, 1, step=0.1, label="Upscaler Visibility (if scale = 1)"
                    )
                gr.Markdown("---")
                swap_in_source = gr.Checkbox(
                    False,
                    label="Swap in source image",
                    visible=is_img2img,
                )
                swap_in_generated = gr.Checkbox(
                    True,
                    label="Swap in generated image",
                    visible=is_img2img,
                )
                
                models = get_models()
                with gr.Row():
                    if len(models) == 0:
                        logger.warning(
                            "You should at least have one model in models directory, please read the doc here : https://github.com/Gourieff/sd-webui-reactor/"
                        )
                        model = gr.inputs.Dropdown(
                            choices=models,
                            label="Model not found, please download one and reload WebUI",
                        )
                    else:
                        model = gr.inputs.Dropdown(
                            choices=models, label="Model", default=models[0]
                        )
                    console_logging_level = gr.Radio(
                        ["No log", "Minimum", "Default"],
                        value="Minimum",
                        label="Console Log Level",
                        type="index",
                    )
                gr.Markdown("---")

        return [
            img,
            enable,
            source_faces_index,
            faces_index,
            model,
            face_restorer_name,
            face_restorer_visibility,
            restore_first,
            upscaler_name,
            upscaler_scale,
            upscaler_visibility,
            swap_in_source,
            swap_in_generated,
            console_logging_level,
            gender_source,
            gender_target,
        ]


    @property
    def upscaler(self) -> UpscalerData:
        for upscaler in shared.sd_upscalers:
            if upscaler.name == self.upscaler_name:
                return upscaler
        return None

    @property
    def face_restorer(self) -> FaceRestoration:
        for face_restorer in shared.face_restorers:
            if face_restorer.name() == self.face_restorer_name:
                return face_restorer
        return None

    @property
    def upscale_options(self) -> UpscaleOptions:
        return UpscaleOptions(
            do_restore_first = self.restore_first,
            scale=self.upscaler_scale,
            upscaler=self.upscaler,
            face_restorer=self.face_restorer,
            upscale_visibility=self.upscaler_visibility,
            restorer_visibility=self.face_restorer_visibility,
        )

    def process(
        self,
        p: StableDiffusionProcessing,
        img,
        enable,
        source_faces_index,
        faces_index,
        model,
        face_restorer_name,
        face_restorer_visibility,
        restore_first,
        upscaler_name,
        upscaler_scale,
        upscaler_visibility,
        swap_in_source,
        swap_in_generated,
        console_logging_level,
        gender_source,
        gender_target,
    ):
        self.enable = enable
        if self.enable:

            reset_messaged()
            if check_process_halt():
                return
            
            global MODELS_PATH
            self.source = img
            self.face_restorer_name = face_restorer_name
            self.upscaler_scale = upscaler_scale
            self.upscaler_visibility = upscaler_visibility
            self.face_restorer_visibility = face_restorer_visibility
            self.restore_first = restore_first
            self.upscaler_name = upscaler_name       
            self.swap_in_generated = swap_in_generated
            self.model = os.path.join(MODELS_PATH,model)
            self.console_logging_level = console_logging_level
            self.gender_source = gender_source
            self.gender_target = gender_target
            if self.gender_source is None or self.gender_source == "No":
                self.gender_source = 0
            if self.gender_target is None or self.gender_target == "No":
                self.gender_target = 0
            self.source_faces_index = [
                int(x) for x in source_faces_index.strip(",").split(",") if x.isnumeric()
            ]
            self.faces_index = [
                int(x) for x in faces_index.strip(",").split(",") if x.isnumeric()
            ]
            if len(self.source_faces_index) == 0:
                self.source_faces_index = [0]
            if len(self.faces_index) == 0:
                self.faces_index = [0]

            if self.source is not None:
                apply_logging_patch(console_logging_level)
                if isinstance(p, StableDiffusionProcessingImg2Img) and swap_in_source:
                    logger.info("Working: source face index %s, target face index %s", self.source_faces_index, self.faces_index)

                    for i in range(len(p.init_images)):
                        logger.info("Swap in %s", i)
                        result = swap_face(
                            self.source,
                            p.init_images[i],
                            source_faces_index=self.source_faces_index,
                            faces_index=self.faces_index,
                            model=self.model,
                            upscale_options=self.upscale_options,
                            gender_source=self.gender_source,
                            gender_target=self.gender_target,
                        )
                        p.init_images[i] = result

                        if shared.state.interrupted or shared.state.skipped:
                            return
            
            else:
                logger.error("Please provide a source face")

    def postprocess_batch(self, p, *args, **kwargs):
        if self.enable:
            images = kwargs["images"]

    def postprocess_image(self, p, script_pp: scripts.PostprocessImageArgs, *args):
        if self.enable and self.swap_in_generated:

            current_job_number = shared.state.job_no + 1
            job_count = shared.state.job_count
            if current_job_number == job_count:
                reset_messaged()
            if check_process_halt():
                return
           
            if self.source is not None:
                logger.info("Working: source face index %s, target face index %s", self.source_faces_index, self.faces_index)
                image: Image.Image = script_pp.image
                result = swap_face(
                    self.source,
                    image,
                    source_faces_index=self.source_faces_index,
                    faces_index=self.faces_index,
                    model=self.model,
                    upscale_options=self.upscale_options,
                    gender_source=self.gender_source,
                    gender_target=self.gender_target,
                )
                try:
                    pp = scripts_postprocessing.PostprocessedImage(result)
                    pp.info = {}
                    p.extra_generation_params.update(pp.info)
                    script_pp.image = pp.image
                except:
                    logger.error("Cannot create a result image")
