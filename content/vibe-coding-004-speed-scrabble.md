Title: Vibe Coding 4 -- Speed Scrabble
Date: 2025-08-04 12:00
Category: Vibe Coding

A few years ago we went on an Alaska cruise,
and we sprung for a cabin in the private/exclusive part of the ship
(which is the way to go!)
which had its own restaurant, its own lounge, and so on.
The lounge had board games, one of which was Scrabble. 
I don't particularly enjoy Scrabble, but I do enjoy 
[Speed Scrabble](https://www.thegamegal.com/2016/01/28/speed-scrabble/)
which is where there's no board and you just have to use your
tiles to make words, racing against others, drawing tiles, etc.
We played a fair amount and every once in a while Google Photos
will show me a picture of it.

![cruise]({static}images/cruise-small.jpg)

As my next exercise in Vibe Coding I thought I'd try to implement
a web version of Speed Scrabble. This is an interesting challenge
for a couple reasons:

* it's pretty much purely a front-end project, which means I really have to cede control to the machine (I can hack together a basic React app, but a complex game UI is well beyond my abilities). This is a project that I never would have attempted on my own because it likely would have involved weeks of frustration
* there are about a million choices to make in terms of UX, everything from how should the board be laid out, to how should the
controls work, to what should the flow of gameplay be

This means that my role on the project is

product manager >> dev manager >> developer

Claude Code is stupid enough (yes it is) that I do have to step in
and tell it to fix failing tests rather than deleting them and so on, but for the most part when it starts going on about React hooks
and drag-and-drop libraries I don't have much to contribute.

Several times during the project I made it stop and "code review"
what it had done, but some of those times it immediately started
"correcting" things (i.e. breaking things) and I had to start being
very explicit about "review don't change."

![speed-scrabble]({static}images/speed-scrabble.png)

This one took me (parts of) 3 days. One day to get a very basic version working. One day to get to it polished and playable. 
And one day to get it to work on a mobile browser.

The last was a partial failure, as I wanted to make it so that
 you could drag the tiles around, but the implementation didn't work. Claude Code was unable to fix it, so I had it write out a 
 summary of the problem (and the libraries we were using) and posed
 the problem to both o3 and Gemini 2.5, neither of which was able to
 solve it either. (Everyone suspected it had something to do with the browser's native up-down scrolling interfering with vertical tile-dragging, but no one was able to fix it.) Eventually I gave up
 and settled for the crappier (but still usable) mobile analog of the desktop UI.


I had in mind a number of improvements, including

* blank tiles (which presented UX challenges in placing them,
assigning them a letter value, and tracking their letter value)
* daily puzzles (i.e. tile orders) with scoreboards, etc
* better sharing of completed puzzles (it's implemented but has some UX problems)

But I'm probably going to call it a day.

On one hand it's pretty impressive that I was able to 
produce a game that works, that looks decent, and that is
actually pretty fun to play.

On the other hand, I ended up with a pile of code that
I don't really understand and that I can't really maintain myself.

Very dangerous!

Check out the code on GitHub: https://github.com/joelgrus/speed-scrabble and feel free to let me know which of the fundamental
rules of React were broken here.

Play it yourself: [speedscrabble.netlify.app](https://speedscrabble.netlify.app/)

Click on (or type) letters to add them at the cursor, click on the cursor (or space bar) to change the orientation, backspace (or long press on mobile) to move tiles back to the rack, you can figure out the rest. It's fun!