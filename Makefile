PKG_NAMESPACE = yhttp.core
PKG_NAME = yhttp
PYDEPS_COMMON += \
	'coveralls' \
	'bddrest >= 4, < 5' \
	'bddcli >= 2.5.1, < 3' \
	'yhttp-dev >= 3.1.2'


include make/common.mk
include make/venv.mk
include make/install.mk
include make/lint.mk
include make/test.mk
include make/sphinx.mk
include make/dist.mk
include make/pypi.mk
