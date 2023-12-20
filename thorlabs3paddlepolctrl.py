import clr
import time

clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.PolarizerCLI.dll")

from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.PolarizerCLI import *
from System import Decimal

def main():
    # Uncomment this line if you are using a simulation
    #SimulationManager.Instance.InitializeSimulations()

    try:
        # Build device list. 
        DeviceManagerCLI.BuildDeviceList()

        # create new device.
        serial_no_dev1 = "38390544"
        device1 = Polarizer.CreatePolarizer(serial_no_dev1)
        

        # Connect to device 1.
        device1.Connect(serial_no_dev1)

        # Ensure that the device settings have been initialized.
        if not device1.IsSettingsInitialized():
            device1.WaitForSettingsInitialized(10000)  # 10 second timeout.
            assert device1.IsSettingsInitialized() is True
            
            

        # Start polling loop and enable device.
        device1.StartPolling(250)  #250ms polling rate.
        time.sleep(5)
        device1.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable.
        


        # Get Device Information and display description.
        device1_info = device1.GetDeviceInfo()
        print(device1_info.Description)
        

        # Call device methods.
        print("Homing Device 1 ")
        paddle1 = PolarizerPaddles.Paddle1#choose first paddle
        device1.Home(paddle1,60000)  # 60 second timeout.
        

        
        #for device 1
        
        paddle2 = PolarizerPaddles.Paddle2#choose 2nd paddle
        device1.Home(paddle2,60000)  # 60 second timeout.
        print("Done")

        time.sleep(2)

        new_pos1 = Decimal(20.0)  # Must be a .NET decimal.
        new_pos2 = Decimal(10.0)  # Must be a .NET decimal.

        print(f'Moving to {new_pos1}')
        device1.MoveTo(new_pos1,paddle1, 60000)  # 60 second timeout.
        print("Done")

        print(f'Moving to {new_pos2}')
        device1.MoveTo(new_pos2,paddle2, 60000)  # 60 second timeout.
        print("Done")
        # Stop polling loop and disconnect device before program finishes. 
        device1.StopPolling()
        #device1.Disconnect()
    
        # Build device list. 
        DeviceManagerCLI.BuildDeviceList()



        # link other paddle
        serial_no_dev2 = "38392094"
        device2 = Polarizer.CreatePolarizer(serial_no_dev2)


        # Connect to device.
        device2.Connect(serial_no_dev2)


            
        # Ensure that the device settings have been initialized.
        if not device2.IsSettingsInitialized():
            device2.WaitForSettingsInitialized(10000)  # 10 second timeout.
            assert device2.IsSettingsInitialized() is True


        
        # Start polling loop and enable device.
        device2.StartPolling(250)  #250ms polling rate.
        time.sleep(5)
        device2.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable.


        # Get Device Information and display description.
        device2_info = device2.GetDeviceInfo()
        print(device2_info.Description)


        # Call device methods.
        print("Homing Device 2")
        paddle1 = PolarizerPaddles.Paddle1#choose first paddle
        device2.Home(paddle1,60000)  # 60 second timeout.
        
        
        
        #for device 2
        
        paddle2 = PolarizerPaddles.Paddle2#choose 2nd paddle
        device2.Home(paddle2,60000)  # 60 second timeout.
        print("Done")

        time.sleep(2)

        new_pos1 = Decimal(20.0)  # Must be a .NET decimal.
        new_pos2 = Decimal(10.0)  # Must be a .NET decimal.

        print(f'Moving to {new_pos1}')
        device2.MoveTo(new_pos1,paddle1, 60000)  # 60 second timeout.
        print("Done")

        print(f'Moving to {new_pos2}')
        device2.MoveTo(new_pos2,paddle2, 60000)  # 60 second timeout.
        print("Done")
        # Stop polling loop and disconnect device before program finishes. 
        device2.StopPolling()
        device2.Disconnect()


    except Exception as e:
        print(e)
        
    #SimulationManager.Instance.UninitializeSimulations()

if __name__ == "__main__":
    main()



 


