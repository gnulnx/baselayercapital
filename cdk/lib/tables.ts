import { Stack, StackProps, RemovalPolicy } from 'aws-cdk-lib'
import { Construct } from 'constructs'
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb'

interface TablesStackProps extends StackProps {
  ENV_NAME: string
  ENV_TYPE: string
  dynamoRemovalPolicy: RemovalPolicy
  deleteProtection: boolean
  pointInTimeRecovery: boolean
}

export class TablesStack extends Stack {
  public readonly historicalDataTable: dynamodb.Table
  public readonly mstrKpiTable: dynamodb.Table
  public readonly TxnTable: dynamodb.Table
  public readonly userService: dynamodb.Table

  constructor(scope: Construct, id: string, props: TablesStackProps) {
    super(scope, id, props)

    const { ENV_NAME, dynamoRemovalPolicy, pointInTimeRecovery } = props

    this.TxnTable = new dynamodb.Table(this, `${ENV_NAME}-Transactions`, {
      tableName: `${ENV_NAME}-Transactions`,
      partitionKey: { name: 'PK', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'SK', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: dynamoRemovalPolicy,
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: pointInTimeRecovery,
      },
    })

    this.userService = new dynamodb.Table(this, `${ENV_NAME}-UserService`, {
      tableName: `${ENV_NAME}-UserService`,
      partitionKey: { name: 'PK', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'SK', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: dynamoRemovalPolicy,
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: pointInTimeRecovery,
      },
    })

    // Add a GSI on email
    this.userService.addGlobalSecondaryIndex({
      indexName: 'email-index',
      partitionKey: { name: 'email', type: dynamodb.AttributeType.STRING },
      projectionType: dynamodb.ProjectionType.ALL,
    })

    this.historicalDataTable = new dynamodb.Table(this, `${ENV_NAME}-HistoricalData`, {
      tableName: `${ENV_NAME}-HistoricalData`,
      partitionKey: { name: 'PK', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'SK', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: dynamoRemovalPolicy,
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: pointInTimeRecovery,
      },
    })

    this.mstrKpiTable = new dynamodb.Table(this, `${ENV_NAME}-StrategyKPIs`, {
      tableName: `${ENV_NAME}-StrategyKPIs`,
      partitionKey: { name: 'PK', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'SK', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: dynamoRemovalPolicy,
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: pointInTimeRecovery,
      },
    })
  }
}
