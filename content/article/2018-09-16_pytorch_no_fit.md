---
title: "'No fit?' - Comparing high-level learning interfaces for PyTorch"
created_at: 2018-09-16
updated_at: 2024-01-29
author: Stefan Otte
_template: article.html
---

<p class="notice">
Note: you can find the jupyter notebook for this post <a href="https://github.com/sotte/sotte.github.io.resources">here</a>.
</p>

<p class="notice">
Update 2019-02-07:
Some corrections regarding skorch. See the update at the bottom of the page.
</p>

I really like `PyTorch` and [I'm not alone](https://twitter.com/karpathy/status/868178954032513024).
However, there is one aspect where `PyTorch` is not too user-friendly.
`PyTorch` does not have a nice high-level `fit` function,
i.e. a `fit` interface like `scikit-learn` or `keras`.
That is the complaint I hear most often about `PyTorch`.

I can't remember how often I have written a training loop in `PyTorch`
and how often I made mistakes doing so.
Writing a training loop is easy enough that anybody can do it,
but tricky enough that everybody can get it subtly wrong when she/he isn't paying full attention.
- Have you ever forgotten to call `model.eval()`? [[1]](https://twitter.com/karpathy/status/1013244313327681536)
- Have you ever forgotten to zero the gradients? [[2]](https://twitter.com/karpathy/status/1013244313327681536)
- Have you ever used the train data in the eval step?
- Have you ever forgotten to move the data to the GPU?
- Have you ever implemented a metric incorrectly?

These problems would be void if `PyTorch` offered a `fit` function ala [keras](https://keras.io/) or [scikit-learn](https://scikit-learn.org/).
(And, yes, you could argue that `PyTorch` is for power users and gives you all the power and flexibility so that you can implement the training loop tailored to your needs.
However, even if there was a `fit` function you could still implement a custom training loop if you really had to.)

In this post I'll evaluate the following high-level training libraries by solving a small image classification problem:
- `ignite` https://github.com/pytorch/ignite
- `skorch` https://github.com/dnouri/skorch
- `PyToune` https://github.com/GRAAL-Research/pytoune
- There are more ([tnt](https://github.com/pytorch/tnt), [fast.ai](https://github.com/fastai/fastai), ...) but it's too hot outside to spend more time in front of the computer.

Note: This is a biased comparision!
- I've used `ignite` before for small toy problems.
- I looked at `skorch` but didn't use it because the support for `PyTorch` datasets seemed weird.
- I've written my own little library and have my own ideas and preferences ;)

## The Classification Problem

I'll evaluate the three libraries by solving a simple image classification problem
within a 30 minute timeframe.
The demo task I'm trying to solve is a simple transfer learning task.
The data is taken from the [Dogs vs Cats kaggle challenge](https://www.kaggle.com/c/dogs-vs-cats)
and wrapped in a `DogsAndCatsDataset` class.
I'll use a pre-trained ResNet and only replace the last layer.

## Setup

This is the usual setup for most ML tasks: data, model, loss, and optimizer.
Feel free to skip it.

```python
import torch
import torch.nn.functional as F
import torch.nn as nn

import torchvision
import torchvision.transforms as transforms
from torch.utils.data import DataLoader
from torchvision.models.resnet import resnet18

import utils
from utils import DogsCatsDataset

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
```

### The Data

```python
def get_data(batch_size=64, sample=False):
    IMG_SIZE = 224
    _mean = [0.485, 0.456, 0.406]
    _std = [0.229, 0.224, 0.225]

    # transforms for dataset
    train_trans = transforms.Compose([
        # some images are too small to only crop --> resize first
        transforms.Resize(256),
        transforms.ColorJitter(.3, .3, .3),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(_mean, _std),
    ])
    val_trans = transforms.Compose([
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(_mean, _std),
    ])

    # dataset
    train_ds = DogsCatsDataset(
        "data",
        "sample/train" if sample else "train",
        transform=train_trans,
        download=True,
    )
    val_ds = DogsCatsDataset(
        "data",
        "sample/valid" if sample else "valid",
        transform=val_trans,
    )

    # data loader
    train_dl = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        num_workers=8,
    )
    val_dl = DataLoader(
        val_ds,
        batch_size=batch_size,
        shuffle=False,
        num_workers=8,
    )
    
    return train_dl, val_dl


train_dl, val_dl = get_data()
```

### Model, Loss, and Optimizer

We'll just use a simple pre-trained ResNet and replace the last fully connected layer with a problem specific layer, i.e. a linear layer with two outputs (one for cats, one for dogs).

```python
def get_model():
    model = resnet18(pretrained=True)
    utils.freeze_all(model.parameters())
    assert utils.all_frozen(model.parameters())

    model.fc = nn.Linear(in_features=512, out_features=2)
    assert utils.all_frozen(model.parameters()) is False

    return model


model = get_model().to(device)
```

We also need to specify the loss function and the optimizer.

```python
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
```

Just for the sake of completeness, a *simple* train loop would look something like this:

```python
def fit(model, criterion, optimizer, n_epochs):
    for epoch in range(n_epochs):
        print(f"Epoch {epoch+1}/{n_epochs} ...")

        # Train
        model.train()  # IMPORTANT
        running_loss, correct = 0.0, 0
        for X, y in train_dl:
            X, y = X.to(device), y.to(device)

            optimizer.zero_grad()
            y_ = model(X)
            loss = criterion(y_, y)

            loss.backward()
            optimizer.step()

            # Statistics
            #print(f"    batch loss: {loss.item():0.3f}")
            _, y_label_ = torch.max(y_, 1)
            correct += (y_label_ == y).sum().item()
            running_loss += loss.item() * X.shape[0]
        print(
            f"  "
            f"loss: {running_loss / len(train_dl.dataset):0.3f} "
            f"acc:  {correct / len(train_dl.dataset):0.3f}"
        )

        # Eval
        model.eval()  # IMPORTANT
        running_loss, correct = 0.0, 0
        with torch.no_grad():  # IMPORTANT
            for X, y in val_dl:
                X, y = X.to(device), y.to(device)

                y_ = model(X)
                loss = criterion(y_, y)

                _, y_label_ = torch.max(y_, 1)
                correct += (y_label_ == y).sum().item()            
                running_loss += loss.item() * X.shape[0]
        print(
            f"  "
            f"val_loss: {running_loss / len(val_dl.dataset):0.3f} "
            f"val_acc:  {correct / len(val_dl.dataset):0.3f}"
        )
```

Let's fit:

```python
%%time
fit(model, criterion, optimizer, n_epochs=2)
```

Output:

```text
Epoch 1/2 ...
  loss: 0.322 acc:  0.886
  val_loss: 0.204 val_acc:  0.938
Epoch 2/2 ...
  loss: 0.153 acc:  0.956
  val_loss: 0.151 val_acc:  0.947
CPU times: user 23 s, sys: 11.8 s, total: 34.8 s
Wall time: 49.3 s
```

## The Contenders

Here I will try to solve the task with the three libraries.

### Ignite
> Ignite is a high-level library to help with training neural networks in PyTorch.
> - ignite helps you write compact but full-featured training loops in a few lines of code
> - you get a training loop with metrics, early-stopping, model checkpointing and other features without the boilerplate

Github: https://github.com/pytorch/ignite

Homepage: https://pytorch.org/ignite/

`ignite` lives under the https://github.com/pytorch umbrella and can be installed with conda or pip:
```
conda install ignite -c pytorch
pip install pytorch-ignite
```

`ignite` does not hide what's going on under the hood, but offers some light abstraction around the training loop.
The main abstractions are `Engines` which loop over the data.
The `State` object is part of the engine and is used to track training/evaluation state.
Via `Events` and `Handlers` you can execute your custom code, e.g. printing out the current loss or storing a checkpoint.
You can register callbacks via decorators:
```python
@trainer.on(Events.ITERATION_COMPLETED)
def log_training_loss(trainer):
    pass
```

`ignite` offers two helper functions, `create_supervised_trainer` and `create_supervised_evaluator`, which create `Engine`s for training and evaluating and should cover >90% or your supervised learning problems (I think).
Even with these helpers, you still have to register callbacks to actually do something like logging and calculating of metrics (however, ignite offers some metrics).

All in all I like the documentation. They have a `Quickstart` and a `Concepts` section which should get you going pretty quick.
Out of the box, `ignite` does not give you any default logging or progress reports, but it's easy to add.
However, I wish `ignite` offered this feature out of the box.

I was done solving the task after ~20 minutes.
Here is the code:

```python
train_dl, val_dl = get_data()

model = get_model().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
```

```python
# The helper functions to create engines
from ignite.engine import (
    Events,
    create_supervised_trainer,
    create_supervised_evaluator,
)
# The metrics we're going to use
from ignite.metrics import (
    CategoricalAccuracy,
    Loss,
)
from ignite.handlers import Timer

# Setup
trainer = create_supervised_trainer(model, optimizer, criterion, device=device)
evaluator = create_supervised_evaluator(
    model,
    metrics={
        "accuracy": CategoricalAccuracy(),
        "loss": Loss(criterion),
    },
    device=device,
)


# logging for output and metrics
@trainer.on(Events.ITERATION_COMPLETED)
def log_training_loss(trainer):
    # too verbose
    # print("Epoch[{}] Loss: {:.2f}".format(trainer.state.epoch, trainer.state.output))
    pass


@trainer.on(Events.EPOCH_COMPLETED)
def log_training_results(trainer):
    evaluator.run(train_dl)
    metrics = evaluator.state.metrics
    print(
        f"Training Results - Epoch: {trainer.state.epoch} "
        f"Avg accuracy: {metrics['accuracy']:.2f} "
        f"Avg loss: {metrics['loss']:.2f}"
    )
    
    
@trainer.on(Events.EPOCH_COMPLETED)
def log_validation_results(trainer):
    evaluator.run(val_dl)
    metrics = evaluator.state.metrics
    print(
        f"Validation Results - Epoch: {trainer.state.epoch} "
        f"Avg accuracy: {metrics['accuracy']:.2f} "
        f"Avg loss: {metrics['loss']:.2f}"
    )


# let's measure the time
timer = Timer(average=True)
timer.attach(
    trainer,
    start=Events.EPOCH_STARTED,
    resume=Events.ITERATION_STARTED,
    pause=Events.ITERATION_STARTED,
    step=Events.ITERATION_COMPLETED,
)
```

```python
%%time
trainer.run(train_dl, max_epochs=2)
```

Output:

```text
Training Results - Epoch: 1 Avg accuracy: 0.96 Avg loss: 0.18
Validation Results - Epoch: 1 Avg accuracy: 0.94 Avg loss: 0.21
Training Results - Epoch: 2 Avg accuracy: 0.97 Avg loss: 0.12
Validation Results - Epoch: 2 Avg accuracy: 0.96 Avg loss: 0.15
CPU times: user 44.3 s, sys: 23.2 s, total: 1min 7s
Wall time: 1min 39s
```

### skorch

> A scikit-learn compatible neural network library that wraps pytorch.
>
> The goal of skorch is to make it possible to use PyTorch with sklearn. This is achieved by providing a wrapper around PyTorch that has an sklearn interface. In that sense, skorch is the spiritual successor to nolearn, but instead of using Lasagne and Theano, it uses PyTorch.

Github: https://github.com/dnouri/skorch

Homepage: https://skorch.readthedocs.io/en/latest/

`skorch` is by the [Otto group](https://github.com/ottogroup/) and can be installed via pip
```
pip install skorch
```
The focus of `skorch` is to build a sklearn-like interface for PyTorch.
I assume they use a lot of sklearn at Otto and they seamlessly want to intgrate PyTorch into their workflow (who could blame them).
`skorch` also integrates into their serving service [palladium](https://github.com/ottogroup/palladium).

`skorch` offers `NeuralNetClassifier` and `NeuralNetRegressor`.
These classes wrap PyTorch's `nn.Module` and offer the sklearn-compatible interface
(`fit`, `predict`, `predict_proba`, etc.).
If you want more control you can create your own class and inherit from `skorch.NeuralNet`.
Note that the `NeuralNet*` classes do internal cross validation.

`skorch` reuses alot of the sklearn goodness (metrics, grid search, pipelines) and that's great.
Additionally, `skorch` offers a simple Callback mechanism.
The documentation is great and the library feels pretty complete.

However, `skorch` does not allow me to wrap my existing datasets.
Maybe it does but I was not able to find out how within 30 minutes.
And I want to reuse all my Datasets :)

> skorch uses the PyTorch DataLoaders by default. However, the Datasets provided by PyTorch are not sufficient for our usecase; for instance, they don’t work with numpy.ndarrays. 

Due to the "dataset issue" I was not able to finish the task within 30 minutes.

Just to give you an idea of what the code looks like:

```python
from skorch.net import NeuralNetClassifier

model = NeuralNetClassifier(model_, max_epochs=2, device=device)
# I can't pass a dataloader
# model.fit(X, y)
```

### PyToune

> PyToune is a Keras-like framework for PyTorch and handles much of the boilerplating code needed to train neural networks.
>
> Use PyToune to:
> - Train models easily.
> - Use callbacks to save your best model, perform early stopping and much more.
>

Github: https://github.com/GRAAL-Research/pytoune

Homepage: https://pytoune.org/

`PyToune` is a relatively young project by [GRAAL-Research](https://github.com/GRAAL-Research).
It can be installed with pip:

```bash
pip install pytoune
```

`PyToune` feels very keras-y and I had a working version with progress reports and whatnot after just 7 minutes.
The main abstraction is the `Model` which takes a `PyTorch` `nn.Module`, an optimizer, and a loss function.
The `Model` then gives you an interface that is very similar to keras
(`fit()`, `fit_generator()`, `evaluate_generator()`, etc).
Additionally, you have a generic callback mechanism to interact with the opitmization process.
There are also some useful callbacks implemented (`ModelCheckpoint`, `EarlyStopping`, `TerminateOnNaN`, `BestModelRestore`, and wrappers for `PyTorch`'s learning rate schedulers).
`PyToune` offers some convenient layers like `Flatten`, `Identity`, and `Lambda` (I'm sure we've all written these many times, so I appreciate that :)).

The documentation is very short (just api docs, but good ones) and could use a "getting started" guide and  more narrative docs.
However, `PyToune` is so simple (in the best sense possible) that you are productive within a few minutes.

All in all: nice! The docs should be extended and I wish there were more metrics, but `PyToune` looks great.
I'm planning to use/evaluate it with some of my projects.

After 25 minutes I stopped because there wasn't anything to do anymore :)
Here is the code:

```python
train_dl, val_dl = get_data()

model_ = get_model().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model_.parameters(), lr=0.0001)
```

```python
from pytoune.framework import Model
from pytoune.framework.callbacks import ModelCheckpoint

model = Model(model_, optimizer, criterion, metrics=["accuracy"])
model = model.to(device)

model_checkpoint_cb = ModelCheckpoint(
    "pytoune_experiment_best_epoch_{epoch}.ckpt",
    monitor="val_acc",
    mode="max",
    save_best_only=True,
    restore_best=True,
    verbose=False,
    temporary_filename="best_epoch.ckpt.tmp",
)
```

```python
%%time
model.fit_generator(
    train_dl,
    valid_generator=val_dl,
    callbacks=[model_checkpoint_cb],
    epochs=2,
);
```

Output:

```text
Epoch 1/2 29.92s Step 360/360: loss: 0.331596, acc: 88.656522, val_loss: 0.202725, val_acc: 94.450000
Epoch 2/2 27.26s Step 360/360: loss: 0.153364, acc: 95.800000, val_loss: 0.147647, val_acc: 95.500000
CPU times: user 24.9 s, sys: 13.2 s, total: 38.2 s
Wall time: 57.3 s

[{'epoch': 1,
  'loss': 0.3315962664977364,
  'acc': 88.65652173913044,
  'val_loss': 0.20272484612464906,
  'val_acc': 94.45},
 {'epoch': 2,
  'loss': 0.15336425514584,
  'acc': 95.8,
  'val_loss': 0.14764661401510237,
  'val_acc': 95.5}]
```

```python
ls pytoune_*
```

Output:

```text
pytoune_experiment_best_epoch_1.ckpt  pytoune_experiment_best_epoch_2.ckpt
```

## Conclusion

All libraries look good.

- `ignite` is a elegant wrapper around `PyTorch`. However, it's a bit too low level for what I'm looking for.
- `skorch` is very complete and offers a ton of features. Sadly it does not play well with Dataset classes.
- `PyToune` clicked right away and if you're familiar with `keras` I'm sure it will click for you as well. 

I highly encourage you to check out `PyToune`!

**Update 2019-02-07:** One of the friendly folks from skorch reached out to me and corrected me:

> One thing to note is that if you have a 'typical' dataset that provides a pair of `X`, `y` values then skorch already supports them as input to .fit: `net.fit(train_dataset, y=None)`
>
> There are also example notebooks that demonstrate this quite well, we hope:
>
> - [notebooks/Transfer_Learning](https://github.com/dnouri/skorch/blob/master/notebooks/Transfer_Learning.ipynb)
> - [notebooks/nuclei_image_segmentation](https://github.com/dnouri/skorch/blob/master/examples/nuclei_image_segmentation/Nuclei_Image_Segmentation.ipynb)

Thanks skorch and Marian for the information! Try out skorch!
