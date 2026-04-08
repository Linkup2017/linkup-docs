SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = docs
BUILDDIR      = docs/_build

help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# -- i18n targets -------------------------------------------------------------
gettext:
	@$(SPHINXBUILD) -b gettext "$(SOURCEDIR)" "$(BUILDDIR)/gettext"

intl-update: gettext
	sphinx-intl update -p "$(BUILDDIR)/gettext" -d "$(SOURCEDIR)/locale" -l ko

html-ko:
	@$(SPHINXBUILD) -b html -D language=ko "$(SOURCEDIR)" "$(BUILDDIR)/html-ko" $(SPHINXOPTS)

html-all: html html-ko

# 로컬 개발용: .po 갱신 후 한국어 빌드
dev-ko: intl-update html-ko

.PHONY: help gettext intl-update html-ko html-all dev-ko livehtml Makefile

%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

livehtml:
	sphinx-autobuild "$(SOURCEDIR)" "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)
