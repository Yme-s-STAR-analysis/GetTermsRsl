import sys
import os
from conf import Args
from yLog import yLog

__version__ = 'Homo 8.0'
__updatedTime__ = '25.11.2025'

l = yLog('.ManagerSystem.log')
CutArgs = Args() # create an instance

modeList = ['submit', 'merge', 'calculate', 'collect', 'clean', 'report']
abbrMap = {
    'sub': 'submit',
    'mer': 'merge',
    'run': 'calculate',
    'calc': 'calculate',
    'col': 'collect',
    'coll': 'collect',
    'cla': 'clean',
    'repo': 'report'
}
mode = sys.argv[1]
mode = abbrMap[mode] if mode in abbrMap else mode
assert(mode in modeList)

if mode not in ['clean', 'report']:
    if CutArgs.yScan:
        l.log(f'Rapidity scan is [ON] with {len(CutArgs.yRange)} tasks.')
        l.log(f'During rapidity scan, pT range will be [{CutArgs.ptMin}, {CutArgs.ptMax}].')
        for i, item in enumerate(CutArgs.yRange):
            l.log(f'\t[{i+1:02d}] {item} {CutArgs.yRange[item][0]} -> {CutArgs.yRange[item][1]} (mode {CutArgs.yRange[item][2]}) Vz: {CutArgs.yRange[item][3]} -> {CutArgs.yRange[item][4]}')
    else:
        l.log(f'Rapidity scan is [OFF].')
    if CutArgs.ptScan:
        l.log(f'pT scan is [ON] with {len(CutArgs.pTRange)} jobs.')
        l.log(f'During pT scan, y range will be [{CutArgs.yMin}, {CutArgs.yMax}].')
        for i, item in enumerate(CutArgs.pTRange):
            l.log(f'\t[{i+1:02d}] {item} {CutArgs.pTRange[item][0]} -> {CutArgs.pTRange[item][1]} Vz: {CutArgs.pTRange[item][2]} -> {CutArgs.pTRange[item][3]}')
    else:
        l.log(f'pT scan is [OFF].')

with open(CutArgs.fileList) as f:
    flist = f.readlines()
nFiles = len(flist)
nFilesPerJob = CutArgs.nFilesPerJob
nJobs = nFiles // nFilesPerJob
bonus = nFiles - nJobs * nFilesPerJob
msDir = f'{CutArgs.targetDir}/ManagerSystem'

