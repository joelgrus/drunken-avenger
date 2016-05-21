Title: A Simple Spot It Clone With PureScript and Pux
Date: 2016-03-30 12:00
Category: Mathematics, Code, Spot it, PureScript

Long-time readers may recall that last year I wrote a blog post
about <a href = "http://joelgrus.com/2015/06/12/on-the-mathematics-of-spot-it/">the
mathematics of Spot It</a>. (For those who don't recall, Spot It is a game where
you have a deck of cards, each of which has 8 pictures on it, where through the
magical mathematics of finite projective planes *every* two cards in the deck have
exactly one image in common.)

As I am currently in more of a
"functional front-end compile-to-JavaScript" mindset,
I thought I'd take those ideas and
build a little app, using my current favorite framework, <a href = "https://github.com/alexmingoia/purescript-pux">purescript-pux</a>.

(Code, as always, on <a href = "https://github.com/joelgrus/pux-it">GitHub</a>)

The <a href = "https://github.com/joelgrus/pux-it/blob/master/src/PuxIt/Math.purs">PuxIt.Math</a>
module is basically just the code that generates the "cards". The most relevant part is

```haskell
type Card = Array Int

createDeck :: Int -> Array Card
createDeck n = map (toIndexes <<< pointsOnLine n) (allLines n)
```

Which generates all the lines (cards) in the finite projective plane,
maps each to the set of points (images) it contains, and then replaces each
point (image) with an (arbitrary but consistent) integer (basically, its index
in the array of all points).  

After which, a "card" looks like `[1,2,3,4,5,6,7,8]`. (If you're interested in
the logic for how the cards are generated, read the previous post.)

Here we'll worry about building a front-end to play with these cards. My first
idea was to show two cards at a time, and have the player have to click on the
picture in common.

![spotit]({filename}images/spot_it.jpg)

But that's too easy to cheat (from our side), since it's trivial to generate
*two* cards with one image in common, over and over again. Eventually I decided
that what's interesting about the setup is that it *works*, and that a cooler
visualization would be to show *all* the cards, allow the player to select any
two, and have the app show the picture in common.

![puxit]({filename}images/puxit.gif)

This means a good first start would be to get some images. For the standard game
(8 images/card) we need 57 different images. After poking around
online, I found <a href = "http://www.flaticon.com/packs/glypho">a nice CC-BY set of SVG icons</a>,
which I then semi-laboriously (and mostly randomly) recolored in my text editor by choosing from
a <a href = "http://www.december.com/html/spec/colorsvg.html">list of named SVG colors</a>
and then adding `fill="purple"` and so forth to each file. I also renamed the files to
`0.svg`, `1.svg`, and so on, to make it easy to generate URLs from the cards.

Now, then, our usual FRP setup involves defining

* `State` : the current state of the app
* `Action` : the possible actions the users can take
* `Update` : how the state should change in response to actions
* `View` : how to generate the HTML that corresponds to a state (and that can trigger actions)

We'll start with some type aliases to make our code more readable:

```haskell
type Image     = Int          -- An image is just represented as an integer.
type Card      = Array Image  -- A card is just an array of images.
type Deck      = Array Card   -- A deck is just an array of cards
type CardIndex = Int          -- indexed by an integer.
```

Like we said above, our mathy card generation library represents a card as an
array of ints, and a deck is just an array of cards. Given the way we named our
image files, we can also define:

```haskell
imageUrl :: Image -> String
imageUrl image = "images/" ++ show image ++ ".svg"
```

If you wanted to use a different set of images, you could change this.

Now, then, the state for the game needs to contain the deck of cards (obviously),
as well as some indication of which cards the player has selected:

```haskell
type State = {
  cards    :: Deck,               -- The cards in the deck, in order.
  selected :: SelectedCards       -- Which cards (indexes) are selected
}
```

There are many possible ways to represent the selected cards, we'll use a simple
sum type to enforce that at most two cards can be selected.

```haskell
data SelectedCards = NoCards | OneCard CardIndex | TwoCards CardIndex CardIndex
```

There's only one possible action -- clicking on a card -- in which case we need
to know its index:

```haskell
data Action = Click CardIndex
```

