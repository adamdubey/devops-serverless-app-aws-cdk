#!/usr/bin/env python3

from aws_cdk import core
from stacks.vpc_stack import VPCStack
from stacks.security_stack import SecurityStack
from stacks.bastion_stack import BastionStack
from stacks.kms_stack import KMSStack
from stacks.s3_stack import S3Stack
from stacks.rds_stack import RDSStack
from stacks.redis_stack import RedisStack
from stacks.cognito_stack import CognitoStack
from stacks.apigw_stack import APIStack
from stacks.lambda_stack import LambdaStack
from stacks.codepipeline_backend import CodePipelineBackendStack
from stacks.notifications import NotificationStack

app = core.App()

vpc_stack = VPCStack(app, 'vpc')
security_stack = SecurityStack(app, 'security-stack', vpc = vpc_stack.vpc)
bastion_stack = BastionStack(app, 'bastion', vpc = vpc_stack.vpc, sg = security_stack.bastion_sg)
kms_stack = KMSStack(app, 'kms')
s3_stack = S3Stack(app, 's3buckets')
rds_stack = RDSStack(app, 'rds', vpc = vpc_stack.vpc, lambdasg = security_stack.lambda_sg, bastionsg = security_stack.bastion_sg, kmskey = kms_stack.kms_rds)
redis_stack = RedisStack(app, 'redis', vpc = vpc_stack.vpc, redissg = core.Fn.import_value('redis-sg-export'))
cognito_stack = CognitoStack(app, 'cognito')
apigw_stack = APIStack(app, 'apigw')
lambda_stack = LambdaStack(app, 'lambda')
#cp_backend = CodePipelineBackendStack(app, 'cp-backend', artifactbucket = core.Fn.import_value('build-artifacts-bucket'))
notification_stack = NotificationStack(app, 'notification')

app.synth()
