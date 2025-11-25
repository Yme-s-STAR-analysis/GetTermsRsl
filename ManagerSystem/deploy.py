import os
import datetime
from conf import Args

DeployArgs = Args()

t = datetime.datetime.now()
print(f'Deploy -> START: {t.ctime()}')

outDir = DeployArgs.outDir
msDir = f'{DeployArgs.targetDir}/ManagerSystem'
jobList = os.listdir(msDir)
jobList = [item for item in jobList if item.endswith('list')]
nJobs = len(jobList)
if os.path.exists(f'{outDir}'):
    os.system(f'rm -rf {outDir}')
os.mkdir(f'{outDir}')
for i in range(nJobs):
    os.mkdir(f'{outDir}/job{i}')
    os.system(f'cp -P {msDir}/getTerms {outDir}/job{i}/getTerms')
    os.system(f'cp {msDir}/{i}.list {outDir}/job{i}/file.list')
    os.system(f'cp {msDir}/cent_edgeX.txt {outDir}/job{i}/cent_edgeX.txt')
    if DeployArgs.yScan:
        for yTag in DeployArgs.yRange:
            # cfg file
            os.symlink(f'{msDir}/{DeployArgs.title}.y{yTag}.getTerms.cfg', f'{outDir}/job{i}/{DeployArgs.title}.y{yTag}.getTerms.cfg')
            # job file
            os.system(f'cp {msDir}/getTerms.job {outDir}/job{i}/{DeployArgs.title}.{i}.y{yTag}.getTerms.job')
            os.system(f'sed -i "s|GTMS|{DeployArgs.title}.{i}.y{yTag}.getTerms.sh|g" {outDir}/job{i}/{DeployArgs.title}.{i}.y{yTag}.getTerms.job')
            os.system(f'sed -i "s|Job|y{yTag}.Job|g" {outDir}/job{i}/{DeployArgs.title}.{i}.y{yTag}.getTerms.job')
            # sh file
            os.system(f'cp {msDir}/getTerms.sh {outDir}/job{i}/{DeployArgs.title}.{i}.y{yTag}.getTerms.sh')
            os.system(f'sed -i "s|TASK_TAG|{DeployArgs.title}.y{yTag}|g" {outDir}/job{i}/{DeployArgs.title}.{i}.y{yTag}.getTerms.sh')
    if DeployArgs.ptScan:
        for pTTag in DeployArgs.pTRange:
            # cfg file
            os.symlink(f'{msDir}/{DeployArgs.title}.pt{pTTag}.getTerms.cfg', f'{outDir}/job{i}/{DeployArgs.title}.pt{pTTag}.getTerms.cfg')
            # job file
            os.system(f'cp {msDir}/getTerms.job {outDir}/job{i}/{DeployArgs.title}.{i}.pt{pTTag}.getTerms.job')
            os.system(f'sed -i "s|GTMS|{DeployArgs.title}.{i}.pt{pTTag}.getTerms.sh|g" {outDir}/job{i}/{DeployArgs.title}.{i}.pt{pTTag}.getTerms.job')
            os.system(f'sed -i "s|Job|pt{pTTag}.Job|g" {outDir}/job{i}/{DeployArgs.title}.{i}.pt{pTTag}.getTerms.job')
            # sh file
            os.system(f'cp {msDir}/getTerms.sh {outDir}/job{i}/{DeployArgs.title}.{i}.pt{pTTag}.getTerms.sh')
            os.system(f'sed -i "s|TASK_TAG|{DeployArgs.title}.pt{pTTag}|g" {outDir}/job{i}/{DeployArgs.title}.{i}.pt{pTTag}.getTerms.sh')

t = datetime.datetime.now()
print(f'Deploy -> END: {t.ctime()}')
