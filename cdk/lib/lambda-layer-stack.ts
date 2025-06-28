// lib/lambda-layer-stack.ts
import * as pythonLambda from '@aws-cdk/aws-lambda-python-alpha'
import { Stack, StackProps } from 'aws-cdk-lib'
import * as lambda from 'aws-cdk-lib/aws-lambda'
import { Construct } from 'constructs'
import * as path from 'path'

interface LambdaLayerStackProps extends StackProps {
  ENV_NAME: string
}

export class LambdaLayerStack extends Stack {
  public readonly common: pythonLambda.PythonLayerVersion

  constructor(scope: Construct, id: string, props: LambdaLayerStackProps) {
    super(scope, id, props)

    const { ENV_NAME } = props

    // this.common = new pythonLambda.PythonLayerVersion(this, `${ENV_NAME}-common_v1`, {
    //   layerVersionName: `${ENV_NAME}-common_v1`,
    //   entry: path.join(__dirname, '../../src/python/layers/common_v1/'),
    //   compatibleRuntimes: [lambda.Runtime.PYTHON_3_12],
    //   description: 'A common layer for Python Lambda',
    // })

    this.common = new pythonLambda.PythonLayerVersion(this, `${ENV_NAME}-common_v1`, {
      layerVersionName: `${ENV_NAME}-common_v1`,
      entry: path.join(__dirname, '../../src/python/layers/common_v1/'),
      compatibleRuntimes: [lambda.Runtime.PYTHON_3_12],
      description: 'A common layer for Python Lambda',
      bundling: {
        image: lambda.Runtime.PYTHON_3_12.bundlingImage,
        command: [
          'bash',
          '-c',
          ['pip install -r requirements.txt -t /asset-output/python'].join(' && '),
        ],
      },
    })
  }
}
