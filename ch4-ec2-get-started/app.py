import os
from aws_cdk import core, aws_ec2 as ec2

class MyFirstEc2(core.Stack):
    def __init__(self, scope: core.App, name:str, key_name:str, **kwargs) -> None:
        super().__init__(scope, name, **kwargs)

        vpc = ec2.Vpc(
            self,
            "MyFirstEc2-Vpc",
            # availability Zoneの数
            max_azs=1,
            # CIDR表記のIPV4のレンジ
            cidr="10.10.0.0/23",
            # publicにしないと外部に出れない
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC
                )
            ],
            nat_gateways=0,
        )

        sg = ec2.SecurityGroup(
            self,
            "MyFirstEc2-sg",
            vpc=vpc,
            # すべてのoutbound(外部へのIP通信の許可)
            allow_all_outbound=True,
        )
        # SSH接続のために22ポートを解法
        sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
        )

        host = ec2.Instance(
            self,
            "MyFirstEc2Instance",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=sg,
            key_name=key_name,
        )

        core.CfnOutput(self, "InstancePublicDnsName", value=host.instance_public_dns_name)
        core.CfnOutput(self, "InstancePublicIp", value=host.instance_public_ip)


app = core.App()

MyFirstEc2(
    app,
    "MyFirstEc2",
    key_name=app.node.try_get_context("key_name"),
    env={
        "region": os.environ["CDK_DEFAULT_REGION"],
        "account": os.environ["CDK_DEFAULT_ACCOUNT"],
    }
)

app.synth()