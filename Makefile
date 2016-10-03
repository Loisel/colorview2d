VERBOSITY = -v
PYTHON_VERSION = 2.7
UNITTEST = python$(PYTHON_VERSION) -m unittest $(VERBOSITY)


testall: testmods testdatafile testmodframework testcvfig
testpip: testmods testdatafile testcvfig
testlocal: testmods testdatafile testmodframework testcvfig

testmods:
	$(eval MODULE = $(UNITTEST) test.mods_test)
	$(MODULE).ModTest

testmodframework:
	$(eval MODULE = $(UNITTEST) test.mods_test)
	$(MODULE).ModFrameworkTest

testdatafile:
	$(eval MODULE = $(UNITTEST) test.datafile_test)
	$(MODULE).DatafileTest
	$(MODULE).FileloaderTest

testcvfig:
	$(eval MODULE = $(UNITTEST) test.cvfig_test)
	$(MODULE).PltFigTest

testdeploy-local:
	./test/docker-test-local.sh
testdeploy-pip:
	./test/docker-test-pip.sh
