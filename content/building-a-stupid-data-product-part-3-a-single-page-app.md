Title: Building a Stupid Data Product, Part 3: A Single-Page App (PureScript)
Date: 2016-02-15 09:00
Category: PureScript, Hacking, Data, Data Science

(<a href = "">part 1</a>, <a href = "">part 2</a>)

OK, so <a href = "">last time</a> we built a web service that responds to GET
requests with random (bogus) elementary school science questions. In this third
(and last) installment, we'll create a single-page quiz app that consumes the
service.

Here's a rough stab at a wireframe:

![wireframe]({filename}/images/wireframe.png)

On the left will be the quiz questions. On the right will be the score, a
"new game" button, and self-aggrandizing stuff like links to my Twitter.
When a question appears, its answers will all be gray. Once you click on one
of the answers, it will get a bold border, and we'll color the correct answer
green and the incorrect ones red.

NOW, you know me, I never met a fancy PureScript framework I didn't like.
In this case it's the brand new
<a href = "http://www.alexmingoia.com/purescript-pux/">purescript-pux</a>,
which is a <a href = "https://en.wikipedia.org/wiki/Functional_reactive_programming">FRP</a> interface to React. (I'm not that into React, but the framework
insulates you away from using it.)

(Code, as always, is on <a href = "https://github.com/joelgrus/science-questions">GitHub</a>.)

## Types

As is almost always the case when I work with Haskell or PureScript,
I start with the types:

```haskell
newtype Question = Question {
  questionText  :: String,
  answers       :: Array Answer,
  correctAnswer :: AnswerId,
  chosenAnswer  :: Maybe AnswerId  -- which answer the player clicked on
}

type QuestionId = Int
type Answer     = String
type AnswerId   = Int
```

