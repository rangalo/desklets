#--------------------------------------------------------------
# Written by S.Fourmanoit <syfou@users.sourceforge.net>, 
# 	2004, 2005.
#
# This is a minimal makefile to facilitate packaging operation
# of adesklets's python desklets, following a syntax similar 
# to automake's
# 
# Some possible invocations would be:
#
# make [dist-bzip2]       - create an updated bzip'ed tarball
# make dist-bzip2-sign    - also create an open PGP signature
# make clean              - just clean up current directory
# 
# You can also set the VER environment variable to 
# any string if you wish to bypass package naming 
# auto-incrementation scheme. For instance:
#
# make VER=0.666.0 
# 
# will force creation of $(PACKAGE)-0.666.0.tar.bz2 
#
# Portability warning:
#
# This was not meant to be portable, but to work on a GNU
# system (GNU sed, GNU make, bc, portable bourne shell, 
# GNU findutils, GNU coreutils). It also need base directory 
# to be named in a standard 'NAME-MAJOR.MINOR.REVISION' 
# fashion.
#
#--------------------------------------------------------------
GPG-LOCAL-USER=syfou	   # User for GnuPG signing the package

#--------------------------------------------------------------
# Do not edit anything below this point, unless you know 
# what you are doing.
#
#--------------------------------------------------------------
PACKAGE=$(shell basename `pwd` | sed 's/^\(.*\)-.*/\1/')
REV=$(shell basename `pwd` | \
	sed 's/.*-\(.*\)$$/\1/;s/.*\.\([0-9]\+\)$$/\1 + 1/' | \
	bc)
MAJ-MIN=$(shell basename `pwd` | \
	sed 's/.*-\(.*\)$$/\1/;s/^\(.*\.\)[0-9]\+/\1/')
VERSION=$(if $(VER),$(VER),$(MAJ-MIN)$(REV))
PWD=$(shell pwd)

#--------------------------------------------------------------
%.tar.bz2.asc: %.tar.bz2
	gpg --local-user $(GPG-LOCAL-USER) \
		--armor --detach-sign $<

$(PACKAGE)-$(VERSION).tar.bz2: $(wildcard *.py) README clean
	-mkdir /tmp/$(PACKAGE)-$(VERSION)
	cp -r . /tmp/$(PACKAGE)-$(VERSION)
	tar --exclude='config.txt' -C /tmp -cvjf \
		$(PWD)/$(PACKAGE)-$(VERSION).tar.bz2 \
		$(PACKAGE)-$(VERSION)
	-rm -rf /tmp/$(PACKAGE)-$(VERSION)

#--------------------------------------------------------------
.INTERMEDIATE: clean
.PHONY: clean dist-bzip2 dist-bzip2-sign
clean:
	-rm `find . -name '*~' -or -name '*.pyc' \
		-or -name '*.bz2' -or -name '*.asc'`
	-rm -rf `find . -mindepth 1 -maxdepth 1 \
		-type d -name '$(PACKAGE)-*'`
dist-bzip2: $(PACKAGE)-$(VERSION).tar.bz2
dist-bzip2-sign: $(PACKAGE)-$(VERSION).tar.bz2.asc

#--------------------------------------------------------------