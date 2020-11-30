============
Installation
============

The easiest way to install ``ncvue`` is via ``pip``:

.. code-block:: bash

    pip install ncvue


Manual install
--------------

The latest version of ``ncvue`` can be installed from source:

.. code-block:: bash

    git clone https://github.com/mcuntz/ncvue.git
    cd ncvue
    pip install .


Local install
-------------

Users without proper privileges can append the `--user` flag to
``pip`` either while installing from the Python Package Index (PyPI):

.. code-block:: bash

    pip install ncvue --user

or from the top ``ncvue`` directory:

.. code-block:: bash

    git clone https://github.com/mcuntz/ncvue.git
    cd ncvue
    pip install . --user

If ``pip`` is not available, then `setup.py` can still be used:

.. code-block:: bash

    python setup.py install --user

When using `setup.py` locally, it might be that one needs to append `--prefix=`
to the command:

.. code-block:: bash

    python setup.py install --user --prefix=

    
Dependencies
------------

``ncvue`` uses the package :mod:`numpy`. It is available in PyPI
and ``pip`` should install it automatically. Installations via
`setup.py` might need to install the dependency first.
