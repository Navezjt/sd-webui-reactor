# Roop-GE 0.2.2 for StableDiffusion
### NSFW (uncensored) version (use it on your own responsibility) of [original sd-webui-roop](https://github.com/s0md3v/sd-webui-roop) with a lot of improvements

> GE (Gourieff Edition), aka "NSFW-Roop"

---
[**Disclaimer**](#disclaimer) | [**Installation**](#installation) | [**Usage**](#usage) | [**Troubleshooting**](#troubleshooting) | [**Updating**](#updating)

---

This is an extension for StableDiffusion's [AUTOMATIC1111 web-ui](https://github.com/AUTOMATIC1111/stable-diffusion-webui/) that allows face-replacement in images. It is based on [Roop-GE](https://github.com/Gourieff/Roop-GE).

<img src="example/demo_crop.jpg" alt="example"/>

### Disclaimer

This software is meant to be a productive contribution to the rapidly growing AI-generated media industry. It will help artists with tasks such as animating a custom character or using the character as a model for clothing etc.

The developers of this software are aware of its possible unethical applicaitons and are committed to take preventative measures against them. We will continue to develop this project in the positive direction while adhering to law and ethics.

Users of this software are expected to use this software responsibly while abiding the local law. If face of a real person is being used, users are suggested to get consent from the concerned person and clearly mention that it is a deepfake when posting content online. **Developers and Contributors of this software are not responsible for actions of end-users.**

## Installation

To install the extension, follow these steps:

1. (For Windows Users) Install **Visual Studio 2022** (Community version, for example - you need this step to build some of dependencies):
  https://visualstudio.microsoft.com/downloads/
  OR only **VS C++ Build Tools** (if you don't need the whole Visual Studio) and select "Desktop Development with C++" under "Workloads -> Desktop & Mobile":
  https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. In web-ui, go to the "Extensions" tab and use this URL `https://github.com/Gourieff/sd-webui-roop-nsfw` in the "Install from URL" tab
3. Pelase, wait for several minutes until installation process will end
4. Check the last message in your SD-WebUI Console:
* If you see the message "--- PLEASE, RESTART the Server! ---" - so, do it, stop the Server (CTRL+C) and start it again. 
* If you see the message "Done!", just go to the "Installed" tab (*if you have any other Roop extension enabled - disable it, otherwise this extension won't work*), click "Apply and restart UI"
5. Enjoy!

If you use [SD.Next](https://github.com/vladmandic/automatic):

1. (For Windows Users) The same 1st step as you see above (VS Studio 2022 or VS C++ Build Tools)
2. Go to `automatic\venv\Scripts` or `automatic/venv/bin`, run Terminal or Console (cmd) for that folder and type `activate`
3. Run `pip install insightface==0.7.3`
4. Run SD.Next, go to the "Extensions" tab and use this URL `https://github.com/Gourieff/sd-webui-roop-nsfw` in the "Install from URL" tab
5. Pelase, wait for several minutes until installation process will end
6. Check the last message in your SD.Next Console:
* If you see the message "--- PLEASE, RESTART the Server! ---" - so, do it, stop the Server (CTRL+C) and start it again.
* If you see the message "Done!", just go to the "Installed" tab (*if you have any other Roop extension enabled - disable it, otherwise this extension won't work*), click "Restart the UI"
7. Stop SD.Next, go to the `automatic\extensions\sd-webui-roop-nsfw` directory - if you see there `models\roop` folder with the file `inswapper_128.onnx`, just move the file to the `automatic\models\roop` folder
8. Run your SD.Next WebUI and enjoy!

## Usage

1. Under "Roop-GE" drop-down menu, import an image containing a face;
2. Turn on the "Enable" checkbox;
3. That's it, now the generated result will have the face you selected.

**You can use Roop-GE with Webui API:**
1. Check the [SD Web API Wiki](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API) for how to use API;
2. Call `requests.get(url=f'{address}/sdapi/v1/script-info')` to find the args that Roop-GE needs;
3. Define Roop-GE script args and add like this `"alwayson_scripts": {"roop-ge":{"args":args}}` in the payload;
4. Call the API, there's an [full usage example](./example/api_example.py) in example folder.

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
2. If you see any folders with names start from `~` (ex. "~rotobuf") - delete them
3. Go to `stable-diffusion-webui\venv\Scripts` or `stable-diffusion-webui/venv/bin`
4. Run Terminal or Console (cmd) for that folder and type `activate`
5. Update your pip at first: `pip install -U pip`
6. Then one-by-one:
   - `pip install insightface==0.7.3`
   - `pip install onnx==1.14.0`
   - `pip install onnxruntime==1.15.0`
   - `pip install opencv-python==4.7.0.72`
   - `pip install diffusers==0.17.1`
   - `pip install tqdm`
7. Type `deactivate`, you can close your Terminal or Console and start your sd-webui, Roop should start OK - if not, welcome to Issues section.

**III. "TypeError: UpscaleOptions.init() got an unexpected keyword argument 'do_restore_first'"**

First of all - you need to disable any other Roop extensions:
- Go to 'Extensions -> Installed' tab and uncheck any Roop except this one
  <img src="example/roop-off.png" alt="uncompatible-with-other-roop"/>
- Click 'Apply and restart UI'

Alternative solution is here: https://github.com/Gourieff/sd-webui-roop-nsfw/issues/3

**IV. "AttributeError: 'FaceSwapScript' object has no attribute 'enable'"**

You need to disable the "SD-CN-Animation" extension (or perhaps some another that causes the conflict)

**V. "INVALID_PROTOBUF : Load model from <...>\models/roop\inswapper_128.onnx failed:Protobuf parsing failed"**

This error may occur if there's smth wrong with the model file `inswapper_128.onnx`

Try to download it manually from [here](https://huggingface.co/henryruhs/roop/resolve/main/inswapper_128.onnx)
and put it to the `stable-diffusion-webui\models\roop` replacing existing one

## Updating

A good and quick way to check for Extensions updates: https://github.com/Gourieff/sd-webui-extensions-updater
