import threading
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.ExifTags import TAGS
from utils.utils import (
    get_exif_data,
    get_camera_info,
    get_printable_text,
    print_Y,
    print_R,
    print_G,
)
import yaml
import sys
import pathlib
import os

# 创建互斥锁
lock = threading.Lock()

os.chdir(pathlib.Path(sys.executable).parent)

print(os.path.dirname(__file__))
def load_config(config_path="conf/config.yml"):
    with open(os.path.join(os.path.dirname(__file__), config_path), encoding="utf-8") as file:
        return yaml.load(file, Loader=yaml.FullLoader)

config = load_config()
# 字体大小
font_size = config.get("font_size", 0)


# 字体文件
font_regular = ImageFont.truetype(
    os.path.join(os.path.dirname(__file__),config.get("font_regular", "./font/NotoSansSC-Regular.otf")), size=font_size
)
font_bold = ImageFont.truetype(
   os.path.join(os.path.dirname(__file__), config.get("font_bold", "./font/NotoSansSC-Bold.otf")), size=font_size
)
# padding
PADDING = int(config.get("padding", 0))
DEFAULT_EXIF_MESSAGE = config.get("default_exif_message", "N/A")

PADDING_LEFT = PADDING
COLOR_BLACK = (0, 0, 0)
COLOR_GREY = (100, 100, 100)


def process_image(image_path):
    print_G(f"\n>>> {image_path}")

    # get Exif
    exif_data = get_exif_data(image_path)
    if len(exif_data) == 0 or exif_data == None:
        print_Y("skip " + image_path + " exif_data " + str(exif_data))
        return 
    print_G("camera info " + str(exif_data))
    # get camera info
    camera_info = get_camera_info(exif_data)
    if len(camera_info) == 0 or camera_info == None:
        print_Y("skip " + image_path + " camera_info " + str(camera_info))
        return
    a, b, c, d = (
        camera_info.get("FocalLength", DEFAULT_EXIF_MESSAGE),
        camera_info.get("ISO", DEFAULT_EXIF_MESSAGE),
        camera_info.get("FNumber", DEFAULT_EXIF_MESSAGE),
        camera_info.get("ExposureTime", DEFAULT_EXIF_MESSAGE),
    )
    text_ise = (
        DEFAULT_EXIF_MESSAGE
        if DEFAULT_EXIF_MESSAGE in (a, b, c, d)
        else "{}mm ISO{} f{} {}".format(int(a), b, c, d)
    )
    make = camera_info.get("Make")
    text_model = "{}".format(camera_info.get("Model", DEFAULT_EXIF_MESSAGE))
    text_lens = "{}".format(camera_info.get("LensModel", DEFAULT_EXIF_MESSAGE))
    text_datetime = "{}".format(
        camera_info.get("DateTimeOriginal", DEFAULT_EXIF_MESSAGE)
    )

    make = get_printable_text(make)
    
    text_model = get_printable_text(text_model)
    text_lens = get_printable_text(text_lens)
    text_datetime = get_printable_text(text_datetime)

    # 绘图
    image_original = Image.open(image_path).convert("RGBA")
    image_original = ImageOps.exif_transpose(image_original)
    image_size = image_original.size

    image = Image.new("RGB", (image_size[0], image_size[1] + 450), (255, 255, 255))
    image.paste(image_original, (0, 0), image_original)
    draw = ImageDraw.Draw(image)

    PADDING_TOP = PADDING + image_size[1]  # - 20

    draw.text(
        (PADDING_LEFT, PADDING_TOP), text_ise, fill=COLOR_BLACK, font=font_bold,
    )

    draw.text(
        (PADDING_LEFT, PADDING_TOP + 120),
        text_datetime,
        fill=COLOR_GREY,
        font=font_regular,
    )

    max_len = max(font_bold.getlength(text_model), font_regular.getlength(text_lens))
    position_make = (image_size[0] - PADDING - max_len, PADDING_TOP)
    position_lens = (image_size[0] - PADDING - max_len, PADDING_TOP + 120)

    draw.text(
        position_make, text_model, fill=COLOR_BLACK, font=font_bold, align="left",
    )

    draw.line(
        (
            (position_make[0] - PADDING // 2, position_make[1] + 10),
            (position_lens[0] - PADDING // 2, PADDING_TOP + 20 + 210),
        ),
        fill=COLOR_GREY,
        width=4,
    )

    draw.text(
        position_lens, text_lens, fill=COLOR_GREY, font=font_regular,
    )

    paste_logo(make, image_size, image, PADDING_TOP, max_len)

    # 保存
    save_img(image_path, image)

def paste_logo(make, image_size, image, PADDING_TOP, max_len):
    try:
        logo = Image.open(os.path.join(os.path.dirname(__file__),f"./logo/{make}.png"))
        width, height = logo.size
        new_width = int((210 / height) * width)
        logo = logo.resize((new_width, 210), Image.LANCZOS).convert("RGBA")

    except Exception as e:
        print_R(f"error {e}")
        return

    image.paste(
        logo,
        (
            int(image_size[0] - max_len - PADDING - logo.size[0] - PADDING),
            PADDING_TOP + 20,
        ),
        logo,
    )

def save_img(image_path, image:Image):
    ori_path = pathlib.Path(image_path)
    image.save(ori_path.parent / "frame" / f"{ori_path.stem}_with_frame{ori_path.suffix}")

def process_image_thread_safe(image_path):
    with lock:
        process_image(image_path)

def handle_images(image_or_file_path):
    threads = []
    if image_or_file_path != None and  image_or_file_path != "" :
        if os.path.isdir(image_or_file_path):
            if not os.path.exists(image_or_file_path + "/frame"):
                os.mkdir(image_or_file_path + "/frame")
            for file in os.listdir(image_or_file_path):
                if file.endswith((".jpg",".jpeg","png")):
                    try:
                        thread = threading.Thread(target=process_image(os.path.join(image_or_file_path, file)))
                        thread.start()
                        threads.append(thread)
                    except Exception as err :
                        print_R(f"error {err}")
        else:
            if not os.path.exists(os.path.dirname(image_or_file_path) + "/frame"):
                os.mkdir(os.path.dirname(image_or_file_path) + "/frame")
            process_image(image_or_file_path)

    for thread in threads:
        thread.join()
    