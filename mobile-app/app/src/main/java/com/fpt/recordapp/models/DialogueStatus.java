package com.fpt.recordapp.models;

public class DialogueStatus {
    String name;
    boolean status;

    public void setName(String name) {
        this.name = name;
    }

    public void setStatus(boolean status) {
        this.status = status;
    }

    public String getName() {
        return name;
    }

    public boolean isStatus() {
        return status;
    }

    public DialogueStatus(String name, boolean status) {
        this.name = name;
        this.status = status;
    }
}
