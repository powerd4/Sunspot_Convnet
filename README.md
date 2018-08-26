# README #

A convolutional neural network that classifies sunspot images. 

### What is this project for? ###

*  Final Year Project, Physics and Astrophysics, Trinity College Dublin.
*  Downloads sunspot image database from SDO database (.fits files), and their labels from NOAA database, matches them up by date and heliographic coordinates, inputs into convolutional neural network in TensorFlow Keras with module Hyperas for hyperparameter optimisation. 

### How do I get set up? ###

* Create a new environment (conda, virtualenv, pyenv).
* pip install -r requirements.txt .
* Run the tests `pytest`.

### How do I run the code? ###

* For flexibility and clarity, we chose to have the files run sequentially. The files in source_code are numbered sequentially, the order in which they must be run. 
* Open the newly created environment.
* navigate to source_code and run files in sequence.

### Contribution guidelines ###

* Copy the hooks/pre-commit file to you local .git/hooks/ `cp hooks/pre-commit .git/hooks`.
* This will run the relevant style checks and runt tests before you can commit.