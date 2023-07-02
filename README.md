# NSFW-Roop 0.1.0 for StableDiffusion
### NSFW (uncensored) version (use it on your own responsibility) of [original sd-webui-roop](https://github.com/s0md3v/sd-webui-roop) with a lot of improvements

This is an extension for StableDiffusion's [AUTOMATIC1111 web-ui](https://github.com/AUTOMATIC1111/stable-diffusion-webui/) that allows face-replacement in images. It is based on [Roop-GE](https://github.com/Gourieff/Roop-GE).

<img src="example/demo_crop.jpg" alt="example"/>

### Disclaimer

This software is meant to be a productive contribution to the rapidly growing AI-generated media industry. It will help artists with tasks such as animating a custom character or using the character as a model for clothing etc.

The developers of this software are aware of its possible unethical applicaitons and are committed to take preventative measures against them. We will continue to develop this project in the positive direction while adhering to law and ethics.

Users of this software are expected to use this software responsibly while abiding the local law. If face of a real person is being used, users are suggested to get consent from the concerned person and clearly mention that it is a deepfake when posting content online. **Developers and Contributors of this software are not responsible for actions of end-users.**

## Installation

To install the extension, follow these steps:

+ (For Windows Users) Install **Visual Studio 2022** (Community version, for example - you need this step to build some of dependencies):
  https://visualstudio.microsoft.com/downloads/
  OR only **VS C++ Build Tools** (if you don't need the whole Visual Studio) and select "Desktop Development with C++" under "Workloads -> Desktop & Mobile":
  https://visualstudio.microsoft.com/visual-cpp-build-tools/
+ In web-ui, go to the "Extensions" tab and use this URL `https://github.com/Gourieff/sd-webui-roop-nsfw` in the "Install from URL" tab.
+ Go to the "Installed" tab and click "Restart the UI"

## Usage

1. Under "NSFW-Roop" drop-down menu, import an image containing a face.
2. Turn on the "Enable" checkbox
3. That's it, now the generated result will have the face you selected

### The result face is blurry
Use the "Restore Face" option. You can also try the "Upscaler" option or for more finer control, use an upscaler from the "Extras" tab.
You can also set the postproduction order (from 0.1.0 version):
<img src="example/pp-order.png" alt="example"/>

*The old logic was the opposite (Upscale -> then Restore), resulting in worse face quality (and big texture differences) after upscaling.* 

### There are multiple faces in result
Select the face numbers you wish to swap using the "Comma separated face number(s)" option for swap-source and result images. You can use different index order.
<img src="example/multiple-faces.png" alt="example"/>

### ~~The result is totally black~~
~~This means roop detected that your image is NSFW.~~

<img src="example/IamSFW.jpg" alt="IamSFW" width="50%"/>

### Img2Img

You can choose to activate the swap on the source image or on the generated image, or on both using the checkboxes. Activating on source image allows you to start from a given base and apply the diffusion process to it.

Inpainting should work but only the masked part will be swapped.

## Troubleshooting

**I. "You should at least have one model in models directory"**

Please, check the path where "inswapper_128.onnx" model is stored. It must be inside the folder `stable-diffusion-webui\models\roop`. Move the model there if it's stored in a different directory.

**II. Any problems with installing Insightface or other dependencies**

(for Windows Users) If you have VS C++ Build Tools or MS VS 2022 installed but still have a problem, then try the next step:
1. Close your sd-webui and start it again
(for Any OS Users) If the problem still there, then do the following:
1. Go to `stable-diffusion-webui\venv\Lib\site-packages` folder (or it can be `stable-diffusion-webui/venv/lib/python3.10/site-packages`)
2. If you see any folders the with names start from `~` (ex. "~rotobuf") - delete them
3. Go to `stable-diffusion-webui\venv\Scripts` or `stable-diffusion-webui/venv/bin`
4. Run Terminal or Console (cmd) for that folder and type `activate`
5. Update your pip at first: `pip install -U pip`
6. Then one-by-one:
   - `pip install insightface==0.7.3`
   - `pip install onnxruntime==1.15.0`
   - `pip install opencv-python==4.7.0.72`
   - `pip install diffusers==0.17.1`
   - `pip install tqdm`
7. Type `deacticate`, you can close your Terminal or Console and start your sd-webui, Roop should start OK - if not, welcome to Issues section.

## Updating

A good and quick way to check for Extensions updates: https://github.com/Gourieff/sd-webui-extensions-updater
