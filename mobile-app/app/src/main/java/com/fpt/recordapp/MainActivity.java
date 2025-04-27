package com.fpt.recordapp;



import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import com.dropbox.core.DbxException;
import com.dropbox.core.DbxRequestConfig;
import com.dropbox.core.oauth.DbxCredential;
import com.dropbox.core.v2.DbxClientV2;

import com.fpt.recordapp.models.DialogueModel;
import com.fpt.recordapp.models.DialogueStatus;
import com.fpt.recordapp.models.SubDialogueModel;

import com.google.gson.Gson;
import androidx.appcompat.app.AlertDialog;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;

import org.json.JSONException;
import org.json.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileInputStream;

import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;

import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Base64;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;

import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;


public class MainActivity extends AppCompatActivity {

    private ImageButton openUserNameInput;

    private static final Logger log = LoggerFactory.getLogger(MainActivity.class);
    private DialogueModel[] dialogueModel;
    private JSONObject config;
    private String CONFIG_DIRECTORY;
    private ListView topicListView;
    private List<String> dialogueNames;
    private List<List<SubDialogueModel>> subDialogueModels = new ArrayList<>();
    private DialogueAdapter dialogueAdapter;
    private String name;
    private boolean[] status;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);


        EdgeToEdge.enable(this);
        setContentView(R.layout.activity_main);
        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.container), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        openUserNameInput = findViewById(R.id.userManagement);
        Button syncButton = findViewById(R.id.syncButton);

        CONFIG_DIRECTORY = Objects.requireNonNull(getExternalFilesDir(null)).getAbsolutePath();

        topicListView = findViewById(R.id.topicListView);

        if (isFirstTimeLogin()){
            popUpUserNameInput();
            CompletableFuture<?> future = CompletableFuture.runAsync(() -> {
                DbxCredential credential = new DbxCredential("", -1L, "", "", "");

                DbxRequestConfig requestConfig = DbxRequestConfig.newBuilder("voice-record").build();

                DbxClientV2 client = new DbxClientV2(requestConfig, credential);
                File configFile = new File(getExternalFilesDir(null), "record_patterns.json");
                try (FileOutputStream outputStream = new FileOutputStream(configFile)) {
                    client.files().downloadBuilder("/voice-record/patterns.json").download(outputStream);
                } catch (DbxException | IOException e) {
                    System.err.println("Error downloading file: " + e.getMessage());
                    e.printStackTrace();
                }
            });
            try {
                future.get(10, TimeUnit.SECONDS);
            } catch (InterruptedException | ExecutionException | TimeoutException e) {
                e.printStackTrace();
            }
            future.thenRun(() -> {
                dialogueModel = getStaticDialogue();
                dialogueNames = new ArrayList<>();
                ArrayList<DialogueStatus> dialogueStatus = new ArrayList<DialogueStatus>();
                initializeFileSystem();

                try {
                    name = (String) config.get("name");
                }
                catch (JSONException exception){
                    exception.printStackTrace();
                }

                int i = 0;
                for (DialogueModel dialogue : dialogueModel) {
                    dialogueNames.add(dialogue.getName());
                    subDialogueModels.add(dialogue.getSubDialogueModels());
                    String topicEncoded = Base64.getEncoder().encodeToString(dialogue.getName().getBytes());
                    try {
                        dialogueStatus.add(new DialogueStatus(
                                dialogue.getName(),
                                (boolean) config.get(topicEncoded)
                        ));
                        i+= 1;
                    } catch (JSONException e) {
                        throw new RuntimeException(e);
                    }
                }
                dialogueAdapter = new DialogueAdapter(MainActivity.this, R.layout.activity_sub_item, dialogueStatus);

                topicListView.setAdapter(dialogueAdapter);

                topicListView.setOnItemClickListener((adapterView, view, index, l) -> {
                    Intent intent = new Intent(MainActivity.this, RecordActivity.class);
                    Gson gson = new Gson();
                    String topicEncoded = Base64.getEncoder().encodeToString(dialogueModel[index].getName().getBytes());
                    File topicDirectory = new File(getExternalFilesDir(null), topicEncoded);
                    if (!topicDirectory.exists()){
                        topicDirectory.mkdirs();
                    }
                    intent.putExtra("dialogue", gson.toJson(subDialogueModels.get(index)));
                    intent.putExtra("topicDirectory", topicDirectory.getAbsolutePath());
                    intent.putExtra("topicName", topicEncoded);
                    intent.putExtra("baseConfigDirectory", CONFIG_DIRECTORY);

                    try {
                        intent.putExtra("userName", config.get("name").toString().toLowerCase());
                    } catch (JSONException e) {
                        intent.putExtra("userName", "Tên của bạn");
                    }

                    startActivity(intent);
                });
                openUserNameInput.setOnClickListener(v -> {
                    popUpUserNameInput();
                });
                syncButton.setOnClickListener(v -> {
                    manualFetching();
                });
            });
        } else {
            dialogueModel = getStaticDialogue();
            dialogueNames = new ArrayList<>();
            ArrayList<DialogueStatus> dialogueStatus = new ArrayList<DialogueStatus>();
            initializeFileSystem();

            try {
                name = (String) config.get("name");
            }
            catch (JSONException exception){
                exception.printStackTrace();
            }

            int i = 0;
            for (DialogueModel dialogue : dialogueModel) {
                dialogueNames.add(dialogue.getName());
                subDialogueModels.add(dialogue.getSubDialogueModels());
                String topicEncoded = Base64.getEncoder().encodeToString(dialogue.getName().getBytes());
                try {
                    dialogueStatus.add(new DialogueStatus(
                            dialogue.getName(),
                            (boolean) config.get(topicEncoded)
                    ));
                    i+= 1;
                } catch (JSONException e) {
                    throw new RuntimeException(e);
                }
            }
            dialogueAdapter = new DialogueAdapter(MainActivity.this, R.layout.activity_sub_item, dialogueStatus);

            topicListView.setAdapter(dialogueAdapter);

            topicListView.setOnItemClickListener((adapterView, view, index, l) -> {
                Intent intent = new Intent(MainActivity.this, RecordActivity.class);
                Gson gson = new Gson();
                String topicEncoded = Base64.getEncoder().encodeToString(dialogueModel[index].getName().getBytes());
                File topicDirectory = new File(getExternalFilesDir(null), topicEncoded);
                if (!topicDirectory.exists()){
                    topicDirectory.mkdirs();
                }
                intent.putExtra("dialogue", gson.toJson(subDialogueModels.get(index)));
                intent.putExtra("topicDirectory", topicDirectory.getAbsolutePath());
                intent.putExtra("topicName", topicEncoded);
                intent.putExtra("baseConfigDirectory", CONFIG_DIRECTORY);

                try {
                    intent.putExtra("userName", config.get("name").toString().toLowerCase());
                } catch (JSONException e) {
                    intent.putExtra("userName", "Tên của bạn");
                }

                startActivity(intent);
            });
            openUserNameInput.setOnClickListener(v -> {
                popUpUserNameInput();
            });
            syncButton.setOnClickListener(v -> {
                manualFetching();
            });
        }
    }

    @Nullable
    private DialogueModel[] getStaticDialogue(){
        StringBuilder builder = new StringBuilder();
        File externalFile = new File(CONFIG_DIRECTORY, "record_patterns.json");

        try (BufferedReader reader = new BufferedReader(new FileReader(externalFile))) {
            String line;
            while ((line = reader.readLine()) != null) {
                builder.append(line);
            }
            Gson gson = new Gson();
            return gson.fromJson(builder.toString(), DialogueModel[].class);

        } catch (IOException e) {
            Toast.makeText(this,
                    "Không thể lấy các cuộc hội thoại",
                    Toast.LENGTH_LONG).show();
        }
        return null;
        }

        private void popUpUserNameInput(){
        LayoutInflater inflater = getLayoutInflater();
        View dialogView = inflater.inflate(R.layout.activity_dialog_input_name, null);
        if (name != null){
            EditText text = dialogView.findViewById(R.id.name);
            text.setText(name);
        }
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        EditText etName = dialogView.findViewById(R.id.name);

        builder.setTitle("Nhập thông tin")
                .setView(dialogView)
                .setPositiveButton("Đăng Nhập", (dialog, which) -> {
                    String inputName = etName.getText().toString().trim();
                    if (!inputName.isEmpty()) {
                        try {
                            updateConfig("name", inputName);
                            byte[] utf8Bytes = inputName.getBytes(java.nio.charset.StandardCharsets.UTF_8);
                            updateConfig("code", Base64.getEncoder().encodeToString(utf8Bytes));
                        }catch (JSONException exception){
                            exception.printStackTrace();
                        }
                        name = inputName;
                        if (!isFirstTimeLogin()){
                            super.recreate();
                        }
                    } else {
                        Toast.makeText(this, "Bạn không được để trống mục này", Toast.LENGTH_SHORT).show();
                    }
                })
                .create()
                .show();
    }

    private boolean isFirstTimeLogin(){
        return !(new File(CONFIG_DIRECTORY, "config.json").exists());
    }

    private void fetchConfigFile() {
        CompletableFuture<?> future = CompletableFuture.runAsync(() -> {
            DbxCredential credential = new DbxCredential();
            DbxRequestConfig requestConfig = DbxRequestConfig.newBuilder("voice-record").build();

            DbxClientV2 client = new DbxClientV2(requestConfig, credential);
            File configFile = new File(getExternalFilesDir(null), "record_patterns.json");
            try (FileOutputStream outputStream = new FileOutputStream(configFile)) {
                client.files().downloadBuilder("/voice-record/patterns.json").download(outputStream);
            } catch (DbxException | IOException e) {
                System.err.println("Error downloading file: " + e.getMessage());
                e.printStackTrace();
            }
        });
        try {
            future.get(10, TimeUnit.SECONDS);
        } catch (InterruptedException | ExecutionException | TimeoutException e) {
            e.printStackTrace();
        }
        future.thenRun(() -> {
            super.recreate();
        });
    }

    private boolean isEligibleForFetching(){
        SharedPreferences sharedPreferences = getSharedPreferences("spam", Context.MODE_PRIVATE);
        String availableTime = sharedPreferences.getString("availableTime", null);
        if (availableTime == null){
            return true;
        }
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");
        LocalDateTime availableTimeFormat = LocalDateTime.parse(availableTime, formatter);
        LocalDateTime now = LocalDateTime.now();

        return now.isAfter(availableTimeFormat);
    }

    private void manualFetching(){
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");
        if (isEligibleForFetching()){
            SharedPreferences sharedPreferences = getSharedPreferences("spam", Context.MODE_PRIVATE);
            SharedPreferences.Editor editor = sharedPreferences.edit();

            editor.putString("availableTime", LocalDateTime.now().plusHours(1).format(formatter));
            editor.apply();
            Toast.makeText(this,
                    "Đồng bộ hóa thành công " + LocalDateTime.now().plusHours(1).format(formatter),
                    Toast.LENGTH_LONG).show();
            fetchConfigFile();
        }
        else {
            Toast.makeText(this,
                    "Xin vui lòng thử lại lúc " + LocalDateTime.now().plusHours(1).format(formatter),
                    Toast.LENGTH_LONG).show();
        }
    }


    private void updateConfig(String field, Object value) throws JSONException {
        config.put(field, value);
        saveConfigFile();
    }

    private void saveConfigFile() {
        File configFile = new File(CONFIG_DIRECTORY, "config.json");
        try (BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(new FileOutputStream(configFile), StandardCharsets.UTF_8))) {
            writer.write(config.toString(4));
        } catch (IOException | JSONException exception) {
            exception.printStackTrace();
        }
    }

    private String readConfigFile() {
        File configFile = new File(CONFIG_DIRECTORY, "config.json");
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

    private void initializeFileSystem() {
        File configDirectory = new File(CONFIG_DIRECTORY);
        if (!configDirectory.exists()){
            configDirectory.mkdirs();
        }
        File configFile = new File(CONFIG_DIRECTORY, "config.json");
        if (!configFile.exists()) {
            try {
                config = new JSONObject();
                config.put("name", null);
                for (int i = 0; i < dialogueModel.length; i++){
                    config.put(Base64.getEncoder().encodeToString(dialogueModel[i].getName().getBytes()), false);
                }
                saveConfigFile();
                return;
            } catch (JSONException exception){
                exception.printStackTrace();
                return;
            }
        }
        try {
            String configContent = readConfigFile();
            config = new JSONObject(configContent);
        } catch (JSONException exception){
            exception.printStackTrace();
        }
    }
}