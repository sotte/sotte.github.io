---
title: My Small Polars Tutorial
created_at: 2022-09-09
author: Stefan Otte
---


[This](https://github.com/sotte/polars-tutorial) is a small [polars](https://www.pola.rs/) tutorial.
It covers basic polars concepts as well as some random (hopefully) useful things.

It is based on the great
[polars cheat sheet](https://franzdiebold.github.io/polars-cheat-sheet/Polars_cheat_sheet.pdf)
but is heavily extended and restructured.
You can find a notebook version [here](https://github.com/sotte/polars-tutorial).

Here are some important facts that you should know when you work with polars.

**polars DataFrames don't have an index**. Aka no `.reset_index()` every third line and less complexity due to no multi-index,
but some operartions are a bit more cumbersome in return.

There are two main concepts in polars: **expressions** and **context**.

- **expression**: what to do with the data without actually knowing the data, e.g. `pl.col("foo").sort().head(2)`
- **context**: the context in which an expression is evaluated, e.g. in a `group_by`

Because of the expression/context setup **method chaining** makes even more sense than with pandas.

These seven verbs cover most things you want to do with polars:

```python
select        # select columns (and add new ones)
with_columns  # like select but keep existing columns
sort          # sort rows
filter        # filter rows
group_by      # group dataframe
agg           # aggregate groups
join          # join/merge another dataframe
```

As always, [read the friendly manual](https://docs.pola.rs/) to really understand how to use polars.

IMO reading manuals is a super power and everybody can attain it. :shrug:

## Setup

### Install


```python
!cat requirements.txt
```

    polars[plot,pyarrow]==1.2.1
    pandera[polars]==0.20.3
    jupyter
    jupytext
    ruff



```python
!pip install -r requirements.txt
```

### Import


```python
import polars as pl

# I personally like to import col as c to shorten some expressions
from polars import col as c
```

## Basics

### Creating/Reading/Saving DataFrames


```python
# Create DataFrame
df = pl.DataFrame(
    {
        "nrs": [1, 2, 3, None, 5],
        "names": ["foo", "ham", "spam", "egg", None],
        "random": [0.3, 0.7, 0.1, 0.9, 0.6],
        "groups": ["A", "A", "B", "C", "B"],
    }
)
df
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td></tr></tbody></table></div>




```python
# Save dataframes as csv
# (do yourself a favour and switch to parquet instead of CSV!)
df.write_csv("df.csv")
```


```python
# Read CSV
(pl.read_csv("df.csv", columns=["nrs", "names", "random", "groups"]).equals(df))
```




    True




```python
# Save dataframe as parquet
df.write_parquet("df.parquet")
```


```python
# Read parquet
# Note: you can also read multiple frames with wildcards
(pl.read_parquet("df*.parquet").equals(df))
```




    True



### Select columns - `select()`


```python
# Select multiple columns with specific names
df.select("nrs", "names")
# equivalent
df.select(pl.col("nrs"), pl.col("names"))
df.select(pl.col.nrs, pl.col.names)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 2)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th></tr><tr><td>i64</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td></tr><tr><td>3</td><td>&quot;spam&quot;</td></tr><tr><td>null</td><td>&quot;egg&quot;</td></tr><tr><td>5</td><td>null</td></tr></tbody></table></div>




```python
df.select(pl.all().exclude("random"))
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 3)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>&quot;A&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>&quot;A&quot;</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>&quot;B&quot;</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>&quot;C&quot;</td></tr><tr><td>5</td><td>null</td><td>&quot;B&quot;</td></tr></tbody></table></div>




```python
# Select columns whose name matches regular expression regex.
df.select(pl.col("^n.*$"))
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 2)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th></tr><tr><td>i64</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td></tr><tr><td>3</td><td>&quot;spam&quot;</td></tr><tr><td>null</td><td>&quot;egg&quot;</td></tr><tr><td>5</td><td>null</td></tr></tbody></table></div>



### Add New Columns - `select()` and `with_columns()`


```python
df.select(NAMES=c.names)
df.select(c("names").alias("NAMES"))
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 1)</small><table border="1" class="dataframe"><thead><tr><th>NAMES</th></tr><tr><td>str</td></tr></thead><tbody><tr><td>&quot;foo&quot;</td></tr><tr><td>&quot;ham&quot;</td></tr><tr><td>&quot;spam&quot;</td></tr><tr><td>&quot;egg&quot;</td></tr><tr><td>null</td></tr></tbody></table></div>




```python
# Keep existing and add new columns with `with_columns`
df.with_columns((pl.col("random") * pl.col("nrs")).alias("product"))
df.with_columns(product=pl.col("random") * pl.col("nrs"))
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 5)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th><th>product</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td><td>f64</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td><td>0.3</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td><td>1.4</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td><td>0.3</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td><td>null</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td><td>3.0</td></tr></tbody></table></div>




```python
# Add several new columns to the DataFrame
df.with_columns(
    product=(pl.col("random") * pl.col("nrs")),
    names_len_bytes=pl.col("names").str.len_bytes(),
)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 6)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th><th>product</th><th>names_len_bytes</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td><td>f64</td><td>u32</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td><td>0.3</td><td>3</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td><td>1.4</td><td>3</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td><td>0.3</td><td>4</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td><td>null</td><td>3</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td><td>3.0</td><td>null</td></tr></tbody></table></div>




```python
# Add a column 'index' that enumerates the rows
df.with_row_index()
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 5)</small><table border="1" class="dataframe"><thead><tr><th>index</th><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>u32</td><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>0</td><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td></tr><tr><td>1</td><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td></tr><tr><td>2</td><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td></tr><tr><td>3</td><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr><tr><td>4</td><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td></tr></tbody></table></div>



### Select rows - `filter()` and friends


