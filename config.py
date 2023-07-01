CATEGORIES = ['https://www2.hm.com/pl_pl/ona/produkty/sukienki.html?sort=stock&image-size=small&image=model&offset=0&page-size=500',
              # 'https://www2.hm.com/pl_pl/dziecko/ubrania-dla-dziewczynek/odziez/sukienki.html?sort=stock&image-size=small&image=model&offset=0&page-size=500'
              ]
# ?sort=stock&image-size=small&image=model&offset=0&page-size=500
SIZES = {
    "XXS":"38",
    "XS":"40",
    "XS/S":"40;44",
    "S":"42;44",
    "M":"46;48",
    "M/L":"46;52",
    "L":"50;52",
    "XL":"54;56",
    "XL/XXL":"54;60",
    "XXL":"58;60",
    "3XL":"62;64",
    "4XL":"66;68",
    "3XL/4XL":"62;68"
}

COLORS = {
    "Czarny": "черный",
    "Zieleń khaki": "хаки",
    "Liliowy": "лиловый",
    "Zielony": "зеленый",
    "Khaki": "хаки",
    "różnokolorowy": "разноцветный",
    "Złocisty": "золотой",
    "Rdzawoczerwony": "медь",
    "Fuksja": "фуксия",
    "Oliwkowozielony": "оливковый",
    "Kremowy/Czarny": "светло-бежевый;черный",
    "brązowy": "коричневый",
    "Limonkowy": "зеленый",
    "Biały": "белый",
    "Jasnoszary": "светло-серый",
    "Szary": "серый",
    "Kremowy": "светло-бежевый",
    "Czerwony": "красный",
    "Jasnobeżowy": "светло-бежевый",
    "Beżowy": "бежевый",
    "Turkusowy": "бирюзовый",
    "Niebieski": "синий",
    "Jasnoniebieski": "голубой",
    "Ciemnozielony": "темно-зеленый",
    "Ciemnofioletowy": "фиолетовый",
    "Fioletowy": "фиолетовый",
    "Jaskrawoniebieski": "синий",
    "Żółty": "желтый",
    "Różowy": "розовый",
    "Koralowy": "красный",
    "Ciemnobrązowy":"темно-коричневый",
    "Ciemnobrązowy/Brokatowy":"темно-коричневый",
    "Jasnobeżowy/Panterka":"разноцветный",
    "Niebieskoszary":"серый;голубой",
    "Jasnożółty":"желтый",
    "Wiśniowy":"красный",
    "Ciemnopomarańczowy":"оранжевый",
    "Czarny/Wzór":"черный",
    "Jasnoróżowy":"светло-розовый",
    "Miętowozielony":"зеленый",
    "Jasnozielony":"светло-зеленый",
    "Ciemna zieleń khaki":"хаки"
}
TABLE_OF_SIZES = '''{
  "content": [
    {
      "widgetName": "tcTable",
      "table": {
        "title": "Таблица Размеров H&M ",
        "body": [
          {
            "data": [
              "Российский размер",
              "38",
              "40",
              "42-44",
              "46-48",
              "50-52",
              "54-56",
              "58-60",
              "62-64",
              "66-68"
            ]
          },
          {
            "data": [
              "Международный размер INT",
              "XXS",
              "XS",
              "S",
              "M",
              "L",
              "XL",
              "XXL",
              "3XL",
              "4XL"
            ]
          },
          {
            "data": [
              "Объем груди, см",
              "74-78",
              "78-82",
              "82-90",
              "90-98",
              "98-107",
              "107-119",
              "119-131",
              "131-143",
              "143-155"
            ]
          },
          {
            "data": [
              "Объем талии, см",
              "58-62",
              "62-66",
              "66-74",
              "74-82,5",
              "82,5-93",
              "93-105",
              "105-117,5",
              "117,5-131,5",
              "131,5-145,5"
            ]
          },
          {
            "data": [
              "Объем бедер, см",
              "82-86",
              "86-90",
              "90-97,5",
              "97,5-103,5",
              "103,5-110,5",
              "110,5-120,5",
              "120,5-131",
              "131-143",
              "143-155"
            ]
          },
          {
            "data": [
              "Европейский размер",
              "32",
              "34",
              "36-38",
              "40-42",
              "44-46",
              "48-50",
              "52-54",
              "56-58",
              "60-62"
            ]
          }
        ]
      }
    }
  ],
  "version": 0.1
}'''
RICH = '''{{
  "content": [
    {{
      "widgetName": "raShowcase",
      "type": "chess",
      "blocks": [
        {{
          "img": {{
            "src": "https://cdn1.ozone.ru/s3/multimedia-tmp-c/item-pic-4eb07acbb8144acd319e8846c7029515.jpg",
            "srcMobile": "https://cdn1.ozone.ru/s3/multimedia-tmp-a/item-pic-5c8ff677957c79e25b4df9ff995a4210.jpg",
            "alt": "",
            "position": "to_the_edge",
            "positionMobile": "to_the_edge"
          }},
          "imgLink": "",
          "title": {{
            "content": [
              "{0}"
            ],
            "size": "size4",
            "align": "left",
            "color": "color1"
          }},
          "text": {{
            "size": "size2",
            "align": "left",
            "color": "color1",
            "content": [
              "{1}",
              "",
              "Предмет номер.:{2}",
              "",
              "Доставка из Европы. При выборе товара ориентируйтесь на ЕВРОПЕЙСКИЙ размер и сверяйтесь с размерной таблицей!"
            ]
          }},
          "reverse": false
        }}
      ]
    }}
  ],
  "version": 0.3
}}'''
TIMEOUT = 0.5
SAVE_PHOTO_PATH = 'photo/'
HOST = '85.193.92.123'