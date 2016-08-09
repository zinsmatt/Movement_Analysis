package matthieu.bluetooth_com;

import android.bluetooth.BluetoothSocket;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.util.List;

/**
 * Created by matthieu on 24/05/16.
 */
public class ConnectedThread extends Thread {
    private final BluetoothSocket mmSocket;
    private final InputStream mmInStream;
    private final OutputStream mmOutStream;
    private final ConnectionActivity connectionActivity;

    public ConnectedThread(BluetoothSocket socket, ConnectionActivity _activity) {
        mmSocket = socket;
        InputStream tmpIn = null;
        OutputStream tmpOut = null;
        connectionActivity = _activity;

        // Get the input and output streams, using temp objects because
        // member streams are final
        try {
            tmpIn = socket.getInputStream();
            tmpOut = socket.getOutputStream();
        } catch (IOException e) { }

        mmInStream = tmpIn;
        mmOutStream = tmpOut;
    }

    public void run() {
        byte[] buffer = new byte[1024];  // buffer store for the stream
        int bytes; // bytes returned from read()

        byte[] response = new byte[1];
        response[0] = 1;

        int synchro_nb_max = 60;
        int synchro_nb = 0;

        // Keep listening to the InputStream until an exception occurs
        while (true) {
            try {
                // Read from the InputStream
                bytes = mmInStream.read(buffer);
                // recoit 1 ==> test time
                // recoit 2 ==> start recording
                // Send the obtained bytes to the UI activity
                //mHandler.obtainMessage(MESSAGE_READ, bytes, -1, buffer).sendToTarget();
                if(bytes == 1) {
                    if (buffer[0] == 2) {
                        // repond immediatement
                        this.write(response);
                        synchro_nb++;

                        if(synchro_nb == synchro_nb_max){
                            connectionActivity.stopSynchronizeMode();
                        }else{
                            connectionActivity.setSynchronizeMode(synchro_nb);
                        }

                    } else if (buffer[0] == 1) {
                        connectionActivity.startRecording();
                    } else if(buffer[0] > 2){
                        synchro_nb_max = buffer[0];
                        connectionActivity.startSynchronizeMode(synchro_nb_max);
                        synchro_nb = 0;
                        this.write(response);
                    }
                }
                System.out.println("READ : "+Integer.toString(bytes));
            } catch (IOException e) {
                break;
            }
        }
    }

    /* Call this from the main activity to send data to the remote device */
    public void write(byte[] bytes) {
        try {
            mmOutStream.write(bytes);
        } catch (IOException e) { }
    }

    /* Call this from the main activity to shutdown the connection */
    public void cancel() {
        try {
            mmSocket.close();
        } catch (IOException e) { }
    }

    public void write(int val){
        byte[] b = ByteBuffer.allocate(4).putInt(val).array();
        byte[] b_inv = b.clone();
        b_inv[0] = b[3];
        b_inv[1] = b[2];
        b_inv[2] = b[1];
        b_inv[3] = b[0];
        this.write(b_inv);
    }

    public void write(float val){
        byte[] b = ByteBuffer.allocate(4).putFloat(val).array();
        byte[] b_inv = b.clone();
        b_inv[0] = b[3];
        b_inv[1] = b[2];
        b_inv[2] = b[1];
        b_inv[3] = b[0];
        this.write(b_inv);
    }

    public void sendValues(List<Float> values){
        // first send nb values
        int nb = values.size();
        System.out.println(Integer.toString(nb) + " have been transfered");
        this.write(nb);

        // send all other values
        for(Float f : values){
            this.write(f);
        }
    }
}