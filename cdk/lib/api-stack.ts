import { Construct } from 'constructs'
import { Stack, StackProps } from 'aws-cdk-lib'
import * as cdk from 'aws-cdk-lib'
import * as apigateway from 'aws-cdk-lib/aws-apigateway'
import * as certificatemanager from 'aws-cdk-lib/aws-certificatemanager'
import * as iam from 'aws-cdk-lib/aws-iam'
import { Lambdas } from './lambdas'

const methodResponses = [
  {
    statusCode: '200',
    responseParameters: {
      'method.response.header.Access-Control-Allow-Origin': true,
      'method.response.header.Access-Control-Allow-Methods': true,
      'method.response.header.Access-Control-Allow-Headers': true,
    },
    responseModels: {
      'application/json': apigateway.Model.EMPTY_MODEL,
    },
  },
  {
    statusCode: '500',
    responseParameters: {
      'method.response.header.Access-Control-Allow-Origin': true,
      'method.response.header.Access-Control-Allow-Methods': true,
      'method.response.header.Access-Control-Allow-Headers': true,
    },
    responseModels: {
      'application/json': apigateway.Model.ERROR_MODEL,
    },
  },
]

interface ApiStackCustomProps extends StackProps {
  env: {
    region: string
    account: string
  }
  ENV_NAME: string
  ENV_TYPE: string
  certificateArn: string
  isProd: boolean
  domainNameStr: string
  lambdas: Lambdas
}

type ApiStackProps = apigateway.RestApiProps & ApiStackCustomProps

export class ApiStack extends Stack {
  public readonly api: apigateway.RestApi

  constructor(scope: Construct, id: string, props: ApiStackProps) {
    super(scope, id, props)

    const { ENV_NAME, certificateArn, isProd, env, domainNameStr, lambdas } = props

    const allowedOrigins = isProd
      ? ['https://baselayercapital.com', 'https://www.baselayercapital.com']
      : apigateway.Cors.ALL_ORIGINS

    const corsOptions = {
      allowOrigins: allowedOrigins,
      allowMethods: apigateway.Cors.ALL_METHODS,
      allowHeaders: apigateway.Cors.DEFAULT_HEADERS,
      allowCredentials: isProd,
      maxAge: cdk.Duration.days(1),
    }

    // Define defaults for deployOptions
    const defaultDeployOptions: apigateway.StageOptions = {
      dataTraceEnabled: false,
      metricsEnabled: false,
      tracingEnabled: false,
    }

    const serviceName = 'api'

    const serviceDomainName = `${ENV_NAME}-${serviceName}-${env.region}.${domainNameStr}`

    this.api = new apigateway.RestApi(this, `${ENV_NAME}-${serviceName}-Api`, {
      restApiName: `${ENV_NAME}-${serviceName}-Api`,
      deployOptions: {
        ...defaultDeployOptions, // Spread defaults first
        ...props.deployOptions, // Override defaults with user-specified options if provided
      },
      domainName: {
        domainName: serviceDomainName,
        certificate: certificatemanager.Certificate.fromCertificateArn(
          this,
          'Certificate',
          certificateArn,
        ),
        endpointType: apigateway.EndpointType.REGIONAL,
      },
      defaultCorsPreflightOptions: corsOptions,
      ...props,
    })

    // Add common Gateway Responses
    this.api.addGatewayResponse('DEFAULT_4XX', {
      type: apigateway.ResponseType.DEFAULT_4XX,
      responseHeaders: {
        'Access-Control-Allow-Origin': `'${isProd ? allowedOrigins[0] : apigateway.Cors.ALL_ORIGINS}'`,
        'Access-Control-Allow-Headers': `'${apigateway.Cors.DEFAULT_HEADERS.join(',')}'`,
        'Access-Control-Allow-Methods': `'${apigateway.Cors.ALL_METHODS}'`,
      },
      templates: {
        'application/json': '{"message":"It seems you are lost"}',
      },
    })

    this.api.addGatewayResponse('UNAUTHORIZED', {
      type: apigateway.ResponseType.UNAUTHORIZED,
      responseHeaders: {
        'Access-Control-Allow-Origin': `'${isProd ? allowedOrigins[0] : apigateway.Cors.ALL_ORIGINS}'`,
        'Access-Control-Allow-Headers': `'${apigateway.Cors.DEFAULT_HEADERS.join(',')}'`,
        'Access-Control-Allow-Methods': `'${apigateway.Cors.ALL_METHODS}'`,
      },
      templates: {
        'application/json': '{"message":"Unauthorized"}',
      },
    })

    const userServiceApi = this.api.root.addResource('userservice')
    const proxyResource = userServiceApi.addResource('{proxy+}')
    const integration = new apigateway.LambdaIntegration(lambdas.userService, {
      proxy: true, // Use Lambda proxy integration for passthrough behavior
    })
    proxyResource.addMethod('ANY', integration, { methodResponses: methodResponses })

    lambdas.userService.addPermission('ApiInvokePermission', {
      principal: new iam.ServicePrincipal('apigateway.amazonaws.com'),
      action: 'lambda:InvokeFunction',
      sourceArn: `arn:aws:execute-api:${process.env.AWS_REGION}:${process.env.AWS_ACCOUNT_ID}:${this.api.restApiId}/*/*/challenge/*`,
    })
  }
}
