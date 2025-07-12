#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib'
import { MainStack } from '../lib/main-stack'
import { TablesStack } from '../lib/tables'
import { LambdaLayerStack } from '../lib/lambda-layer-stack'
import { FrontendStack } from '../lib/front-end-stack'
import { execSync } from 'child_process'

execSync(
  'aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws',
  { stdio: 'inherit' },
)

// === Read environment ===
const ENV_NAME = process.env.ENV_NAME || 'dev'
const ENV_TYPE = process.env.ENV_TYPE || 'dev'
const ACCOUNT = process.env.AWS_ACCOUNT_ID!
const REGION = process.env.AWS_REGION!
const PROFILE = process.env.AWS_PROFILE!

console.log(`Deploying ${ENV_NAME} environment in account ${ACCOUNT} and region ${REGION}`)

if (!ACCOUNT || !REGION || !PROFILE) {
  throw new Error('Missing one of: AWS_ACCOUNT_ID, AWS_REGION, AWS_PROFILE')
}

// === CDK App config ===
let dynamoRemovalPolicy = cdk.RemovalPolicy.RETAIN
let deleteProtection = false

const isProd = ENV_NAME === 'prd'
const baseDomain = 'baselayercapital.com'
const domainNameStr = isProd ? 'baselayercapital.com' : `${ENV_NAME}.baselayercapital.com`

const certificateArn =
  'arn:aws:acm:us-east-1:740239033577:certificate/6e15ac94-f0b9-42ee-91c5-45d0c95efa81'

if (isProd) {
  dynamoRemovalPolicy = cdk.RemovalPolicy.RETAIN
  deleteProtection = true
}

const stackProps = {
  env: { account: ACCOUNT, region: REGION },
  ENV_NAME,
  ENV_TYPE,
  isProd,
  baseDomain,
  domainNameStr,
  dynamoRemovalPolicy,
  deleteProtection,
  certificateArn,
  pointInTimeRecovery: ENV_TYPE === 'prd',
}

// === CDK App + Stack Composition ===
const app = new cdk.App()

const layers = new LambdaLayerStack(app, `${ENV_NAME}-BLCLambdaLayerStack`, stackProps)

const tables = new TablesStack(app, `${ENV_NAME}-BtcTablesStack`, stackProps)

const mainStack = new MainStack(app, `${ENV_NAME}-MainStack`, {
  ...stackProps,
  tables,
  layers,
})

new FrontendStack(app, `${ENV_NAME}-FrontendStack`, {
  ...stackProps,
  env: { account: ACCOUNT, region: REGION },
})
