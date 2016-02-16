Title: Building a Stupid Data Product, Part 2: The Web Service (Haskell)
Date: 2016-02-15 08:00
Category: Haskell, Hacking, Data, Data Science

(<a href = "/2016/02/15/building-a-stupid-data-product-part-1-the-data-python/">part 1</a>,
 <a href = "/2016/02/15/building-a-stupid-data-product-part-3-the-single-page-app-purescript/">part 3</a>)

Last time we
<a href = "/2016/02/15/building-a-stupid-data-product-part-1-the-data-python/">collected and processed the data</a>
for generating stupid fake elementary school science questions and answers. The
important parts to remember are

1. we generated two files `questions.json` and `answers.json`
   containing _transition dictionaries_ mapping each word to an array / list of
   possible following words, and
2. we used _sentinel_ tokens `__START__` and `__STOP__` to indicate the beginning
   and end of sentences.

In this post we'll use a Haskell library called
<a href = "https://haskell-servant.github.io/">servant</a>
to build a web service that generates and returns random questions.
If you know Haskell, I'm sure you can find fault with the way I did things,
but if you don't know Haskell you might find it educational and/or mind-expanding.

(Code, as always, is on <a href = "https://github.com/joelgrus/science-questions">GitHub</a>.)

We'll do this in four steps:

1. define some types
2. write code that can generate a random question, given an (abstract) `GetNextToken`
   function
3. implement a (concrete) `GetNextToken` based on our transitions
4. create an API that serves up the random questions

## The Types

Let's start with the types. We need to define the `Question` that our web service
will return. In our API, a question will have a `questionText`, a list/array of
`answers` (which are just strings), and an integer indicating the index of the
`correctAnswer`. Pretty simple:

```haskell
data Question = Question
  { questionText  :: String
  , answers       :: [Answer]
  , correctAnswer :: Int
  } deriving (Eq, Show)

type Answer = String

$(deriveJSON defaultOptions ''Question)
```

