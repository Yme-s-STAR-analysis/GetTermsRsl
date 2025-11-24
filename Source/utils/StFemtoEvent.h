/*
	My StFemtoEvent v3.0
	30.01.2024 by yghuang
	(now is the same version with AceTree)
*/

#ifndef StFemtoEvent_h
#define StFemtoEvent_h

// C++ headers
#include <vector>
#include <iostream>

// ROOT headers
#include "TObject.h"
#include "TClonesArray.h"
#include "StFemtoTrack.h"
#include "TVector3.h"


class StFemtoTrack;

//_________________
class StFemtoEvent : public TObject {

	public:
  		StFemtoEvent();
  		StFemtoEvent(const StFemtoEvent &event);
  		virtual ~StFemtoEvent(){}
  		void ClearEvent();

		// Getters
        Int_t GetRegion()           {       return mRegion;             }
		Int_t GetRefMult3()			{		return mRefMult3;			}
		Int_t GetRefMult3X()		{		return mRefMult3X;			}
		Float_t GetVz()				{		return (Float_t) mVz;		}

		// Setters

		void SetRefMult3(Int_t val) {		mRefMult3 = val;			}
		void SetRefMult3X(Int_t val){		mRefMult3X= val;			}
		void SetVz(Float_t val)   	{ 		mVz  = val;					}
        void SetRegion(Int_t val)   {       mRegion = val;              }        
		
		Int_t GetEntries()			{	return mFemtoTrackArray.size();	}
		
		StFemtoTrack GetFemtoTrack(int i)	{	return (StFemtoTrack) mFemtoTrackArray[i];}
		void SetStFemtoTrackArray(std::vector< StFemtoTrack > val){mFemtoTrackArray = val;}


	private:

		Int_t   mRefMult3;
		Int_t   mRefMult3X;
		Float_t mVz;
        Int_t   mRegion;
		std::vector< StFemtoTrack>  mFemtoTrackArray;

	ClassDef(StFemtoEvent,1)

};

#endif
