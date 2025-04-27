package com.fpt.recordapp.models;


import androidx.annotation.Nullable;

import com.fpt.recordapp.types.DialogueType;

public class SubDialogueModel {
    private int id;
    private String type;
    private String sentence;
    @Nullable
    private String explanation;

    public SubDialogueModel(int id, String type, String sentence, String explanation) {
        this.explanation = explanation;
        this.sentence = sentence;
        this.type = type;
        this.id = id;
    }

    public String getType() {
        return type;
    }

    public int getId() {
        return id;
    }

    public void setId(int id) {
        this.id = id;
    }

    public void setType(String type) {
        this.type = type;
    }

    public void setSentence(String sentence) {
        this.sentence = sentence;
    }

    public void setExplanation(@Nullable String explanation) {
        this.explanation = explanation;
    }

    public String getSentence() {
        return sentence;
    }

    @Nullable
    public String getExplanation() {
        return explanation;
    }
}
