import express from 'express';
import multer from 'multer';
import fs from 'fs';
import axios from 'axios';
import ffmpeg from 'fluent-ffmpeg';

interface TranscriptionData {
    model: string;
    language: string;
    prompt: string;
    response_format: string;
}

const app = express();
const upload = multer({ dest: 'uploads/' });

app.get('/', (req, res) => {
    res.send(`
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="video">
        <input type="submit">
    </form>
    `);
});

app.post('/upload', upload.single('video'), async (req, res) => {
    const video = req.file;

    const inputFile = video.path;
    const compressedFile = await compressAudio(inputFile);

    // You'll need to define the values for these variables
    const srtFile = `srt_${video.filename}.srt`;
    const transcriptionData: TranscriptionData = {
        model: 'whisper-1',
        language: 'zh', 
        prompt: 'prompt',
        response_format: 'srt',
    };
    const apiKey = 'your-api-key';

    await transcribeAudio(compressedFile, srtFile, transcriptionData, apiKey);
    
    res.send('Video processed!');
});

app.listen(3000, () => console.log('Server running on http://localhost:3000'));

async function compressAudio(inputFile: string, targetSize: number = 21): Promise<string> {
    return new Promise((resolve, reject) => {
        const targetSizeBytes = targetSize * 1000 * 1000;
        const outputFileName = `compressed_${inputFile}.mp3`;

        ffmpeg.ffprobe(inputFile, (err, metadata) => {
            if (err) {
                reject(err);
            } else {
                const durationSeconds = metadata.format.duration;
                const targetBitrate = Math.floor((targetSizeBytes * 8) / durationSeconds);
                ffmpeg(inputFile)
                    .audioBitrate(targetBitrate)
                    .output(outputFileName)
                    .on('end', () => {
                        console.log(`目標檔案大小：${targetSize} MB`);
                        console.log(`目標比特率：${targetBitrate / 1000} kbps`);
                        console.log(`壓縮後的檔案已儲存為：${outputFileName}`);
                        resolve(outputFileName);
                    })
                    .on('error', reject)
                    .run();
            }
        });
    });
}

async function transcribeAudio(compressedFile: string, srtFile: string, data: TranscriptionData, apiKey: string) {
    const file = fs.createReadStream(compressedFile);
    const response = await axios.post('https://api.openai.com/v1/audio/transcriptions', data, {
        headers: {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'multipart/form-data'
        },
        data: {
            file: file
        }
    });

    if (response.status === 200) {
        fs.writeFileSync(srtFile, response.data, 'utf-8');
    } else {
        console.error(`Error transcribing audio: ${response.data}`);
        throw new Error(`Error transcribing audio: ${response.data}`);
    }
}