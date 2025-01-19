from pyscript import display, when, document, media

device_select = document.querySelector("#devices")
video = document.querySelector("video")
devices = {}

async def list_media_devices(event=None):
    global devices
    for i, device in enumerate(await media.list_devices()):
        devices[device.id] = device
        label = f"{i} - ({device.kind}) {device.label} [{device.id}]"
        display(label, append=True, target="result")
        
        # Create a new option element using createElement
        option = document.createElement("option")
        option.text = label  # Set the display text
        option.value = device.id  # Set the value attribute
        device_select.add(option)  # Add the option to the select element

@when("click", "#pick-device")
async def connect_to_device(event):
    device = devices[device_select.value]
    video.srcObject = await device.get_stream()
    
@when("click", "#snap")
async def camera_click(event):
    video.snap().download()
    
await list_media_devices()