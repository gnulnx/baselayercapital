import { Stack, StackProps, RemovalPolicy } from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';

interface TablesStackProps extends StackProps {
  ENV_NAME: string;
  ENV_TYPE: string;
  dynamoRemovalPolicy: RemovalPolicy;
  deleteProtection: boolean;
  pointInTimeRecovery: boolean;
}

export class TablesStack extends Stack {
  constructor(scope: Construct, id: string, props: TablesStackProps) {
    super(scope, id, props);

    const {
      ENV_NAME,
      dynamoRemovalPolicy,
      pointInTimeRecovery,
    } = props;

    // === Holdings Table ===
    new dynamodb.Table(this, `${ENV_NAME}-HoldingsTable`, {
      tableName: `${ENV_NAME}-HoldingsTable`,
      partitionKey: { name: 'PK', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'SK', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: dynamoRemovalPolicy,
      pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: pointInTimeRecovery,
     },
    });

    // === Transactions Table ===
    new dynamodb.Table(this, `${ENV_NAME}-TransactionsTable`, {
      tableName: `${ENV_NAME}-TransactionsTable`,
      partitionKey: { name: 'PK', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'SK', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: dynamoRemovalPolicy,
       pointInTimeRecoverySpecification: {
        pointInTimeRecoveryEnabled: pointInTimeRecovery,
     },
    });

    // Add future tables below, e.g., Loans, LednSnapshots, etc.
  }
}
