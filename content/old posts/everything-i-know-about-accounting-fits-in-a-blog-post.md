Title: Everything I Know About Accounting Fits in a Blog Post
Date: 2010-10-12 15:51
Author: joelgrus
Tags: Business
Slug: everything-i-know-about-accounting-fits-in-a-blog-post

When I'm not writing books or arguing on the Internet or playing
Spelunky, I run a small publishing company. By "small" I mean "zero
employees" small. By necessity, I have to wear a number of hats.

I'm the CEO, but I'm also the janitor. (And the janitor is *this close*
to getting fired.) I'm the webmaster, the editor, the editorial
assistant, the chief human resources officer, the slush-piler, and the
VP of marketing. And, of course, I'm the accountant.

Which is unfortunate, because I hate accounting. Mostly this is because
I don't understand accounting. I try to learn it, and it doesn't take. I
try again, and it still doesn't take. I managed to learn Calculus. I
managed to learn Complex Analysis and Abstract Algebra and Microeconomic
Theory and Probability Modeling. I can write computer programs in a
variety of languages. I once hand-sewed an Einstein doll out of felt.
And yet I can't learn accounting.

Nonetheless, I *do* accounting, using a variety of tricks that I picked
up from the kind of tutorials that people used to host on their
Geocities websites, with [MIDI versions of Pink Floyd
"Money"](http://www.floydhead.com/PF_MIDI/Money.mid) playing in the
background.

Here, then, is everything I know about accounting. This isn't even
Accounting for Dummies, because when it comes to accounting I'm not even
a dummy. It's Accounting for Not-Even Dummies:

1. Debits and Credits
---------------------

There are two kinds of things. Debits and Credits. Debits are one thing,
and Credits are the other thing. Whenever you make a Debit, you have to
also make a Credit. I think this has something to do with Buddhism and
the Wheel in the Sky.

2. The Accounting Identity
--------------------------

Did I say there were two kinds of things? There's also three other kinds
of things. Assets, Liabilities, and Equity. Assets are things that are
good, like bank accounts. Liabilities are things that are bad, like
credit card bills. Equity is what's left -- the morally ambiguous.

These are all interrelated by the Fundamental Identity of Accounting:

**Assets = Liabilities + Equity**

don't try to overthink this in terms of good and evil. It just is. I
think this also has something to do with Buddhism.

3. Double Entry
---------------

Every time you account, you have to make 2 entries in what's called a
"Ledger." One of the entries has to be a Debit and one of them has to be
a Credit. There are 4 reasons to make a Debit and 4 reasons to make a
Credit.

**4 Reasons to Make a Debit**

Asset increases in value\
 Liability decreases in value\
 Business incurs expense\
 Owner withdraws equity

**4 Reasons to Make a Credit**

Asset decreases in value\
 Liability increases in value\
 Business receives revenue\
 Owner invests equity

There's probably some logic involved here, but I don't understand
Buddhism enough to know what it is, so just memorize the list. It might
have to with the fact that all the Debits *increase* Assets and
*decrease* Liabilities and Equity, whereas Credits do the opposite. This
means that if you make a Debit and Credit that are the same size, you'll
preserve Assets = Liabilities + Equity, which is good for your karma.

4. Mixing and Matching
----------------------

To account, just choose a Debit and a Credit from each list and put
equal amounts in both.

**Example: Initial Investment of \$1000**

Debit: Checking Account (Asset+) \$1000\
 Credit: Owner's Equity (Equity+) \$1000

**Example: Pay \$50 for Facebook ads with Credit Card**

Debit: Advertising (Expense) \$50\
 Credit: Mastercard (Liability+) \$50

**Example: Pay Credit Card Bill from Checking Account**

Debit: Mastercard (Liability-) \$50\
 Credit: Checking Account (Asset-) \$50

**Example: Sold \$100 of Kindle Books**

Debit: Accounts Receivable (Asset+) \$100\
 Credit: Kindle Revenue (Revenue) \$100

**Example: Get Actual \$\$ from Amazon**

Debit: Checking Account (Asset+) \$100\
 Credit: Accounts Receivable (Asset-) \$100

I forgot to mention that "Accounts Receivable" is accounting-speak for
"Money Someone Owes Me," which is an asset. Similarly, "Accounts
Payable" means "Money I Owe Someone," which is a liability.

5. Building an Accounting System
--------------------------------

There are a number of excellent accounting systems out there, I imagine,
but they all cost money. Therefore I use Excel. It also costs money, but
not if you already have a copy.

Here are the columns in my spreadsheet:

A. Canonical: I use this to label recurring transactions. For instance,
every month I have to account for the money I pay my webhost. These
entries say "WEBHOST".

B. Date: The date of the expense. This is an important one.

C. \#: I feel more professional if every accounting has its own number.
But I don't use them for anything.

D. Ref \#: I had this great idea that I might want to reference earlier
accountings in later ones. But I barely manage to *enter* the later
ones, so this column doesn't actually get used.

E. Account: This is the account something goes in. To be clever I
hierarchy my accounts with dashes. So they're things like "Expenses -
Adminstrative" and "Assets - Checking." Then later I use Excel formulas
to extract out the first part.

F-M. Debits and Credits: If I understood accounting, I'd have one column
for Debits and one for Credits. Instead I have four for Debits (Asset+,
Liability-, Expense, Draw) and four for Credits (Asset-, Liability+,
Revenue, Investment) so that I don't even have to memorize the rules for
Debits and Credits, I can just put numbers in the appropriate columns.

N. For: What the entry is for.

O. Comment: In case I want to comment.

After that I have a bunch of Calculated Fields.

P-Q. Debit and Credit: sum up the earlier eight.

R. Year: Computed off the date

S. Month: Computed off the date

T. Fiscal Month: YYYY-MM, computed off the date

U. Account Category: The first part of the account

V. Debit - Credit: The difference

W. Credit - Debit: The difference

6. Using the Accounting System
------------------------------

To make an accounting, figure out the Debit and the Credit, and just
enter them on consecutive lines. Each line should have either one Debit
or one Credit. It should never have both, and it should never have more
than one of either. The Debit and Credit on consecutive lines have to be
the same amounts!

Then you can use a Pivot Table to do all your reporting.

For liabilities and equity and revenue, you want to look at the sum of
Credit - Debit. For assets and expenses, you want to look at the sum of
Debit - Credit. I'm not sure why, but this works.

For instance, in the above examples, to find the balance in your
checking account (which is an asset), you want Debit - Credit, which is
(\$1000 + \$100) - (\$50) = \$1050.

7. Closing the Books
--------------------

At the end of the year, you're supposed to close your books. First, move
everything from the Revenue and Expenses accounts into an account called
Income Summary. Then move everything from Income Summary into an account
called Equity - Retained Earnings.

I don't understand this part at all, and the website I got it from
didn't have any MIDI songs on it, so it might not even be trustworthy.
Someday I might figure this out, but for now I just use the Pivot Table
to see my Revenue and Expenses by year.

8. Preparing for an Audit
-------------------------

Hide under the bed and cry like a baby.

------------------------------------------------------------------------

And there you have it. Now you know as much about accounting as I do!

Next time: "Everything I Know About Do-It-Yourself Ingrown Toenail
Surgery Fits in a Blog Post."
