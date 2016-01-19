Title: Polyglot Twitter Bot, Part 4: PureScript
Date: 2015-12-31 9:00
Category: Code, Twitter, PureScript, AWS, Make_GreatAgain

[The fourth in an (at least) 6-part series, all code <a href = "https://github.com/joelgrus/polyglot-twitter-bot">on GitHub</a> as always.]

1. <a href="http://joelgrus.com/2015/12/29/polyglot-twitter-bot-part-1-nodejs/">Node.js</a>
2. <a href="http://joelgrus.com/2015/12/29/polyglot-twitter-bot-part-2-nodejs-aws-lambda/">Node.js + AWS Lambda</a>
3. <a href="http://joelgrus.com/2015/12/30/polyglot-twitter-bot-part-3-python-27-aws-lambda/">Python 2.7 + AWS Lambda</a>
4. <b>PureScript</b>
5. PureScript + AWS Lambda
6. Bonus: PureScript + Twitter Streaming

I know, you're thinking, "I've already read three parts of this series,
and I haven't heard one mention of Haskell. Who are you and what have you done
with Joel?"

Well, AWS Lambda doesn't support Haskell. (Yet.) Instead we'll work in
<a href ="http://www.PureScript.org/">PureScript</a>, a very Haskell-like
language that compiles to Javascript. In particular, we'll be able to (re-)use
the Node.js `twitter` library via PureScript's foreign function interface.

[Big caveat: I am a PureScript newbie. Although the code here works,
 it's possible (indeed, likely) that it's not well-designed PureScript. And although my
 explanations reflect my understanding of what's going on, it's possible (indeed, likely)
 that some of them are totally wrong. Mostly I did this part to help me learn PureScript better.
 If any PureScript gurus are reading this, I am eager to hear what I could have done better
 or more idiomatically.]

To start with, <a href = "http://www.PureScript.org/download/">install PureScript</a>
and its build tool `pulp`.

Then we need to create a directory and initialize:

```bash
$ mkdir purescript-twitter-bot
$ cd purescript-twitter-bot
$ pulp init
$ npm init
$ npm install twitter --save
```

(It's possible that it's bad form to both `pulp init` and `npm init`, but I did both.)

A new PureScript project doesn't include by default a lot of its basic
libraries, so we'll need to install the ones we need for this project:

```bash
$ pulp dep install --save purescript-console purescript-foreign purescript-arrays purescript-strings  purescript-functions
```

Now, `pulp init` should have created a `src` subdirectory. Go there and create
`Twitter.purs`, where we'll create all of the common *types* for working
with Twitter, as well as the function to initialize the Twitter client.

```haskell
module Twitter where

import Prelude
import Data.Foreign (Foreign())
import Control.Monad.Eff (Eff())

-- | Effect type for interacting with Twitter.
foreign import data TWITTER :: !

-- | The Twitter client returned by the Javascript `Twitter()` constructor.
foreign import data TwitterClient :: *
```

What do these things mean?
In PureScript functions are (by default) <a href = "https://en.wikipedia.org/wiki/Pure_function">pure</a>.
If we want them to have side effects, we need to explicitly declare those
side effects. And a function that interacts with Twitter is necessarily impure,
since it depends on -- and possibly modifies -- the state of Twitter.
So we need to define a `TWITTER`
<a href = "http://www.PureScript.org/learn/eff/">effect</a> that we can use to
mark functions as having Twitter-based side effects (or side inputs).
(The bang `!` means that `TWITTER` is an effect.)

