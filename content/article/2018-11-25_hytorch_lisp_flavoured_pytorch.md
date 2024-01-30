---
title: HyTorch - A lisp flavoured PyTorch
created_at: 2018-11-25
updated_at: 2024-01-26
author: Stefan Otte
---

Clearly, this post falls into the category: "don't try this at home",
or, the developers' equivalent: "don't use this in production".
With the warning out of the way, you should really try `HyTorch` if you feel
particularly bored on a cold Sunday!

`HyTorch` is not really a thing or library.
It is just [hy](http://hylang.org/), "a dialect of Lisp that's embedded in Python",
and PyTorch 1.0 nightly, because we don't want this project to be too stable.

Why am I doing this?
Don't get me wrong, I really like python, and it's my main language for all
things data science and machine learning.
(Also there are pretty cool things happening in python land:
type annotations ([PEP484](https://www.python.org/dev/peps/pep-0484/), [PEP483](https://www.python.org/dev/peps/pep-0483/),
and [PEP526](https://www.python.org/dev/peps/pep-0526/)),
[PEP557 data classes](https://www.python.org/dev/peps/pep-0557/),
[hypothesis - property based testing](https://hypothesis.works/),
[asyncio](https://docs.python.org/3/library/asyncio.html#module-asyncio)
and [trio](https://trio.readthedocs.io/en/latest/),
[dask](https://dask.org/), and more).
But I also like functional languages, immutability, "proper" concurrency and parallelism,
Clojure, Elixir/Erlang with OTP and more.
Sometimes it's just fun to play with a new thing (even though in this case it's technically still python).

## Hy lang

We setup hy in a virtualenv for `hy`:

```bash
virtualenv --p python3.7 .venv
source .venv/bin/activate
# install hy
pip install git+https://github.com/hylang/hy.git
```

Here is a short demo of a few very basic hy features:
```hy
#!/usr/bin/env hy

(print "Hello world")
(print (+ "hello" "world" "!"))
(print)

(defn greet []
  (print (* "Hello world!\n" 5)))

(greet)

; lists
(setv some_list [1, 2, 3])
(print some_list)

; dicts
(setv some_dict {1 "one" 2 "two"})
(print some_dict)

; using python's std lib
(import os)
(print (os.cpu_count))
```
You can also import hy from your python program!
Pretty crazy already :)

If you would like to learn more, the [official hy tutorial](http://docs.hylang.org/en/stable/tutorial.html)
and [learn x in y](https://learnxinyminutes.com/docs/hy/) are good.
Paul Tagliamonte, one of the creators of hy, has a very entertaining talk on YouTube: [Getting Hy on Python: How to implement a Lisp front-end to Python](https://www.youtube.com/watch?v=AmMaN1AokTI).


## PyTorch nightly

Install the PyTorch 1.0 preview with `pip` for linux and python 3.7 and CUDA 9.0:
```bash
pip install numpy torchvision_nightly
pip install torch_nightly -f https://download.pytorch.org/whl/nightly/cu90/torch_nightly.html
python -c "import torch; print(torch.cuda.is_available())"
# True
```

## Hy + PyTorch = HyTorch

Now let's do some transfer learning with HyTorch.
We'll write a little image classifier that classifies
[dogs and cats](https://www.kaggle.com/c/dogs-vs-cats-redux-kernels-edition).

```hy
➤ # start the hy repl
➤ hy
hy 0.15.0+48.gc5abc85 using CPython(default) 3.7.0 on Linux
=> (print "# General infos")
# General infos
=> (import torch)
=> ; this is already amazing!
=> (print "GPU available:" (torch.cuda.is_available))
GPU available: True
=> ; we'll mode the model to the GPU later
=> (setv device (torch.device (lif (torch.cuda.is_available) "cuda:0" "cpu")))
=> (print "Device:" device)
Device: cuda:0
=>
=> (print "# Get the data")
# Get the data
=> ; I copy and pasted some utility functions
=> ; from an old pytorch tutorial into utils.py.
=> ; I'm importing python here!
=> (import utils)
=> (setv [train_dl val_dl]
...   (utils.get_data :batch_size 128 :image_size 224 :sample False :download False))
Loading data from data/dogscats/train.
Loading data from data/dogscats/valid.
=>
=> (print "# Get the model")
# Get the model
=> (setv module (utils.get_model 2))
=> ; this is a simple frozen ResNet model.
=> ; Now we use the amazing PyToune to train the model.
=> (import [pytoune.framework [Model]])
=> (setv model
...   (Model module "adam" "cross_entropy" :metrics ["accuracy"]))
=> (setv model
...   (model.to device))
=>
=> (print "# Train...")
# Train...
=> (import pprint)
=> (pprint.pprint
...   (model.fit_generator train_dl val_dl :epochs 2))
Epoch 1/2 52.61s Step 180/180: loss: 0.149578, acc: 94.730435, val_loss: 0.067275, val_acc: 97.750000
Epoch 2/2 53.10s Step 180/180: loss: 0.083727, acc: 96.821739, val_loss: 0.065457, val_acc: 97.250000
[{'acc': 94.7304347773013,
  'epoch': 1,
  'loss': 0.14957752645534017,
  'val_acc': 97.75,
  'val_loss': 0.06727455681562423},
 {'acc': 96.82173912247367,
  'epoch': 2,
  'loss': 0.08372681827130525,
  'val_acc': 97.25,
  'val_loss': 0.06545671501010657}]
```

Wow, this is cool and it all worked out of the box.
Downloading pytorch took me longer than writing the code to train the model and
I haven't used hy in several years.

I don't know where I want to go with this, but it sure was a fun little
experiment :)
