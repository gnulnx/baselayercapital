import { Construct } from 'constructs'
import { Stack, StackProps } from 'aws-cdk-lib'
import * as logs from 'aws-cdk-lib/aws-logs'
import { Lambdas } from './lambdas'
import { TablesStack } from './tables'
import { LambdaLayerStack } from '../lib/lambda-layer-stack'
import { Api } from '../lib/api-stack'
import { Route53 } from './route53'
import * as certificatemanager from 'aws-cdk-lib/aws-certificatemanager'
import * as sqs from 'aws-cdk-lib/aws-sqs'
import { Duration } from 'aws-cdk-lib'

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

    const dataIngestionQueue = new sqs.Queue(this, `${ENV_NAME}-DataIngestionQueue`, {
      queueName: `${ENV_NAME}-DataIngestionQueue`,
      visibilityTimeout: Duration.seconds(300), // adjust as needed
      retentionPeriod: Duration.days(4), // adjust as needed
    })

    this.lambdas = new Lambdas(this, `${ENV_NAME}-Lambdas`, {
      env: props.env,
      ENV_NAME,
      ENV_TYPE,
      tables,
      logRetention,
      layers,
      dataIngestionQueue,
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