# submit mode
if mode == 'submit':
    if len(sys.argv) != 3:
        raise Exception(f'Submit mode must accept 3 arguments but got {len(sys.argv)}')
    else:
        sMode = sys.argv[2]
        assert(sMode in ['s', 'b', 'r']) # this r: read resubmit.id.txt and resubmit
        if sMode == 's':
            l.log('Simulation mode, only generate sub-folders, you can submit the jobs with option [b].')
        if sMode == 'b':
            l.log('Submit jobs with pre-generated sub-folders.')
        if sMode == 'r':
            l.log('Resubmit jobs from "resubmit.id.txt"')
            if not os.path.exists('resubmit.id.txt'):
                raise Exception(f'[ERROR] Cannot open resubmit.id.txt!')
            
    outDir = CutArgs.outDir
    if sMode == 'r':
        rids = open('resubmit.id.txt').readlines()
        rids = [item.strip() for item in rids]
        rids = [item for item in rids if item != '']
        l.log(f'{len(rids)} jobs will be resubmitted.')
        for idx, line in enumerate(rids):
            rScanTag, rJobIdx  = line.split(' ') # must splited by one space
            l.log(f'[{idx+1}] - {CutArgs.title} {rScanTag} job{rJobIdx}')
            os.system(f'cd {outDir}/job{rJobIdx} && condor_submit {CutArgs.title}.{rJobIdx}.{rScanTag}.getTerms.job')
        l.log('Done.')
    else:
        l.log('Now preparing Job Directory and File Lists. May take few seconds.')
        if not os.path.exists(outDir):
            os.mkdir(outDir)
        l.log(f'===Submit System for GetTerms===')
        l.log('Summary of configuration are listed below:')
        l.log(f'{CutArgs.nFilesPerJob=}')
        l.log(f'{CutArgs.outDir=}')
        l.log(f'{CutArgs.fileList=}')
        l.log(f'{CutArgs.energy=}')
        l.log(f'{CutArgs.nSigmaTag=}')
        l.log(f'{CutArgs.eff_fac_pro=}')
        l.log(f'{CutArgs.eff_fac_pbar=}')
        l.log(f'{nFiles} files in total, {nJobs} regular jobs with {nFilesPerJob} files to handle.')
        if bonus:
            nJobs += 1
            l.log(f'Bonus job will manage {bonus} jobs.')

    if sMode == 's':
        # step 1: prepare file lists
        l.log('Now generating file lists for sub-jobs')
        if os.path.exists(f'{msDir}'):
            os.system(f'rm -rf {msDir}')
        os.mkdir(f'{msDir}')
        for i in range(nJobs):
            if bonus and i == nJobs -1: # nJobs already takes bonus into account 
                continue
            with open(f'{msDir}/{i}.list', 'w') as f:
                for line in range(i * nFilesPerJob, (i+1) * nFilesPerJob):
                    f.write(flist[line])
        if bonus:
            with open(f'{msDir}/{nJobs - 1}.list', 'w') as f:
                for line in range((nJobs - 1) * nFilesPerJob, nFiles):
                    f.write(flist[line])

        # step 2: prepare submitting scripts
        l.log('Now preparing submitting scripts')
        # TASK_TAG will ba changed when submit the jobs
        # on current stage, general parameters are given
        getTermsShellFile = f'{msDir}/getTerms.sh'
        os.system(f'cp {os.getcwd()}/getTerms.sh {getTermsShellFile}')
        os.system(f'sed -i "s|NSIG_TAG|{CutArgs.nSigmaTag}|g" {getTermsShellFile}')
        os.system(f'sed -i "s|EFF_FAC_PRO|{CutArgs.eff_fac_pro}|g" {getTermsShellFile}')
        os.system(f'sed -i "s|EFF_FAC_PBAR|{CutArgs.eff_fac_pbar}|g" {getTermsShellFile}')
        os.system(f'sed -i "s|ENERGY|{CutArgs.energy}|g" {getTermsShellFile}')

        # step 3: prepare cfg files
        l.log('Now preparing cfg files')
        if CutArgs.yScan:
            nScan_y = len(CutArgs.yRange)
            l.log(f'Rapidity scan is [ON], task list:')
            for i, item in enumerate(CutArgs.yRange):
                l.log(f'[{i:02d} / {nScan_y:02d}] - {item}: {CutArgs.yRange[item][0]} -> {CutArgs.yRange[item][1]}, (mode {CutArgs.yRange[item][2]}) Vz range: {CutArgs.yRange[item][3]} -> {CutArgs.yRange[item][4]} cm')
                with open(f'{msDir}/{CutArgs.title}.y{item}.getTerms.cfg', 'w') as f:
                    f.write('VARLIST\n')
                    f.write(f'VZ\t{CutArgs.yRange[item][3]}\t{CutArgs.yRange[item][4]}\n')
                    f.write(f'PT\t{CutArgs.ptMin}\t{CutArgs.ptMax}\n')
                    f.write(f'YP\t{CutArgs.yRange[item][0]}\t{CutArgs.yRange[item][1]}\n')
                    f.write(f'NHITSFIT\t{CutArgs.nHitsFit}\n')
                    f.write(f'NSIG\t{CutArgs.nSig}\n')
                    f.write(f'DCA\t{CutArgs.dca}\n')
                    f.write(f'MASS2\t{CutArgs.m2Min}\t{CutArgs.m2Max}\n')
                    f.write(f'RMODE\t{CutArgs.yRange[item][2]}\n')
                    f.write(f'END')
                    
        if CutArgs.ptScan:
            nScan_pt = len(CutArgs.pTRange)
            l.log(f'pT scan is [ON], task list:')
            for i, item in enumerate(CutArgs.pTRange):
                l.log(f'[{i:02d} / {nScan_pt:02d}] - {item}: {CutArgs.pTRange[item][0]} -> {CutArgs.pTRange[item][1]} Vz range: {CutArgs.pTRange[item][2]} -> {CutArgs.pTRange[item][3]} cm')
                with open(f'{msDir}/{CutArgs.title}.pt{item}.getTerms.cfg', 'w') as f:
                    f.write('VARLIST\n')
                    f.write(f'VZ\t{CutArgs.pTRange[item][2]}\t{CutArgs.pTRange[item][3]}\n')
                    f.write(f'PT\t{CutArgs.pTRange[item][0]}\t{CutArgs.pTRange[item][1]}\n')
                    f.write(f'YP\t{CutArgs.yMin}\t{CutArgs.yMax}\n')
                    f.write(f'NHITSFIT\t{CutArgs.nHitsFit}\n')
                    f.write(f'NSIG\t{CutArgs.nSig}\n')
                    f.write(f'DCA\t{CutArgs.dca}\n')
                    f.write(f'MASS2\t{CutArgs.m2Min}\t{CutArgs.m2Max}\n')
                    f.write(f'RMODE\t{CutArgs.yMode}\n')
                    f.write(f'END')

        
        # step 4: prepare symlink
        l.log('Now preparing symlink to the executable')
        # get the absolute path to getTerms
        execPath = os.path.abspath(f'{os.getcwd()}/../Source/getTerms')
        os.symlink(execPath, f'{msDir}/getTerms')

        # step 5: prepare job files
        l.log('Now preparing job files')
        os.system(f'cp getTerms.job {msDir}/getTerms.job')

        # step 6: prepare text files
        l.log('Now preparing text files')
        with open(f'{msDir}/cent_edgeX.txt', 'w') as f:
            for idx, item in enumerate(CutArgs.cent_edgeX):
                f.write(f'{item}')
                if idx != len(CutArgs.cent_edgeX) -1:
                    f.write('\n')
        with open(f'{msDir}/w8X.txt', 'w') as f:
            for idx, item in enumerate(CutArgs.w8X):
                f.write(f'{item}')
                if idx != len(CutArgs.w8X) -1:
                    f.write('\n')
        with open(f'{msDir}/NpartX.txt', 'w') as f:
            for idx, item in enumerate(CutArgs.NpartX):
                f.write(f'{item}')
                if idx != len(CutArgs.NpartX) -1:
                    f.write('\n')

        l.log('Now deploying')
        os.system(f'cp conf.py {msDir}/conf.py')
        os.system(f'cp SystemConf.py {msDir}/SystemConf.py')
        os.system(f'cp deploy.py {msDir}/deploy.py')
        os.system(f'cp deploy.job {msDir}/deploy.job')
        os.system(f'cd {msDir} && condor_submit deploy.job')
        l.log('Done.')

    if sMode == 'b':
        for i in range(nJobs):
            if CutArgs.yScan:
                for item in CutArgs.yRange:
                    os.system(f'cd {outDir}/job{i} && condor_submit {CutArgs.title}.{i}.y{item}.getTerms.job')
            if CutArgs.ptScan:
                for item in CutArgs.pTRange:
                    os.system(f'cd {outDir}/job{i} && condor_submit {CutArgs.title}.{i}.pt{item}.getTerms.job')
        l.log('Done.')

