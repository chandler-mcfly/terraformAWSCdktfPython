from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput, Token
from imports.aws import Instance, AwsProvider, Subnet, Vpc, DefaultRouteTable, InternetGateway, Route, SecurityGroup, SecurityGroupRule, KeyPair
# from imports.terraform_aws_modules.vpc.aws import Vpc

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        AwsProvider(self, 'Aws', region='us-east-1')

        tag = {
                "tag":"content",
                "Created through":"Terraform"
        }

        newVpc = Vpc(self, 'newVpc', enable_dns_hostnames=True, cidr_block='10.0.0.0/16', tags=tag)

        newSecurityGroup = SecurityGroup(self, 'newSecurityGroup', name="newSecurityGroup", vpc_id=Token().as_string(newVpc.id), tags=tag)

        newSecurityGroupInboundRule = SecurityGroupRule(self, 'newSecurityGroupInboundRule', type="ingress", cidr_blocks=["0.0.0.0/0"], from_port=0, to_port=65535, protocol="-1", security_group_id=Token().as_string(newSecurityGroup.id))

        newSecurityGroupOutboundRule = SecurityGroupRule(self, 'newSecurityGroupOutboundRule', type="egress", cidr_blocks=["0.0.0.0/0"], from_port=0, to_port=65535, protocol="-1", security_group_id=Token().as_string(newSecurityGroup.id))

        newInternetGateway = InternetGateway(self, 'newInternetGateway', vpc_id=Token().as_string(newVpc.id), tags=tag)

        newSubnet = Subnet(self, 'newSubnet', vpc_id=Token().as_string(newVpc.id), cidr_block="10.0.0.0/24", availability_zone="us-east-1a", map_public_ip_on_launch=True, tags=tag)
        
        newDefaultRouteTable = DefaultRouteTable(self, 'newDefaultRouteTable', default_route_table_id=Token().as_string(newVpc.default_route_table_id), tags=tag)

        newKeyPair = KeyPair(self, 'newKeyPair', key_name="AccessKey", public_key="")

        newInstance = Instance(self, 'newInstance',
          ami="ami-0739f8cdb239fe9ae", 
          instance_type="t2.micro",
          subnet_id=Token().as_string(newSubnet.id),
          vpc_security_group_ids=[Token().as_string(newSecurityGroup.id)],
          key_name=newKeyPair.key_name,
          tags=tag
        )

        newRoute = Route(self, 'newRoute', route_table_id=Token().as_string(newDefaultRouteTable.id), destination_cidr_block="0.0.0.0/0", gateway_id=Token().as_string(newInternetGateway.id))

        # newRoute = Route(self, 'newRoute', route_table_id=Token().as_string(newDefaultRouteTable.id), destination_cidr_block="0.0.0.0/0", instance_id=Token().as_string(newInstance.id))

        TerraformOutput(self, 'newInstance_public_ip',
          value=newInstance.public_ip
        )


app = App()
MyStack(app, "pythonnewInstanceTerraform")

app.synth()
