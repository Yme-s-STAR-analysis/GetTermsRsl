#ifndef __RSL_QLTCTRL__
#define __RSL_QLTCTRL__

#include <fstream>
#include <iostream>
#include <string>

class QualityController {

    private:
        std::ifstream* mIfConfig;
        // event quantities
        double vzMin;
        double vzMax;
        // double vrCut;
        // double nSigDCAzCut;
        // double nSigsDCAxyCut;

        // track quantities
        double ptMin;
        double ptMax;
        int rapidityMode;
        double yMin;
        double yMax;
        double nHitsFitCut;
        // double nHitsDedxCut;
        // double nHitsRatioCut;
        double nSigmaCut;
        double dcaCut;
        double mass2Min;
        double mass2Max;
        // switch: have read config
        bool isDefault;

    public:
        QualityController();
        ~QualityController(){}

        void readConfig(std::ifstream* ifConfig);
        void Print();
        bool isBadEvent(double vz); // vr is removed
        bool isBadTrack(double pt, double y, int nHitsFit, double nSigma, double dca, bool needTOF, double mass2, bool asCut=false); // nHitsDedx and nHitsRatio are removed
};

#endif
