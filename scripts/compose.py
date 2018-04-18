#!/usr/bin/env python
""" Docker Compose utilities and AWS ECS deployment automation

AWSServiceRoleForECS = \
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ec2:AttachNetworkInterface",
                    "ec2:CreateNetworkInterface",
                    "ec2:CreateNetworkInterfacePermission",
                    "ec2:DeleteNetworkInterface",
                    "ec2:DeleteNetworkInterfacePermission",
                    "ec2:Describe*",
                    "ec2:DetachNetworkInterface",
                    "elasticloadbalancing:DeregisterInstancesFromLoadBalancer",
                    "elasticloadbalancing:DeregisterTargets",
                    "elasticloadbalancing:Describe*",
                    "elasticloadbalancing:RegisterInstancesWithLoadBalancer",
                    "elasticloadbalancing:RegisterTargets",
                    "route53:ChangeResourceRecordSets",
                    "route53:CreateHealthCheck",
                    "route53:DeleteHealthCheck",
                    "route53:Get*",
                    "route53:List*",
                    "route53:UpdateHealthCheck",
                    "servicediscovery:DeregisterInstance",
                    "servicediscovery:Get*",
                    "servicediscovery:List*",
                    "servicediscovery:RegisterInstance",
                    "servicediscovery:UpdateInstanceCustomHealthStatus"
                ],
                "Resource": "*"
            }
        ]
    }

AmazonECSTaskExecutionRolePolicy = \
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "ecr:GetAuthorizationToken",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchGetImage",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents"
                ],
                "Resource": "*"
            }
        ]
    }
"""
import json
import os
import sys
import subprocess
import tempfile

import boto3


def compose2ecs(dc_path='docker-compose.yml', family=None, task_role_arn=None):
    """ Convert docker-compose.yml file to return an ECS task definition (json object).

    Args:
      dc_path (str): Path to the docker-compose file.

    Returns:
      dict: ecs_task_definition
    """
    with open(dc_path, 'r') as dc_file, tempfile.TemporaryFile('w+t') as tmp:
        subprocess.check_call(
            [
                '/usr/bin/env',
                'docker',
                'run',
                '--rm',
                '-i',
                'micahhausler/container-transform'
            ],
            stdin=dc_file,
            stdout=tmp,
        )
        tmp.seek(0)
        ecs_task_definition = json.load(tmp)
        ecs_task_definition['family'] = family
        ecs_task_definition['taskRoleArn'] = task_role_arn
        return ecs_task_definition


def register_ecs(ecs_client=boto3.client('ecs'), ecs_task_definition=json.load('task.json')):
    """Register an ECS task definition and return it.

    Args:
      ecs_client (boto3.client): Boto client to register your task with ECS
      ecs_task_definition (dict): task definition, from Micah Hausler's ecs_from_dc
    """
    family = ecs_task_definition['family']
    task_role_arn = ecs_task_definition['taskRoleArn']

    return ecs_client.register_task_definition(
        family=family,
        taskRoleArn=task_role_arn,
        containerDefinitions=ecs_task_definition,
    )


def create_cluster(ecs_client=boto3.client('ecs'), name='openchat'):
    """ Create an ECS cluster, return the boto3 cluster client object

    Positional parameters:
      name (str): cluster name (there must not be existing clusters with the same name)
    """
    return ecs_client.create_cluster(clusterName=name)


def main(compose_file_path='docker-compose.yml', ecs_file_name='ecs-task.json', family='', task_role_arn=''):
    ecs_task_definition = compose2ecs(compose_file_path)
    ecs_task_path = os.path.join(os.path.dirname(compose_file_path), ecs_file_name)
    ecs_task_json = json.dumps(ecs_task_definition, indent=2)
    print(ecs_task_json)
    with open(ecs_task_path, 'w') as fout:
        fout.write(ecs_task_json)


if __name__ == '__main__':
    ecs_client = boto3.client('ecs')
    """Client interface for ECS"""
    compose_file_path = sys.argv[1] if len(sys.argv) > 1 else 'docker-compose.yml'
    task_json = compose2ecs(compose_file_path)
    print(register_ecs(ecs_client=ecs_client, ecs_task_definition=task_json))
    boto3.client('ecs')
