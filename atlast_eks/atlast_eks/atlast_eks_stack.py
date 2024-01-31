from aws_cdk import (
    aws_eks as aws_eks,
    Stack,
    aws_ec2 as ec2,
    aws_iam as aws_iam,
    core
    
)
from constructs import Construct

class AtlastEksStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        availability_zones = ['eu-central-1a', 'eu-central-1b']
        # Create a new VPC
        vpc = ec2.Vpc(self, 'Vpc',
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            vpc_name='eks-vpc',
            enable_dns_hostnames=True,
            enable_dns_support=True,
            availability_zones=availability_zones,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name='eks-subnet-public',
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name='eks-subnet-private',
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ]
        )
       
          

        # Create an IAM Role to be assumed by admins
        masters_role = aws_iam.Role(
            self,
            'EksMastersRole',
            assumed_by=aws_iam.AccountRootPrincipal('*')
        )

        # Attach an IAM Policy to that Role so users can access the Cluster
        masters_role_policy = aws_iam.PolicyStatement(
            actions=['eks:DescribeCluster'],
            resources=['*'],  # Adjust the resource ARN if needed
        )
        masters_role.add_to_policy(masters_role_policy)
        cluster.aws_auth.add_masters_role(masters_role)

        # Add the user to the cluster's admins
        admin_user = aws_iam.User.from_user_arn(self, "AdminUser")
        cluster.aws_auth.add_user_mapping(admin_user, groups=["system:masters"])

        # Output the EKS cluster name
        core.CfnOutput(
        self,
        'ClusterNameOutput',
        value=cluster.cluster_name,
        )

        #Output the EKS master role ARN
        core.CfnOutput(
        self,
        'ClusterMasterRoleOutput',
        value=masters_role.role_arn,
        description="IAM Role ARN for EKS cluster administrators",  # Add a description for clarity
        )


        # Creating cluster variable
        cluster = aws_eks.Cluster(
            self, 'EKS-Cluster',
            cluster_name='eks-cluster',
            version=aws_eks.KubernetesVersion.V1_26,
            vpc=vpc,
            default_capacity=0
        )

        ...
        # Create the EC2 node group
        aws_eks.nodegroup = cluster.add_nodegroup_capacity(
            'Nodegroup',
            instance_types=[ec2.InstanceType('t3.medium')],
            desired_size=1,
            min_size=1,
            max_size=3,
            ami_type=aws_eks.NodegroupAmiType.AL2_X86_64
        )


        # The code that defines your stack goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "AtlastEksQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
