Title: Creating Games in Streamlit
Date: 2020-10-02 12:00
Category: Python, Streamlit

A while back I had the idea that 9yo and I would
program a bunch of simple games together and she'd get
interested in coding. Well, we did program a bunch of simple games together:

* [Guessing Game](https://github.com/joelgrus/learning-my-kid-to-code/blob/master/guessing_game.py) - the computer picks a random number, you guess, it tells you "too high" or "too low" and then you try again
* [Mad Libs](https://github.com/joelgrus/learning-my-kid-to-code/blob/master/madlib.py) - you know it from when you were a kid, I found a bunch of madlibs that were part of a Microsoft EMNLP paper and used those
* [Hangchicken](https://github.com/joelgrus/learning-my-kid-to-code/blob/master/hangchicken.py) - like hangman, but with a chicken instead
* [Mastermind](https://github.com/joelgrus/learning-my-kid-to-code/blob/master/mastermind.py) - the classic, the computer picks a sequence and you have to guess it

But it failed to create any interest in coding. What it did create an interest in was using my computer to play Mad Libs.

Which was fine, but I wanted her to be able to play when I wasn't around (or when I was using my computer for something else).

And then last week I came into possession of a beta invite to [the new Streamlit sharing feature](https://www.streamlit.io/for-teams). If I could just turn these games into Streamlit apps, then they could be hosted online.
And she could play them whenever she wanted.

However, there are several ways in which games are at odds with the Streamlit paradigm. 
And so it actually took me a long time to get them successfully implemented.
Here are some of the things I learned.

# Game State

Streamlit apps are not exactly "stateless", but (for the most part) if you build a Streamlit app
its state is determined by the states of its widgets. 
Moving sliders and clicking buttons and filling in
text fields creates an application state, but (1) it's not hidden from the user, and (2) the user can change it directly.
These are not desiderata for a "game state".

Fortunately, it is well known that you can abuse Streamlit's caching mechanism 
to create persistent state. The pattern I initially used looks like this:

```python
@dataclasses.dataclass 
class GameState:
    number_to_guess: int
    game_number: int = 0
    game_over: bool = False

@st.cache(allow_output_mutation=True)
def persistent_game_state() -> GameState:
    return GameState(random.randint(1, 1000))

state = persistent_game_state()

if st.button("new game"):
    state.number_to_guess = random.randint(1, 1000)
    state.game_number += 1
    state.game_over = False
```

Normally I avoid dataclasses on account of their being mutable,
but here that's what we need. `GameState` contains whatever state our game needs.
In Mad Libs, that's a randomly chosen story. In Hangchicken, that's the word to guess
and the letters already guessed. And so on. Most of the games also have a `game_over` flag
to disable the inputs and an incrementing `game_number` so that new games' inputs can have
different keys. More on that below.

The `persistent_state` function takes no arguments and is decorated with `st.cache` which
makes the `GameState` instance it returns a singleton. When an input value changes and the app reruns,
the same `state` object sticks around, which is what we want.

Finally, we add a "new game" button that resets the game state for a new game.

# Game Number

Many of my first attempts had a nasty bug where if, for example,
your text input for Hangchicken had a letter in it, then when you clicked
"new game" it would start by guessing that letter. Eventually what I realized
was that that text input needed to have a `key` that depended on an incrementing game number.
That way when you click "new game" the key changes and you get a (logically) different text input.
(I think.)

# Mind the Order

By far the most difficult part to figure out was the order of operations. 
What I mean is this: my original hangchicken game (which ran in the terminal)
showed you the chicken, then the word, then the letters you'd guessed; and then asked for your input.
Indeed, a terminal game basically has to put the input last.

![hangchicken in the terminal]({static}images/hangchicken_terminal.png)

My initial attempts at the game mimicked this order and produced a weird off by 1 error
where you'd guess a letter, and then nothing would happen, and then you'd guess a second letter,
and then the first letter would show up. This drove me crazy (and I'm still not entirely sure I get it),
but I think it has to do with how state "flows through" the Streamlit app.

Eventually I realized that I needed to have the text input _before_ the outputs,
so that when it was updated the outputs would update appropriately. But this took me a long time
to figure out.

![hangchicken in streamlit]({static}images/hangchicken_streamlit.png)

I had similar problems pretty much in all the games,
but once I figured it out I figured it out.

# Text Inputs

One annoying thing you can notice in the above picture 
is that after you guess a letter the text input doesn't clear itself,
you have to backspace and then guess the next letter. I tried to address this
by making the text input `key` depend both on the game number and on how many letters
you'd guessed so far, but this reintroduced a variant of the "off by 1" error I described
above and I couldn't figure out how to fix it. So you have to backspace.

# Avoid the Loop

I made many false starts that tried to use a `while` loop
and keep rendering down the page much as you'd do in the terminal.
It's possible there's a way to make this work, but I couldn't figure it out.
In any case, it was intended as a second-best solution, and since I figured out
the first-best solution, I didn't need it.

# Flat is Better than Nested, But...

Streamlit apps tend to be more nested than I'd like, 
because there's so much conditional rendering,
and these games are no exception:

```python
if not state.game_over:
    guess = st.text_input(
        f"guess a number between 1 and {HI}", 
        key=state.game_number)

    if guess:
        try:
            guess = int(guess)
            state.num_guesses += 1
        # ...
```

Maybe there's a pattern that avoids this, but I couldn't think of it.

("Monads, you've invented monads.")

# Shared State

Unfortunately, our state hack results in the same state for every client.
This doesn't matter if one person is playing the game locally, but it matters 
a lot if you're hosting the app publicly.
If you were to play hosted Hangchicken, you and everyone else playing
would be making guesses in the same game, which would cause a giant mess.

You can imagine some games for which that would be a feature,
but it's harder to imagine those games as Streamlit apps,
as you'd likely want your browser to get notified when someone else
performs an action in her browser. (It's possible there are deep Streamlit
hacks that allow this, but I don't know them.)

Here's a little multiplayer plotting app that illustrates the issue:

[multiplayer plotting app](https://s4a.streamlit.io/joelgrus/collaborative-regression/master/app.py/+/)

Everyone is adding points to the same canvas. Make something pretty.

# Unsharing the State

It turns out to be relatively simple to unshare the state.
You just make your "singleton" function depend on the session id.
(_Getting_ the session id is less simple.)

```python
@st.cache(allow_output_mutation=True)
def persistent_game_state(session_id: str) -> GameState:
    return GameState(random.randint(1, 1000))

session_id = st.report_thread.get_report_ctx().session_id
state = persistent_game_state(session_id)
```

Now each browser session (i.e. game player)
gets their own copy of the state, and hence their own game.

# The Thing About Caching

Unfortunately, there's still a problem, and that's that the app
has a "clear cache" button. And when you clear the cache, you clear it for everyone.

So we need to be even more devious and attach the state to the session object:

```python
def persistent_game_state() -> GameState:
    session_id = st.report_thread.get_report_ctx().session_id
    session = st.server.server.Server.get_current()._get_session_info(session_id).session
    if not hasattr(session, '_gamestate'):
        setattr(session, '_gamestate', GameState(random.randint(1, 1000)))
    return session._gamestate

state = persistent_game_state()
```

And finally we have a nice app that supports multiple players!

# Refactoring

Of course, that's a repeated mess, so we might as well pull it out into its own module:

```python
from typing import TypeVar

import streamlit as st

StateT = TypeVar('StateT')

def persistent_game_state(initial_state: StateT) -> StateT:
    session_id = st.report_thread.get_report_ctx().session_id
    session = st.server.server.Server.get_current()._get_session_info(session_id).session
    if not hasattr(session, '_gamestate'):
        setattr(session, '_gamestate', initial_state)
    return session._gamestate
```

Which means that our games can then just import that function and do

```python
state = persistent_game_state(initial_state=GameState(random.randint(1, 1000)))
```

(Yes, it's inefficient to recreate that initial state and throw it away each time.
 Avoiding that is left as an exercise for the reader.)

# When Are They Going To Get to the Fireworks Factory

Right, the games. The original code is at

[github/joelgrus/learning-my-kid-to-code](https://github.com/joelgrus/learning-my-kid-to-code)

The Streamlit-ified versions are all at 

[github/joelgrus/streamlit-games](https://github.com/joelgrus/streamlit-games)

If you clone that repo you can play them locally with e.g.

```bash
streamlit run hangchicken.py
```

and so on. Here are links to the specific games:

## Guessing Game

* [code for original terminal version](https://github.com/joelgrus/learning-my-kid-to-code/blob/master/guessing_game.py)
* [code for Streamlit version](https://github.com/joelgrus/streamlit-games/blob/master/guessing_game.py)
* [PLAY IT ONLINE](https://s4a.streamlit.io/joelgrus/streamlit-games/master/guessing_game.py/+/)

## Hangchicken (Joel's favorite!)

* [code for original terminal version](https://github.com/joelgrus/learning-my-kid-to-code/blob/master/hangchicken.py)
* [code for Streamlit version](https://github.com/joelgrus/streamlit-games/blob/master/hangchicken.py)
* [PLAY IT ONLINE](https://s4a.streamlit.io/joelgrus/streamlit-games/master/hangchicken.py/+/)

## Mad Libs (9yo's favorite!)

* [code for original terminal version](https://github.com/joelgrus/learning-my-kid-to-code/blob/master/madlib.py)
* [code for Streamlit version](https://github.com/joelgrus/streamlit-games/blob/master/madlibs.py)
* [PLAY IT ONLINE](https://s4a.streamlit.io/joelgrus/streamlit-games/master/madlibs.py/+/)

## Mastermind

* [code for original terminal version](https://github.com/joelgrus/learning-my-kid-to-code/blob/master/mastermind.py)
* [code for Streamlit version](https://github.com/joelgrus/streamlit-games/blob/master/mastermind.py)
* [PLAY IT ONLINE](https://s4a.streamlit.io/joelgrus/streamlit-games/master/mastermind.py/+/)

# And You?

Let me know if you come up with any cool Streamlit games. Or if there's an easier way to do some of the things I did.