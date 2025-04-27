package com.fpt.recordapp;


import android.content.Intent;

import android.content.pm.PackageManager;
import android.media.MediaPlayer;
import android.media.MediaRecorder;
import android.net.Uri;
import android.os.Bundle;

import android.util.Log;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;


import androidx.appcompat.app.AppCompatActivity;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.FragmentTransaction;


import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.BlobContainerClientBuilder;
import com.fpt.recordapp.models.SubDialogueModel;
import com.fpt.recordapp.services.AzureBlobStorage;
import com.fpt.recordapp.ui.ContentViewFragment;
import com.google.gson.Gson;


import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Random;

//public class RecordActivity extends AppCompatActivity {
//    private TextView timerTextView;
//    private boolean hasBeenRecoreded = false;
//    private static final int PERMISSION_REQUEST_CODE = 200;
//    private MediaRecorder mediaRecorder;
//    private long startTime = 0L;
//    private long pauseTime = System.currentTimeMillis();
//    long elapsedTime = 0;
//    private Handler timerHandler = new Handler();
//    private Runnable timerRunnable = new Runnable(){
//        @Override
//        public void run() {
//            long elapsedTime = pauseTime - startTime;
//            int seconds = (int) (elapsedTime / 1000);
//            int minutes = seconds / 60;
//            int hours = minutes / 60;
//            seconds = seconds % 60;
//            minutes = minutes % 60;
//            timerTextView.setText(String.format("%02d:%02d:%02d", hours, minutes, seconds));
//            timerHandler.postDelayed(this, 1000);
//        }
//    };
//    private String audioFilePath;
//    private boolean isPaused = false;
//    private Button recordButton;
//    private Button pauseButton;
//    private boolean isRecording = false;
//    private String RECORD_DIRECTORY;
//    private String SYSTEM_RECORDING;
//
//    private String sessionID;
//    private File metadata;
//    private ActivityRecordscreenBinding binding;
//    @Override
//    protected void onCreate(Bundle savedInstanceState) {
//        super.onCreate(savedInstanceState);
//        setContentView(R.layout.activity_recordscreen);
//
//        Intent intent = getIntent();
//        sessionID = intent.getStringExtra("sessionID");
//        binding = ActivityRecordscreenBinding.inflate(getLayoutInflater());
//        setContentView(binding.getRoot());
//
//        recordButton = findViewById(R.id.recordButton);
//        pauseButton = findViewById(R.id.pauseButton);
//        timerTextView = findViewById(R.id.timerTextView);
//
//        RECORD_DIRECTORY = new File(getExternalFilesDir(null), "Recordings").getAbsolutePath();
//        SYSTEM_RECORDING = new File(getExternalFilesDir(null), "System").getAbsolutePath();
//        metadata = new File(SYSTEM_RECORDING, "metadata.json");
//
//        initializeFileSystem();
//        recordButton.setOnClickListener(v -> {
//            if (isRecording) {
//                showConfirmStopRecording();
//            } else {
//                if (checkPermission()) {
//                    startRecording();
//                } else {
//                    requestPermission();
//                }
//            }
//        });
//        pauseButton.setOnClickListener(v -> {
//            pauseRecord();
//        });
//    }
//
//
//    private void initializeFileSystem() {
//        File recordDirectory = new File(RECORD_DIRECTORY);
//        File systemDirectory = new File(SYSTEM_RECORDING);
//        if (!recordDirectory.exists()){
//            recordDirectory.mkdirs();
//        }
//        if (!systemDirectory.exists()){
//            systemDirectory.mkdirs();
//        }
//        if (!metadata.exists()){
//            try {
//                metadata.createNewFile();
//            }
//            catch (IOException e) {
//                e.printStackTrace();
//            }
//        }
//    }
//
//    private void showConfirmToLeave(Runnable callback){
//        if (isRecording || isPaused){
//            new androidx.appcompat.app.AlertDialog.Builder(this)
//                    .setTitle("Confirm")
//                    .setMessage("Are you sure stop the record?")
//                    .setPositiveButton("Yes", (dialog, which) -> {
//                        callback.run();
//                    })
//                    .setNegativeButton("No", (dialog, which) -> {
//                        dialog.dismiss();
//                    })
//                    .create()
//                    .show();
//        }
//        else {
//            callback.run();
//        }
//    }
//
//    private boolean checkPermission() {
//        return ContextCompat.checkSelfPermission(this,
//                Manifest.permission.RECORD_AUDIO) ==
//                PackageManager.PERMISSION_GRANTED;
//    }
//
//    private void requestPermission() {
//        ActivityCompat.requestPermissions(this,
//                new String[]{Manifest.permission.RECORD_AUDIO},
//                PERMISSION_REQUEST_CODE);
//    }
//
//
//    private List<String> getFileNamesFromDirectory(File directory){
//        if ( !directory.exists() || !directory.isDirectory()){
//            return List.of();
//        }
//        else {
//            return Stream.of(directory.listFiles())
//                    .filter(file -> file !=!= null && file.isFile())
//                    .map(File::getName)
//                    .collect(Collectors.toList());
//        }
//    }
//    private void showConfirmStopRecording() {
//        new androidx.appcompat.app.AlertDialog.Builder(this)
//                .setTitle("Confirm to stop")
//                .setMessage("Are you sure stop the record?")
//                .setPositiveButton("Yes", (dialog, which) -> {
//                    stopRecording();
//                })
//                .setNegativeButton("No", (dialog, which) -> {
//                    dialog.dismiss();
//                })
//                .create()
//                .show();
//    }
//    private void showPermissionExplanationDialog() {
//        new androidx.appcompat.app.AlertDialog.Builder(this)
//                .setTitle("Microphone Permission Required")
//                .setMessage("This app needs access to your microphone to record audio. " +
//                        "Please grant this permission to continue.")
//                .setPositiveButton("Request Again", (dialog, which) -> {
//                    requestPermission();
//                })
//                .setNegativeButton("Cancel", (dialog, which) -> {
//                    dialog.dismiss();
//                    Toast.makeText(this,
//                            "App cannot record audio without microphone permission",
//                            Toast.LENGTH_LONG).show();
//                })
//                .create()
//                .show();
//    }
//
//    private void startRecording() {
//        LocalDateTime now = LocalDateTime.now();
//
//        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd_HH-mm");
//        String formattedTimestamp = now.format(formatter);
//
//        audioFilePath = new File(RECORD_DIRECTORY,
//                "Recording_" + formattedTimestamp + "_" + String.valueOf(sessionID) + ".mp3").getAbsolutePath();
//
//
//        mediaRecorder = new MediaRecorder();
//        try {
//            if (android.os.Build.VERSION.SDK_INT >=
//                    android.os.Build.VERSION_CODES.S) {
//                mediaRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
//                mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
//                mediaRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AAC);
//                mediaRecorder.setOutputFile(audioFilePath);
//                mediaRecorder.setAudioChannels(1); // Mono
//                mediaRecorder.setAudioSamplingRate(44100);
//                mediaRecorder.setAudioEncodingBitRate(128000);
//            } else {
//                mediaRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
//                mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
//                mediaRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AAC);
//                mediaRecorder.setOutputFile(audioFilePath);
//            }
//
//            mediaRecorder.prepare();
//            mediaRecorder.start();
//            pauseButton.setVisibility(View.VISIBLE);
//            isRecording = true;
//
//            startTime = System.currentTimeMillis();
//            timerHandler.postDelayed(timerRunnable, 0);
//
//            recordButton.setText("Stop Recording");
//            Toast.makeText(this, "Recording Started", Toast.LENGTH_SHORT).show();
//        } catch (IOException e) {
//            e.printStackTrace();
//            Toast.makeText(this, "Recording Failed: " + e.getMessage(),
//                    Toast.LENGTH_SHORT).show();
//        }
//    }
//
//    private void pauseRecord(){
//        if (isRecording){
//            if (!isPaused){
//                isPaused = true;
//                mediaRecorder.pause();
//                pauseTime = System.currentTimeMillis();
//                pauseButton.setText("CONTINUTE");
//                timerHandler.removeCallbacks(timerRunnable);
//            }else {
//                mediaRecorder.resume();
//                startTime = System.currentTimeMillis();
//                timerHandler.postDelayed(timerRunnable, 0);
//                isPaused = false;
//                pauseButton.setText("PAUSE");
//            }
//        }
//    }
//
//    private void stopRecording() {
//        if (mediaRecorder != null) {
//            try {
//                mediaRecorder.stop();
//                mediaRecorder.release();
//                mediaRecorder = null;
//                isRecording = false;
//                pauseButton.setVisibility(View.INVISIBLE);
//                timerHandler.removeCallbacks(timerRunnable);
//                timerTextView.setText("00:00:00");
//                recordButton.setText("Start Recording");
//                Toast.makeText(this, "Recording Saved: " + audioFilePath,
//                        Toast.LENGTH_SHORT).show();
//
//            } catch (IllegalStateException e) {
//                e.printStackTrace();
//                Toast.makeText(this, "Error stopping recording",
//                        Toast.LENGTH_SHORT).show();
//            }
//        }
//    }
//
//    @Override
//    protected void onStop() {
//        super.onStop();
//        if (isRecording) {
//            stopRecording();
//        }
//    }
//
//}


