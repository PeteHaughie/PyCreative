# Troubleshooting

## Capture

On Mac OS the webcam needs to be granted permission to run in whatever environment is calling the capture device - most likely a terminal or IDE with integrated terminal - in my case that's Visual Studio Code. Permissions errors will look something like this:

```
OpenCV: camera access has been denied. Either run 'tccutil reset Camera' command in same terminal to reset application authorization status, either modify 'System Preferences -> Security & Privacy -> Camera' settings for your application.
OpenCV: camera failed to properly initialize!
[Capture] Device 0: not found
```

Close the sketch, run the commans `tccutil reset Camera` as suggested by OpenCV and then reopen the sketch. You will be asked to allow or deny the webcam terminal access by the OS - select "allow". Close the sketch and reopen it. You will now be able to see the input of your selected capture device.