```python
# Filter: Extract rows that meet logical criteria.
df.filter(pl.col("random") > 0.5)
df.filter(c("random") > 0.5)
df.filter(c.random > 0.5)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (3, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td></tr></tbody></table></div>




```python
df.filter((pl.col("groups") == "B") & (pl.col("random") > 0.5))
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (1, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td></tr></tbody></table></div>




```python
# Randomly select fraction of rows.
df.sample(fraction=0.5)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (2, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td></tr><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td></tr></tbody></table></div>




```python
# Randomly select n rows.
df.sample(n=2)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (2, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr></tbody></table></div>




```python
# Select first n rows
df.head(n=2)

# Select last n rows.
df.tail(n=2)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (2, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td></tr></tbody></table></div>



### Select rows and columns


```python
# Select rows 2-4
df[2:4, :]
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (2, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr></tbody></table></div>




```python
# Select columns in positions 1 and 3 (first column is 0).
df[:, [1, 3]]
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 2)</small><table border="1" class="dataframe"><thead><tr><th>names</th><th>groups</th></tr><tr><td>str</td><td>str</td></tr></thead><tbody><tr><td>&quot;foo&quot;</td><td>&quot;A&quot;</td></tr><tr><td>&quot;ham&quot;</td><td>&quot;A&quot;</td></tr><tr><td>&quot;spam&quot;</td><td>&quot;B&quot;</td></tr><tr><td>&quot;egg&quot;</td><td>&quot;C&quot;</td></tr><tr><td>null</td><td>&quot;B&quot;</td></tr></tbody></table></div>




```python
# Select rows meeting logical condition, and only the specific columns.
(df.filter(pl.col("random") > 0.5).select("names", "groups"))
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (3, 2)</small><table border="1" class="dataframe"><thead><tr><th>names</th><th>groups</th></tr><tr><td>str</td><td>str</td></tr></thead><tbody><tr><td>&quot;ham&quot;</td><td>&quot;A&quot;</td></tr><tr><td>&quot;egg&quot;</td><td>&quot;C&quot;</td></tr><tr><td>null</td><td>&quot;B&quot;</td></tr></tbody></table></div>




```python
# Select one columns as Series
print(type(df["names"]))
df["names"]
```

    <class 'polars.series.series.Series'>





<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5,)</small><table border="1" class="dataframe"><thead><tr><th>names</th></tr><tr><td>str</td></tr></thead><tbody><tr><td>&quot;foo&quot;</td></tr><tr><td>&quot;ham&quot;</td></tr><tr><td>&quot;spam&quot;</td></tr><tr><td>&quot;egg&quot;</td></tr><tr><td>null</td></tr></tbody></table></div>



### Sort rows - `sort()`


```python
# Order rows by values of a column (high to low)
df.sort("random", descending=True)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td></tr><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td></tr></tbody></table></div>




```python
# Order by multiple rows
df.sort("groups", "random")
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr></tbody></table></div>



### Summarize Data


```python
# Tuple of # of rows, # of columns in DataFrame
df.shape
```




    (5, 4)




```python
# number of rows in DataFrame
len(df)
df.height
```




    5




```python
# number of cols in DataFrame
df.width
```




    4




```python
# Count number of rows with each unique value of variable
df["groups"].value_counts()
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (3, 2)</small><table border="1" class="dataframe"><thead><tr><th>groups</th><th>count</th></tr><tr><td>str</td><td>u32</td></tr></thead><tbody><tr><td>&quot;A&quot;</td><td>2</td></tr><tr><td>&quot;C&quot;</td><td>1</td></tr><tr><td>&quot;B&quot;</td><td>2</td></tr></tbody></table></div>




```python
# # of distinct values in a column
df["groups"].n_unique()
```




    3




```python
# Basic descriptive and statistics for each column
df.describe()
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (9, 5)</small><table border="1" class="dataframe"><thead><tr><th>statistic</th><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>str</td><td>f64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>&quot;count&quot;</td><td>4.0</td><td>&quot;4&quot;</td><td>5.0</td><td>&quot;5&quot;</td></tr><tr><td>&quot;null_count&quot;</td><td>1.0</td><td>&quot;1&quot;</td><td>0.0</td><td>&quot;0&quot;</td></tr><tr><td>&quot;mean&quot;</td><td>2.75</td><td>null</td><td>0.52</td><td>null</td></tr><tr><td>&quot;std&quot;</td><td>1.707825</td><td>null</td><td>0.319374</td><td>null</td></tr><tr><td>&quot;min&quot;</td><td>1.0</td><td>&quot;egg&quot;</td><td>0.1</td><td>&quot;A&quot;</td></tr><tr><td>&quot;25%&quot;</td><td>2.0</td><td>null</td><td>0.3</td><td>null</td></tr><tr><td>&quot;50%&quot;</td><td>3.0</td><td>null</td><td>0.6</td><td>null</td></tr><tr><td>&quot;75%&quot;</td><td>3.0</td><td>null</td><td>0.7</td><td>null</td></tr><tr><td>&quot;max&quot;</td><td>5.0</td><td>&quot;spam&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr></tbody></table></div>




```python
# Aggregation functions
df.select(
    # Sum values
    pl.sum("random").alias("sum"),
    # Minimum value
    pl.min("random").alias("min"),
    # Maximum value
    pl.max("random").alias("max"),
    # or
    pl.col("random").max().alias("other_max"),
    # Standard deviation
    pl.std("random").alias("std_dev"),
    # Variance
    pl.var("random").alias("variance"),
    # Median
    pl.median("random").alias("median"),
    # Mean
    pl.mean("random").alias("mean"),
    # Quantile
    pl.quantile("random", 0.75).alias("quantile_0.75"),
    # or
    pl.col("random").quantile(0.75).alias("other_quantile_0.75"),
    # First value
    pl.first("random").alias("first"),
)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (1, 11)</small><table border="1" class="dataframe"><thead><tr><th>sum</th><th>min</th><th>max</th><th>other_max</th><th>std_dev</th><th>variance</th><th>median</th><th>mean</th><th>quantile_0.75</th><th>other_quantile_0.75</th><th>first</th></tr><tr><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td></tr></thead><tbody><tr><td>2.6</td><td>0.1</td><td>0.9</td><td>0.9</td><td>0.319374</td><td>0.102</td><td>0.6</td><td>0.52</td><td>0.7</td><td>0.7</td><td>0.3</td></tr></tbody></table></div>



### Group And Aggregate Data - `group_by()` and `agg()`


```python
# Group by values in column named "col", returning a GroupBy object
df.group_by("groups")
```




    <polars.dataframe.group_by.GroupBy at 0x7f674d02c990>




```python
# All of the aggregation functions from above can be applied to a group as well
df.group_by("groups").agg(
    # Sum values
    pl.sum("random").alias("sum"),
    # Minimum value
    pl.min("random").alias("min"),
    # Maximum value
    pl.max("random").alias("max"),
    # or
    pl.col("random").max().alias("other_max"),
    # Standard deviation
    pl.std("random").alias("std_dev"),
    # Variance
    pl.var("random").alias("variance"),
    # Median
    pl.median("random").alias("median"),
    # Mean
    pl.mean("random").alias("mean"),
    # Quantile
    pl.quantile("random", 0.75).alias("quantile_0.75"),
    # or
    pl.col("random").quantile(0.75).alias("other_quantile_0.75"),
    # First value
    pl.first("random").alias("first"),
)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (3, 12)</small><table border="1" class="dataframe"><thead><tr><th>groups</th><th>sum</th><th>min</th><th>max</th><th>other_max</th><th>std_dev</th><th>variance</th><th>median</th><th>mean</th><th>quantile_0.75</th><th>other_quantile_0.75</th><th>first</th></tr><tr><td>str</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td></tr></thead><tbody><tr><td>&quot;B&quot;</td><td>0.7</td><td>0.1</td><td>0.6</td><td>0.6</td><td>0.353553</td><td>0.125</td><td>0.35</td><td>0.35</td><td>0.6</td><td>0.6</td><td>0.1</td></tr><tr><td>&quot;C&quot;</td><td>0.9</td><td>0.9</td><td>0.9</td><td>0.9</td><td>null</td><td>null</td><td>0.9</td><td>0.9</td><td>0.9</td><td>0.9</td><td>0.9</td></tr><tr><td>&quot;A&quot;</td><td>1.0</td><td>0.3</td><td>0.7</td><td>0.7</td><td>0.282843</td><td>0.08</td><td>0.5</td><td>0.5</td><td>0.7</td><td>0.7</td><td>0.3</td></tr></tbody></table></div>




```python
# Additional GroupBy functions
(
    df.group_by("groups").agg(
        # Count the number of values in each group
        pl.count("random").alias("size"),
        # Sample one element in each group
        # (favour `map_elements` over `apply`)
        pl.col("names").map_elements(
            lambda group_df: group_df.sample(1).item(0), return_dtype=pl.String
        ),
    )
)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (3, 3)</small><table border="1" class="dataframe"><thead><tr><th>groups</th><th>size</th><th>names</th></tr><tr><td>str</td><td>u32</td><td>str</td></tr></thead><tbody><tr><td>&quot;A&quot;</td><td>2</td><td>&quot;foo&quot;</td></tr><tr><td>&quot;B&quot;</td><td>2</td><td>null</td></tr><tr><td>&quot;C&quot;</td><td>1</td><td>&quot;egg&quot;</td></tr></tbody></table></div>




```python
(df.group_by("groups").agg(pl.col("names").sample(1).alias("foo")))
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (3, 2)</small><table border="1" class="dataframe"><thead><tr><th>groups</th><th>foo</th></tr><tr><td>str</td><td>list[str]</td></tr></thead><tbody><tr><td>&quot;C&quot;</td><td>[&quot;egg&quot;]</td></tr><tr><td>&quot;B&quot;</td><td>[null]</td></tr><tr><td>&quot;A&quot;</td><td>[&quot;foo&quot;]</td></tr></tbody></table></div>



### Reshaping Data - Changing Layout and Renaming


```python
# Rename the columns of a DataFrame
df.rename({"nrs": "idx"})
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 4)</small><table border="1" class="dataframe"><thead><tr><th>idx</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td></tr></tbody></table></div>




```python
# Drop columns from DataFrame
df.drop(["names", "random"])
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 2)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>groups</th></tr><tr><td>i64</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;A&quot;</td></tr><tr><td>2</td><td>&quot;A&quot;</td></tr><tr><td>3</td><td>&quot;B&quot;</td></tr><tr><td>null</td><td>&quot;C&quot;</td></tr><tr><td>5</td><td>&quot;B&quot;</td></tr></tbody></table></div>




```python
df2 = pl.DataFrame(
    {
        "nrs": [6],
        "names": ["wow"],
        "random": [0.9],
        "groups": ["B"],
    }
)

df3 = pl.DataFrame(
    {
        "primes": [2, 3, 5, 7, 11],
    }
)
```


```python
# Append rows of DataFrames.
pl.concat([df, df2])
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (6, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td></tr><tr><td>6</td><td>&quot;wow&quot;</td><td>0.9</td><td>&quot;B&quot;</td></tr></tbody></table></div>




```python
# Append columns of DataFrames
pl.concat([df, df3], how="horizontal")
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 5)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th><th>primes</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td><td>i64</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td><td>2</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td><td>3</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td><td>5</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td><td>7</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td><td>11</td></tr></tbody></table></div>




