#include "StFemtoEvent.h"
#include "StFemtoTrack.h"


ClassImp(StFemtoEvent)

//____________________________________________________________
StFemtoEvent::StFemtoEvent(): TObject(),
	mRefMult3(-999), mRefMult3X(-999), mVz(-999), mRegion(0) {
}

//____________________________________________________________
StFemtoEvent::StFemtoEvent(const StFemtoEvent &event): TObject() {

  mRefMult3 = event.mRefMult3;
  mRefMult3X = event.mRefMult3X;
  mRegion = event.mRegion;
  mVz = event.mVz;
  mFemtoTrackArray = event.mFemtoTrackArray;

}

//____________________________________________________________
void StFemtoEvent::ClearEvent() {
	mRefMult3 = -999;
	mRefMult3X = -999;
  mRegion = 0;
	mVz = -999;

	mFemtoTrackArray.clear();
}