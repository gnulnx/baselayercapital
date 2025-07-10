import { Construct } from 'constructs'
import { Stack, StackProps } from 'aws-cdk-lib'
import * as logs from 'aws-cdk-lib/aws-logs'
import { Lambdas } from './lambdas'
import { TablesStack } from './tables'
import { LambdaLayerStack } from '../lib/lambda-layer-stack'
import { Api } from '../lib/api-stack'
import * as iam from 'aws-cdk-lib/aws-iam'
import { Route53 } from './route53'
import * as certificatemanager from 'aws-cdk-lib/aws-certificatemanager'
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
  baseDomain: string
  certificateArn: string
}

export class MainStack extends Stack {
  public readonly lambdas: Lambdas

  constructor(scope: Construct, id: string, props: MainStackProps) {
    super(scope, id, props)

    const { ENV_NAME, ENV_TYPE, tables, layers, baseDomain, isProd } = props

    const logRetention = logs.RetentionDays.ONE_DAY

    this.lambdas = new Lambdas(this, `${ENV_NAME}-Lambdas`, {
      env: props.env,
      ENV_NAME,
      ENV_TYPE,
      tables,
      logRetention,
      layers,
    })

    const certificate = certificatemanager.Certificate.fromCertificateArn(
      this,
      'Certificate',
      props.certificateArn,
    )

    const serviceDomainName = isProd ? `api.${baseDomain}` : `${ENV_NAME}-api.${baseDomain}`

    const api = new Api(this, `${ENV_NAME}-ApiStack`, {
      ...props,
      certificate,
      env: props.env,
      serviceDomainName,
      lambdas: this.lambdas,
    })

    new Route53(this, `${ENV_NAME}-userservice-cname`, {
      ...props,
      serviceName: serviceDomainName,
      api: api,
    })
  }
}
