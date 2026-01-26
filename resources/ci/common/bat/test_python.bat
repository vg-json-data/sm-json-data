@echo off
python ./resources/ci/common/keywords.py
python scripts/update_schema.py
python -m tests.asserts.validate
python -m tests.asserts.keywords
