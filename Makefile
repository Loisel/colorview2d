VERBOSITY = -v
UNITTEST = python -m unittest $(VERBOSITY)


testall: testmods testdatafile testmodframework testcvfig testdeploy-local
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
	./docker-test-local.sh
testdeploy-pip:
	./docker-test-pip.sh
