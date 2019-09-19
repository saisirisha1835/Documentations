node('jenkins_fcrs_84'){
    
    try{
        deleteDir()
        
        def build_ok = true
        
        stage('Checkouts'){
            parallel 'sources':{
                try{
                    stage('source code'){
                        echo 'Checking out source code...'
                        checkout([$class: 'SubversionSCM', additionalCredentials: [], excludedCommitMessages: '', excludedRegions: '', excludedRevprop: '', excludedUsers: '', filterChangelog: false, ignoreDirPropChanges: false, includedRegions: '', locations: [[cancelProcessOnExternalsFail: true, credentialsId: 'FCRS', depthOption: 'infinity', ignoreExternalsOption: true, local: 'source_code', remote: 'https://mlxsdgsvn.icicibankltd.com/svn/BT3_120_FinancialConglomerateReportingSystem_FCRS_/120-FCRS/SourceCode/${folderName}/${modName}']], quietOperation: true, workspaceUpdater: [$class: 'UpdateUpdater']])
                        echo 'Successfully checkout source code repo!'
                    }
                }catch(err){
                    echo 'Unable to checkout sources repo...'
                    currentBuild.result = "FAILURE"
                    error()
                }
            }, 'rel-notes':{
                try{
                    stage('release note'){
                        echo 'Checking out release note repo...'
                        checkout([$class: 'SubversionSCM', additionalCredentials: [], excludedCommitMessages: '', excludedRegions: '', excludedRevprop: '', excludedUsers: '', filterChangelog: false, ignoreDirPropChanges: false, includedRegions: '', locations: [[cancelProcessOnExternalsFail: true, credentialsId: 'FCRS', depthOption: 'infinity', ignoreExternalsOption: true, local: 'release_note', remote: 'https://mlxsdgsvn.icicibankltd.com/svn/BT3_120_FinancialConglomerateReportingSystem_FCRS_/120-FCRS/ReleaseNotes']], quietOperation: true, workspaceUpdater: [$class: 'UpdateUpdater']])
                        echo 'Successfully checked out release note repo!'
                    }
                }catch(err){
                    echo 'Unable to checkout release note repo...'
                    currentBuild.result = "FAILURE"
                    error()
                }
            }
        }
        
        /*stage('CR-Echo'){
            bat label: '', script: 'copy "%WORKSPACE%\\release_note\\120_FCRS_ReleaseNote_%CRN%.xls" "C:\\Users\\op_2150\\Desktop\\dummy\\"'
        }*/
        
        try{
            stage('Compilation'){
                println "Now proceeding for source compilation using MSBuild executable"
                bat label: 'msbuild-step', script: '%Framework% %SLN% /p:Configuration=Debug /p:AllowUntrustedCertificate=True /p:CreatePackageOnPublish=True'
                successfulBuildTransitionIssue()
                CIP2DepTransitionIssue() 
            }
        }catch(err){
            println("Unable to compile...there were some errors!")
            currentBuild.result = "FAILURE"
            unsuccessfulBuildTransitionIssue()
            error()
            
        }
        
        try{
            stage('ReSharper Analysis'){
                println 'Now performing code inspection'
                bat label: 'code-inspection-check', script: '%INS_CODE% "%WORKSPACE%\\%SLN%" -output="%WORKSPACE%\\source_code\\inspector.xml"'
                println 'Now performing code duplication checks'
                bat label: 'code-duplication-check', script: '%DUP_CODE% "%WORKSPACE%\\%SLN%" -output="%WORKSPACE%\\source_code\\dupchecks.xml"'
            }
        } catch (err){
            println('There were some problems in performing code inspection checks')
            currentBuild.result = "FAILURE"
            error()
        }
        
        try{
            stage('ReSharper Quality Gates'){
                println 'Now trying to generate human-readable report analysis'
                recordIssues ignoreFailedBuilds: false, qualityGates: [[threshold: 50, type: 'TOTAL', unstable: true], [threshold: 50, type: 'NEW', unstable: true]], tools: [resharperInspectCode(pattern: 'source_code\\inspector.xml'), dupFinder(pattern: 'source_code\\dupchecks.xml')]
            }
        } catch (err){
            println 'There were problems in creating human readable reports!'
            currentBuild.result = "FAILURE"
            error()
	        createJira()
        }
        
        stage('Approval to Proceed?'){
            input(id: '100', message: 'Continue post code analysis stage?', ok: 'Approved', submitter: '\'Administrator\'', submitterParameter: 'approvalAuth')
        }
        
        try{
            stage('NUnit3'){
                build 'FCRS-SDG/NUnitExec'
            }
        }catch(err){
            echo "There are some errors in your unit tests!"
            build_ok = false
            echo err.toString()
            currentBuild.result = "FAILURE"
            createJira()
        }
        
        stage('Approval to Proceed?'){
            input(id: '100', message: 'Continue post unit test stage?', ok: 'Approved', submitter: '\'Administrator\'', submitterParameter: 'approvalAuth')
        }
        
        try {
            stage('CherryPicker-Backup'){
                println 'Making a directory for backup in desktop...'
                bat label: '', script: 'mkdir "%DSK%\\Bkp_Jenkins_%BUILD_TIMESTAMP%"'
                println('backing up current files')
                bat label: 'backup-phase', script: '%CP% --path "%WORKSPACE%\\release_note\\120_FCRS_ReleaseNote_%CRN%.xls" --workspace "%iisPath%"'
                //bat label: 'backup-phase', script: 'G:\\cherrypicker.exe --path "%WORKSPACE%\\release_note\\120_FCRS_ReleaseNote_%CRN%.xls" --workspace "%iisPath%"'
                println('backup done...')
                println 'Now extracting the impact file zip for ms deploy rollback purposes'
                bat label: 'unzip-bkp', script: '%UZP% --path "%IMPF%\\%CRN%"'
                println('Renaming the file before uploading to Nexus')
                bat label: 'move-ren', script: 'move "%IMPF%\\%CRN%\\*.zip" %WORKSPACE%\\source_code\\patch_bkp.zip'
                println 'Renaming of backup patch folder'
                bat label: 'patch-ren-phase', script: '%RNBKPBAT% %CRN%'
                println 'Moving the backup patch to backup folder...'
                bat label: 'move-bkp', script: 'move "%IMPF%\\%CRN%\\patch_backup" "%DSK%\\Bkp_Jenkins_%BUILD_TIMESTAMP%"'
                echo 'uploading backup to backup repo in nexus...'
                nexusArtifactUploader artifacts: [[artifactId: 'FCRS', classifier: '', file: 'source_code\\patch_bkp.zip', type: 'zip']], credentialsId: 'NexusRepoSDG', groupId: 'com.icicibank.backup.sdg', nexusUrl: '10.75.21.109:9043/repository/fcrs-backup/', nexusVersion: 'nexus3', protocol: 'http', repository: 'fcrs-backup', version: '$BUILD_TIMESTAMP'
                echo 'backup done'
            }
        }catch(err){
            println('Unable to selectively pick the backup file')
            currentBuild.result = "FAILURE"
            error()
        }
        
        try{
            stage("CherryPicker"){
                echo 'Now proceeding with selective file picking'
                bat label: 'file-pick', script: '%CP% --path "%WORKSPACE%\\release_note\\120_FCRS_ReleaseNote_%CRN%.xls" --workspace "%WORKSPACE%\\source_code\\IUI"'
                //bat label: 'file-pick', script: '"G:\\cherrypicker.exe" --path "%WORKSPACE%\\release_note\\120_FCRS_ReleaseNote_%CRN%.xls" --workspace "%WORKSPACE%\\source_code\\IUI"'
                echo 'Now extracting the compressed file..'
                bat label: 'unzip', script: '%UZP% --path "%IMPF%\\%CRN%"'
                echo 'Move the zip file to another location'
                bat label: 'move-ren', script: 'move "%IMPF%\\%CRN%\\*.zip" %WORKSPACE%\\source_code\\patch.zip'
                echo 'Performing pre-deployment ops...'
                bat label: 'patch-ren-phase', script: '%RNBAT% %CRN%'
                echo 'Uploading to Nexus...'
                nexusArtifactUploader artifacts: [[artifactId: 'FCRS', classifier: '', file: 'source_code\\patch.zip', type: 'zip']], credentialsId: 'NexusRepoSDG', groupId: 'com.icicibank.sdg', nexusUrl: '10.75.21.109:9043/repository/FCRS/', nexusVersion: 'nexus3', protocol: 'http', repository: 'FCRS', version: '$CRN-$BUILD_TIMESTAMP'
                echo 'Upload to nexus done...'
            }
        }catch(err){
            echo 'Unable to selectively pick the file'
            currentBuild.result = "FAILURE"
            error()
        }
            
        stage("Deploy Approval"){
            input(id: '100', message: 'Continue with the Deployment?', ok: 'Approved', submitter: '\'Administrator\'', 
            submitterParameter: 'approvalAuth')
        }
        
        try{
            stage('Deployment'){
                echo 'Trying to deploy release patch...'
                bat label: 'deploy-phase', script: '''"%MSD%" -verb:sync -source:contentPath="%IMPF%\\%CRN%\\patch" -dest:contentPath="%iisPath%",computerName="https://JPRDEVOPSDB01:8172/msdeploy.axd",UserName=\'op_2150\',Password=\'admin@123\',AuthType=\'Basic\' -enableRule:DoNotDeleteRule -allowUntrusted:True'''
                println 'DEPLOYMENT IS SUCCESSFUL!'
                currentBuild.displayName = "${env.CRN}-${env.BUILD_TIMESTAMP}"
                echo 'Trying to delete Impact File folder...'
                bat label: '', script: 'rmdir /Q /S "%IMPF%\\%CRN%"'
                bat label: '', script: 'rmdir /Q /S "%DSK%\\Bkp_Jenkins_%BUILD_TIMESTAMP%"'
                //successfulDeployTransitionIssue()
                //FTA2TestTransitionIssue()
            }
        }catch(err){
            echo 'Deployment of release patch has somehow not worked...'
            echo 'Now applying the backup to IIS Site'
            bat label: 'rollback-apply-phase', script: '''"%MSD%" -verb:sync -source:contentPath="%DSK%\\Bkp_Jenkins_%BUILD_TIMESTAMP%\\patch_backup" -dest:contentPath="%iisPath%",computerName="https://JPRDEVOPSDB01:8172/msdeploy.axd",UserName=\'op_2150\',Password=\'admin@123\',AuthType=\'Basic\' -enableRule:DoNotDeleteRule -allowUntrusted:True'''
            echo 'Trying to delete backup patch files...'
            bat label: '', script: 'rmdir /Q /S "%DSK%\\Bkp_Jenkins_%BUILD_TIMESTAMP%"'
            bat label: '', script: 'rmdir /Q /S "%IMPF%\\%CRN%"'
            currentBuild.result = "FAILURE"
            //unsuccessfulDeployTransitionIssue()
            error()
            
        }
        
        /*try{
            stage('FTA'){
                build 'FCRS-SDG/FCRS_FTA'
               successfulTestTransitionIssue()
            }
        }catch(err){
            echo "There are some errors in your FTA tests!"
            currentBuild.result = "FAILURE"
            createJira()
            unsuccessfulTestTransitionIssue()
        }*/
        
        stage('Test Automation'){
            parallel 'FTA':{
                try{
                    stage('Functional Testing'){
                        build 'FCRS-SDG/FCRS_FTA'
                        //successfulTestTransitionIssue()
                    }
                }catch(err){
                    echo 'Unable to checkout sources repo...'
                    build_ok = false
                    echo err.toString()
                    currentBuild.result = "FAILURE"
                    //createJira()
                }
            }, 'API TA':{
                try{
                    stage('API Testing'){
                        build 'FCRS-SDG/FCRS_APIS'
                        //successfulTestTransitionIssue()
                    }
                }catch(err){
                    echo 'There were some failures in API test automation'
                    echo err.toString()
                    currentBuild.result = "FAILURE"
                    build_ok = false
                    //createJira()
                }
            }
        }
        
        stage('Post TA Approval'){
            input(id: '100', message: 'Continue post TA?', ok: 'Approved', submitter: '\'Administrator\'', 
            submitterParameter: 'approvalAuth')
        }
        
        stage('UAT'){
            echo 'UAT in progress'
        }
        
        if(build_ok) {
            currentBuild.result = "SUCCESS"
        } else {
            currentBuild.result = "FAILURE"
        }
       
    }catch(err){
        echo "=================ERROR: ${err}"
        currentBuild.displayName = "${env.CRN}-${env.BUILD_TIMESTAMP}"
        currentBuild.result = "FAILURE"
        error()  
    }
}

