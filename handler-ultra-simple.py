import json

def lambda_handler(event, context):
    print("=== ULTRA SIMPLE HANDLER START ===")
    print(f"Event: {event}")
    print(f"Context: {context}")
    
    try:
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Ultra Simple Handler Working',
                'status': 'OK',
                'handler': 'ultra-simple-v1.0'
            })
        }
        
        print("=== RESPONSE CREATED ===")
        print(f"Response: {response}")
        print("=== ULTRA SIMPLE HANDLER END ===")
        
        return response
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
