package com.fpt.recordapp.ui;

import android.os.Bundle;

import androidx.fragment.app.Fragment;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.fpt.recordapp.R;

/**
 * A simple {@link Fragment} subclass.
 * Use the {@link ContentViewFragment#newInstance} factory method to
 * create an instance of this fragment.
 */
public class ContentViewFragment extends Fragment {
    private static final String ARG_PARAM1 = "questionType";
    private static final String ARG_PARAM2 = "content";
    private static final String ARG_PARAM3 = "explanation";

    private String questionType;
    private String content;

    private String explanation;
    public static ContentViewFragment newInstance(String questionType, String content, String explanation) {
        ContentViewFragment fragment = new ContentViewFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM1, questionType);
        args.putString(ARG_PARAM2, content);
        args.putString(ARG_PARAM3, explanation);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            questionType = getArguments().getString(ARG_PARAM1);
            content = getArguments().getString(ARG_PARAM2);
            explanation = getArguments().getString(ARG_PARAM3);
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View rootView = inflater.inflate(R.layout.fragment_content_view, container, false);


        TextView textViewQuestionType = rootView.findViewById(R.id.question);
        TextView textViewContent = rootView.findViewById(R.id.content);
        TextView textViewExplanation = rootView.findViewById(R.id.explanation);


        textViewQuestionType.setText("Vui lòng đọc lại đoạn chữ bên dưới:");
        textViewContent.setText(content != null ? content : "");
        textViewExplanation.setText(explanation != null ? "Chú thích: " + explanation : "");

        return rootView;
    }
}