# merge mode
if mode == 'merge':
    outDir = CutArgs.outDir
    mergeDir = CutArgs.mergeDir

    mIter = 0
    if len(sys.argv) != 3:
        raise Exception(f'Merge mode must accept 2 arguments but got {len(sys.argv)}')
    else:
        mIter = int(sys.argv[2])
        assert(mIter >= 0)
        if mIter == 1:
            l.log('First iteration of merging, will merge raw outputs from previous stage')
        elif mIter == 0:
            l.log('One-time merging, will merge all raw outputs from previous stage')
        else:
            l.log(f'Additional iteration of merging ({mIter}), will merge merged files from previous iteration ({mIter-1})')

    if not os.path.exists(outDir):
        raise Exception(f'[ERROR] {outDir=} which does not exist.')

    if not os.path.exists(mergeDir):
        os.mkdir(mergeDir)

    if not os.path.exists(f'{mergeDir}/Iter{mIter}'):
        os.mkdir(f'{mergeDir}/Iter{mIter}')

    l.log('Here are the root files to be merged:')
    if CutArgs.yScan:
        l.log('For rapidity scan:')
        for idx, item in enumerate(CutArgs.yRange):
            l.log(f'Item {idx+1:02d}: y{item}')
    if CutArgs.ptScan:
        l.log('For pT scan:')
        for idx, item in enumerate(CutArgs.pTRange):
            l.log(f'Item {idx+1:02d}: pt{item}')
    
    if mIter == 1: # first iteration
        mFilesPerJob = 15
        if bonus:
            nJobs += 1
        mJobs = nJobs // mFilesPerJob
        mBonus = nJobs - mJobs * mFilesPerJob

        for iJob in range(mJobs):
            cJobDir = f'{mergeDir}/Iter{mIter}/job{iJob}'
            if os.path.exists(f'{cJobDir}'):
                os.system(f'rm -rf {cJobDir}')
            os.mkdir(f'{cJobDir}')
            os.system(f'cp merge.py {cJobDir}/merge.py')
            os.system(f'cp yLog.py {cJobDir}/yLog.py')

            if CutArgs.yScan:
                for item in CutArgs.yRange:
                    if True:
                        cJobFile = f'merge.y{item}X.job'
                        # prepare list
                        with open(f'{cJobDir}/y{item}X.{iJob}.list', 'w') as f:
                            for iFile in range(mFilesPerJob):
                                f.write(f'{outDir}/job{iFile+iJob*mFilesPerJob}/{CutArgs.title}.y{item}X.root\n')
                        # change configuration
                        os.system(f'cp merge.job {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TASKNAME|{CutArgs.title}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|SCANNAME|y{item}X|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|ITERID|{mIter}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|MERGEID|{iJob}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|FLIST|{cJobDir}/y{item}X.{iJob}.list|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TDIR|{cJobDir}|g" {cJobDir}/{cJobFile}')
                        # submit
                        l.log(f'Current task: y{item} Iteration-{mIter} Job-{iJob} RefMult3X mTerms')
                        os.system(f'cd {cJobDir} && condor_submit {cJobDir}/{cJobFile}')
                    # pDist
                    if True:
                        cJobFile = f'merge.y{item}.pDist.job'
                        # prepare list
                        with open(f'{cJobDir}/y{item}.pDist.{iJob}.list', 'w') as f:
                            for iFile in range(mFilesPerJob):
                                f.write(f'{outDir}/job{iFile+iJob*mFilesPerJob}/{CutArgs.title}.y{item}.pDist.root\n')
                        # change configuration
                        os.system(f'cp merge.job {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TASKNAME|{CutArgs.title}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|SCANNAME|y{item}.pDist|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|ITERID|{mIter}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|MERGEID|{iJob}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|FLIST|{cJobDir}/y{item}.pDist.{iJob}.list|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TDIR|{cJobDir}|g" {cJobDir}/{cJobFile}')
                        # submit
                        l.log(f'Current task: y{item} Iteration-{mIter} Job-{iJob} pDist')
                        os.system(f'cd {cJobDir} && condor_submit {cJobDir}/{cJobFile}')
            if CutArgs.ptScan:
                for item in CutArgs.pTRange:
                    if True:
                        cJobFile = f'merge.pt{item}X.job'
                        # prepare list
                        with open(f'{cJobDir}/pt{item}X.{iJob}.list', 'w') as f:
                            for iFile in range(mFilesPerJob):
                                f.write(f'{outDir}/job{iFile+iJob*mFilesPerJob}/{CutArgs.title}.pt{item}X.root\n')
                        # change configuration
                        os.system(f'cp merge.job {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TASKNAME|{CutArgs.title}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|SCANNAME|pt{item}X|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|ITERID|{mIter}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|MERGEID|{iJob}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|FLIST|{cJobDir}/pt{item}X.{iJob}.list|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TDIR|{cJobDir}|g" {cJobDir}/{cJobFile}')
                        # submit
                        l.log(f'Current task: pt{item} Iteration-{mIter} Job-{iJob} RefMult3X mTerms')
                        os.system(f'cd {cJobDir} && condor_submit {cJobDir}/{cJobFile}')
                    # pDist
                    if True:
                        cJobFile = f'merge.pt{item}.pDist.job'
                        # prepare list
                        with open(f'{cJobDir}/pt{item}.pDist.{iJob}.list', 'w') as f:
                            for iFile in range(mFilesPerJob):
                                f.write(f'{outDir}/job{iFile+iJob*mFilesPerJob}/{CutArgs.title}.pt{item}.pDist.root\n')
                        # change configuration
                        os.system(f'cp merge.job {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TASKNAME|{CutArgs.title}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|SCANNAME|pt{item}.pDist|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|ITERID|{mIter}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|MERGEID|{iJob}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|FLIST|{cJobDir}/pt{item}.pDist.{iJob}.list|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TDIR|{cJobDir}|g" {cJobDir}/{cJobFile}')
                        # submit
                        l.log(f'Current task: pt{item} Iteration-{mIter} Job-{iJob} pDist')
                        os.system(f'cd {cJobDir} && condor_submit {cJobDir}/{cJobFile}')
        
        if mBonus > 0:
            cJobDir = f'{mergeDir}/Iter{mIter}/job{mJobs}'
            if os.path.exists(f'{cJobDir}'):
                os.system(f'rm -rf {cJobDir}')
            os.mkdir(f'{cJobDir}')
            os.system(f'cp merge.py {cJobDir}/merge.py')
            os.system(f'cp yLog.py {cJobDir}/yLog.py')
            if CutArgs.yScan:
                for item in CutArgs.yRange:
                    if True:
                        cJobFile = f'merge.y{item}X.job'
                        # prepare list
                        with open(f'{cJobDir}/y{item}X.{mJobs}.list', 'w') as f:
                            for iFile in range(mBonus):
                                f.write(f'{outDir}/job{iFile+mJobs*mFilesPerJob}/{CutArgs.title}.y{item}X.root\n')
                        # change configuration
                        os.system(f'cp merge.job {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TASKNAME|{CutArgs.title}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|SCANNAME|y{item}X|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|ITERID|{mIter}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|MERGEID|{mJobs}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|FLIST|{cJobDir}/y{item}X.{mJobs}.list|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TDIR|{cJobDir}|g" {cJobDir}/{cJobFile}')
                        # submit
                        l.log(f'Current task: y{item} Iteration-{mIter} Job-{mJobs} RefMult3X mTerms')
                        os.system(f'cd {cJobDir} && condor_submit {cJobDir}/{cJobFile}')
                    # pDist
                    if True:
                        cJobFile = f'merge.y{item}.pDist.job'
                        # prepare list
                        with open(f'{cJobDir}/y{item}.pDist.{mJobs}.list', 'w') as f:
                            for iFile in range(mBonus):
                                f.write(f'{outDir}/job{iFile+mJobs*mFilesPerJob}/{CutArgs.title}.y{item}.pDist.root\n')
                        # change configuration
                        os.system(f'cp merge.job {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TASKNAME|{CutArgs.title}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|SCANNAME|y{item}.pDist|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|ITERID|{mIter}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|MERGEID|{mJobs}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|FLIST|{cJobDir}/y{item}.pDist.{mJobs}.list|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TDIR|{cJobDir}|g" {cJobDir}/{cJobFile}')
                        # submit
                        l.log(f'Current task: y{item} Iteration-{mIter} Job-{mJobs} pDist')
                        os.system(f'cd {cJobDir} && condor_submit {cJobDir}/{cJobFile}')   
            if CutArgs.ptScan:
                for item in CutArgs.pTRange:
                    if True:
                        cJobFile = f'merge.pt{item}X.job'
                        # prepare list
                        with open(f'{cJobDir}/pt{item}X.{mJobs}.list', 'w') as f:
                            for iFile in range(mBonus):
                                f.write(f'{outDir}/job{iFile+mJobs*mFilesPerJob}/{CutArgs.title}.pt{item}X.root\n')
                        # change configuration
                        os.system(f'cp merge.job {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TASKNAME|{CutArgs.title}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|SCANNAME|pt{item}X|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|ITERID|{mIter}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|MERGEID|{mJobs}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|FLIST|{cJobDir}/pt{item}X.{mJobs}.list|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TDIR|{cJobDir}|g" {cJobDir}/{cJobFile}')
                        # submit
                        l.log(f'Current task: pt{item} Iteration-{mIter} Job-{mJobs} RefMult3X mTerms')
                        os.system(f'cd {cJobDir} && condor_submit {cJobDir}/{cJobFile}')
                    # pDist
                    if True:
                        cJobFile = f'merge.pt{item}.pDist.job'
                        # prepare list
                        with open(f'{cJobDir}/pt{item}.pDist.{mJobs}.list', 'w') as f:
                            for iFile in range(mBonus):
                                f.write(f'{outDir}/job{iFile+mJobs*mFilesPerJob}/{CutArgs.title}.pt{item}.pDist.root\n')
                        # change configuration
                        os.system(f'cp merge.job {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TASKNAME|{CutArgs.title}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|SCANNAME|pt{item}.pDist|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|ITERID|{mIter}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|MERGEID|{mJobs}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|FLIST|{cJobDir}/pt{item}.pDist.{mJobs}.list|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TDIR|{cJobDir}|g" {cJobDir}/{cJobFile}')
                        # submit
                        l.log(f'Current task: pt{item} Iteration-{mIter} Job-{mJobs} pDist')
                        os.system(f'cd {cJobDir} && condor_submit {cJobDir}/{cJobFile}')

    elif mIter == 0: # one-time merging
        if bonus:
            nJobs += 1

        cJobDir = f'{mergeDir}/Iter2'
        if os.path.exists(f'{cJobDir}'):
            os.system(f'rm -rf {cJobDir}')
        os.mkdir(f'{cJobDir}')
        os.system(f'cp merge.py {cJobDir}/merge.py')
        os.system(f'cp yLog.py {cJobDir}/yLog.py')

        if CutArgs.yScan:
            for item in CutArgs.yRange:
                if True:
                    cJobFile = f'merge.y{item}X.job'
                    # prepare list
                    with open(f'{cJobDir}/y{item}X.list', 'w') as f:
                        for iFile in range(nJobs):
                            f.write(f'{outDir}/job{iFile}/{CutArgs.title}.y{item}X.root\n')
                    # change configuration
                    os.system(f'cp merge.job {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|TASKNAME|{CutArgs.title}|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|SCANNAME|y{item}X|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|ITERID|2|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|MERGEID|0|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|FLIST|{cJobDir}/y{item}X.list|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|TDIR|{cJobDir}|g" {cJobDir}/{cJobFile}')
                    # submit
                    l.log(f'Current task: y{item} Iteration-0 RefMult3X mTerms')
                    os.system(f'cd {cJobDir} && condor_submit {cJobDir}/{cJobFile}')
                # pDist
                if True:
                    cJobFile = f'merge.y{item}.pDist.job'
                    # prepare list
                    with open(f'{cJobDir}/y{item}.pDist.list', 'w') as f:
                        for iFile in range(nJobs):
                            f.write(f'{outDir}/job{iFile}/{CutArgs.title}.y{item}.pDist.root\n')
                    # change configuration
                    os.system(f'cp merge.job {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|TASKNAME|{CutArgs.title}|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|SCANNAME|y{item}.pDist|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|ITERID|2|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|MERGEID|0|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|FLIST|{cJobDir}/y{item}.pDist.list|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|TDIR|{cJobDir}|g" {cJobDir}/{cJobFile}')
                    # submit
                    l.log(f'Current task: y{item} Iteration-0 pDist')
                    os.system(f'cd {cJobDir} && condor_submit {cJobDir}/{cJobFile}')
            if CutArgs.ptScan:
                for item in CutArgs.pTRange:
                    if True:
                        cJobFile = f'merge.pt{item}X.job'
                        # prepare list
                        with open(f'{cJobDir}/pt{item}X.list', 'w') as f:
                            for iFile in range(nJobs):
                                f.write(f'{outDir}/job{iFile}/{CutArgs.title}.pt{item}X.root\n')
                        # change configuration
                        os.system(f'cp merge.job {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TASKNAME|{CutArgs.title}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|SCANNAME|pt{item}X|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|ITERID|2|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|MERGEID|0|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|FLIST|{cJobDir}/pt{item}X.list|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TDIR|{cJobDir}|g" {cJobDir}/{cJobFile}')
                        # submit
                        l.log(f'Current task: pt{item} Iteration-0 RefMult3X mTerms')
                        os.system(f'cd {cJobDir} && condor_submit {cJobDir}/{cJobFile}')
                    # pDist
                    if True:
                        cJobFile = f'merge.pt{item}.pDist.job'
                        # prepare list
                        with open(f'{cJobDir}/pt{item}.pDist.list', 'w') as f:
                            for iFile in range(nJobs):
                                f.write(f'{outDir}/job{iFile}/{CutArgs.title}.pt{item}.pDist.root\n')
                        # change configuration
                        os.system(f'cp merge.job {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TASKNAME|{CutArgs.title}|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|SCANNAME|pt{item}.pDist|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|ITERID|2|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|MERGEID|0|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|FLIST|{cJobDir}/pt{item}.pDist.list|g" {cJobDir}/{cJobFile}')
                        os.system(f'sed -i "s|TDIR|{cJobDir}|g" {cJobDir}/{cJobFile}')
                        # submit
                        l.log(f'Current task: pt{item} Iteration-0 pDist')
                        os.system(f'cd {cJobDir} && condor_submit {cJobDir}/{cJobFile}')
        
    elif mIter == 2: # in principle, we only need at most 2 times
        lastIterPath = f'{mergeDir}/Iter{mIter-1}'
        lastIterJobs = os.listdir(lastIterPath)
        lastIterJobs = [item for item in lastIterJobs if item.startswith('job')]
        mJobs = len(lastIterJobs)
        cJobDir = f'{mergeDir}/Iter{mIter}'
        os.system(f'cp merge.py {cJobDir}/merge.py')
        os.system(f'cp yLog.py {cJobDir}/yLog.py')

        if CutArgs.yScan:
            for item in CutArgs.yRange:
                if True:
                    cJobFile = f'merge.y{item}X.job'
                    # prepare list
                    with open(f'{cJobDir}/y{item}X.list', 'w') as f:
                        for iFile in range(mJobs):
                            f.write(f'{mergeDir}/Iter{mIter-1}/job{iFile}/{CutArgs.title}.y{item}X.root\n')
                    # change configuration
                    os.system(f'cp merge.job {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|TASKNAME|{CutArgs.title}|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|SCANNAME|y{item}X|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|ITERID|{mIter}|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|MERGEID|tot|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|FLIST|{cJobDir}/y{item}X.list|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|TDIR|{cJobDir}|g" {cJobDir}/{cJobFile}')
                    # submit
                    l.log(f'Current task: y{item} Iteration-{mIter} RefMult3X mTerms')
                    os.system(f'cd {cJobDir} && condor_submit {cJobDir}/{cJobFile}')
                # pDist
                if True:
                    cJobFile = f'merge.y{item}.pDist.job'
                    # prepare list
                    with open(f'{cJobDir}/y{item}.pDist.list', 'w') as f:
                        for iFile in range(mJobs):
                            f.write(f'{mergeDir}/Iter{mIter-1}/job{iFile}/{CutArgs.title}.y{item}.pDist.root\n')
                    # change configuration
                    os.system(f'cp merge.job {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|TASKNAME|{CutArgs.title}|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|SCANNAME|y{item}.pDist|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|ITERID|{mIter}|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|MERGEID|tot|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|FLIST|{cJobDir}/y{item}.pDist.list|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|TDIR|{cJobDir}|g" {cJobDir}/{cJobFile}')
                    # submit
                    l.log(f'Current task: y{item} Iteration-{mIter} pDist')
                    os.system(f'cd {cJobDir} && condor_submit {cJobDir}/{cJobFile}')
        if CutArgs.ptScan:
            for item in CutArgs.pTRange:
                if True:
                    cJobFile = f'merge.pt{item}X.job'
                    # prepare list
                    with open(f'{cJobDir}/pt{item}X.list', 'w') as f:
                        for iFile in range(mJobs):
                            f.write(f'{mergeDir}/Iter{mIter-1}/job{iFile}/{CutArgs.title}.pt{item}X.root\n')
                    # change configuration
                    os.system(f'cp merge.job {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|TASKNAME|{CutArgs.title}|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|SCANNAME|pt{item}X|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|ITERID|{mIter}|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|MERGEID|tot|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|FLIST|{cJobDir}/pt{item}X.list|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|TDIR|{cJobDir}|g" {cJobDir}/{cJobFile}')
                    # submit
                    l.log(f'Current task: pt{item} Iteration-{mIter} RefMult3X mTerms')
                    os.system(f'cd {cJobDir} && condor_submit {cJobDir}/{cJobFile}')
                # pDist
                if True:
                    cJobFile = f'merge.pt{item}.pDist.job'
                    # prepare list
                    with open(f'{cJobDir}/pt{item}.pDist.list', 'w') as f:
                        for iFile in range(mJobs):
                            f.write(f'{mergeDir}/Iter{mIter-1}/job{iFile}/{CutArgs.title}.pt{item}.pDist.root\n')
                    # change configuration
                    os.system(f'cp merge.job {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|TASKNAME|{CutArgs.title}|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|SCANNAME|pt{item}.pDist|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|ITERID|{mIter}|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|MERGEID|tot|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|FLIST|{cJobDir}/pt{item}.pDist.list|g" {cJobDir}/{cJobFile}')
                    os.system(f'sed -i "s|TDIR|{cJobDir}|g" {cJobDir}/{cJobFile}')
                    # submit
                    l.log(f'Current task: pt{item} Iteration-{mIter} pDist')
                    os.system(f'cd {cJobDir} && condor_submit {cJobDir}/{cJobFile}')
    else:
        raise Exception('As per current design, merge supports at most 2 iteration!') 

