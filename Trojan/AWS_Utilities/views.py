import boto3
import traceback
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from Trojan.settings import PUBLIC_IP
from AWS_Utilities.src.aws_utils import *
from botocore.exceptions import ClientError

def test(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}
    return JsonResponse(response)

# Request:
# - instance_id
#
def instance_start(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    instance_id = request.GET.get('instance_id')

    if instance_id == None:
        instance_id = getInstanceID()

    ec2 = boto3.client('ec2')

    # Do a dryrun first to verify permissions
    try:
        ec2.start_instances(InstanceIds=[instance_id], DryRun=True)
    except ClientError as e:
        if e.response['Error']['Code'] == 'UnauthorizedOperation':
            response['HTTPStatus'] = 'Unauthorized'
            response['HTTPStatusCode'] = '401'
            response['Message'] = 'Dry run failed'
            response['Error'] = e.args[0]

    # Dry run succeeded, call stop_instances without dryrun
    try:
        results = ec2.start_instances(InstanceIds=[instance_id], DryRun=False)
        response.update(results)
    except Exception as e:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - instance_id
#
def instance_stop(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    instance_id = request.GET.get('instance_id')

    if instance_id == None:
        instance_id = getInstanceID()

    ec2 = boto3.client('ec2')

    # Do a dryrun first to verify permissions
    try:
        ec2.stop_instances(InstanceIds=[instance_id], DryRun=True)
    except ClientError as e:
        if e.response['Error']['Code'] == 'UnauthorizedOperation':
            response['HTTPStatus'] = 'Unauthorized'
            response['HTTPStatusCode'] = '401'
            response['Message'] = 'Dry run failed'
            response['Error'] = e.args[0]

    # Dry run succeeded, call stop_instances without dryrun
    try:
        results = ec2.stop_instances(InstanceIds=[instance_id], DryRun=False)
        response.update(results)
    except Exception as e:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
#
def instance_getAll(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    try:
        ec2 = boto3.client('ec2')
        instances = ec2.describe_instances()
        response.update(instances)

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - instance_id
#
def instance_getInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    instance_id = request.GET.get('instance_id')

    try:
        if instance_id == None:
            instance_id = getInstanceID()

        ec2 = boto3.resource('ec2')
        instance = ec2.Instance(instance_id)

        response['instance_id'] = instance.instance_id
        response['instance_public_ip'] = instance.public_ip_address
        response['instance_public_dns_name'] = instance.public_dns_name
        response['instance_private_ip_address'] = instance.private_ip_address
        response['instance_private_dns_name'] = instance.private_dns_name
        response['instance_type'] = instance.instance_type
        response['instance_kernel_id'] = instance.kernel_id
        response['instance_security_groups'] = instance.security_groups
        response['instance_state'] = instance.state
        response['instance_subnet_id'] = instance.subnet_id
        response['instance_tags'] = instance.tags
        response['instance_vpc_id'] = instance.vpc_id
        response['instance_launch_time'] = instance.launch_time

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - namespace
# - name
# - period
#
def cloudwatch_getMetric(request,attempts=0):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    namespace = request.GET.get('namespace')
    name = request.GET.get('name')
    period = request.GET.get('period')

    try:
        client = boto3.client('cloudwatch', region_name='ap-southeast-1')

        endTime = datetime.utcnow()
        startTime = (endTime - timedelta(days=1))
        dimension = getDimension(namespace)

        statistics = client.get_metric_statistics(
            Namespace=namespace,
            MetricName=name,
            Dimensions=[dimension],
            StartTime=startTime.isoformat(),
            EndTime=endTime.isoformat(),
            Period=int(period),
            Statistics=[
                'SampleCount','Average','Sum','Minimum','Maximum',
            ],
        )

        response['metric_dimensions'] = [dimension]
        response['metric_metric_name'] = name
        response['metric_statistics'] = statistics

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - namespace
#
def cloudwatch_getAvailableMetrics(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    namespace = request.GET.get('namespace')

    if namespace == None:
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['message'] = 'Please indicate a namespace (i.e. AWS/EC2)'
        return JsonResponse(response)

    try:
        client = boto3.client('cloudwatch', region_name='ap-southeast-1')
        dimension = getDimension(namespace)

        results = client.list_metrics(
            Namespace=namespace,
            Dimensions=[dimension],
        )

        response['metric_dimensions'] = [dimension]
        response.update(results)

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
#
def loadbalancer_getAll(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    try:
        client = boto3.client('elb')
        loadbalancers = client.describe_load_balancers()
        response.update(loadbalancers)

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - loadbalancer_name
#
def loadbalancer_getInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    loadbalancer_name = request.GET.get('loadbalancer_name')

    try:
        if loadbalancer_name == None:
            loadbalancer_name = getLoadBalancerName()

        client = boto3.client('elb')
        loadbalancers = client.describe_load_balancers(
            LoadBalancerNames=[
                loadbalancer_name,
            ],
        )
        response.update(loadbalancers)

    except Exception as e:
        # traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
#
def loadbalancerV2_getAll(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    try:
        client = boto3.client('elbv2')
        loadbalancers = client.describe_load_balancers()
        response.update(loadbalancers)

    except Exception as e:
        traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)

# Request:
# - loadbalancer_arn
#
def loadbalancerV2_getInfo(request):
    response = {'HTTPStatus':'OK', 'HTTPStatusCode':200}

    loadbalancer_arn = request.GET.get('loadbalancer_arn')

    try:
        if loadbalancer_arn == None:
            loadbalancer_arn = getLoadBalancerID()

        client = boto3.client('elbv2')
        loadbalancers = client.describe_load_balancers(
            LoadBalancerArns=[
                loadbalancer_arn,
            ],
        )
        response.update(loadbalancers)

    except Exception as e:
        # traceback.print_exc()
        response['HTTPStatus'] = 'Bad request'
        response['HTTPStatusCode'] = '400'
        response['Error'] = e.args[0]

    return JsonResponse(response)
