#!/usr/bin/env python3
"""
AWS Resource Manager - Manage EC2, RDS, GitHub Runners, and ECR repositories
"""

import boto3
import json
import logging
import sys
import argparse
from datetime import datetime
from typing import List, Dict, Any
from botocore.exceptions import ClientError
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AWSResourceManager:
    """Manages AWS resources: EC2, RDS, GitHub Runners, and ECR"""

    def __init__(self, region: str = 'us-east-1'):
        """Initialize AWS clients"""
        self.region = region
        self.ec2_client = boto3.client('ec2', region_name=region)
        self.rds_client = boto3.client('rds', region_name=region)
        self.ecr_client = boto3.client('ecr', region_name=region)
        logger.info(f"Initialized AWS Resource Manager for region: {region}")

    # ==================== EC2 Operations ====================
    
    def start_ec2_instances(self, instance_ids: List[str]) -> Dict[str, Any]:
        """Start EC2 instances"""
        try:
            logger.info(f"Starting EC2 instances: {instance_ids}")
            response = self.ec2_client.start_instances(InstanceIds=instance_ids)
            
            result = {
                'status': 'success',
                'operation': 'start',
                'resource': 'ec2',
                'instances': instance_ids,
                'timestamp': datetime.now().isoformat(),
                'response': response['StartingInstances']
            }
            logger.info(f"Successfully started EC2 instances: {instance_ids}")
            return result
        except ClientError as e:
            error_msg = f"Error starting EC2 instances: {str(e)}"
            logger.error(error_msg)
            return {'status': 'error', 'message': error_msg, 'resource': 'ec2'}

    def stop_ec2_instances(self, instance_ids: List[str]) -> Dict[str, Any]:
        """Stop EC2 instances"""
        try:
            logger.info(f"Stopping EC2 instances: {instance_ids}")
            response = self.ec2_client.stop_instances(InstanceIds=instance_ids)
            
            result = {
                'status': 'success',
                'operation': 'stop',
                'resource': 'ec2',
                'instances': instance_ids,
                'timestamp': datetime.now().isoformat(),
                'response': response['StoppingInstances']
            }
            logger.info(f"Successfully stopped EC2 instances: {instance_ids}")
            return result
        except ClientError as e:
            error_msg = f"Error stopping EC2 instances: {str(e)}"
            logger.error(error_msg)
            return {'status': 'error', 'message': error_msg, 'resource': 'ec2'}

    def describe_ec2_instances(self, instance_ids: List[str] = None) -> Dict[str, Any]:
        """Get status of EC2 instances"""
        try:
            if instance_ids:
                response = self.ec2_client.describe_instances(InstanceIds=instance_ids)
            else:
                response = self.ec2_client.describe_instances()
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instances.append({
                        'InstanceId': instance['InstanceId'],
                        'State': instance['State']['Name'],
                        'InstanceType': instance['InstanceType'],
                        'LaunchTime': instance.get('LaunchTime', '').isoformat() if 'LaunchTime' in instance else None
                    })
            
            logger.info(f"Retrieved status for {len(instances)} EC2 instance(s)")
            return {'status': 'success', 'instances': instances}
        except ClientError as e:
            error_msg = f"Error describing EC2 instances: {str(e)}"
            logger.error(error_msg)
            return {'status': 'error', 'message': error_msg}

    # ==================== RDS Operations ====================
    
    def start_rds_instances(self, db_instance_ids: List[str]) -> Dict[str, Any]:
        """Start RDS instances"""
        results = []
        for db_id in db_instance_ids:
            try:
                logger.info(f"Starting RDS instance: {db_id}")
                response = self.rds_client.start_db_instance(DBInstanceIdentifier=db_id)
                results.append({
                    'DBInstanceIdentifier': db_id,
                    'status': 'success',
                    'DBInstanceStatus': response['DBInstance'].get('DBInstanceStatus')
                })
                logger.info(f"Successfully started RDS instance: {db_id}")
            except ClientError as e:
                error_msg = f"Error starting RDS instance {db_id}: {str(e)}"
                logger.error(error_msg)
                results.append({
                    'DBInstanceIdentifier': db_id,
                    'status': 'error',
                    'message': error_msg
                })
        
        return {
            'status': 'completed',
            'operation': 'start',
            'resource': 'rds',
            'timestamp': datetime.now().isoformat(),
            'results': results
        }

    def stop_rds_instances(self, db_instance_ids: List[str]) -> Dict[str, Any]:
        """Stop RDS instances"""
        results = []
        for db_id in db_instance_ids:
            try:
                logger.info(f"Stopping RDS instance: {db_id}")
                response = self.rds_client.stop_db_instance(DBInstanceIdentifier=db_id)
                results.append({
                    'DBInstanceIdentifier': db_id,
                    'status': 'success',
                    'DBInstanceStatus': response['DBInstance'].get('DBInstanceStatus')
                })
                logger.info(f"Successfully stopped RDS instance: {db_id}")
            except ClientError as e:
                error_msg = f"Error stopping RDS instance {db_id}: {str(e)}"
                logger.error(error_msg)
                results.append({
                    'DBInstanceIdentifier': db_id,
                    'status': 'error',
                    'message': error_msg
                })
        
        return {
            'status': 'completed',
            'operation': 'stop',
            'resource': 'rds',
            'timestamp': datetime.now().isoformat(),
            'results': results
        }

    def describe_rds_instances(self, db_instance_ids: List[str] = None) -> Dict[str, Any]:
        """Get status of RDS instances"""
        try:
            if db_instance_ids:
                instances = []
                for db_id in db_instance_ids:
                    response = self.rds_client.describe_db_instances(DBInstanceIdentifier=db_id)
                    for db in response['DBInstances']:
                        instances.append({
                            'DBInstanceIdentifier': db['DBInstanceIdentifier'],
                            'DBInstanceStatus': db['DBInstanceStatus'],
                            'DBInstanceClass': db['DBInstanceClass'],
                            'Engine': db['Engine']
                        })
            else:
                response = self.rds_client.describe_db_instances()
                instances = [{
                    'DBInstanceIdentifier': db['DBInstanceIdentifier'],
                    'DBInstanceStatus': db['DBInstanceStatus'],
                    'DBInstanceClass': db['DBInstanceClass'],
                    'Engine': db['Engine']
                } for db in response['DBInstances']]
            
            logger.info(f"Retrieved status for {len(instances)} RDS instance(s)")
            return {'status': 'success', 'instances': instances}
        except ClientError as e:
            error_msg = f"Error describing RDS instances: {str(e)}"
            logger.error(error_msg)
            return {'status': 'error', 'message': error_msg}

    # ==================== ECR Operations ====================
    
    def list_ecr_repositories(self) -> Dict[str, Any]:
        """List all ECR repositories"""
        try:
            logger.info("Listing ECR repositories")
            response = self.ecr_client.describe_repositories()
            
            repositories = [{
                'repositoryName': repo['repositoryName'],
                'repositoryArn': repo['repositoryArn'],
                'repositoryUri': repo['repositoryUri'],
                'createdAt': repo['createdAt'].isoformat() if 'createdAt' in repo else None
            } for repo in response['repositories']]
            
            logger.info(f"Retrieved {len(repositories)} ECR repositories")
            return {'status': 'success', 'repositories': repositories}
        except ClientError as e:
            error_msg = f"Error listing ECR repositories: {str(e)}"
            logger.error(error_msg)
            return {'status': 'error', 'message': error_msg}

    def get_ecr_images(self, repository_name: str) -> Dict[str, Any]:
        """Get images in an ECR repository"""
        try:
            logger.info(f"Getting images for repository: {repository_name}")
            response = self.ecr_client.describe_images(repositoryName=repository_name)
            
            images = [{
                'imageId': f"{img.get('imageTags', ['untagged'])[0]}@{img['imageId']['imageDigest']}",
                'imagePushedAt': img['imagePushedAt'].isoformat() if 'imagePushedAt' in img else None,
                'imageSizeInBytes': img.get('imageSizeInBytes', 0)
            } for img in response['imageDetails']]
            
            logger.info(f"Retrieved {len(images)} images from repository: {repository_name}")
            return {'status': 'success', 'repository': repository_name, 'images': images}
        except ClientError as e:
            error_msg = f"Error getting ECR images: {str(e)}"
            logger.error(error_msg)
            return {'status': 'error', 'message': error_msg}

    # ==================== GitHub Runner Operations ====================
    
    def manage_github_runners(self, operation: str, github_token: str, repo: str) -> Dict[str, Any]:
        """Manage GitHub self-hosted runners"""
        try:
            logger.info(f"Managing GitHub runners: {operation}")
            
            headers = {
                'Authorization': f'token {github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            
            url = f"https://api.github.com/repos/{repo}/actions/runners"
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                error_msg = f"Error fetching GitHub runners: {response.text}"
                logger.error(error_msg)
                return {'status': 'error', 'message': error_msg}
            
            runners = response.json().get('runners', [])
            logger.info(f"Retrieved {len(runners)} GitHub runners")
            
            return {
                'status': 'success',
                'operation': operation,
                'resource': 'github_runners',
                'runners': [{
                    'id': runner['id'],
                    'name': runner['name'],
                    'status': runner['status'],
                    'busy': runner['busy']
                } for runner in runners]
            }
        except Exception as e:
            error_msg = f"Error managing GitHub runners: {str(e)}"
            logger.error(error_msg)
            return {'status': 'error', 'message': error_msg}


def main():
    parser = argparse.ArgumentParser(
        description="AWS Resource Manager - Start/Stop EC2, RDS, manage ECR and GitHub Runners"
    )
    
    parser.add_argument(
        '--resource',
        type=str,
        required=True,
        choices=['ec2', 'rds', 'ecr', 'github'],
        help='Resource type to manage'
    )
    
    parser.add_argument(
        '--operation',
        type=str,
        required=True,
        choices=['start', 'stop', 'status', 'list'],
        help='Operation to perform'
    )
    
    parser.add_argument(
        '--region',
        type=str,
        default='us-east-1',
        help='AWS region (default: us-east-1)'
    )
    
    parser.add_argument(
        '--ids',
        type=str,
        nargs='+',
        help='Resource IDs (instance IDs for EC2, DB identifiers for RDS)'
    )
    
    parser.add_argument(
        '--github-token',
        type=str,
        help='GitHub personal access token for runner operations'
    )
    
    parser.add_argument(
        '--github-repo',
        type=str,
        help='GitHub repository in format: owner/repo'
    )
    
    parser.add_argument(
        '--json-output',
        action='store_true',
        help='Output results as JSON'
    )
    
    args = parser.parse_args()
    
    manager = AWSResourceManager(region=args.region)
    result = {}
    
    try:
        if args.resource == 'ec2':
            if args.operation == 'start':
                if not args.ids:
                    logger.error("--ids required for EC2 start operation")
                    sys.exit(1)
                result = manager.start_ec2_instances(args.ids)
            elif args.operation == 'stop':
                if not args.ids:
                    logger.error("--ids required for EC2 stop operation")
                    sys.exit(1)
                result = manager.stop_ec2_instances(args.ids)
            elif args.operation in ['status', 'list']:
                result = manager.describe_ec2_instances(args.ids)
        
        elif args.resource == 'rds':
            if args.operation == 'start':
                if not args.ids:
                    logger.error("--ids required for RDS start operation")
                    sys.exit(1)
                result = manager.start_rds_instances(args.ids)
            elif args.operation == 'stop':
                if not args.ids:
                    logger.error("--ids required for RDS stop operation")
                    sys.exit(1)
                result = manager.stop_rds_instances(args.ids)
            elif args.operation in ['status', 'list']:
                result = manager.describe_rds_instances(args.ids)
        
        elif args.resource == 'ecr':
            if args.operation == 'list':
                result = manager.list_ecr_repositories()
            elif args.operation == 'status' and args.ids:
                result = manager.get_ecr_images(args.ids[0])
        
        elif args.resource == 'github':
            if not args.github_token or not args.github_repo:
                logger.error("--github-token and --github-repo required for GitHub operations")
                sys.exit(1)
            result = manager.manage_github_runners(args.operation, args.github_token, args.github_repo)
        
        if args.json_output:
            print(json.dumps(result, indent=2))
        else:
            logger.info(f"Operation completed: {json.dumps(result, indent=2)}")
        
        # Exit with error code if operation failed
        if result.get('status') == 'error':
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()