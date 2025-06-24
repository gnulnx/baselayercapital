#!/usr/bin/env node
import * as dotenv from 'dotenv'
dotenv.config({ path: '.env.dev', override: true }) // Hard default to .env.dev for local development for NOW

import * as cdk from 'aws-cdk-lib'
import { TablesStack } from '../lib/tables'

// === Read environment ===
const ENV_NAME = process.env.ENV_NAME || 'dev'
const ENV_TYPE = process.env.ENV_TYPE || 'dev'
const ACCOUNT = process.env.AWS_ACCOUNT_ID!
const REGION = process.env.AWS_REGION!
const PROFILE = process.env.AWS_PROFILE!

if (!ACCOUNT || !REGION || !PROFILE) {
  throw new Error('Missing one of: AWS_ACCOUNT_ID, AWS_REGION, AWS_PROFILE')
}

// === CDK App config ===
let dynamoRemovalPolicy = cdk.RemovalPolicy.DESTROY
let deleteProtection = false

if (ENV_TYPE === 'prd') {
  dynamoRemovalPolicy = cdk.RemovalPolicy.RETAIN
  deleteProtection = true
}

// Always use RETAIN for now
dynamoRemovalPolicy = cdk.RemovalPolicy.RETAIN

const stackProps = {
  env: { account: ACCOUNT, region: REGION },
  ENV_NAME,
  ENV_TYPE,
  dynamoRemovalPolicy,
  deleteProtection,
  pointInTimeRecovery: ENV_TYPE === 'prd',
}

// === CDK App ===
const app = new cdk.App()
new TablesStack(app, `${ENV_NAME}-BtcTablesStack`, stackProps)
