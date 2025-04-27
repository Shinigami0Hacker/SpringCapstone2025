package com.fpt.recordapp;


import android.content.Context;
import android.content.Intent;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;

import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.BlobContainerClientBuilder;
import com.fpt.recordapp.databinding.ActivityFileViewBinding;
import com.fpt.recordapp.services.AzureBlobStorage;

import java.io.File;
import java.io.IOException;

public class FileViewActivity extends AppCompatActivity {

    private ActivityFileViewBinding binding;
    AzureBlobStorage uploadService;
    boolean isUploading = false;
    ProgressBar progressBar;
    TextView uploadPercentage;
    private String filePath;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityFileViewBinding.inflate(getLayoutInflater());

        setContentView(binding.getRoot());
        Intent intent = getIntent();
        filePath = intent.getStringExtra("selectedFile");
        progressBar = findViewById(R.id.downloadBar);
        uploadPercentage = findViewById(R.id.progressPercentage);
        Button uploadButton = findViewById(R.id.uploadButton);
        setupBlobConnection();

        uploadButton.setOnClickListener(
                v -> {
                    File file = new File(filePath);
                    try {
                        if (!isWifiConnected()){
                            uploadFileToAzureBlobStorage(file);
                        }
                        else {
                            Toast.makeText(this,
                                    "Don't have wifi-connection! Please connect wifi to upload.",
                                    Toast.LENGTH_LONG).show();
                        }
                    } catch (IOException e) {
                        Toast.makeText(this, "Something went wrong!", Toast.LENGTH_SHORT).show();
                    }
                }
        );

        TextView fileTextView = findViewById(R.id.recordName);
        fileTextView.setText(new File(filePath).getName());
    }

    private void setupBlobConnection(){
        String CONNECTION_STRING = "";
        String CONTAINER_NAME = "records";
        BlobContainerClient containerClient = new BlobContainerClientBuilder()
                .connectionString(CONNECTION_STRING)
                .containerName(CONTAINER_NAME)
                .buildClient();
        uploadService = new AzureBlobStorage(containerClient);
    }

    private boolean isWifiConnected() {
        WifiManager wifiManager = (WifiManager) getSystemService(Context.WIFI_SERVICE);
        if (wifiManager != null) {
            WifiInfo wifiInfo = wifiManager.getConnectionInfo();
            return wifiInfo != null && wifiInfo.getNetworkId() != -1;
        }
        return false;
    }

    private void uploadFileToAzureBlobStorage(File file) throws IOException {
        isUploading = true;
        uploadPercentage.setVisibility(TextView.VISIBLE);

        if (!file.exists()){
            Toast.makeText(
                    this,
                    "The file is not exist.",
                    Toast.LENGTH_SHORT
            ).show();
        }
        String filePath = file.getAbsolutePath();
        String fileName = file.getName();
        uploadService.uploadFile(
                filePath,
                fileName,
                (percentage, transferred, total) -> {
                    progressBar.setProgress((int) percentage);
                    uploadPercentage.setText(percentage + " %");
                }
        );
//        Files.setAttribute(file.toPath(), "sync", "yes");
        isUploading = false;
    }
}
