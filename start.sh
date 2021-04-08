#!/bin/bash
pipenv run jupyter lab --ip 0.0.0.0 --no-browser --ServerApp.token='' --ServerApp.password='' --notebook-dir=notebooks
