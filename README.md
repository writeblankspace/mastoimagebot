# mastoimagebot

A bot written in Python that allows users to turn Mastodon posts into beautiful, shareable images.

**NOTE: This is a personal project done for fun. I may abandon it whenever I want**

![A sample of the resulting image](https://github.com/writeblankspace/mastoimagebot/assets/75297066/209c9f7a-5b0b-4097-a24a-6630e025e480.png)

## Usage

Reply to any post with `mastoimagebot_!` and the bot will reply with the image (the post will be in mentioned-only visibility so as to not bother other users).

Please note that the bot I am currently hosting will only reply to messages made by my user or the account that the bot is currently running in.

## Self-hosting?

You might have to alter some code. I didn't develop this with 'running it yourself' in mind. Perhaps that'll change in the future, but whatevs.

As the bot currently only replies to me, you will have to get rid of an if statement in index.py.

You may also need to set some environment variables like the access token for the bot's account.
