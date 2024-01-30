---
title: PyData Talk 2017 - On Bandits and Swipes - Gamification of Search
author: Stefan Otte
created_at: 2017-07-16
---

This is a slightly edited version of the talk I gave at the PyData Berlin 2017.

Here is the [github repo](https://github.com/sotte/pydata_berlin_2017_active_learning)
containing the source and additional materials,
here is the [reveal.js presentation](https://sotte.github.io/pydata_berlin_2017_active_learning/),
here is the [bandit demo](https://github.com/sotte/pydata_berlin_2017_active_learning/blob/gh-pages/bandit_demo.ipynb),
and here is the [youtube video](https://www.youtube.com/watch?v=SpRg8KSLZ2w).

Enjoy!

---

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-01.png">
</aside>
"On Bandit and Swipes - Gamification of Search"
This is the title that I submitted.
But while preparing the talk I came up with a much better title.

<div style="clear: both;"></div>

<aside style="width: 50%;">
  <img src="/static/images/pydata2017/slide-02.png">
</aside>
"Active Learning or: How I Learned to Stop Worrying and Love Small Data".
This is the spiritual title of the talk.

<div style="clear: both;"></div>

<aside style="width: 50%;">
  <img src="/static/images/pydata2017/slide-03.png">
</aside>
Hello, I'm Stefan.
I'm a machine learner, data scientist, and coder.

<div style="clear: both;"></div>

<aside style="width: 50%;">
  <img src="/static/images/pydata2017/slide-04.png">
</aside>
In my previous life I was a roboticist
and actually used active learning to create "intelligent" behaviour.

<div style="clear: both;"></div>

<aside style="width: 50%;">
  <img src="/static/images/pydata2017/slide-05.png">
</aside>
Now I work at *um as a data scientist.

<div style="clear: both;"></div>

<aside style="width: 50%;">
  <img src="/static/images/pydata2017/slide-06.png">
</aside>
So back to the topic: gamification of search.

When you search for a product you fill out little forms.

<div style="clear: both;"></div>

<aside style="width: 50%;">
  <img src="/static/images/pydata2017/slide-07.png">
</aside>
This reduces the space of all things to a subset...

<div style="clear: both;"></div>

<aside style="width: 50%;">
  <img src="/static/images/pydata2017/slide-08.png">
</aside>
which, hopefully, is of interest to you.

<div style="clear: both;"></div>

<aside style="width: 50%;">
  <img src="/static/images/pydata2017/slide-09.png">
</aside>
This works well in certain scenarios,
but maybe is not ideal in every situation.
Maybe search should not be just black and white but more nuanced.

<div style="clear: both;"></div>

<aside style="width: 50%;">
  <img src="/static/images/pydata2017/slide-10.png">
</aside>
Maybe there is also a better, more fun interface,
to inform the system about your preferences.
Like swiping.
It seems to be pretty addictive in certain scenarios ;)

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-11.png">
</aside>
So we developed this system which allows you to search for your dream car
by swiping the cars you like and don't like.
The system effectively learns your preferences.


<div style="clear: both;"></div>


<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-12.png">
</aside>
I could just tell you how we implemented it and all the gotchas,
but I think there is more to it.
There is a theory underlying this project.
And in fact "nothing is quite so practical as a good theory".


<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-13.png">
</aside>
So I'm going to introduce you to the theory of Active Learning.
What is active learning?


<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-14.png">
</aside>
I'm quoting:
"The key idea behind active learning is that a machine learning algorithm can achieve greater accuracy with fewer training labels if it is allowed to choose the data from which it learns.

<div style="clear: both;"></div>

<aside style="width: 50%;">
  <img src="/static/images/pydata2017/slide-15.png">
</aside>
An active learner may pose queries, usually in the form of unlabeled data instances to be labeled by an oracle (e.g., a human annotator).

<div style="clear: both;"></div>

<aside style="width: 50%;">
  <img src="/static/images/pydata2017/slide-16.png">
</aside>
Active learning is well-motivated in many modern machine learning problems, where unlabeled data may be abundant or easily obtained, but *labels are difficult, time-consuming, or expensive to obtain*."

This is taken from the Active Learning Literature Survey by Burr Settles.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-17.png">
</aside>
This is a great summary.
The survey, or the book version of it,
gives a great overview of active learning.


<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-18.png">
</aside>
But also Burr Settles seems to be a funny guy
as the picture suggests.


<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-19.png">
</aside>
So to reiterate the key points of active learning:

1. AL can achieve greater accuracy with fewer training labels.
   You don't need big data/many data points but small data/few data points.
   The data points you have, though,
   have a high information to noise ratio.
   I think of this as "good data".

2. Because AL methods actively query for labels we're dealing with a different
   kind of problem now, a sequential decision making problem.


<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-20.png">
</aside>
To bring this last point home: in the usual supervised learning setting
you have your data X and your labels y (dogs, cats, ...).
The goal is to learn a mapping from X to y.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-21.png">
</aside>
In an AL setting you have your data X,
but you don't have labels (or only very few).
You still have to learn the mapping,
but you also have to actively select what data point to query.
You have to decide: what is an interesting point to query?

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-22.png">
</aside>
But what is interesting?

And that is the essential question.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-23.png">
</aside>
So let's look at an example.
Given some data points...

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-24.png">
</aside>
...and two labels for the data (here the blue and the red class).

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-25.png">
</aside>
With the initial labels we can compute a decision boundary.

So what is interesting now?

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-26.png">
</aside>
Maybe all datapoints that are close to the decision boundary?
Darker is more interesting.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-27.png">
</aside>
Or maybe we use a support vector machine (SVM)
and all the points that are potential support vectors are interesting?


<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-28.png">
</aside>
Or maybe we have an ensemble (here of size 2)
and the disagreement of the ensemble determines whats interesting?
Here the point at the bottom in the middle.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-29.png">
</aside>
Or maybe it's something completly different.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-30.png">
</aside>
Let's assume we queried this point and it was labeled as red.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-31.png">
</aside>
This would change the existing model a lot.
So maybe we're interested in the biggest expected model change.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-32.png">
</aside>
Or maybe we have something like the uncertainty around the decision
boundary, think of a Gaussian Process.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-33.png">
</aside>
There are many different ways to measure interestingness.
It depends on your problem at hand,
the methods you you,
runtime contraints (don't forget that you have to learn online now),
and other things.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-34.png">
</aside>
Let's take a little detour.
You can use active learning not just for classification.
Here is an old project of mine.
You see a robot which is guided by active learning methods to explore the
world.
It has a model of the world and uses the uncertainty of the objects and
properties to determine which object is interesting.
Then it actively explores the properties of the object,
i.e., it creates its own labels!
A human is not necessary.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-35.png">
</aside>
Enough theory,
back to gamification of search.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-36.png">
</aside>
We said we want a more fun way to interact with the app: swipes.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-37.png">
</aside>
We also said that we want a more nuanced way to integrate a swipe,
to integrate new information.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-38.png">
</aside>
One that is not just black and white...

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-39.png">
</aside>
...but something in between...

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-40.png">
</aside>
...and also allows us to update our belief when new evidence comes to light.
Here the two cars in the red rectangle are interesting again.

This looks like a sequential decision making problem.
Which car should I show the user to gain the most information?
Maybe AL can help us?


<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-41.png">
</aside>
Indeed, there is something closely related to active learning which can
help us.
It's called the mutli-armed bandit setting.


<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-42.png">
</aside>
The problem statement looks something like this:

1. find a multi armed bandit
2. play arms using bandit theory
3. Profit $$$


<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-43.png">
</aside>
More formally:

- given a bandit with n arms,
- and each arm returns a reward y that is sampled from a distribution with
unknown parameters (e.g. a Bernoulli distribution with p=.3).
- Now the goal is to find a policy
(a set of rules that tell you which arm to play)
that maximizes the total reward.


<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-44.png">
</aside>
There exists something called UCB, Upper Confident Bound, which yields very
good results in this setting.
The UCB strategy determines which arm to play next by using two terms,

1. the past performance of an arm (in 80% I got a coin when I played the arm),
2. and something which I call exploration bonus (I only played this arm once, but the other one 10 times; maybe I should try the first arm again).

The second term is often described as *optimism in the face of uncertainty*.

Just for completeness I should mention that UCB is
actually a family of strategies.
UCB strategies are *greedy*,
they are *not optimal* but *bounded suboptimal*,
and they deal with the *exploration vs exploitation* trade-off automatically.

So let's look at a concrete UCB strategy.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-45.png">
</aside>
The UCB1 strategy plays each arm once, just to get some initial data.
Then the arm which maximizes this formula is played.
Here you see the two terms: the past performance (the mean reward of arm i) + the exploration bonus.

Ignore the sqrt and the log.
You basically have a ratio of total rounds played to number of rounds arm
i was played.

So if you played many rounds in total,
but played a particular bandit only a few times,
you have a big number divided by a small number which is a big number.
Therefore you have a big exploration bonus.
Maybe you would play that arm even if the past performance was not that
great.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-46.png">
</aside>
Let's look at an example to make it clearer: <a href="https://github.com/sotte/pydata_berlin_2017_active_learning/blob/gh-pages/bandit_demo.ipynb" target="_blank">demo on github</a>

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-47.png">
</aside>
Ok, now with UCB we have a stategy which selects the most promising arm from
a set of arms.
But we can't directly apply that to our car scenario.
If we have thousands of cars, we would have to play each car once in the beginning.
Nobody would do that.

Instead, we'll have bandits for each feature we're interested in.

- We have a multi-armed bandit for the car brand. The arms then correspond to
  e.g. Porsche, VW, Ford, etc.
- We have a multi armed bandit for the car body. The arms then correspond to
  e.g. SUV, coupe, etc.
- We have a multi-armed bandit for the car segment. The arms then correspond to
  e.g. economy car, sports car, etc.

Now when we swipe a car,
we pull three arms of three different multi-armed bandits and update our belief.

Remember, each bandit spits out a ranking for all its arms,
an estimate of how profitable each arm is.
That still does not directly determine which car to show next.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-48.png">
</aside>
We use Elasticsearch to combine the output of the bandits to create
a weighted search query.
Then Elasticsearch returns a set of cars the user is interested in.

  Elasticsearch was made for these kinds of queries and is quite performant.
  So we can scale our approach quite easily to many clients.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-49.png">
</aside>
One last thing and then we're done.
Initially we have to show the bandits some cars.
However, if we randomly sampled from the population of all cars we most
likely would only sample the popular cars.
There is a huge popularity bias.
However, we want to show the user a representative of each class.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-50.png">
</aside>
After some experimentation we ended up doing sparse PCA + clustering and
extracted representatives of each cluster.

We used Sparse PCA to find a set of *sparse* components that can optimally reconstruct the data.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-51.png">
</aside>
Even though this talk was fairly abstract, I should mention python's roll in
this project.
It's python all the way down.
We used the usual suspects.
sklearn for the machine learning part.
Flask was used to create a REST API that is queried from the mobile client.
And Elasticsearch is used to create the final ranking.

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-52.png">
</aside>
Conclusion - what's the take away?

I think it's the spiritual title:
"Active Learning or: How I Learned to Stop Worrying and Love Small Data".

Active Learning (or similar techniques) can deal with small data.
In some scenarios it's a great fit.
Maybe it works for you.
Give it a try!

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-53.png">
</aside>
There are some related topics which I should mention:

sequential decision making, global optimization, experimental design and
(bayesian) reinforcement learning are quite similar to what we talked about
here.

Also, optimal solutions exist, it's called planning in belief space, but
for all practical purposes they are too expensive to compute.

Finally, I just found a hyperparameter optimization approach which uses
bandits.
It looks quite cool!
[Link](https://people.eecs.berkeley.edu/~kjamieson/hyperband.html).

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-54.png">
</aside>
That's it. Thanks!

<div style="clear: both;"></div>

<aside style="width: 50%;">
<img src="/static/images/pydata2017/slide-55.png">
</aside>

<div style="clear: both;"></div>
References:

- [Active Learning Literature Survey](http://burrsettles.com/pub/settles.activelearning.pdf)
- [Finite-time Analysis of the Multiarmed Bandit Problem - Auer et al](http://homes.dsi.unimi.it/~cesabian/Pubblicazioni/ml-02.pdf)
- [Bandits, Global Optimization, Active Learning, and Bayesian RL -- understanding the common ground - Toussaint](https://ipvs.informatik.uni-stuttgart.de/mlr/marc/teaching/14-BanditsOptimizationActiveLearningBayesianRL.pdf)
  [video](https://www.youtube.com/watch?v=5rev-zVx1Ps)
