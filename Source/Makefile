all: compile

mdict:
	rootcint dict.cxx utils/StFemtoEvent.h utils/StFemtoTrack.h

compile: clean mdict
	g++ -o getTerms -std=c++11 dict.cxx utils/LoaderHomo.cxx utils/QualityController.cxx utils/StFemtoEvent.cxx utils/StFemtoTrack.cxx utils/EffMaker.cxx utils/CentDefinition.cxx Core.cxx `root-config --libs --cflags`

clean:
	touch getTerms
	touch dictTmp
	rm dict* 
	rm getTerms
