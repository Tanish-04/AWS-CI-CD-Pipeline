import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_ci_cd_pipeline.aws_ci_cd_pipeline_stack import AwsCiCdPipelineStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_ci_cd_pipeline/aws_ci_cd_pipeline_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsCiCdPipelineStack(app, "aws-ci-cd-pipeline")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })

def test_alarm():
    app = core.App()
    stack = AwsCiCdPipelineStack(app, "aws_ci_cd_pipeline")
    template = assertions.Template.from_stack(stack)
    template.has_resource_properties(
        "AWS::CloudWatch::Alarm",
                    {"EvaluationPeriods":1}
    )
    

def test_lambda_count():
    app = core.App()
    stack = AwsCiCdPipelineStack(app, "aws_ci_cd_pipeline")
    template = assertions.Template.from_stack(stack)
    template.resource_count_is(
        "AWS::Lambda::Function",2)

def test_subscription_count():
    app = core.App()
    stack = AwsCiCdPipelineStack(app, "aws_ci_cd_pipeline")
    template = assertions.Template.from_stack(stack)
    template.resource_count_is("AWS::SNS::Subscription",
                      2
                    )

