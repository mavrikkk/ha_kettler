[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

# Redmond SkyKettle, SkyCooker and SkyHeat series integration
allows you to connect Redmond SkyKettle, SkyCooker and SkyHeat to your Home Assistant (full list of supported devices see in:  https://github.com/mavrikkk/ha_kettler/blob/master/custom_components/ready4sky/r4sconst.py ).

**!!!ATTENTION!!!**

After every update remove integration from HA and then add it again! После обновления модуля лучше удалить интеграцию из интерфейса HA и заново добавить ее.

BAD NEWS about my attempt to use BLEAK (https://github.com/hbldh/bleak) async libriry:   https://github.com/home-assistant/core/issues/37593

**What's new:**

2020/10/13 Add support for SkyHeat RCH-4529S (RFS-HPL001).

2020/05/29 Minor bug fixes and improvements. No more lags in interface, if disconnect device from power strip. states update immediatly.

2020/05/22 Minor bug fixes and improvements. +speed, +stability, -freezes. Rename r4s_kettler to ready4sky (now it is not only kettle). Delete old intefration from UI before install this!

2020/05/14 Minor bug fixes and improvements. integration some other models. add Cooker!

2020/05/06 Minor bug fixes and improvements. integration some other models. The name of the device is the model of kettle. Removed Authorize switch. Autorization is in the config flow. Turn on or turn off backlight is in the config flow !!!ATTENTION!!! In this version, some functions are cut down (there are no statistics on power-ups and energy costs, there is no HOLD mode)

Мелкие исправления и улучшения. Частичная интеграции других моделей чайников. Имя устройства соответствует модели вашего чайника. Убран элемент authorize. Авторизация встроена в первоначальную настройку. В первоначальную настройку добавлена возможность включения или отключения постоянной подсветки. !!!ВНИМАНИЕ!!! Все также урезано часть функций (нет статистики включений и затрат электроэнергии, нет режима Поддерживать)

2020/04/30 Now the integration finds all the bluetooth devices during connection and offers to select it from the list. Minor bug fixes and improvements. Preparing for the integration of other models. !!!ATTENTION!!! In this version, some functions are cut down (there are no statistics on power-ups and energy costs, there is no way to turn off the kettle's backlight, there is no HOLD mode)

Теперь интеграция при подключении сама находит все устройства bluetooth и предлагает выбрать из списка. Мелкие исправления и улучшения. Подготовка к интеграции других моделей чайников !!!ВНИМАНИЕ!!! Все также урезано часть функций (нет статистики включений и затрат электроэнергии, нет возможности отключить подсветку чайника, нет режима Поддерживать)

2020/04/24 complete revision of the code. Replacing "pexpect" library with "bluepy". Instead of an interactive mode, full support for subscribing to notifications. !!!ATTENTION!!! In the new version, some functions are cut down (there are no statistics on power-ups and energy costs, there is no way to turn off the kettle's backlight, there is no HOLD mode)

Полный пересмотр кода. Замена библиотеки pexpect на bluepy. Вместо интерактивного режима работы полная поддержка подписки на уведомления. !!!ВНИМАНИЕ!!! В новой версии урезано часть функций (нет статистики включений и затрат электроэнергии, нет возможности отключить подсветку чайника, нет режима Поддерживать)

2020/04/09 yaml configuration has been replaced with config flow (thanks to https://github.com/fantomnotabene). Now you can add/remove entry via UI without HA restart, able to change entity_id for each entity to your desired

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


**WARNING**

this configuration works out of the box with hassio. In any other configuration, you may have to make additional settings: Install modules for working with bluetooth (pybluez, bluepy), configure these modules so that they work without root privileges. (данная конфигурация работает из коробки с hassio. В любой другой конфигурации возможно придется сделать дополнительные настройки: Установить модули для работы с bluetooth (pybluez, bluepy), настроить эти модули так, чтобы они работали без прав root.)

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
