
PREFIX     ?= /usr/local
INSTALL_PATH ?= $(PREFIX)/lib/$(PYTHON_VERSION)/site-packages

CURR_PATH   := $(shell pwd)

PACKAGE    := compressio
LICENSE    := LICENSE
SRC_PATH   := $(CURR_PATH)/src
BUILD_PATH := $(CURR_PATH)/build
TEST_PATH  := $(CURR_PATH)/test
LIB_PATH   := $(BUILD_PATH)/lib

ECHO       := $(shell which echo 2>/dev/null)
INSTALL    := $(shell which install 2>/dev/null)
MKDIR      := $(shell which mkdir 2>/dev/null)
AWK        := $(shell which awk 2>/dev/null)
CAT        := $(shell which cat 2>/dev/null)
CP         := $(shell which cp 2>/dev/null)
CP_R        = $(CP) -R
RM         := $(shell which rm 2>/dev/null)
RM_R        = $(RM) -R
INSTALL_REG = $(INSTALL) -p -m 644
INSTALL_DIR = $(INSTALL) -p -m 755 -d
MKDIR_P     = $(MKDIR) -p

ifeq ($(shell uname),Linux)
INSTALL_REG += -D
else
INSTALL_REG = $(CP_R) 
endif

ifneq ($(shell which python3),)
PYTHON     := $(shell which python3)
else ifneq ($(shell which python),)
PYTHON     := $(shell which python)
else
$(error "Python interpreter not found. Please install Python and ensure it is accessible via PATH.")
endif

PYTHON_VERSION := $(shell $(PYTHON) --version 2>&1 | $(AWK) '{if (/Python/) {split($$2,v,".");print "python"v[1]"."v[2]}}')



BUILD_TARGETS = $(BGZ_BUILD_TARGETS) $(COMPRESSIO_BUILD_TARGETS)

BGZ_SOURCE_FILES = $(SRC_PATH)/bgzip.py
BGZ_BUILD_PATH = $(LIB_PATH)
BGZ_BUILD_TARGETS = $(patsubst $(SRC_PATH)/%,$(LIB_PATH)/%,$(BGZ_SOURCE_FILES))
BGZ_INSTALL_PATH = $(INSTALL_PATH)
BGZ_INSTALL_TARGETS = $(patsubst $(SRC_PATH)/%,$(INSTALL_PATH)/%,$(BGZ_SOURCE_FILES))

COMPRESSIO_SOURCE_FILES = $(wildcard $(SRC_PATH)/$(PACKAGE)/*.py)
COMPRESSIO_BUILD_PATH = $(LIB_PATH)/$(PACKAGE)
COMPRESSIO_BUILD_TARGETS = $(patsubst $(SRC_PATH)/%,$(LIB_PATH)/%,$(COMPRESSIO_SOURCE_FILES))
COMPRESSIO_INSTALL_PATH = $(INSTALL_PATH)/$(PACKAGE)
COMPRESSIO_INSTALL_TARGETS = $(patsubst $(SRC_PATH)/%,$(INSTALL_PATH)/%,$(COMPRESSIO_SOURCE_FILES))



.SUFFIXES:
.SUFFIXES: .py

.PHONY: install activate test clean

all: build



build: build-bgzip build-compressio

build-bgzip: $(LIB_PATH) $(BGZ_BUILD_TARGETS)

build-compressio: $(LIB_PATH) $(COMPRESSIO_BUILD_TARGETS)

$(LIB_PATH):
	@$(MKDIR_P) $@

$(LIB_PATH)/%: $(SRC_PATH)/%
	@$(MKDIR_P) $(@D)
	@$(AWK) '{print "#",$$0}' $(LICENSE) | $(CAT) - $< >$@

$(COMPRESSIO_INSTALL_PATH):
	$(INSTALL_DIR) $@

$(BGZ_INSTALL_PATH):
	$(INSTALL_DIR) $@



test: $(COMPRESSIO_BUILD_TARGETS) $(BGZ_BUILD_TARGETS)
	PYTHONPATH="$(LIB_PATH)" $(PYTHON) -m unittest discover -v $(TEST_PATH)



activate:
	@$(ECHO) 'export PYTHONPATH="$(INSTALL_PATH)$${PYTHONPATH:+:$${PYTHONPATH}}";' >activate
	@$(ECHO) '#setenv PYTHONPATH "$(INSTALL_PATH):$$PYTHONPATH";' >>activate



install: build test install-bgzip install-compressio

install-bgzip: $(BGZ_INSTALL_PATH) $(BGZ_INSTALL_TARGETS)

install-compressio: $(COMPRESSIO_INSTALL_PATH) $(COMPRESSIO_INSTALL_TARGETS)

$(BGZ_INSTALL_PATH)/%.py: $(LIB_PATH)/%.py
	$(INSTALL_REG) $< $@

$(COMPRESSIO_INSTALL_PATH)/%.py: $(LIB_PATH)/$(PACKAGE)/%.py
	$(INSTALL_REG) $< $@



clean:
	-$(RM_R) $(BUILD_PATH)
