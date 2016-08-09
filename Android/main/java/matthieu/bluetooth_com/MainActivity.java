package matthieu.bluetooth_com;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.TextView;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;

public class MainActivity extends AppCompatActivity implements SensorEventListener {
    private final AtomicBoolean ThreadRunning = new AtomicBoolean(true);

    static final int BLUETOOTH_ENABLE_REQUEST = 123;
    private List<String> devicesName;
    private Set<BluetoothDevice> pairedDevice;
    private Map<String,BluetoothDevice> devices;
    private BluetoothAdapter bt_adapter;
    private ConnectThread connection;
    private final BroadcastReceiver receiver = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            System.out.println("+++++++++++++++++ onReceive +++++++++++++++++");
            String action = intent.getAction();
            if(BluetoothDevice.ACTION_FOUND.equals(action)){
                BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                if(!devicesName.contains(device.getName())){
                    devicesName.add(device.getName());
                    devices.put(device.getName(),device);
                    updateListDevices();
                }
                System.out.println("New device : " + device.getName() + " - " + device.getAddress());
            }
        }
    };

    // sensor
    private SensorManager manager;
    private Sensor accel_sensor;
    boolean isRecording;
    private long prev_time = System.currentTimeMillis();
    List<Float> values;

    // textView
    private TextView text;
    private ListView list_devices;
    private Button search_button;









    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        devices = new HashMap<>();
        devicesName = new ArrayList<String>();

        text = (TextView) findViewById(R.id.label_text);
        text.setText("Appareils liés ");

        list_devices = (ListView) findViewById(R.id.list_devices);
        search_button = (Button) findViewById(R.id.search_device_button);
        search_button.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v) {
                // Perform action on click
                if(bt_adapter.isDiscovering()){
                    bt_adapter.cancelDiscovery();
                }

                // discover new devices
                IntentFilter filter = new IntentFilter(BluetoothDevice.ACTION_FOUND);
                registerReceiver(receiver,filter);
                bt_adapter.startDiscovery();
            }
        });

        bt_adapter = BluetoothAdapter.getDefaultAdapter();
        if(bt_adapter != null) {

            // activation du bluetooth si necessaire
            if(bt_adapter.isEnabled() == false){
                Intent discoverIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE);
                discoverIntent.putExtra(BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION, 300);
                startActivityForResult(discoverIntent, BLUETOOTH_ENABLE_REQUEST);
            }else{
                System.out.println("Bluetooth was already enabled");
            }

            addPairedDevices();


            list_devices.setOnItemClickListener(new AdapterView.OnItemClickListener() {

                @Override
                public void onItemClick(AdapterView<?> arg0, View arg1, int arg2, long arg3) {
                    // TODO Auto-generated method stub
                    Object item = arg0.getItemAtPosition(arg2);
                    if (item != null) {
                        System.out.println("Device clicked : " + item.toString());
                        Intent intent = new Intent(MainActivity.this, ConnectionActivity.class);
                        BluetoothDevice dev = devices.get(item.toString());
                        intent.putExtra("device", dev);
                        startActivity(intent);
                    }
                }
            });

        }
    }

    public void addPairedDevices(){
        // add paired devices
        if(bt_adapter.isEnabled()  == true){
            System.out.println("----------------PAIRED DEVICES ----------------");
            pairedDevice = bt_adapter.getBondedDevices();
            if(pairedDevice.size() > 0){
                for (BluetoothDevice device : pairedDevice){
                    devicesName.add(device.getName());
                    devices.put(device.getName(),device);
                    System.out.println(device.getName());
                }
            }
            updateListDevices();
        }
    }

    public void updateListDevices(){
        ArrayAdapter<String> list_adapter = new ArrayAdapter<String>(MainActivity.this,
                android.R.layout.simple_list_item_1, devicesName);
        list_devices.setAdapter(list_adapter);
    }

    @Override
    public void onDestroy(){
        super.onDestroy();
        System.out.println("############# DESTROY #############");
        bt_adapter.cancelDiscovery();
        bt_adapter.disable();
        unregisterReceiver(receiver);
    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
       // getMenuInflater().inflate(R.menu.menu_main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        /*int id = item.getItemId();

        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }*/

        return super.onOptionsItemSelected(item);
    }


    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        /*System.out.print("!!!!!!!!!!!!!!!!!! on Activity Result !!!!!!!!!!!!!!!!!!!!!!!!!!!");
        if(requestCode > 0){
            if(resultCode == resultCode){
                is_bluetooth_enabled = true;
            }
        }*/
        System.out.println("+++++++ onactivityresult +++++++++++++");
        System.out.println("+++++++ requestcode = "+Integer.toString(requestCode)+" +++++++++++++");
        System.out.println("+++++++ resultcode = "+Integer.toString(resultCode)+" +++++++++++++");

        if(requestCode ==   BLUETOOTH_ENABLE_REQUEST){
            if(resultCode  == 300){
                System.out.println("Bluetooth as enabled");
                addPairedDevices();
            }else if(resultCode == RESULT_CANCELED){
                finish();
            }
        }


    }


    @Override
    public final void onAccuracyChanged(Sensor sensor, int accuracy){

    }

    @Override
    public final void onSensorChanged(SensorEvent event){
//        System.out.println(event.values[0]);
        /*if(!isRecording)
            return;
        if(System.currentTimeMillis()-prev_time>5000) {
            isRecording = false;
            if(connection != null){
                connection.sendValues(values);
                values.clear();
            }
            prev_time = System.currentTimeMillis();
            isRecording = false;
            text.setText("Fin enregistrement");
        }else
        {
            values.add(event.values[0]);
            values.add(event.values[1]);
            values.add(event.values[2]);
        }*/
    }

    @Override
    protected void onResume(){
        super.onResume();
        //manager.registerListener(this, accel_sensor, manager.SENSOR_DELAY_NORMAL);
    }

    @Override
    protected void onPause(){
        super.onPause();
        //manager.unregisterListener(this);
    }

    private class ConnectThread extends Thread {
        private final BluetoothDevice device;
        private final BluetoothSocket socket;
        private int num;
        public ConnectThread(BluetoothDevice _device) {
            BluetoothSocket temp = null;
            num = 0;
            device = _device;
            System.out.println("connect thread !!!!");
            try {

               /* Class<?> cls = adapter.getRemoteDevice(device.getAddress()).getClass();
                Class<?>[] paramTypes = new Class<?>[]{ Integer.TYPE };
                Method m = cls.getMethod("createRfcommSocket", paramTypes);
                Object[] params = new Object[]{ Integer.valueOf(1) };
                temp = (BluetoothSocket) m.invoke(adapter.getRemoteDevice(device.getAddress()), params);*/

                temp = device.createRfcommSocketToServiceRecord(java.util.UUID.fromString("e8e10f95-1a70-4b27-9ccf-02010264e9c8"));
            } /*catch (InvocationTargetException e) {
                e.printStackTrace();
            } catch (NoSuchMethodException e) {
                e.printStackTrace();
            } catch (IllegalAccessException e) {
                e.printStackTrace();
            }*/ catch(IOException e){
                e.printStackTrace();
            }
            socket = temp;
        }


        public void run() {
            System.out.println("run");
            bt_adapter.cancelDiscovery();

            try {
                socket.connect();
            }catch(IOException connect_exception){
                try{
                    socket.close();
                }catch(IOException close_exception) {}
                return ;
            }

            if(socket!=null){

                while(ThreadRunning.get()){
                    readMessage();
                    isRecording = true;
                    while(isRecording){}
                }
                //manageSocket();
            }else{
                System.out.println("Error connection");
            }

        }

        public void cancel(){
            try{
                socket.close();
            }catch (IOException e) {}
        }

        public void manageSocket(){
            System.out.println("manageSocket");
            try{
                OutputStream stream = socket.getOutputStream();
                String str = "losc " + Integer.toString(num);
                num = num +1;
                byte[] buffer = str.getBytes();
                stream.write(buffer);
                stream.flush();
            }catch(IOException e)
            {

            }
        }

        public void readMessage(){
            System.out.println("ReadMEssage");
            final byte[] buffer = new byte[16];
            try{
                InputStream stream = socket.getInputStream();

                while(stream.read(buffer) == -1){
                    System.out.print("...");
                }
                System.out.println("#######################  signe de demarrage lu #####################\n");
                //text.setText(new String(buffer));
                /*runOnUiThread(new Runnable() {
                    public void run() {
                        text.setText("Enregistrement demarre");
                    }
                });*/

            }catch(IOException e){
                System.out.println("### IOException ###");
            }

        }

        public void write(byte[] buffer){
            try{
                OutputStream stream = socket.getOutputStream();
                stream.write(buffer);
                //stream.flush();
            }catch(IOException e)
            {
            }
        }

        public void sendValues(List<Float> values){
            int nb = 0;
            int i=0;
            for(Float f : values){
                byte[] b = ByteBuffer.allocate(4).putFloat(f).array();
                byte[] b_inv = b.clone();
                b_inv[0] = b[3];
                b_inv[1] = b[2];
                b_inv[2] = b[1];
                b_inv[3] = b[0];

                this.write(b_inv);
                nb += 1;
            }

            System.out.println(Integer.toString(nb) + " have been transfered");
            System.out.println(Float.toString(values.get(0)));
            System.out.println(Float.toString(values.get(1)));
            System.out.println(Float.toString(values.get(2)));

        }
    };

}
