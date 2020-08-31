def ALL_ENV_TAGS =  ["-s", "-m"]
def inputTC
def inputENV
def inputSorM


pipeline {
  agent any
  stages {
    stage("test") {
            steps {
                script {
                def userInput = input(
                 id: 'userInput', message: 'Parameters', 
                 parameters: [
                 [$class: 'ChoiceParameterDefinition', description: 'Stream or Module?', choices: ALL_ENV_TAGS.join('\n'), name:'FLAG'],
                 [$class: 'TextParameterDefinition',  description: 'Stream or Module Name', name: 'TC'],
                 [$class: 'TextParameterDefinition',  description: 'Environment Name', name: 'ENV']
                ])
                

                inputTC = userInput.TC?:''
                inputENV = userInput.ENV?:''
                inputSorM = userInput.FLAG?:''


                echo ("Stream or Module: "+inputSorM)
                echo ("Stream or Module: "+inputTC)
                echo ("Environment: "+inputSorM)
                sh 'python -u "source/tests.py" ' +  inputSorM + ' ' + inputTC + ' -e ' + inputENV


                }
            }
          }
       }
    }
  

