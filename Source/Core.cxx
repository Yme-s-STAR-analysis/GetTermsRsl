#include <iostream>
#include <utility>
#include <numeric>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <string>
#include <cmath>

#include "TFile.h"
#include "TH2D.h"
#include "TChain.h"
#include "TRandom3.h"
#include "TF1.h"
#include "TString.h"
#include "TObjArray.h"
#include "TObjString.h"

#include "utils/StFemtoTrack.h"
#include "utils/StFemtoEvent.h"
#include "utils/QualityController.h"
#include "utils/CentDefinition.h"
#include "utils/EffMaker.h"
#include "utils/LoaderHomo.h"


int main(int argc, char** argv){
	/*
		Arguments: 5
		[1]:nsigma cut tag: like 2p0
		[2]:eff factor (pro)
		[3]:eff factor (pbar)
		[4]:task tag: like default.y0p5 = default + y0p5 (system tag + scan tag)
		[5]:energy
	*/

	TChain *chain = new TChain("fDst");
	std::ifstream fileList("file.list");
	std::string filename;
	while (fileList >> filename){
		chain->Add(filename.c_str());
	}
  	long int nentries = chain->GetEntries();

    // prepare a np hist (TH2D for Np and RefMult3)
	int MaxMult = 1250;
    TH2D* hNpRef3X = new TH2D("hNprotonRefMult3X", ";RefMult3X;N_{proton}", MaxMult, -0.5, MaxMult-0.5, 100, -0.5, 99.5);
    TH2D* hNaRef3X = new TH2D("hNantiprotonRefMult3X", ";RefMult3X;N_{antiproton}", MaxMult, -0.5, MaxMult-0.5, 50, -0.5, 49.5);
    TH2D* hNnRef3X = new TH2D("hNnetprotonRefMult3X", ";RefMult3X;N_{net-proton}", MaxMult, -0.5, MaxMult-0.5, 80, -10.5, 69.5);
  	std::cout << "[LOG] There will be " << nentries << " events.\n";

	const char* task_tag = argv[4];
	TString full_tag(task_tag);
	TString system_tag, scan_tag;
	TObjArray* tokens = full_tag.Tokenize(".");
	if (tokens->GetEntries() == 2) {
		system_tag = ((TObjString*)tokens->At(0))->GetString();
		scan_tag = ((TObjString*)tokens->At(1))->GetString();
	} else {
		std::cout << "[ERROR] - From Core: Cannot regcognize the task tag " << task_tag << ". Now quit!\n";
		return -1;
	}
	delete tokens;
	std::cout << "[LOG] - From Core: System Tag is " << system_tag << ".\n";
	std::cout << "[LOG] - From Core: Scan Tag is " << scan_tag << ".\n";
	
	std::string energy = argv[5];
	if (
		energy != "7.7" && energy != "9.2" && energy != "11.5" &&
		energy != "14.6" && energy != "17.3" && energy != "19.6" && energy != "27"
	) {
		std::cout << "[ERROR] - From Core: Invalid energy " << energy << ". Now quit!\n";
		return -1;
	}

	std::ifstream* fin = new std::ifstream();
	fin->open(Form("%s.getTerms.cfg", task_tag));
	QualityController* qc = new QualityController();
	qc->readConfig(fin);

	CentDefinition* centDef3X = new CentDefinition();
	std::cout << "[LOG] - From Core: Initializing centrality tool for RefMult3X" << std::endl;
	centDef3X->Init("cent_edgeX.txt");

	// efficiency items here (for uncorrected case, just ignore them is okey)
	EffMaker* effMaker = new EffMaker();
	bool effSuccess = effMaker->Init(energy, system_tag.Data(), argv[1]);
	if (!effSuccess) {
		std::cout << "[ERROR] - From Core: Fail to initialize the efficiency maker. Now quit!\n";
		return -1;
	}
    double eff_factor_pro = std::atof(argv[2]);
    double eff_factor_pbar = std::atof(argv[3]);
	std::cout << "[LOG] - From Core: Efficiency Factor (proton): " << eff_factor_pro << std::endl;
	std::cout << "[LOG] - From Core: Efficiency Factor (antiproton): " << eff_factor_pbar << std::endl;

	StFemtoEvent *event = new StFemtoEvent();
	chain->SetBranchAddress("StFemtoEvent", &event);

	TFile* terms3X = new TFile(Form("%sX.root", task_tag), "recreate");
	Loader* lder_nX = new Loader("Netp", terms3X, MaxMult);
	Loader* lder_pX = new Loader("Pro", terms3X, MaxMult);
	Loader* lder_aX = new Loader("Pbar", terms3X, MaxMult);

	int progress = 0;	
  	for (int iEntry = 0; iEntry < nentries; iEntry++){
		// if (iEntry != 0 && iEntry % 100000 == 0){
		if (iEntry * 100.0 / progress > nentries) {
			std::cout << "[LOG]: Progress: " << iEntry << " / " << nentries << " events finished!\n";
			progress += 5; // show progress per 5% events done
		}

		chain->GetEntry(iEntry);

		// Make Event Cuts
		double vz = event->GetVz();
		int region = 0;
		if (energy == "9.2") { region = event->GetRegion(); }
		effMaker->SetRegion(region);

		double refMult3X = event->GetRefMult3X();
		int centBinX = centDef3X->GetCentrality(refMult3X);
		if (refMult3X > MaxMult) { continue; }
		if (centBinX < 0) { continue; }

		if (qc->isBadEvent(vz)) { continue; }

		// track loop
        Int_t np = 0;
        Int_t na = 0;
		for (int iTrack = 0; iTrack < event->GetEntries(); iTrack++){

			StFemtoTrack trk = event->GetFemtoTrack(iTrack);
			
			double pt = trk.GetPt(); 
			bool positive = pt > 0; // true if positive pt
			pt = fabs(pt);
			double pcm = trk.GetP();
			double YP = trk.GetY();
			short nHitsFit = trk.GetNHitsFit();
			double dca = trk.GetDca();
			double nSig = trk.GetNSigmaProton();
			double mass2 = trk.GetMass2();
			double fYP = fabs(YP);

			// Here is the PID selection: use TOF or not
			bool needTOF = false;
			bool asCut = false; // by default, apply symmetric PID cut

			// set different PID strategy for various energies
			if (energy == "7.7") {
				if (positive) {
					if (fYP < 0.6 && pt > 0.8) { needTOF = true; }
					if (fYP >= 0.5 && fYP < 0.6 && pt > 0.7 && pt <= 0.8) { asCut = true; }
				} else {
					if (fYP < 0.4 && pt > 0.7) { needTOF = true; }
					if (fYP >= 0.4 && fYP < 0.6 && pt <= 0.8) { asCut = true; }
					if (fYP >= 0.4 && fYP < 0.6 && pt > 0.8) { needTOF = true; }
				}
			} else if (energy == "9.2") {
				if (fYP < 0.5 && pt > 0.8) { needTOF = true; }
				if (fYP >= 0.5 && fYP < 0.6) {
					if (pt > 0.8) { asCut = true; }
					if (pt > 0.9) { needTOF = true; }
				} 
			} else if (energy == "11.5") {
				if (fYP < 0.5 && pt > 0.8) { needTOF = true; }
				if (fYP >= 0.5 && fYP < 0.6) {
					if (positive) {
						if (pt > 0.9) { asCut = true; }
						if (pt > 1.1) { needTOF = true; }
					} else {
						if (pt > 0.7) { asCut = true; }
						if (pt > 0.9) { needTOF = true; }
					}
				}
			} else if (energy == "14.6") {
				if (fYP < 0.5 && pt > 0.8) { needTOF = true; }
				if (fYP >= 0.5 && fYP < 0.6) {
					if (pt > 0.8) { asCut = true; }
					if (pt > 1.0) { needTOF = true; }
				} 
			} else if (energy == "17.3") {
				if (fYP < 0.5 && pt > 0.8) { needTOF = true; }
				if (fYP >= 0.5 && fYP < 0.6) {
					if (pt > 0.8) { asCut = true; }
					if (pt > 1.0) { needTOF = true; }
				} 
			} else if (energy == "19.6") {
				if (fYP < 0.5 && pt > 0.8) { needTOF = true; }
				if (fYP >= 0.5 && fYP < 0.6) {
					if (positive) {
						if (pt > 0.9) { asCut = true; }
						if (pt > 1.1) { needTOF = true; }
					} else {
						if (pt > 0.7) { asCut = true; }
						if (pt > 1.0) { needTOF = true; }
					}
				}
			} else if (energy == "27") {
				if (fYP < 0.5 && pt > 0.8) { needTOF = true; }
			}

			// Make track Cut
			// nHitsRatio quantity is already cut when generating the tree
			// add asymmetric cut
			if (qc->isBadTrack(pt, YP, nHitsFit, nSig, dca, needTOF, mass2, asCut)) {
				continue;
			} 

			np += positive;
			na += !positive;

			// detector efficiency

			// for corrected case:
			double pid_eff = effMaker->GetPidEff(positive, pt, YP, asCut && !needTOF);

			double eff_factor = positive ? eff_factor_pro : eff_factor_pbar;

			double effX = 1.0;
			double tpc_effX = effMaker->GetTpcEff(positive, pt, YP, centBinX, vz);
			double tof_effX = effMaker->GetTofEff(positive, pt, YP, centBinX, vz);

			effX = tpc_effX * pid_eff;
			if (needTOF) { effX *= tof_effX; }
			effX *= eff_factor;
            effX = effX > 1.0 ? 1.0 : effX;

			if (positive) {
				lder_pX->ReadTrack(1.0, effX);
				lder_nX->ReadTrack(1.0, effX);
			} else {
				lder_aX->ReadTrack(1.0, effX);
				lder_nX->ReadTrack(-1.0, effX);
			}

		} // track loop ends

		lder_pX->Store(refMult3X);
		lder_aX->Store(refMult3X);
		lder_nX->Store(refMult3X);
        hNpRef3X->Fill(refMult3X, np);
        hNaRef3X->Fill(refMult3X, na);
        hNnRef3X->Fill(refMult3X, np - na);
  	} // event loop ends

	terms3X->cd();
	terms3X->Write();
	terms3X->Close();

    TFile* p_dist_file = new TFile(Form("%s.pDist.root", task_tag), "recreate");
    p_dist_file->cd();

    hNpRef3X->Write();
    hNaRef3X->Write();
    hNnRef3X->Write();
    p_dist_file->Close();

	std::cout << "[LOG] - From Core: This is the end of getTerms." << std::endl;

  	return 0;
}
