**Description (Описание)**
<p>This integration allows you to connect Redmond Kettler G200S to your HomeAssistant (Интеграция позволяет подключить чайник Redmond G200S к вашему HomeAssistant)</p>



**Example configuration.yaml:**

```yaml
r4s_kettler:
  device: 'hci0'
  mac: 'FF:FF:FF:FF:FF:FF'
  password: 'ffffffffffffffff'
```



**Configuration variables:**  
  
key | description  
:--- | :---  
**device (Required)** | The physical bluetooth device, for example 'hci0' (имя физического устройства блютус, например 'hci0')
**mac (Required)** | The mac address of Redmond Kettler (мак адрес чайника Redmond)
**password (Required)** | the password to your kettler, need to be 8 byte length (пароль для подключения к чайнику, должен быть длиной 8 байт)


  
**Installation instructions**

<p>After installation add the above strings to your configuration.yaml. Need to come up with any hex password 8 bytes long. Then hold down the button on the kettle until the LEDs flash rapidly. Restart HA immediately.You must see new water heater, sensor and light elements.

(После установки добавьте вышеуказанные строки в ваш конфигурационный файл. Нужно придумать любой hex пароль длиной 8 байт. Удерживайте кнопку на чайнике до тех пор, пока светодиоды не начнут часто мигать. Сразу перезагрузите HA. После загрузки вы должны увидеть новые элементы water heater, sensor and light).</p>



**Screenshots**

![example][exampleimg]



***

[exampleimg]: map.jpeg
