#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib'
import { TablesStack } from '../lib/tables'

const ENV_NAME = (process.env.ENV_NAME as string) || 'dev'
const ENV_TYPE = (process.env.ENV_TYPE as string) || 'dev'
const ACCOUNT = (process.env.AWS_ACCOUNT_ID as string) || '123456789012'
const REGION = (process.env.AWS_REGION as string) || 'us-east-1'
const AWS_PROFILE = (process.env.AWS_PROFILE as string) || 'blx-dev'

// switch to the correct AWS profile
process.env.AWS_PROFILE = AWS_PROFILE

let dynamoRemovalPolicy = cdk.RemovalPolicy.DESTROY
let deleteProtection = false
if (ENV_TYPE === 'prd') {
  dynamoRemovalPolicy = cdk.RemovalPolicy.RETAIN
  deleteProtection = true
}

dynamoRemovalPolicy = cdk.RemovalPolicy.RETAIN // Temporary force while we try to relocate tables to new stack

const stackProps = {
  env: { account: ACCOUNT, region: REGION },
  ENV_NAME: ENV_NAME,
  ENV_TYPE: ENV_TYPE,
  dynamoRemovalPolicy: dynamoRemovalPolicy,
  deleteProtection: deleteProtection,
  pointInTimeRecovery: ENV_TYPE === 'prd' ? true : false,
}

const app = new cdk.App()
new TablesStack(app, `${ENV_NAME}-BlcTablesStack`, stackProps)
