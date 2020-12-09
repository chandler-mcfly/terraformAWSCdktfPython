from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput, Token
from imports.aws import Instance, AwsProvider, Subnet, Vpc, DefaultRouteTable, InternetGateway, Route, SecurityGroup, SecurityGroupRule, KeyPair
# from imports.terraform_aws_modules.vpc.aws import Vpc

class MyStack(TerraformStack):
    def __init__(self, scope: Construct, ns: str):
        super().__init__(scope, ns)

        AwsProvider(self, 'Aws', region='us-east-1')

        tag = {
                "OHR_ID":"850047690",
                "Created through":"Terraform"
        }

        newVpc = Vpc(self, 'newVpc', enable_dns_hostnames=True, cidr_block='10.0.0.0/16', tags=tag)

        newSecurityGroup = SecurityGroup(self, 'newSecurityGroup', name="newSecurityGroup", vpc_id=Token().as_string(newVpc.id), tags=tag)

        newSecurityGroupInboundRule = SecurityGroupRule(self, 'newSecurityGroupInboundRule', type="ingress", cidr_blocks=["0.0.0.0/0"], from_port=0, to_port=65535, protocol="-1", security_group_id=Token().as_string(newSecurityGroup.id))

        newSecurityGroupOutboundRule = SecurityGroupRule(self, 'newSecurityGroupOutboundRule', type="egress", cidr_blocks=["0.0.0.0/0"], from_port=0, to_port=65535, protocol="-1", security_group_id=Token().as_string(newSecurityGroup.id))

        newInternetGateway = InternetGateway(self, 'newInternetGateway', vpc_id=Token().as_string(newVpc.id), tags=tag)

        newSubnet = Subnet(self, 'newSubnet', vpc_id=Token().as_string(newVpc.id), cidr_block="10.0.0.0/24", availability_zone="us-east-1a", map_public_ip_on_launch=True, tags=tag)
        
        newDefaultRouteTable = DefaultRouteTable(self, 'newDefaultRouteTable', default_route_table_id=Token().as_string(newVpc.default_route_table_id), tags=tag)

        newKeyPair = KeyPair(self, 'newKeyPair', key_name="AccessKey", public_key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDHXCpTsz95b2CbqqduP6FxM6ymQQcqm5g66kynw5qyvTvIMy7SUkTTjS1BCYguVG9d2ZQ7NMXWTCbFIp9bh3VyT9ZpF5N6GBgLLowiJAbkVpmOmoZkZ1NFPCmqgppIwdcECMDWI5hyqPND8hLsh2tq8kSAlCJNB0QE+2QNjMTy1QYQ32B90wLoi8y0GDTWlU4MD43dfznI1Mq99JppjezRiBWqWUJvlPpfHVbj5MaPXlyQNiN3GcE9MA9ME3dQ7XBumFNVBbDf/YvqRstG56fRUr/a0Tly/PVKLm/dHtKq0GwLCrjUnkmIbSBu6QMx7aBJF3jdpPAuohqOoGNdXd/ohOeprSkkGl5OcrIfimKq6BIsLxAK0k0YgfmB7wM1ZlL495x13BttimNqe/dvn/lo5/8O76PtIZ2VpFlWAEpqBVzTyhJNfWLMUevpMNdoRETmYwWB6UIo68S3h71sndEazMqZp67ikeqMtAdzytpmtX9+VikIXurZSRbtQX4Nys8= chandlermcfly@ubuntu")

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