public class RecordActivity extends AppCompatActivity {
    private JSONObject recordStatus = new JSONObject();
    private JSONObject uploadStatus = new JSONObject();
    private String topicName;
    private final String recordStatusPath = "record_status.json";
    private final String uploadStatusPath = "upload_status.json";

    private class RecordEntity {
        public boolean hasBeenUploaded;
        public boolean hasBeenRecorded;
        private int id;
        private MediaRecorder mediaRecorder;
        private final File audioFile;

        public boolean isRecording;
        private final RecordActivity ctx;

        private boolean isExist;
        public RecordEntity(RecordActivity ctx, int id, Boolean hasBeenRecorded, Boolean hasBeenUploaded) {
            this.ctx = ctx;
            this.id = id;
            this.hasBeenRecorded = hasBeenRecorded;
            this.hasBeenUploaded = hasBeenUploaded;

            audioFile = new File(topicDirectory,
                    String.valueOf(id) + ".mp3");
        }
        public void setUploadDone(){
            this.hasBeenUploaded = true;
        }
        public void startRecord() {
            mediaRecorder = new MediaRecorder();
            try {
                if (android.os.Build.VERSION.SDK_INT >=
                        android.os.Build.VERSION_CODES.S) {
                    mediaRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
                    mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
                    mediaRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AAC);
                    mediaRecorder.setOutputFile(audioFile);
                    mediaRecorder.setAudioChannels(1);
                    mediaRecorder.setAudioSamplingRate(44100);
                    mediaRecorder.setAudioEncodingBitRate(128000);
                } else {
                    mediaRecorder.setAudioSource(MediaRecorder.AudioSource.MIC);
                    mediaRecorder.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4);
                    mediaRecorder.setAudioEncoder(MediaRecorder.AudioEncoder.AAC);
                    mediaRecorder.setOutputFile(audioFile);
                }