# run mode
if mode == 'calculate':
    mergeDir = f'{CutArgs.mergeDir}/Iter2' # we only wants 2 iterations
    runDir = CutArgs.runDir

    if not os.path.exists(mergeDir):
        raise Exception(f'[ERROR] {mergeDir=} which does not exist.')
    
    if not os.path.exists(runDir):
        os.mkdir(runDir)

    l.log('Here are the task names to be calculated:')
    if CutArgs.yScan:
        for idx, item in enumerate(CutArgs.yRange):
            l.log('For rapidity scan:')
            l.log(f'Item {idx+1:03d} - y{item}')

            if True:
                cJobDir = f'{runDir}/y{item}X'
                if not os.path.exists(f'{cJobDir}'):
                    os.mkdir(f'{cJobDir}')
                if not os.path.exists(f'{cJobDir}/runCumulant'):
                    os.symlink(CutArgs.calc_exec, f'{cJobDir}/runCumulant')
                if not os.path.exists(f'{cJobDir}/cent_edge.txt'):
                    os.symlink(f'{msDir}/cent_edgeX.txt', f'{cJobDir}/cent_edge.txt')
                if not os.path.exists(f'{cJobDir}/Npart.txt'):
                    os.symlink(f'{msDir}/NpartX.txt', f'{cJobDir}/Npart.txt')
                if not os.path.exists(f'{cJobDir}/w8.txt'):
                    os.symlink(f'{msDir}/w8X.txt', f'{cJobDir}/w8.txt')
                if os.path.exists(f'{cJobDir}/{CutArgs.title}.y{item}X.root'):
                    os.remove(f'{cJobDir}/{CutArgs.title}.y{item}X.root')
                os.symlink(f'{mergeDir}/{CutArgs.title}.y{item}X.root', f'{cJobDir}/{CutArgs.title}.y{item}X.root')
                os.system(f'cp calc.sh {cJobDir}/{CutArgs.title}.y{item}X.calc.sh')
                os.system(f'cp calc.job {cJobDir}/{CutArgs.title}.y{item}X.calc.job')
                os.system(f'sed -i "s|TASKNAME|{CutArgs.title}.y{item}X|g" {cJobDir}/{CutArgs.title}.y{item}X.calc.sh')
                os.system(f'sed -i "s|SHELLNAME|{CutArgs.title}.y{item}X.calc.sh|g" {cJobDir}/{CutArgs.title}.y{item}X.calc.job')
                os.system(f'sed -i "s|TASKNAME|{CutArgs.title}.y{item}X|g" {cJobDir}/{CutArgs.title}.y{item}X.calc.job')
                os.system(f'cd {cJobDir} && condor_submit {CutArgs.title}.y{item}X.calc.job')
                l.log(f' - Current y{item} with RefMult3X')

    if CutArgs.ptScan:
        for idx, item in enumerate(CutArgs.pTRange):
            l.log('For pT scan:')
            l.log(f'Item {idx+1:03d} - pt{item}')

            if True:
                cJobDir = f'{runDir}/pt{item}X'
                if not os.path.exists(f'{cJobDir}'):
                    os.mkdir(f'{cJobDir}')
                if not os.path.exists(f'{cJobDir}/runCumulant'):
                    os.symlink(CutArgs.calc_exec, f'{cJobDir}/runCumulant')
                if not os.path.exists(f'{cJobDir}/cent_edge.txt'):
                    os.symlink(f'{msDir}/cent_edgeX.txt', f'{cJobDir}/cent_edge.txt')
                if not os.path.exists(f'{cJobDir}/Npart.txt'):
                    os.symlink(f'{msDir}/NpartX.txt', f'{cJobDir}/Npart.txt')
                if not os.path.exists(f'{cJobDir}/w8.txt'):
                    os.symlink(f'{msDir}/w8X.txt', f'{cJobDir}/w8.txt')
                if os.path.exists(f'{cJobDir}/{CutArgs.title}.pt{item}X.root'):
                    os.remove(f'{cJobDir}/{CutArgs.title}.pt{item}X.root')
                os.symlink(f'{mergeDir}/{CutArgs.title}.pt{item}X.root', f'{cJobDir}/{CutArgs.title}.pt{item}X.root')
                os.system(f'cp calc.sh {cJobDir}/{CutArgs.title}.pt{item}X.calc.sh')
                os.system(f'cp calc.job {cJobDir}/{CutArgs.title}.pt{item}X.calc.job')
                os.system(f'sed -i "s|TASKNAME|{CutArgs.title}.pt{item}X|g" {cJobDir}/{CutArgs.title}.pt{item}X.calc.sh')
                os.system(f'sed -i "s|SHELLNAME|{CutArgs.title}.pt{item}X.calc.sh|g" {cJobDir}/{CutArgs.title}.pt{item}X.calc.job')
                os.system(f'sed -i "s|TASKNAME|{CutArgs.title}.pt{item}X|g" {cJobDir}/{CutArgs.title}.pt{item}X.calc.job')
                os.system(f'cd {cJobDir} && condor_submit {CutArgs.title}.pt{item}X.calc.job')
                l.log(f' - Current pt{item} with RefMult3X')
        
    l.log('All submitted!')

