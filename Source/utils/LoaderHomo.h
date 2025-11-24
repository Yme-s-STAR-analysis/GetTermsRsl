#ifndef __RSL_LOADER__
#define __RSL_LOADER__

class TProfile;
class TH1D;
class TFile;

//	CumLoader saves terms for cumulants calculation only.
//	Loader also saves terms for stat. error calculation.

class Loader {

  	public:
		Loader(const char*, TFile*, int);
		~Loader();
		void ReadTrack(float, float);
		void Store(int);
		// void Save(const char*);
		// void Update(const char*);

  	private:
		int _nMultBin;
		const char* ParticleType;
		int LowEventCut;
		Double_t _q[4][4];
		// static const Int_t _nTerms = 2535;
		static const Int_t _nTerms = 55; // 
		TProfile* _V[_nTerms+1]; // -> _nTerms + 1
		const Char_t* Terms[_nTerms]={"q01_01q03_03", "q01_01q02_02q03_01", "q01_01_3q03_03", "q02_01q03_01", "q01_01_4q02_01", "q01_01_3", "q01_01_6", "q01_01q02_01_2", "q01_01_2q03_01", "q02_01", "q02_02q03_02", "q01_01_3q02_02", "q03_01", "q01_01_2q02_01_2", "q03_03", "q03_01q03_02", "q02_01q03_03", "q01_01_2q03_02", "q01_01_3q03_01", "q01_01q02_02q03_02", "q01_01q02_01", "q02_01q03_02", "q01_01_4", "q01_01q02_01q03_02", "q03_01_2", "q01_01_2q02_02", "q01_01_5", "q01_01q02_02_2", "q03_01q03_03", "q01_01q03_02", "q01_01q03_01", "q02_01q02_02", "q01_01_4q02_02", "q03_03_2", "q02_01_2", "q01_01q02_01q02_02", "q03_02", "q01_01q02_02q03_03", "q01_01", "q01_01_3q02_01", "q01_01q02_02", "q02_02q03_01", "q01_01q02_01q03_03", "q01_01_2q02_01q02_02", "q02_02_2", "q01_01_3q03_02", "q03_02q03_03", "q01_01_2q02_02_2", "q02_02q03_03", "q01_01_2q03_03", "q02_02", "q03_02_2", "q01_01_2", "q01_01_2q02_01", "q01_01q02_01q03_01"};
};

#endif
