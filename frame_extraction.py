import boto3
import os
import subprocess

def extract_frames(event, context):
    input_bucket = event['Records'][0]['s3']['bucket']['name']
    input_key = event['Records'][0]['s3']['object']['key']
    output_bucket = os.environ['OUTPUT_BUCKET']
    output_key = input_key.split('.')[0] + '/'

    # Connect to S3
    s3 = boto3.client('s3')

    # Create a temporary directory to store the extracted frames
    temp_dir = '/tmp/frames'
    os.makedirs(temp_dir, exist_ok=True)

    # Download the input video from S3
    local_input_path = os.path.join(temp_dir, 'input.mp4')
    s3.download_file(input_bucket, input_key, local_input_path)

    # Get the duration of the input video
    cmd = f'ffprobe -i {local_input_path} -show_entries format=duration -v quiet -of csv="p=0"'
    output = subprocess.check_output(cmd, shell=True)
    duration = float(output)

    # Calculate the maximum second to extract frames
    max_second = int(duration) - (int(duration) % 30)

    # Extract frames every 30 seconds using FFmpeg
    output_files = []
    for i in range(30, max_second + 1, 30):
        output_file = f'frame_{i}.jpg'
        output_files.append(output_file)
        output_path = os.path.join(temp_dir, output_file)
        cmd = f'ffmpeg -ss {i} -i {local_input_path} -vf "select=eq(n\,0)" -vframes 1 {output_path}'
        subprocess.run(cmd, shell=True, check=True)

    # Upload the extracted frames to the output S3 bucket
    for output_file in output_files:
        local_output_path = os.path.join(temp_dir, output_file)
        s3.upload_file(local_output_path, output_bucket, output_key + output_file)

    # Clean up the temporary directory
    for file in os.listdir(temp_dir):
        file_path = os.path.join(temp_dir, file)
        os.remove(file_path)
    os.rmdir(temp_dir)