```python
# Spread rows into columns
df.pivot(values="nrs", index="groups", columns="names")
```

    /tmp/ipykernel_20290/3836154377.py:2: DeprecationWarning: The argument `columns` for `DataFrame.pivot` is deprecated. It has been renamed to `on`.
      df.pivot(values="nrs", index="groups", columns="names")





<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (3, 6)</small><table border="1" class="dataframe"><thead><tr><th>groups</th><th>foo</th><th>ham</th><th>spam</th><th>egg</th><th>null</th></tr><tr><td>str</td><td>i64</td><td>i64</td><td>i64</td><td>i64</td><td>i64</td></tr></thead><tbody><tr><td>&quot;A&quot;</td><td>1</td><td>2</td><td>null</td><td>null</td><td>null</td></tr><tr><td>&quot;B&quot;</td><td>null</td><td>null</td><td>3</td><td>null</td><td>5</td></tr><tr><td>&quot;C&quot;</td><td>null</td><td>null</td><td>null</td><td>null</td><td>null</td></tr></tbody></table></div>




```python
# Gather columns into rows (this is equivalent to the deprecated melt() function)
df.unpivot(index="nrs", on=["names", "groups"])
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (10, 3)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>variable</th><th>value</th></tr><tr><td>i64</td><td>str</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;names&quot;</td><td>&quot;foo&quot;</td></tr><tr><td>2</td><td>&quot;names&quot;</td><td>&quot;ham&quot;</td></tr><tr><td>3</td><td>&quot;names&quot;</td><td>&quot;spam&quot;</td></tr><tr><td>null</td><td>&quot;names&quot;</td><td>&quot;egg&quot;</td></tr><tr><td>5</td><td>&quot;names&quot;</td><td>null</td></tr><tr><td>1</td><td>&quot;groups&quot;</td><td>&quot;A&quot;</td></tr><tr><td>2</td><td>&quot;groups&quot;</td><td>&quot;A&quot;</td></tr><tr><td>3</td><td>&quot;groups&quot;</td><td>&quot;B&quot;</td></tr><tr><td>null</td><td>&quot;groups&quot;</td><td>&quot;C&quot;</td></tr><tr><td>5</td><td>&quot;groups&quot;</td><td>&quot;B&quot;</td></tr></tbody></table></div>



### Reshaping Data - Joining Data Sets


```python
df4 = pl.DataFrame(
    {
        "nrs": [1, 2, 5, 6],
        "animals": ["cheetah", "lion", "leopard", "tiger"],
    }
)
```


```python
# Inner join
# Retains only rows with a match in the other set.
df.join(df4, on="nrs")
# or
df.join(df4, on="nrs", how="inner")
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (3, 5)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th><th>animals</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td><td>&quot;cheetah&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td><td>&quot;lion&quot;</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td><td>&quot;leopard&quot;</td></tr></tbody></table></div>




