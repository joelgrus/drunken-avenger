Title: T-Shirts, Feminism, Parenting, and Data Science, Part 2: Eigenshirts
Date: 2013-06-24 20:37
Author: joelgrus
Tags: Uncategorized
Slug: t-shirts-feminism-parenting-and-data-science-part-2-eigenshirts

(You might want to read [Part
1](https://joelgrus.com/2013/06/19/t-shirts-feminism-parenting-and-data-science-part-1-colors/)
first.)

When last we left off, we'd built a model using *shirt colors* to
predict boy-ness / girl-ness.

Our second attempt will involve the shirt images themselves (sort of).
For our purposes, computer images are made up of
[pixels](https://en.wikipedia.org/wiki/Pixel), each of whose color is
determined by specifying [red, green, and blue
values](https://en.wikipedia.org/wiki/Rgb#Numeric_representations)
between 0 and 255. So if you have an image with *N* pixels, you can
think of it as a point in 3*N*-dimensional space, all of whose
coordinates lie between 0 and 255.

And as before, we can build a linear model to classify points in space
using logistic regression. The trick here is that the images have
different sizes (and hence different numbers of pixels). So as a first
step, we'll rescale every image to 138 pixels x 138 pixels = 19,044
pixels. (A lot of our images are this size, and the rest are mostly
larger, which is why I chose it.) This will give us a representation of
each t-shirt image as a point in 57,132-dimensional space. (Visualizing
57,132-dimensional space is tricky, so don't feel bad if you can't do
it.)

Our dataset only contains about 1,000 shirts, which means that a
57,000-dimensional classifier would learn to *identify* every shirt in
the test dataset rather than figure out what distinguishes the boys
shirts from the girls shirts. This means we need to do some sort of
[dimensionality
reduction](https://en.wikipedia.org/wiki/Dimensionality_reduction) to
get our t-shirt images into a much lower-dimensional space.

Here we'll use [Principal Component
Analysis](https://en.wikipedia.org/wiki/Principal_component_analysis),
which finds the direction (in 57,132-dimensional space) that accounts
for the largest amount of variance in the dataset. It then subtracts out
this direction, finds the most-variant-direction of the new dataset, and
so on, until it has enough components.

(As always, code is on [GitHub](https://github.com/joelgrus/shirts).)

I ended up using 10 components, which gives a representation of each
t-shirt as just 10 numbers, representing the projection of the
(57,132-dimensional representation of the) shirt onto the first 10
principal components, each of which is itself a vector in
57,132-dimensional space. For instance, the first principal component is
the 57,132-element vector

[0.0002334, 0.00029256, 0.00042805, ... , 0.00051605]

By thinking of this as a vector of 19,044 rgb triplets, and by rescaling
it so that its smallest component is 0 and its largest component 255, we
can convert it into an image of an *eigenshirt* representing the
"essence" of this component. Shirts with a large value for the first
component will tend to be "similar" to this eigenshirt. Shirts with a
large negative value for the first component will tend to be "similar"
to its color-inverted "anti-eigenshirt". [We could have just as easily
picked the "anti-eigenshirt" as the eigenshirt and flipped the signs of
the components.]

The below table shows, for each of the 10 principal components, the
eigenshirt, the shirt with the largest component value, the shirt with
the closest-to-zero value, the shirt with the largest *negative*
component value, and the "anti-eigenshirt".

<table>
<tr>
<th>Eigenshirt</th><th>Most Eigenshirty</th><th>Not Eigenshirty</th><th>Most Anti-Eigenshirty</th><th>Anti-Eigenshirt</th>
</tr>
<tr><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/0_eigenshirt.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/0_most.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/0_none.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/0_least.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/0_inverted_eigenshirt.png">
</td></tr>https://joelgrus.comhttps://joelgrus.comhttps://joelgrus.comhttps://joelgrus.comhttps://joelgrus.com
<tr><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/1_eigenshirt.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/1_most.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/1_none.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/1_least.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/1_inverted_eigenshirt.png">
</td></tr>https://joelgrus.comhttps://joelgrus.comhttps://joelgrus.comhttps://joelgrus.comhttps://joelgrus.com
<tr><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/2_eigenshirt.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/2_most.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/2_none.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/2_least.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/2_inverted_eigenshirt.png">
</td></tr>https://joelgrus.comhttps://joelgrus.comhttps://joelgrus.comhttps://joelgrus.comhttps://joelgrus.com
<tr><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/3_eigenshirt.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/3_most.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/3_none.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/3_least.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/3_inverted_eigenshirt.png">
</td></tr>https://joelgrus.comhttps://joelgrus.comhttps://joelgrus.comhttps://joelgrus.comhttps://joelgrus.com
<tr><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/4_eigenshirt.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/4_most.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/4_none.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/4_least.png"></td><td><img width="140" src="https://joelgrus.com/wp-content/uploads/2013/06/4_inverted_eigenshirt.png">
</td></tr>https://joelgrus.comhttps://joelgrus.comhttps://joelgrus.comhttps://joelgrus.comhttps://joelgrus.com
<tr><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/5_eigenshirt.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/5_most.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/5_none.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/5_least.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/5_inverted_eigenshirt.png">
</td></tr>
<tr><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/6_eigenshirt.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/6_most.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/6_none.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/6_least.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/6_inverted_eigenshirt.png">
</td></tr>
<tr><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/7_eigenshirt.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/7_most.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/7_none.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/7_least.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/7_inverted_eigenshirt.png">
</td></tr>
<tr><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/8_eigenshirt.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/8_most.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/8_none.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/8_least.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/8_inverted_eigenshirt.png">
</td></tr>
<tr><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/9_eigenshirt.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/9_most.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/9_none.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/9_least.png"></td><td><img width="140" src="http://joelgrus.com/wp-content/uploads/2013/06/9_inverted_eigenshirt.png">
</td></tr>
</table>

If I were to try to give qualitative descriptions of these ten
components, I guess they would be something like:

<ul>
<li>Component 0: White -\> Black</li>
<li>Component 1: Orange -\> Blue</li>
<li>Component 2: Dark sleeved / white sleeveless -\> White sleeved / dark
sleeveless</li>
<li>Component 3: Wide dark / narrow white -\> Narrow dark / wide white</li>
<li>Component 4: ?</li>
<li>Component 5: Green -\> Purple</li>
<li>Component 6: White trim / dark shirt -\> Dark trim / white shirt</li>
<li>Component 7: https://joelgrus.comwhite sleeveless -\> White long sleeve
/ dark sleeveless</li>
<li>Component 8: White shirt / dark print -\> Dark shirt / white print</li>
<li>Component 9: ?</li>
</ul>

The Principal Component representation of each shirt is a 10-dimensional
vector representing (roughly) where it fits on each of these spectra.
For instance, the monkey shirt

![monkey\_shirt](http://joelgrus.com/wp-content/uploads/2013/06/monkey_shirt.jpg)

is represented by the vectorhttps://joelgrus.com

[ -9313, 10067, -149, -4013, -2147, 1574, -296, -954, 1729, -196]

the biggest components of which are "orange" (eigenshirt \#1), "dark"
(anti-eigenshirt 0), and "narrow" (anti-eigenshirt 3).

If we try to reconstruct the image using just these ten components, we
get

![monkey\_shirt\_reconstructed](http://joelgrus.com/wp-content/uploads/2013/06/monkey_shirt_reconstructed.png)

which seems to have captured *orange*, *short sleeve*, and *dark
graphic*. You certainly can't tell it's a monkey, though.

Predicting
----------

If we try to predict "boy shirt or girl shirt" using just these 10
components, we get a model that's 93% accurate on the test set. The
coefficients (multiplied by 10,000, since they're small) look like:

Component 0: -2.71 (eigenshirt is girlish)\
 Component 1: -2.56 (girlish)\
 Component 2: 3.55 (boyish)\
 Component 3: 0.53 (weakly boyish)\
 Component 4: -0.56 (https://joelgrus.com
 Component 5: 5.43 (boyish)\
 Component 6: -15.9 (very girlish)\
 Component 7: -4.68 (girlish)\
 Component 8: 2.73 (boyish)\
 Component 9: -2.14 (girlish)

As before, we can look at how the shirts are distributed as a function
of the score they get from the model:

![shirts\_by\_scorhttps://joelgrus.comcom/wp-content/uploads/2013/06/shirts_by_score1.png)

The miscategorized shirts generally have low (close to 0) scores, except
for one particularly "girly" boys shirt that we'll see below.
https://joelgrus.com
Superlatives
------------

**Girliest Girl*https://joelgrus.comsed on shape and colors)

![girliest\_girl](http://joelgrus.com/wp-content/uploads/2013/06/girliest_girl.jpg)

**Girliest Boy** https://joelgrus.comgain)

![girliest\_boy](http://joelgrus.com/wp-content/uploads/2013/06/girliest_boy.jpg)

**Boyiest Boy** (da Bears)

![boyiest\_boy](http://joelgrus.com/wp-content/uploads/2013/06/boyiest_boy.jpg)

**Boyiest Girl** (same one as last time!)

![boyiest\_girl](http://joelgrus.com/wp-content/uploads/2013/06/boyiest_girl.jpg)

This is all very interesting and hints at [Platonic
ideal](https://en.wikipedia.org/wiki/Platonic_idealism) shirts (the
philosophical details of which are out of scope for this blog). And
clearly it does a much better job of predicting "boy shirt or girl
shirt" than our previous color-based attempt. But whereas everyone knows
about colors (except for the color-blind, of course), most people are
unfamiliar with "eigenshirts" and will accuse you of having made them up
just in order to have something to blog about. In particular, the girl
who works at Gap Kids was entirely unimpressed with this model, and said
that I needed to either buy something or leave the store.

Were I really committed to this model, I'd probably do more work to get
the images comparable to each other so that not only were they the same
size but the shirts were oriented as closely as possible and all had the
same background color. Alas, I'm sort of principal-componented-out, and
am eager to get back to writing my blog post about "the only correct way
to interview engineers", the punch-line of which is that you should only
ask questions that involve golf balls, piano tuners, counterfeit coins,
airplanes, treadmills, or piano tuners.

And so we leave things until part 3, "Shirt Language Processing", which
will be forthcoming at some point after I muster up the motivation to
either transcribe the shirt images or find an intern to do it for me.
