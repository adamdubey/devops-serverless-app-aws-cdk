from aws_cdk import (
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_kms as kms,
    aws_ssm as ssm,
    aws_secretsmanager as sm,
    core
)

import json

class RDSStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc: ec2.Vpc, lambdasg: ec2.SecurityGroup, bastionsg: ec2.SecurityGroup, kmskey, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        json_template = {'username': 'admin'}

        db_creds = sm.Secret(self, 'db-secret',
            secret_name = env_name + '/rds-secret',
            generate_secret_string = sm.SecretStringGenerator(
                include_space =  False,
                password_length = 12,
                generate_string_key = 'rds-password',
                exclude_punctuation = True,
                secret_string_template = json.dumps(json_template)
            )
        )

        db_mysql = rds.DatabaseCluster(self, 'mysql',
                default_database_name=prj_name+env_name,
                engine=rds.DatabaseClusterEngine.aurora_mysql(
                    version=rds.AuroraMysqlEngineVersion.VER_5_7_12
                ),
                instance_props=rds.InstanceProps(
                    vpc=vpc,
                    vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.ISOLATED),
                    instance_type=ec2.InstanceType(instance_type_identifier='t3.small')
                ),
                instances=1,
                parameter_group=rds.ParameterGroup.from_parameter_group_name(
                    self, 'pg-dev',
                    parameter_group_name='default.aurora-mysql5.7'
                ),
                removal_policy=core.RemovalPolicy.DESTROY,
                credentials=rds.Credentials.from_secret(secret=db_creds)
                # credentials=rds.Credentials.from_generated_secret(
                #     username='admin',
                #     secret_name='cds-rds-secret'
                # )
        )

        db_mysql.connections.allow_default_port_from(lambdasg, "Access from Lambda Functions")
        db_mysql.connections.allow_default_port_from(bastionsg, "Access from Bastion Host")

        ssm.StringParameter(self, 'db-host',
            parameter_name = '/' + env_name + '/db-host',
            string_value = db_mysql.cluster_endpoint.hostname
        )