def createJira(){
    withEnv(['JIRA_SITE=JIRA Pipeline UAT']){
        def failIssue = [fields: [project: [id: 10607],
                        summary: ''+CRN+' Jenkins execution bug',
                        description: ''+CRN+ ' has failed. Please do the needful',
                        issuetype: [name: 'Bug']]]
        response = jiraNewIssue issue: failIssue
        echo response.successful.toString()
        echo response.data.toString()
    }
}

def successfulBuildTransitionIssue(){
    withEnv(['JIRA_SITE=JIRA Pipeline UAT']){
        def searchResults = jiraJqlSearch jql: "project = 'SDG-FCRS' AND Sprint = 355 AND statusCategory = 'In Progress' AND status = 'Jenkins DEV WIP'"
        def issues = searchResults.data.issues
        def comment = [ body: 'Comment from Jenkins. Positive transition for %BUILD_DISPLAY_NAME%' ]
        for (i = 0; i <issues.size(); i++) {
            def transitionInput = [
                transition: [
                    id: '91'
                ]
            ]
            jiraTransitionIssue idOrKey: issues[i].key, input: transitionInput
            jiraAddComment idOrKey: issues[i].key, input: comment
        }
    }
}

def unsuccessfulBuildTransitionIssue(){
    withEnv(['JIRA_SITE=JIRA Pipeline UAT']){
        def searchResultsQuery = jiraJqlSearch jql: "project = 'SDG-FCRS' AND Sprint = 355 AND statusCategory = 'In Progress' AND status = 'Jenkins DEV WIP'"
        def issueNos = searchResultsQuery.data.issues
        def comment = [ body: 'Comment from Jenkins. Negative transition for %BUILD_DISPLAY_NAME%!' ]
        for (i = 0; i < issueNos.size(); i++){
            def transInput = [
                transition: [
                    id: '101'
                ]
            ]
            jiraTransitionIssue idOrKey: issueNos[i].key, input: transInput
            jiraAddComment idOrKey: issueNos[i].key, input: comment
        }
    }
}

