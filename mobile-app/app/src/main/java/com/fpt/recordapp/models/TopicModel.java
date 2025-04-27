package com.fpt.recordapp.models;



import java.util.List;

public class TopicModel {
    private List<DialogueModel> dialogueModels;

    public TopicModel(List<DialogueModel> dialogueModels) {
        this.dialogueModels = dialogueModels;
    }

    public List<DialogueModel> getDialogueModels() {
        return dialogueModels;
    }

    public void setDialogueModels(List<DialogueModel> dialogueModels) {
        this.dialogueModels = dialogueModels;
    }
}
