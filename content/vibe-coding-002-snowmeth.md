Title: Vibe Coding 2 -- SnowMeth - an AI Novel-Writing Assistant
Date: 2025-07-23 09:00
Category: Vibe Coding, Claude, Writing

I have started several novels, although I have never finished one.
Can AI maybe help with that?

One way of writing a novel I have tried is the 
[Snowflake method](https://www.advancedfictionwriting.com/articles/snowflake-method/),
so named because of its fractal nature: 
start with a one sentence summary,
expand it to a paragraph,
expand that to several pages,
make a list of the chapters, and so on.

As I've been experimenting with AI, I was curious: can an AI use the Snowflake method to write a novel?

The answer is: sort of!

(I am not a front-end developer or a designer, so forgive me my crimes in those areas.)

![step-10]({static}images/snowmeth-step-10.png)

Claude Code and I spent a couple of days putting together a prototype
using 
[dspy](https://dspy.ai/) for the AI agents,
[Gemini 2.5 Flash-Lite](https://developers.googleblog.com/en/gemini-25-flash-lite-is-now-stable-and-generally-available/) for the LLM,
and React for the front-end.

(I tried getting Gemini Code to pitch in a bit whenever I timed out of Claude credits, but it [deleted my database](https://x.com/joelgrus/status/1947812286959390805), so it lost its coding privileges.)

You can work on multiple stories:

![home]({static}images/snowmeth-home.png)


You get to pick your own premise:

![step-1]({static}images/snowmeth-step-1.png)

It proceeds step by step (and you can suggest changes at any time):

![step-5]({static}images/snowmeth-step-5.png)

And at the end of it you'll end up with sort of a novel:

![step-10]({static}images/snowmeth-step-10.png)

Here is a video of the whole process:

<iframe width="560" height="315" src="https://www.youtube.com/embed/oMsm57Egpno?si=aPH_56ruk0ksxrhQ" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

And here is the project on GitHub:

[github.com/joelgrus/snowmeth](https://github.com/joelgrus/snowmeth)

This is not deployed anywhere, but you can download the code from GitHub and run it yourself with your own API keys. (Gemini 2.5 Flash-Lite is dirt cheap, I have been hacking on this for several days and have used probably $2 in tokens)

-----


As sort of a sidenote, dspy is really interesting.
Initially the appeal for me was that it allows you to do 
programmatic [optimization](https://dspy.ai/learn/optimization/overview/) of prompts (rather than having to do a lot of bespoke prompt engineering). 
But on this project I had a lot of different LLM calls and very little
interest in "optimizing" them at this stage. 

Nonetheless, from a hacking / prototyping perspective, it
was extremely ergonomic to work in terms of signatures rather than prompts:

```python
class ParagraphExpander(dspy.Signature):
    """Expand a one-sentence novel summary into a full paragraph"""

    sentence_summary = dspy.InputField(desc="The one-sentence summary to expand")
    story_idea = dspy.InputField(desc="The original story idea for context")
    paragraph = dspy.OutputField(
        desc="A compelling paragraph (3-5 sentences) that expands on the summary with more detail about the setup, conflict, and stakes"
    )
```

Even these descriptions were probably overkill, I blame Claude.

Anyway, I quite enjoyed working with dspy and will 
likely keep using it as my agent framework.