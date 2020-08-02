import boto3
import json

def lambda_handler(event, context):
    
    # call to Rekognition
    
    rekognition = boto3.client('rekognition', region_name='us-east-2')
    bucket_1 = 'testonebuck'
    response = rekognition.compare_faces(
            SimilarityThreshold=0,
            SourceImage={
                'S3Object': {
                    'Bucket': bucket_1,
                    'Name': event['image_1'],
                },
            },
            TargetImage={
                'S3Object': {
                    'Bucket': bucket_1,
                    'Name': event['image_2'],
                },
            },
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps(response['FaceMatches'][0]['Similarity'])
    }