package com.fpt.recordapp.types;

public enum DialogueType {
    GREETING,
    QUESTION,
    RESPONSE,
    REPEAT;

    public static DialogueType fromString(String value) {
        if (value.equalsIgnoreCase("repeat")) {
            return DialogueType.REPEAT;
        }
        throw new IllegalArgumentException("Unexpected value: " + value);
    }
}
