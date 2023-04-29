@echo off
py ./resources/ci/common/keywords.py
py -m tests.asserts.validate
py -m tests.asserts.keywords
