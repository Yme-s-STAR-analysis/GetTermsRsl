#ifndef __RSL_EFFMAKER__
#define __RSL_EFFMAKER__

#include <string>

class TH1D;
class TH2F;
class TF1;

class EffMaker{
    private:
        static const int nCent = 9;
        static const int nVz = 5;
        static const int nRegion = 2; // this is for 9.2 GeV

        int region;
        std::string energy;
        TH2F* pid_pro;
        TH2F* pid_pbar;

        TH2F* th2;

        static const int nY = 12;
        // TPC efficiency, two-region design is only for 9.2 GeV
        TF1* ftpc_pro[nCent][nVz][nY][nRegion];
        TF1* ftpc_pbar[nCent][nVz][nY][nRegion];

        // TOF efficiency, bin-by-bin for enenrgy >= 14.6
        TH1D* htof_pro[nCent][nVz][nY];
        TH1D* htof_pbar[nCent][nVz][nY];
        // TOF efficiency, interpolation for enenrgy <= 11.5
        TF1* ftof_pro[nCent][nVz][nY];
        TF1* ftof_pbar[nCent][nVz][nY];

        TF1* ff;

        bool tpcOff;
        bool tofOff;
        bool pidOff;

    public:
        EffMaker():region(0){}
        ~EffMaker(){}

        bool Init(std::string energy, const char* sysTag,const char* nSigTag);
        void ReadInEffFile(const char* tpc, const char* tof, const char* pid, const char* nSigTag);
        double GetTpcEff(bool positive, double pt, double y, int cent, double vz);
        double GetTofEff(bool positive, double pt, double y, int cent, double vz);
        double GetPidEff(bool positive, double pt, double y, bool asCut);
        int YPSplit(double y);
        int VzSplit(double vz);
        void SetRegion(int region) { this->region = region; } // for 9.2 GeV, call this in Core.cxx when for each femto-event
};

#endif