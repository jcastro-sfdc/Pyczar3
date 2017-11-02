from setuptools import setup, find_packages

version = '0.9.2'

setup(name='pyczar3',
      version=version,
      description="Package for pyczar3 client code",
      long_description="Package for pyczar client code",
      classifiers=['Development Status :: 3 - Alpha',
                   'License :: Other/Proprietary License',
                   'Programming Language :: Python :: 3 :: Only'],
      # keywords='',
      author='Jason Schroeder',
      author_email='jschroeder@salesforce.com',
      url='https://git.soma.salesforce.com/Mobile/Pyczar3',
      license='SFDC',
      packages=find_packages(),
      install_requires=['requests'],
      # setup_requires=['pytest-runner'],
      package_data={'pyczar3': ['certs/ca_bundle.crt']},
      tests_require=['pytest', 'responses', 'coverage'],
      scripts=[],
      entry_points={
            'console_scripts': [
                  'pyczar3 = pyczar3.cli:main'
            ]
      }
)
