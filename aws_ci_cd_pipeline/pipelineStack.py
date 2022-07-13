from aws_cdk import (
    # Duration,
    Stack,
    pipelines,
    SecretValue,
    aws_codepipeline_actions as actions,
    # aws_sqs as sqs,
)
from constructs import Construct

from Stage import TanishStage


class MyPipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # defining my source first

        source = pipelines.CodePipelineSource.git_hub('Tanish-04/AWS-CI-CD-Pipeline', 'master',
                                                      authentication=SecretValue.secrets_manager(
                                                          'my-cicd-token'),
                                                      trigger=actions.GitHubTrigger(value="POLL"))

        # Build my code with ShellStep

        synth = pipelines.ShellStep("TanishSynth",
                                    input=source,
                                    commands=[
                                        'cd AWS-CI-CD-PIPELINE', 'npm install -g aws-cdk', 'pip install - r requirements.txt', 'cdk synth'],
                                    primary_output_directory='AWS-CI-CD-PIPELINE/cdk.out/'
                                    )

        # Unit test into the pipeline
        unit_test = pipelines.ShellStep("TanishUnitTest",
        commands=["cd AWS-CI-CD-PIPELINE",
        "pip3 install -r requirements.txt",
        "pip3 install pytest",
        "pytest"])

        # Creating my pipeline
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.pipelines/CodePipeline.html

        myPipeline = pipelines.CodePipeline(self, "TanishPipeline",
                                            synth=synth,
                                            )

        # Creating stages

        betaStage = TanishStage(self, "BetaStage")
        prodStage = TanishStage(self, "ProdStage")


        #https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.pipelines/README.html
        
        # Adds stages to the pipeline
        myPipeline.addStage(betaStage, pre=['unittest'])
        myPipeline.addStage(prodStage, pre=[pipelines.ManualApprovalStep("Need Approval!")])
