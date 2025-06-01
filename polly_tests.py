import boto3
import time
import asyncio
import os
from botocore.exceptions import ClientError, NoCredentialsError


class VoiceCreation:
    def __init__(self, text):
        self.polly_client = boto3.client(
            'polly',
            aws_access_key_id='AKIAUJ3VURJ6URQHAQ7O',  # From the IAM CSV
            aws_secret_access_key='0EwigvWe62viiOaxw0q/XTSC6IS9x7CcMqDKcWKN',  # From the IAM CSV
            # Choose a region close to you, e.g., 'us-east-1' for N. Virginia
            region_name='eu-north-1'
        )
        self.text = text

    def upload_to_s3(self, image_path):
        try:
            s3_client = boto3.client('s3',
                                     aws_access_key_id="AKIAUJ3VURJ6X2ADLHIZ",
                                     aws_secret_access_key="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",
                                     region_name='eu-north-1')

            # file_extension = os.path.splitext(image_path)[1]  # e.g., '.png'
            video_key = f"audio/{image_path}"
            s3_client.upload_file(
                image_path,
                "ntiembotbucket",
                video_key,
                ExtraArgs={'ContentType': 'audio/mpeg'}
            )
            url = f"https://ntiembotbucket.s3.eu-north-1.amazonaws.com/{video_key}"
            os.remove(image_path)
            return url
        except ValueError as e:
            print(e)
        except FileNotFoundError:
            print("Video file not found")
        except NoCredentialsError:
            print("AWS credentials not found. Configure using:")
            print("1. AWS CLI: 'aws configure'")
            print("2. Environment variables: AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY")
        except ClientError as e:
            print(f"AWS Client Error: {e.response['Error']['Message']}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")

    def text_to_speech(self):
        # Call Polly to synthesize speech
        try:
            response = self.polly_client.synthesize_speech(
                Text=self.text,
                OutputFormat='mp3',  # WhatsApp-compatible format
                # A natural-sounding voice (see AWS docs for other options)
                VoiceId='Joanna'
            )

            # Save the audio to a file
            output_file = f"audio/response_{int(time.time())}.mp3"
            with open(output_file, 'wb') as out:
                out.write(response['AudioStream'].read())

            url = self.upload_to_s3(output_file)
            return url
        except Exception as e:
            print(e)


# Initialize the Polly client with your credentials
# if __name__ == "__main__":
#     x = VoiceCreation(
#         "Uche Raymond is a minister of the Gospel devoted to preaching the word of God").text_to_speech()
#     print(x)


# async def hello():
#     print("Hello")
# asyncio.run(text_to_speech(
#     "Udochi Raymond is the fastst runner in Pacemark school"))
