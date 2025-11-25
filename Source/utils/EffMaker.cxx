#include "EffMaker.h"
#include "TH1D.h"
#include "TH2F.h"
#include "TFile.h"
#include "TF1.h"
#include "TString.h"
#include <iostream>
#include <cstring>
#include <string>

bool EffMaker::Init(std::string energy, const char* sysTagRaw, const char* nSigTag) {
    this->energy = energy;
    // if sysTag is a member of this vector, it will be used in efficiency file,
    // otherwise, we use "default"
    std::string sysTag = "default";

    if (strncmp(sysTagRaw, "dca", 3) == 0 || strncmp(sysTagRaw, "nhit", 4) == 0) {
        sysTag = sysTagRaw;
    }
    if (energy == "7.7") {
        ReadInEffFile(
            Form("/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/7/TpcEff.%s.root", sysTag.c_str()),
            Form("/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/7/TofEff.%s.root", sysTag.c_str()),
            "/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/7/PidEff.root",
            nSigTag
        );
    } else if (energy == "9.2") {
        std::cout << "[LOG] - From EffMaker Module: Initialize EffMaker with energy " << energy << "." << std::endl;
        ReadInEffFile(
            Form("/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/9/TpcEff.%s.root", sysTag.c_str()),
            Form("/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/9/TofEff.%s.root", sysTag.c_str()),
            "/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/9/PidEff.root",
            nSigTag
        );
    } else if (energy == "11.5") {
        std::cout << "[LOG] - From EffMaker Module: Initialize EffMaker with energy " << energy << "." << std::endl;
        ReadInEffFile(
            Form("/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/11/TpcEff.%s.root", sysTag.c_str()),
            Form("/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/11/TofEff.%s.root", sysTag.c_str()),
            "/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/11/PidEff.root",
            nSigTag
        );
    } else if (energy == "14.6") {
        std::cout << "[LOG] - From EffMaker Module: Initialize EffMaker with energy " << energy << "." << std::endl;
        ReadInEffFile(
            Form("/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/14/TpcEff.%s.root", sysTag.c_str()),
            Form("/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/14/TofEff.%s.root", sysTag.c_str()),
            "/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/14/PidEff.root",
            nSigTag
        );
    } else if (energy == "17.3") {
        std::cout << "[LOG] - From EffMaker Module: Initialize EffMaker with energy " << energy << "." << std::endl;
        ReadInEffFile(
            Form("/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/17/TpcEff.%s.root", sysTag.c_str()),
            Form("/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/17/TofEff.%s.root", sysTag.c_str()),
            "/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/17/PidEff.root",
            nSigTag
        );
    } else if (energy == "19.6") {
        std::cout << "[LOG] - From EffMaker Module: Initialize EffMaker with energy " << energy << "." << std::endl;
        ReadInEffFile(
            Form("/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/19/TpcEff.%s.root", sysTag.c_str()),
            Form("/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/19/TofEff.%s.root", sysTag.c_str()),
            "/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/19/PidEff.root",
            nSigTag
        );
    } else if (energy == "27") {
        std::cout << "[LOG] - From EffMaker Module: Initialize EffMaker with energy " << energy << "." << std::endl;
        ReadInEffFile(
            Form("/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/27/TpcEff.%s.root", sysTag.c_str()),
            Form("/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/27/TofEff.%s.root", sysTag.c_str()),
            "/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/4EmbedList/4EffFiles/27/PidEff.root",
            nSigTag
        );
    } else {
        std::cout << "[LOG] - From EffMaker Module: Initializaion encountered with an invalid enenrgy " << energy << "." << std::endl;
        return false;
    }
    std::cout << "[LOG] - From EffMaker Module: Initialize EffMaker with energy " << energy << "." << std::endl;
    return true;
}