# collect mode
if mode == 'collect':
    mergeDir = f'{CutArgs.mergeDir}/Iter2'
    runDir = CutArgs.runDir

    if not os.path.exists(mergeDir):
        raise Exception(f'[ERROR] {mergeDir=} which does not exist.')

    if not os.path.exists(runDir):
        raise Exception(f'[ERROR] {runDir=} which does not exist.')
    
    l.log('Here are the task names to be collected:')
    if CutArgs.yScan:
        l.log(f'Rapidity scan is [ON]:')
        for idx, item in enumerate(CutArgs.yRange):
            l.log(f'Item {idx+1:03d} - y{item}')
    if CutArgs.ptScan:
        l.log(f'pT scan is [ON]:')
        for idx, item in enumerate(CutArgs.pTRange):
            l.log(f'Item {idx+1:03d} - pt{item}')

    col = f'{CutArgs.title}.coll'

    if os.path.exists(col):
        l.log(f'Already have {col} now removing it.')
        os.system(f'rm -rf {col}')
    
    os.mkdir(col)
    if CutArgs.yScan:
        for item in CutArgs.yRange:
            os.system(f'cp {mergeDir}/{CutArgs.title}.y{item}.pDist.root {col}/')
            os.system(f'cp {runDir}/y{item}X/cum.cbwc.{CutArgs.title}.y{item}X.root {col}/')
    if CutArgs.ptScan:
        for item in CutArgs.pTRange:
            os.system(f'cp {mergeDir}/{CutArgs.title}.pt{item}.pDist.root {col}/')
            os.system(f'cp {runDir}/pt{item}X/cum.cbwc.{CutArgs.title}.pt{item}X.root {col}/')
    
    if os.path.exists(f'{col}.tgz'):
        l.log(f'Already have {col}.tgz now removing it.')
        os.remove(f'{col}.tgz')
    os.system(f'tar -zcvf {col}.tgz {col}/')
    l.log(f'All done. See {col} and {col}.tgz')