def CIP2DepTransitionIssue(){
    withEnv(['JIRA_SITE=JIRA Pipeline UAT']){
        def searchResults = jiraJqlSearch jql: "project = 'SDG-FCRS' AND Sprint = 355 AND statusCategory = 'Done' AND status = 'CI Pass'"
        def issues = searchResults.data.issues
        def comment = [ body: 'Comment from Jenkins. Positive transition for deployment in %BUILD_DISPLAY_NAME%!' ]
        for (i = 0; i <issues.size(); i++) {
            def transitionInput = [
                transition: [
                    id: '121'
                ]
            ]
            jiraTransitionIssue idOrKey: issues[i].key, input: transitionInput
            jiraAddComment idOrKey: issues[i].key, input: comment
        }
    }
}

def successfulDeployTransitionIssue(){
    withEnv(['JIRA_SITE=JIRA Pipeline UAT']){
        def searchResults = jiraJqlSearch jql: "project = 'SDG-FCRS' AND Sprint = 355 AND statusCategory = 'In Progress' AND status = 'DEV Deploy WIP'"
        def issues = searchResults.data.issues
        def comment = [ body: 'Comment from Jenkins. Positive transition for deployment in %BUILD_DISPLAY_NAME%!' ]
        for (i = 0; i <issues.size(); i++) {
            def transitionInput = [
                transition: [
                    id: '131'
                ]
            ]
            jiraTransitionIssue idOrKey: issues[i].key, input: transitionInput
            jiraAddComment idOrKey: issues[i].key, input: comment
        }
    }
}

