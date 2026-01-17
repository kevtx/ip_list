set dotenv-load

import '/Users/keo/.config/just/python.justfile'
import '/Users/keo/.config/just/conda.justfile'

PROJECT_ROOT := clean(justfile_directory())

APP_NAME := "python-iplist"
PYTHON_VERSION := "3.8"

default:
    just --choose


[group('project')]
init:
    git config --local core.hooksPath .githooks


[unix]
[no-exit-message]
[group('project')]
format:
    bash -c .githooks/pre-commit --format


[windows]
[group('project')]
format:
    echo "Not implemented. Please execute '.githooks/pre-commit' manually."

alias fmt := format


[group('project')]
test:
	python -m unittest discover tests