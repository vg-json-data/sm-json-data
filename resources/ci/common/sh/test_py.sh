py ./resources/ci/common/keywords.py
py scripts/update_schema.py
py -m tests.asserts.validate
py -m tests.asserts.keywords
