.PHONY: testmod testdatafile testall

VERBOSITY = -v
UNITTEST = python -m unittest $(VERBOSITY)

testall: testmod testdatafile testmodframework testcvfig

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
	
