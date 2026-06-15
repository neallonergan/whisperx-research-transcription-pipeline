# Activate virtual environment
& ".\whisperx-env\Scripts\Activate.ps1"

# Set the folder containing your .m4a files
$inputFolder = "C:\Users\YourName\Desktop\AUDIO"
$outputFolder = "C:\Users\YourName\Folder\Desktop\TRANSCRIPTION"  # Change if you want to store outputs elsewhere

# Get all .m4a files in the folder
$audioFiles = Get-ChildItem -Path $inputFolder -Filter "*.m4a"

foreach ($file in $audioFiles) {
    $inputPath = $file.FullName
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($file.Name)
    $logPath = Join-Path $outputFolder "$baseName`_log.txt"
    $timePath = Join-Path $outputFolder "$baseName`_time.txt"

    Write-Host ""
    Write-Host ">>> Transcribing: $file.Name"
    Write-Host "    Log: $logPath"

    # Time the WhisperX transcription
    $timeResult = Measure-Command {
        whisperx --diarize "$inputPath" `
                 --model medium.en `
                 --output_dir "$outputFolder" `
                 --language en `
                 --hf YOUR_HUGGING_FACE_TOKEN `
                 --compute_type int8 `
                 --print_progress True `
                 --min_speakers 1 `
                 --max_speakers 8 *> $logPath
    }

    # Save the timing to file
    $timeResult | Out-File $timePath

    Write-Host "Finished: $file.Name"
}
