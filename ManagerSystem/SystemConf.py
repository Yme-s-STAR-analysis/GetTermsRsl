r'''
    Version: Homogenous 8.0
    Date: 25.11.2025
'''

class CutConfig:
    def __init__(self):
        self.nHitsFit = 20
        self.nSig = 2.0
        self.dca = 1.0
        self.m2Min = 0.6
        self.m2Max = 1.2
        self.eff_fac_pro = 1.0
        self.eff_fac_pbar = 1.0
        self.nSigmaTag = '2p0'
        self.energy = None
        self.ptMin = 0.4
        self.ptMax = 2.0
        self.fileList = None
        # y range: [min, max, mode, vz range]
        # mode = 0: min < y < max -> necessary when our range is asymmetry about zero
        # mode = 1: min < |y| < max -> necessary when our range doesn't cross zero
        self.yRange = { 
            '0p1': [0.0, 0.1, 1, -50, 50],
            '0p2': [0.0, 0.2, 1, -50, 50],
            '0p3': [0.0, 0.3, 1, -50, 50],
            '0p4': [0.0, 0.4, 1, -50, 50],
            '0p5': [0.0, 0.5, 1, -50, 50],
            '0p6': [0.0, 0.6, 1, -20, 20],
        }
        self.cent_edgeX = None
        self.NpartX = None
        self.w8X = None

    def SetEnergy(self, energy):
        r'''
        To set the energy of dataset.
        This will set the file list.
        This will change rapidity scan range.
        This will set centrality related parameters, including refMult3X edge, mean Npart, reweight.
        '''
        validEnergy = [
            '7.7', '9.2', '11.5', '14.6', '17.3', '19.6', '27'
        ]
        assert(energy in validEnergy)
        self.fileList = f'/star/u/yghuang/Work/DataAnalysis/BES2/OverAll/3AceList/{energy.split(".")[0]}.list'
        self.energy = energy
        if energy == '7.7':
            self.yRange['0p6'] = [0.0, 0.6, 1, -20, 20]
        if energy in ['9.2', '11.5']:
            self.yRange['0p6'] = [0.0, 0.6, 1, -30, 30]
        if energy in ['14.6', '17.3', '19.6']:
            self.yRange['0p6'] = [0.0, 0.6, 1, -40, 40]
        if energy == '27':
            self.yRange = { 
                '0p1': [0.0, 0.1, 1, -27, 27],
                '0p2': [0.0, 0.2, 1, -27, 27],
                '0p3': [0.0, 0.3, 1, -27, 27],
                '0p4': [0.0, 0.4, 1, -27, 27],
                '0p5': [0.0, 0.5, 1, -27, 27],
            }
        # dicts for centrality related parameters
        cent_edgeMap = {
            '7.7': [376, 310, 212, 142, 92, 56, 32, 17, 8],
            '9.2': [465, 384, 262, 175, 113, 70, 40, 21, 10],
            '11.5': [553, 459, 316, 213, 138, 84, 48, 25, 12],
            '14.6': [625, 520, 359, 243, 158, 97, 55, 29, 14],
            '17.3': [675, 561, 386, 260, 168, 103, 59, 31, 15],
            '19.6': [710, 590, 407, 275, 178, 109, 62, 33, 16],
            '27': [494, 409, 279, 187, 121, 74, 42, 22, 11]
        }
        NpartMap = {
            '7.7': [341, 289, 225, 159, 109, 71, 44, 25, 13],
            '9.2': [340, 288, 224, 158, 108, 71, 44, 25, 13],
            '11.5': [341, 289, 225, 159, 109, 71, 44, 25, 13],
            '14.6': [341, 289, 225, 159, 109, 72, 44, 25, 13],
            '17.3': [341, 289, 225, 159, 109, 71, 44, 25, 13],
            '19.6': [342, 290, 226, 160, 110, 72, 44, 25, 13],
            '27': [343, 291, 227, 160, 110, 73, 45, 26, 13]
        }
        w8Map = {
            '7.7': [1.18693, -20.7881, 2.53979, 12.5433, -0.000619924, 5.68357e-07, 1408.1, 212],
            '9.2': [1.40965, -54.8434, 2.45717, 22.1981, -0.00104891, 7.47957e-07, 3244.05, 262],
            '11.5': [1.46036, -77.8252, 2.40017, 33.7963, -0.00100547, 6.43618e-07, 5049.17, 316],
            '14.6': [1.4512, -88.392, 2.37458, 42.5801, -0.000877, 5.1938e-07, 6228.17, 359],
            '17.3': [1.45726, -89.8776, 2.35282, 49.2204, -0.000871909, 4.85995e-07, 7115.1, 386],
            '19.6': [1.62005, -145.283, 2.37174, 48.7206, -0.00102936, 5.35555e-07, 11989.1, 407],
            '27': [1.29286, -41.3695, 2.43434, 26.3825, -0.000741628, 5.3655e-07, 2559.85, 279]
        }
        self.cent_edgeX = cent_edgeMap[energy]
        self.NpartX = NpartMap[energy]
        self.w8X = w8Map[energy]
        
    def SetSystemTag(self, sysTag):
        r'''
        To set the systematic uncertainty tag of dataset.
        This will change the corresponding cuts.
        This will NOT affect the efficiency path, as it is embedded in the EffMaker.
        '''
        if self.energy is None:
            raise Exception('Error: One must call SetEnergy before SetSystemTag!')
        validTag = [
            'default',
            'dca0p8', 'dca0p9', 'dca1p1', 'dca1p2', 
            'nhit15', 'nhit18', 'nhit22', 'nhit25', 'nhit12', 'nhit17',
            'nsig1p6', 'nsig1p8', 'nsig2p2', 'nsigp2p5', 
            'mass21', 'mass22', 'mass23', 'mass24', 
            'effp', 'effm'
        ]
        assert(sysTag in validTag)
        if sysTag[:3] == 'dca': # dca series
            self.dca = float(sysTag[3:].replace('p', '.'))
        if sysTag[:4] == 'nhit': # nHits series
            self.nHitsFit = float(sysTag[4:])
        if sysTag[:4] == 'nsig': # nSigma series
            self.nSigmaTag = sysTag[4:]
            self.nSig = float(sysTag[4:].replace('p', '.'))
        if sysTag[:5] == 'mass2': # mass squared series
            m2Min = [0.5, 0.55, 0.65, 0.7]
            m2Max = [1.1, 1.15, 1.25, 1.3]
            self.m2Min = m2Min[int(sysTag[-1]) - 1]
            self.m2Max = m2Max[int(sysTag[-1]) - 1]
        if sysTag[:3] == 'eff':
            eff_fac = -1
            if self.energy == '27':
                if sysTag[-1] == 'p':
                    eff_fac = 1.05
                if sysTag[-1] == 'm':
                    eff_fac = 0.95
            else:
                if sysTag[-1] == 'p':
                    eff_fac = 1.02
                if sysTag[-1] == 'm':
                    eff_fac = 0.98
            self.eff_fac_pro = eff_fac
            self.eff_fac_pbar = eff_fac