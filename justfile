set quiet
set allow-duplicate-variables

import? '~/.config/just/base.justfile'
import? '~/.config/just/python.justfile'
import? '~/.config/just/conda.justfile'

APP_NAME := "python-iplist"
PYTHON_VERSION := "3.8"
PROJECT_ROOT := clean(justfile_directory())


#[group('project')]
#init:
#    git config --local core.hooksPath .githooks


[unix]
[no-exit-message]
[group('project')]
format:
    bash .githooks/pre-commit --format


[windows]
[group('project')]
format:
    echo "Not implemented. Please execute '.githooks/pre-commit' manually."

alias fmt := format


[group('project')]
test:
	python -m unittest discover tests