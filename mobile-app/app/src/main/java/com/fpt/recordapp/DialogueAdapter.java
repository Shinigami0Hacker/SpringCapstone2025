package com.fpt.recordapp;

import android.app.Activity;
import android.content.Context;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.ImageButton;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.fpt.recordapp.models.DialogueStatus;

import java.util.ArrayList;

public class DialogueAdapter extends ArrayAdapter<DialogueStatus> {
    int IdLayout;
    Activity context;
    ArrayList<DialogueStatus> dialogueStatuses;
    public DialogueAdapter(Activity context, int idLayout, ArrayList<DialogueStatus> dialogueStatuses) {
        super(context, idLayout, dialogueStatuses);
        this.context = context;
        this.IdLayout = idLayout;
        this.dialogueStatuses = dialogueStatuses;
    }

    @NonNull
    @Override
    public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
        LayoutInflater inflater = context.getLayoutInflater();
        convertView = inflater.inflate(IdLayout, null);
        DialogueStatus dialogueStatus = dialogueStatuses.get(position);
        TextView name = convertView.findViewById(R.id.dialogueName);
        TextView statusText = convertView.findViewById(R.id.statusText);

        name.setText(dialogueStatus.getName());
        if (dialogueStatus.isStatus()){
            statusText.setText("Trạng thái: Hoàn Thành");
        }
        else{
            statusText.setText("Trạng thái: Chưa Hoàn Thành");
        }
        return convertView;
    }
}
