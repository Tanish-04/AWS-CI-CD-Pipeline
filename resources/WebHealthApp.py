import urllib3
import datetime
import constants as constants
from CloudWatches_putmatrix import cloudWatchPutMetrix



def lambda_handler(event, context):

    """
    This function returns if our response was successful or not by returning boolean values
    
    :Args event: triggered event, Event can be treated as an input of the functions
        context: During running of the program, it passes context object to the handler

    :return: return boolean value 
    """
    cw = cloudWatchPutMetrix()
    values = dict()

    for monitor_url in constants.MONITOR_URL:
            
        dimensions = [{'Name' : 'url', 'Value': monitor_url}]
        availability = get_availability(monitor_url)
        cw.put_data(constants.URL_MONITOR_NAMESPACE,constants.URL_MONITOR_METRIC_NAME_AVAILABILITY,dimensions, availability)


        latency = get_latency(monitor_url)     
        cw.put_data(constants.URL_MONITOR_NAMESPACE,constants.URL_MONITOR_METRIC_NAME_LATENCY,dimensions, latency)
    
        values.update({'availability': availability, "Latency": latency})
    return values

def get_availability(url):
    
    """
    This function returns if our response was successful or not by returning boolean values
    
    :Args:  This function takes no argument

    :return: return boolean value 
    """

    http = urllib3.PoolManager()
    #for link in constants.MONITOR_URL:
    response = http.request("GET", url)
    
    if response.status == 200:
        return 1
    else:
        return 0

def get_latency(url):
    """
    This function returns the latency (Time taken to give us response) of that website where we send our request
    
    :Args:  This function takes no argument

    :return: return the float value of latency in seconds
    """
    http = urllib3.PoolManager()
    start = datetime.datetime.now()
    #for link in constants.MONITOR_URL:
    response = http.request("GET", url)
    end = datetime.datetime.now()
    duration = end - start
    latency = round(duration.microseconds * .000001,6)
    return latency
