---
title: Note to self - How to publish packages on PyPI
created_at: 2016-01-20
updated_at: 2024-01-26
author: Stefan Otte
_template: article.html
---

Update 2024: The information in this article is out of date.
Just use [poetry](https://python-poetry.org/) (or other modern tools).
That being said, it's quite interesting to see how the python packaging system has evolved over time.

One of the least favorite things about python is package and release management.
Even though it's getting better, there is still room for improvement.
There are guides of how to publish package on [PyPI][PyPI] out there,
but many are out of date and/or recommend methods that leak your password
(**DON'T** use `setup.py upload` or `setup.py register`!).

This guide is mostly for myself because I tend to forget things,
but maybe it's useful for someone else.
The authoritative source,
and everybody should know about it,
is [python packaging][python packaging].
It's a bit lengthy but really good.

## Goal

The goal is to release an already existing package
(which works with python 2&3 and does not include any compiled stuff)
on PyPI
as [source distribution][source distribution] and as [universal wheel][universal wheel]
so it's easy to `pip install`.

## Tools

The tools we're going to be using:

- use `setuptools` in your `setup.py`,
- use `pip` for installing,
- use `wheels` to generate binary `universal wheel`_, and
- use `twine` to upload the packages to PyPI
  (`twine` uses an encrypted connection whereas `setup.py upload`
  leaks your password).

See [packaging tools][packaging tools] for more details.

## Preperation: Create accounts

Even if you only want to publish your package on [PyPI][PyPI]
you should have accounts on [PyPITest][PyPITest] (for testing purposes)
**and** PyPI (for the real thing).
Create accounts on both platforms.
Work with PyPITest until you have the workflow down.
Then actually release your package on PyPI.

After you registered on
[PyPI](https://pypi.python.org/pypi?%3Aaction=register_form) and
[PyPITest](https://testpypi.python.org/pypi?%3Aaction=register_form)
you should create a file `~/.pypirc` and add your credentials:

```ini
# .pypirc
[distutils]
index-servers=
    pypi
    pypitest

[pypitest]
repository=https://testpypi.python.org/pypi
username=<your user name goes here>
password=<your password goes here>

[pypi]
repository=https://pypi.python.org/pypi
username=<your user name goes here>
password=<your password goes here>
```

## Your Package Should Have

... a `setup.py` file, a `setup.cfg` file, and a `README.rst` file (and
a bunch of python code that actually does something).

How to structure your ``setup.py`` is described
[here](https://packaging.python.org/en/latest/distributing/#setup-args).

The `setup.cfg` is needed to create a universal wheels and should look like
this:

```ini
# setup.cfg
[bdist_wheel]
# univesal wheel
universal=1
```

I use `README.rst` because PyPI recognizes the `rst` format
and I can reuse the `README.rst` with sphinx.

## Steps to upload to PyPI(Test)

Given a proper setup package your can build the package:

```bash
# create a source distribution
python setup.py sdist
# create a universal wheel for
# (py2&3 without any ompiled stuff)
python setup.py bdist_wheel --universal
```

If the package is not on PyPI yet you have to register it first.
Register your package on PyPI by uploading the `PKG-INFO`
from `myproject.egg-info/PKG-INFO`
via the [PyPITest web form](https://testpypi.python.org/pypi?%3Aaction=submit_form)
or the [PyPI web form](https://testpypi.python.org/pypi?%3Aaction=submit_form).
DON'T use `python setup.py register` because it leaks your password!

Then upload it to PyPITest:

```bash
twine upload --repository pypitest dist/*
```

or PyPI:

```bash
twine upload --repository pypi dist/*
```

## Conclusion

Congratulations, you're done!
Once you know what to do it's not that hard :)

I think it's a pain that default tools leak your password and you're forced
to upload PKG
`PKG-INFO` via a web form and install `twine` to upload the packages.
Hopefully that changes at some point...

<!-- links -->
[PyPITest]: https://testpypi.python.org/pypi
[PyPI]: https://pypi.python.org/pypi
[python packaging]: https://packaging.python.org/en/latest/
[universal wheel]: https://packaging.python.org/en/latest/distributing/#universal-wheels
[source distribution]: https://packaging.python.org/en/latest/glossary/#term-source-distribution-or-sdist
[packaging tools]: https://packaging.python.org/en/latest/current/
