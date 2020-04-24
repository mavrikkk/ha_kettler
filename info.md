**Description (Описание)**
<p>This integration allows you to connect Redmond SkyKettle G200S, G210S (other kettles need tests) to your Home Assistant (Интеграция позволяет подключить чайник Redmond G200S, G210S (другие нуждаются в тестировании) к вашему HomeAssistant)</p>



**What's new:**

2020/04/24 complete revision of the code. Replacing "pexpect" library with "bluepy". Instead of an interactive mode, full support for subscribing to notifications. !!!ATTENTION!!! In the new version, some functions are cut down (there are no statistics on power-ups and energy costs, there is no way to turn off the kettle's backlight, there is no HOLD mode)

Полный пересмотр кода. Замена библиотеки pexpect на bluepy. Вместо интерактивного режима работы полная поддержка подписки на уведомления. !!!ВНИМАНИЕ!!! В новой версии урезано часть функций (нет статистики включений и затрат электроэнергии, нет возможности отключить подсветку чайника, нет режима Поддерживать)

2020/01/26 add switch to manage "use backlight to show current temperaure and sync statuses" option

2020/01/27 add switch to manage "hold temperature after heat" option

2020/02/07 add switch to first authorize redmond kettler (now, you can initialize Redmond device and AFTER that connect to kettler from HA frontend), bugfixes

2020/04/09 yaml configuration has been replaced with config flow (thanks to https://github.com/fantomnotabene) Now you can add/remove entry via UI without HA restart, able to change entity_id for each entity to your desired.


**Installation instructions:**
<p>After installation, in the UI go to the settings page, then to integrations. There click/tap on the plus button and select Redmond SkyKettle integration. Fill all the fields. No more need to reboot. You must see new inactive water heater, sensor and light elements. Hold down the button on the kettle until the LEDs flash rapidly. Turn on redmondauthorize switch

(После установки, в пользовательском интерфейсе зайдите на старницу настроек, затем в Интеграции. Там нажмите на кнопку со знаком "+" и выберите интеграцию Redmond SkyKettle. Заполните все поля. Больше нет нужды в перезагрузке. Вы должны увидеть новые неактивные элементы water heater, sensor и light. Удерживайте кнопку на чайнике до тех пор, пока светодиоды не начнут часто мигать. Включите переключатель redmondauthorize. ).</p>



**Configuration variables:**  
  
key | description  
:--- | :---  
**device (Required)** | The physical bluetooth device, for example 'hci0' (имя физического устройства блютус, например 'hci0')
**mac (Required)** | The mac address of Redmond Kettler (мак адрес чайника Redmond)
**password (Required)** | the password to your kettler, need to be 8 byte length (пароль для подключения к чайнику, должен быть длиной 8 байт)



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
