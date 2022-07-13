import boto3

class cloudWatchPutMetrix:
    def __init__(self):
        self.client = boto3.client('cloudwatch')
    
    def put_data(self, nameSpace, metricName, dimension, value):

        """
        This function put our information to the cloudwatch
        :Args 
        nameSpace: we have defined this in constants.py, it will be unique string and will be only 1 in whole project.
        metricName: Metric to published on the cloud, in our app we have only two metrics, which is in constants.py
        dimension: The required filed for this are Name and url values
        value: In dimension, the url latency and availability value is in value parameter

        :return: 
        """
    


        response = self.client.put_metric_data(
            Namespace=nameSpace,
            MetricData=[
                {
                    'MetricName': metricName,
                    'Dimensions': dimension,
                    'Value': value,
                },
            ]
        )