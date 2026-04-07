#!/usr/bin/env python3
"""
Automated API Gateway Setup Script
Creates REST API with /analyze endpoint connected to Lambda
"""

import boto3
import json
import time

def create_api_gateway():
    client = boto3.client('apigateway', region_name='us-east-2')
    lambda_client = boto3.client('lambda', region_name='us-east-2')
    
    print("\n" + "="*60)
    print("🚀 API GATEWAY SETUP - AUTOMATED")
    print("="*60)
    
    # Step 1: Create REST API
    print("\n[1/8] Creating REST API...")
    try:
        api_response = client.create_rest_api(
            name='plagiarism-detection-api',
            description='REST API for plagiarism detection system',
            endpointConfiguration={'types': ['REGIONAL']}
        )
        api_id = api_response['id']
        print(f"✅ API created: {api_id}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 2: Get root resource
    print("\n[2/8] Getting root resource...")
    try:
        resources = client.get_resources(restApiId=api_id)
        root_id = resources['items'][0]['id']
        print(f"✅ Root resource: {root_id}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 3: Create /analyze resource
    print("\n[3/8] Creating /analyze resource...")
    try:
        resource_response = client.create_resource(
            restApiId=api_id,
            parentId=root_id,
            pathPart='analyze'
        )
        resource_id = resource_response['id']
        print(f"✅ Resource created: /analyze ({resource_id})")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 4: Create POST method
    print("\n[4/8] Creating POST method...")
    try:
        client.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            authorizationType='NONE'
        )
        print("✅ POST method created")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 5: Integrate with Lambda
    print("\n[5/8] Integrating with Lambda function...")
    try:
        lambda_arn = f"arn:aws:lambda:us-east-2:093954665664:function:plagiarism-detection"
        
        client.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            type='AWS_PROXY',
            integrationHttpMethod='POST',
            uri=f"arn:aws:apigateway:us-east-2:lambda:path/2015-03-31/functions/{lambda_arn}/invocations"
        )
        print("✅ Lambda integration configured")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Step 6: Add Lambda permission for API Gateway
    print("\n[6/8] Adding Lambda permission for API Gateway...")
    try:
        lambda_client.add_permission(
            FunctionName='plagiarism-detection',
            StatementId=f'apigateway-{api_id}',
            Action='lambda:InvokeFunction',
            Principal='apigateway.amazonaws.com',
            SourceArn=f"arn:aws:execute-api:us-east-2:093954665664:{api_id}/*/*"
        )
        print("✅ Lambda permission granted")
    except lambda_client.exceptions.ResourceConflictException:
        print("✅ Lambda permission already exists")
    except Exception as e:
        print(f"⚠️  Warning: {e}")
    
    # Step 7: Enable CORS
    print("\n[7/8] Enabling CORS...")
    try:
        client.put_method_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            statusCode='200',
            responseModels={'application/json': 'Empty'}
        )
        
        client.put_integration_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='POST',
            statusCode='200',
            responseTemplates={'application/json': ''}
        )
        
        # CREATE OPTIONS method for CORS
        client.put_method(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            authorizationType='NONE'
        )
        
        client.put_integration(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            type='MOCK',
            requestTemplates={'application/json': '{"statusCode": 200}'}
        )
        
        client.put_method_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': True,
                'method.response.header.Access-Control-Allow-Methods': True,
                'method.response.header.Access-Control-Allow-Origin': True
            }
        )
        
        client.put_integration_response(
            restApiId=api_id,
            resourceId=resource_id,
            httpMethod='OPTIONS',
            statusCode='200',
            responseParameters={
                'method.response.header.Access-Control-Allow-Headers': "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
                'method.response.header.Access-Control-Allow-Methods': "'POST,OPTIONS'",
                'method.response.header.Access-Control-Allow-Origin': "'*'"
            }
        )
        
        print("✅ CORS enabled")
    except Exception as e:
        print(f"⚠️  Warning (CORS): {e}")
    
    # Step 8: Deploy API
    print("\n[8/8] Deploying API to 'prod' stage...")
    try:
        deployment = client.create_deployment(
            restApiId=api_id,
            stageName='prod',
            stageDescription='Production stage',
            description='Automated deployment'
        )
        deployment_id = deployment['id']
        print(f"✅ Deployment created: {deployment_id}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Get invoke URL
    invoke_url = f"https://{api_id}.execute-api.us-east-2.amazonaws.com/prod/analyze"
    
    print("\n" + "="*60)
    print("✅ API GATEWAY SETUP COMPLETE!")
    print("="*60)
    print(f"\n📌 Your API Endpoint:")
    print(f"   {invoke_url}")
    print(f"\n📌 API Gateway ID: {api_id}")
    print(f"📌 Region: us-east-2")
    print(f"📌 Stage: prod")
    print(f"\n✅ Next Steps:")
    print(f"   1. Copy the API endpoint above")
    print(f"   2. Update Streamlit dashboard with this endpoint")
    print(f"   3. Test with: curl -X POST {invoke_url}")
    print("\n" + "="*60 + "\n")
    
    return invoke_url

if __name__ == '__main__':
    create_api_gateway()