```python
# Left join
# Retains each row from "left" set (df).
df.join(df4, on="nrs", how="left")
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 5)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th><th>animals</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td><td>&quot;cheetah&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td><td>&quot;lion&quot;</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td><td>null</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td><td>null</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td><td>&quot;leopard&quot;</td></tr></tbody></table></div>




```python
# Outer join
# Retains each row, even if no other matching row exists.
df.join(df4, on="nrs", how="outer")
```

    /tmp/ipykernel_20290/1617706674.py:3: DeprecationWarning: Use of `how='outer'` should be replaced with `how='full'`.
      df.join(df4, on="nrs", how="outer")





<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (6, 6)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th><th>nrs_right</th><th>animals</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td><td>i64</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td><td>1</td><td>&quot;cheetah&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td><td>2</td><td>&quot;lion&quot;</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td><td>null</td><td>null</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td><td>null</td><td>null</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td><td>5</td><td>&quot;leopard&quot;</td></tr><tr><td>null</td><td>null</td><td>null</td><td>null</td><td>6</td><td>&quot;tiger&quot;</td></tr></tbody></table></div>




```python
# Anti join
# Contains all rows from df that do not have a match in df4.
df.join(df4, on="nrs", how="anti")
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (2, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr></tbody></table></div>



## Misc

### Changing Entries That Match Certain Criteria
Use the `when().then().otherwise()` chain for this.


```python
df.with_columns(
    pl.when((c("groups") == "A") & (c("names") == "foo"))
    .then(9.0)
    .otherwise(c.random)
    .alias("random")
)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>9.0</td><td>&quot;A&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td></tr></tbody></table></div>



### Handling Missing Data


```python
# How many nulls per column?
df.null_count()
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (1, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>u32</td><td>u32</td><td>u32</td><td>u32</td></tr></thead><tbody><tr><td>1</td><td>1</td><td>0</td><td>0</td></tr></tbody></table></div>




```python
# Drop rows with any column having a null value
df.drop_nulls()
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (3, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td></tr></tbody></table></div>




```python
# Replace null values with given value
df.fill_null(42)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td></tr><tr><td>42</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td></tr></tbody></table></div>




```python
# Replace null values using forward strategy
df.fill_null(strategy="forward")
# Other fill strategies are "backward", "min", "max", "mean", "zero" and "one"
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td></tr><tr><td>3</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr><tr><td>5</td><td>&quot;egg&quot;</td><td>0.6</td><td>&quot;B&quot;</td></tr></tbody></table></div>




```python
# Replace floating point NaN values with given value
df.fill_nan(42)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td></tr></tbody></table></div>



### Rolling Functions


```python
# The following rolling functions are available
import numpy as np

df.select(
    pl.col("random"),
    # Rolling maximum value
    pl.col("random").rolling_max(window_size=2).alias("rolling_max"),
    # Rolling mean value
    pl.col("random").rolling_mean(window_size=2).alias("rolling_mean"),
    # Rolling median value
    pl.col("random")
    .rolling_median(window_size=2, min_periods=2)
    .alias("rolling_median"),
    # Rolling minimum value
    pl.col("random").rolling_min(window_size=2).alias("rolling_min"),
    # Rolling standard deviation
    pl.col("random").rolling_std(window_size=2).alias("rolling_std"),
    # Rolling sum values
    pl.col("random").rolling_sum(window_size=2).alias("rolling_sum"),
    # Rolling variance
    pl.col("random").rolling_var(window_size=2).alias("rolling_var"),
    # Rolling quantile
    pl.col("random")
    .rolling_quantile(quantile=0.75, window_size=2, min_periods=2)
    .alias("rolling_quantile"),
    # Rolling skew
    pl.col("random").rolling_skew(window_size=2).alias("rolling_skew"),
    # Rolling custom function
    pl.col("random")
    .rolling_map(function=np.nanstd, window_size=2)
    .alias("rolling_apply"),
)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 11)</small><table border="1" class="dataframe"><thead><tr><th>random</th><th>rolling_max</th><th>rolling_mean</th><th>rolling_median</th><th>rolling_min</th><th>rolling_std</th><th>rolling_sum</th><th>rolling_var</th><th>rolling_quantile</th><th>rolling_skew</th><th>rolling_apply</th></tr><tr><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td><td>f64</td></tr></thead><tbody><tr><td>0.3</td><td>null</td><td>null</td><td>null</td><td>null</td><td>null</td><td>null</td><td>null</td><td>null</td><td>null</td><td>null</td></tr><tr><td>0.7</td><td>0.7</td><td>0.5</td><td>0.5</td><td>0.3</td><td>0.282843</td><td>1.0</td><td>0.08</td><td>0.7</td><td>-4.3368e-16</td><td>0.2</td></tr><tr><td>0.1</td><td>0.7</td><td>0.4</td><td>0.4</td><td>0.1</td><td>0.424264</td><td>0.8</td><td>0.18</td><td>0.7</td><td>3.8549e-16</td><td>0.3</td></tr><tr><td>0.9</td><td>0.9</td><td>0.5</td><td>0.5</td><td>0.1</td><td>0.565685</td><td>1.0</td><td>0.32</td><td>0.9</td><td>0.0</td><td>0.4</td></tr><tr><td>0.6</td><td>0.9</td><td>0.75</td><td>0.75</td><td>0.6</td><td>0.212132</td><td>1.5</td><td>0.045</td><td>0.9</td><td>0.0</td><td>0.15</td></tr></tbody></table></div>



### Window Functions


```python
# Window functions allow to group by several columns simultaneously
df.select(
    "names",
    "groups",
    "random",
    pl.col("random").sum().over("names").alias("sum_by_names"),
    pl.col("random").sum().over("groups").alias("sum_by_groups"),
)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 5)</small><table border="1" class="dataframe"><thead><tr><th>names</th><th>groups</th><th>random</th><th>sum_by_names</th><th>sum_by_groups</th></tr><tr><td>str</td><td>str</td><td>f64</td><td>f64</td><td>f64</td></tr></thead><tbody><tr><td>&quot;foo&quot;</td><td>&quot;A&quot;</td><td>0.3</td><td>0.3</td><td>1.0</td></tr><tr><td>&quot;ham&quot;</td><td>&quot;A&quot;</td><td>0.7</td><td>0.7</td><td>1.0</td></tr><tr><td>&quot;spam&quot;</td><td>&quot;B&quot;</td><td>0.1</td><td>0.1</td><td>0.7</td></tr><tr><td>&quot;egg&quot;</td><td>&quot;C&quot;</td><td>0.9</td><td>0.9</td><td>0.9</td></tr><tr><td>null</td><td>&quot;B&quot;</td><td>0.6</td><td>0.6</td><td>0.7</td></tr></tbody></table></div>



### Date Range Creation


```python
# create data with pl.date_range
from datetime import date


df_date = pl.DataFrame(
    {
        # eager=True is important to turn the expression into actual data
        "date": pl.date_range(
            date(2024, 1, 1), date(2024, 1, 7), interval="1d", eager=True
        ),
        "value": [1, 2, 3, 4, 5, 6, 7],
    }
)
df_date
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (7, 2)</small><table border="1" class="dataframe"><thead><tr><th>date</th><th>value</th></tr><tr><td>date</td><td>i64</td></tr></thead><tbody><tr><td>2024-01-01</td><td>1</td></tr><tr><td>2024-01-02</td><td>2</td></tr><tr><td>2024-01-03</td><td>3</td></tr><tr><td>2024-01-04</td><td>4</td></tr><tr><td>2024-01-05</td><td>5</td></tr><tr><td>2024-01-06</td><td>6</td></tr><tr><td>2024-01-07</td><td>7</td></tr></tbody></table></div>



### Time-based Upsampling - `group_by_dynamic()`
`group_by_dynamic` has **many** useful options.

[[docs]](https://docs.pola.rs/py-polars/html/reference/dataframe/api/polars.DataFrame.group_by_dynamic.html#polars.DataFrame.group_by_dynamic)


```python
(df_date.group_by_dynamic("date", every="1w").agg(c.value.sum()))
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (1, 2)</small><table border="1" class="dataframe"><thead><tr><th>date</th><th>value</th></tr><tr><td>date</td><td>i64</td></tr></thead><tbody><tr><td>2024-01-01</td><td>28</td></tr></tbody></table></div>



### Custom Expressions
You can create your own expression and reuse them throughout your projects.


```python
def normalize_str_col(col_name: str) -> pl.Expr:
    return pl.col(col_name).str.to_lowercase().str.replace_all(" ", "_")


df.select(new_col=normalize_str_col(col_name="groups"))
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 1)</small><table border="1" class="dataframe"><thead><tr><th>new_col</th></tr><tr><td>str</td></tr></thead><tbody><tr><td>&quot;a&quot;</td></tr><tr><td>&quot;a&quot;</td></tr><tr><td>&quot;b&quot;</td></tr><tr><td>&quot;c&quot;</td></tr><tr><td>&quot;b&quot;</td></tr></tbody></table></div>



## Plotting
Polars does not implement plotting itself, but delegates to `hvplot`.
The plot functions are available via the `.plot` accessor.

[[docs]](https://docs.pola.rs/py-polars/html/reference/dataframe/plot.html)


```python
df
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (5, 4)</small><table border="1" class="dataframe"><thead><tr><th>nrs</th><th>names</th><th>random</th><th>groups</th></tr><tr><td>i64</td><td>str</td><td>f64</td><td>str</td></tr></thead><tbody><tr><td>1</td><td>&quot;foo&quot;</td><td>0.3</td><td>&quot;A&quot;</td></tr><tr><td>2</td><td>&quot;ham&quot;</td><td>0.7</td><td>&quot;A&quot;</td></tr><tr><td>3</td><td>&quot;spam&quot;</td><td>0.1</td><td>&quot;B&quot;</td></tr><tr><td>null</td><td>&quot;egg&quot;</td><td>0.9</td><td>&quot;C&quot;</td></tr><tr><td>5</td><td>null</td><td>0.6</td><td>&quot;B&quot;</td></tr></tbody></table></div>




```python
(
    df.group_by("groups", maintain_order=True)
    .agg(pl.sum("random"))
    .plot.bar(x="groups", y="random")
)
```

    %opts magic unavailable (pyparsing cannot be imported)
    %compositor magic unavailable (pyparsing cannot be imported)







<style>*[data-root-id],
*[data-root-id] > * {
  box-sizing: border-box;
  font-family: var(--jp-ui-font-family);
  font-size: var(--jp-ui-font-size1);
  color: var(--vscode-editor-foreground, var(--jp-ui-font-color1));
}

/* Override VSCode background color */
.cell-output-ipywidget-background:has(
    > .cell-output-ipywidget-background > .lm-Widget > *[data-root-id]
  ),
.cell-output-ipywidget-background:has(> .lm-Widget > *[data-root-id]) {
  background-color: transparent !important;
}
</style>



<div id='p1002'>
  <div id="e2d2945b-0ec7-4638-be07-5a0052166451" data-root-id="p1002" style="display: contents;"></div>
</div>
<script type="application/javascript">(function(root) {
  var docs_json = {"a6326047-3672-434b-bae6-3098094d02b7":{"version":"3.4.2","title":"Bokeh Application","roots":[{"type":"object","name":"panel.models.browser.BrowserInfo","id":"p1002"},{"type":"object","name":"panel.models.comm_manager.CommManager","id":"p1003","attributes":{"plot_id":"p1002","comm_id":"27e7d69f8176448ca5e88b8f60e1cce6","client_comm_id":"0aa233070fff4903bc25e8551bfb2891"}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"copy_to_clipboard1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"value","kind":"Any","default":null}]}]}};
  var render_items = [{"docid":"a6326047-3672-434b-bae6-3098094d02b7","roots":{"p1002":"e2d2945b-0ec7-4638-be07-5a0052166451"},"root_ids":["p1002"]}];
  var docs = Object.values(docs_json)
  if (!docs) {
    return
  }
  const py_version = docs[0].version.replace('rc', '-rc.').replace('.dev', '-dev.')
  async function embed_document(root) {
    var Bokeh = get_bokeh(root)
    await Bokeh.embed.embed_items_notebook(docs_json, render_items);
    for (const render_item of render_items) {
      for (const root_id of render_item.root_ids) {
	const id_el = document.getElementById(root_id)
	if (id_el.children.length && id_el.children[0].hasAttribute('data-root-id')) {
	  const root_el = id_el.children[0]
	  root_el.id = root_el.id + '-rendered'
	  for (const child of root_el.children) {
            // Ensure JupyterLab does not capture keyboard shortcuts
            // see: https://jupyterlab.readthedocs.io/en/4.1.x/extension/notebook.html#keyboard-interaction-model
	    child.setAttribute('data-lm-suppress-shortcuts', 'true')
	  }
	}
      }
    }
  }
  function get_bokeh(root) {
    if (root.Bokeh === undefined) {
      return null
    } else if (root.Bokeh.version !== py_version) {
      if (root.Bokeh.versions === undefined || !root.Bokeh.versions.has(py_version)) {
	return null
      }
      return root.Bokeh.versions.get(py_version);
    } else if (root.Bokeh.version === py_version) {
      return root.Bokeh
    }
    return null
  }
  function is_loaded(root) {
    var Bokeh = get_bokeh(root)
    return (Bokeh != null && Bokeh.Panel !== undefined)
  }
  if (is_loaded(root)) {
    embed_document(root);
  } else {
    var attempts = 0;
    var timer = setInterval(function(root) {
      if (is_loaded(root)) {
        clearInterval(timer);
        embed_document(root);
      } else if (document.readyState == "complete") {
        attempts++;
        if (attempts > 200) {
          clearInterval(timer);
	  var Bokeh = get_bokeh(root)
	  if (Bokeh == null || Bokeh.Panel == null) {
            console.warn("Panel: ERROR: Unable to run Panel code because Bokeh or Panel library is missing");
	  } else {
	    console.warn("Panel: WARNING: Attempting to render but not all required libraries could be resolved.")
	    embed_document(root)
	  }
        }
      }
    }, 25, root)
  }
})(window);</script>







<div id='p1004'>
  <div id="bb692441-3d3f-4cbc-b4bc-2cb6519ba73c" data-root-id="p1004" style="display: contents;"></div>
</div>
<script type="application/javascript">(function(root) {
  var docs_json = {"0fe96f77-1dd6-468e-bcde-b4b98bb2286b":{"version":"3.4.2","title":"Bokeh Application","roots":[{"type":"object","name":"Row","id":"p1004","attributes":{"name":"Row00938","tags":["embedded"],"stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"type":"object","name":"ImportedStyleSheet","id":"p1007","attributes":{"url":"https://cdn.holoviz.org/panel/1.4.4/dist/css/loading.css"}},{"type":"object","name":"ImportedStyleSheet","id":"p1063","attributes":{"url":"https://cdn.holoviz.org/panel/1.4.4/dist/css/listpanel.css"}},{"type":"object","name":"ImportedStyleSheet","id":"p1005","attributes":{"url":"https://cdn.holoviz.org/panel/1.4.4/dist/bundled/theme/default.css"}},{"type":"object","name":"ImportedStyleSheet","id":"p1006","attributes":{"url":"https://cdn.holoviz.org/panel/1.4.4/dist/bundled/theme/native.css"}}],"min_width":700,"margin":0,"sizing_mode":"stretch_width","align":"start","children":[{"type":"object","name":"Spacer","id":"p1008","attributes":{"name":"HSpacer00945","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"p1007"},{"id":"p1005"},{"id":"p1006"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}},{"type":"object","name":"Figure","id":"p1016","attributes":{"width":700,"height":300,"margin":[5,10],"sizing_mode":"fixed","align":"start","x_range":{"type":"object","name":"FactorRange","id":"p1009","attributes":{"tags":[[["groups",null]],[]],"factors":["A","B","C"]}},"y_range":{"type":"object","name":"Range1d","id":"p1010","attributes":{"tags":[[["random",null]],{"type":"map","entries":[["invert_yaxis",false],["autorange",false]]}],"end":1.03,"reset_start":0.0,"reset_end":1.03}},"x_scale":{"type":"object","name":"CategoricalScale","id":"p1026"},"y_scale":{"type":"object","name":"LinearScale","id":"p1027"},"title":{"type":"object","name":"Title","id":"p1019","attributes":{"text_color":"black","text_font_size":"12pt"}},"renderers":[{"type":"object","name":"GlyphRenderer","id":"p1056","attributes":{"data_source":{"type":"object","name":"ColumnDataSource","id":"p1047","attributes":{"selected":{"type":"object","name":"Selection","id":"p1048","attributes":{"indices":[],"line_indices":[]}},"selection_policy":{"type":"object","name":"UnionRenderers","id":"p1049"},"data":{"type":"map","entries":[["groups",["A","B","C"]],["random",{"type":"ndarray","array":{"type":"bytes","data":"AAAAAAAA8D9mZmZmZmbmP83MzMzMzOw/"},"shape":[3],"dtype":"float64","order":"little"}]]}}},"view":{"type":"object","name":"CDSView","id":"p1057","attributes":{"filter":{"type":"object","name":"AllIndices","id":"p1058"}}},"glyph":{"type":"object","name":"VBar","id":"p1053","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"groups"},"width":{"type":"value","value":0.8},"top":{"type":"field","field":"random"},"fill_color":{"type":"value","value":"#30a2da"},"hatch_color":{"type":"value","value":"#30a2da"}}},"selection_glyph":{"type":"object","name":"VBar","id":"p1059","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"groups"},"width":{"type":"value","value":0.8},"bottom":{"type":"value","value":0},"top":{"type":"field","field":"random"},"line_color":{"type":"value","value":"black"},"line_alpha":{"type":"value","value":1.0},"line_width":{"type":"value","value":1},"line_join":{"type":"value","value":"bevel"},"line_cap":{"type":"value","value":"butt"},"line_dash":{"type":"value","value":[]},"line_dash_offset":{"type":"value","value":0},"fill_color":{"type":"value","value":"#30a2da"},"fill_alpha":{"type":"value","value":1.0},"hatch_color":{"type":"value","value":"#30a2da"},"hatch_alpha":{"type":"value","value":1.0},"hatch_scale":{"type":"value","value":12.0},"hatch_pattern":{"type":"value","value":null},"hatch_weight":{"type":"value","value":1.0}}},"nonselection_glyph":{"type":"object","name":"VBar","id":"p1054","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"groups"},"width":{"type":"value","value":0.8},"top":{"type":"field","field":"random"},"line_alpha":{"type":"value","value":0.1},"fill_color":{"type":"value","value":"#30a2da"},"fill_alpha":{"type":"value","value":0.1},"hatch_color":{"type":"value","value":"#30a2da"},"hatch_alpha":{"type":"value","value":0.1}}},"muted_glyph":{"type":"object","name":"VBar","id":"p1055","attributes":{"tags":["apply_ranges"],"x":{"type":"field","field":"groups"},"width":{"type":"value","value":0.8},"top":{"type":"field","field":"random"},"line_alpha":{"type":"value","value":0.2},"fill_color":{"type":"value","value":"#30a2da"},"fill_alpha":{"type":"value","value":0.2},"hatch_color":{"type":"value","value":"#30a2da"},"hatch_alpha":{"type":"value","value":0.2}}}}}],"toolbar":{"type":"object","name":"Toolbar","id":"p1025","attributes":{"tools":[{"type":"object","name":"WheelZoomTool","id":"p1014","attributes":{"tags":["hv_created"],"renderers":"auto","zoom_together":"none"}},{"type":"object","name":"HoverTool","id":"p1015","attributes":{"tags":["hv_created"],"renderers":[{"id":"p1056"}],"tooltips":[["groups","@{groups}"],["random","@{random}"]]}},{"type":"object","name":"SaveTool","id":"p1038"},{"type":"object","name":"PanTool","id":"p1039"},{"type":"object","name":"BoxZoomTool","id":"p1040","attributes":{"overlay":{"type":"object","name":"BoxAnnotation","id":"p1041","attributes":{"syncable":false,"level":"overlay","visible":false,"left":{"type":"number","value":"nan"},"right":{"type":"number","value":"nan"},"top":{"type":"number","value":"nan"},"bottom":{"type":"number","value":"nan"},"left_units":"canvas","right_units":"canvas","top_units":"canvas","bottom_units":"canvas","line_color":"black","line_alpha":1.0,"line_width":2,"line_dash":[4,4],"fill_color":"lightgrey","fill_alpha":0.5}}}},{"type":"object","name":"ResetTool","id":"p1046"}],"active_drag":{"id":"p1039"},"active_scroll":{"id":"p1014"}}},"left":[{"type":"object","name":"LinearAxis","id":"p1033","attributes":{"ticker":{"type":"object","name":"BasicTicker","id":"p1034","attributes":{"mantissas":[1,2,5]}},"formatter":{"type":"object","name":"BasicTickFormatter","id":"p1035"},"axis_label":"random","major_label_policy":{"type":"object","name":"AllLabels","id":"p1036"}}}],"below":[{"type":"object","name":"CategoricalAxis","id":"p1028","attributes":{"ticker":{"type":"object","name":"CategoricalTicker","id":"p1029"},"formatter":{"type":"object","name":"CategoricalTickFormatter","id":"p1030"},"axis_label":"groups","major_label_policy":{"type":"object","name":"AllLabels","id":"p1031"}}}],"center":[{"type":"object","name":"Grid","id":"p1032","attributes":{"axis":{"id":"p1028"},"grid_line_color":null}},{"type":"object","name":"Grid","id":"p1037","attributes":{"dimension":1,"axis":{"id":"p1033"},"grid_line_color":null}}],"min_border_top":10,"min_border_bottom":10,"min_border_left":10,"min_border_right":10,"output_backend":"webgl"}},{"type":"object","name":"Spacer","id":"p1061","attributes":{"name":"HSpacer00946","stylesheets":["\n:host(.pn-loading):before, .pn-loading:before {\n  background-color: #c3c3c3;\n  mask-size: auto calc(min(50%, 400px));\n  -webkit-mask-size: auto calc(min(50%, 400px));\n}",{"id":"p1007"},{"id":"p1005"},{"id":"p1006"}],"margin":0,"sizing_mode":"stretch_width","align":"start"}}]}}],"defs":[{"type":"model","name":"ReactiveHTML1"},{"type":"model","name":"FlexBox1","properties":[{"name":"align_content","kind":"Any","default":"flex-start"},{"name":"align_items","kind":"Any","default":"flex-start"},{"name":"flex_direction","kind":"Any","default":"row"},{"name":"flex_wrap","kind":"Any","default":"wrap"},{"name":"gap","kind":"Any","default":""},{"name":"justify_content","kind":"Any","default":"flex-start"}]},{"type":"model","name":"FloatPanel1","properties":[{"name":"config","kind":"Any","default":{"type":"map"}},{"name":"contained","kind":"Any","default":true},{"name":"position","kind":"Any","default":"right-top"},{"name":"offsetx","kind":"Any","default":null},{"name":"offsety","kind":"Any","default":null},{"name":"theme","kind":"Any","default":"primary"},{"name":"status","kind":"Any","default":"normalized"}]},{"type":"model","name":"GridStack1","properties":[{"name":"mode","kind":"Any","default":"warn"},{"name":"ncols","kind":"Any","default":null},{"name":"nrows","kind":"Any","default":null},{"name":"allow_resize","kind":"Any","default":true},{"name":"allow_drag","kind":"Any","default":true},{"name":"state","kind":"Any","default":[]}]},{"type":"model","name":"drag1","properties":[{"name":"slider_width","kind":"Any","default":5},{"name":"slider_color","kind":"Any","default":"black"},{"name":"value","kind":"Any","default":50}]},{"type":"model","name":"click1","properties":[{"name":"terminal_output","kind":"Any","default":""},{"name":"debug_name","kind":"Any","default":""},{"name":"clears","kind":"Any","default":0}]},{"type":"model","name":"FastWrapper1","properties":[{"name":"object","kind":"Any","default":null},{"name":"style","kind":"Any","default":null}]},{"type":"model","name":"NotificationAreaBase1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0}]},{"type":"model","name":"NotificationArea1","properties":[{"name":"js_events","kind":"Any","default":{"type":"map"}},{"name":"notifications","kind":"Any","default":[]},{"name":"position","kind":"Any","default":"bottom-right"},{"name":"_clear","kind":"Any","default":0},{"name":"types","kind":"Any","default":[{"type":"map","entries":[["type","warning"],["background","#ffc107"],["icon",{"type":"map","entries":[["className","fas fa-exclamation-triangle"],["tagName","i"],["color","white"]]}]]},{"type":"map","entries":[["type","info"],["background","#007bff"],["icon",{"type":"map","entries":[["className","fas fa-info-circle"],["tagName","i"],["color","white"]]}]]}]}]},{"type":"model","name":"Notification","properties":[{"name":"background","kind":"Any","default":null},{"name":"duration","kind":"Any","default":3000},{"name":"icon","kind":"Any","default":null},{"name":"message","kind":"Any","default":""},{"name":"notification_type","kind":"Any","default":null},{"name":"_destroyed","kind":"Any","default":false}]},{"type":"model","name":"TemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"BootstrapTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"TemplateEditor1","properties":[{"name":"layout","kind":"Any","default":[]}]},{"type":"model","name":"MaterialTemplateActions1","properties":[{"name":"open_modal","kind":"Any","default":0},{"name":"close_modal","kind":"Any","default":0}]},{"type":"model","name":"copy_to_clipboard1","properties":[{"name":"fill","kind":"Any","default":"none"},{"name":"value","kind":"Any","default":null}]}]}};
  var render_items = [{"docid":"0fe96f77-1dd6-468e-bcde-b4b98bb2286b","roots":{"p1004":"bb692441-3d3f-4cbc-b4bc-2cb6519ba73c"},"root_ids":["p1004"]}];
  var docs = Object.values(docs_json)
  if (!docs) {
    return
  }
  const py_version = docs[0].version.replace('rc', '-rc.').replace('.dev', '-dev.')
  async function embed_document(root) {
    var Bokeh = get_bokeh(root)
    await Bokeh.embed.embed_items_notebook(docs_json, render_items);
    for (const render_item of render_items) {
      for (const root_id of render_item.root_ids) {
	const id_el = document.getElementById(root_id)
	if (id_el.children.length && id_el.children[0].hasAttribute('data-root-id')) {
	  const root_el = id_el.children[0]
	  root_el.id = root_el.id + '-rendered'
	  for (const child of root_el.children) {
            // Ensure JupyterLab does not capture keyboard shortcuts
            // see: https://jupyterlab.readthedocs.io/en/4.1.x/extension/notebook.html#keyboard-interaction-model
	    child.setAttribute('data-lm-suppress-shortcuts', 'true')
	  }
	}
      }
    }
  }
  function get_bokeh(root) {
    if (root.Bokeh === undefined) {
      return null
    } else if (root.Bokeh.version !== py_version) {
      if (root.Bokeh.versions === undefined || !root.Bokeh.versions.has(py_version)) {
	return null
      }
      return root.Bokeh.versions.get(py_version);
    } else if (root.Bokeh.version === py_version) {
      return root.Bokeh
    }
    return null
  }
  function is_loaded(root) {
    var Bokeh = get_bokeh(root)
    return (Bokeh != null && Bokeh.Panel !== undefined)
  }
  if (is_loaded(root)) {
    embed_document(root);
  } else {
    var attempts = 0;
    var timer = setInterval(function(root) {
      if (is_loaded(root)) {
        clearInterval(timer);
        embed_document(root);
      } else if (document.readyState == "complete") {
        attempts++;
        if (attempts > 200) {
          clearInterval(timer);
	  var Bokeh = get_bokeh(root)
	  if (Bokeh == null || Bokeh.Panel == null) {
            console.warn("Panel: ERROR: Unable to run Panel code because Bokeh or Panel library is missing");
	  } else {
	    console.warn("Panel: WARNING: Attempting to render but not all required libraries could be resolved.")
	    embed_document(root)
	  }
        }
      }
    }, 25, root)
  }
})(window);</script>



## Debugging
If you have a long chain of transformations, it can be handy to look at / log intemediate steps.
Write little helpers to make this easy and call them via `pipe()`.


```python
def log_df(df: pl.DataFrame, prefix="") -> pl.DataFrame:
    print(f"{prefix}shape:{df.shape}  schema: {dict(df.schema)}")
    return df


(
    df.pipe(log_df, "step 1: ")
    .filter(c.random > 0.5)
    .pipe(log_df, "step 2: ")
    .select("names")
    .pipe(log_df, "step 3: ")
)
```

    step 1: shape:(5, 4)  schema: {'nrs': Int64, 'names': String, 'random': Float64, 'groups': String}
    step 2: shape:(3, 4)  schema: {'nrs': Int64, 'names': String, 'random': Float64, 'groups': String}
    step 3: shape:(3, 1)  schema: {'names': String}





<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (3, 1)</small><table border="1" class="dataframe"><thead><tr><th>names</th></tr><tr><td>str</td></tr></thead><tbody><tr><td>&quot;ham&quot;</td></tr><tr><td>&quot;egg&quot;</td></tr><tr><td>null</td></tr></tbody></table></div>



## Eager, lazy, out-of-core
Lazy mode allows optimization of the query plan.

Out-of-core or streaming allows to work with data that is bigger than the RAM.


```python
# eager loading, lazy execution
data = pl.read_parquet("df.parquet")
(
    data.lazy()
    .group_by("groups")
    .agg(pl.sum("random").alias("total"))
    .sort("total")
    # till here nothing really happened
    .collect()  # now we execute the plan and collect the results
)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (3, 2)</small><table border="1" class="dataframe"><thead><tr><th>groups</th><th>total</th></tr><tr><td>str</td><td>f64</td></tr></thead><tbody><tr><td>&quot;B&quot;</td><td>0.7</td></tr><tr><td>&quot;C&quot;</td><td>0.9</td></tr><tr><td>&quot;A&quot;</td><td>1.0</td></tr></tbody></table></div>




```python
# lazy loading, lazy execution
data = pl.scan_parquet("df.parquet")
(
    data.lazy()
    .group_by("groups")
    .agg(pl.sum("random").alias("total"))
    .sort("total")
    # till here nothing really happened
    # with the next line, we execute the plan and collect the results
    .collect()
)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (3, 2)</small><table border="1" class="dataframe"><thead><tr><th>groups</th><th>total</th></tr><tr><td>str</td><td>f64</td></tr></thead><tbody><tr><td>&quot;B&quot;</td><td>0.7</td></tr><tr><td>&quot;C&quot;</td><td>0.9</td></tr><tr><td>&quot;A&quot;</td><td>1.0</td></tr></tbody></table></div>




```python
# stream data
data = pl.scan_parquet("df.parquet")
(
    data.lazy()
    .group_by("groups")
    .agg(pl.sum("random").alias("total"))
    .sort("total")
    # till here nothing really happened
    # with the next line, we execute the plan in a streaming fashion
    .collect(streaming=True)
)
```




<div><style>
.dataframe > thead > tr,
.dataframe > tbody > tr {
  text-align: right;
  white-space: pre-wrap;
}
</style>
<small>shape: (3, 2)</small><table border="1" class="dataframe"><thead><tr><th>groups</th><th>total</th></tr><tr><td>str</td><td>f64</td></tr></thead><tbody><tr><td>&quot;B&quot;</td><td>0.7</td></tr><tr><td>&quot;C&quot;</td><td>0.9</td></tr><tr><td>&quot;A&quot;</td><td>1.0</td></tr></tbody></table></div>



## Data Validation with Pandera

Since 0.19 [pandera offers polars support](https://pandera.readthedocs.io/en/stable/polars.html).
That means you can validate the schema and data of your polars DataFrame.

This is just a sneak peak, read the docs for more.


```python
import pandera.polars as pa


# define your schema in as much detail as you want


class MySchema(pa.DataFrameModel):
    nrs: int
    names: str  # or pl.String
    # different range
    random: float = pa.Field(in_range={"min_value": 1.0, "max_value": 2.0})
    # C is not allowed
    groups: str = pa.Field(isin=["A", "B"])

    class Config:
        # All existing columns must be listed in the schema
        strict = True
```


```python
# Then validate it.
# Use lazy=True to run all validations before throwing the SchemaErrors
try:
    MySchema.validate(df, lazy=True)
except pa.errors.SchemaErrors as e:
    print("Got SchemaErrors exception.")
    print(e)
```

    Got SchemaErrors exception.
    {
        "SCHEMA": {
            "SERIES_CONTAINS_NULLS": [
                {
                    "schema": "MySchema",
                    "column": "nrs",
                    "check": "not_nullable",
                    "error": "non-nullable column 'nrs' contains null values"
                },
                {
                    "schema": "MySchema",
                    "column": "names",
                    "check": "not_nullable",
                    "error": "non-nullable column 'names' contains null values"
                }
            ]
        },
        "DATA": {
            "DATAFRAME_CHECK": [
                {
                    "schema": "MySchema",
                    "column": "random",
                    "check": "in_range(1.0, 2.0)",
                    "error": "Column 'random' failed validator number 0: <Check in_range: in_range(1.0, 2.0)> failure case examples: [{'random': 0.3}, {'random': 0.7}, {'random': 0.1}, {'random': 0.9}, {'random': 0.6}]"
                },
                {
                    "schema": "MySchema",
                    "column": "groups",
                    "check": "isin(['A', 'B'])",
                    "error": "Column 'groups' failed validator number 0: <Check isin: isin(['A', 'B'])> failure case examples: [{'groups': 'C'}]"
                }
            ]
        }
    }

