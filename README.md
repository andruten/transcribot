# Transcribot

## Environment variables

| Key              | example value | Description                                                                  |
|------------------|---------------|------------------------------------------------------------------------------|
| BOT_TOKEN        | 1234:abcde    | Bot token obtained by Bot father                                             |
| ALLOWED_CHAT_IDS | 1234,5678     | A comma-separated list for allow list groups which can interact with the bot |
| WHISPER_MODEL    | small         | Default tiny                                                                 |
| WHISPER_DEVICE   | cpu           | Default cpu                                                                  |
| WHISPER_COMPUTE_TYPE | int8      | faster-whisper compute type. Default int8                                    |
| WHISPER_CPU_THREADS | 4          | CPU threads used by CTranslate2                                              |
| LOG_LEVEL        | INFO          | Log level of the application                                                 |
