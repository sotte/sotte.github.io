---
title: dplyr enlightenment with pandas
created_at: 2017-07-14
updated_at: 2024-01-29
author: 2017-07-14
_template: article.html
---

<p class="notice">
  Update 2024-01-29:
  more current libraries than the one mentioned here in the article are
  <a href="https://github.com/machow/siuba/">siuba</a>
  and
  <a href="https://github.com/pwwang/datar">datar</a>.
  Also check out <a href="https://github.com/pola-rs/polars">polars</a> for a fast dataframe library that offers a nice but different interface.
<p>

I tried to reach [dplyr](http://dplyr.tidyverse.org/) enlightenment in the `pandas` ecosystem,
but what I found was different from what I expected. Be warned: opinions ahead!

According to the [dplyr homepage](https://github.com/tidyverse/dplyr)
> "dplyr is a grammar of data manipulation, providing a consistent set of verbs that help > you solve the most common data manipulation challenges.
>
> - mutate() adds new variables that are functions of existing variables
> - select() picks variables based on their names.
> - filter() picks cases based on their values.
> - summarise() reduces multiple values down to a single summary.
> - arrange() changes the ordering of the rows."

Some people, myself included, think that you can write some concise and easy-to-read code with just these few verbs.

Here is an example of dplyr in action taken from the [python-ply](https://github.com/coursera/pandas-ply) page:

```R
flights %>%
  group_by(year, month, day) %>%
  summarise(
    arr = mean(arr_delay, na.rm = TRUE),
    dep = mean(dep_delay, na.rm = TRUE)
  ) %>%
  filter(arr > 30 & dep > 30)
```

Compare this to, what they call, "the most common way to express this in pandas":

```python
grouped_flights = flights.groupby(['year', 'month', 'day'])
output = pd.DataFrame()
output['arr'] = grouped_flights.arr_delay.mean()
output['dep'] = grouped_flights.dep_delay.mean()
filtered_output = output[(output.arr > 30) & (output.dep > 30)]
```

The dplyr version is more readable.

Let's check out if there is a dplyr-like way to write the obove with python and `pandas`.
Luckily there are some libraries which implement some of dplyr's features in python.

- [`python-ply`](https://github.com/coursera/pandas-ply) has 124 stars and 12 forks on github. The last commit was in August 2015. `python-ply` monkey-patches `pandas` and adds `.ply_select` and `.ply_where` and adds a special `X` variable for lazy evaluation.
- [`dplython`](https://github.com/dodger487/dplython) has 576 stars and 38 forks on github. The last commit was in December 2016. `dplython` uses more of verb-like approach with functions and also adds a special `X` for delayed execution.

## Case Study with the Diamond dataset

I'm going to show some simple data mungling with the diamonds dataset.
[dplython](https://github.com/dodger487/dplython) has some data mungling examples that demonstrate of how to use dplython with this dataset.
I'm going to do the same with `pandas-ply` and vanilla `pandas`.

```python
# The imports...
import pandas as pd

# pandas-ply
from pandas_ply import install_ply
# normally just X
from pandas_ply import X as X_ply
install_ply(pd)

# dplython
from dplython import (
    select,
    sift,
    sample_n,
    head,
    arrange,
    mutate,
    group_by,
    summarize,
)
# normally just X
from dplython import X as X_dpl
```

`dplython` already ships the diamonds dataset.
Note that dplython uses `DplyFrame` as extension of the `DataFrame` and `dyf` is the diamond data as `DplyFrame`.

```python
from dplython import diamonds

# Note that dplython needs the DplyFrame
# and dyf is the diamond data as DplyFrame
dyf = diamonds 
df = pd.DataFrame(diamonds)
print(type(df))
print(type(dyf))
```

Just to get an idea of how the data look like:

```python
df.sample(3)
```

```python
n = 3  # number of samples we'll draw
```

### Simple select

```python
# dplython
(
    dyf
    >> select(X_dpl.carat, X_dpl.cut, X_dpl.price)
    >> head(n)
)
```

I like dplython's `>>` operator for piping the data (but I'm spoiled by elixir and I'm aware that operator overloading can be used for evil (hello c++)).
The use of `X` gives us access to the columns of the data.
It's nice, but again not a huge difference.

```python
# pandas-ply
(
    df
    .ply_select('carat', 'cut', 'price')
    .head(n)
);
```

The `ply_select` methods is the equivalent to `dplython`'s `select` function.

```python
# pandas
(
    df
    [['carat', 'cut', 'price']]
    .head(n)
);
```

With pandas we use the good old bracket notation.
Also quite readable.

### Filter and select

```python
# dplython
(
    dyf
    >> sift(X_dpl.carat > 4)
    >> select(X_dpl.carat, X_dpl.cut, X_dpl.depth, X_dpl.price)
)
```

`dplython`'s sift is like a filter and quite redable.

```python
# pandas-ply
(
    df
    .ply_where(X_ply.carat > 4)
    .ply_select('carat', 'cut', 'depth', 'price')
);
```

`.ply_where` in combination with the `X` is just as nice as `dplyton`.

```python
# pandas
(
    df
    [df.carat > 4]
    [['carat', 'cut', 'depth', 'price']]
);
```

I guess this is the most common way to write the same in vanilla `pandas`.

```python
# pandas
(
    df
    .query('carat > 4')
    [['carat', 'cut', 'depth', 'price']]
);
```

But it's also possible to use the `query` method of `pandas`.

### Sample and sort

```python
# dplython
(
    dyf
    >> sample_n(n)
    >> arrange(X_dpl.carat)
    >> select(X_dpl.carat, X_dpl.cut, X_dpl.depth, X_dpl.price)
)
```

`arrange` might seem strange in the beginning.
Just think of it as sort and you're fine.

```python
# python-ply
(
    df
    .sample(n)
    .sort_values('carat')
    .ply_select('carat', 'cut', 'depth', 'price')
);
```

No surprises with `pandas-ply`.

```python
# pandas
(
    df
    .sample(n)
    .sort_values('carat')
    [['carat', 'cut', 'depth', 'price']]
);
```

And no surprises with vanilla `pandas`, but I still think it's quite readable.

### Assign, group by and summarize

```python
# dplython
(
    dyf
    >> mutate(carat_bin=X_dpl.carat.round())
    >> group_by(X_dpl.cut, X_dpl.carat_bin)
    >> summarize(avg_price=X_dpl.price.mean())
    >> head(10)
)
```

This is an example where dplython shines.
`mutate` makes clear that something is changed (though technically we return a copy, so we don't change anything)
and `summarize` is similar to `pandas` `agg` but with a better interface/more functionality and a better name.

```python
# python-ply and pandas
(
    df
    .assign(carat_bin=df.carat.round())
    .groupby(['cut', 'carat_bin'])
    .agg({'price': 'mean'})
    .rename(columns={"price": "avg_price"})
    .reset_index()
    .head(10)
)
```

We were not really able to use any padans-ply features here. `ply_select(carat=_X.carat.round())` only leaves the selected 'carat' column.

`pandas`'s `assign` method is quite clear.
`agg` does not feel as clean as the `summarize` function from `dplython`.
With `summarize` we can directly assign the name for the new column which we can't do with `agg` 
(you could use `.agg({'price': {'avg_price': 'mean'}})` but that is going to be deprecated soon).
Therefore we manually rename the column.

Also note, that `agg()` returns a `DataFrame` with a `MultiIndex` whereas `summarize` of `dplython` returns a flat `DataFrame`.
We flatten the `MultiIndex` by resetting the index.

## Conclusion

So which one is better? `dplython`, `pandas-ply`, or even vanilla `pandas`?

I think the method-chaining version of `pandas` is quite readable,
but `pandas` is still `pandas`.
Even though I know `pandas` quite well,
I found myself looking up the docs more often than for `python-ply` and `dplython` (which I haven't used before):
- does the `rename` methods require a keyword argument?
- wasn't there a `select` method in pandas that I can use?
- can `agg` rename at the same time?

`pandas-ply` does not really offer a big advantage over good old `pandas` and is also not actively maintained.

`dplython` feels good!
Piping, concise verbs, more popular.
Will I use it in the future?
I think I'll give it a try in a bigger project and see how it goes.

Nevertheless, check out the [modern pandas post](https://tomaugspurger.github.io/method-chaining.html) on method chaining if you don't use this feature yet!

## References

- [dplython talk at PyGotham 2016](https://www.youtube.com/watch?v=4YAcwCe1mAE)
- [dplython](https://github.com/dodger487/dplython)
- [python-ply](https://github.com/coursera/pandas-ply)
- [pandas](http://pandas.pydata.org/)
