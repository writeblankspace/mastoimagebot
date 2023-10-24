    url: str = post["url"]
    account: dict = post["account"] # more on this later
    content: str = post["content"] # this is html... might cause problems but whatevs
    media_attachments: list = post["media_attachments"] # list of media dicts

    # get account stuff
    acct: str = account["acct"] # username@domain.com
    display_name: str = account["display_name"] # display name, aka what people usually see
    avatar: str = account["avatar_static"] # URL for avatar, but not a gif

