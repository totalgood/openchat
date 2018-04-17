#!/usr/bin/env python
""" Docker Compose utilities """
import json
import os
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

    compose_file_path = sys.argv[1]
