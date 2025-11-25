r'''
    Version: Homogenous 8.0
    Date: 25.11.2025
'''
import SystemConf

class Args:
    def __init__(self):
        self.nFilesPerJob = 80
        self.targetDir = '/target/path'
        self.outDir = f'{self.targetDir}/job'
        self.mergeDir = f'{self.targetDir}/merge'
        self.runDir = f'{self.targetDir}/run'
        self.energy = '27'
        self.sysTag = 'default'
        self.calc_exec = '/star/u/yghuang/.tools/CumulantCalculation/runCumulantHomo'

        # cut configurations
        self.cf = SystemConf.CutConfig()
        self.cf.SetEnergy(self.energy)
        self.cf.SetSystemTag(self.sysTag)
        self.title = self.sysTag # for compatibility
        self.fileList = self.cf.fileList
        self.nHitsFit = self.cf.nHitsFit
        self.nSig = self.cf.nSig
        self.dca = self.cf.dca
        self.m2Min = self.cf.m2Min
        self.m2Max = self.cf.m2Max
        self.nSigmaTag = self.cf.nSigmaTag
        self.eff_fac_pro = self.cf.eff_fac_pro
        self.eff_fac_pbar = self.cf.eff_fac_pbar
        # centrality related parameters
        self.cent_edgeX = self.cf.cent_edgeX
        self.NpartX = self.cf.NpartX
        self.w8X = self.cf.w8X
        # pt scan options, by default we turn off all of them
        self.ptScan = False
        self.ptMin = self.cf.ptMin # when do pT scan,
        self.ptMax = self.cf.ptMax # this value will be default
        self.pTRange = {}
        # y scan options
        self.yScan = True
        self.yMin = 0.0 # when do pt scan
        self.yMax = 0.5 # these values will be default
        self.yMode = 1  # y min/max and mode (-0.5~0.5)
        self.yRange = self.cf.yRange