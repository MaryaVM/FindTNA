import socket
import folium
import zlib

# создаем сокет
client = socket.socket()
# устанавливаем соединение
client.connect(('94.19.19.131', 5117))
# вспомогательное число
for_center_of_map = 1
# подсчет неправильных контрольных сумм
wrong_ks = 0

# основной цикл
while True:
    # принимаем данные
    data = client.recv(1024)
    # проверяем на пустую строку
    if data == b'':
        break
    # печатаем данные
    print(data)
    # делимое - присланная строка без присланной контрольной суммы
    delimoe = data[0:47]
    # раскодировка строки
    data = data.decode('utf-8')

    # делим строку на подстроки
    ident = data[0:2]
    lat = data[2:13]
    lon = data[13:24]
    speed = data[24:28]
    way = data[28:34]
    day = data[34:36]
    month = data[36:38]
    year = data[38:42]
    time = data[42:47]
    crc_in = data[49:57]
    # делаем буквы контрольной суммы заглавными
    crc_in = crc_in.upper()

    # вычисляем свою контрольную сумму
    hash = 0
    hash = zlib.crc32(delimoe, hash)
    crc_solve = "%08X" % (hash & 0xFFFFFFFF)

    # цикл с картой, если КС совпадают и идентификатор пакета 42, то отмечаем координаты
    if (crc_in == crc_solve) and (ident == '42'):
        # цикл для открытия карты, для считывания первой координаты
        if for_center_of_map == 1:
            # запоминаем координату открытия карты
            center_lat = lat
            center_lon = lon
            # запоминаем предыдущую первую координату для соединения координат линией
            lat1 = center_lat
            lon1 = center_lon
            # открываем карту
            map = folium.Map(location=[center_lat, center_lon], zoom_start=16)
        # меняем значение вспомогательной переменной, так как карту мы уже открыли
        for_center_of_map = 2

        # отмечаем точку на карте
        folium.Marker(location=[lat, lon],
                      popup=f"Cкорость:{speed}км/ч \nНаправление:{way}° \nДата:\n {day}.{month}.{year} \nВремя:\n {time}",
                      icon=folium.Icon(color="red")).add_to(map)

        # записываем результат на карту
        map.save("map1.html")

        # соединяем координаты линиями
        folium.PolyLine(locations=[(float(lat1), float(lon1)), (lat, lon)], color="red", opacity=1).add_to(map)

        # запоминаем предыдущую координату, чтобы соединить ее и следующую линией
        lat1 = lat
        lon1 = lon

        print('КС совпадают')
    else:
        print('КС не совпадают')
        wrong_ks = wrong_ks + 1

# печатаем количество неверных КС
print('Количество неверных КС - ', wrong_ks)
