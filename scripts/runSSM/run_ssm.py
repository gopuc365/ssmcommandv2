import boto3
import argparse
import time

def main():
    parser = argparse.ArgumentParser(description="Run a shell command on an EC2 instance via SSM")
    parser.add_argument('--instance-id', required=True, help='EC2 Instance ID')
    parser.add_argument('--command', required=True, help='Shell command to run')
    parser.add_argument('--region', required=True, help='AWS region (e.g., us-east-1)')
    args = parser.parse_args()

    # Initialize SSM client with the provided region
    ssm = boto3.client('ssm', region_name=args.region)

    print(f"Sending command to EC2 instance {args.instance_id} in region {args.region}...")
    try:
        response = ssm.send_command(
            InstanceIds=[args.instance_id],
            DocumentName='AWS-RunShellScript',
            Parameters={'commands': [args.command]},
        )
    except Exception as e:
        print(f"❌ Failed to send command: {e}")
        return

    command_id = response['Command']['CommandId']
    print(f"✅ Command sent. Command ID: {command_id}")

    # Poll for result
    print("⏳ Waiting for command to complete...")
    status = "Pending"

    while status in ["Pending", "InProgress", "Delayed"]:
        time.sleep(2)
        try:
            result = ssm.get_command_invocation(
                CommandId=command_id,
                InstanceId=args.instance_id,
            )
            status = result['Status']
            print(f"Current status: {status}")
        except Exception as e:
            print(f"⚠️ Error retrieving command invocation: {e}")
            return

    # Print the results
    print("\n📤 --- STDOUT ---")
    print(result.get("StandardOutputContent", "").strip() or "<empty>")

    print("\n❗ --- STDERR ---")
    print(result.get("StandardErrorContent", "").strip() or "<empty>")

    print(f"\n📦 Exit Code: {result.get('ResponseCode')}")

if __name__ == '__main__':
    main()
