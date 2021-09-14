from aws_cdk import (
    aws_elasticache as redis,
    aws_ec2 as ec2,
    aws_ssm as ssm,
    core
)

class RedisStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, vpc, redissg, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        prj_name = self.node.try_get_context("project_name")
        env_name = self.node.try_get_context("env")

        subnets = [ subnet.subnet_id for subnet in vpc.private_subnets ]

        subnet_group = redis.CfnSubnetGroup(self, 'redis-subnet-group',
            subnet_ids = subnets,
            description = "Subnet Group for Redis"
        )

        redis_cluster = redis.CfnCacheCluster(self, 'redis',
            cache_node_type = 'cache.t2.small',
            engine = 'redis',
            num_cache_nodes = 1,
            cluster_name = prj_name + '-redis-' + env_name,
            cache_subnet_group_name = subnet_group.ref,
            vpc_security_group_ids = [redissg],
            auto_minor_version_upgrade = True
        )

        redis_cluster.add_depends_on(subnet_group)
