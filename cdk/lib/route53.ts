import * as route53 from 'aws-cdk-lib/aws-route53'
import * as route53targets from 'aws-cdk-lib/aws-route53-targets'
import { Construct } from 'constructs'
import * as cdk from 'aws-cdk-lib'
import { Api } from './api-stack'

interface Route53Props {
  env: {
    region: string
    account: string
  }
  ENV_NAME: string
  isProd: boolean
  domainNameStr: string
  serviceName: string
  api: Api
}

export class Route53 {
  constructor(scope: Construct, id: string, props: Route53Props) {
    const { ENV_NAME, serviceName, api } = props

    const domainName = 'baselayercapital.com'
    const hostedZone = route53.HostedZone.fromLookup(scope, `${ENV_NAME}-UserServiceHostedZone`, {
      domainName: domainName,
    })

    new route53.ARecord(scope, `${ENV_NAME}-userservice-A-record`, {
      zone: hostedZone,
      target: route53.RecordTarget.fromAlias(
        new route53targets.ApiGatewayDomain(api.api.domainName!),
      ),
      recordName: serviceName,
      ttl: cdk.Duration.minutes(5),
    })
  }
}
