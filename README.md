# `nodata.science` - my blog

## Useful snippets / notes

### use imagemagic to replace transparent background with white background

```fish
for image in *.png
    echo $image
    convert $image -background white -alpha remove -alpha off $image
end
```
