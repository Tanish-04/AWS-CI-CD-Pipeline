from aws_cdk import (
    Duration,
    Stack,
    aws_lambda as lambda_,
    aws_events as events_,
    aws_events_targets as targets_,
    aws_iam as iam_,
    aws_cloudwatch as cloudwatch_,
    aws_sns as sns_,
    RemovalPolicy,
    aws_sns_subscriptions as subscriptions_,
    aws_cloudwatch_actions as CWActions,
    aws_dynamodb as db_,
    # aws_sqs as sqs,
)
from constructs import Construct
from resources import constants as constants


class AwsCiCdPipelineStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.lambda_role = self.create_lambda_role()
        WHLambda = self.create_lambda(
            'TanishWebHealthLambda', './resources', 'WebHealthApp.lambda_handler')
        # Lambda is stateful resource
        # When we destroy infrastructure, lambda function doesn't destroy, we have to explicitly write below line for stateful resources
        # Below line tells us that when our infrastructure destroyed, also destroyed our Lambda
        WHLambda.apply_removal_policy(RemovalPolicy.DESTROY)

        metricDuration = WHLambda.metric_duration()
        metricErrors = WHLambda.metric_errors()

        # Last requirement, Automated rollback if above alarm raised
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_codedeploy/LambdaDeploymentGroup.html

        version = WHLambda.current_version
        alias = lambda_.Alias(self, "TanishLambdaAlias",
            alias_name="Prod",
            version=version
        )

        deployment_group = codedeploy_.LambdaDeploymentGroup(self, "BlueGreenDeployment",
            alias=alias,
            alarms=[errorsAlarm, durationAlarm], 
            deployment_config=codedeploy_.LambdaDeploymentConfig.LINEAR_10_PERCENT_EVERY_1_MINUTE
        ) 


        # DB Lambda function to write data in DynamoDB Table

        # Define event generate
        WHLambdaEvent = events_.Schedule.rate(Duration.minutes(1))
        # Target
        target = targets_.LambdaFunction(WHLambda)
        # Rule
        rule = events_.Rule(self, "LamdaRuleOfEvent",
                            schedule=WHLambdaEvent, targets=[target])

        # Creating cloudwatch metric
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cloudwatch/Metric.html

        for monitor_url in constants.MONITOR_URL:
            dimensions_CW = {'url': monitor_url}

            # Availability Metric
            availMetric = cloudwatch_.Metric(
                metric_name=constants.URL_MONITOR_METRIC_NAME_AVAILABILITY,
                namespace=constants.URL_MONITOR_NAMESPACE,
                dimensions_map=dimensions_CW,
                label="Availability Metric Dashboard",
                period=Duration.minutes(1)
            )

            # Latency Metric
            latencyMetric = cloudwatch_.Metric(
                metric_name=constants.URL_MONITOR_METRIC_NAME_LATENCY,
                namespace=constants.URL_MONITOR_NAMESPACE,
                dimensions_map=dimensions_CW,
                label="Latency Metric Dashboard",
                period=Duration.minutes(1)

            )
            # Alarm creation
            # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cloudwatch/Alarm.html

            # Availability Alarm
            availabilityAlarm = cloudwatch_.Alarm(self, "TanishAvailabilityAlarm" + monitor_url,
                                                  comparison_operator=cloudwatch_.ComparisonOperator.LESS_THAN_THRESHOLD,
                                                  threshold=1,
                                                  evaluation_periods=1,
                                                  metric=availMetric,
                                                  datapoints_to_alarm=1
                                                  )

            # Latency Alarm
            latencyAlarm = cloudwatch_.Alarm(self, "TainshLatencyAlarm"+monitor_url,
                                             comparison_operator=cloudwatch_.ComparisonOperator.GREATER_THAN_THRESHOLD,
                                             threshold=.3,
                                             evaluation_periods=1,
                                             metric=latencyMetric,
                                             datapoints_to_alarm=1,
                                             )
            # Action to take when alarm tiggered
            # Defining alarm actions
            # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_cloudwatch_actions/SnsAction.html
            availabilityAlarm.add_alarm_action(CWActions.SnsAction(topic))
            latencyAlarm.add_alarm_action(CWActions.SnsAction(topic))

        # SNS Topic
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_sns.html
        topic = sns_.Topic(self, "WebHealthNotification")
        # When our infrastructure destroyed, we will also destroy our topic, command written below
        topic.apply_removal_policy(RemovalPolicy.DESTROY)
        topic.add_subscription(subscriptions_.EmailSubscription(
            'tanishkumar473@gmail.com'))
        topic.add_subscription(subscriptions_.LambdaSubscription(dbLambda))

        # Creating a db table
        # https://docs.aws.amazon.com/cdk/api/v1/python/aws_cdk.aws_dynamodb/Table.html
        dbLambda = self.create_lambda(
            'DBLambda', './resources', 'DBApp.lambda_handler')
        dbLambda.apply_removal_policy(RemovalPolicy.DESTROY)

        # Creating table in the name of TanishAlarmTable, and giving full access to the dblambda function so that we add our data
        # in dynamoDB using dblambda function.
        table = db_.Table(self, "TanishAlarmTable",
                          partition_key=db_.Attribute(
                              name="id", type=db_.AttributeType.STRING),
                          removal_policy=RemovalPolicy.DESTROY,
                          )
        table.grant_full_access(dbLambda)
        tableName = table.table_name
        # Setting tableName as a environment variable in dbLambda for table accessing
        dbLambda.add_environment('NameOfTable', tableName)

    def create_lambda(self, id, code, handler):
        """
        Creating lambda function for accessing of application WebHealthApp to get values of latency and availability    
        :Args:
        id: assign unique string
        code: path of the file
        handler: file name along with function name
        :return: function which lambda calling
        """

        return lambda_.Function(self,
                                id=id,
                                code=lambda_.Code.from_asset(code),
                                handler=handler,
                                runtime=lambda_.Runtime.PYTHON_3_9,
                                timeout=Duration.seconds(10),
                                role=self.lambda_role
                                )

    def create_lambda_role(self):
        """
        Created lambda role for assigning full access to the services we want to used.    
        :Args:
        :return: list of all access policies
        """
        lambdaRole = iam_.Role(self, "Lambda-role",
                               assumed_by=iam_.ServicePrincipal(
                                   "lambda.amazonaws.com"),
                               managed_policies=[
                                   iam_.ManagedPolicy.from_aws_managed_policy_name(
                                       'service-role/AWSLambdaBasicExecutionRole'),
                                   iam_.ManagedPolicy.from_aws_managed_policy_name(
                                       'CloudWatchFullAccess'),
                                   iam_.ManagedPolicy.from_aws_managed_policy_name(
                                       'AmazonDynamoDBFullAccess'),
                               ])

        return lambdaRole