# clean mode
if mode == 'clean':
    if len(sys.argv) != 3:
        l.log(f'Clean All: It is dangerous! This function is forbiden!')
    else:
        clcmd = sys.argv[2]
        if clcmd not in ['out', 'merge', 'run', 'calc']:
            raise Exception(f'[ERROR] Clean Mode support the following command: out merge run calc. Received: {clcmd}')
        if clcmd == 'out':
            l.log(f'Need safe word, please input CONFIRM and continue:')
            k = input()
            if k == 'CONFIRM':
                outDir = CutArgs.outDir
                l.log(f'Now we are trying to clean {outDir}.')
                os.system(f'rm -rf {outDir}')
                l.log(f'Removed.')
            else:
                l.log(f'Safe word was not accepted, canceled.')
        elif clcmd == 'merge':
            l.log(f'Need safe word, please input CONFIRM and continue:')
            k = input()
            if k == 'CONFIRM':
                mergeDir = CutArgs.mergeDir
                l.log(f'Now we are trying to clean {mergeDir}.')
                os.system(f'rm -rf {mergeDir}')
                l.log(f'Removed.')
            else:
                l.log(f'Safe word was not accepted, canceled.')
        elif clcmd in ['run', 'calc']:
            l.log(f'Need safe word, please input CONFIRM and continue:')
            k = input()
            if k == 'CONFIRM':
                runDir = CutArgs.runDir
                l.log(f'Now we are trying to clean {runDir}.')
                os.system(f'rm -rf {runDir}')
                l.log(f'Removed.')
            else:
                l.log(f'Safe word was not accepted, canceled.')
        else:
            l.log('Nothing happend. But I don\'t think you can see this in log file.')

