'''
Author: SpenserCai
Date: 2023-07-28 14:37:40
version: 
LastEditors: SpenserCai
LastEditTime: 2023-08-07 22:04:42
Description: file content
'''
# DeOldify API
from fastapi import FastAPI, Body

from modules.api.models import *
from modules.api import api
from modules import paths_internal,shared
import gradio as gr

from deoldify import device as deoldify_device
from deoldify.device_id import DeviceId

device_id = shared.cmd_opts.device_id

if device_id is not None:
    device_id = DeviceId(int(device_id))
    deoldify_device.set(device=device_id)
else:
    deoldify_device.set(device=DeviceId.GPU0)

from PIL import Image

from deoldify.visualize import *

import warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*?Your .*? set is empty.*?")
warnings.filterwarnings("ignore", category=UserWarning, message="The parameter 'pretrained' is deprecated since 0.13 and may be removed in the future, please use 'weights' instead.")
warnings.filterwarnings("ignore", category=FutureWarning, message="Arguments other than a weight enum or `None`.*?")

def deoldify_api(_: gr.Blocks, app: FastAPI):
    @app.post("/deoldify/image")
    async def deoldify_image(
        input_image: str = Body("",title="image input"),
        render_factor: int = Body(35,title="render factor"),
        artistic: bool = Body(False,title="artistic")
    ):
        vis = get_image_colorizer(root_folder=Path(paths_internal.models_pat),render_factor=render_factor, artistic=artistic)
        # 把base64转换成图片 PIL.Image
        img = Image.open(BytesIO(base64.b64decode(input_image)))
        outImg = vis.get_transformed_image_from_image(img, render_factor=render_factor)
        return {"image": api.encode_pil_to_base64(outImg).decode("utf-8")}

try:
    import modules.script_callbacks as script_callbacks

    script_callbacks.on_app_started(deoldify_api)
except:
    pass