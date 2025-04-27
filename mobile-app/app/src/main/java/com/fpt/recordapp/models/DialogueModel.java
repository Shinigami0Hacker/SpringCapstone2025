package com.fpt.recordapp.models;

import java.util.List;
import com.google.gson.annotations.SerializedName;

public class DialogueModel {
    @SerializedName("name")
    public String name;

    @SerializedName("sub-dialogue")
    public List<SubDialogueModel> subDialogueModels;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setSubDialogueModels(List<SubDialogueModel> subDialogueModels) {
        this.subDialogueModels = subDialogueModels;
    }

    public List<SubDialogueModel> getSubDialogueModels() {
        return subDialogueModels;
    }

    public DialogueModel(String name, List<SubDialogueModel> subDialogueModels) {
        this.name = name;
        this.subDialogueModels = subDialogueModels;
    }
}
