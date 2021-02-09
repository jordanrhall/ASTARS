# ASTARS

Derivative-Free Optimization (DFO) algorithm for noisy convex functions which leverages [active subspaces](https://github.com/paulcon/active_subspaces) for efficiency

Please see our corresponding [paper and technical report](https://arxiv.org/abs/2101.07444) on arXiv

## Installation instructions:

* If you do not have a computational environment set up to run Python, download [Anaconda](https://www.anaconda.com/products/individual)
* You'll need to clone the active subspaces library, updated to Python 3 by Varis, using `git clone https://github.com/variscarey/active_subspaces_py3.git` in a destination of your choosing (executed in terminal)
* Inside the active_subspaces_py3 directory you've just created, run `python setup.py install` (executed in terminal)
* Be sure to navigate __outside__ of active_subspaces_py3 in your terminal before the next step
* Next, clone this ASTARS repo locally, using `git clone git@github.com:jordanrhall/ASTARS.git` in a destination of your choosing (executed in terminal)
* Inside the ASTARS directory you've just created, run `python setup.py install` (executed in terminal)

Now you should be able to run any of our examples stored in paper_examples. 
e.g., Navigate to paper_examples in terminal and run `python paper_examples.py` (executed in terminal)

Enjoy!
