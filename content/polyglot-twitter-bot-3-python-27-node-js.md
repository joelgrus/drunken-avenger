Title: Polyglot Twitter Bot, Part 3: Python 2.7 + AWS Lambda
Date: 2015-12-30 12:00
Category: Code, Twitter, Python, AWS, Make_GreatAgain

[The third in an (at least) 6-part series, all code <a href = "https://github.com/joelgrus/polyglot-twitter-bot">on GitHub</a> as always.]

1. <a href="http://joelgrus.com/2015/12/29/polyglot-twitter-bot-part-1-nodejs/">Node.js</a>
2. <a href="http://joelgrus.com/2015/12/29/polyglot-twitter-bot-part-2-nodejs-aws-lambda/">Node.js + AWS Lambda</a>
3. <b>Python 2.7 + AWS Lambda</b>
4. Purescript
5. Purescript + AWS Lambda
6. Bonus: Purescript + Twitter Streaming

Lambda also allows Python functions, although only Python 2.7.  In practice,
this won't affect us much, as we'll just

```python
from __future__ import print_function
```

and cross our fingers that our bot will do the right thing where Unicode
is concerned. (Or, at least, won't crash with a `UnicodeEncodeError`.)

Now, because Python isn't oriented around asynchronous callbacks,
we don't need to worry about `context.succeed` and `context.fail`,
instead we can just write the usual Python function that's done when it's done.

To work with Twitter, we'll use the
<a href = "https://github.com/ryanmcgrath/twython">Twython</a> library.
As before, we'll need to "deploy" a zip file that contains all of the dependencies
we need, which means we need to install Twython into our project directory.

Create a directory for your Python bot and in that directory run

```bash
$ pip install twython -t .
```

which should install all the Twython files right there. (There are various subtleties,
for example, if you are using `virtualenv`, or if your Python is installed
using Homebrew, which you should read about
<a href="http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html">here</a>, but which you should not expect me to understand or explain.)

Now we're ready to write our bot. In `index.py` (because why not?), let's start
with the imports we need:

```python
from __future__ import print_function
from twython import Twython
from twython.exceptions import TwythonError
import re
import json
```

As always, we need credentials, but we don't want them checked into our code.
One way is to create a `credentials.json` file

```json
{
  "consumer_key": "...",
  "consumer_secret": "...",
  "access_token_key": "...",
  "access_token_secret": "..."
}
```

which our script can just load:

```python
with open('credentials.json') as f:
  credentials = json.loads(f.read())
```

After which we can initialize the client:

```python
client = Twython(credentials["consumer_key"],
                 credentials["consumer_secret"],
                 credentials["access_token_key"],
                 credentials["access_token_secret"])
```

Of course, we also need to create our query and regular expression:

```python
query = 'make "great again" -america -filter:retweets'
rgx = r"make (.*) great again"
```

And then we just have to create the handler:

```python
def handler(event, context):
    results = client.search(q=query)
    for tweet in results["statuses"]:
        text = tweet["text"]
        # re.search matches anywhere in the string; re.I means case-insensitive
        if re.search(rgx, text, re.I):
            print(tweet["text"])
            # client.retweet will raise an error if we try to retweet a tweet
            # that we've already retweeted. to avoid having to keep track, we
            # just use a try/except block
            try:
                client.retweet(id=tweet["id"])
            except TwythonError as e:
                print(e)
```

And that's the bot!  We just need to zip it up:

```bash
$ zip -r twitter.zip *
```

and go through the exact same "create a lambda function" process as before.
(Make sure to choose "Python 2.7" as the runtime.) Probably (certainly) you don't need
both the Node bot and the Python bot active at the same time, so make sure to
disable the event source for one of them.

Next post we'll dive into the crazy world of Purescript!