The last line is (I believe) some template Haskell voodoo
that makes it so our service knows how to serialize a `Question` to
JSON (since we can't send Haskell objects over the wire). I don't understand it,
I just copied it from the docs.

Now we need to define a type for our tokens. One of the benefits of working in
a nicely-typed language is that we don't have to use "sentinel values", we can
use our type system for that:

```haskell
data Token = Start | Stop | Word String deriving (Eq, Ord)
```

So a token is either `Start`, `Stop`, or a `Word` with an associated `String`
value. The `deriving (Eq, Ord)` just makes it so that we can test two tokens
for equality and inequalities.

Since our tokens will come from deserializing JSON, we'll also need a `Read`
instance, which indicates how to parse text into `Token` objects:

```haskell
instance Read Token where
  readsPrec _ "__START__" = [(Start,  "")]
  readsPrec _ "__STOP__"  = [(Stop,   "")]
  readsPrec _ w           = [(Word w, "")]
```

Don't get hung up on the details, it does exactly what you'd expect it to do.
(If you do get hung up on the details, read <a href = "http://hackage.haskell.org/package/base-4.8.2.0/docs/Prelude.html#t:Read">the docs</a>.)

We also want to define a type alias

```haskell
type GetNextToken = Token -> IO Token
```

that represents a function that takes a `Token` and returns an `IO Token`.
If you are not a Haskell person, you are at this point wondering

1. Why does it not just return a `Token`?
2. What the hell is an `IO Token`?

For the first, Haskell is a _pure_ functional language. This means that if you
tried

```haskell
type GetNextTokenBad = Token -> Token
```

any instance of `GetNextTokenBad` would have to always return the same value
for the same input. In particular, it wouldn't be able to choose the next token
randomly. If we want side-effects like randomness
(or printing things, or reading from files),
we need to do computations in the `IO` context. So when you see

```haskell
type GetNextToken = Token -> IO Token
```

you can understand that as a function that takes a token, does something side-effectful,
and returns a new token in the `IO` context. In particular, this function doesn't
need to return the same value for the same inputs, but also you can only *use* it
in a context that allows side effects. More on that in a bit.

## Generating Random Questions

Now we're ready to write the code for generating a sentence. This is where things
start to get a little complicated. We'll break it into two parts. First, given
a starting `Token` and a `GetNextToken` function, we want to generate a list of
`Token`s in the `IO` context:

```haskell
tokensFrom :: Token -> GetNextToken -> IO [Token]
tokensFrom startToken getNext = do
  nextToken <- getNext startToken   -- nextToken :: Token
  case nextToken of
    Stop  -> return []
    token -> liftA2 (:) (pure token) (tokensFrom token getNext)
```

This shouldn't be hard _conceptually_, it's just recursion:

* `tokensFrom` takes a start `Token` and a `GetNextToken` function
* it calls the `GetNextToken` function on the starting `Token`
* if `nextToken` is `Stop`, the result is an empty list;
* otherwise, the result is the list whose first element is `nextToken`,
  and whose subsequent elements are the results of `tokensFrom nextToken`.

In _reality_, it's complicated because of the need to do things in an effectful
context. The `do` is
<a href = "https://en.wikibooks.org/wiki/Haskell/do_notation">sugar</a> for
working in the `IO` context. In particular, it allows us to pull the `Token`
value out of the result of a `GetNextToken` call. That is, while `getNext` returns
an `IO Token`, as long as we're inside the `do` block for an `IO` context, we can
use `<-` to "get the `Token` out."

If we find `Stop`, the result is `return []`. Notably, this is not the `return`
you might know from other languages. Here this is

```haskell
return :: a -> IO a
```

which sticks a value (in this case the empty list) into an IO context. So, since
`[]` is a `[Token]`, `return []` is an `IO [Token]`.

The last line is even uglier. `(:)` is the "cons" operator that takes a head and
a tail and produces a list:

```haskell
(:) :: a -> [a] -> [a]
```

Here `nextToken` is a `Token`, but the recursive call to `tokensFrom` produces
an `IO [Token]`, so the types don't match up. We've already seen that we can
shove values into an `IO` context, so we could get by if we had something like

```haskell
-- | not a real operator
(:???) :: IO a -> IO [a] -> IO [a]
```

We can get there with `liftA2`, which (specialized for `IO`) looks like

```haskell
liftA2 :: (a -> b -> c) -> IO a -> IO b -> IO c
```

That is, it "lifts" a function of two arguments into an `IO` context. If you
work through the types, you get:

```haskell
liftA2 (:) :: IO a -> IO [a] -> IO [a]
```

which is exactly what we want.

[Why did I use `pure` instead of `return` to stick
`nextToken` into the `IO` context? I'm not sure, exactly. In this case they're
the same thing. In the previous instance I was using `IO` as a Monad, so I used
`return`; here I'm using it as an Applicative, so I used `pure`. That's not a
good explanation, and it's probably not even a good reason. I don't care.
(I was also trying not to say "monad" in this post, but I guess I failed.)]

Next we want to turn a list of `Token`s into a `String`:

```haskell
smartJoin :: [Token] -> String
smartJoin = dropWhile (== ' ') . concat . addSeparators
  where
    addSeparators = concatMap addSeparator
    addSeparator token = case token of
      Word w | w `elem` ["?", ",", "."] -> ["",  w]
      Word w                            -> [" ", w]
      _                                 -> []
```

The first thing we do is `addSeparators`, which turns each `Word` into a list
`[separator, word]` and then concatenates the resulting lists.
If the `Word` is punctuation, the separator is an empty string.
Otherwise it's a space.

(We should never call `smartJoin` on a list that includes the `Start` or `Stop`
 tokens, but just in case we add in an empty list, which is the same as ignoring
 the token.)

So, for instance, if you were to call

```haskell
addSeparators [Word "What", Word "is", Word "love", Word "?"]
```

you would get

```haskell
[" ", "What", " ", "is", " ", "love", "", "?"]
```

We then call `concat` on that to concatenate all the strings

```haskell
" What is love?"
```

and `dropWhile (== ' ')` to get rid of the leading spaces. (I know, sort of clunky.)

Now we're ready to implement our sentence generator:

```haskell
generate :: GetNextToken -> IO String
generate = fmap smartJoin . tokensFrom Start
```

To be a jerk, I wrote it in point-free style, it's the same as if I'd done

```haskell
generate nextToken = fmap smartJoin (tokensFrom Start nextToken)
```

Here `tokensFrom` generates `IO [Token]` (an list of tokens in an effectful context)
and `fmap` lifts `smartJoin` (which maps `[Token] -> String`) into the `IO`
context, resulting in our desired `IO String`.

And finally we can create our `Question` generator:

```haskell
randomQuestion :: Int -> GetNextToken -> GetNextToken -> IO Question
randomQuestion numAnswers getNextQuestionToken getNextAnswerToken =
  Question <$> generate getNextQuestionToken
           <*> replicateM numAnswers (generate getNextAnswerToken)
           <*> randomRIO (0, numAnswers - 1)
```

It takes an `Int` indicating how many answers the question should have.
And it needs two `GetNextToken` functions, one for generating `questionText`
and the other for generating `Answer`s.

You can think of `<$>` and `<*>` as
plumbing to lift the `Question` constructor into the
`IO` context. That's a Haskell-y way of doing (in essence)

```haskell
-- the constructor is in essence
-- Question :: String -> [Answer] -> Int -> Question

makeEffectfulQuestion :: IO String -> IO [Answer] -> IO Int -> IO Question
makeEffectfulQuestion = liftA3 Question
```

Here the `IO String` comes from `generate`-ing the question,
the `IO [Answer]` comes from using `replicateM` to `generate` multiple answers,
and the `IO Int` comes from choosing a random "correct answer".

## Using Transitions

Now that we have a way to generate `Question`s using `GetNextToken` functions,
we have to figure out how create `GetNextToken` functions from the
transition maps we generated last time. We serialized them as JSON,
but now we want a typed way to work with them in Haskell:

```haskell
type Transitions = M.Map Token [Token]
```

Here `Transitions` is a `Map` (like a dictionary)
whose keys are `Token`s and whose values are lists of `Token`s.

However, our _serialized_ map of transitions is a dictionary whose keys are
_strings_ and whose values are _lists of strings_. That means we need to
deserialize it and then convert the strings to `Token`s:

```haskell
loadTransitions :: String -> IO Transitions
loadTransitions = fmap (textToTokens . fromJust . decode) . BS.readFile
  where textToTokens = M.map (map read) . M.mapKeys read
```


Our `loadTransitions` is another point-free function. It reads a file
(which gets us some bytes in an `IO` context), and then uses `fmap` to lift the three
composed functions into the `IO` context.

First, `decode` `Maybe`-deserializes the bytes into a map (with text keys and values).
After that, `fromJust` assumes the deserialization succeeded and pulls the map out of the `Maybe`.
Finally, `textToTokens` converts the text-texts map into a `Token`-`Token`s map.

(The `fromJust` isn't a "safe" way to do things (usually we'd want to check that
 `decode` doesn't return `Nothing` and deal with that somehow),
but because we generated the JSON ourselves, we know it's valid.)

How does `textToTokens` work? First, it calls `M.mapKeys read`, which returns the
new `Map` that results from applying `read` to each of the input `Map`'s keys.
So it returns a map whose keys are `Token`s but whose values are still lists of text.
And then we feed it into `M.Map (map read)`, which returns the `Map` that results
from calling `map read` on each of the input `Map`'s values. Those values are
lists of text, so `map read` converts each one to a list of `Token`s.
At the end of the process we have a `M.Map Token [Token]` as required.

Now we're ready to actually load the data:

```haskell
questionTransitions :: IO Transitions
questionTransitions = loadTransitions "questions.json"

answerTransitions :: IO Transitions
answerTransitions = loadTransitions "answers.json"
```

Next, remember that the abstraction we used was

```haskell
type GetNextToken = Token -> IO Token
```

so we simply need to implement a function like this that uses our `Transitions`.
First we write a function to pick a random element of a (nonempty) list.
We get a random `Int` (in an `IO` context, of course)
and use it to index into the list:

```haskell
-- will crash if the input is an empty list
pick :: [a] -> IO a
pick xs = do
  idx <- randomRIO (0, length xs - 1) -- choose a random index
  return (xs !! idx)                  -- return that element of the list
```

And then our implementation is easy, we just create a function that takes as
input a `Transitions` object and returns the corresponding `GetNextToken`
function:

```haskell
randomNextToken :: Transitions -> GetNextToken
randomNextToken transitions token =
  case M.lookup token transitions of
    Just tokens -> pick tokens
    _           -> return Stop  -- this shouldn't happen, but let's be safe
```

If you are confused about why we define it as `randomNextToken transitions token`,
substitute in the definition of `GetNextToken`:

```haskell
randomNextToken :: Transitions -> Token -> IO Token
```

Once it's applied to a `Transitions` object, what's left is a function that
looks up a token in the `Transitions` map and pick one of the
following tokens at random.

## The API

*Finally*, we're ready to create the actual web service.
To start with, we define our API:

```haskell
type API = "question" :> Get '[JSON] Question
```

It has a single endpoint "question", which responds to HTTP GET requests
and returns a `Question` serialized into JSON.

My first attempt at implementing this turned out to be *really* slow.
After poking around at a lot of stuff, I finally figured out it was because
every reference to the effectful `questionTransitions` and `answerTransitions`
was deserializing them from disk again. Needless to say, that was not the desired
behavior.

After some digging I found <a href = "http://hackage.haskell.org/package/io-memoize-1.1.1.0/docs/System-IO-Memoize.html">System.IO.Memoize</a>, which memoizes expensive `IO` actions (like deserializing a giant transitions object).
Initially this didn't help because I was memoizing *too late*. So I moved it
right to app startup:

```haskell
startApp :: IO ()
startApp = do
  cachedQt <- eagerlyOnce questionTransitions
  cachedAt <- eagerlyOnce answerTransitions
  run 8080 $ simpleCors $ app cachedQt cachedAt
```

(Incidentally, most of this stuff is standard servant boilerplate,
 just tweaked in order to use my cached `Transitions`.)

The type of `eagerlyOnce` is

```haskell
eagerlyOnce :: IO a -> IO (IO a)
```

Since `questionTransitions` is `IO Transitions`, this means that
`eagerlyOnce questionTransitions` is `IO (IO Transitions)`. Since we're in an `IO`
context, the `<-` means that `cachedQt` and `cachedAt` are both `IO Transitions`
(and that they should memoize their values).

(The `simpleCors` is just middleware that allows our service to handle
 cross-origin requests.)

Now we can define our `Application`.

<blockquote>
Which again needs the cached transitions
as inputs, I am not very happy about the ugly way we're passing them around
everywhere, but when I tried to avoid that by e.g. moving all the helpers into
the `startApp` function, I got all sorts of cryptic "Couldn't match type"
errors, so eventually I gave up and accepted my fate.
</blockquote>

It's pretty simple (again, this is all basically servant boilerplate):

```haskell
app :: IO Transitions -> IO Transitions -> Application
app cachedQt cachedAt = serve api (server cachedQt cachedAt)
```

And finally we define the `server`:

```haskell
server :: IO Transitions -> IO Transitions -> Server API
server cachedQt cachedAt = liftIO $ do
  qt <- cachedQt
  at <- cachedAt
  randomQuestion 4 (randomNextToken qt) (randomNextToken at)
```

In an `IO` context it retrieves the cached transitions for the questions and
answers, and then it uses them to generate a random `Question`. It then uses
`liftIO` to lift the `Question` out of the `IO` context and into the `Server`
context.

There is a tiny amount of more boilerplate:

```haskell
api :: Proxy API
api = Proxy
```

AND THAT'S IT. If you build and run it, you'll end up with a (very fast)
service running on localhost:8080:

```bash
$ curl http://localhost:8080/question
{"answers":["a rainstorm lasting several times","preventing too many babies the fall leaves","worms from the morning.","conserving water."],"correctAnswer":0,"questionText":"In order of behavior is most important to make life must first"}
```

## The Punchline

After all that work, I spent a couple of hours trying to deploy this to an EC2 machine,
failing miserably. The generated executable depends on a bunch of libraries on
my system. When I tried to statically include those, the compilation failed.
And the EC2 machine was way too underpowered to install `stack` and build it
there. The Internet/StackOverflow was not a lot of help.

At the end of the day, I just rewrote it in <a href = "https://github.com/joelgrus/science-questions/tree/master/python-flask">flask</a>
and deployed that version. :sad_face

(However, it was only because I had a (much faster) flask version that I realized
 the servant version was way too slow and went down the `System.IO.Memoize` path,
 so in that sense it's a good thing!)

The flask version is up and running at `http://54.174.99.38/question`:

```bash
$ curl http://54.174.99.38/question
{"questionText": "Which system?", "answers": ["Absorbing water plants than the air pollution", "It will be healthy", "flood the air pollution", "tying a great gardener."], "correctAnswer": 0}
```

But it's a cheap EC2 nano instance, so please be gentle.

## Next Time

In the third (and final) post, we'll
<a href = "/2016/02/15/building-a-stupid-data-product-part-3-the-single-page-app-purescript/">build a quiz webapp</a>
that uses this service.
