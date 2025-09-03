# audio-merge

AWS Lambda function in **Python** for processing audio files stored in **Amazon S3**.  
It allows you to **merge multiple MP3 files into a single track** or **bundle them into a ZIP archive**.  
Perfect for content pipelines, automation workflows, and voiceover generation.

---

## ✨ Features
- 🔑 Authentication via `x-api-key` (validated against the `API_KEY` environment variable)
- 🎵 Merge multiple MP3 files into one unified track (128 kbps bitrate)
- 📦 Create a ZIP archive with the original MP3 files
- ☁️ Automatic upload to Amazon S3
- ⚡ Ready to integrate with API Gateway + Lambda

---

## 🧱 Architecture
```
Client → API Gateway (POST) → Lambda (audio-merge) → S3
```

---

## 📦 Dependencies
- Python 3.10+
- [boto3](https://boto3.amazonaws.com/)
- [pydub](https://github.com/jiaaro/pydub)
- **ffmpeg** (binary packaged in the Lambda layer or deployment package)

> The code appends the directory of `ffmpeg` to the `PATH` automatically.

---

## 🔐 Environment Variables
| Variable   | Description                     | Example         |
|------------|---------------------------------|-----------------|
| `API_KEY`  | Expected key for `x-api-key`    | `supersecret123` |

> The S3 bucket is hardcoded as `dubla-ai`. You can make this configurable by adding a `BUCKET_NAME` environment variable.

---

## 🛣️ Example Request
**POST** `/merge`  

**Headers**
```http
Content-Type: application/json
x-api-key: <your-api-key>
```

**Body**
```json
{
  "output_key": "outputs/project-123/voiceover.mp3",
  "keys": [
    "inputs/seg1.mp3",
    "inputs/seg2.mp3",
    "inputs/seg3.mp3"
  ],
  "type": "unified"  // "unified" | "zip"
}
```

---

## ✅ Responses
### Success (Unified)
```json
{
  "message": "Successfully combined files and uploaded to outputs/project-123/voiceover.mp3",
  "output_key": "outputs/project-123/voiceover.mp3"
}
```

### Success (ZIP)
```json
{
  "message": "Successfully created ZIP file and uploaded to outputs/project-123/voiceover.zip",
  "output_key": "outputs/project-123/voiceover.zip"
}
```

### Forbidden (Invalid API Key)
```json
{
  "message": "Forbidden: Invalid API Key"
}
```