def unsuccessfulDeployTransitionIssue(){
    withEnv(['JIRA_SITE=JIRA Pipeline UAT']){
        def searchResultsQuery = jiraJqlSearch jql: "project = 'SDG-FCRS' AND Sprint = 355 AND statusCategory = 'In Progress' AND status = 'DEV Deploy WIP'"
        def issueNos = searchResultsQuery.data.issues
        def comment = [ body: 'Comment from Jenkins. Negative transition for deployment %BUILD_DISPLAY_NAME%!' ]
        for (i = 0; i < issueNos.size(); i++){
            def transInput = [
                transition: [
                    id: '531'
                ]
            ]
            jiraTransitionIssue idOrKey: issueNos[i].key, input: transInput
            jiraAddComment idOrKey: issueNos[i].key, input: comment
        }
    }
}
    
def FTA2TestTransitionIssue(){
    withEnv(['JIRA_SITE=JIRA Pipeline UAT']){
        def searchResults = jiraJqlSearch jql: "project = 'SDG-FCRS' AND Sprint = 355  AND statusCategory = 'Done' AND status = 'Dev Deploy Pass'"
        def issues = searchResults.data.issues
        def comment = [ body: 'Comment from Jenkins. Positive transition for deployment in %BUILD_DISPLAY_NAME%!' ]
        for (i = 0; i <issues.size(); i++) {
            def transitionInput = [
                transition: [
                    id: '141'
                ]
            ]
            jiraTransitionIssue idOrKey: issues[i].key, input: transitionInput
            jiraAddComment idOrKey: issues[i].key, input: comment
        }
    }
}

