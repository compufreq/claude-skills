# CloudFormation Reference

## Table of Contents
1. Template Structure
2. Common Patterns
3. Nested Stacks
4. Parameters & Conditions
5. Intrinsic Functions
6. Deployment Commands

---

## 1. Template Structure

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: Production VPC and networking

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, production]
  VpcCidr:
    Type: String
    Default: '10.0.0.0/16'

Conditions:
  IsProduction: !Equals [!Ref Environment, production]

Mappings:
  RegionConfig:
    us-east-1:
      AmiId: ami-0123456789abcdef0
    eu-west-1:
      AmiId: ami-fedcba9876543210

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidr
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: !Sub '${Environment}-vpc'
        - Key: Environment
          Value: !Ref Environment

Outputs:
  VpcId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${Environment}-VpcId'
```

---

## 2. Common Patterns

### VPC with Subnets
```yaml
Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: !Ref VpcCidr
      EnableDnsHostnames: true
      EnableDnsSupport: true

  PublicSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Select [0, !Ref PublicSubnetCidrs]
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true

  PrivateSubnet1:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: !Select [0, !Ref PrivateSubnetCidrs]
      AvailabilityZone: !Select [0, !GetAZs '']

  InternetGateway:
    Type: AWS::EC2::InternetGateway

  GatewayAttachment:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

  NatGateway:
    Type: AWS::EC2::NatGateway
    Condition: IsProduction
    Properties:
      AllocationId: !GetAtt NatEIP.AllocationId
      SubnetId: !Ref PublicSubnet1

  NatEIP:
    Type: AWS::EC2::EIP
    Condition: IsProduction
    Properties:
      Domain: vpc
```

### RDS Instance
```yaml
  Database:
    Type: AWS::RDS::DBInstance
    DeletionPolicy: Snapshot
    Properties:
      DBInstanceIdentifier: !Sub '${Environment}-postgres'
      Engine: postgres
      EngineVersion: '16.3'
      DBInstanceClass: !If [IsProduction, db.r6g.xlarge, db.t4g.medium]
      AllocatedStorage: !If [IsProduction, 100, 20]
      StorageEncrypted: true
      StorageType: gp3
      MultiAZ: !If [IsProduction, true, false]
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups:
        - !Ref DBSecurityGroup
      MasterUsername: !Ref DBUsername
      MasterUserPassword: !Sub '{{resolve:secretsmanager:${Environment}/db-password}}'
      BackupRetentionPeriod: 7
      DeletionProtection: !If [IsProduction, true, false]
```

### ECS Fargate Service
```yaml
  TaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: !Sub '${Environment}-myapp'
      NetworkMode: awsvpc
      RequiresCompatibilities: [FARGATE]
      Cpu: '512'
      Memory: '1024'
      ExecutionRoleArn: !GetAtt TaskExecutionRole.Arn
      TaskRoleArn: !GetAtt TaskRole.Arn
      ContainerDefinitions:
        - Name: myapp
          Image: !Sub '${AWS::AccountId}.dkr.ecr.${AWS::Region}.amazonaws.com/myapp:${ImageTag}'
          PortMappings:
            - ContainerPort: 8080
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region
              awslogs-stream-prefix: myapp
          HealthCheck:
            Command: ['CMD-SHELL', 'curl -f http://localhost:8080/health || exit 1']
            Interval: 30
            Timeout: 5
            Retries: 3

  Service:
    Type: AWS::ECS::Service
    Properties:
      Cluster: !Ref ECSCluster
      TaskDefinition: !Ref TaskDefinition
      DesiredCount: !If [IsProduction, 3, 1]
      LaunchType: FARGATE
      NetworkConfiguration:
        AwsvpcConfiguration:
          Subnets: !Ref PrivateSubnetIds
          SecurityGroups: [!Ref ServiceSecurityGroup]
      LoadBalancers:
        - ContainerName: myapp
          ContainerPort: 8080
          TargetGroupArn: !Ref TargetGroup
```

---

## 3. Nested Stacks

```yaml
# Root template
Resources:
  NetworkStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: !Sub 'https://${TemplateBucket}.s3.amazonaws.com/templates/networking.yaml'
      Parameters:
        Environment: !Ref Environment
        VpcCidr: !Ref VpcCidr

  DatabaseStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: NetworkStack
    Properties:
      TemplateURL: !Sub 'https://${TemplateBucket}.s3.amazonaws.com/templates/database.yaml'
      Parameters:
        Environment: !Ref Environment
        VpcId: !GetAtt NetworkStack.Outputs.VpcId
        SubnetIds: !GetAtt NetworkStack.Outputs.PrivateSubnetIds
```

---

## 4. Parameters & Conditions

```yaml
Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, production]
  InstanceType:
    Type: String
    Default: t3.medium
    AllowedValues: [t3.small, t3.medium, t3.large, m6i.xlarge]
  EnableMonitoring:
    Type: String
    Default: 'true'
    AllowedValues: ['true', 'false']

Conditions:
  IsProduction: !Equals [!Ref Environment, production]
  EnableMon: !Equals [!Ref EnableMonitoring, 'true']
  ProdWithMonitoring: !And [!Condition IsProduction, !Condition EnableMon]
```

---

## 5. Intrinsic Functions

| Function | Purpose | Example |
|----------|---------|---------|
| `!Ref` | Reference parameter/resource | `!Ref VPC` |
| `!Sub` | String substitution | `!Sub '${Environment}-vpc'` |
| `!GetAtt` | Get resource attribute | `!GetAtt VPC.CidrBlock` |
| `!Select` | Select from list | `!Select [0, !GetAZs '']` |
| `!Split` | Split string | `!Split [',', !Ref SubnetList]` |
| `!Join` | Join strings | `!Join [',', [a, b, c]]` |
| `!If` | Conditional value | `!If [IsProduction, 3, 1]` |
| `!ImportValue` | Cross-stack reference | `!ImportValue prod-VpcId` |
| `!GetAZs` | List AZs in region | `!GetAZs ''` |

---

## 6. Deployment Commands

```bash
# Validate
aws cloudformation validate-template --template-body file://template.yaml

# Create stack
aws cloudformation create-stack \
  --stack-name production-vpc \
  --template-body file://vpc.yaml \
  --parameters file://parameters/production.json \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --tags Key=Environment,Value=production

# Update stack (change set — recommended)
aws cloudformation create-change-set \
  --stack-name production-vpc \
  --template-body file://vpc.yaml \
  --parameters file://parameters/production.json \
  --change-set-name update-$(date +%s)

aws cloudformation describe-change-set \
  --stack-name production-vpc \
  --change-set-name update-12345

aws cloudformation execute-change-set \
  --stack-name production-vpc \
  --change-set-name update-12345

# Delete stack
aws cloudformation delete-stack --stack-name staging-vpc

# Wait for completion
aws cloudformation wait stack-create-complete --stack-name production-vpc
```



---
