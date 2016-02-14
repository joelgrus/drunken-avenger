Title: Building a Stupid Data Product, Part 2: The Web Service (Haskell)
Date: 2016-02-15 08:00
Category: Haskell, Hacking, Data, Data Science

(<a href = "">part 1</a>, <a href = "">part 3</a>)

Last time we <a href = "">collected and processed the data</a> for generating
stupid fake elementary school science questions and answers. The important parts
to remember are

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

Next we define a few types for dealing with tokens and our sentinel values:

```haskell
type Token = String

type GetNextToken = Token -> IO Token

start :: Token
start = "__START__"

stop :: Token
stop = "__STOP__"
```

A token is just a string, that's pretty simple. And the type `GetNextToken`
represents a function that takes a `Token` and returns an `IO Token`. If you
are not a Haskell person, you are at this point wondering

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
  if nextToken == stop
    then return []                  -- empty list in an IO context
    else liftA2 (:) (pure nextToken) (tokensFrom nextToken getNext)
```

This shouldn't be hard _conceptually_, it's just recursion:

* `tokensFrom` takes a start `Token` and a `GetNextToken` function
* it calls the `GetNextToken` function on the starting `Token`
* if `nextToken` is our `stop` sentinel, the result is an empty list;
* otherwise, the result is the list whose first element is `nextToken`,
  and whose subsequent elements are the results of `tokensFrom nextToken`.

In _reality_, it's complicated because of the need to do things in an effectful
context. The `do` is
<a href = "https://en.wikibooks.org/wiki/Haskell/do_notation">sugar</a> for
working in the `IO` context. In particular, it allows us to pull the `Token`
value out of the result of a `GetNextToken` call. That is, while `getNext` returns
an `IO Token`, as long as we're inside the `do` block for an `IO` context, we can
use `<-` to "get the `Token` out."

If we find `stop`, the result is `return []`. Notably, this is not the `return`
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

Next we want to turn a list of `Token`s into a `String`. Naively we could use
Haskell's `unwords`, which just uses spaces everywhere. But we don't want to put
spaces before punctuation marks, so we'll write our own:

```haskell
smartJoin :: [Token] -> String
smartJoin = dropWhile (== ' ') . concat . addSeparators
  where
    addSeparators = concatMap addSeparator
    addSeparator word
      | word `elem` ["?", ",", "."] = ["",  word]
      | otherwise                   = [" ", word]
```

The first thing we do is `addSeparators`, which turns each word into a list
`[separator, word]` and then concatenates the resulting lists.
If the word is punctuation, the separator is an empty string.
Otherwise it's a space.

So, for instance, if you were to call

```haskell
addSeparators ["What", "is", "love", "?"]
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
generate = fmap smartJoin . tokensFrom start
```

To be a jerk, I wrote it in point-free style, it's the same as if I'd done

```haskell
generate nextToken = fmap smartJoin (tokensFrom start nextToken)
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

loadTransitions :: String -> IO Transitions
loadTransitions = fmap (fromJust . decode) . BS.readFile
```

Here `Transitions` will be a `Map` (like a dictionary)
whose keys are `Token`s and whose values are lists of `Token`s.

And `loadTransitions` is another point-free function. It involves the pieces
(with types specialized to this instance)

```haskell
BS.readFile :: FilePath -> IO BS.ByteString
decode :: BS.ByteString -> Maybe Transitions
fromJust :: Maybe Transitions -> Transitions
fmap :: (a -> b) -> IO a -> IO b
```

That is, we read a file (which gets us some bytes in an `IO` context)
and then we lift `fromJust . decode` (which deserializes those bytes
into a `Transitions` object, crashing if it can't) into the `IO` context.
This isn't a "safe" way to do things (usually we'd want to check that
`decode` doesn't return `Nothing` and deal with that somehow),
but because we generated the JSON ourselves, we know it's safe:

```haskell
questionTransitions :: IO Transitions
questionTransitions = loadTransitions "questions.json"

answerTransitions :: IO Transitions
answerTransitions = loadTransitions "answers.json"
```

Remember that the abstraction we used was

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
    _           -> return stop  -- this shouldn't happen, but let's be safe
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

*Finally*, we're ready to create the API. After all we've done, this part is
pretty anti-climactic. To start with, we define our API:

```haskell
type API = "question" :> Get '[JSON] Question
```

It has a single endpoint "question", which responds to HTTP GET requests
and returns a `Question` serialized into JSON. Our server just implements
this API:

```haskell
getRandomQuestionUsingTransitions :: IO Question
getRandomQuestionUsingTransitions = do
  qt <- questionTransitions
  at <- answerTransitions
  randomQuestion 4 (randomNextToken qt) (randomNextToken at)

server :: Server API
server = liftIO getRandomQuestionUsingTransitions
```

All the `server` does is get a random `Question` (in an `IO` context)
and "lift" it into the `Server` context.

There is a tiny amount of more boilerplate:

```haskell
startApp :: IO ()
startApp = run 8080 $ simpleCors $ app

app :: Application
app = serve api server

api :: Proxy API
api = Proxy
```

which basically just says to serve this on port 8080,
and to use some
<a href = "https://developer.mozilla.org/en-US/docs/Web/HTTP/Access_control_CORS">CORS</a>
middleware to allow cross-origin requests.

AND THAT'S IT. If you build and run it, you'll end up with a service running on
localhost:8080:

```bash
$ curl http://localhost:8080/question
{"answers":["a rainstorm lasting several times","preventing too many babies the fall leaves","worms from the morning.","conserving water."],"correctAnswer":0,"questionText":"In order of behavior is most important to make life must first"}
```

## The Punchline

I spent a couple of hours trying to deploy this to an EC2 machine,
failing miserably. The generated executable depends on a bunch of libraries on
my system. When I tried to statically include those, the compilation failed.
And the EC2 machine was way too underpowered to install `stack` and build it
there. The Internet/StackOverflow was not a lot of help.

At the end of the day, I just rewrote it in <a href = "https://github.com/joelgrus/science-questions/tree/master/python-flask">flask</a>. :sad_face:

That said, it's up and running at `http://54.174.99.38/question`:

```bash
$ curl http://54.174.99.38/question
{"questionText": "Which system?", "answers": ["Absorbing water plants than the air pollution", "It will be healthy", "flood the air pollution", "tying a great gardener."], "correctAnswer": 0}
```

But it's a cheap EC2 nano instance, so please be gentle.

## Next Time

In the third (and final) post, we'll <a href = "">build a quiz webapp</a>
that uses this service.
