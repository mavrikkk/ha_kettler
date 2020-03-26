[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

# Redmond kettler G200S series integration
allows you to connect Redmond Kettler G200S (other kettlers need tests) to your Home Assistant


**What's new:**

2020/01/26 add switch to manage "use backlight to show current temperaure and sync statuses" option

2020/01/27 add switch to manage "hold temperature after heat" option

2020/02/07 add switch to first authorize redmond kettler (now, you can initialize Redmond device and AFTER that connect to kettler from HA frontend), bugfixes


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
**scan_interval (Optional)** | The polling interval in seconds. The default is 60. Please note that at Rasberberry it led to a load on the module and periodic dumps. You can experimentally set the time interval that suits you. (Время между опросами BLE устройства в секундах. По умолчанию 60 секунд. Учтите, что на Raspberry PI  это приводило к нагрузке на модуль и периодическим отвалам. Экспериментальным путем можете установить устраивающий вас промежуток времени.)


  
**Installation instructions**

<p>After installation add the above strings to your configuration.yaml. Need to come up with any hex password 8 bytes long. Restart HA. You must see new inactive water heater, sensor and light elements. Hold down the button on the kettle until the LEDs flash rapidly. Turn on redmondauthorize switch.

(После установки добавьте вышеуказанные строки в ваш конфигурационный файл. Нужно придумать любой hex пароль длиной 8 байт. Перезагрузите homeassistant для применения конфигурации. После загрузки вы должны увидеть новые неактивные элементы water heater, sensor and light. Удерживайте кнопку на чайнике до тех пор, пока светодиоды не начнут часто мигать. Включите переключатель redmondauthorize. ).</p>



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
