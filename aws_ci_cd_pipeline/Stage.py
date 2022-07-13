from aws_cdk import {

}

from constructs import Construct
from aws_ci_cd_pipeline_stack import AwsCiCdPipelineStack


class TanishStage(Stage):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Instantiate our instance of application stage
        self.stage = CiCdAwsStack(self, 'TanishApplicationInstance')
