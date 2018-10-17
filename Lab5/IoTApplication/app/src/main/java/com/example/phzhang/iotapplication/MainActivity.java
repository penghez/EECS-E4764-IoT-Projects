package com.example.phzhang.iotapplication;


import java.util.ArrayList;
import java.util.Locale;
import com.loopj.android.http.*;
import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.speech.RecognizerIntent;
import android.support.annotation.NonNull;
import android.view.View;
import android.widget.EditText;
import android.widget.Toast;
import android.widget.Button;
import android.widget.TextView;

import java.util.Date;
import java.text.SimpleDateFormat;

import cz.msebera.android.httpclient.Header;


public class MainActivity extends Activity {
    private Button btnRecognizer;
    private Button sendButton;
    private TextView msgText;
    private EditText urlText;
    String speechWord = new String();
    String urlPath = new String();
    private static final int VOICE_RECOGNITION_REQUEST_CODE = 1234;
    private static final int REQUEST_AUDIO = 0;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // TODO Auto-generated method stub
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (Build.VERSION.SDK_INT >= 23) {
            if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
                // BEGIN_INCLUDE(camera_permission_request)
                if (shouldShowRequestPermissionRationale(android.Manifest.permission.RECORD_AUDIO)) {
                    showMessageOKCancel("You need to allow access to Contacts", new DialogInterface.OnClickListener() {
                        @Override
                        public void onClick(DialogInterface dialog, int which) {
                            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, REQUEST_AUDIO);
                        }
                    });
                } else {
                    requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO}, REQUEST_AUDIO);
                }
            }
        }

        urlText =(EditText)findViewById(R.id.edit);

        btnRecognizer=(Button) this.findViewById(R.id.button);
        btnRecognizer.setOnClickListener(new Button.OnClickListener() {
            @Override
            public void onClick(View v) {
                // TODO Auto-generated method stub
                try{
                    Intent intent=new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
                    intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
                    intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.ENGLISH);
                    intent.putExtra(RecognizerIntent.EXTRA_PROMPT, "Start recording");
                    // only get one result from Google
                    intent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1);
                    startActivityForResult(intent, VOICE_RECOGNITION_REQUEST_CODE);
                } catch (Exception e) {
                    // TODO: handle exception
                    e.printStackTrace();
                    Toast.makeText(getApplicationContext(), "Please install Google Voice Search", Toast.LENGTH_LONG).show();
                }
            }
        });

        sendButton=(Button) this.findViewById(R.id.button2);
        sendButton.setOnClickListener(new Button.OnClickListener() {
            @Override
            public void onClick(View v) {
                // TODO Auto-generated method stub
                String res = speechWord;
                urlPath = urlText.getText().toString();
                String path = "http://" + urlPath + "/?msg=";
                if (res.indexOf("time") != -1) {
                    SimpleDateFormat df = new SimpleDateFormat("yyyy-MM-dd-HH-mm-ss");
                    res = "time=" + df.format(new Date());
                }
                sendGet(path, res);
            }
        });
    }


    private void showMessageOKCancel(String message, DialogInterface.OnClickListener okListener) {
        new AlertDialog.Builder(this)
           .setMessage(message)
           .setPositiveButton("OK", okListener)
           .setNegativeButton("Cancel", null)
           .create()
           .show();
    }


    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        // TODO Auto-generated method stub
        msgText =(TextView) this.findViewById(R.id.text);
        if(requestCode==VOICE_RECOGNITION_REQUEST_CODE && resultCode==RESULT_OK){
            ArrayList<String> results=data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
            StringBuilder resultString = new StringBuilder();
            for(int i=0; i<results.size(); i++){
                resultString.append(results.get(i)).append("\n");
            }
            msgText.setText(resultString);
            speechWord = resultString.toString();
        }
        super.onActivityResult(requestCode, resultCode, data);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        switch (requestCode) {
            case REQUEST_AUDIO:
                if (grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                    Toast.makeText(this, "AUDIO Permitted!", Toast.LENGTH_SHORT).show();
                }
                break;
            default:
                super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        }
    }


    private void sendGet(String path, String msg) {
        AsyncHttpClient client = new AsyncHttpClient();
        client.get(path + msg, new AsyncHttpResponseHandler() {
            @Override
            public void onSuccess(int i, Header[] headers, byte[] bytes) {
                String resp = new String(bytes);
                resp = "Get response from huzzah: " + resp;
                Toast.makeText(getApplicationContext(), resp, Toast.LENGTH_LONG).show();
            }

            @Override
            public void onFailure(int i, Header[] headers, byte[] bytes, Throwable throwable) {
                Toast.makeText(getApplicationContext(), "Cannot not reach server: " + urlPath, Toast.LENGTH_LONG).show();
            }
        });
    }
}

