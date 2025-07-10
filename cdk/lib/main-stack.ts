import { Construct } from 'constructs'
import { Stack, StackProps } from 'aws-cdk-lib'
import * as logs from 'aws-cdk-lib/aws-logs'
import { Lambdas } from './lambdas'
import { TablesStack } from './tables'
import { LambdaLayerStack } from '../lib/lambda-layer-stack'
import { ApiStack } from '../lib/api-stack'
import * as iam from 'aws-cdk-lib/aws-iam'

interface MainStackProps extends StackProps {
  env: {
    region: string
    account: string
  }
  ENV_NAME: string
  ENV_TYPE: string
  dynamoRemovalPolicy: string
  deleteProtection: boolean
  pointInTimeRecovery: boolean
  tables: TablesStack
  layers: LambdaLayerStack
  isProd: boolean
  domainNameStr: string
  certificateArn: string
}

export class MainStack extends Stack {
  public readonly lambdas: Lambdas

  constructor(scope: Construct, id: string, props: MainStackProps) {
    super(scope, id, props)

    const { ENV_NAME, ENV_TYPE, tables, layers } = props

    const logRetention = logs.RetentionDays.ONE_DAY

    this.lambdas = new Lambdas(this, `${ENV_NAME}-Lambdas`, {
      env: props.env,
      ENV_NAME,
      ENV_TYPE,
      tables,
      logRetention,
      layers,
    })

    const apiStack = new ApiStack(scope, `${ENV_NAME}-ApiStack`, {
      ...props,
      env: props.env,
      lambdas: this.lambdas,
    })

    this.lambdas.userService.addPermission('ApiInvokePermission', {
      principal: new iam.ServicePrincipal('apigateway.amazonaws.com'),
      action: 'lambda:InvokeFunction',
      sourceArn: `arn:aws:execute-api:${process.env.AWS_REGION}:${process.env.AWS_ACCOUNT_ID}:${apiStack.api.restApiId}/*/*/challenge/*`,
    })
  }
}