The card generation library will generate the exact same cards each time. But we'd
like each game to be pseudo-unique. Accordingly, when we start a game, we'll
shuffle the cards, and we'll shuffle the images contained on each card. (Clearly
this doesn't affect the "every two cards have exactly one image in common" property.)

This means we need a function to `shuffle` an array. Because it requires randomness,
it needs to run in an effectful context:

```haskell
shuffle :: forall e a. Array a -> Eff (random :: RANDOM | e) (Array a)
shuffle xs = do
  randoms <- replicateM (length xs) random
  return $ map snd $ sortBy compareFst $ zip randoms xs
  where compareFst (Tuple a _) (Tuple b _) = compare a b
```

Given some array (of any type) `xs`, we generate a random number for each element
and `zip` them together to get an array of pairs `(rnd, x)`. We then sort that array
using the `compareFst` function, which only looks at the first element in each pair.
Finally, we call `map snd` to throw away the random numbers. (This is not
  <a href = "https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle">the most efficient way to shuffle</a>, but it's simple and it works.)

We can now write a function to create a randomized deck:

```haskell
createRandomDeck :: forall e. Int -> Eff (random :: RANDOM | e) Deck
createRandomDeck n = shuffle (createDeck n) >>= traverse shuffle
```

Here, `createDeck` is the math-y function that returns the same deck always.
We call `shuffle` on it (creating a shuffled deck in an effectful context),
and then "bind" that to `traverse shuffle`. This is possibly the most complicated
part of this code. Let's look at `traverse`:

```haskell
class (Functor t, Foldable t) <= Traversable t where
  traverse :: forall a b m. Applicative m => (a -> m b) -> t a -> m (t b)
  sequence :: forall a m. Applicative m => t (m a) -> m (t a)
```

So `traverse` takes an effectful computation (`m` is the effect), applies to
a `traversable` container (`t` is the container) and returns an effectful container
of (non-effectful) results. (Huh?) Here `t` is Array and `m` is `Eff (random :: RANDOM)`,
so this specializes to

```haskell
traverse :: forall a b. (a -> Eff (random :: RANDOM) b) ->
                        Array a ->
                        Eff (random :: RANDOM) (Array b)
```

so that `traverse shuffle` takes an array of "shufflables", shuffles each array
element individually, and returns the result in an effectful context. And now we're
ready to write our (effectful) function that generates an initial `State` for the game:

```haskell
initialState :: forall e. Int -> Eff (random :: RANDOM | e) State
initialState n = do
  cards <- createRandomDeck n
  return { cards : cards, selected : NoCards }
```

Now that we've gotten actions and state taken care of, it's time to think about
how to update the state in response to actions. Here's there's only a single
action, which makes it pretty easy:

```haskell
update :: Action -> State -> EffModel State Action (random  :: RANDOM)
update (Click i) state = { state: cardClicked i state, effects: [] }
```

The only action is `Click i`, and so we update the state using the `cardClicked i`
function, which we haven't written yet:

```haskell
cardClicked :: CardIndex -> State -> State
cardClicked i state = state { selected = toggle state.selected }
  where
    toggle NoCards                      = OneCard i       -- select card i
    toggle (OneCard s1)     | i == s1   = NoCards         -- unselect
                            | otherwise = TwoCards s1 i   -- select second card
    toggle (TwoCards s1 s2) | i == s1   = OneCard s2      -- unselect s1
                            | i == s2   = OneCard s1      -- unselect s2
                            | otherwise = TwoCards s1 s2  -- no op
```

This is a lot of lines, but conceptually it shouldn't be too hard. When you click
on a card you're never changing the deck itself, only the `SelectedCards` property.
If no cards are currently selected, we want to select the clicked card.
If one card is selected and we click that card, we want to unselect it; if we
click a different card we want to select the second card as well. And if two cards
are already selected, we either unselect one (if we clicked it), or do nothing
(if it's a different card).

At last, we're ready to create the view. As usual, we have a lot of logic that
involves the "index" of an array element, so we'll need a helper function to
`map` across elements and their indexes:

```haskell
mapWithIndex :: forall a b. (a -> Int -> b) -> Array a -> Array b
mapWithIndex f xs = map (uncurry f) $ zip xs (0 .. (length xs - 1))
```

And since we'll want to add a special CSS class to the common image between
two selected cards, we'll also need a helper function to find it:

```haskell
commonImage :: Deck -> CardIndex -> CardIndex -> Image
commonImage cards i j = head $ do
  image1 <- cards `unsafeIndex` i
  image2 <- cards `unsafeIndex` j
  guard $ image1 == image2
  return image1
```

This is possibly a bad way to write it, since it will crash if the cards had no
common image, but if our math is correct that will never happen. Right?

So then the view:

```haskell
view :: State -> Html Action
view state = div [] cardsHtml
  where
    cardsHtml = mapWithIndex (renderCard state.selected correctImage) state.cards
    correctImage = case state.selected of
      TwoCards i j -> Just (commonImage state.cards i j)
      _            -> Nothing
```

Curiously, right when I finished the first version of this project, pux 1.0.0
dropped, with a large number of breaking changes, so I had to redo a lot of stuff.
In particular, there is a sugary hypertext DSL, but it doesn't cover every use case,
so I decided not to use it, since the code looked weird with a mix of DSL and not DSL.

Here the `div` function takes an array of attrbutes (here, empty) and an array
of child `Html` elements, which are the outcome of the call to `mapWithIndex`.
The function we pass to `mapWithIndex` is `renderCard state.selected correctImage`.
In order to figure out the correct image, we need to look at multiple cards,
so we have to do it at this stage (each call to `renderCard` will only know about
  the card it's given). If 0 or 1 cards are selected, there is no `correctImage`,
so it's an option type. We also have to pass down `state.selected` so that we can
add a CSS class to the selected cards.

This leads to a `renderCard` that looks like

```haskell
renderCard :: SelectedCards -> Maybe Image -> Card -> CardIndex -> Html Action
renderCard selectedCards correctImage card i =
  div [ className cardClass, onClick cardClick ] cardHtml
  where
    isSelected = case selectedCards of
      NoCards        -> false
      OneCard s      -> s == i
      TwoCards s1 s2 -> s1 == i || s2 == i
    cardClass = if isSelected then "card selected" else "card"
    cardClick = const (Click i)
    cardHtml = map (renderImage isSelected correctImage) card
```

Because we're passing it to `mapWithIndex`, it's a function of both `Card` and
`CardIndex` (after we curry the `SelectedCards` and the correct image). Again we
create a `div` with an array of attributes (a class, and a click handler) and
an array of `Html` children.

Hopefully the class logic is straightforward. `cardClick` should be a function
that takes a click event and returns an `Action`, but here we don't actually need
any information from the click event, so we just use `const`.

Finally, the `cardHtml` is just the result of mapping `renderImage` over the card
(which is an array of images). It needs to know `isSelected` and `correctImage`,
because we want to add the flashing "correct" class only the the correct image
*on the selected cards*.

At long last we can write `renderImage`:

```haskell
renderImage :: Boolean -> Maybe Image -> Image -> Html Action
renderImage isSelected correctImage image =
  img [ src url, alt altText, className imageClass ]
  where
    url = imageUrl image
    altText = show image
    imageClass = if isCorrectImage then "image correct" else "image"
    isCorrectImage = case correctImage of
      Just correct -> isSelected && image == correct
      _            -> false
```

Because an `<img>` tag has no children,
the `img` function only takes an array of attributes, which should be pretty straighforward.

That's the whole application, now we just need to wire it all together:

```haskell
main = do
  state <- initialState 7  -- you could change this, if you have enough images
  app <- start {           -- but it *must* be a prime number
    initialState: state
  , update: update
  , view: view
  , inputs: []
  }

  renderToDOM "#app" app.html
```

The only non-ordinary thing here is that because `initialState` is an effectful
function, we need to `<-` the state out of it.

Anyway, that's about it. (There is also some CSS voodoo to make matching images
  pulse) and to draw borders around selected cards, but you're not interested
  in CSS voodoo, are you?)

You can check it out at

<a href = "http://joelgrus.com/experiments/pux-it/">http://joelgrus.com/experiments/pux-it/</a>

although the bundle of all the code is almost 1MB. :(  Or fork it and make it your own. :)
