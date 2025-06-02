import os
import base64
from IPython.display import HTML, display

def display_image(image_path, width=500):

    ext = os.path.splitext(image_path)[1].lower()
    if ext in ['.jpg', '.jpeg']:
        image_format = "jpeg"
    elif ext == '.png':
        image_format = "png"
    elif ext == '.gif':
        image_format = "gif"
    else:
        image_format = "jpeg"

    with open(image_path, "rb") as file:
        encoded_image = base64.b64encode(file.read()).decode('utf-8')
    
    html_code = (
        f'<img src="data:image/{image_format};base64,{encoded_image}" '
        f'alt="图片" style="width:{width}px; height:auto;">'
    )
    display(HTML(html_code))
