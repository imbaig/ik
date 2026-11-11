"""Generate a secret-free CloudFormation template from the reviewed bootstrap."""

import json
from pathlib import Path


def ref(name):
    return {"Ref": name}


def sub(text):
    return {"Fn::Sub": text}


def template():
    return {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "Music Store v1 sample: EC2, HTTPS CloudFront, quota, scheduled stop",
        "Parameters": {
            "SourceRevision": {"Type": "String", "AllowedPattern": "[0-9a-f]{40}"},
            "VpcId": {"Type": "AWS::EC2::VPC::Id"},
            "SubnetId": {"Type": "AWS::EC2::Subnet::Id"},
            "SecretParameterName": {
                "Type": "String",
                "Default": "/music-store/v1/openai-api-key",
                "AllowedPattern": "/music-store/v1/[a-z0-9-]+",
            },
            "StopAfterDays": {"Type": "Number", "Default": 7, "MinValue": 1, "MaxValue": 14},
            "ImageId": {
                "Type": "AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>",
                "Default": "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64",
            },
        },
        "Rules": {
            "VirginiaOnly": {
                "Assertions": [
                    {
                        "Assert": {"Fn::Equals": [ref("AWS::Region"), "us-east-1"]},
                        "AssertDescription": "Course deployment is restricted to us-east-1",
                    }
                ]
            }
        },
        "Resources": {
            "ServerRole": {
                "Type": "AWS::IAM::Role",
                "Properties": {
                    "AssumeRolePolicyDocument": {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Principal": {"Service": "ec2.amazonaws.com"},
                                "Action": "sts:AssumeRole",
                            }
                        ],
                    },
                    "Policies": [
                        {
                            "PolicyName": "ReadOnlyOwnProviderParameter",
                            "PolicyDocument": {
                                "Version": "2012-10-17",
                                "Statement": [
                                    {
                                        "Effect": "Allow",
                                        "Action": "ssm:GetParameter",
                                        "Resource": sub(
                                            "arn:${AWS::Partition}:ssm:us-east-1:${AWS::AccountId}:parameter${SecretParameterName}"
                                        ),
                                    },
                                    {
                                        "Effect": "Allow",
                                        "Action": [
                                            "ssm:UpdateInstanceInformation",
                                            "ssmmessages:CreateControlChannel",
                                            "ssmmessages:CreateDataChannel",
                                            "ssmmessages:OpenControlChannel",
                                            "ssmmessages:OpenDataChannel",
                                        ],
                                        "Resource": "*",
                                    },
                                ],
                            },
                        }
                    ],
                },
            },
            "ServerProfile": {
                "Type": "AWS::IAM::InstanceProfile",
                "Properties": {"Roles": [ref("ServerRole")]},
            },
            "ServerSecurityGroup": {
                "Type": "AWS::EC2::SecurityGroup",
                "Properties": {
                    "GroupDescription": "HTTP from CloudFront only; no public SSH or Gradio",
                    "VpcId": ref("VpcId"),
                    "SecurityGroupIngress": [
                        {
                            "IpProtocol": "tcp",
                            "FromPort": 80,
                            "ToPort": 80,
                            "SourcePrefixListId": "pl-3b927c52",
                        }
                    ],
                    "SecurityGroupEgress": [{"IpProtocol": "-1", "CidrIp": "0.0.0.0/0"}],
                },
            },
            "Server": {
                "Type": "AWS::EC2::Instance",
                "Properties": {
                    "ImageId": ref("ImageId"),
                    "InstanceType": "t2.medium",
                    "CreditSpecification": {"CPUCredits": "standard"},
                    "IamInstanceProfile": ref("ServerProfile"),
                    "InstanceInitiatedShutdownBehavior": "stop",
                    "MetadataOptions": {"HttpTokens": "required", "HttpPutResponseHopLimit": 1},
                    "BlockDeviceMappings": [
                        {
                            "DeviceName": "/dev/xvda",
                            "Ebs": {
                                "VolumeSize": 16,
                                "VolumeType": "gp3",
                                "Encrypted": True,
                                "DeleteOnTermination": True,
                            },
                        }
                    ],
                    "NetworkInterfaces": [
                        {
                            "DeviceIndex": "0",
                            "AssociatePublicIpAddress": True,
                            "SubnetId": ref("SubnetId"),
                            "GroupSet": [ref("ServerSecurityGroup")],
                        }
                    ],
                    "UserData": {
                        "Fn::Base64": sub(Path(__file__).with_name("bootstrap.sh").read_text())
                    },
                    "Tags": [
                        {"Key": "Name", "Value": "music-store-v1-grading"},
                        {"Key": "Project", "Value": "capstone-v1"},
                    ],
                },
            },
            "Site": {
                "Type": "AWS::CloudFront::Distribution",
                "Properties": {
                    "DistributionConfig": {
                        "Enabled": True,
                        "IPV6Enabled": True,
                        "HttpVersion": "http2",
                        "PriceClass": "PriceClass_100",
                        "Comment": "Public sample music store v1 grading; no cached conversations",
                        "Origins": [
                            {
                                "Id": "v1",
                                "DomainName": {"Fn::GetAtt": ["Server", "PublicDnsName"]},
                                "CustomOriginConfig": {
                                    "HTTPPort": 80,
                                    "OriginProtocolPolicy": "http-only",
                                    "OriginReadTimeout": 60,
                                },
                            }
                        ],
                        "DefaultCacheBehavior": {
                            "TargetOriginId": "v1",
                            "ViewerProtocolPolicy": "redirect-to-https",
                            "AllowedMethods": [
                                "GET",
                                "HEAD",
                                "OPTIONS",
                                "PUT",
                                "POST",
                                "PATCH",
                                "DELETE",
                            ],
                            "CachedMethods": ["GET", "HEAD"],
                            "Compress": True,
                            "MinTTL": 0,
                            "DefaultTTL": 0,
                            "MaxTTL": 0,
                            "ForwardedValues": {
                                "QueryString": True,
                                "Cookies": {"Forward": "all"},
                                "Headers": ["*"],
                            },
                        },
                        "CustomErrorResponses": [
                            {"ErrorCode": code, "ErrorCachingMinTTL": 0}
                            for code in (400, 403, 404, 405, 414, 416, 500, 501, 502, 503, 504)
                        ],
                        "ViewerCertificate": {"CloudFrontDefaultCertificate": True},
                    }
                },
            },
        },
        "Outputs": {
            "GradingUrl": {"Value": sub("https://${Site.DomainName}/")},
            "InstanceId": {"Value": ref("Server")},
            "SourceRevision": {"Value": ref("SourceRevision")},
            "StopAfterDays": {"Value": ref("StopAfterDays")},
        },
    }


if __name__ == "__main__":
    print(json.dumps(template(), indent=2))
