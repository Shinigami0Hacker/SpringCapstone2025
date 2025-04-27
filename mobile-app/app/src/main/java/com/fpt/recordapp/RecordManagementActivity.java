package com.fpt.recordapp;

import android.content.Intent;
import android.os.Bundle;

import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.Toast;

import androidx.activity.EdgeToEdge;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.graphics.Insets;
import androidx.core.view.ViewCompat;
import androidx.core.view.WindowInsetsCompat;


import java.io.File;
import java.util.Arrays;

public class RecordManagementActivity extends AppCompatActivity {

    ListView listView;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_record_management);

        listView = findViewById(R.id.fileView);

        EdgeToEdge.enable(this);

        ViewCompat.setOnApplyWindowInsetsListener(findViewById(R.id.main), (v, insets) -> {
            Insets systemBars = insets.getInsets(WindowInsetsCompat.Type.systemBars());
            v.setPadding(systemBars.left, systemBars.top, systemBars.right, systemBars.bottom);
            return insets;
        });

        Button deleteAllButton = findViewById(R.id.deleteButton);


        File[] files = new File(getExternalFilesDir(null), "Recordings").listFiles();
        if (files != null){
            String[] fileName = Arrays.stream(files).map(File::getName).toArray(String[]::new);
            ArrayAdapter<String> adapter = new ArrayAdapter<>(
                    this,
                    android.R.layout.simple_list_item_1,
                    fileName
            );

            listView.setAdapter(adapter);

            listView.setOnItemClickListener((adapterView, view, index, l) -> {
                Intent intent = new Intent(RecordManagementActivity.this, FileViewActivity.class);
                intent.putExtra("selectedFile", files[index].getAbsolutePath());
                startActivity(intent);
            });
        }
        deleteAllButton.setOnClickListener(v -> {
            showConfirmToDelete(this::deleteAllRecords);
        });
    }

    private void showConfirmToDelete(Runnable callback){
        new androidx.appcompat.app.AlertDialog.Builder(this)
                .setTitle("Confirm to delete")
                .setMessage("Do you want to delete all records?")
                .setPositiveButton("Yes", (dialog, which) -> {
                    callback.run();
                })
                .setNegativeButton("No", (dialog, which) -> {
                    dialog.dismiss();
                })
                .create()
                .show();
    }
    private void deleteAllRecords(){
        File[] files = new File(getExternalFilesDir(null), "Recordings").listFiles();
        if (files != null) {
            for (File file : files) {
                file.delete();
            }
        }
        Toast.makeText(this,
                "Delete all the records",
                Toast.LENGTH_LONG).show();
        recreate();
    }
}