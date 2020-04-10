[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

# Redmond SkyKettle series integration
allows you to connect Redmond SkyKettle G200S, G210S (other kettles need tests) to your Home Assistant


**What's new:**

2020/04/09 yaml configuration has been replaced with config flow (now you can add/remove entry via UI without HA restart, able to change entity_id for each entity to your desired)

2020/02/07 add switch to first authorize redmond kettler (now, you can initialize Redmond device and AFTER that connect to kettler from HA frontend), bugfixes

2020/01/27 add switch to manage "hold temperature after heat" option

2020/01/26 add switch to manage "use backlight to show current temperaure and sync statuses" option


**Example configuration:**

<img width="456" alt="Config flow" src="https://user-images.githubusercontent.com/9576189/78805578-3fdca180-79ca-11ea-9dda-5710c7f46f66.png">


**Configuration variables:**  
  
key | description  
:--- | :---  
**device (Required)** | The physical bluetooth device, for example 'hci0' (имя физического устройства блютус, например 'hci0')
**mac (Required)** | The mac address of Redmond Kettler (мак адрес чайника Redmond)
**password (Required)** | the password to your kettler, need to be 8 byte length (пароль для подключения к чайнику, должен быть длиной 8 байт)
**scan_interval (Optional)** | The polling interval in seconds. The default is 60. Please note that at Rasberberry it led to a load on the module and periodic dumps. You can experimentally set the time interval that suits you. (Время между опросами BLE устройства в секундах. По умолчанию 60 секунд. Учтите, что на Raspberry PI  это приводило к нагрузке на модуль и периодическим отвалам. Экспериментальным путем можете установить устраивающий вас промежуток времени.)


  
**Installation instructions**

<p>After installation, in the UI go to the settings page, then to integrations. There click/tap on the plus button and select Redmond SkyKettle integration. Fill all the fields. No more need to reboot. You must see new inactive water heater, sensor and light elements. Hold down the button on the kettle until the LEDs flash rapidly. Turn on redmondauthorize switch.

(После установки, в пользовательском интерфейсе зайдите на старницу настроек, затем в Интеграции. Там нажмите на кнопку со знаком "+" и выберите интеграцию Redmond SkyKettle. Заполните все поля. Больше нет нужды в перезагрузке. Вы должны увидеть новые неактивные элементы water heater, sensor и light. Удерживайте кнопку на чайнике до тех пор, пока светодиоды не начнут часто мигать. Включите переключатель redmondauthorize. ).</p>



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
