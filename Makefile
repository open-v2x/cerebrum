SOURCES := src
TOOLS := tools
DIST := book
ROOT_DIR ?= $(shell git rev-parse --show-toplevel)

DPRINT_VERSION := 0.15.0
MDBOOK_VERSION := 0.4.10
UNAMESTR := $(shell uname)

ifeq ($(UNAMESTR),Darwin)
DPRINT=$(TOOLS)/dprint-$(DPRINT_VERSION)-darwin
MDBOOK=$(TOOLS)/mdbook-$(MDBOOK_VERSION)-darwin
else
DPRINT=$(TOOLS)/dprint-$(DPRINT_VERSION)
MDBOOK=$(TOOLS)/mdbook-$(MDBOOK_VERSION)
endif

.PHONY: help
help:
	@echo "V2X documents development makefile"
	@echo
	@echo "Usage: make <TARGET>"
	@echo
	@echo "Target:"
	@echo "  build               Render book from markdown."
	@echo "  server              Preview the book by server via HTTP."
	@echo "  fmt                 Format markdown style."
	@echo "  lint                Check markdown style."
	@echo "  clean               Delete generated book and clear cache."
	@echo


.PHONY: build
build:
	$(MDBOOK) build -d $(DIST)


.PHONY: server
server:
	$(MDBOOK) serve -d $(DIST) -p 3000 -n 0.0.0.0


.PHONY: fmt
fmt:
	$(DPRINT) fmt


.PHONY: lint
lint:
	$(DPRINT) check


.PHONY: clean
clean:
	$(MDBOOK) clean
	$(DPRINT) clear-cache