A few things here. The `Question` type is basically a record that looks like the
JSON responses we'll get from the service. In addition,
since our wireframe called for different formatting (i.e. different css classes)
for selected / correct / wrong answers,
I added a `chosenAnswer` field that's either `Nothing`
(if the question hasn't been answered yet)
or `Just answerId` (if the quizzee clicked on the `answerId` answer).
And in order to make it an instance of the `IsForeign` typeclass
(which makes it easy to convert the JSON responses from AJAX calls
 into typed objects) we need to wrap it in a `newtype`.

I also made type aliases for `QuestionId`, `Answer`, and `AnswerId`
just to make our code nicer and more descriptive.

Anyway, like I said, we can now define an `IsForeign` instance for `Question`:

```haskell
instance questionIsForeign :: IsForeign Question where
  read value = do
    questionText  <- readProp "questionText"  value
    answers       <- readProp "answers"       value
    correctAnswer <- readProp "correctAnswer" value
    return $ Question {
      questionText : questionText,
      answers : answers,
      correctAnswer : correctAnswer,
      chosenAnswer : Nothing
    }
```

Here `read` tells us how to turn the JSON object
`value` into a `Question`. The type of `read` is

```haskell
read :: Foreign -> Either ForeignError Question
```

You can think of this (if you like) as a function that takes a `Foreign`
object (i.e. some untyped JSON), and returns a `Question` object
in a `Either ForeignError` context. In other words, it describes a computation
that might return a `Question`
but might fail with some kind of `ForeignError`. In that context, the line

```haskell
questionText  <- readProp "questionText" value
```

tries to get the value of the `questionText` field as a String. If it succeeds,
it goes on to the next line. If it fails, the whole computation fails with the
corresponding `ForeignError`.

If we successfully read these fields, we can create a `Question` object
(with, in addition, its `chosenAnswer` field set to `Nothing`),
and then use `return` to stick it in the `Either ForeignError` context.

## FRP

Similar to our previous stabs at FRP, our app will consist of

* `State`, which keeps track of the state of the app
* `Actions`, which update the state (in a pure way) and kick off side effects
* `View`, which turns the state into a `VirtualDOM` that can be rendered by React

## State

Let's deal with the state first:

```haskell
type State = {
  score              :: Int,
  questions          :: Array Question,
  waitingForQuestion :: Boolean -- are we waiting for an AJAX call to return?
}
```

Our state consists simply of a score (the number of questions you've answered correctly),
an array of questions, and a flag that indicates whether the app is waiting for a question.
(The initial version didn't have this flag, which caused a bug where if you clicked
the "New Game" button a lot of times quickly, it would fire off a lot of AJAX requests
and then add all the questions when they eventually returned. We just want to add
one question at a time.)

## Actions

Now we can deal with the actions, of which there are three:

```haskell
data Action =
    NewGame                          -- start a new game
  | ClickAnswer QuestionId AnswerId  -- click on an answer
  | QuestionReceived Question        -- receive an AJAX response with a question
```

`NewGame` is the action to take when someone clicks on the "New Game" button.
`ClickAnswer` is the action to take when someone clicks on one of the answers.
Its payload contains the id of the question and the id of the answer, since we'll
need both of those to update the state. And `QuestionReceived` is the action to
take when the app receives the result of an (asynchronous) call to the random
question service. Its payload is the received `Question` (as a typed PureScript object).

Next we'll write the code that updates the state in response to each of these
actions. For `NewGame` we'll just replace the state with:

```haskell
initialState :: State
initialState = { score: 0, questions: [], waitingForQuestion: true }
```

For the `QuestionReceived` action, we just append the question to
`state.questions`. (That's what `snoc` does. It's `cons` backward.)
The only subtlety involves the `waitingForQuestion` flag;
if it's `false` then we _don't_ add the question;
if it's `true` then we set it to `false`. The flag ensures that we add
at most one question per "intra-game question request".

```haskell
appendQuestion :: Question -> State -> State
appendQuestion question state =
  if state.waitingForQuestion
  then state { questions = snoc state.questions question,
               waitingForQuestion = false }
  else state
```

And we need a function that updates the state after a `ClickAnswer` action.
It needs to know the `QuestionId` and `AnswerId` that were clicked on.

```haskell
answerClicked :: QuestionId -> AnswerId -> State -> State
answerClicked questionId answerId state =
  { score : newScore, questions: newQuestions, waitingForQuestion: true }
  where
    q = case state.questions `unsafeIndex` questionId of Question q' -> q'
    newScore = state.score + (if q.correctAnswer == answerId then 1 else 0)
    answeredQuestion = Question $ q { chosenAnswer = Just answerId }
    newQuestions =
      fromJust $ updateAt questionId answeredQuestion state.questions
```

This one is a little more complicated. First we use `unsafeIndex`
to pull the clicked `Question` out of `state.questions`, and use pattern-matching
to pull the question record out of the `newtype`. We compute a new score by
adding 1 to the current if the clicked `answerId` was the `correctAnswer`.
Then we update the question at `questionId` by setting its
`chosenAnswer` property correctly.

So, at this point we have `Action`s
and we have functions that update the state in response
to each action type. Now we need to glue them together:

```haskell
-- How to update the state (and perform effects) for each action type.
update :: forall eff. Update (ajax    :: AJAX,
                              err     :: EXCEPTION,
                              console :: CONSOLE    | eff) State Action
update action state input =
  case action of
    NewGame ->
      { state: initialState
      , effects: [ requestQuestion ] }
    ClickAnswer questionId answerId ->
      { state: answerClicked questionId answerId state
      , effects: [ requestQuestion ]
      }
    QuestionReceived question ->
      { state: appendQuestion question state
      , effects: [] }
```

The `Update` function takes in an `Action`, the state, and `input`
(which is part of the plumbing for asynchronous state changes),
and returns a record with the new state and an array of side-effects.

Since we have three `Action` types, we use pattern matching to handle the
three different cases. For `NewGame`,
we reset the initial state and make an AJAX request for a new question.
For `ClickAnswer` we call our `answerClicked` function to get a new state
and also make an AJAX request for a new question. And for `QuestionReceived`
we use our `appendQuestion` function to update the state.

You're probably wondering what `requestQuestion` is. It's pretty much boilerplate
around making an AJAX call, and to be honest I don't really understand it well
(I mostly copied it from
<a href="http://www.alexmingoia.com/purescript-pux/docs/examples/ajax.html">the documentation</a>).

```haskell
  where
    requestQuestion =
      launchAff $ do
        res <- get questionServiceUrl
        let question = readJSON res.response :: F Question
        liftEff $ case question of
          (Left err) -> log "Error parsing JSON!"
          (Right question) -> S.send input (singleton (QuestionReceived question))
```

Here `launchAff` takes a value in an "asynchronous computation effect context",
runs it synchronously, and ignores the value. (This is fine, since we don't
need the result of the computation, we just want the callback effect.)

The asynchronous computation makes an GET request to the questionServiceUrl,
uses `readJSON` to convert the response into a `Question` object
(in the `F` context, which is a type synonym for `Either ForeignError`)
and then either logs the error (if the conversion fails)
or sends a `QuestionReceived` action (if the conversion succeeds).

(Because both the `log` and `S.send` effects operate in the
 synchronous effect context `Eff`, we have to "lift" them into the
 asynchronous effect context of `requestQuestion`.)

## View

Now it's time to produce the view. At a high level our goal is

```haskell
view :: State -> VirtualDOM
```

`VirtualDOM` is a hyperscript DSL that allows you to write stuff like

```haskell
-- This is an illustrative example, not part of our code:
view :: State -> VirtualDOM
view state = div $ do
  p $ text ("Counter: " ++ show state.counter)
  p $ do
    button ! onClick (send Increment) $ text "Increment"
    button ! onClick (send Decrement) $ text "Decrement"
```

The place where I got stuck was on how to create arbitrarily many elements
by `map`-ing over an array. Eventually I noticed that `VirtualDOM` has a
`Monoid` instance, which means we can use

```haskell
foldMap :: forall a m. (Monoid m) => (a -> m) -> Array a -> m
```

with the types in this particular case specialized as

```haskell
foldMap :: forall a. (a -> VirtualDOM) -> Array a -> VirtualDOM
```

which means we could do stuff like

```haskell
-- This is an illustrative example, not part of our code:
showTenUsers :: State -> VirtualDOM
showTenUsers state =
  foldMap (\user -> p $ text user.name) (take 10 state.users)
```

Now because we're using array indexes as `QuestionId` and `AnswerId`, we really
want a variant that allows the generated `VirtualDOM` elements to also depend
on the index, which I'll call `foldMapWithIndex`:

```haskell
foldMapWithIndex :: forall a. (a -> Int -> VirtualDOM) -> Array a -> VirtualDOM
foldMapWithIndex f xs = foldMap (uncurry f) pairs
  where pairs = zip xs (0 .. (length xs - 1))
```

As desired, it takes a function that generates a `VirtualDOM` from an element
and its index, `uncurry`s it (i.e. converts it from a function of two arguments
to a function of one `Tuple` argument), and `foldMap`s it over the pairs
`(element, index)`.

Now we're ready to write our view. We'll start at the highest level and work our
way down:

```haskell
view :: State -> VirtualDOM
view state = div $ do
  div ! className "sidebar" $ do
    p ! className "score" $ text ("Score: " ++ show state.score)
    button ! onClick (send NewGame) $ text "New Game"
    p ! className "twitter" $
      a ! href "http://twitter.com/joelgrus" $ text "@joelgrus"
    p ! className "github" $
      a ! href "https://github.com/joelgrus/science-questions" $
        img ! src "octocat.png"
  foldMapWithIndex renderQuestion state.questions
```

OK. So our view produces a `div` with two `VirtualDOM` children.

The first child is a "sidebar". We'll use css to float it off to the right.
It contains a `p` showing the current score,
a "New Game" button,
a link to my Twitter account,
and a link to the GitHub repo for this project.

The only two interesting parts are

* the "score", which looks into the `state` to find the score, and
* the "new game" button, which uses `send` to trigger a `NewGame` action

The second child is the output of a call to `foldMapWithIndex`, which
(as we described above) feeds each element of `state.questions`
and its index to the `renderQuestion` function.

This tells us that we must have

```haskell
renderQuestion :: Question -> Int -> VirtualDOM
```

(Or, since `QuestionId` is a type alias for `Int`, we can use the more descriptive)

```haskell
renderQuestion :: Question -> QuestionId -> VirtualDOM
renderQuestion (Question q) questionId = div $ do
  p ! className "question" $ text $ questionNumber ++ ". " ++ q.questionText
  foldMapWithIndex (renderAnswer (Question q) questionId) q.answers
  where
    questionNumber = show (questionId + 1)
```

Here we render a question as a `p` with the question number and question text,
followed by another `foldMapWithIndex` across the question's `answers`.

Now we need to write `renderAnswer`. Notice our usage: we passed it a
`Question` and a `QuestionId`, after which (since we're using
`foldMapWithIndex`) we need to end up with a function
that takes an `Answer` and an `AnswerId`:

```haskell
renderAnswer :: Question -> QuestionId -> Answer -> AnswerId -> VirtualDOM
renderAnswer (Question q) questionId answer answerId =
  div ! className classes ! clickHandlerIfUnanswered $ text answer
  where
    isAnswered = isJust q.chosenAnswer
    isChosen   = isAnswered && answerId == fromJust q.chosenAnswer
    isCorrect  = answerId == q.correctAnswer

    classes = joinWith " " $ map snd $ filter fst [
      Tuple true                          "answer",
      Tuple isChosen                      "chosen",
      Tuple (isAnswered && isCorrect)     "correct",
      Tuple (isAnswered && not isCorrect) "wrong"
    ]

    clickHandlerIfUnanswered =
      if isAnswered
      then Attrs [] [] -- no-op "attribute"
      else onClick (send $ ClickAnswer questionId answerId)
```

How on earth is rendering a measly little answer so involved? Well, two reasons.

1. Our original wireframe involved a lot of different state-dependent styles for
   answers, which means that we need to assign state-dependent classes in a
   slightly complicated way.
2. The main activity of the game involves clicking on answers, which means that
   we need to set up click handlers.

The hyperscript part is quite simple:

```haskell
  div ! className classes ! clickHandlerIfUnanswered $ text answer
```

It's a `div`, with some classes attached to it,
possibly with a click handler attached to it,
and containing the text of the answer. Simple.

The classes are determined by three boolean values:

* `isAnswered` -- has this question been answered (at all)
* `isChosen`   -- did the quizzee click *this* answer?
* `isCorrect`  -- is this the correct answer?

The logic is possibly too clever
(although all my alternative versions with lots of `if` and `then`
were really ugly), but basically it sets up an array of pairs
(boolean value, class name), throws out the pairs where the first element is false,
and joins together the class names that are left.

For the click handler, we only want answers clickable if they belong to a question
that hasn't been answered yet. The simplest way I could come up with to do that
was the `if`-`then` statement that produced either a click handler or an "empty attribute"
depending on the value of `isAnswered`.

I think that's pretty much it, other than the `main` boilerplate:

```haskell
main = renderToDOM "#app" =<< app
  { state: initialState
  , update: update
  , view: view
  , inputs: []
  }
```

## The Result

You can see it up and running
<a href = "http://joelgrus.com/experiments/science-questions/">here</a>.
The front-end is totally robust, but the back-end question service is running
on an EC2 nano instance, so try to be gentle.

![science quiz]({filename}/images/science_quiz.png)

## The Verdict

I really enjoyed working with purescript-pux,
it's probably my favorite of the PureScript frameworks I've tried.
It's pretty much brand new (I think it was announced a couple of weeks ago),
so there's not a ton of help, but I managed to figure everything out mostly.

Anyway, that's the end of our end-to-end stupid data product.
Possibly you learned something, and possibly you'll go off and
build your own stupid data product (or maybe even a not-stupid one).
If you do, let me know about it!
