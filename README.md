# `nodata.science` - my blog

My personal website.

It uses a **very simple** self written site generator [`mksite.py`](mksite.py).
The style sheet is vanilla [simple.css](https://simplecss.org/).

## Usage

Use `poe` for all build tasks.
Some important tasks are:

```bash
poe clean

poe devgen
poe devsercer

poe proddeploy
```

## Useful snippets / notes

### Use `imagemagic` to replace transparent background with white background

```fish
for image in *.png
    echo $image
    convert $image -background white -alpha remove -alpha off $image
end
```
