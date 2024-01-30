import gradio as gr
from scripts.reactor_swapper import build_face_model

# TAB TOOLS
def show():
    with gr.Tab("Tools"):
        with gr.Tab("Face Models"):
            gr.Markdown("Load an image containing one person, name it and click 'Build and Save'")
            img_fm = gr.Image(
                type="pil",
                label="Load Image to build Face Model",
            )
            with gr.Row(equal_height=True):
                fm_name = gr.Textbox(
                    value="",
                    placeholder="Please type any name (e.g. Elena)",
                    label="Face Model Name",
                )
                save_fm_btn = gr.Button("Build and Save")
            save_fm = gr.Markdown("You can find saved models in 'models/reactor/faces'")
            save_fm_btn.click(
                build_face_model,
                inputs=[img_fm, fm_name],
                outputs=[save_fm],
            )
