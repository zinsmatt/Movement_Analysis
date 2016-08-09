package matthieu.bluetooth_com;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.os.Environment;
import android.support.design.widget.FloatingActionButton;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.View;
import android.widget.ProgressBar;
import android.widget.SeekBar;
import android.widget.TextView;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

public class ConnectionActivity extends AppCompatActivity implements SensorEventListener {

    private final int RecordingTime = 5000; // ms

    private TextView device_name_text;
    private TextView device_adr_text;
    private TextView connection_status;
    private ProgressBar progressBar;
    private BluetoothSocket socket;
    private ConnectedThread connectedThread;

    // sensor
    private SensorManager manager;
    private Sensor accel_sensor;
    private final AtomicBoolean isRecording = new AtomicBoolean(false);
    private FileWriter filewriter;
    private File file;

    private long prev_time = System.currentTimeMillis();
    List<Float> values;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_connection);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        FloatingActionButton fab = (FloatingActionButton) findViewById(R.id.fab);
        device_name_text = (TextView) findViewById(R.id.device_name_text);
        device_adr_text = (TextView) findViewById(R.id.device_adr_text);
        connection_status = (TextView) findViewById(R.id.connection_status);
        progressBar = (ProgressBar) findViewById(R.id.progressBar);
        progressBar.setMax(RecordingTime);
        progressBar.setProgress(0);


        manager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        accel_sensor = manager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);

        Bundle b = getIntent().getExtras();
        BluetoothDevice device = (BluetoothDevice) b.getParcelable("device");
        System.out.println("recieved device : " + device.getName());
        device_name_text.setText(device.getName());
        device_adr_text.setText(device.getAddress());

        socket = null;
        connection_status.setText("");
        values = new ArrayList<Float>();


        BluetoothAdapter mBluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        ConnectThread connection_thread = new ConnectThread(device,this,mBluetoothAdapter);
        connection_thread.start();

        //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        String NOTES ="ZZZZZ_mi12_test.txt";
        file = new File(Environment.getExternalStorageDirectory(), NOTES);

        try {
            file.createNewFile();
            filewriter = new FileWriter(file, false);
        }catch(IOException e) {
            System.err.print("Error create file ----------------------\n");
        }
        //+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    }

    public void startSynchronizeMode(int _max)
    {
        final int max_val = _max;
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                progressBar.setMax(max_val);
                progressBar.setProgress(1);
                connection_status.setText("Synchronisation...");
            }
        });
    }

    public void setSynchronizeMode(int _val)
    {
        final int val = _val;
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                progressBar.setProgress(val);
            }
        });
    }

    public void stopSynchronizeMode()
    {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                progressBar.setMax(RecordingTime);
                progressBar.setProgress(RecordingTime);
                connection_status.setText("Synchonisation faite");
            }
        });
    }


    public void recieveBluetoothSocket(BluetoothSocket _socket, final ConnectionActivity _activity){
        socket = _socket;
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                if(socket != null){
                    connection_status.setText("Connexion étalie");
                    findViewById(R.id.loading_spinner).setVisibility(View.INVISIBLE);
                    if(socket!=null){
                        connectedThread = new ConnectedThread(socket, _activity);
                        connectedThread.start();
                        System.out.println("ConnectedThread started");
                    }
                }else{
                    connection_status.setText("Impossible de se connecter");
                    findViewById(R.id.loading_spinner).setVisibility(View.INVISIBLE);
                }
            }
        });

    }

    @Override
    public final void onAccuracyChanged(Sensor sensor, int accuracy){

    }

    @Override
    public final void onSensorChanged(SensorEvent event){
       if(isRecording.get() == false)
           return;
        System.out.println(event.values[0]);
        if(isRecording.get() == false)
            return;
        if(System.currentTimeMillis()-prev_time>RecordingTime) {
            progressBar.setProgress((int) (System.currentTimeMillis()-prev_time));

            if(connectedThread != null){
                //+++++++++++++++++++++++++++++++++++++++++++++
                try {
                    for(float a : values){
                        filewriter.write(Float.toString(a) + "\n");
                    }
                    //filewriter.write( + "\n");
                    filewriter.close();
                } catch (IOException e) {
                    System.err.print("ERROR -------------------- WRITE");
                }
                //++++++++++++++++++++++++++++++++++++++++++++
                connectedThread.sendValues(values);
                values.clear();
                connection_status.setText("Données envoyées");
            }
            prev_time = System.currentTimeMillis();
            isRecording.set(false);
            System.out.println("Value send");
        }else
        {

            progressBar.setProgress((int) (System.currentTimeMillis()-prev_time));
            values.add(event.values[0]);
            values.add(event.values[1]);
            values.add(event.values[2]);
        }
    }

    public void startRecording(){
        progressBar.setProgress(0);
        isRecording.set(true);
        prev_time = System.currentTimeMillis();
        System.out.println(System.currentTimeMillis());
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                connection_status.setText("Enregistrement des donnnées...");
            }
        });
    }


    @Override
    protected void onResume(){
        super.onResume();
        manager.registerListener(this, accel_sensor, manager.SENSOR_DELAY_NORMAL);
    }

    @Override
    protected void onPause(){
        super.onPause();
        manager.unregisterListener(this);
    }
}