                mediaRecorder.prepare();
                mediaRecorder.start();
                isRecording = true;

                Toast.makeText(this.ctx, "Bắt đầu ghi âm!", Toast.LENGTH_SHORT).show();

            } catch (IOException e) {
                e.printStackTrace();
                Toast.makeText(this.ctx, "Ghi âm thất bại!" + e.getMessage(),
                        Toast.LENGTH_SHORT).show();
            }
        }

        private void stopRecording() {
            if (mediaRecorder != null) {
                try {
                    mediaRecorder.stop();
                    mediaRecorder.release();
                    mediaRecorder = null;
                    isRecording = false;
                    startButton.setText("Bắt đầu");
                } catch (IllegalStateException e) {
                    e.printStackTrace();
                    Toast.makeText(this.ctx, "Ghi âm thất bại!",
                            Toast.LENGTH_SHORT).show();
                }
            }
        }

        private String getBlobUri(){
            return userCode + "/" + topicName + "/" + id + ".mp3";
        }

        private void deleteRecord() {
            if (!this.hasBeenRecorded){
                Toast.makeText(this.ctx,
                        "Bạn chưa thu âm!",
                        Toast.LENGTH_LONG).show();
            }
            else {
                boolean deleted = audioFile.delete();
                if (deleted) {
                    Toast.makeText(this.ctx,
                            "Xóa bản thu thành công!",
                            Toast.LENGTH_LONG).show();
                }
                else {
                    Toast.makeText(this.ctx,
                            "Xóa bản thu thất bại!",
                            Toast.LENGTH_LONG).show();
                }
            }
        }

        public void setRecordDone(boolean done) {
            hasBeenRecorded = done;
        }
    }
    private void updateRecordStatus(String field, Object value) throws JSONException {
        recordStatus.put(field, value);
        saveConfigFile(recordStatusPath, recordStatus);
    }

    private void updateUploadStatus(String field, Object value) throws JSONException {
        recordStatus.put(field, value);
        saveConfigFile(uploadStatusPath, recordStatus);
    }


    private Map<Integer, String> numberToWordMapper = new HashMap<Integer, String>() {{
        put(0, "không");
        put(1, "một");
        put(2, "hai");
        put(3, "ba");
        put(4, "bốn");
        put(5, "năm");
        put(6, "sáu");
        put(7, "bảy");
        put(8, "tám");
        put(9, "chín");
    }};

    private TextView statusText;
    private int currentIndex = 0;
    private List<SubDialogueModel> subDialogueModels;
    private String topicDirectory;

    private void parseSubDialogue(String jsonData) {
        Gson gson = new Gson();
        subDialogueModels = new ArrayList<>(Arrays.asList(gson.fromJson(jsonData, SubDialogueModel[].class)));
        replacePatternToSentence();
    }

    private List<RecordEntity> recordEntities = new ArrayList<>();
    private String name;
    private Button replayButton;
    private ProgressBar progressBar;
    private String baseConfigDDirectory;
    private Button startButton;
    private boolean isUploading;

    private static final int PERMISSION_REQUEST_CODE = 200;

    private String userCode;

    private AzureBlobStorage uploadService;
    private RecordEntity getCurrentRecordEntity() {
        return recordEntities.get(currentIndex);
    }

    private void initializeRecordsList() throws JSONException {
        for (SubDialogueModel subDialogueModel : subDialogueModels) {
            int id = subDialogueModel.getId();
            try {
                recordEntities.add(new RecordEntity(
                        this,
                        id,
                        (Boolean) recordStatus.get(String.valueOf(id)),
                        (Boolean)  uploadStatus.get(String.valueOf(id))
                ));
            }
            catch (JSONException exception){
                updateRecordStatus(String.valueOf(id), false);
                updateUploadStatus(String.valueOf(id), false);
                recordEntities.add(new RecordEntity(
                        this,
                        id,
                        false,
                        false
                        ));
            }
        }
    }

    private void disableStartButton(){
        startButton.setEnabled(false);
        startButton.setText("-");
    }

    private void enableStartButton(){
        startButton.setEnabled(true);
        startButton.setText("Bắt đầu");
    }

    private boolean checkOnGoingTask(){
        return isRecording || isUploading;
    }



    private void startRecording() {
        RecordEntity recordEntity = recordEntities.get(currentIndex);
        recordEntity.startRecord();
        isRecording = true;
        disableStartButton();
    }

    private void stopRecord()  {
        RecordEntity recordEntity = recordEntities.get(currentIndex);
        isRecording = false;
        recordEntity.setRecordDone(true);
        recordEntity.stopRecording();
        Toast.makeText(this, "Ghi âm hoàn tất", Toast.LENGTH_SHORT).show();
        try {
            updateRecordStatus(String.valueOf(currentIndex + 1), true);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        enableStartButton();
        updateUI();
    }

    private void replayRecord() {
        RecordEntity recordEntity = recordEntities.get(currentIndex);
        if (recordEntity.hasBeenRecorded && ! isRecording) {
            File audioFile = recordEntity.audioFile;
            MediaPlayer mediaPlayer = new MediaPlayer();
            try {
                mediaPlayer.setDataSource(this, Uri.fromFile(audioFile.getAbsoluteFile()));
                mediaPlayer.prepare();
                mediaPlayer.start();
            } catch (IOException e) {
                e.printStackTrace();
            }
        } else {
            Toast.makeText(this, "Không tìm thấy bản ghi đã thu!", Toast.LENGTH_SHORT).show();
        }

    }

    private void next() {
        if (checkOnGoingTask()){
            Toast.makeText(this,
                    "Bạn đang ghi âm/tải file lên",
                    Toast.LENGTH_LONG).show();
        }
        if (currentIndex + 1 == subDialogueModels.size()) {
            Toast.makeText(this,
                    "Bạn đang ở cuộc hội thoại cuối cùng",
                    Toast.LENGTH_LONG).show();
            return;
        }
        currentIndex += 1;
        updateUI();
    }

    private boolean isRecording = false;

    private void previous() {
        if (checkOnGoingTask()){
            Toast.makeText(this,
                    "Bạn đang ghi âm/tải file lên",
                    Toast.LENGTH_LONG).show();
        }
        if (currentIndex == 0) {
            Toast.makeText(this,
                    "Bạn đang ở cuộc hội thoại cuối cùng",
                    Toast.LENGTH_LONG).show();
            return;
        }
        currentIndex -= 1;
        updateUI();
    }
    private void setupBlobConnection(){
        String CONTAINER_NAME = "records";
        BlobContainerClient containerClient = new BlobContainerClientBuilder()
                .connectionString(CONNECTION_STRING)
                .containerName(CONTAINER_NAME)
                .buildClient();
        uploadService = new AzureBlobStorage(containerClient);
    }


    private void uploadFileToAzureBlobStorage(File file, String blobUri) throws IOException {
        if (!file.exists()){
            Toast.makeText(
                    this,
                    "The file is not exist.",
                    Toast.LENGTH_SHORT
            ).show();
        }
        String filePath = file.getAbsolutePath();
        uploadService.uploadFile(
                filePath,
                blobUri,
                (percentage, transferred, total) -> {
                    progressBar.setProgress((int) percentage);
                }
                );
        isUploading = false;
        updateUI();
    }


    private List<String> numberEncoder(Integer num) {
        List<String> wordNumber = new ArrayList<>();
        while (num != 0) {
            wordNumber.add(numberToWordMapper.get(num % 10));
            num /= 10;
        }
        return wordNumber;
    }

    private void replacePatternToSentence() {
        for (SubDialogueModel subDialogueModel : subDialogueModels) {
            if (subDialogueModel.getSentence().contains("{{name}}")) {
                subDialogueModel.setSentence(subDialogueModel.getSentence().replace("{{name}}", Objects.requireNonNull(name)));
            }
            if (subDialogueModel.getSentence().contains("{{random}}")) {
                int sizeNumbers = subDialogueModel.getSentence().split("\\{\\{random\\}\\}", -1).length - 1;
                for (int i = 0; i < sizeNumbers; i++) {
                    subDialogueModel.setSentence(subDialogueModel.getSentence().replaceFirst("\\{\\{random\\}\\}", String.join(" ", numberEncoder(new Random().nextInt(100)))));
                }
            }
            if (subDialogueModel.getSentence().contains("{{type}}")) {
                List<String> types = List.of("A", "B", "C");
                Random random = new Random();
                String type = types.get(random.nextInt(types.size()));
                subDialogueModel.setSentence(subDialogueModel.getSentence().replace("{{type}}", type));
            }
        }
    }


    private boolean checkAllUploadStatus(){
        for (Iterator<String> it = uploadStatus.keys(); it.hasNext(); ) {
            String key = it.next();
            try {
                Boolean value = (Boolean) uploadStatus.get(key);
                if (!value) {
                    return false;
                }
            }
            catch (JSONException e){
                return false;
            }
        }
        return true;
    }
    private void updateBaseConfig() {
        File configFile = new File(baseConfigDDirectory, "config.json");
        StringBuilder content = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(new FileInputStream(configFile), StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                content.append(line).append("\n");
            }
        } catch (IOException exception) {
            exception.printStackTrace();
        }
        try {
            JSONObject baseConfig = new JSONObject(content.toString());
            baseConfig.put(topicName, true);
            try (BufferedWriter writer = new BufferedWriter(
                    new OutputStreamWriter(new FileOutputStream(configFile), StandardCharsets.UTF_8))) {
                writer.write(baseConfig.toString(4));
            } catch (IOException | JSONException exception) {
                exception.printStackTrace();
            }
        } catch (JSONException exception){
            exception.printStackTrace();
        }
    }

    private TextView uploadStatusText;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_record);
        Intent intent = getIntent();


        ImageButton previousBtn = findViewById(R.id.previous);
        ImageButton nextBtn = findViewById(R.id.next);
        String dialogue = intent.getStringExtra("dialogue");

        name = intent.getStringExtra("userName");
        topicDirectory = intent.getStringExtra("topicDirectory");
        userCode = Base64.getEncoder().encodeToString(name.getBytes());
        topicName = intent.getStringExtra("topicName");
        baseConfigDDirectory = intent.getStringExtra("baseConfigDirectory");

        statusText = findViewById(R.id.statusText);
        uploadStatusText = findViewById(R.id.uploadStatusText);
        progressBar = findViewById(R.id.uploadProgress);
        startButton = findViewById(R.id.startButton);
        Button stopButton = findViewById(R.id.stopButton);
        replayButton = findViewById(R.id.replayButton);
        Button deleteButton = findViewById(R.id.deleteButton);
        Button uploadButton = findViewById(R.id.uploadButton);

        parseSubDialogue(dialogue);
        initializeRecordStatus();
        initializeUploadStatus();

        try {
            initializeRecordsList();
        } catch (JSONException e) {
            throw new RuntimeException(e);
        }

        replacePatternToSentence();

        setupBlobConnection();

        if (savedInstanceState == null) {
            updateUI();
        }
        nextBtn.setOnClickListener((v) -> {
            next();
        });
        previousBtn.setOnClickListener((v) -> {
            previous();
        });
        startButton.setOnClickListener(v -> {
            if (checkPermission()) {
                startRecording();
            } else {
                requestPermission();
            }
        });
        stopButton.setOnClickListener(v -> {
            if (isRecording){
                stopRecord();
            }
        });

        replayButton.setOnClickListener(v -> {
            replayRecord();
        });

        deleteButton.setOnClickListener(v -> {
            deleteRecord();
            try {
                updateRecordStatus(String.valueOf(currentIndex + 1), false);
                updateUploadStatus(String.valueOf(currentIndex + 1), false);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        });
        uploadButton.setOnClickListener(v -> {
            try {
                upload();
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        });
    }

    private void upload() throws IOException {
        if (!isRecording){
            RecordEntity recordEntity = recordEntities.get(currentIndex);
            if (recordEntity.hasBeenRecorded){
                String blobUri = recordEntity.getBlobUri();
                File audioFile = recordEntity.audioFile;
                uploadFileToAzureBlobStorage(audioFile, blobUri);
                if (checkAllUploadStatus()){
                    updateBaseConfig();
                }
                updateBaseConfig();
                recordEntity.setUploadDone();

                try {
                    updateUploadStatus(String.valueOf(currentIndex) + 1, true);
                } catch (JSONException e) {
                    e.printStackTrace();
                }

                updateUI();
            }
        }
        else {
            Toast.makeText(this, "Bạn không thể tải bản ghi lên khi đang ghi âm!",
                    Toast.LENGTH_SHORT).show();
        }
    }

    private void deleteRecord(){
        RecordEntity recordEntity = recordEntities.get(currentIndex);
        recordEntity.deleteRecord();
    }
    private void saveConfigFile(String type, JSONObject config) {
        File configFile = new File(topicDirectory, type);
        try (BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(new FileOutputStream(configFile), StandardCharsets.UTF_8))) {
            writer.write(config.toString(4));
        } catch (IOException | JSONException exception) {
            exception.printStackTrace();
        }
    }

    private void initializeRecordStatus() {
        File topicBaseDirectory = new File(topicDirectory);

        if (!topicBaseDirectory.exists()){
            topicBaseDirectory.mkdirs();
        }
        File configFile = new File(topicBaseDirectory, recordStatusPath);

        if (!configFile.exists()) {
            try {
                recordStatus = new JSONObject();
                for (int i = 1; i < subDialogueModels.size() + 1; i++){
                    recordStatus.put(String.valueOf(i), false);
                }
                saveConfigFile(recordStatusPath, recordStatus);
                return;
            } catch (JSONException exception){
                exception.printStackTrace();
                return;
            }
        }
        try {
            String configContent = readFileInCurrentDirectory(recordStatusPath);
            recordStatus = new JSONObject(configContent);
        } catch (JSONException exception){
            exception.printStackTrace();
        }
    }

    private void initializeUploadStatus() {
        File topicBaseDirectory = new File(topicDirectory);

        if (!topicBaseDirectory.exists()){
            topicBaseDirectory.mkdirs();
        }
        File configFile = new File(topicBaseDirectory, uploadStatusPath);

        if (!configFile.exists()) {
            try {
                uploadStatus = new JSONObject();
                uploadStatus.put("name", null);
                for (int i = 1; i < subDialogueModels.size() + 1; i++){
                    uploadStatus.put(String.valueOf(i), false);
                }
                saveConfigFile(recordStatusPath, uploadStatus);
                return;
            } catch (JSONException exception){
                exception.printStackTrace();
                return;
            }
        }
        try {
            String configContent = readFileInCurrentDirectory(uploadStatusPath);
            uploadStatus = new JSONObject(configContent);
        } catch (JSONException exception){
            exception.printStackTrace();
        }
    }

    private String readFileInCurrentDirectory(String fileName) {
        File configFile = new File(topicDirectory, fileName);
        StringBuilder content = new StringBuilder();
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(new FileInputStream(configFile), StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                content.append(line).append("\n");
            }
        } catch (IOException exception) {
            exception.printStackTrace();
        }
        return content.toString();
    }

    private boolean getRecordStatus(){
        return recordEntities.get(currentIndex).hasBeenRecorded;
    }

    private boolean getUploadStatus(){
        return recordEntities.get(currentIndex).hasBeenUploaded;
    }
    private void updateUI() {
        String newType = subDialogueModels.get(currentIndex).getType();
        String newSentence = subDialogueModels.get(currentIndex).getSentence();
        String newExplanation = subDialogueModels.get(currentIndex).getExplanation();

        if (getRecordStatus()){
            statusText.setText("Trạng thái ghi âm: Đã ghi âm");
        }
        else {
            statusText.setText("Trạng thái ghi âm: Chưa ghi âm");
        }

        if (getUploadStatus()){
            uploadStatusText.setText("Trạng thái tải lên: Đã tải lên");
        }
        else {
            uploadStatusText.setText("Trạng thái tải lên: Chưa tải lên");
        }
        ContentViewFragment newFragment = ContentViewFragment.newInstance(newType, newSentence, newExplanation);

        FragmentTransaction transaction = getSupportFragmentManager().beginTransaction();
        transaction.replace(R.id.fragment_container, newFragment);

        transaction.commit();
    }

    private boolean checkPermission() {
        return ContextCompat.checkSelfPermission(this,
                android.Manifest.permission.RECORD_AUDIO) ==
                PackageManager.PERMISSION_GRANTED;
    }

    private void requestPermission() {
        ActivityCompat.requestPermissions(this,
                new String[]{android.Manifest.permission.RECORD_AUDIO},
                PERMISSION_REQUEST_CODE);
    }
}