# report mode
if mode == 'report':
    l.log('Manager System: Task Report')
    l.log(f'Current verion of manager: {__version__} ({__updatedTime__})')
    l.log(f'Energy: {CutArgs.energy}')
    l.log(f'Task Name: {CutArgs.title}')
    
    l.log(f'# General Information')
    l.log(f'\tnHitsFit cut: {CutArgs.nHitsFit}')
    l.log(f'\tnSigma cut: {CutArgs.nSig}')
    l.log(f'\tDCA cut: {CutArgs.dca}')
    l.log(f'\tmass square cut: {CutArgs.m2Min} -> {CutArgs.m2Max}')
    if CutArgs.yScan:
        l.log(f'\tRapidity scan is [ON] with {len(CutArgs.yRange)} tasks.')
        l.log(f'\tDuring rapidity scan, pT range will be [{CutArgs.ptMin}, {CutArgs.ptMax}].')
        for i, item in enumerate(CutArgs.yRange):
            l.log(f'\t {i+1:02d}) {item} {CutArgs.yRange[item][0]} -> {CutArgs.yRange[item][1]} (mode {CutArgs.yRange[item][2]}) Vz: {CutArgs.yRange[item][3]} -> {CutArgs.yRange[item][4]}')
    else:
        l.log(f'\tRapidity scan is [OFF].')
    if CutArgs.ptScan:
        l.log(f'\tpT scan is [ON] with {len(CutArgs.pTRange)} jobs.')
        l.log(f'\tDuring pT scan, y range will be [{CutArgs.yMin}, {CutArgs.yMax}].')
        for i, item in enumerate(CutArgs.pTRange):
            l.log(f'\t {i+1:02d}) {item} {CutArgs.pTRange[item][0]} -> {CutArgs.pTRange[item][1]} Vz: {CutArgs.pTRange[item][2]} -> {CutArgs.pTRange[item][3]}')
    
    if os.path.exists(CutArgs.outDir):
        l.log(f'# GetTerms: [E]')
        l.log(f'\tJobs are here: {CutArgs.outDir}')
        l.log('\tThe directory exists, which means we are done or doing this step.')
    else:
        l.log(f'# GetTerms: [D]')
        l.log(f'\tJobs are here: {CutArgs.outDir}')
        l.log('\tThe directory does not exist, which means it has not got started or is removed already.')
    l.log(f'\tFile list is: {CutArgs.fileList} ({nFiles} files).')
    l.log(f'\t{nJobs} jobs are dispatched for processing {nFilesPerJob} files.')
    if bonus:
        l.log(f'\tBesides, there is one bonus job which will process {bonus} files.')
    l.log(f'\tMaybe we are changing nSigma for systematic uncertainty calculations, the tag is: {CutArgs.nSigmaTag}')

    if os.path.exists(CutArgs.mergeDir): # has merge folder
        if os.path.exists(f'{CutArgs.mergeDir}/Iter1'): # has iter 1
            if os.path.exists(f'{CutArgs.mergeDir}/Iter2'): # has iter 2
                l.log(f'# Merge: [2]')
                l.log(f'\t2-iteration jobs are here: {CutArgs.mergeDir}/Iter2')
                l.log('\tThe directory exists, which means we are done or doing this step.')
            else : # has not iter 2
                l.log(f'# Merge: [1]')
                l.log(f'\t1-iteration jobs are here: {CutArgs.mergeDir}/Iter1')
                l.log('\tThe directory exists, which means we are done or doing this step.')
                l.log('\tNext step might be merge iteration 2')
        else: # has not iter 1
            if os.path.exists(f'{CutArgs.mergeDir}/Iter2'): # has iter 2
                l.log(f'# Merge: [0]')
                l.log(f'\tOne-term merging jobs are here: {CutArgs.mergeDir}/Iter2')
                l.log('\tThe directory exists, which means we are done or doing this step.')
            else : # has not iter 2
                l.log(f'# Merge: [E]')
                l.log(f'\tJobs are here: {CutArgs.mergeDir}')
                l.log('\tThe directory exists, but iteration folders do not exist, which means we haven\'t started it or they have been removed')
    else: # removed
        l.log(f'# Merge: [D]')
        l.log(f'\tJobs are here: {CutArgs.mergeDir}')
        l.log('\tThe directory does not exist, which means it has not got started or is removed already.')

    if os.path.exists(CutArgs.runDir):
        l.log(f'# Calculation: [E]')
        l.log(f'\tJobs are here: {CutArgs.runDir}')
        l.log('\tThe directory exists, which means we are done or doing this step.')
    else:
        l.log(f'# Calculation: [D]')
        l.log(f'\tJobs are here: {CutArgs.runDir}')
        l.log('\tThe directory does not exist, which means it has not got started or is removed already.')
    l.log(f'\tThe executable file: {CutArgs.calc_exec}')
    l.log(f'Generated files for manger system can be found at: {CutArgs.targetDir}/ManagerSystem')
    
    l.log('This is the end of report.')