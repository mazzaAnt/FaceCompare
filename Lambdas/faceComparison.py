import json
import boto3
import time
from datetime import datetime
from multiprocessing import Process, Pipe


class RekognitionParallel(object):
    """
    Compares all faces in a list and determines similarity
    using Rekognition
    
    """
    def __init__(self):
        self.s3 = boto3.client('s3', region_name='us-east-2')
        self.bucket_1 = 'testonebuck'

    # function to be run in parallel
    def instance_faces(self, image_1, image_2, process_id, conn):
        """
        Finds similarity metric between two images
        
        """
        
        # Calls lambda to get similarity metric from Rekognition
        # Splittig into multiple lambdas because single lambda instance might be a bottleneck
        # NOTICE - US-EAST-2 Rekognition has a limit of 5 calls per second to compare_faces,
        #          I have a ticket to increase this to 200.
        
        lambda_client = boto3.client('lambda')
        msg = {"key":"new_invocation", "at": str(datetime.now()), "image_1":image_1, "image_2":image_2}
        invoke_response = lambda_client.invoke(FunctionName="callRekognition",
                                               InvocationType='RequestResponse',
                                               Payload=json.dumps(msg))
                        
        JSONresponse = json.loads(invoke_response['Payload'].read().decode())
        
        print(str(process_id) + " Rekognition Response: " + str(JSONresponse))
        print(str(process_id) + " Similarity Metric: " + str(JSONresponse['body']) + " between " + image_1 + " and " + image_2)
        
        conn.send([[image_1, image_2, JSONresponse['body']]])
        conn.close()

    def faceComparison(self):
        """
        Parrallel Rekognition
        
        """
        print ("Running in parallel")
        
        
        # get all Image names in S3 bucket
        response_bucket1 = self.s3.list_objects(Bucket = self.bucket_1)
        imageNames = [ item['Key'] for item in response_bucket1['Contents'] ]
        print("List of Image Names: " + str(imageNames))
        print("Number of Images: " + str(len(imageNames)))
        
        # create a list to keep all processes
        processes = []

        # create a list to keep connections
        parent_connections = []
        
        imageCount = len(imageNames)
        index_counter = 0
        process_id = 0
        # create a process per instance
        for i in range(imageCount):
            for j in range(index_counter, imageCount):
                # create a pipe for communication
                parent_conn, child_conn = Pipe()
                parent_connections.append(parent_conn)
    
                # create the process, pass instance and connection
                process = Process(target=self.instance_faces, args=(imageNames[i], imageNames[j], process_id, child_conn,))
                # as we receive items we can insert them into a map based on the order we iterated over them
                processes.append(process)
                process_id += 1
                
            #counter so we don't do duplicate compares    
            index_counter += 1

        # start all processes
        for process in processes:
            process.start()

        # make sure that all processes have finished
        for process in processes:
            process.join()

        instances_total = []
        for parent_connection in parent_connections:
            instances_total.append(parent_connection.recv()[0])

        return {"imageNamesList": imageNames, "comparisons" : instances_total}



    
def lambda_handler(event, context):
    
    # Run Rekognition in Parallel
    faceCompares = RekognitionParallel()
    allComparisons = faceCompares.faceComparison()
    print("Number of facial comparisons: " + str(len(allComparisons)))
    print("List of all facial comparisons: " + str(allComparisons))

    # return results
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': json.dumps(allComparisons)
    };
    
