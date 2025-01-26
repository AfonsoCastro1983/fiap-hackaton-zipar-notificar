import boto3
import json
import os
import zipfile
import io
from botocore.exceptions import BotoCoreError, ClientError

# Configuração de clientes AWS
ses_client = boto3.client('ses', region_name='us-east-2')
s3_client = boto3.client('s3', region_name='us-east-2')
dynamodb_client = boto3.resource('dynamodb')
bucket = 'amz.video-upload.bucket'

def retornar_dados_video(video_id):
    """Busca informações do vídeo no DynamoDB."""
    table = dynamodb_client.Table("VideosTable")
    try:
        response = table.query(
            IndexName="videoId-index",
            KeyConditionExpression="videoId = :videoId",
            ExpressionAttributeValues={":videoId": video_id}
        )
        return response['Items'][0] if response['Items'] else {}
    except (BotoCoreError, ClientError) as e:
        print(f"Erro ao buscar dados do vídeo: {e}")
        return {}

def zipar_frames(video_id):
    """Compacta os frames de um vídeo e faz o upload do arquivo ZIP para o S3."""
    diretorio_frames = f'videos/{video_id}/frames/'
    arquivo_frames = f'videos/{video_id}/frames.zip'
    zip_buffer = io.BytesIO()

    try:
        response = s3_client.list_objects_v2(Bucket=bucket, Prefix=diretorio_frames)
        if 'Contents' not in response:
            raise ValueError("Nenhum frame encontrado para compactar.")

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for obj in response['Contents']:
                if obj['Size'] > 0:
                    file_obj = s3_client.get_object(Bucket=bucket, Key=obj['Key'])
                    zip_file.writestr(os.path.basename(obj['Key']), file_obj['Body'].read())
        
        zip_buffer.seek(0)
        s3_client.upload_fileobj(zip_buffer, bucket, arquivo_frames)
        return arquivo_frames

    except Exception as e:
        print(f"Erro ao zipar frames: {e}")
        return None

def enviar_email(to, subject, message):
    """Envia e-mail usando o AWS SES."""
    try:
        ses_client.send_email(
            Source=os.getenv('email_sender'),
            Destination={'ToAddresses': [to]},
            Message={
                'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                'Body': {'Html': {'Data': message, 'Charset': 'UTF-8'}}
            }
        )
    except (BotoCoreError, ClientError) as e:
        print(f"Erro ao enviar e-mail para {to}: {e}")

def lambda_handler(event, context):
    """Função Lambda principal."""
    print('Evento recebido:', event)

    try:
        folder_frame = next(
            os.path.dirname(detail['outputFilePaths'][0])
            for group in event['detail']['outputGroupDetails']
            for detail in group['outputDetails']
            if '/frames/' in detail['outputFilePaths'][0]
        )
    except StopIteration:
        return {'statusCode': 404, 'body': json.dumps('Frames não encontrados.')}

    video_id = folder_frame.split('/')[4]
    arquivo_frames = zipar_frames(video_id)
    if not arquivo_frames:
        return {'statusCode': 500, 'body': json.dumps('Erro ao criar arquivo ZIP.')}

    dados_video = retornar_dados_video(video_id)
    if not dados_video:
        return {'statusCode': 404, 'body': json.dumps('Dados do vídeo não encontrados.')}

    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': arquivo_frames},
        ExpiresIn=86400
    )

    message = (
        f"<html><body><p>Olá, seu vídeo '{dados_video.get('videoName', 'desconhecido')}' "
        f"finalizou o processamento. Clique <a href='{presigned_url}'>aqui</a> para baixar.</p></body></html>"
    )
    subject = "Notificação de processamento de vídeo"
    enviar_email(dados_video['user_data']['email'], subject, message)

    dados_video['link_download'] = presigned_url
    dynamodb_client.Table("VideosTable").put_item(Item=dados_video)

    return {'statusCode': 200, 'body': json.dumps('Processo finalizado com sucesso.')}