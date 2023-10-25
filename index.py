from mastodon import Mastodon
from mastodon.streaming import StreamListener
from keep_alive import keep_alive
import time
from io import BytesIO
from image_gen import gen_image
from markdownify import markdownify as md
import os
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("TOKEN")

# set up Mastodon
mastodon = Mastodon(
	access_token = ACCESS_TOKEN,
	api_base_url = "https://fosstodon.org"
)

print("Bot is ready!")

# useful tool; probably won't use

def get_id(url: str):
	return url[-18:]

def main(invocation_post):
	t = time.localtime()
	current_time = time.strftime("%H:%M:%S", t)

	# make sure that the person who did it is me
	if invocation_post["account"]["id"] in [mastodon.me()["id"], 109693174502836599]:
		if invocation_post["in_reply_to_id"] != None:

			post: dict = mastodon.status(id=invocation_post["in_reply_to_id"])
			
			# get the image
			image = gen_image(post=post)
			# save the image to a buffer
			buffer = BytesIO()
			image.save(buffer, "png")
			buffer.seek(0)
			
			# get alt text using content
			# change the content to markdown so I don't have to do my job
			md_content = md(
				post["content"], 
				strip=["a"], 
				escape_asterisks=False, 
				escape_underscores=False, 
			)

			media = mastodon.media_post(
				media_file = buffer,
				description = f"post by @{post['account']['acct']}: {md_content}",
				mime_type = "png"
			)

			res = mastodon.status_reply(
				to_status =  invocation_post,
				status = "Here's an image of the post you replied to!",
				media_ids = media["id"],
				visibility = "direct",
				spoiler_text = "bot reply"
			)

			# mastodon.status_delete(invocation_post["id"])
			print(f"{current_time} Found a post {invocation_post['id']} and replied accordingly")

		else:
			print(f"{current_time} Found a post and it was me but it wasn't a reply to anything")
	else:
		print(f"{current_time} Found a post but it wasn't me")

print("Set up done")

keep_alive()

# Setup StreamListener
class Listener(StreamListener):
	def on_update(self, invocation_post):
		if "mastoimagebot_!" in invocation_post["content"]:
			main(invocation_post)
		else:
            t = time.localtime()
            current_time = time.strftime("%H:%M:%S", t)
            print(f"{current_time} Found a post by {invocation_post['account']['acct']}. Ignoring.")

listener = Listener()

# Start streaming and listening for mentions
mastodon.stream_user(listener=listener)
