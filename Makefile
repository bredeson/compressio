
PREFIX     ?= /usr/local

PACKAGE    := compression
LICENSE    := LICENSE
SRC_DIR    := src
BUILD_DIR  := build
TEST_DIR   := test
LIB_DIR    := $(BUILD_DIR)/lib
CURR_DIR   := $(shell pwd)

ECHO       := echo
INSTALL    := $(filter /%,$(shell /bin/sh -c 'type install'))
MKDIR      := $(filter /%,$(shell /bin/sh -c 'type mkdir'))
AWK        := $(filter /%,$(shell /bin/sh -c 'type awk'))
CAT        := $(filter /%,$(shell /bin/sh -c 'type cat'))
RM         := $(filter /%,$(shell /bin/sh -c 'type rm'))
RM_R        = $(RM) -r
INSTALL_REG = $(INSTALL) -p -m 644 -D
MKDIR_P     = $(MKDIR) -p

ifneq ($(shell which python3),)
PYTHON     := $(shell which python3)
else ifneq ($(shell which python),)
PYTHON     := $(shell which python)
else
$(error "Python interpreter not found. Please install Python and ensure it is accessible via PATH.")
endif


PYTHON_VERSION := $(shell $(PYTHON) --version 2>&1 | $(AWK) '{if (/Python/) {split($$2,v,".");print "python"v[1]"."v[2]}}')
INSTALL_PATH ?= $(PREFIX)/lib/$(PYTHON_VERSION)/site-packages

BUILD_TARGETS = $(BGZ_BUILD_TARGETS) $(COMPRESSION_BUILD_TARGETS)

BGZ_SOURCE_FILES = $(SRC_DIR)/bgzip.py
BGZ_BUILD_TARGETS = $(patsubst $(SRC_DIR)/%,$(LIB_DIR)/%,$(BGZ_SOURCE_FILES))
BGZ_INSTALL_TARGETS = $(patsubst $(SRC_DIR)/%,$(INSTALL_PATH)/%,$(BGZ_SOURCE_FILES))

COMPRESSION_SOURCE_FILES = $(wildcard $(SRC_DIR)/$(PACKAGE)/*.py)
COMPRESSION_BUILD_TARGETS = $(patsubst $(SRC_DIR)/%,$(LIB_DIR)/%,$(COMPRESSION_SOURCE_FILES))
COMPRESSION_INSTALL_TARGETS = $(patsubst $(SRC_DIR)/%,$(INSTALL_PATH)/%,$(COMPRESSION_SOURCE_FILES))


.SUFFIXES:
.SUFFIXES: .py

.PHONY: install activate test clean

all: build



build: $(LIB_DIR) build-bgzip build-compression

build-bgzip: $(BGZ_BUILD_TARGETS)

build-compression: $(COMPRESSION_BUILD_TARGETS)

$(LIB_DIR):
	@$(MKDIR_P) $@

$(LIB_DIR)/%: $(SRC_DIR)/%
	@$(MKDIR_P) $(@D)
	@$(AWK) '{print "#",$$0}' $(LICENSE) | $(CAT) - $< >$@



test: $(COMPRESSION_BUILD_TARGETS)
	PYTHONPATH="$(CURR_DIR)/$(LIB_DIR)" $(PYTHON) -m unittest discover -v $(TEST_DIR)



activate:
	@$(ECHO) 'export PYTHONPATH="$(INSTALL_PATH)$${PYTHONPATH:+:$${PYTHONPATH}}";' >activate
	@$(ECHO) '#setenv PYTHONPATH "$(INSTALL_PATH):$$PYTHONPATH";' >>activate



install: build test install-bgzip install-compression

install-bgzip: $(BGZ_INSTALL_TARGETS)

install-compression: $(COMPRESSION_INSTALL_TARGETS)

$(INSTALL_PATH)/%.py: $(LIB_DIR)/%.py
	$(INSTALL_REG) $< $@

$(INSTALL_PATH)/$(PACKAGE)/%.py: $(LIB_DIR)/$(PACKAGE)/%.py
	$(INSTALL_REG) $< $@



clean:
	-$(RM_R) $(BUILD_DIR)