def successfulTestTransitionIssue(){
    withEnv(['JIRA_SITE=JIRA Pipeline UAT']){
        def searchResults = jiraJqlSearch jql: "project = 'SDG-FCRS' AND Sprint = 355 AND statusCategory = 'In Progress' AND status = 'Functional Test  WIP'"
        def issues = searchResults.data.issues
        def comment = [ body: 'Comment from Jenkins. Positive transition for %BUILD_DISPLAY_NAME%' ]
        for (i = 0; i <issues.size(); i++) {
            def transitionInput = [
                transition: [
                    id: '151'
                ]
            ]
            jiraTransitionIssue idOrKey: issues[i].key, input: transitionInput
            jiraAddComment idOrKey: issues[i].key, input: comment
        }
    }
}

def unsuccessfulTestTransitionIssue(){
    withEnv(['JIRA_SITE=JIRA Pipeline UAT']){
        def searchResultsQuery = jiraJqlSearch jql: "project = 'SDG-FCRS' AND Sprint = 355  AND statusCategory = 'In Progress' AND status = 'Functional Test  WIP'"
        def issueNos = searchResultsQuery.data.issues
        def comment = [ body: 'Comment from Jenkins. Negative transition for %BUILD_DISPLAY_NAME%!' ]
        for (i = 0; i < issueNos.size(); i++){
            def transInput = [
                transition: [
                    id: '161'
                ]
            ]
            jiraTransitionIssue idOrKey: issueNos[i].key, input: transInput
            jiraAddComment idOrKey: issueNos[i].key, input: comment
        }
    }
}


