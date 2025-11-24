#ifndef __RSL_CENTDEFCLASS__
#define __RSL_CENTDEFCLASS__

class CentDefinition {

    private:
        static const int nCent = 9;
        int edge[nCent];
        bool set;

    public:
        CentDefinition();
        ~CentDefinition(){}

        void Init(const char* path);
        int GetCentrality(int mult);
};

#endif