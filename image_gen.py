import mastodon
from PIL import Image, ImageDraw, ImageFont, ImageColor
import requests
from markdownify import markdownify as md
import re
import textwrap


def shorten_str(string: str, length: int):
    """ Shorten very long strings and add ellipsis, so the max string length is 60 
    """
    if len(string) > length:
        return string[:length-3] + "..."
    else:
        return string

def rounded_mask(image, radius: int):
    """ Returns a mask that will round the image's corners
    """
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(
        xy = ((0, 0), (image.size[0], image.size[1])),
        radius = radius,
        fill = 255
    )
    return mask

def gen_image(post: dict):
    # make sure it's not a boost!
    # if it is, set the post to the actual post, not the boost
    if post["reblog"] != None:
        post: dict = post["reblog"]
    
    # get useful stuff
    url: str = post["url"]
    account: dict = post["account"] # more on this later
    content: str = post["content"] # this is html... might cause problems but whatevs
    media_attachments: list = post["media_attachments"] # list of media dicts

    # get account stuff
    username: str = account["username"] # username
    display_name: str = account["display_name"] # display name, aka what people usually see
    avatar: str = account["avatar_static"] # URL for avatar, but not a gif
    acc_url: str = account["url"] # URL for profile
    
    # configuration
    text_size = 40 # 30
    text_wrap = 45 # 60
    small_margin = text_size/3 # 10
    big_margin = int(text_size*1.5) # 60

    x_padding = 55 # 40
    y_padding = 55 # 40
    
    # get the domain name of the account
    domain = re.search(r"^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/\n]+)", acc_url).group(1) 

    # get a max width
    max_x = (x_padding*2)+((text_size/1.8)*text_wrap)
    
    # get the image, if any
    media_attachments_previewable: list = []
    for i in media_attachments:
        if i["type"] in ["image", "video", "gifv"]:
            media_attachments_previewable.append(i["preview_url"])
    if media_attachments_previewable:
        media_attachment = media_attachments_previewable[0]
        # make it the right size, with a max width
        media_attachment = Image.open(requests.get(media_attachment, stream=True).raw)
        media_attachment_x = int(max_x)
        media_attachment_y = int(media_attachment.height*max_x//media_attachment.width)
        media_attachment = media_attachment.resize((media_attachment_x, media_attachment_y))
        # for the height of the final image, give a big margin
        media_attachment_y += big_margin 
    else:
        media_attachment = None
        media_attachment_y = 0

    # change the content to markdown so I don't have to do my job
    md_content = md(
        content, 
        strip=["a"], 
        escape_asterisks=False, 
        escape_underscores=False, 
    )
    # wrap it
    md_content_split: list = md_content.splitlines() # split into paragraphs, to be wrapped separately
    md_content_wrapped_split: list = []
    # wrap each paragraph
    for paragraph in md_content_split:
        md_content_wrapped_split.append(
            textwrap.fill(
                paragraph,
                width = text_wrap,
                break_long_words = True
            )
        )
    md_content = "\n".join(md_content_wrapped_split)
    # add media stuff if there is media 
    if media_attachment:
        len_m_a_p = len(media_attachments_previewable)
        if len_m_a_p > 1:
            plural_or_no = "images" if len_m_a_p > 2 else "image"
            md_content += f"\n(view {len_m_a_p-1} more {plural_or_no} on original post)\n"
    md_content_y = md_content.count("\n") + 1

    # get the avatar
    pfp = Image.open(requests.get(avatar, stream=True).raw)
    # make it smaller
    pfp_size = 4 + (text_size*2) + (small_margin*2) # 84
    pfp.thumbnail((pfp_size, pfp_size))
        
    # make a new image
    # this will be the final image
    x = int((2*x_padding)+max_x)
    y = int((2*y_padding)+(pfp_size)+(text_size)+(text_size*md_content_y)+text_size+media_attachment_y) 

    res = Image.new(
        mode = "RGB",
        size = (x, y),
        color = (235, 235, 235)
    )
    # mask it for pretty rounded corners
    res.putalpha(rounded_mask(res, 50))

    # paste the pfp onto the blank image, with its mask
    res.paste(
        im = pfp,
        box = (x_padding, y_padding),
        mask = rounded_mask(pfp, 25)
    )

    # now we will be working with text!
    # import some fonts
    try:
        # use font files - might throw an OSError if font is not installed
        font_regular = ImageFont.truetype("assets/font/RobotoMono-Regular.ttf", size=text_size)
        font_medium = ImageFont.truetype("assets/font/RobotoMono-Medium.ttf", size=text_size)
        font_bold = ImageFont.truetype("assets/font/RobotoMono-Bold.ttf", size=text_size)
        font_light = ImageFont.truetype("assets/font/RobotoMono-Light.ttf", size=text_size)
    except OSError:
        # for some reason, you can't use font files
        req = requests.get("https://github.com/googlefonts/roboto/blob/master/src/hinted/RobotoMono-Regular.ttf?raw=true")
        font_regular = ImageFont.truetype(BytesIO(req.content), size=text_size)
        req = requests.get("https://github.com/googlefonts/roboto/blob/master/src/hinted/RobotoMono-Medium.ttf?raw=true")
        font_medium = ImageFont.truetype(BytesIO(req.content), size=text_size)
        req = requests.get("https://github.com/googlefonts/roboto/blob/master/src/hinted/RobotoMono-Bold.ttf?raw=true")
        font_bold = ImageFont.truetype(BytesIO(req.content), size=text_size)
        req = requests.get("https://github.com/googlefonts/roboto/blob/master/src/hinted/RobotoMono-Light.ttf?raw=true")
        font_light = ImageFont.truetype(BytesIO(req.content), size=text_size)
    
    draw = ImageDraw.Draw(res)
    # add the display name
    draw.text(
        xy = (x_padding+pfp_size+(small_margin*3), y_padding+2),
        text = shorten_str(display_name, text_wrap-10),
        font = font_bold,
        fill = (0, 0, 0)
    )
    # add the acct below it
    draw.text(
        xy = (x_padding+pfp_size+(small_margin*3), y_padding+2+text_size+small_margin),
        text = f"@{shorten_str(username, (text_wrap-10)/2)}@{domain}",
        font = font_regular,
        fill = (70, 70, 70)
    )   
    # add the content
    draw.text(
        xy = (x_padding, y_padding+4+text_size+small_margin+text_size+(text_size)),
        text = md_content,
        font = font_regular,
        fill = (0, 0, 0)
    )
    # add the image 
    if media_attachment: 
        res.paste(
            im = media_attachment,
            box = (x_padding, int(y_padding+pfp_size+text_size+text_size+(text_size*md_content_y)+text_size)),
            mask = rounded_mask(media_attachment, 50)
        )
        
    # show the image, for testing purposes 
    # res.show()

    return res

