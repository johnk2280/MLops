# MLops

#### Установка:
1. Склонировать данный репозиторий;
2. Из корневой директории приложения собрать образ командой:

        $ docker-compose build
3. Запустить:

        $ docker-compose up
 

>_Стек: DjangoFramework, DRF, SQLite_
>
>_Адрес запуске через встроеный сервер django:_
>_http://127.0.0.1:8000/api/v1/real_estate_price_prediction/predict/_
>
>_Адрес при запуске через docker-compose:_ 
>_http://0.0.0.0:8000/api/v1/real_estate_price_prediction/predict/_

Структура данных и наименование признаков подаваемых на вход:

    {
      "Id": 7202,
      "DistrictId": 94,
      "Rooms": 1.0,
      "Square": 35.81547646722722,
      "LifeSquare": 22.301367212492828,
      "KitchenSquare": 6.0,
      "Floor": 9,
      "HouseFloor": 9.0,
      "HouseYear": 1975,
      "Ecology_1": 0.127375905,
      "Ecology_2": "B",
      "Ecology_3": "B",
      "Social_1": 43,
      "Social_2": 8429,
      "Social_3": 3,
      "Healthcare_1": "",
      "Helthcare_2": 3,
      "Shops_1": 9,
      "Shops_2": "B"
    }

Струткутра данных на выходе:

    {
        "status": "OK",
        "price": 185852.6266987764,
        "message": "predicted_price - 185852.6266987764",
        "request_id": 40
    }

