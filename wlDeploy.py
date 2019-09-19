from re import findall
from os import listdir
from os.path import splitext
from os import getenv

deploymentTarget = getenv("targetnode")
domainName = getenv("domainEnv")
username = getenv("uname")
password = getenv("pword")
wlUrl = getenv("url")
appLocation = getenv("appLoc")

filenames = []
lstWOExt = []

for files in listdir(appLocation):
    if files.endswith('.war'):
        filenames.append(files)
print(filenames)

for filext in filenames:
    lstWOExt.append(splitext(filext)[0])
print(lstWOExt)

if not listdir(appLocation):
    print('War file directory is empty. Nothing to deploy...')
else:
    print('There are war files in this directory')
    for file in lstWOExt:
        deploymentFile = ''+appLocation+'\\'+file+'.war'
        try:
            print('Trying to connect with '+domainName+'')
            connect(username, password, wlUrl)
            print('Successfully connected with '+domainName+'')
        except:
            print('Couldn\'t successfully connect with '+domainName+'...')

        appList = findall(file, ls('/AppDeployments'))
        if len(appList) >= 1:
            print('=' * 100)
            print(''+file+' found on '+deploymentTarget+'. Hence, undeploying it...')
            print('=' * 100)
            try:
                print('Trying to stop '+file+' in '+deploymentTarget+'...')
                stopApplication(file, targets=deploymentTarget)
                print('+' * 100)
                print('Successfully stopped '+file+' in '+deploymentTarget+'!')
                print('+' * 100)
            except:
                print('couldn\'t stop '+file+'...')
            try:
                print('Now we will try to undeploy '+file+' in '+deploymentTarget+'...')
                undeploy(file, deploymentFile, targets=deploymentTarget)
                print('+' * 100)
                print('Successfully undeployed '+file+' in '+deploymentTarget+'!')
                print('+' * 100)
            except:
                print('Couldn\'t undeploy '+file+'')
                print('=' * 100)
                print('Redeploying '+file+' on '+deploymentTarget+'')
                print('=' * 100)
                #deployApp()
            try:
                print('Trying to deploy '+file+' in '+deploymentTarget+'...')
                edit()
                startEdit()
                deploy(file, deploymentFile, targets=deploymentTarget)
                activate()
                startApplication(file)
                print('+' * 100)
                print('Successfully started '+file+' in '+deploymentTarget+'!')
                print('+' * 100)
            except:
                print('Unable to start '+file+'')
                exit()

        else:
            print('=' * 100)
            print('There is no such app. Hence, deploying dpplication '+file+' on'+deploymentTarget+'...')
            print('=' * 100)
            try:
                print('Trying to deploy '+file+'...')
                edit()
                startEdit()
                deploy(file, deploymentFile, targets=deploymentTarget)
                activate()
                startApplication(file)
                print('+' * 100)
                print('Successfully started '+file+' in '+deploymentTarget+'!')
                print('+' * 100)
            except:
                print('Unable to start '+file+'')
                exit()