Title: Creating a Function Index Using Cycle.js
Date: 2016-01-21 09:00
Category: Javascript, Hacking

The readers of my book have been clamoring for an <a href = "https://github.com/joelgrus/data-science-from-scratch/issues/21">index of functions</a>,
so that -- for example -- when someone sees me use `vector_mean` on page 200 they can
easily figure out where to find its definition.

It was easy enough (if tedious) to go through the book and create a spreadsheet,
but it also seemed an opportunity to build something in Javascript, which I always
unreasonably enjoy.

My idea was pretty simple: a text input that you type in, and a table of
{ function_name, chapter, page } that's filtered (in real-time) by whatever you
type. So if you type "add" you get all the functions that contain "add" somewhere
in their name (e.g. `vector_add`).

![index-of-functions]({static}images/index-of-functions.png)

Simple enough, but also a good opportunity to
use/learn some newfangled client-side-virtual-dom-javascript-magic framework.

Given my love of all things Purescript, I
<a href = "https://github.com/joelgrus/dsfs-function-index">built the first version using purescript-halogen</a>.
Unfortunately (or fortunately), I don't understand <a href="http://www.haskellforall.com/2012/06/you-could-have-invented-free-monads.html">free monads</a>
well enough to explain it to you. If you understand Purescript (or Haskell) it is
mostly straightforward, save that the halogen library gave me no easy way
(or at least no obvious way) to get at the value of a text input on every
`keyup` event, which required a lot of ugly hacking around (and made up the bulk
of the time I spent on the project).

Recently I've been poking at <a href = "http://cycle.js.org/">cycle.js</a>
(whose creator recently wrote an <a href = "http://staltz.com/why-react-redux-is-an-inferior-paradigm.html">anti-React rant</a>
that kind of resonated with me), so I figured I'd try recreating the project
using cycle. (It was surprisingly easy and fun, once I got past the self-loathing
of using a non-typed language.)

The central idea of cycle is using <a href = "http://cycle.js.org/observables.html">observables</a>,
which are basically lazy streams of values. (If you want types, I believe this is basically
the paradigm of <a href ="http://elm-lang.org/">Elm</a>, and also there is a
<a href = "https://github.com/bodil/purescript-signal">purescript-signal</a> library
that does this.)

The documentation calls the architecture
"Model-View-Intent", but I prefer to think of it as "Intent-Model-View", which is the order
in which things happen:

* Intent: given some external source (the DOM, AJAX calls), create a lazy stream
  of _events_.
* Model: given a lazy stream of events, turn it into a lazy stream of _states_.
* View: given a lazy stream of states, turn it into a lazy stream of _outputs_
  (in our case, virtual-dom trees)

Each of these can be a pure function (yay!), and the cycle.js machinery hooks
these together to create a loop.

In this case, we'll have a text input, and the _intent_ should output its value
every time there is a keyup event:

```javascript
function intent(DOM) {
  return DOM.select('input').events('keyup')
    .map(ev => ev.target.value)
    .startWith('');
}
```

Hopefully this is pretty straightforward. (The `startWith('')` just says that our stream should
start with an empty string event before any events happen.)

Now the model needs to use that value (our "query") to produce a state. The state should be
whatever data we need to produce the output. Here that will be the query itself, as well as the
list of functions that satisfy the query:

```javascript
function model(value$) {
  return value$.map(query => ({
    query,
    entries : indexEntries.filter(entry => (entry.name.indexOf(query) !== -1))
  }));
}
```

(The `$`-suffix is a cycle convention (maybe broader) to indicate that a variable
 is an observable.) This is again pretty simple: given an element of the `value$`
stream (which is the value of the text input after a keyup),
output a state consisting of both the query and the index entries that match it.

Finally, we need the _view_ to turn that state into a virtual-dom representation:

```javascript
function view(state$) {
  return state$.map(state =>
    div([
      input({type: 'text',
             autofocus: true,
             placeholder: 'Search Query',
             value: state.query}),
      // v-dom table containing the entries
      showEntries(state.entries)
    ]));
}
```

Given a `state`, we need a text input with its value set to `state.query`,
and a table displaying the entries. (Yes, this is one of those setups where
you use Javascript functions to write HTML, deal with it.)
`showEntries` is not very interesting, but here it is for completeness:

```js
function showEntries(indexEntries) {
  return table([
    thead([
      tr([th('chapter'), th('page'), th('function') ])
    ]),
    tbody(indexEntries.map(entry =>
      tr([td('' + entry.chapter), td('' + entry.page), td(entry.name)])
    ))
  ]);
}
```

(The table header contains headings, the table body contains one row for each
 index entry. Apparently `td` requires a string as its input.)

That's essentially it, all that's left is to hook it all together:

```js
function main({DOM}) {
  return {DOM: view(model(intent(DOM)))};
}

Cycle.run(main, {
  DOM: makeDOMDriver('#app')
});
```

Here `main` just takes the `DOM` source (which is the output of `makeDOMDriver`)
and returns the virtual-dom sink that we've defined. (Or possibly I got "source"
and "sink" mixed up here, I don't really understand them.)

Anyway, that's it, that's the whole app (modulo a html file that has an `div#app`
and some hacky CSS and the file that contains the actual "index entries" data).

Because there's lots of ES2015 voodoo, we need to use `browserify` with all sorts
of plugins, and the output is a disgustingly large 600KB Javascript file. That's
the price of progress, I guess!

(<a href = "https://github.com/joelgrus/dsfs-function-index-cycle-js">Code on GitHub</a>.)
