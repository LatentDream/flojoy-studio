In this example, we use the `PCAN_CONNECT` block to establish a connection to a PEAK-USB CAN sniffer, decode received CAN bus messages, and display the output in a tabular format.

To replicate this application, you must connect the PEAK-USB to your computer and install the required driver (refer to the `PCAN_CONNECT` blocks for more information on the necessary driver for your platform). Then, simply specify the PEAK-USB channel in the `PCAN_CONNECT` and `PCAN_READ` blocks, and this Flojoy application will log the messages received by the device!

**Detecting channels**
A valuable block is the `PCAN_DETECT_AVAILABLE_DEVICE`. This block allows you to display the devices using the PCAN interface that are connected to your computer.