In comparison, the `*` means that `TwitterClient` is a *type*, this allows us
to define functions that take a `TwitterClient` as input and functions that
return a `TwitterClient` as output. (The `foreign import` means that we're not
going to define the type within PureScript, but that it's going to refer to something
we'll do in Javascript.)

Notably, these are (mostly) just *names*. We will define a (Javascript-implemented)
function that returns a `TwitterClient`, as well as other functions that take a `TwitterClient`
as input. The type system will simply enforce that any function that wants a `TwitterClient`
gets something that we've identified as a `TwitterClient`. And that any computation that
involves a `TWITTER` effect can only run in a context that allows `TWITTER` effects.

(If this all seems new and confusing, that's because it is new and confusing. Bear with me.)

We also need a type to represent Twitter credentials:

```haskell
type Credentials = {
  consumer_key :: String,
  consumer_secret :: String,
  access_token_key :: String,
  access_token_secret :: String
}
```

PureScript has easy <a href = "https://leanpub.com/PureScript/read#leanpub-auto-simple-types">record types</a>
that basically correspond to Javascript objects. That is, the `Credentials` type is (basically)
a Javascript object that has those exact four keys, and whose values are all strings.
(However, on the PureScript side it is typed, and you would get an error if you tried
  to create a `Credentials` instance with no `consumer_key` or with a numeric `consumer_secret`.)

Now we can use the Foreign Function Interface to get an instance of the Twitter client.
Let's first handle the PureScript side:

```haskell
foreign import twitterClient :: forall eff. Credentials -> Eff (twitter :: TWITTER | eff) TwitterClient
```

Yikes. The `foreign import` means that we're going to define this function in Javascript.
And the type says that this function takes as input a `Credentials` object and does something
that involves a `TWITTER` side effect and returns a `TwitterClient`.

(`Eff` is the
monad for <a href = "http://www.PureScript.org/learn/eff/">specifying native effects</a>,
and indicates that this function can only be run in a "context" that allows
`TWITTER` side effects. The `forall eff` means that the context can allow other
side effects as well.)

Now we're ready to write the Javascript side.  Create a companion file `Twitter.js`:

```js
/* global exports */
"use strict";

// module Twitter

var Twitter = require('twitter');

exports.twitterClient = function(credentials) {
  return function() {
    return new Twitter(credentials);
  };
};
```

That's it. The `module Twitter` comment is important (I think) and tells the
PureScript compiler that this goes with the `Twitter` module in `Twitter.purs`.
The code simply loads the Node.js `twitter` library and exports the `twitterClient` function
that we declared in `Twitter.purs`. Its input is a PureScript `Credentials` object
(which gets translated here into just a plain Javascript object, which is
 exactly what the `Twitter` function requires).

The only subtlety is that instead of returning the Twitter client directly,
we wrap it in a function of zero arguments. We need to do this <a href = "https://github.com/PureScript/PureScript/wiki/FFI-tips">whenever our function
returns an `Eff` context</a>. (And conversely, if you create a PureScript function
whose return value is an `Eff`, the generated Javascript function requires an
extra call, as we'll see later (and which caused me a lot of confusion)).

Let's also create simple (non-production quality) types to represent Tweets:

```haskell
type TweetId = String

type Tweet = {
  id :: TweetId,
  user :: String,
  text :: String
}

type Tweets = Array Tweet
```

So, for us, a tweet has an `id`, a `user`, and some `text`. Obviously the actual
data model is a lot richer, but this is all we'll need to build our bot.

Next we need to write the code to interface with the search API. We'll stick this
in its own module `Twitter.Search` which we'll create in `src/Twitter/Search.purs`.

```haskell
module Twitter.Search where

import Prelude (Unit())
import Data.Function
import Control.Monad.Eff (Eff())

import Twitter
```

This looks like the previous set of imports, except that now we also import the `Twitter` module
we just created, as well as the `Data.Function` module.

You see, PureScript functions are all really functions of a single variable.
If you were to have

```haskell
sum :: Int -> Int -> Int
sum a b = a + b
```

then `sum` is really a function that takes an `Int` and returns a new function `Int -> Int`.
For example `sum 2` is the function that adds 2 to any number, and `sum 2 3` is really
`(sum 2) 3`.

This means that (naively) we need to write foreign functions the same way:

```haskell
foreign import sum :: Int -> Int -> Int
```

with implementation

```js
exports.sum = function(a) {
  return function(b) {
    return a + b;
  }
}
```

If you have functions with a lot of parameters, this can get ugly really fast.
That's where `Data.Function` comes in, it provides helper functions that allow us
to write normal multiple-argument Javascript functions.

```haskell
foreign import sumImpl :: Fn2 Int Int Int

sum :: Int -> Int -> Int
sum = runFn2 sumImpl
```

with implementation

```js
exports.sumImpl = function(a, b) {
  return a + b;
}
```

The declaration `Fn2 Int Int Int` means `sumImpl` is a Javascript
function of two Int arguments that returns an Int result. And the `runFn2`
converts it into the usual curried PureScript function. The exposed `sum`
still looks the same as before, so anyone using the function doesn't need to
worry about all of these details.

Anyway, back to Twitter searching. The Twitter search API allows you to specify
a lot of options, but we'll restrict ourselves to just `q` [query] and `count`
[number of results]. And we'll provide a helper function that allows callers
to just specify the query:

```haskell
type SearchOptions = {
  q :: String,
  count :: Int
}

searchOptions :: String -> SearchOptions
searchOptions query = {
  q : query,
  count : 15
}
```

Finally, we're ready to define the search function, using the Data.Function
trick from above:

```haskell
foreign import searchImpl :: forall eff. Fn3
                                         TwitterClient
                                         SearchOptions
                                         (Tweets -> Eff (twitter :: TWITTER | eff) Unit)
                                         (Eff (twitter :: TWITTER | eff) Unit)

search :: forall eff. TwitterClient ->
                      SearchOptions ->
                      (Tweets -> Eff (twitter :: TWITTER | eff) Unit) ->
                      (Eff (twitter :: TWITTER | eff) Unit)
-- the docs suggest not using point-free style here
search client options callback = runFn3 searchImpl client options callback
```

That is, the `search` function takes a `TwitterClient`, some `SearchOptions`,
and a callback (that takes some `Tweets` as input and does something effectful
with them), and does something with a `TWITTER` effect (and returns no result).

[Incidentally, I would rather not insist that the callback include the `TWITTER`
effect. Our eventual "retweet" callback will, but you could also imagine just a
"log to the console" callback that doesn't. However, it caused me problems if I
didn't include it, so it's there.]

Then we need to define `searchImpl` in `Search.js`, which is not dissimilar to our initial
Node.js version:

```js
exports.searchImpl = function(client, searchOptions, callback) {
  // Because `searchImpl` returns a value in the Eff monad, its Javascript implementation
  // needs to return a function of no arguments.
  return function() {
    client.get('search/tweets', searchOptions, function(error, tweets, response){
      var results = tweets.statuses.map(function(tweet) {
        // Map results to our `Tweet` record type.
        // (If `Tweet` wasn't a plain old record type, we'd have to do something
        //  more complicated here.)
        return { id : tweet.id_str, user : tweet.user.screen_name, text : tweet.text };
      });
      // Similarly, because `callback` returns a value in the Eff monad, its
      // Javascript transpilation returns a function of no arguments, which means
      // that to actually *execute* the callback, we need to call the returned function.
      // Not realizing this caused me a lot of grief.
      callback(results)();

      // Because the return type is `Unit`, we just return an empty object.
      return {};
    });
  };
};
```

We similarly create a `Twitter.Retweet` module in `src/Twitter/Retweet.purs`, with just a single function:

```haskell
foreign import retweetImpl :: forall eff. Fn2
                                          TwitterClient
                                          TweetId
                                          (Eff (console :: CONSOLE, twitter :: TWITTER | eff) Unit)

retweet :: forall eff. TwitterClient ->
                       TweetId ->
                       Eff (console :: CONSOLE, twitter :: TWITTER | eff) Unit
-- the docs suggest not using point-free style here
retweet client tweetId = runFn2 retweetImpl client tweetId
```

Where `retweetImpl` is defined in `src/Twitter/Retweet.js` as

```js
exports.retweetImpl = function(client, tweetId) {
  return function() {
    client.post('statuses/retweet/' + tweetId, function(err, tweet, id) {
      console.log(err || tweet.text);
    });
    return {};
  };
};
```

Finally, we're ready to do the actual work. (So far we've just been doing the groundwork.)
As usual, we create a separate file
for credentials, here `src/MyCredentials.purs`

```haskell
module MyCredentials where

import Twitter

myCredentials :: Credentials
myCredentials = {
  consumer_key: "...",
  consumer_secret: "...",
  access_token_key: "...",
  access_token_secret: "..."
}
```

And then we stick the actual work in `src/Main.purs`. After importing all the stuff
we need, we can create a `findAndRetweet` function.

```haskell
module Main where

import Prelude
import Control.Monad.Eff
import Control.Monad.Eff.Console
import qualified Data.Array as Array
import Data.Maybe
import qualified Data.String.Regex as Regex

import MyCredentials
import Twitter
import Twitter.Search
import Twitter.Retweet

findAndRetweet :: SearchOptions ->
                  Maybe Regex.Regex ->
                  TwitterClient ->
                  Eff (twitter :: TWITTER, console :: CONSOLE) Unit
findAndRetweet options rgx client = search client options retweetMatches
  where
    -- for each tweet that passes the regex filter, send its id to `retweet`
    retweetMatches tweets = do
      foreachE (filter rgxFilter tweets) (\tweet -> retweet client tweet.id)
    -- if there's a regex, make sure it matches tweet.text
    rgxFilter tweet = case rgx of
      Just pattern -> Regex.test pattern tweet.text
      Nothing -> true
```

Given a `TwitterClient` and some `SearchOptions`, it just runs the search
using the callback `retweetMatches` defined here. And `retweetMatches` just
filters out tweets that don't match the regex (if there is one) and calls
`retweet` for each of the tweets that's left.

Finally, we just need a `main` function to do the work.

```haskell
-- This assumes MyCredentials.purs exports myCredentials :: Credentials
main :: Eff (console :: CONSOLE, twitter :: TWITTER) Unit
main = twitterClient myCredentials >>= (findAndRetweet options rgx)
  where
    query = "make \"great again\" -america -filter:retweets"
    options = searchOptions query
    rgx = Just $ Regex.regex "make (.*) great again" flags
    flags = Regex.noFlags { ignoreCase = true }
```

The type of `main` indicates that it does something that involves both
the `CONSOLE` side effect and the `TWITTER` side effect, and that it doesn't
return anything. (`Unit` is similar to other languages' `void`.)

And `>>=` is the scary <a href = "https://wiki.haskell.org/Monad_tutorials_timeline">monad</a>
bind, which grabs the `TwitterClient`
out of the `Eff` monad (recall that `twitterClient` returns an `Eff _ TwitterClient`)
and hands it to the `findAndRetweet` function, which (after currying the
search options and regex) just takes a `TwitterClient` and does its magic.

If you run this from the command line:

```bash
$ pulp run
```

it should retweet all the things!

<img src="http://i.imgur.com/l5Q0wHw.jpg" alt="RETWEET ALL THE THINGS!">

Final note: this probably seems like a lot of work. It *was* a lot of work. But
most of the work was creating a (bare-bones, toy) PureScript `Twitter` library.
If you already had such a library (which, in many applications, you would),
it would have been a lot less work, and you would just have to have written
the code in `Main.purs`.

Next time we'll get this PureScript version running on AWS Lambda. (Which might
take me a couple of days to pull together, happy new year!)