void EffMaker::ReadInEffFile(const char* tpc, const char* tof, const char* pid, const char* nSigTag) {
    TFile* tf_tpc = 0;
    TFile* tf_tof = 0;
    TFile* tf_pid = 0;
    if (strcmp(tpc, "none")) { // true for IS DIFFERENT
	    std::cout << "[LOG] - From EffMaker Module: TPC Efficiency root file path: " << tpc << ".\n";
        tf_tpc = TFile::Open(tpc);
        tpcOff = false;
    } else {
	    std::cout << "[LOG] - From EffMaker Module: TPC Efficiency OFF.\n";
        tpcOff = true;
    }
    if (strcmp(tof, "none")) { // true for IS DIFFERENT
	    std::cout << "[LOG] - From EffMaker Module: TOF Efficiency root file path: " << tof << ".\n";
        tf_tof = TFile::Open(tof);
        tofOff = false;
    } else {
	    std::cout << "[LOG] - From EffMaker Module: TOF Efficiency OFF.\n";
        tofOff = true;
    }
    if (strcmp(pid, "none")) { // true for IS DIFFERENT
        std::cout << "[LOG] - From EffMaker Module: PID Efficiency root file path: " << pid << " with nSigma Tag: " << nSigTag << ".\n";
        tf_pid = TFile::Open(pid);
        pidOff = false;
    } else {
	    std::cout << "[LOG] - From EffMaker Module: PID Efficiency OFF.\n";
        pidOff = true;
    }

    for (int iVz=0; iVz<nVz; iVz++) {
        for (int iCent=0; iCent<nCent; iCent++) {
            for (int iY=0; iY<nY; iY++) {
                // skip iVz >= 3 and iY >= 10 bins for 27 GeV
                if (energy == "27") { if (iVz > 2 || iY > 9) { continue; } }
                if (!tpcOff) {
                    if (energy != "9.2") {
                        tf_tpc->GetObject(
                            Form("TpcEff_cent%d_vz%d_y%d_Pro", iCent, iVz, iY),
                            ftpc_pro[iCent][iVz][iY][0]
                        );
                        tf_tpc->GetObject(
                            Form("TpcEff_cent%d_vz%d_y%d_Pbar", iCent, iVz, iY),
                            ftpc_pbar[iCent][iVz][iY][0]
                        );

                    } else { // for 9.2 GeV, we have 2 regions using different TPC tracking efficiency
                        tf_tpc->GetObject(
                            Form("TpcEff_cent%d_vz%d_y%d_Pro_0", iCent, iVz, iY),
                            ftpc_pro[iCent][iVz][iY][0]
                        );
                        tf_tpc->GetObject(
                            Form("TpcEff_cent%d_vz%d_y%d_Pbar_0", iCent, iVz, iY),
                            ftpc_pbar[iCent][iVz][iY][0]
                        );
                        tf_tpc->GetObject(
                            Form("TpcEff_cent%d_vz%d_y%d_Pro_1", iCent, iVz, iY),
                            ftpc_pro[iCent][iVz][iY][1]
                        );
                        tf_tpc->GetObject(
                            Form("TpcEff_cent%d_vz%d_y%d_Pbar_1", iCent, iVz, iY),
                            ftpc_pbar[iCent][iVz][iY][1]
                        );
                    }
                }
                if (!tofOff) {
                    if (energy == "7.7" || energy == "9.2" || energy == "11.5") {
                        tf_tof->GetObject(
                            Form("TofEff_cent%d_vz%d_y%d_Pro", iCent, iVz, iY),
                            htof_pro[iCent][iVz][iY]
                        );
                        tf_tof->GetObject(
                            Form("TofEff_cent%d_vz%d_y%d_Pbar", iCent, iVz, iY),
                            htof_pbar[iCent][iVz][iY]
                        );
                    } else {
                        tf_tof->GetObject(
                            Form("TofEff_cent%d_vz%d_y%d_Pro", iCent, iVz, iY),
                            ftof_pro[iCent][iVz][iY]
                        );
                        tf_tof->GetObject(
                            Form("TofEff_cent%d_vz%d_y%d_Pbar", iCent, iVz, iY),
                            ftof_pbar[iCent][iVz][iY]
                        );
                    }
                }
            }

        }
    }
    if (!pidOff) {
        tf_pid->GetObject(
            Form("PidEff_%s_Pro", nSigTag),
            pid_pro
        );
        tf_pid->GetObject(
            Form("PidEff_%s_Pbar", nSigTag),
            pid_pbar
        );
    }
    return;
}

