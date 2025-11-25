import os
import sys
from yLog import yLog

taskName = sys.argv[1]
scanName = sys.argv[2]
iterIdx = sys.argv[3]
mergeIdx = sys.argv[4]
fileList = sys.argv[5]
targetDir = sys.argv[6]

l = yLog(f'.{taskName}.iter{iterIdx}.log')

l.log(f'{taskName=}')
l.log(f'{scanName=}')
l.log(f'{iterIdx=}')
l.log(f'{mergeIdx=}') # just to show the merge job index
l.log(f'{fileList=}')
l.log(f'{targetDir=}')

lists = open(fileList).readlines()
lists = [item.strip() for item in lists]
n = len(lists)

baseFile = lists.pop(0)
saveName = f'{taskName}.{scanName}.root'
hadd = '/cvmfs/star.sdcc.bnl.gov/star-spack/spack/opt/spack/linux-rhel7-x86/gcc-4.8.5/root-5.34.38-llsepmmfuwlsucogcwbjiodncxanoudt/bin/hadd'
l.log(f'Now hadd 1 / {n} : {baseFile}')
os.system(f'cp {baseFile} {targetDir}/tmp.{saveName}')
for idx, item in enumerate(lists):
    l.log(f'Now hadd {idx + 2} / {n} : {item}')
    if not os.path.exists(item):
        l.log(f'{item} does not exist, skip!')
        continue
    os.system(f'{hadd} {targetDir}/{saveName} {item} {targetDir}/tmp.{saveName}')
    os.system(f'mv {targetDir}/{saveName} {targetDir}/tmp.{saveName}')
os.system(f'mv {targetDir}/tmp.{saveName} {targetDir}/{saveName}')

l.log('All done.')
