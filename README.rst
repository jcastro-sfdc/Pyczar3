Pyczar3
=======
.. image:: https://codecov.moe.prd-sam.prd.slb.sfdc.net/ghe/Mobile/pyczar3/branch/master/graph/badge.svg
  :target: https://codecov.moe.prd-sam.prd.slb.sfdc.net/ghe/Mobile/pyczar3

.. image:: https://sonarqube.eng.sfdc.net/api/project_badges/measure?project=python%3Apyczar3&metric=alert_status
    :target: https://sonarqube.eng.sfdc.net/dashboard?id=python%3Apyczar3

A Python 3.5+ fork of Pyczar that only supports certificate-based access. No more keypairs.


Building this
-------------

::

    python setup.py test build bdist_wheel

Your wheel is in ``dist/pyczar3-{{version}}-py2.py3-none-any.whl``


Testing this
------------

::

    tox


Development
-----------

This project uses pre-commit_ project to run checks before you commit any code. Please use it!

::

    brew install pre-commit
    precommit install

Configuration is in ``.pre-commit-config.yaml``

.. _pre-commit: https://pre-commit.com
