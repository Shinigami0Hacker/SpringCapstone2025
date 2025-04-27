package com.fpt.recordapp.services;

import android.util.Log;
import android.widget.ProgressBar;

import com.azure.storage.blob.BlobClient;
import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.models.ParallelTransferOptions;

import java.io.File;
import java.util.List;
import java.util.concurrent.atomic.AtomicLong;

public class AzureBlobStorage {
    private final BlobContainerClient containerClient;

    public AzureBlobStorage(BlobContainerClient containerClient) {
        this.containerClient = containerClient;
    }

    @FunctionalInterface
    public interface UploadProgressCallback {
        void onProgress(double percentage, long bytesTransferred, long totalBytes);
    }

    public void uploadFile(String filePath, String blobName, UploadProgressCallback progressHandler) {
        new Thread(() -> {
            try {
                File file = new File(filePath);
                long fileSize = file.length();

                AtomicLong uploadedBytes = new AtomicLong(0);
                BlobClient blobClient = containerClient.getBlobClient(blobName);

                com.azure.storage.blob.models.ParallelTransferOptions options = new ParallelTransferOptions()
                        .setMaxConcurrency(2)
                        .setProgressListener(bytesTransferred -> {
                            uploadedBytes.set(bytesTransferred);
                            double percentage = (double) bytesTransferred * 100 / fileSize;
                            progressHandler.onProgress(percentage, bytesTransferred, fileSize);
                        });
                blobClient.uploadFromFile(file.getAbsolutePath(), options, null, null, null, null, null);

                Log.i(AzureBlobStorage.class.toString(), "Upload completed successfully!");

            } catch (Exception e) {
                Log.e(AzureBlobStorage.class.toString(),"Error uploading file: " + e.getMessage());
            }
        }).start();
    }
}
