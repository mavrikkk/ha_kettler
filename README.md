[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

# ha_kettler
allows you to connect Redmond Kettler G200S (other kettlers need tests) to your Home Assistant


**What's new:**

2020/01/26 add switch to manage "use backlight to show current temperaure and sync statuses" option

2020/01/27 add switch to manage "hold temperature after heat" option



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

![example1][exampleimg1]
![example2][exampleimg2]
![example3][exampleimg3]
![example4][exampleimg4]



***


[exampleimg1]: 01.jpg
[exampleimg2]: 02.jpg
[exampleimg3]: 03.jpg
[exampleimg4]: 04.jpg
