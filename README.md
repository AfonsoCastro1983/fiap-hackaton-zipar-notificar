#  Lambda para Processamento de Vídeos e Notificações via AWS

## Introdução

Este projeto implementa uma função AWS Lambda que processa vídeos enviados para um bucket S3. A solução compacta frames de vídeos em arquivos ZIP, armazena os arquivos compactados no S3, gera links pre-assinados para download e envia notificações por e-mail aos usuários.

O objetivo é demonstrar o uso de serviços AWS, como **Amazon S3**, **AWS Lambda**, **Amazon DynamoDB** e **Amazon SES**, para construir um fluxo automatizado e escalável para processamento de vídeos.

---

## Funcionalidades

1. **Compactação de Frames de Vídeo**:
   - Compacta todos os frames de um vídeo em um arquivo ZIP.
   - Salva o arquivo ZIP em um bucket S3.

2. **Geração de Link Pre-assinado**:
   - Cria um link pre-assinado para download do arquivo ZIP, com validade de 24 horas.

3. **Notificação por E-mail**:
   - Envia um e-mail ao usuário com o link para download do arquivo ZIP.

4. **Atualização no DynamoDB**:
   - Registra as informações de download no DynamoDB, incluindo o link gerado.

---

## Pré-requisitos

1. **Configuração do Amazon S3**:
   - Bucket chamado `amz.video-upload.bucket` configurado para armazenar frames e arquivos ZIP.

2. **Configuração do DynamoDB**:
   - Tabela chamada `VideosTable` com os seguintes atributos:
     - **Partition Key:** `videoId` (String).
     - **Atributos adicionais:** `user_data`, `videoName`, `link_download`.

3. **Configuração do SES**:
   - Um domínio verificado no Amazon SES para envio de e-mails.
   - Configuração da variável de ambiente `email_sender` com o e-mail do remetente.

4. **Permissões IAM**:
   - A função Lambda deve possuir permissões para:
     - Leitura e escrita no Amazon S3.
     - Leitura e gravação no DynamoDB.
     - Envio de e-mails via Amazon SES.

---

## Estrutura do Código

### Principais Componentes

1. **`retornar_dados_video(video_id)`**  
   Busca informações do vídeo na tabela `VideosTable` do DynamoDB com base no `videoId`.

2. **`zipar_frames(video_id)`**  
   Compacta frames de vídeo em um arquivo ZIP e faz o upload para o bucket S3.

3. **`enviar_email(to, subject, message)`**  
   Envia e-mails aos usuários utilizando o Amazon SES.

4. **`lambda_handler(event, context)`**  
   Função principal que:
   - Identifica os frames processados.
   - Compacta os frames em um arquivo ZIP.
   - Gera um link pre-assinado para download.
   - Envia notificação ao usuário e atualiza o DynamoDB.

---

## Configuração e Deploy

### 1. **Configuração do AWS Lambda**
- Crie uma nova função Lambda no console AWS.
- Faça o upload do código como um arquivo `.zip`.
- Configure as variáveis de ambiente:
  ```plaintext
  email_sender=<seu-email-verificado-no-SES>
  ```
- Vincule uma função IAM com permissões apropriadas.

### 2. **Configuração do Amazon S3**
- Crie um bucket chamado `amz.video-upload.bucket`.
- Certifique-se de que o bucket permite operações de leitura e gravação autenticadas.

### 3. **Configuração do DynamoDB**
- Crie uma tabela chamada `VideosTable` com os atributos mencionados nos pré-requisitos.

### 4. **Configuração do SES**
- Verifique o domínio ou endereço de e-mail utilizado para envio.
- Ajuste as permissões para permitir o envio de e-mails através do SES.

---

## Fluxo de Funcionamento

1. **Recebimento de Evento**:
   - O evento recebido contém informações sobre os frames processados.

2. **Compactação de Frames**:
   - Os frames são compactados em um arquivo ZIP e enviados ao S3.

3. **Geração de Link Pre-assinado**:
   - Um link pre-assinado é gerado para download do arquivo ZIP.

4. **Notificação por E-mail**:
   - O usuário é notificado por e-mail com o link para download.

5. **Atualização do DynamoDB**:
   - As informações de download são registradas na tabela `VideosTable`.

---

## Exemplo de Resposta

### Resposta Bem-Sucedida:
```json
{
  "statusCode": 200,
  "body": "Processo finalizado com sucesso."
}
```

### Resposta com Erro:
- Caso os frames não sejam encontrados:
```json
{
  "statusCode": 404,
  "body": "Frames não encontrados."
}
```

- Caso haja falha ao criar o arquivo ZIP:
```json
{
  "statusCode": 500,
  "body": "Erro ao criar arquivo ZIP."
}
```

---

## Diagrama da Arquitetura

```plaintext
[ Usuário ] -> [ Evento de Processamento ] -> [ Lambda Function ]
                          ↘               ↙
                    [ DynamoDB ]     [ S3 Bucket ]
                             ↘         ↙
                          [ SES - Notificação ]
```

---

## Pontos de Aprendizado

- Integração com Amazon S3 para armazenamento e geração de links pre-assinados.
- Uso de Amazon DynamoDB para gerenciamento de metadados.
- Envio de notificações automatizadas via Amazon SES.
- Implementação de fluxos serverless utilizando AWS Lambda.

---

**Apresentação prática:** Durante a demonstração, será exibido o fluxo de compactação de frames, geração do link pre-assinado, envio de notificação e atualização do DynamoDB em tempo real.

