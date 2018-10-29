Pyczar3
=======
.. image:: https://codecov.moe.prd-sam.prd.slb.sfdc.net/ghe/Mobile/pyczar3/branch/master/graph/badge.svg
  :target: https://codecov.moe.prd-sam.prd.slb.sfdc.net/ghe/Mobile/pyczar3

A Python 3.5+ fork of Pyczar that only supports certificate-based access. No more keypairs.


Building this
-------------

    python setup.py test build bdist_wheel

your wheel is in ``dist/pyczar3-{{version}}-py2.py3-none-any.whl``


Testing this
------------

    tox
