import * as cdk from 'aws-cdk-lib'
import * as certificatemanager from 'aws-cdk-lib/aws-certificatemanager'
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront'
import * as iam from 'aws-cdk-lib/aws-iam'
import * as route53 from 'aws-cdk-lib/aws-route53'
import * as route53_targets from 'aws-cdk-lib/aws-route53-targets'
import * as s3 from 'aws-cdk-lib/aws-s3'
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment'
import { Construct } from 'constructs'
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins'
import * as path from 'path'

interface FrontendStackProps extends cdk.StackProps {
  env: {
    account: string
    region: string
  }
  ENV_NAME: string
}

export class FrontendStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: FrontendStackProps) {
    super(scope, id, props)

    const ENV_NAME = props.ENV_NAME

    const isProd = ENV_NAME === 'prd'
    const domainName = isProd ? 'baselayercapital.com' : `${ENV_NAME}.baselayercapital.com`
    console.log(`Deploying frontend for domain: ${domainName}`)

    const oai = new cloudfront.OriginAccessIdentity(this, `${ENV_NAME}-BLC-OAI`)

    // S3 bucket to store the frontend assets
    const bucket = new s3.Bucket(this, `${ENV_NAME}-BLCFEBucket`, {
      bucketName: `${ENV_NAME}.baselayercapital.com`,
      //   websiteIndexDocument: 'index.html',
      //   websiteErrorDocument: 'index.html',
      // publicReadAccess: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      autoDeleteObjects: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
    })
    bucket.addToResourcePolicy(
      new iam.PolicyStatement({
        actions: ['s3:GetObject'],
        resources: [bucket.arnForObjects('*')],
        principals: [
          new iam.CanonicalUserPrincipal(oai.cloudFrontOriginAccessIdentityS3CanonicalUserId),
        ],
      }),
    )

    // Determine the certificate ARN based on environment
    const certificateArn =
      'arn:aws:acm:us-east-1:740239033577:certificate/6e15ac94-f0b9-42ee-91c5-45d0c95efa81'

    const certificate = certificatemanager.Certificate.fromCertificateArn(
      this,
      'Certificate',
      certificateArn,
    )

    // CloudFront distribution
    const distribution = new cloudfront.Distribution(this, `${ENV_NAME}-BLC-Distribution`, {
      defaultBehavior: {
        origin: new origins.S3Origin(bucket, { originAccessIdentity: oai }),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
      },
      domainNames: [domainName],
      certificate,
      errorResponses: [
        {
          httpStatus: 403,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
          ttl: cdk.Duration.minutes(1),
        },
        {
          httpStatus: 404,
          responseHttpStatus: 200,
          responsePagePath: '/index.html',
          ttl: cdk.Duration.minutes(1),
        },
      ],
    })

    // const distribution = new cloudfront.CloudFrontWebDistribution(
    //   this,
    //   `${ENV_NAME}-BLC-Distribution`,
    //   {
    //     comment: `${ENV_NAME} distribution for FE ${domainName}`,
    //     originConfigs: [
    //       {
    //         s3OriginSource: {
    //           s3BucketSource: bucket,
    //           originAccessIdentity: oai,
    //         },
    //         behaviors: [{ isDefaultBehavior: true }],
    //       },
    //     ],
    //     viewerCertificate: cloudfront.ViewerCertificate.fromAcmCertificate(certificate, {
    //       aliases: [domainName],
    //     }),
    //     errorConfigurations: [
    //       {
    //         errorCode: 403,
    //         responsePagePath: '/index.html',
    //         responseCode: 200,
    //       },
    //       {
    //         errorCode: 404,
    //         responsePagePath: '/index.html',
    //         responseCode: 200,
    //       },
    //     ],
    //   },
    // )

    // Route 53 DNS record
    const zone = route53.HostedZone.fromLookup(this, `${ENV_NAME}-BLC-HostedZone`, {
      domainName: 'baselayercapital.com',
    })

    const recordName = isProd ? '' : `${ENV_NAME}`

    new route53.ARecord(this, `${ENV_NAME}-BLC-FE-AliasRecord`, {
      zone,
      target: route53.RecordTarget.fromAlias(new route53_targets.CloudFrontTarget(distribution)),
      recordName: recordName,
    })

    // Deploy site contents to S3 bucket
    new s3deploy.BucketDeployment(this, `${ENV_NAME}-BLC-DeployWithInvalidation`, {
      //   sources: [s3deploy.Source.asset('../../frontend/dist')],
      sources: [s3deploy.Source.asset(path.resolve(__dirname, '../../frontend/dist'))],

      destinationBucket: bucket,
      distribution,
      distributionPaths: ['/*'],
      memoryLimit: 1024,
      prune: true,
    })
  }
}