double EffMaker::GetTpcEff(bool positive, double pt, double y, int cent, double vz_) {
    if (tpcOff) { return 1.0; }
    if (cent < 0 || cent >= nCent) { return -1; }
    int vz = VzSplit(vz_);
    if (vz < 0) { return -1; }
    int yb = YPSplit(y);
    if (yb < 0) { return -1; }
    if (positive) {
        ff = ftpc_pro[cent][vz][yb][region];
    } else {
        ff = ftpc_pbar[cent][vz][yb][region];
    }
    double eff = ff->Eval(pt);
    if (eff < 0 || eff > 1) { return -1; }
    return eff;
}

double EffMaker::GetTofEff(bool positive, double pt, double y, int cent, double vz_) {
    if (tofOff) { return 1.0; }
    if (cent < 0 || cent >= nCent) { return -1; }
    int vz = VzSplit(vz_);
    if (vz < 0) { return -1; }
    int yb = YPSplit(y);
    if (yb < 0) { return -1; }
    double eff = -1;
    if (energy == "7.7" || energy == "9.2" || energy == "11.5") {
        if (positive) {
            eff = htof_pro[cent][vz][yb]->Interpolate(pt);
        } else {
            eff = htof_pbar[cent][vz][yb]->Interpolate(pt);
        }
    } else {
        if (positive) {
            eff = ftof_pro[cent][vz][yb]->Eval(pt);
        } else {
            eff = ftof_pbar[cent][vz][yb]->Eval(pt);
        }
    }
    if (eff < 0 || eff > 1) { return -1; }
    return eff;
}

double EffMaker::GetPidEff(bool positive, double pt, double y, bool asCut) {
    if (pidOff) { return 1.0; }
    if (positive) {
        th2 = pid_pro;
    } else {
        th2 = pid_pbar;
    }
    int ybin = th2->GetXaxis()->FindBin(y);
    int ptbin = th2->GetYaxis()->FindBin(pt);
    double eff = th2->GetBinContent(ybin, ptbin);
    if (eff < 0 || eff > 1) { return -1; }
    if (asCut) { eff *= 0.5; }
    return eff;
}

int EffMaker::VzSplit(double vz) {
    /*
        This depends on your vz split method.
        -1 means invalid vz
    */
    if (energy == "27") { // only 3 Vz bins for 27 GeV
        if (-27 < vz && vz < -10) {
            return 0;
        } else if (-10 < vz && vz < 10) {
            return 1;
        } else if (10 < vz && vz < 27) {
            return 2;
        } else {
            return -1;
        }
    } else {
        if (-30 < vz && vz < -10) {
            return 0;
        } else if (-10 < vz && vz < 10) {
            return 1;
        } else if (10 < vz && vz < 30) {
            return 2;
        } else if (-50 < vz && vz < -30) {
            return 3;
        } else if (30 < vz && vz < 50) {
            return 4;
        } else {
            return -1;
        }
    }
}

int EffMaker::YPSplit(double y) {
    /*
        10 bins for 27 GeV, and
        12 bins for other enenrgies
    */
   if (-0.5 < y && y < -0.4) { return 0; }
   else if (-0.4 < y && y < -0.3) { return 1; }
   else if (-0.3 < y && y < -0.2) { return 2; }
   else if (-0.2 < y && y < -0.1) { return 3; }
   else if (-0.1 < y && y < 0.0) { return 4; }
   else if (0.0 < y && y < 0.1) { return 5; }
   else if (0.1 < y && y < 0.2) { return 6; }
   else if (0.2 < y && y < 0.3) { return 7; }
   else if (0.3 < y && y < 0.4) { return 8; }
   else if (0.4 < y && y < 0.5) { return 9; }
   else if (-0.6 < y && y < -0.5 && energy != "27") { return 10; }
   else if (0.5 < y && y < 0.6 && energy != "27") { return 11; }
   else { return -1; }
}