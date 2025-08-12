Title: Vibe Coding 6 -- pymgflip
Date: 2025-08-12 12:00
Category: Vibe Coding

As my next project, I thought it would be fun to use AI
to generate memes. For many years I have used 
[imgflip](https://imgflip.com) to generate memes.
And they have an [API](https://imgflip.com/api)!
Unfortunately, they don't have an official Python library (that I could find, I found a bunch of one-GitHub-star unofficial ones).

So I thought, why not let Claude write one.

I created a CLAUDE.md that just said

```markdown
# imgflip

This is a python library that wraps the imgflip API in a type-safe way.

The imgflip API is described at:

https://imgflip.com/api

We use httpx to make API calls and provide a type-safe interface for all the API features.
```

And then I started claude in live-dangerously-mode and told it to write the library. Which it did.

(It made a couple of bad design decisions, 
 like asking the user
 to specify whether they had a paid account, 
 rather than just error-handling that case properly,
 but we corrected these in short order.)

Once it was done I ran its sample script, and this was what came out:

![drake]({static}images/when_you_finally_get_the_api_working.png)

(On Twitter someone criticized this for not being a "correct" use of the meme,
 which it isn't, but that's because the sample script just calls
"list all memes" and captions whichever one is first.)

I uploaded it to pypi so that I can use it in projects, which means you can too: 

```bash
uv add pymgflip
```

(All of the obvious names on pypi were taken, `pymgflip` was the best I could do.)

The example from the README is actually pretty good:

```python
from pymgflip import Client

client = Client(username="your_username", password="your_password")

# Create a meme
result = client.caption_image(
    template_id="61579",  # "One Does Not Simply" template
    text0="One does not simply",
    text1="Use the Imgflip API without pymgflip"
)

if result.success:
    print(f"Meme created: {result.url}")
```

![one-does-not]({static}images/one_does_not_simply.png)
