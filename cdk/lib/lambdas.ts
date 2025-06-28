import { Construct } from 'constructs'
import * as cdk from 'aws-cdk-lib'
import * as lambda from 'aws-cdk-lib/aws-lambda'
import * as iam from 'aws-cdk-lib/aws-iam'
import * as logs from 'aws-cdk-lib/aws-logs'
import { TablesStack } from './tables'
import * as events from 'aws-cdk-lib/aws-events'
import * as targets from 'aws-cdk-lib/aws-events-targets'
import { PythonFunction } from '@aws-cdk/aws-lambda-python-alpha'

interface LambdasProps {
  env: {
    region: string
    account: string
  }
  ENV_NAME: string
  ENV_TYPE: string
  tables: TablesStack
  logRetention: logs.RetentionDays
}

export class Lambdas {
  public readonly fetchDataLambda: lambda.Function

  constructor(scope: Construct, id: string, props: LambdasProps) {
    const { ENV_NAME, ENV_TYPE, tables, logRetention, env } = props

    const lambdaRole = new iam.Role(scope, `${ENV_NAME}-LambdaExecutionRole`, {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
      ],
    })

    const environment = {
      REGION: env.region,
      ENV_NAME,
      ENV_TYPE,
      TABLE_NAME: tables.historicalDataTable.tableName,
    }

    this.fetchDataLambda = new PythonFunction(scope, `${ENV_NAME}-FetchDataLambda`, {
      functionName: `${ENV_NAME}-FetchDataLambda`,
      runtime: lambda.Runtime.PYTHON_3_12,
      memorySize: 512,
      timeout: cdk.Duration.seconds(30),
      architecture: lambda.Architecture.ARM_64,
      entry: '../src/python/lambdas/',
      index: 'fetch_data_lambda.py',
      handler: 'handler',
      logRetention,
      environment,
      role: lambdaRole,
    })

    tables.historicalDataTable.grantReadWriteData(this.fetchDataLambda)

    // schedule the Lambda function to run at specific times
    const schedules = [
      //    cron({ minute: '0', hour: '*' })
      { id: 'every 15 minutes', cron: events.Schedule.rate(cdk.Duration.minutes(15)) }, // every 15 minutes

      { id: 'Morning', cron: events.Schedule.cron({ minute: '0', hour: '12' }) }, // 7am EST
      { id: 'Noon', cron: events.Schedule.cron({ minute: '0', hour: '17' }) }, // 12pm EST
      { id: 'Afternoon', cron: events.Schedule.cron({ minute: '10', hour: '21' }) }, // 4:10pm EST
      // ⚠️ Temporary test schedule — runs every minute
      //   { id: 'TestEveryMinute', cron: events.Schedule.rate(cdk.Duration.minutes(1)) },
    ]

    for (const { id, cron } of schedules) {
      const rule = new events.Rule(scope, `${ENV_NAME}-FetchDataRule-${id}`, {
        schedule: cron,
        enabled: true,
      })

      rule.addTarget(new targets.LambdaFunction(this.fetchDataLambda))
    }
  }
}
